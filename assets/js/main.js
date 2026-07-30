/* RegenOrtho Palm Beach — interactions
   Nav, scroll reveals, counters, marquees, testimonial rotator,
   hero figure attract cycle, FAQ filter/search. No dependencies. */
(function () {
  "use strict";
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------- nav */
  var toggle = document.querySelector(".nav-toggle");
  var body = document.body;
  var mobileMQ = window.matchMedia("(max-width: 1160px)"); // keep in sync with CSS

  function closeMenu() {
    body.classList.remove("nav-locked");
    if (toggle) toggle.setAttribute("aria-expanded", "false");
    document.querySelectorAll(".has-drop.is-open").forEach(function (li) {
      li.classList.remove("is-open");
      var b = li.querySelector(".drop-btn");
      if (b) b.setAttribute("aria-expanded", "false");
    });
  }

  if (toggle) {
    toggle.addEventListener("click", function () {
      var open = body.classList.toggle("nav-locked");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  document.querySelectorAll(".drop-btn").forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var li = btn.closest(".has-drop");
      var wasOpen = li.classList.contains("is-open");
      document.querySelectorAll(".has-drop.is-open").forEach(function (o) {
        if (o !== li) {
          o.classList.remove("is-open");
          var ob = o.querySelector(".drop-btn");
          if (ob) ob.setAttribute("aria-expanded", "false");
        }
      });
      li.classList.toggle("is-open", !wasOpen);
      btn.setAttribute("aria-expanded", String(!wasOpen));
    });
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest(".has-drop")) {
      document.querySelectorAll(".has-drop.is-open").forEach(function (li) {
        li.classList.remove("is-open");
        var b = li.querySelector(".drop-btn");
        if (b) b.setAttribute("aria-expanded", "false");
      });
    }
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeMenu();
  });

  mobileMQ.addEventListener("change", closeMenu);

  /* -------------------------------------------- header on scroll only */
  var header = document.querySelector(".site-header");
  if (header) {
    var stuck = false;
    var applyStuck = function () {
      var should = window.scrollY > 24;
      if (should !== stuck) { stuck = should; header.classList.toggle("is-stuck", should); }
    };
    window.addEventListener("scroll", applyStuck, { passive: true });
    applyStuck();
  }

  /* ------------------------------------------------------------ reveals */
  var revealEls = document.querySelectorAll(".reveal");
  if (reduceMotion || !("IntersectionObserver" in window)) {
    revealEls.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          en.target.classList.add("is-in");
          io.unobserve(en.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -5% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ----------------------------------------------------------- counters */
  var counters = document.querySelectorAll(".stat-num");
  if (counters.length && !reduceMotion && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        cio.unobserve(en.target);
        var el = en.target;
        var target = parseInt(el.getAttribute("data-count"), 10) || 0;
        var t0 = null;
        var dur = 1600;
        function tick(t) {
          if (!t0) t0 = t;
          var k = Math.min((t - t0) / dur, 1);
          k = 1 - Math.pow(1 - k, 3);
          el.textContent = Math.round(target * k).toLocaleString("en-US");
          if (k < 1) requestAnimationFrame(tick);
        }
        requestAnimationFrame(tick);
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ----------------------------------------------------------- marquees */
  /* Track content is cloned once so the -50% keyframe loops seamlessly.
     Spacing lives on per-item margins (not flex gap) to keep the joint clean. */
  document.querySelectorAll("[data-marquee]").forEach(function (track) {
    if (reduceMotion) return;
    var children = Array.prototype.slice.call(track.children);
    children.forEach(function (c) {
      var clone = c.cloneNode(true);
      clone.setAttribute("aria-hidden", "true");
      if (clone.tagName === "A") clone.setAttribute("tabindex", "-1");
      track.appendChild(clone);
    });
  });

  /* --------------------------------------------------- testimonial deck */
  var stage = document.querySelector("[data-quotes]");
  if (stage) {
    var slides = stage.querySelectorAll(".quote-slide");
    var dotsWrap = stage.querySelector(".quote-dots");
    var idx = 0, timer = null;

    function show(i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle("is-active", k === idx); });
      if (dotsWrap) {
        dotsWrap.querySelectorAll("button").forEach(function (d, k) {
          d.setAttribute("aria-selected", k === idx ? "true" : "false");
        });
      }
    }
    function play() {
      if (reduceMotion) return;
      stop();
      timer = setInterval(function () { show(idx + 1); }, 6000);
    }
    function stop() { if (timer) { clearInterval(timer); timer = null; } }

    if (dotsWrap) {
      slides.forEach(function (_, k) {
        var b = document.createElement("button");
        b.setAttribute("role", "tab");
        b.setAttribute("aria-selected", k === 0 ? "true" : "false");
        b.setAttribute("aria-label", "Testimonial " + (k + 1));
        b.addEventListener("click", function () { show(k); play(); });
        dotsWrap.appendChild(b);
      });
    }
    stage.addEventListener("mouseenter", stop);
    stage.addEventListener("mouseleave", play);
    stage.addEventListener("focusin", stop);
    stage.addEventListener("focusout", play);
    play();
  }

  /* ------------------------------------------------ hero figure cycle */
  var figure = document.querySelector(".figure-stage");
  if (figure) {
    var nodes = Array.prototype.slice.call(figure.querySelectorAll(".bm-node"));
    var capLabel = figure.querySelector(".figure-caption-label");
    var capBlurb = figure.querySelector(".figure-caption-blurb");
    var capGo = figure.querySelector(".figure-go");
    var capGoLabel = figure.querySelector(".figure-go-label");
    /* Devices that can't hover get no preview, so the first tap on a node only
       reveals its blurb; the second tap (or the "Explore …" button) navigates. */
    var noHover = window.matchMedia("(hover: none)");
    var fIdx = -1, fTimer = null, holdUntil = 0, pickedIdx = -1;

    function activate(i, fromUser) {
      fIdx = (i + nodes.length) % nodes.length;
      nodes.forEach(function (n, k) { n.classList.toggle("is-active", k === fIdx); });
      var n = nodes[fIdx];
      if (capLabel) capLabel.textContent = n.getAttribute("data-label");
      if (capBlurb) capBlurb.textContent = n.getAttribute("data-blurb");
      if (capGo) {
        capGo.setAttribute("href", n.getAttribute("href"));
        if (capGoLabel) capGoLabel.textContent = n.getAttribute("data-label");
      }
      if (fromUser) holdUntil = Date.now() + 9000;
    }

    nodes.forEach(function (n, k) {
      n.addEventListener("mouseenter", function () { activate(k, true); });
      n.addEventListener("focus", function () { activate(k, true); });
      n.addEventListener("click", function (e) {
        if (!noHover.matches) return;      // pointer devices: click goes straight through
        if (pickedIdx === k) return;       // second tap on the same node — let it navigate
        e.preventDefault();
        pickedIdx = k;
        /* the visitor has taken over — stop the attract cycle so the node under
           their finger can't change between the first tap and the second */
        if (fTimer) { clearInterval(fTimer); fTimer = null; }
        activate(k, true);
        if (capGo) {
          capGo.hidden = false;
          /* nudge it above the fixed Call Now / assistant pills, but only as far
             as it actually needs — the node has to stay tappable for tap two */
          var r = capGo.getBoundingClientRect();
          var safeBottom = window.innerHeight - 96;
          if (r.bottom > safeBottom) window.scrollBy({ top: r.bottom - safeBottom + 12, left: 0 });
        }
      });
    });

    /* the skeleton draws in + attract cycle arms when the section scrolls into view */
    var armed = false;
    function arm() {
      if (armed) return;
      armed = true;
      figure.classList.add("is-live");
      if (!reduceMotion) {
        setTimeout(function () {
          if (pickedIdx === -1 && Date.now() >= holdUntil) activate(0, false);
        }, 2100);
        fTimer = setInterval(function () {
          if (pickedIdx !== -1 || Date.now() < holdUntil) return;
          activate(fIdx + 1, false);
        }, 3000);
      } else {
        activate(0, false);
      }
    }
    if (reduceMotion || !("IntersectionObserver" in window)) {
      arm();
    } else {
      var fio = new IntersectionObserver(function (entries) {
        if (entries[0].isIntersecting) { arm(); fio.disconnect(); }
      }, { threshold: 0.25 });
      fio.observe(figure);
    }
  }

  /* ------------------------------------------------------- FAQ filters */
  var faqWrap = document.querySelector("[data-faq]");
  if (faqWrap) {
    var chips = Array.prototype.slice.call(document.querySelectorAll(".faq-chip"));
    var panels = Array.prototype.slice.call(faqWrap.querySelectorAll(".faq-panel"));
    var search = document.getElementById("faq-search");
    var empty = document.querySelector(".faq-empty");

    function pick(cat) {
      chips.forEach(function (c) {
        var on = c.getAttribute("data-cat") === cat;
        c.classList.toggle("is-active", on);
        c.setAttribute("aria-selected", on ? "true" : "false");
      });
      panels.forEach(function (p) {
        p.classList.toggle("is-active", p.getAttribute("data-cat") === cat);
      });
    }

    chips.forEach(function (chip, i) {
      chip.addEventListener("click", function () {
        if (search) { search.value = ""; runSearch(""); }
        pick(chip.getAttribute("data-cat"));
      });
      chip.addEventListener("keydown", function (e) {
        var next = null;
        if (e.key === "ArrowRight") next = chips[(i + 1) % chips.length];
        if (e.key === "ArrowLeft") next = chips[(i - 1 + chips.length) % chips.length];
        if (next) { e.preventDefault(); next.focus(); next.click(); }
      });
    });

    function runSearch(q) {
      q = q.trim().toLowerCase();
      body.classList.toggle("faq-searching", q.length > 0);
      if (!q) {
        panels.forEach(function (p) { p.classList.remove("faq-cat-empty"); });
        faqWrap.querySelectorAll(".faq-item").forEach(function (item) {
          item.classList.remove("faq-hide");
          item.open = false;
        });
        if (empty) empty.hidden = true;
        return;
      }
      var any = false;
      panels.forEach(function (p) {
        var hit = false;
        p.querySelectorAll(".faq-item").forEach(function (item) {
          var match = item.textContent.toLowerCase().indexOf(q) !== -1;
          item.classList.toggle("faq-hide", !match);
          if (match) { hit = true; item.open = true; }
        });
        p.classList.toggle("faq-cat-empty", !hit);
        if (hit) any = true;
      });
      if (empty) empty.hidden = any;
    }

    if (search) {
      search.addEventListener("input", function () { runSearch(search.value); });
    }
  }

  /* ------------------------------------------- assistant deep-link hook */
  document.querySelectorAll("[data-open-assist]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (window.RGAssist && window.RGAssist.open) window.RGAssist.open();
    });
  });
})();
