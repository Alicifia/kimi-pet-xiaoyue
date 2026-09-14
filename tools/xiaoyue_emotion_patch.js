      // ---- xiaoyue emotion patch ----
      (function xyEmotionPatch() {
        try {
          var xyInputs = riveInstance.stateMachineInputs(stateMachine);
          if (Array.isArray(xyInputs)) {
            for (var xi = 0; xi < xyInputs.length; xi++) {
              var inp = xyInputs[xi];
              if (inp && ['jump', 'angry', 'empty1', 'empty2'].indexOf(inp.name) !== -1 && typeof inp.fire === 'function') {
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
        var xyHoverTimer = null;
        rivePet.addEventListener('mouseover', function () {
          xyFire('jump');
          if (xyHoverTimer) clearInterval(xyHoverTimer);
          xyHoverTimer = setInterval(function () { xyFire('jump'); }, 600);
        });
        rivePet.addEventListener('mouseout', function () {
          if (xyHoverTimer) { clearInterval(xyHoverTimer); xyHoverTimer = null; }
        });
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
