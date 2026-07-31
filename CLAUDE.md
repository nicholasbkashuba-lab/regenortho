# RegenOrtho Palm Beach — Website (regenorthopb.com)

Static site, 56 pages, generated — do not edit HTML files directly.

## Architecture
- **`build.py`** is the single source of truth: all page content, services, team, conditions,
  locations, IV menu/pricing, FAQs, testimonials. Edit it, run `python3 build.py` (from this
  directory) to regenerate every page in place. `blog_content.py` holds blog post bodies.
- Fonts are SELF-HOSTED in assets/fonts/ (Fraunces + Manrope variable woff2, @font-face at
  the top of styles.css, preloads in head()) — do not add Google Fonts links.
- All CSS/JS links carry build-time content-hash cache-busters (`asset_v()` in build.py) —
  never link an asset without one.
- `assets/css/styles.css` — design system: navy #092D5C + gold #FDC929 (from the logo),
  porcelain #F9F7F2, bronze text accent #74590A (AA on porcelain — don't lighten).
  Signature elements: the CSS-animated golden-hour coastline hero (a real <video> can drop
  into .hero-video-slot as assets/video/hero-beach.mp4 + hero-poster.jpg — slot + CSS are
  ready, just uncomment the snippet in build.py), the detailed skeletal anatomy section
  (#body-map — skull/ribs/spine/pelvis/capsules generated in figure_svg(), draws in on
  scroll, interactive labeled nodes), aurora gradients, orbit rings + scan line, social
  marquee, gold outlined numerals.
- `assets/js/main.js` — nav (Escape closes; matchMedia 1100px must stay in sync with the
  CSS breakpoint), reveals, counters, seamless marquees (children cloned once; per-item
  margins, NOT flex gap), quote rotator, figure attract cycle, FAQ filter/search.
- `assets/js/assist.js` — concierge assistant. SET ANSWERS only (FAQ array) — no AI, no
  external API, no medical advice; route unknowns to 833-783-6561. Leads deliver via
  FormSubmit (formsubmit.co/ajax/info@regenorthopalmbeach.com) with a localStorage retry queue.
  Never put secret keys in it.
- `assets/js/forms.js` + `assets/css/forms.css` + `forms_content.py` — the two patient
  forms (`/forms/new-patient.html`, `/forms/peptide-glp-questionnaire.html`). Questions are
  declarative in `forms_content.py`; the renderer (`_field`/`_section`/`build_forms` in
  build.py) generates markup, validation, the step rail, the summary and the print sheet.

