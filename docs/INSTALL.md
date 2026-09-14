# 安装指南 · 小月（Xiaoyue）桌宠

> 适用：Kimi Work（kimi-desktop）Windows 版。路径中的 `%APPDATA%` 指系统的 Roaming 目录（可在资源管理器地址栏直接输入 `%APPDATA%` 打开）。

## 一、放置桌宠文件

每个形态对应一个桌宠工作区目录：

```
%APPDATA%\kimi-desktop\daimon-share\daimon\agents\main\blueprint\widgets\<widget-id>\workspace\
```

把对应形态的两个文件放进去：

- `riv/xiaoyue_<形态>.riv` → 重命名为 `pet.riv`
- `manifest/pet.<形态>.json` → 重命名为 `pet.json`

形态与目录的对应关系在 Kimi Work 的桌宠库（`blueprint/pet/library/xiaoyue-*`）中登记；如果你是从零安装，请在 Kimi Work 内先创建桌宠，再替换其 workspace 下的同名文件。

## 二、打交互补丁（必需）

官方运行时只会触发 8 个方向输入与 `shake`，本样式的表情交互（开心 / 生气 / 打瞌睡 / 惊讶 / 悬停保持）需要给工作区的 `index.html` 注入补丁。

### 方式 A：一键工具（推荐）

```bat
python tools/xiaoyue_repatch.py
```

工具会自动发现所有小月 widget、读取运行时版本、备份原文件、把补丁打到正确位置，并用 node 做语法检查；已打过补丁的会自动跳过。**Kimi Work 更新后互动失效时，同样运行这一条命令即可恢复。**

### 方式 B：手动补丁

**先备份 `index.html`**，然后找到 `bindRiveLookInputs` 函数尾部这一行（全文件唯一）：

```js
      syncRiveActivityTrigger();
```

把 `tools/xiaoyue_emotion_patch.js` 的全文插入到该行之后、函数闭合大括号 `}` 之前。补丁全文如下：

```js
      // ---- xiaoyue emotion patch ----
      (function xyEmotionPatch() {
        try {
          var xyInputs = riveInstance.stateMachineInputs(stateMachine);
          if (Array.isArray(xyInputs)) {
            for (var xi = 0; xi < xyInputs.length; xi++) {
              var inp = xyInputs[xi];
              if (inp && ['jump', 'angry', 'empty1', 'empty2', 'happyOn', 'happyOff'].indexOf(inp.name) !== -1 && typeof inp.fire === 'function') {
                riveActivityInputs.set(inp.name, inp);
              }
            }
          }
        } catch (e0) {}
        try { riveLookInputs.clear(); } catch (e0b) {}
        if (rivePet.__xyEmotionBound) return;
        rivePet.__xyEmotionBound = true;
        function xyFire(name) {
          try {
            var t = riveActivityInputs.get(name);
            if (t && typeof t.fire === 'function') t.fire();
          } catch (e1) {}
        }
        // 悬停持续开心：happyOn → happyHold（loop 状态，不自动返回）；happyOff → 回 idle。
        // 不要改成定时重触发 jump——jump 是一次性动画（约 667ms 后自动回 idle），接力会造成微笑/正常来回闪。
        rivePet.addEventListener('mouseover', function () { xyFire('happyOn'); });
        rivePet.addEventListener('mouseout', function () { xyFire('happyOff'); });
        var xyMoves = [];
        rivePet.addEventListener('mousemove', function (ev) {
          var now = Date.now();
          xyMoves.push({ t: now, x: ev.clientX });
          while (xyMoves.length && now - xyMoves[0].t > 800) xyMoves.shift();
          if (xyMoves.length >= 6) {
            var flips = 0;
            for (var i = 2; i < xyMoves.length; i++) {
              var dPrev = xyMoves[i - 1].x - xyMoves[i - 2].x;
              var dCur = xyMoves[i].x - xyMoves[i - 1].x;
              if (dPrev !== 0 && dCur !== 0 && ((dPrev > 0) !== (dCur > 0))) flips++;
            }
            if (flips >= 3) { xyFire('angry'); xyMoves = []; }
          }
        });
        rivePet.addEventListener('dblclick', function () { xyFire('angry'); });
        var xyIdleTimer = null;
        var xyIdleAlt = false;
        var xyIdleFirst = true;
        function xyScheduleIdle() {
          if (xyIdleTimer) { clearTimeout(xyIdleTimer); xyIdleTimer = null; }
          var delay = xyIdleFirst ? 18000 : (45000 + Math.random() * 45000);
          xyIdleTimer = setTimeout(function () {
            xyIdleFirst = false;
            xyFire(xyIdleAlt ? 'empty2' : 'empty1');
            xyIdleAlt = !xyIdleAlt;
            xyScheduleIdle();
          }, delay);
        }
        rivePet.addEventListener('mousemove', xyScheduleIdle);
        rivePet.addEventListener('mouseover', xyScheduleIdle);
        xyScheduleIdle();
      })();
      // ---- end xiaoyue emotion patch ----
```

补丁说明：

- 把 `jump/angry/empty1/empty2/happyOn/happyOff` 补充进可触发输入表（官方白名单不含它们）
- `riveLookInputs.clear()`：关闭「鼠标移动 → 身体倾斜跟随」。**如果想恢复跟随，删掉这一行即可**
- 悬停保持开心：进入时触发 `happyOn`（→ `happyHold` 循环状态，不自动返回），离开时触发 `happyOff`（→ 回 idle）。**不要改成定时重触发 `jump`**：`jump` 是一次性动画，约 667ms 后自动回 idle，接力会造成微笑 / 正常来回闪
- 摇晃生气、双击生气、待机打瞌睡 / 惊讶交替；待机首次触发约 18 秒，之后每 45–90 秒，改 `18000` 与 `45000` 两个数字即可调节

## 三、重启 Kimi Work

完全退出后重新打开，即可看到桌宠。

## 注意事项

- 官方升级 Kimi Work 会覆盖 `index.html`（运行时 v66 → v77 升级中已实际发生），届时运行 `python tools/xiaoyue_repatch.py` 即可一键恢复。
- 本补丁已适配运行时 v66 / v77 的 `index.html` 结构；若未来版本锚点失配，工具会明确报错且不会写坏原文件，欢迎提 Issue。
- 一切修改前先备份原文件（一键工具会自动备份到 `tools/backups/`）。
