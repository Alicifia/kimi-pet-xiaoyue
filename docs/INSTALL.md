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

官方运行时只会触发 8 个方向输入与 `shake`，本样式的表情交互（开心 / 生气 / 打瞌睡 / 惊讶 / 悬停保持）需要给工作区的 `index.html` 注入下面的补丁。

**先备份 `index.html`**，然后找到这段（在 `bindRiveLookInputs` 函数尾部，全文件唯一）：

```js
      syncRiveActivityTrigger();
    }

    function resetRiveLookDirection() {
```

把下面的补丁插入到 `syncRiveActivityTrigger();` 那一行之后、闭合大括号 `}` 之前：

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
- 悬停保持开心（`happyOn` / `happyOff`）、摇晃生气、双击生气、待机打瞌睡 / 惊讶交替
- 待机首次触发约 18 秒，之后每 45–90 秒；改 `18000` 与 `45000` 两个数字即可调节

## 三、重启 Kimi Work

完全退出后重新打开，即可看到桌宠。

## 注意事项

- 官方升级 Kimi Work 可能覆盖 `index.html`，届时需重新打补丁。
- 本补丁针对撰写时的官方 `index.html` 结构；锚点失配时请核对 `bindRiveLookInputs` 函数尾部。
- 一切修改前先备份原文件。