## Business facts (canonical)
- RegenOrtho Palm Beach · "The Regeneration of Orthopedics"
- 11380 Prosperity Farms Road, Suite 204–208, Palm Beach Gardens, FL 33410
- 833-STEM561 = 833-783-6561 · info@regenorthopalmbeach.com · Mon–Fri 8 AM–5 PM
- Instagram: @regenortho_palmbeach (only real social profile — X/YouTube don't exist)
- Dr. Marc Matarazzo, MD (ortho/sports medicine, MAKO-certified) · Dr. Orlando Cedeno, DPM
  (podiatric surgery + vein) · Dr. Michael Carpino (concierge provider) · Emily Bahnick,
  MSN, RN (IV infusion nurse)
- Palm Beach Gardens deliberately has NO location page — the homepage owns that keyword;
  8 nearby cities have /locations/ pages, linked in the header dropdown + footer.

## CSS gotchas (inherited from hard-won experience — don't reintroduce)
- Header backdrop-filter becomes the containing block for fixed descendants: keep the
  `body.nav-locked .site-header { backdrop-filter: none }` override or the mobile menu
  clips to the header box (iOS + Chromium).
- Desktop dropdowns use translateX(-50%); mobile keeps a `transform: none` override.
- Mobile menu: `justify-content: flex-start` + `overscroll-behavior: contain` (centered
  flex clips the top of an overflowing list unreachably).
- Marquees: spacing via per-item margins; content cloned once in JS for the -50% loop.
- Mobile Call Now pill is fixed bottom-LEFT; the assistant launcher owns bottom-right.
  Don't move either.

## The homepage figure
`aura.py` renders it: a luminous human form built from soft masses (head, trunk,
arms, legs) under a blur + bloom, with gold treatment points and drifting light
threads between them. It replaced an anatomically-correct skeleton — that read as
clinical beside an IV lounge and a peptide menu, which is the wrong half of this
practice's identity. Do not put anatomy back without asking.

`figure.py` is now the geometry source: the LANDMARKS block drives the aura form,
the hotspots and the label leaders together. Its skeleton/muscle renderers are
retained but unused — keep the landmarks if you delete them.

Two traps that cost real time here:
- `auBody` MUST stay `gradientUnits="userSpaceOnUse"`. The objectBoundingBox
  default maps a fresh gradient onto every shape, so head, torso and each limb
  light separately and the body breaks into seamed parts.
- The arm masses deliberately overlap the trunk. Drawn clear of it, the gap shows
  background through the lit figure as a hard black void.

## Hero video (do not regress)
Source of truth: "Juno.MP4" in the Dropbox /kashuba folder — 2688×1512@59.94,
15.65s drone shot of the Juno Beach Pier. That is the camera's native resolution:
there is NO true-4K master, so never upscale past 2688. Renditions in assets/video/
(all encoded on a GitHub Actions runner from the master, single generation, bt709,
-movflags +faststart, no audio):
  juno-max.mp4    2688×1512 crf26  ~18.5MB — screens resolving ≥2200 effective px
  juno-hd.mp4     1920×1080 crf23  ~14MB   — desktop default
  juno-hd.webm    2560×1440 VP9    ~26MB   — desktop fallback for no-H.264 browsers
  juno-mobile.mp4 1280×720  crf30  ~3.9MB  — phones (<768px)
  juno-mobile.webm 1280×720 VP9    ~5.2MB
  juno-poster.jpg 1600×900 q80     ~186KB  — preloaded poster
The <video> ships with NO <source> children and preload="none"; main.js attaches
exactly ONE rendition pair via matchMedia, mp4 before webm. Nothing downloads under
prefers-reduced-motion or Save-Data (poster only). .hero-video-scrim keeps the pale
lede legible over white surf — weighted left on desktop, vertical on phones; don't
remove it, and keep it light (the client asked for a bright hero). The CSS coastline
scene remains underneath as the no-video fallback. asset_v() tolerates missing files
("pending") so builds work before renditions land.

## SEO — keep maximized
- Org node: MedicalClinic+MedicalBusiness @id https://www.regenorthopb.com/#organization.
  Per page: Physician (providers), MedicalTherapy (services), MedicalCondition (conditions),
  FAQPage (faq + service/condition pages), Service-per-city (locations), BlogPosting (posts),
  BreadcrumbList (interior). sitemap.xml/robots.txt/llms.txt regenerate on build.
- DELIBERATE: no aggregateRating in our own schema (Google guideline). Do not add.
- New pages: unique title (~50–60 chars, keyword + city front-loaded), desc (~150–160),
  canonical, entry in build_meta() pages list.
- robots.txt names AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended…)
  with Allow: / — several treat silence as refusal, which costs AI-answer visibility.
  Robots meta carries max-snippet:-1 + max-image-preview:large (feeds AI Overviews).
  /blog/feed.xml is RSS. IndexNow key file at the root — ping the API on changes
  (README has the curl); Bing/Yandex act in minutes, Google ignores it.
- Per page: WebSite + WebPage nodes graph-linked to the org @id; org carries
  knowsAbout, paymentAccepted, availableLanguage and an ImageObject logo.
- vercel.json 301-maps every old WordPress URL — keep ≥12 months post-launch. It is a
  standalone file (NOT generated by build.py) — edit directly.

## Patient forms — HIPAA (do not regress)
These two pages collect PHI, so they are built to keep it in the browser. `forms.js` has
NO fetch/XHR/beacon/third-party SDK — Finish renders an on-page summary the patient prints,
saves as PDF, or downloads. No analytics or tracking script may be added to `/forms/*`.
localStorage persistence is opt-in (unchecked by default) with an Erase button — never
flip that default; these are often shared devices. `vercel.json` sets `no-store` +
`noarchive` for `/forms/*`. Do NOT point these at FormSubmit, Formspree, Zapier, a Google
Form, or a plain mailbox: electronic delivery needs a HIPAA-eligible destination under a
signed BAA plus encryption, access controls, audit logging and a retention schedule — and
the on-page notice and privacy policy both promise nothing is transmitted, so they must be
rewritten in the same change. Full checklist in README.md → "Patient forms & HIPAA".
The site's other forms (contact, assistant) may keep using FormSubmit — they collect
contact details and a reason for calling, not clinical history.

## Facts discipline
All claims/credentials/prices/reviews are from the practice's own published content. Never
invent credentials, statistics, outcomes, or testimonials. Reviews stay verbatim.
