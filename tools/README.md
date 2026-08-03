# Site quality tooling

Two scripts that check this site against the standard the sibling site
(firstrehabnpb.com) is held to. Both are read-only — they report, they never edit.

## audit.py — structure, SEO, schema, forms

```bash
python3 tools/audit.py .              # summary
python3 tools/audit.py . --verbose    # every finding, with the page it is on
python3 tools/audit.py . ../other-site   # compare two sites side by side
```

Checks, per page: `<title>` present and 25–65 chars, meta description present and
110–175, `rel=canonical`, exactly one `<h1>`, Open Graph and Twitter tags, `alt` on
every `<img>`, no skipped heading levels, `?v=` cache-busters on local CSS/JS, and
that every JSON-LD block parses.

Site-wide: duplicate titles/descriptions/canonicals, sitemap present and covering
every page, `robots.txt` present and pointing at the sitemap, `llms.txt`, manifest,
redirect rules well-formed, and where each `<form>` submits.

It also fails the build if `aggregateRating` ever appears in our own schema — that is
self-serving review markup and violates Google's guidelines.

Exit code is the number of ERROR-level findings, so it can gate CI.

**It does not check content quality.** It cannot tell you whether a page is worth
reading, whether a claim is accurate, or whether a title is any good. It tells you
what is structurally missing; a human decides what to do about it.

## axe-sweep.js — accessibility

```bash
npm i --no-save axe-core playwright-core
python3 -m http.server 8901 &
node tools/axe-sweep.js
```

Loads every URL in `sitemap.xml` in headless Chromium and runs axe-core against the
`wcag2a`, `wcag2aa`, `wcag21a` and `wcag21aa` rule sets. Prints per-page violations
and a tally by rule.

Re-run it after any colour, contrast, or component change. Last full pass:
**60/60 pages clean, zero violations (3 August 2026).**

## What these deliberately do not touch

`/forms/new-patient.html` and `/forms/peptide-glp-questionnaire.html` collect PHI and
transmit nothing by design. `audit.py` reports where forms submit so that a change in
that behaviour is visible in a diff — it does not treat "no endpoint" on those two as
a fault. Read the HIPAA section of the root `README.md` before changing anything there.
