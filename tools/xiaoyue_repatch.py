# -*- coding: utf-8 -*-
"""
xiaoyue_repatch.py — 小月桌宠互动补丁一键恢复工具（通用版）

用途：Kimi Work 更新后会用官方新版 index.html 覆盖桌宠 widget，导致
「小月」的情绪互动补丁（悬停开心 / 摇晃生气 / 待机瞌睡等）失效。
本脚本自动把补丁重新打入所有小月 widget。

特性：
- 自动发现小月 widget（读 pet/current.json，petId 以 xiaoyue- 开头；
  兜底扫描所有 widget 的 pet.json），不硬编码 widget ID
- 自动读取运行时版本（meta daimon-pet-runtime）
- 自动定位插入锚点（bindRiveLookInputs 内的 syncRiveActivityTrigger 调用后）
- 幂等：已打补丁的文件自动跳过
- 改前自动备份到脚本旁 backups/ 目录
- 改后自动验证补丁就位；若本机有 node 则顺带做语法检查

用法：
    python xiaoyue_repatch.py                # 检查并修复所有小月 widget
    python xiaoyue_repatch.py --check        # 只检查不修改
    python xiaoyue_repatch.py --blueprint <路径>   # 指定 blueprint 根目录（测试用）

补丁内容在同目录 xiaoyue_emotion_patch.js 中，两个文件必须放在一起。
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PATCH_FILE = SCRIPT_DIR / "xiaoyue_emotion_patch.js"
BACKUP_DIR = SCRIPT_DIR / "backups"
PET_ID_PREFIX = "xiaoyue-"
PATCH_MARKER = "xiaoyue emotion patch"

DEFAULT_BLUEPRINT = (
    Path.home()
    / "AppData/Roaming/kimi-desktop/daimon-share/daimon/agents/main/blueprint"
)

# Kimi Work 自带的 node（用于语法检查，可选）
KIMI_NODE_DIR = (
    Path.home()
    / "AppData/Local/Programs/kimi-desktop/resources/resources/runtime/node"
)


def find_xiaoyue_widgets(blueprint: Path):
    """返回 [(widget_id, pet_id, workspace_dir), ...]"""
    found = []
    current = blueprint / "pet" / "current.json"
    if current.exists():
        try:
            data = json.loads(current.read_text(encoding="utf-8"))
            for item in data.get("installed", []):
                pid = item.get("petId", "")
                wid = item.get("widgetId", "")
                if pid.startswith(PET_ID_PREFIX) and wid:
                    ws = blueprint / "widgets" / wid / "workspace"
                    if (ws / "index.html").exists():
                        found.append((wid, pid, ws))
        except Exception as e:
            print(f"[warn] 读取 current.json 失败，改用扫描方式：{e}")
    if found:
        return found
    # 兜底：扫描所有 widget 的 pet.json
    widgets_dir = blueprint / "widgets"
    if not widgets_dir.exists():
        return []
    for wdir in sorted(widgets_dir.iterdir()):
        pj = wdir / "workspace" / "pet.json"
        if not pj.exists():
            continue
        try:
            pid = json.loads(pj.read_text(encoding="utf-8")).get("id", "")
        except Exception:
            continue
        if pid.startswith(PET_ID_PREFIX) and (wdir / "workspace" / "index.html").exists():
            found.append((wdir.name, pid, wdir / "workspace"))
    return found


def runtime_version(html: str) -> str:
    m = re.search(r'<meta\s+name="daimon-pet-runtime"\s+content="([^"]+)"', html)
    return m.group(1) if m else "未知"


def insert_patch(html: str, patch: str):
    """在 bindRiveLookInputs 内的 syncRiveActivityTrigger(); 之后插入补丁。

    返回 (新文本, 说明) 或 (None, 错误说明)。
    """
    func_pos = html.find("function bindRiveLookInputs")
    if func_pos == -1:
        return None, "找不到 bindRiveLookInputs 函数（运行时结构可能已大变）"
    m = re.compile(r"^(?P<indent>[ \t]*)syncRiveActivityTrigger\(\);[ \t]*$",
                   re.M).search(html, func_pos)
    if not m:
        return None, "bindRiveLookInputs 内找不到 syncRiveActivityTrigger(); 锚点"
    insert_at = m.end()
    # 补丁块本身的缩进与锚点行保持一致
    indent = m.group("indent")
    patch_lines = patch.rstrip("\n").split("\n")
    reindented = []
    for line in patch_lines:
        stripped = line.lstrip()
        # 补丁原缩进基准为 6 空格，换算到目标缩进
        orig_indent = len(line) - len(stripped)
        extra = max(0, orig_indent - 6)
        reindented.append(indent + (" " * extra) + stripped if stripped else "")
    patch_text = "\n" + "\n".join(reindented) + "\n"
    return html[:insert_at] + patch_text + html[insert_at:], f"锚点位于偏移 {insert_at}"


def node_syntax_check(html_path: Path) -> str:
    node = KIMI_NODE_DIR / ("node.exe" if sys.platform == "win32" else "node")
    if not node.exists():
        node = shutil.which("node") or ""
        if not node:
            return "node 不可用，跳过语法检查"
    try:
        html = html_path.read_text(encoding="utf-8")
        scripts = [s for s in re.findall(r"<script(?:\s[^>]*)?>(.*?)</script>",
                                         html, re.S) if s.strip()]
        for i, s in enumerate(scripts):
            tmp = SCRIPT_DIR / f"_syntax_tmp_{i}.js"
            tmp.write_text(s, encoding="utf-8")
            r = subprocess.run([str(node), "--check", str(tmp)],
                               capture_output=True, text=True)
            tmp.unlink(missing_ok=True)
            if r.returncode != 0:
                return f"语法检查失败: {r.stderr.strip()[:200]}"
        return f"语法检查通过（{len(scripts)} 个脚本块）"
    except Exception as e:
        return f"语法检查异常: {e}"


def main():
    ap = argparse.ArgumentParser(description="小月桌宠互动补丁一键恢复")
    ap.add_argument("--check", action="store_true", help="只检查不修改")
    ap.add_argument("--blueprint", type=Path, default=DEFAULT_BLUEPRINT,
                    help="blueprint 根目录（默认自动定位）")
    args = ap.parse_args()

    if not PATCH_FILE.exists():
        print(f"[错误] 找不到补丁文件 {PATCH_FILE}")
        print("       请确保 xiaoyue_emotion_patch.js 与本脚本在同一目录。")
        return 2
    patch = PATCH_FILE.read_text(encoding="utf-8")

    blueprint = args.blueprint
    if not blueprint.exists():
        print(f"[错误] blueprint 目录不存在: {blueprint}")
        return 2

    widgets = find_xiaoyue_widgets(blueprint)
    if not widgets:
        print("[错误] 没有发现任何小月桌宠 widget（petId 以 xiaoyue- 开头）。")
        print("       可能桌宠尚未安装，或 Kimi Work 目录结构已变化。")
        return 1

    print(f"发现 {len(widgets)} 个小月 widget，blueprint: {blueprint}\n")
    failures = 0
    for wid, pid, ws in widgets:
        target = ws / "index.html"
        html = target.read_text(encoding="utf-8")
        ver = runtime_version(html)
        status = ""
        if PATCH_MARKER in html:
            status = "已有补丁，跳过"
            print(f"[{pid}] 运行时 v{ver} —— {status}")
            continue
        if args.check:
            print(f"[{pid}] 运行时 v{ver} —— 补丁缺失，需要恢复（--check 模式未修改）")
            failures += 1
            continue
        new_html, msg = insert_patch(html, patch)
        if new_html is None:
            print(f"[{pid}] 运行时 v{ver} —— [失败] {msg}")
            print("       请把该 widget 的 index.html 发给维护者适配新版结构。")
            failures += 1
            continue
        BACKUP_DIR.mkdir(exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = BACKUP_DIR / f"index_{pid}_v{ver}_{stamp}_prepatch.html"
        shutil.copy2(target, backup)
        target.write_text(new_html, encoding="utf-8", newline="")
        ok = PATCH_MARKER in target.read_text(encoding="utf-8")
        check_msg = node_syntax_check(target) if ok else ""
        if ok:
            print(f"[{pid}] 运行时 v{ver} —— 补丁已恢复（{msg}）")
            print(f"       备份: {backup.name}；{check_msg}")
        else:
            print(f"[{pid}] 运行时 v{ver} —— [失败] 写入后验证未通过，已保留备份 {backup.name}")
            failures += 1

    print()
    if failures:
        print(f"完成，但有 {failures} 个 widget 需要人工处理。")
        return 1
    if args.check:
        print("检查完毕：所有小月 widget 补丁均在位。")
    else:
        print("全部完成。请在 Kimi Work 中切换一次宠物或重启应用以加载新文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
