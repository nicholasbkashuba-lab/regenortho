# RegenOrtho Palm Beach — Website

Static site for **regenorthopb.com**. 56 pages, fully generated — a complete redesign of the
practice's WordPress site, built to be handed over and self-managed.

**The Regeneration of Orthopedics** · 11380 Prosperity Farms Road, Suite 204–208, Palm Beach
Gardens, FL 33410 · 833-STEM561 (833-783-6561) · info@regenorthopalmbeach.com

## How it works

- **`build.py` is the single source of truth.** All page content — services, team bios,
  conditions, locations, IV menu + pricing, FAQs, testimonials — lives in this one file.
  Edit it, then run `python3 build.py` from this directory to regenerate every page in place.
- **`blog_content.py`** holds the 10 blog post bodies (ported verbatim from the old site).
  To add a post, add a dict at the TOP of `BLOG_POSTS` and rebuild.
- `assets/css/styles.css` — the whole design system (navy `#092D5C` + gold `#FDC929` from the
  brand mark, porcelain background, Fraunces + Manrope self-hosted fonts).
- `assets/js/main.js` — nav, scroll reveals, counters, marquees, testimonial rotator, and the
  homepage's interactive anatomy section (draws in on scroll; nodes link to condition pages).
- **Hero video drop-in**: the homepage hero background is a CSS-animated coastline. To swap in
  real footage, add `assets/video/hero-beach.mp4` + `assets/video/hero-poster.jpg` and
  uncomment the `<video>` snippet in `build_home()` in `build.py`, then rebuild.
- `assets/js/assist.js` + `assets/css/assist.css` — the concierge assistant (chat popup on
  every page). "Ask a question" serves **set answers** from the FAQ array in `assist.js` —
  no AI, no external API. Keep those answers factually accurate: no medical advice, route
  unknowns to 833-783-6561. Appointment requests are emailed via FormSubmit (below).

## Editing cheat-sheet

| Change | Where |
| --- | --- |
| Phone, address, hours | Constants at the top of `build.py` |
| Add/edit a service page | `SERVICES` list in `build.py` |
| Add/edit a condition page | `CONDITIONS` list |
| Add/edit a location page | `LOCATIONS` list |
| IV menu & pricing | `IV_MENU` list |
| Team bios & credentials | `TEAM`, `MATARAZZO_BIO`, `CEDENO_BIO` |
| FAQs (site-wide page + schema) | `GENERAL_FAQS`, `INSURANCE_FAQS`, `IV_FAQS` + per-service `faqs` |
| Testimonials | `TESTIMONIALS` (keep quotes verbatim — never invent reviews) |
| Blog posts | `blog_content.py` |
| Assistant answers | `FAQ` array in `assets/js/assist.js` |
| Patient form questions | `forms_content.py` (`INTAKE_FORM`, `GLP_FORM`) |

After ANY edit: `python3 build.py`, then commit. Preview locally with
`python3 -m http.server 8000` → http://localhost:8000.

## Leads (appointment requests)

Both the contact form and the assistant deliver to **formsubmit.co → info@regenorthopalmbeach.com**.
⚠️ FormSubmit requires one-time activation: the first submission triggers a confirmation
email to that inbox — click it (check spam) or leads will not arrive. If delivery fails,
the assistant queues the lead in the visitor's browser and retries automatically.

## Patient forms & HIPAA — read before changing anything here

`/forms/new-patient.html` and `/forms/peptide-glp-questionnaire.html` collect protected
health information (PHI). They are deliberately built so that **the PHI never leaves the
patient's browser**:

* **Nothing is transmitted.** `assets/js/forms.js` contains no `fetch`, no XHR, no beacon,
  no third-party SDK. Pressing *Finish* renders the answers into an on-page summary the
  patient prints, saves as a PDF, or downloads as a text file.
* **No tracking on form pages.** No analytics, ad pixel, or session-recording script is
  loaded on any page that asks about health. Don't add one — a page view of a
  condition-specific URL tied to an IP address is exactly the pattern regulators have
  gone after.
* **Saving is opt-in.** Progress is written to `localStorage` only if the patient ticks
  "Save my progress in this browser", and the *Erase my answers* button clears it. Never
  flip that default — a phone or a front-desk tablet is often a shared device.
* **`vercel.json`** sends `Cache-Control: no-store` and `X-Robots-Tag: noarchive` for
  `/forms/*` so the pages aren't held in shared caches or archived by crawlers.
* **Questions live in `forms_content.py`.** Edit the section/field lists there and rebuild;
  the markup, validation, step rail, summary, and print stylesheet all follow automatically.

### If you want submissions delivered electronically

That is a real change in risk, not a config tweak. Before wiring up any destination:

1. The destination must be **HIPAA-eligible and covered by a signed Business Associate
   Agreement (BAA)** with the practice. Supabase offers this on paid plans; Google
   Workspace offers it for Gmail (a consumer `@gmail.com` address does **not** qualify).
2. **Do not** point these forms at FormSubmit, Formspree, Zapier, a Google Form, a plain
   mailbox, or any automation tool without a BAA. The lead/appointment forms elsewhere on
   this site use FormSubmit — that is acceptable only because they collect contact details
   and a reason for calling, not clinical history. The patient forms are a different thing.
3. You also need the rest of the Security Rule around it: encryption in transit and at
   rest, access controls so only authorised staff can read submissions, audit logging, a
   retention/disposal schedule, and the forms added to the practice's risk analysis.
4. Update the privacy policy and the on-page notice — both currently tell patients that
   nothing is transmitted. Leaving that text in place while transmitting would be a
   material misstatement to patients.

This is engineering guidance, not legal advice. Have the practice's HIPAA compliance
contact or counsel sign off before turning on electronic delivery.

## Deploying (handover plan)

This folder is fully self-contained. To move it to the practice's own accounts:

1. Copy this `regenortho/` folder into a fresh GitHub repository (its own account/org).
2. Import the repo into their own Vercel account — no build step needed (static output;
   `vercel.json` is already configured). Set the production domain to `www.regenorthopb.com`.
3. Point DNS: `A @ → 76.76.21.21`, `CNAME www → cname.vercel-dns.com`.
4. Submit `sitemap.xml` in their Google Search Console and update the Google Business
   Profile website link.
5. Click the FormSubmit activation email on the first lead.

## SEO — do not regress

- Every page emits a unique title/description, canonical, Open Graph/Twitter tags, and
  JSON-LD (MedicalClinic org node `#organization`, Physician, MedicalTherapy,
  MedicalCondition, FAQPage, Service-per-city, BlogPosting, BreadcrumbList).
- `sitemap.xml`, `robots.txt`, `llms.txt`, and `site.webmanifest` are regenerated by the build.
- **`vercel.json` carries 301s for every old WordPress URL** (services, IV drip pages,
  blog posts, intake forms). These preserve existing Google rankings — keep them for at
  least 12 months after launch. Deliberate: no aggregateRating markup (self-serving review
  schema violates Google's guidelines — the Google Business Profile carries review signal).
- New page checklist: unique `title`/`desc`/`canonical` via `head()`, add the path to the
  `pages` list in `build_meta()`, one `<h1>` per page, descriptive `alt` text.

## Facts discipline

Every clinical claim, credential, statistic, review, and price on this site came from the
practice's own published content. Do not invent credentials, outcomes, statistics, or
testimonials. When in doubt, ask the practice and leave it out.
