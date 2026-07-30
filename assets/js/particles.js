/* RegenOrtho Palm Beach — the homepage particle field.
   A cloud of gold points that settles into a word, scatters from the cursor and
   pulls itself back together. Deliberately not anatomy and not product: earlier
   attempts at an illustrated centrepiece read as either clinical or tacky.

   No dependencies. Pauses entirely when off-screen, and renders one static
   formed state under prefers-reduced-motion. */
(function () {
  "use strict";

  var stage = document.querySelector("[data-particles]");
  if (!stage) return;
  var canvas = stage.querySelector("canvas");
  var ctx = canvas.getContext("2d", { alpha: true });
  if (!ctx) return;

  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var WORDS = (stage.getAttribute("data-words") || "REGENERATE").split("|");
  var wordIdx = 0;

  var dpr = Math.min(window.devicePixelRatio || 1, 2);
  var W = 0, H = 0;
  var particles = [];
  var pointer = { x: -9999, y: -9999, active: false };
  var raf = null, morphAt = 0, running = false;

  /* ---------------------------------------------------------- targets */
  /* Render the word to an offscreen canvas and read back the lit pixels —
     cheaper and far more faithful than hand-plotting glyph outlines. */
  function sample(word) {
    var off = document.createElement("canvas");
    off.width = W; off.height = H;
    var o = off.getContext("2d");
    // Measure, then scale to fit. Estimating from character count overflows the
    // canvas badly on the longer words and the letterforms turn to noise.
    o.textAlign = "center";
    o.textBaseline = "middle";
    var size = 200;
    o.font = "700 " + size + "px 'Fraunces', Georgia, serif";
    var w = o.measureText(word).width || 1;
    size = Math.min(size * (W * 0.86) / w, H * 0.62);
    o.font = "700 " + size + "px 'Fraunces', Georgia, serif";
    o.fillStyle = "#fff";
    o.fillText(word, W / 2, H / 2);

    var data = o.getImageData(0, 0, W, H).data;
    var pts = [];
    var step = Math.max(3, Math.round(3 * dpr));
    for (var y = 0; y < H; y += step) {
      for (var x = 0; x < W; x += step) {
        if (data[(y * W + x) * 4 + 3] > 128) pts.push([x, y]);
      }
    }
    return pts;
  }

  function assign(pts) {
    // grow or shrink the pool to match, then hand out targets
    while (particles.length < pts.length) {
      particles.push({
        x: Math.random() * W, y: Math.random() * H,
        vx: 0, vy: 0, tx: 0, ty: 0,
        r: 0.45 + Math.random() * 0.75,
        k: 0.045 + Math.random() * 0.05        // per-particle spring, so the
      });                                       // word assembles unevenly
    }
    particles.length = pts.length;
    for (var i = 0; i < pts.length; i++) {
      particles[i].tx = pts[i][0];
      particles[i].ty = pts[i][1];
    }
  }

  function resize() {
    var rect = stage.getBoundingClientRect();
    W = Math.max(320, Math.round(rect.width * dpr));
    H = Math.max(200, Math.round(rect.height * dpr));
    canvas.width = W; canvas.height = H;
    canvas.style.width = rect.width + "px";
    canvas.style.height = rect.height + "px";
    assign(sample(WORDS[wordIdx]));
  }

  /* ----------------------------------------------------------- render */
  function frame(now) {
    ctx.clearRect(0, 0, W, H);

    var rep = 78 * dpr, rep2 = rep * rep;
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];

      if (pointer.active) {
        var dx = p.x - pointer.x, dy = p.y - pointer.y;
        var d2 = dx * dx + dy * dy;
        if (d2 < rep2 && d2 > 0.01) {
          var d = Math.sqrt(d2);
          var push = (1 - d / rep) * 5.2;
          p.vx += (dx / d) * push;
          p.vy += (dy / d) * push;
        }
      }

      p.vx += (p.tx - p.x) * p.k;
      p.vy += (p.ty - p.y) * p.k;
      p.vx *= 0.86; p.vy *= 0.86;       // damping: settle without oscillating
      p.x += p.vx; p.y += p.vy;

      var speed = Math.abs(p.vx) + Math.abs(p.vy);
      ctx.globalAlpha = Math.min(1, 0.42 + speed * 0.1);
      ctx.fillStyle = speed > 2.4 ? "#FFF3CE" : "#FDC929";   // hot when moving
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * dpr, 0, 6.2832);
      ctx.fill();
    }
    ctx.globalAlpha = 1;

    if (now > morphAt) {
      morphAt = now + 4600;
      wordIdx = (wordIdx + 1) % WORDS.length;
      assign(sample(WORDS[wordIdx]));
    }
    raf = requestAnimationFrame(frame);
  }

  function drawStatic() {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "#FDC929";
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];
      ctx.beginPath();
      ctx.arc(p.tx, p.ty, p.r * dpr, 0, 6.2832);
      ctx.fill();
    }
  }

  function start() {
    if (running) return;
    running = true;
    if (reduce) { drawStatic(); return; }
    morphAt = performance.now() + 4600;
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    running = false;
    if (raf) { cancelAnimationFrame(raf); raf = null; }
  }

  /* ---------------------------------------------------------- pointer */
  function movePointer(e) {
    var rect = canvas.getBoundingClientRect();
    var src = e.touches ? e.touches[0] : e;
    pointer.x = (src.clientX - rect.left) * dpr;
    pointer.y = (src.clientY - rect.top) * dpr;
    pointer.active = true;
  }
  stage.addEventListener("pointermove", movePointer);
  stage.addEventListener("pointerleave", function () { pointer.active = false; });
  stage.addEventListener("pointerout", function (e) {
    if (!stage.contains(e.relatedTarget)) pointer.active = false;
  });
  window.addEventListener("blur", function () { pointer.active = false; });
  stage.addEventListener("touchmove", function (e) { movePointer(e); }, { passive: true });
  stage.addEventListener("touchend", function () { pointer.active = false; });
  // tapping or clicking advances the word rather than waiting out the timer
  stage.addEventListener("click", function () {
    wordIdx = (wordIdx + 1) % WORDS.length;
    assign(sample(WORDS[wordIdx]));
    morphAt = performance.now() + 4600;
  });

  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { resize(); if (reduce) drawStatic(); }, 180);
  });

  // never burn a frame while the section is off-screen or the tab is hidden
  if ("IntersectionObserver" in window) {
    new IntersectionObserver(function (en) {
      if (en[0].isIntersecting) start(); else stop();
    }, { threshold: 0.05 }).observe(stage);
  } else {
    start();
  }
  document.addEventListener("visibilitychange", function () {
    if (document.hidden) stop();
    else if (!reduce) start();
  });

  // the word is drawn in Fraunces; wait for it or the first sample is Georgia
  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(function () { resize(); if (reduce) drawStatic(); });
  }
  resize();
})();
