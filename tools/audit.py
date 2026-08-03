#!/usr/bin/env python3
"""Site quality audit — checks a generated static site against the standard
established on firstrehabnpb.com.

Usage:  python3 audit.py <site-root> [--base https://www.example.com]

Checks only things that are mechanically verifiable. It never guesses at
content quality; it reports structural gaps a human then decides about.
Exit code is the number of ERROR-level findings, so it can gate CI.
"""
import sys, os, re, json, glob, argparse
from collections import Counter

ERR, WARN, OK = "ERROR", "WARN", "OK"

class Audit:
    def __init__(self, root, base=None):
        self.root = root.rstrip("/")
        self.base = base
        self.findings = []
        self.pages = sorted(
            p for p in glob.glob(f"{self.root}/**/*.html", recursive=True)
            if "/node_modules/" not in p and "/.git/" not in p
        )

    def add(self, level, check, detail, page=None):
        self.findings.append((level, check, detail, page))

    def rel(self, p):
        return os.path.relpath(p, self.root)

    # ---------- per page ----------
    def check_pages(self):
        titles, descs, canons = Counter(), Counter(), Counter()
        for p in self.pages:
            html = open(p, encoding="utf-8", errors="replace").read()
            r = self.rel(p)
            is404 = r.endswith("404.html")

            t = re.search(r"<title>(.*?)</title>", html, re.S)
            if not t:
                self.add(ERR, "title", "no <title>", r)
            else:
                tt = re.sub(r"\s+", " ", t.group(1)).strip()
                titles[tt] += 1
                if not is404 and not (25 <= len(tt) <= 65):
                    self.add(WARN, "title-length", f"{len(tt)} chars (aim 50-60): {tt[:60]}", r)

            d = re.search(r'<meta name="description" content="(.*?)"', html, re.S)
            if not d:
                if not is404:
                    self.add(ERR, "meta-description", "missing", r)
            else:
                dd = d.group(1).strip()
                descs[dd] += 1
                if not is404 and not (110 <= len(dd) <= 175):
                    self.add(WARN, "desc-length", f"{len(dd)} chars (aim 150-160)", r)

            c = re.search(r'rel="canonical" href="(.*?)"', html)
            if not c:
                if not is404:
                    self.add(ERR, "canonical", "missing", r)
            else:
                canons[c.group(1)] += 1

            h1s = re.findall(r"<h1[\s>]", html)
            if len(h1s) == 0 and not is404:
                self.add(ERR, "h1", "no <h1>", r)
            elif len(h1s) > 1:
                self.add(ERR, "h1", f"{len(h1s)} <h1> tags (should be 1)", r)

            for prop, lvl in (("og:title", WARN), ("og:description", WARN),
                              ("og:image", WARN), ("twitter:card", WARN)):
                if f'"{prop}"' not in html and f"'{prop}'" not in html:
                    self.add(lvl, "social-meta", f"missing {prop}", r)

            # images without alt
            imgs = re.findall(r"<img\b[^>]*>", html)
            noalt = [i for i in imgs if not re.search(r'\balt="', i)]
            if noalt:
                self.add(ERR, "img-alt", f"{len(noalt)} of {len(imgs)} <img> lack alt", r)

            # heading level skips
            levels = [int(m) for m in re.findall(r"<h([1-6])[\s>]", html)]
            for a, b in zip(levels, levels[1:]):
                if b > a + 1:
                    self.add(WARN, "heading-skip", f"h{a} followed by h{b}", r)
                    break

            # cache-busting on local assets
            for m in re.finditer(r'(?:href|src)="((?:\.\./)*assets/[^"]+\.(?:css|js))"', html):
                if "?v=" not in m.group(1):
                    self.add(WARN, "cache-bust", f"no ?v= on {m.group(1)}", r)

            # JSON-LD validity
            for blk in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
                try:
                    json.loads(blk)
                except Exception as e:
                    self.add(ERR, "json-ld", f"invalid JSON-LD: {e}", r)

        for label, counter, check in (("title", titles, "duplicate-title"),
                                      ("description", descs, "duplicate-desc"),
                                      ("canonical", canons, "duplicate-canonical")):
            for val, n in counter.items():
                if n > 1:
                    self.add(ERR, check, f"{n} pages share the same {label}: {val[:70]}")

    # ---------- schema coverage ----------
    def check_schema(self):
        types = Counter()
        total = 0
        for p in self.pages:
            html = open(p, encoding="utf-8", errors="replace").read()
            blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
            total += len(blocks)
            if not blocks and not self.rel(p).endswith("404.html"):
                self.add(WARN, "schema", "page has no structured data", self.rel(p))
            for b in blocks:
                try:
                    d = json.loads(b)
                except Exception:
                    continue
                for node in (d if isinstance(d, list) else [d]):
                    t = node.get("@type")
                    for x in (t if isinstance(t, list) else [t]):
                        if x:
                            types[x] += 1
        self.add(OK, "schema-total", f"{total} JSON-LD blocks across {len(self.pages)} pages")
        self.schema_types = types
        # self-serving review markup is a guidelines violation
        if types.get("aggregateRating"):
            self.add(ERR, "schema-review",
                     "aggregateRating present on own site (Google guidelines violation)")

    # ---------- site-level files ----------
    def check_site_files(self):
        sm = os.path.join(self.root, "sitemap.xml")
        if not os.path.exists(sm):
            self.add(ERR, "sitemap", "sitemap.xml missing")
        else:
            locs = re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())
            self.add(OK, "sitemap", f"{len(locs)} URLs listed")
            listed = set()
            for u in locs:
                path = re.sub(r"^https?://[^/]+/", "", u) or "index.html"
                listed.add(path if path.endswith(".html") or path == "" else path)
            for p in self.pages:
                r = self.rel(p)
                if r.endswith("404.html"):
                    continue
                stem = r[:-len("index.html")] if r.endswith("index.html") else r
                if r not in listed and stem not in listed and stem.rstrip("/") not in listed:
                    self.add(WARN, "sitemap-missing", "not in sitemap.xml", r)

        for f, lvl in (("robots.txt", ERR), ("llms.txt", WARN), ("site.webmanifest", WARN)):
            if not os.path.exists(os.path.join(self.root, f)):
                self.add(lvl, "site-file", f"{f} missing")

        rb = os.path.join(self.root, "robots.txt")
        if os.path.exists(rb) and "sitemap" not in open(rb, encoding="utf-8").read().lower():
            self.add(ERR, "robots", "robots.txt does not reference the sitemap")

    # ---------- redirects ----------
    def check_redirects(self):
        vj = os.path.join(self.root, "vercel.json")
        if not os.path.exists(vj):
            self.add(WARN, "redirects", "no vercel.json — old URLs may 404")
            return
        try:
            v = json.load(open(vj, encoding="utf-8"))
        except Exception as e:
            self.add(ERR, "redirects", f"vercel.json unparseable: {e}")
            return
        rd = v.get("redirects", [])
        self.add(OK, "redirects", f"{len(rd)} redirect rules")
        for r in rd:
            if "source" not in r or "destination" not in r:
                self.add(ERR, "redirects", f"malformed rule: {r}")

    # ---------- forms ----------
    def check_forms(self):
        endpoints, forms = set(), 0
        for p in self.pages:
            html = open(p, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"<form\b[^>]*>", html):
                forms += 1
                a = re.search(r'action="([^"]+)"', m.group(0))
                if a:
                    endpoints.add(a.group(1))
                elif "id=" in m.group(0):
                    endpoints.add("(JS-handled)")
        for js in glob.glob(f"{self.root}/assets/js/*.js"):
            src = open(js, encoding="utf-8", errors="replace").read()
            for m in re.finditer(r"https://formsubmit\.co/[^\"'\s\\)]+", src):
                endpoints.add(m.group(0))
            if "supabase" in src.lower():
                endpoints.add("(Supabase insert)")
        self.add(OK, "forms", f"{forms} <form> elements; endpoints: {sorted(endpoints) or 'NONE'}")
        if forms and not endpoints:
            self.add(ERR, "forms", "forms present but no submission endpoint found")

    def run(self):
        self.check_pages()
        self.check_schema()
        self.check_site_files()
        self.check_redirects()
        self.check_forms()
        return self.findings


def report(name, findings, verbose=False):
    errs = [f for f in findings if f[0] == ERR]
    warns = [f for f in findings if f[0] == WARN]
    oks = [f for f in findings if f[0] == OK]
    print(f"\n{'='*72}\n{name}\n{'='*72}")
    for _, c, d, _ in oks:
        print(f"  · {c}: {d}")
    print(f"\n  ERRORS {len(errs)}   WARNINGS {len(warns)}")
    for label, group in (("ERRORS", errs), ("WARNINGS", warns)):
        if not group:
            continue
        print(f"\n  {label}")
        by = {}
        for lvl, c, d, page in group:
            by.setdefault(c, []).append((d, page))
        for c, items in sorted(by.items(), key=lambda kv: -len(kv[1])):
            print(f"    {c:<22} {len(items):>4}")
            if verbose:
                for d, page in items[:8]:
                    print(f"        {page or '-'}: {d}")
                if len(items) > 8:
                    print(f"        … and {len(items)-8} more")
    return len(errs)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()
    total = 0
    for r in a.roots:
        total += report(r, Audit(r).run(), a.verbose)
    sys.exit(min(total, 250))
