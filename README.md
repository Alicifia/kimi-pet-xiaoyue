# 小月（Xiaoyue）· Kimi 拟人化桌宠 — Q 版女仆装样式

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Powered by Rive](https://img.shields.io/badge/powered%20by-Rive-1d1d1d.svg)](https://rive.app)
[![非官方同人作品](https://img.shields.io/badge/%E9%9D%9E%E5%AE%98%E6%96%B9-%E5%90%8C%E4%BA%BA%E4%BD%9C%E5%93%81-orange.svg)](#版权与免责声明)

> Kimi Work 桌面宠物「小月」：Q 版动漫小女孩，覆盖 K2.6 / K3 标准 / K3 进阶 / K3 极致四个模型形态，会开心、会生气、会打瞌睡，还会在你悬停时一直冲你笑。
>
> **English**: An unofficial chibi-style desktop pet ("Xiaoyue") for Kimi Work — 4 model forms, interactive expressions, Rive-based. Fan-made, not affiliated with Moonshot AI.

如果这个项目让你桌面上的 Kimi 可爱了一点，欢迎点个 ⭐ **Star** 支持一下～

![六种状态实测](screenshots/six-states.png)

## 形态预览

四个形态均为大头 Q 版小女孩，以服装与装饰华丽程度区分档位：

| K2.6 | K3 标准 | K3 进阶 | K3 极致 |
|---|---|---|---|
| ![K2.6](assets/k26/k26_base.png) | ![K3](assets/k3/k3_base.png) | ![K3 进阶](assets/k3plus/k3plus_base.png) | ![K3 极致](assets/k3max/k3max_base.png) |
| `xiaoyue_k26.riv` | `xiaoyue_k3.riv` | `xiaoyue_k3plus.riv` | `xiaoyue_k3max.riv` |

每形态内置 7 张立绘：基础 / 开心 / 生气 / 惊讶 / 打瞌睡 / 害羞 / 坏笑（备用），384px 高、已去水印裁边。

## 交互逻辑

| 操作 | 反应 | 状态机输入 |
|---|---|---|
| 鼠标移到桌宠身上（不挪开） | 一直保持开心 | `happyOn` / `happyOff` |
| 按住快速来回摇晃 | 生气 | `angry` |
| 待机不管（约 45–90 秒） | 打瞌睡 ↔ 惊讶 交替 | `empty1` / `empty2` |
| 有审批 / 授权待处理 | 害羞 | `shake`（运行时原生触发） |
| 双击 | 生气（备用途径） | `angry` |
| 鼠标移动 | 8 方向注视（本样式默认关闭倾斜跟随，见安装文档） | 8 方向 trigger |
| 深浅主题切换 | 深色面纱 | `light` / `dark`（运行时原生） |

| 悬停持续开心实测 | 交互动作实测 |
|---|---|
| ![悬停保持开心](screenshots/hover-hold.png) | ![交互实测](screenshots/interactions.png) |

## 安装（简要）

> ⚠️ 需要修改 Kimi Work 宿主文件，**操作前请先备份**。

1. 选择你想要的形态，从 `riv/` 取出对应的 `.riv` 文件，从 `manifest/` 取出对应的 `pet.*.json`。
2. 放入 Kimi Work 桌宠工作区目录（`pet.riv` + `pet.json`），详细路径见 [docs/INSTALL.md](docs/INSTALL.md)。
3. 按安装文档给桌宠的 `index.html` 打上交互补丁（补丁代码与锚点位置全文附在文档中）。
4. 重启 Kimi Work，小月就住进来啦 🎉

完整步骤、目录对照表与回滚方法：**[docs/INSTALL.md](docs/INSTALL.md)**

## 仓库结构

```
riv/          四个形态的成品 Rive 文件（可直接安装）
assets/       每形态 7 张立绘 PNG（384px 高、已去水印裁边）
manifest/     四份 pet.json 安装清单
docs/         安装与运行时补丁说明
screenshots/  实机效果截图
```

## 状态机

状态机名：`KimiAvator_homepage`

- 数字输入：`light` / `dark`（主题，运行时原生）
- 触发器：`right / lower_right / down / lower_left / left / upper_left / up / upper_right`（方向）、`shake`（审批）、`jump` / `angry` / `empty1` / `empty2`（表情动作）、`happyOn` / `happyOff`（悬停持续开心开关）

## 版权与免责声明

- **本项目为非官方同人作品，与 Moonshot AI（月之暗面）没有任何官方关联，未获其背书或授权。**
- 「Kimi」名称及角色原型的相关权利归 **Moonshot AI** 所有；本项目的角色形象为粉丝二次创作。
- 立绘由 AI 生成后经人工处理（去水印、裁边、统一规格）。
- 本仓库中的代码、`pet.json` 清单与文档采用 [MIT License](LICENSE)，**Copyright (c) 2026 Alicifia**。
- 角色形象（立绘 PNG 及 riv 中嵌入的形象）**不包含** 在上述 MIT 授权范围内，仅供个人非商业使用；如需他用请自行确保已取得相关权利人许可。
- 使用本项目修改 Kimi Work 宿主文件存在风险，操作前请备份；因使用本项目造成的任何问题，作者不承担责任。

## License

MIT（详见 [LICENSE](LICENSE)）——注意上方关于角色形象的例外条款。

---

喜欢就点个 ⭐ Star，也欢迎 Issue 交流～后续还会有其他样式的 Kimi 桌宠，敬请期待。
