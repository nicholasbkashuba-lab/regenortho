#!/usr/bin/env python3
"""RegenOrtho Palm Beach — static site generator.

Single source of truth for every page on the site. Edit this file, then run
`python3 build.py` from the regenortho/ directory to regenerate all HTML in
place. All facts (services, team, pricing, reviews) come from the practice's
own published content — do not invent credentials, statistics, or clinical
claims.
"""

import hashlib
import html
import math
import json
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
BASE = "https://www.regenorthopb.com"

NAME = "RegenOrtho Palm Beach"
TAGLINE = "The Regeneration of Orthopedics"
PHONE_DISPLAY = "833-783-6561"
PHONE_VANITY = "833-STEM561"
PHONE_TEL = "+18337836561"
EMAIL = "info@regenorthopalmbeach.com"
ADDRESS_STREET = "11380 Prosperity Farms Road, Suite 204–208"
ADDRESS_CITY = "Palm Beach Gardens"
ADDRESS_STATE = "FL"
ADDRESS_ZIP = "33410"
HOURS = "Monday – Friday: 8:00 AM – 5:00 PM"
INSTAGRAM = "https://www.instagram.com/regenortho_palmbeach/"
MAP_URL = "https://maps.google.com/maps?q=RegenOrtho%20Palm%20Beach%2011380%20Prosperity%20Farms%20Road%20Palm%20Beach%20Gardens"
GEO_LAT, GEO_LNG = 26.8449, -80.0693

ORG_ID = f"{BASE}/#organization"

# ---------------------------------------------------------------------------
# Asset cache-busting
# ---------------------------------------------------------------------------

_v_cache = {}


def asset_v(path):
    """Content-hash version for an asset path relative to regenortho/."""
    if path not in _v_cache:
        full = os.path.join(ROOT, path)
        with open(full, "rb") as f:
            _v_cache[path] = hashlib.md5(f.read()).hexdigest()[:8]
    return _v_cache[path]


# ---------------------------------------------------------------------------
# Shared chrome
# ---------------------------------------------------------------------------

def head(title, desc, depth=0, canonical="", og_image="assets/media/og-image.jpg",
         page_type="website", extra_schema="", preload_hero=False, extra_css=""):
    p = "../" * depth
    canonical_url = f"{BASE}/{canonical}" if canonical else f"{BASE}/"
    og_url = f"{BASE}/{og_image}?v={asset_v(og_image)}"
    schema = org_schema()
    hero_preload = ""
    if preload_hero:
        hero_preload = ""  # hero is SVG/CSS — nothing extra to preload
    extra_css_tag = ""
    if extra_css:
        extra_css_tag = f'<link rel="stylesheet" href="{p}{extra_css}?v={asset_v(extra_css)}">\n'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{canonical_url}">
<meta property="og:type" content="{page_type}">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:image" content="{og_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{html.escape(title)}">
<meta name="twitter:description" content="{html.escape(desc)}">
<meta name="twitter:image" content="{og_url}">
<meta name="theme-color" content="#071A38">
<link rel="icon" type="image/png" sizes="32x32" href="{p}assets/media/favicon-32.png?v=1">
<link rel="icon" type="image/png" sizes="16x16" href="{p}assets/media/favicon-16.png?v=1">
<link rel="apple-touch-icon" href="{p}assets/media/apple-touch-icon.png?v=1">
<link rel="manifest" href="{p}site.webmanifest">
<link rel="preload" href="{p}assets/fonts/fraunces.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{p}assets/fonts/manrope.woff2" as="font" type="font/woff2" crossorigin>
{hero_preload}<link rel="stylesheet" href="{p}assets/css/styles.css?v={asset_v('assets/css/styles.css')}">
<link rel="stylesheet" href="{p}assets/css/assist.css?v={asset_v('assets/css/assist.css')}">
{extra_css_tag}<script type="application/ld+json">{schema}</script>
{extra_schema}</head>
"""


SERVICES_NAV = [
    ("services/orthopedic-sports-medicine.html", "Orthopedic & Sports Medicine"),
    ("services/podiatric-medicine-foot-ankle-surgery.html", "Podiatric Medicine & Foot/Ankle Surgery"),
    ("services/regenerative-medicine-orthobiologics.html", "Regenerative Medicine & Orthobiologics"),
    ("services/advanced-non-surgical-therapies.html", "Advanced Non-Surgical Therapies"),
    ("services/peptide-therapy.html", "Peptide Therapy"),
    ("services/vein-care.html", "Vein Care — Medical & Cosmetic"),
    ("iv-therapy.html", "IV Recovery & Wellness Lounge"),
    ("services/misha-knee-system.html", "MISHA Knee System"),
    ("services/mako-robotic-knee-replacement.html", "Mako Robotic Knee Replacement"),
    ("services/neuropathy-program.html", "Neuropathy Restoration Program"),
    ("services/medical-weight-loss.html", "Medical Weight Loss & GLP-1"),
    ("services/concierge-care.html", "Concierge & Direct-Pay Care"),
    ("infusions/index.html", "Specialty Infusion Center"),
]

CONDITIONS_NAV = [
    ("conditions/knee-pain.html", "Knee Pain"),
    ("conditions/shoulder-pain.html", "Shoulder Pain"),
    ("conditions/hip-pain.html", "Hip Pain"),
    ("conditions/arthritis-joint-pain.html", "Arthritis & Joint Pain"),
    ("conditions/sports-injuries.html", "Sports Injuries"),
    ("conditions/tendon-ligament-injuries.html", "Tendon & Ligament Injuries"),
    ("conditions/foot-ankle-pain.html", "Foot & Ankle Pain"),
    ("conditions/plantar-fasciitis.html", "Plantar Fasciitis & Heel Pain"),
    ("conditions/peripheral-neuropathy.html", "Peripheral Neuropathy"),
    ("conditions/varicose-spider-veins.html", "Varicose & Spider Veins"),
]

LOCATIONS_NAV = [
    ("locations/jupiter.html", "Jupiter"),
    ("locations/north-palm-beach.html", "North Palm Beach"),
    ("locations/juno-beach.html", "Juno Beach"),
    ("locations/tequesta.html", "Tequesta"),
    ("locations/palm-beach.html", "Palm Beach"),
    ("locations/west-palm-beach.html", "West Palm Beach"),
    ("locations/singer-island.html", "Singer Island"),
    ("locations/lake-park.html", "Lake Park"),
]


def nav(depth=0, current=""):
    p = "../" * depth
    svc = "\n".join(
        f'<li><a href="{p}{href}">{label}</a></li>' for href, label in SERVICES_NAV
    )
    cond = "\n".join(
        f'<li><a href="{p}{href}">{label}</a></li>' for href, label in CONDITIONS_NAV
    )
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header" id="top">
  <div class="header-inner">
    <a class="brand" href="{p}index.html" aria-label="{NAME} — home">
      <img class="brand-dark" src="{p}assets/media/logo-dark-nav.png?v={asset_v('assets/media/logo-dark-nav.png')}" alt="{NAME} — {TAGLINE}" width="167" height="52">
      <img class="brand-light" src="{p}assets/media/logo-light-nav.png?v={asset_v('assets/media/logo-light-nav.png')}" alt="{NAME} — {TAGLINE}" width="167" height="52">
    </a>
    <nav class="main-nav" aria-label="Primary">
      <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu"><span class="nav-toggle-box" aria-hidden="true"><span></span><span></span><span></span></span>Menu</button>
      <ul class="nav-menu" id="nav-menu">
        <li class="has-drop"><button class="drop-btn" aria-expanded="false">About<svg viewBox="0 0 12 8" width="10" height="7" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 1.5 6 6.5 11 1.5"/></svg></button>
          <ul class="drop">
            <li><a href="{p}about.html">About the Practice</a></li>
            <li><a href="{p}providers/dr-marc-matarazzo.html">Dr. Marc Matarazzo, MD</a></li>
            <li><a href="{p}providers/dr-orlando-cedeno.html">Dr. Orlando Cedeno, DPM</a></li>
            <li><a href="{p}providers/emily-bahnick.html">Emily Bahnick, MSN, RN</a></li>
            <li><a href="{p}patient-resources.html">Patient Resources</a></li>
          </ul>
        </li>
        <li class="has-drop has-mega"><button class="drop-btn" aria-expanded="false">Services<svg viewBox="0 0 12 8" width="10" height="7" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 1.5 6 6.5 11 1.5"/></svg></button>
          <ul class="drop drop-mega">
            {svc}
            <li class="drop-all"><a href="{p}services/index.html">All services →</a></li>
          </ul>
        </li>
        <li class="has-drop"><button class="drop-btn" aria-expanded="false">Conditions<svg viewBox="0 0 12 8" width="10" height="7" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 1.5 6 6.5 11 1.5"/></svg></button>
          <ul class="drop">
            {cond}
          </ul>
        </li>
        <li><a class="nav-link" href="{p}iv-therapy.html">IV Lounge</a></li>
        <li class="has-drop"><button class="drop-btn" aria-expanded="false">Patient Forms<svg viewBox="0 0 12 8" width="10" height="7" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 1.5 6 6.5 11 1.5"/></svg></button>
          <ul class="drop">
            <li><a href="{p}forms/index.html">All patient forms</a></li>
            <li><a href="{p}forms/new-patient.html">New Patient Intake Form</a></li>
            <li><a href="{p}forms/peptide-glp-questionnaire.html">Peptide &amp; GLP-1 Questionnaire</a></li>
          </ul>
        </li>
        <li><a class="nav-link" href="{p}blog/index.html">Blog</a></li>
        <li><a class="nav-link" href="{p}faq.html">FAQ</a></li>
        <li><a class="nav-link" href="{p}contact.html">Contact</a></li>
        <li class="nav-cta-item"><a class="btn btn-gold nav-cta" href="{p}contact.html#book">Book a Consultation</a></li>
      </ul>
    </nav>
    <a class="btn btn-gold header-cta" href="{p}contact.html#book">Book a Consultation</a>
  </div>
</header>
"""


def footer(depth=0, extra_js=""):
    p = "../" * depth
    extra_js_tag = ""
    if extra_js:
        extra_js_tag = f'<script src="{p}{extra_js}?v={asset_v(extra_js)}" defer></script>\n'
    svc = "\n".join(
        f'<li><a href="{p}{href}">{label}</a></li>' for href, label in SERVICES_NAV[:8]
    )
    loc = "\n".join(
        f'<li><a href="{p}{href}">{label}</a></li>' for href, label in LOCATIONS_NAV
    )
    year = 2026
    return f"""<footer class="site-footer">
  <div class="footer-glow" aria-hidden="true"></div>
  <div class="footer-inner">
    <div class="footer-brand">
      <img src="{p}assets/media/logo-dark-nav.png?v={asset_v('assets/media/logo-dark-nav.png')}" alt="{NAME} — {TAGLINE}" width="220" height="68" loading="lazy">
      <p>Concierge orthopedic, podiatric, regenerative, and vein care in Palm Beach Gardens — board-certified specialists helping you move better, heal faster, and live healthier.</p>
      <a class="footer-ig" href="{INSTAGRAM}" rel="noopener" target="_blank"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 2.2c3.2 0 3.6 0 4.8.1 1.2.1 1.8.2 2.2.4.6.2 1 .5 1.4.9.4.4.7.8.9 1.4.2.4.4 1 .4 2.2.1 1.2.1 1.6.1 4.8s0 3.6-.1 4.8c-.1 1.2-.2 1.8-.4 2.2-.2.6-.5 1-.9 1.4-.4.4-.8.7-1.4.9-.4.2-1 .4-2.2.4-1.2.1-1.6.1-4.8.1s-3.6 0-4.8-.1c-1.2-.1-1.8-.2-2.2-.4-.6-.2-1-.5-1.4-.9-.4-.4-.7-.8-.9-1.4-.2-.4-.4-1-.4-2.2C2.2 15.6 2.2 15.2 2.2 12s0-3.6.1-4.8c.1-1.2.2-1.8.4-2.2.2-.6.5-1 .9-1.4.4-.4.8-.7 1.4-.9.4-.2 1-.4 2.2-.4C8.4 2.2 8.8 2.2 12 2.2m0 1.8c-3.1 0-3.5 0-4.7.1-1.1.1-1.5.2-1.8.3-.5.2-.8.4-1.1.7-.3.3-.5.6-.7 1.1-.1.3-.3.7-.3 1.8-.1 1.2-.1 1.6-.1 4.7s0 3.5.1 4.7c.1 1.1.2 1.5.3 1.8.2.5.4.8.7 1.1.3.3.6.5 1.1.7.3.1.7.3 1.8.3 1.2.1 1.6.1 4.7.1s3.5 0 4.7-.1c1.1-.1 1.5-.2 1.8-.3.5-.2.8-.4 1.1-.7.3-.3.5-.6.7-1.1.1-.3.3-.7.3-1.8.1-1.2.1-1.6.1-4.7s0-3.5-.1-4.7c-.1-1.1-.2-1.5-.3-1.8-.2-.5-.4-.8-.7-1.1-.3-.3-.6-.5-1.1-.7-.3-.1-.7-.3-1.8-.3-1.2-.1-1.6-.1-4.7-.1M12 7.1a4.9 4.9 0 1 1 0 9.8 4.9 4.9 0 0 1 0-9.8m0 1.8a3.1 3.1 0 1 0 0 6.2 3.1 3.1 0 0 0 0-6.2m5.1-3.1a1.1 1.1 0 1 1 0 2.3 1.1 1.1 0 0 1 0-2.3"/></svg> @regenortho_palmbeach</a>
    </div>
    <nav class="footer-col" aria-label="Quick links">
      <h2>Explore</h2>
      <ul>
        <li><a href="{p}about.html">About Us</a></li>
        <li><a href="{p}services/index.html">Our Services</a></li>
        <li><a href="{p}iv-therapy.html">IV Therapy Lounge</a></li>
        <li><a href="{p}patient-resources.html">Patient Resources</a></li>
        <li><a href="{p}forms/index.html">Patient Forms</a></li>
        <li><a href="{p}faq.html">FAQ</a></li>
        <li><a href="{p}blog/index.html">Blog</a></li>
        <li><a href="{p}contact.html">Contact Us</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="Services">
      <h2>Services</h2>
      <ul>
        {svc}
      </ul>
    </nav>
    <nav class="footer-col" aria-label="Areas we serve">
      <h2>Areas We Serve</h2>
      <ul>
        <li><a href="{p}index.html">Palm Beach Gardens</a></li>
        {loc}
      </ul>
    </nav>
    <div class="footer-col footer-contact">
      <h2>Visit Us</h2>
      <address>
        <a href="{MAP_URL}" rel="noopener" target="_blank">{ADDRESS_STREET}<br>{ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP}</a>
      </address>
      <p class="footer-hours">{HOURS}</p>
      <p><a class="footer-tel" href="tel:{PHONE_TEL}">{PHONE_VANITY}<span> · {PHONE_DISPLAY}</span></a></p>
      <p><a class="footer-mail" href="mailto:{EMAIL}">{EMAIL}</a></p>
    </div>
  </div>
  <div class="footer-base">
    <p>© {year} {NAME} · {TAGLINE}</p>
    <p><a href="{p}privacy-policy.html">Privacy Policy</a> · <a href="{p}terms.html">Terms &amp; Conditions</a></p>
  </div>
  <a class="mobile-call" href="tel:{PHONE_TEL}"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M6.6 10.8c1.5 2.9 3.7 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.4.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.4 0 .7-.2 1l-2.3 2.2z"/></svg>Call Now</a>
</footer>
<script src="{p}assets/js/main.js?v={asset_v('assets/js/main.js')}"></script>
<script src="{p}assets/js/assist.js?v={asset_v('assets/js/assist.js')}" defer></script>
{extra_js_tag}</body>
</html>
"""


def page_hero(eyebrow, title, lede, crumbs_html="", cta=True, depth=0):
    p = "../" * depth
    cta_html = ""
    if cta:
        cta_html = f"""<div class="hero-cta-row">
      <a class="btn btn-gold" href="{p}contact.html#book">Book a Consultation</a>
      <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">Call {PHONE_VANITY}</a>
    </div>"""
    return f"""<section class="page-hero">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="page-hero-inner reveal">
    {crumbs_html}
    <p class="eyebrow">{eyebrow}</p>
    <h1>{title}</h1>
    <p class="lede">{lede}</p>
    {cta_html}
  </div>
</section>
"""


def crumbs(items, depth=0):
    p = "../" * depth
    out = [f'<nav class="crumbs" aria-label="Breadcrumb"><ol>']
    out.append(f'<li><a href="{p}index.html">Home</a></li>')
    for href, label in items[:-1]:
        out.append(f'<li><a href="{p}{href}">{label}</a></li>')
    out.append(f'<li aria-current="page">{items[-1][1]}</li>')
    out.append("</ol></nav>")
    return "".join(out)


def cta_band(depth=0, heading="Ready to feel like <em>yourself</em> again?",
             sub="Book a consultation with our board-certified specialists and get a personalized plan — often with same-week availability."):
    p = "../" * depth
    return f"""<section class="cta-band">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="cta-band-inner reveal">
    <div class="cta-mark" aria-hidden="true"><svg viewBox="0 0 64 64" width="56" height="56"><circle cx="32" cy="32" r="30" fill="#FDC929"/><path d="M32 18c-2 5-8 7-12 6 3 3 8 4 10 3-4 3-9 9-9 15 0 0 5-8 11-11-1 6 0 12 3 16 1-5 1-11 0-16 4 2 8 7 9 11 1-6-3-12-7-15 3 0 7-2 9-5-4 1-9 0-12-3 0 0-1-1-2-1z" fill="#092D5C"/></svg></div>
    <h2>{heading}</h2>
    <p>{sub}</p>
    <div class="cta-row">
      <a class="btn btn-gold" href="{p}contact.html#book">Book a Consultation</a>
      <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">{PHONE_VANITY} · {PHONE_DISPLAY}</a>
    </div>
  </div>
</section>
"""


# ---------------------------------------------------------------------------
# Schema helpers
# ---------------------------------------------------------------------------

_org_cache = None


def org_schema():
    global _org_cache
    if _org_cache is None:
        org = {
            "@context": "https://schema.org",
            "@type": ["MedicalClinic", "MedicalBusiness"],
            "@id": ORG_ID,
            "name": NAME,
            "alternateName": ["Regen Ortho", "RegenOrtho", "Regen Ortho PB"],
            "slogan": TAGLINE,
            "description": "Concierge orthopedic, podiatric, regenerative, and vein care in Palm Beach Gardens, FL — board-certified specialists offering sports medicine, foot & ankle surgery, orthobiologic therapies, IV wellness, and minimally invasive vein treatment.",
            "url": f"{BASE}/",
            "logo": f"{BASE}/assets/media/logo-dark.png",
            "image": f"{BASE}/assets/media/og-image.jpg",
            "telephone": "+1-833-783-6561",
            "email": EMAIL,
            "priceRange": "$$",
            "currenciesAccepted": "USD",
            "isAcceptingNewPatients": True,
            "medicalSpecialty": ["Orthopedic surgery", "Sports medicine", "Podiatric medicine", "Regenerative medicine", "Phlebology"],
            "address": {
                "@type": "PostalAddress",
                "streetAddress": ADDRESS_STREET,
                "addressLocality": ADDRESS_CITY,
                "addressRegion": ADDRESS_STATE,
                "postalCode": ADDRESS_ZIP,
                "addressCountry": "US",
            },
            "geo": {"@type": "GeoCoordinates", "latitude": GEO_LAT, "longitude": GEO_LNG},
            "hasMap": MAP_URL,
            "openingHoursSpecification": [{
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "08:00",
                "closes": "17:00",
            }],
            "areaServed": [
                {"@type": "City", "name": c} for c in [
                    "Palm Beach Gardens", "Jupiter", "North Palm Beach", "Juno Beach",
                    "Tequesta", "Palm Beach", "West Palm Beach", "Singer Island",
                    "Lake Park", "Riviera Beach",
                ]
            ],
            "sameAs": [INSTAGRAM],
            "availableService": [
                {"@type": "MedicalTherapy", "@id": f"{BASE}/services/orthopedic-sports-medicine.html#service"},
                {"@type": "MedicalTherapy", "@id": f"{BASE}/services/podiatric-medicine-foot-ankle-surgery.html#service"},
                {"@type": "MedicalTherapy", "@id": f"{BASE}/services/regenerative-medicine-orthobiologics.html#service"},
                {"@type": "MedicalTherapy", "@id": f"{BASE}/services/vein-care.html#service"},
                {"@type": "MedicalTherapy", "@id": f"{BASE}/iv-therapy.html#service"},
            ],
        }
        _org_cache = json.dumps(org, separators=(",", ":"))
    return _org_cache


def extra_ld(obj):
    return f'<script type="application/ld+json">{json.dumps(obj, separators=(",", ":"))}</script>\n'


def breadcrumb_schema(items):
    """items: list of (url_path, name) including the current page last."""
    return extra_ld({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": name,
             "item": f"{BASE}/{path}" if path else f"{BASE}/"}
            for i, (path, name) in enumerate(items)
        ],
    })


def faq_schema(pairs):
    return extra_ld({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in pairs
        ],
    })


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)
    print("wrote", path)

# ---------------------------------------------------------------------------
# Content data — every fact sourced from the practice's published content
# ---------------------------------------------------------------------------

TEAM = [
    {
        "slug": "dr-marc-matarazzo",
        "name": "Dr. Marc Matarazzo, MD",
        "role": "MD, FAAOS · Medical Director & Owner",
        "photo": "team/marc-matarazzo.jpg",
        "short": "Board-certified, fellowship-trained orthopedic surgeon with more than 23 years of clinical and surgical experience in sports medicine, minimally invasive arthroscopy, and MAKO robotic-assisted knee replacement.",
    },
    {
        "slug": "dr-orlando-cedeno",
        "name": "Dr. Orlando Cedeno, DPM",
        "role": "DPM, FACFAS · Owner",
        "photo": "team/orlando-cedeno.jpg",
        "short": "Board certified in foot surgery by the American Board of Foot & Ankle Surgery, fellowship-trained in reconstructive and trauma surgery of the foot and ankle, with advanced expertise in vein care.",
    },
    {
        "slug": "emily-bahnick",
        "name": "Emily Bahnick, MSN, RN",
        "role": "IV Infusion Nurse & Care Coordinator",
        "photo": "team/emily-bahnick.jpg",
        "short": "Registered nurse with MSN and BSN degrees and more than 10 years of experience — your IV infusion nurse and care coordinator, focused on longevity, reducing reliance on pharmaceuticals, and healing from within.",
        "stats": ["10+ years experience", "MSN · BSN", "Registered Nurse"],
    },
]

SUPPORT_TEAM = [
    {"name": "Dr. Michael Carpino", "role": "Concierge Provider", "photo": "team/michael-carpino.jpg"},
]

TESTIMONIALS = [
    ("RegenOrtho Palm Beach gave me my life back. Their regenerative therapy helped me avoid surgery, and I feel stronger every day.", "Sarah W.", "Patient testimonial"),
    ("The team is so caring and professional. They explained every step and made sure I was comfortable throughout my treatment.", "Michael R.", "Patient testimonial"),
    ("I was struggling with chronic knee pain. Within weeks of my procedure here, I noticed a huge improvement. Highly recommend!", "Linda T.", "Patient testimonial"),
    ("From the moment I walked in, I felt supported. They truly deliver personalized care with advanced techniques.", "James K.", "Patient testimonial"),
    ("Very professional service. The staff and doctor were very accommodating to my needs. I felt comfortable, well cared for and well informed.", "Al Franc", "Posted on Google"),
    ("Dr Cendeno was very knowledgeable, he took the time to explain my diagnosis in detail and answered all my questions. Office staff was welcoming and kind.", "Erika S.", "Posted on Google"),
    ("My experience was one of the best as i followed Dr Cedeno instructions and his treatment my plantar fasciitis issue has been resolved. Both locations are easy to find and the staff are very friendly knowledgeable and kind. If you have any type of discomfort or feet pain this is definitely the doctor for you!", "Veronica “Roni” Lee", "Posted on Google"),
    ("I am so Thankful I found this practice. I was very happy with the prompt appointment scheduled. The staff is friendly, the Dr as well made me feel comfortable. The pain is much better. I am able to increase my activity.", "Michelle Legere", "Posted on Google"),
]

ASSOCIATIONS = [
    ("assoc-1.png", "American Academy of Orthopaedic Surgeons"),
    ("assoc-2.png", "American Podiatric Medical Association"),
    ("assoc-3.png", "American Podiatric Medical Association — Accepted"),
    ("assoc-4.png", "American Orthopaedic Association"),
    ("assoc-5.png", "American Orthopaedic Association"),
    ("assoc-6.png", "American Professional Wound Care Association"),
    ("assoc-7.png", "Academy of Physicians in Wound Healing"),
    ("assoc-8.png", "American Professional Wound Care Association"),
    ("assoc-aens.png", "Association of Extremity Nerve Surgeons"),
]

IV_MENU = [
    {"name": "Hangover", "price": 299, "bag": "bag-hydration.png",
     "desc": "Rehydrates, detoxifies, and relieves headaches, nausea, and fatigue from dehydration, alcohol, or overexertion."},
    {"name": "Recovery", "price": 299, "bag": "bag-athletic.png",
     "desc": "Supports post-surgery healing and sports recovery with rehydration and targeted nutrients."},
    {"name": "Performance / Energy (Myers + Amino-6)", "price": 225, "bag": "bag-myers.png",
     "desc": "Increases energy, endurance, and focus with amino acids and B-vitamins to combat fatigue and optimize daily performance."},
    {"name": "Beauty / Glow / Anti-Aging (Myers + Biotin)", "price": 259, "bag": "bag-beauty.png",
     "desc": "Promotes radiant skin, stronger hair and nails, and overall anti-aging wellness through targeted vitamins and antioxidants."},
    {"name": "Hydration / Basic Electrolyte", "price": 189, "bag": "bag-hydration.png",
     "desc": "Rapidly restores fluid and electrolyte balance for dehydration, heat exposure, or post-workout recovery."},
    {"name": "Myers’ PLUS", "price": 225, "bag": "bag-myers.png",
     "desc": "Foundational wellness infusion supporting energy, immune balance, and recovery by replenishing essential vitamins and minerals lost to stress, fatigue, or illness."},
    {"name": "Immune Boost (Vit C + Zinc + GSH)", "price": 259, "bag": "bag-immune.png",
     "desc": "Strengthens the immune system, reduces inflammation, and supports faster recovery from viral or seasonal illness."},
    {"name": "Cleanse", "price": 349, "bag": "bag-cleanse.png",
     "desc": "Deep detox and metabolic reset designed to cleanse the liver, flush toxins, and restore energy and clarity."},
    {"name": "NAD⁺ 500 mg", "price": 499, "bag": "bag-nad.png",
     "desc": "High-dose NAD⁺ infusion for deep cellular rejuvenation, energy renewal, and neuroprotective support."},
    {"name": "Athletic Recovery & Performance (Myers + Amino-6)", "price": 225, "bag": "bag-athletic.png",
     "desc": "Rebuilds and refuels muscles with amino acids and electrolytes to enhance performance, reduce soreness, and accelerate recovery."},
    {"name": "Neuro Restore", "price": 231, "bag": "bag-nad.png",
     "desc": "Antioxidant and nerve support with Alpha Lipoic Acid (ALA) and Vitamin B12 to help promote healthy nerve function and neurological wellness."},
    {"name": "All-Inclusive", "price": 399, "bag": "bag-all-inclusive.png",
     "desc": "Comprehensive full-body infusion delivering vitamins, minerals, amino acids, antioxidants, and hydration for total wellness optimization."},
]

INFUSIONS = [
    {"slug": "ivig", "name": "IVIG (Intravenous Immunoglobulin)",
     "title": "IVIG Infusion Therapy Palm Beach Gardens | RegenOrtho",
     "desc": "Physician-supervised IVIG (intravenous immunoglobulin) infusion therapy in a private Palm Beach Gardens infusion suite. Insurance coordination and flexible scheduling.",
     "lede": "Intravenous immunoglobulin therapy delivered in a private, clinician-supervised infusion suite — without the hospital.",
     "body": "IVIG (intravenous immunoglobulin) is a physician-prescribed infusion used to support patients with certain immune-mediated and neurological conditions. Our infusion center administers IVIG in a calm, private suite with clinical monitoring throughout your visit, coordinating directly with your referring physician on protocol, frequency, and follow-up."},
    {"slug": "krystexxa", "name": "Krystexxa Infusion Therapy",
     "title": "Krystexxa Infusion Therapy Palm Beach Gardens | RegenOrtho",
     "desc": "Krystexxa (pegloticase) infusion therapy for uncontrolled gout, administered under physician supervision in our Palm Beach Gardens infusion suite.",
     "lede": "Physician-supervised Krystexxa (pegloticase) infusions for chronic, uncontrolled gout — in a private outpatient setting.",
     "body": "Krystexxa is an infusion medication prescribed for adults with chronic gout that has not responded to conventional urate-lowering therapy. Treatment is administered in our monitored infusion suite, with pre-infusion screening and coordination with your prescribing physician at every step."},
    {"slug": "ocrevus", "name": "Ocrevus Treatment",
     "title": "Ocrevus Infusion Palm Beach Gardens | RegenOrtho Infusion Center",
     "desc": "Ocrevus (ocrelizumab) infusion treatment administered under clinical supervision in a private Palm Beach Gardens suite, coordinated with your neurologist.",
     "lede": "Ocrevus (ocrelizumab) infusions coordinated with your neurologist and delivered in a private, monitored suite.",
     "body": "Ocrevus is a prescription infusion used in the management of certain forms of multiple sclerosis. Our team works with your neurologist's treatment plan, provides pre-infusion screening, and monitors you throughout each visit in a comfortable outpatient environment."},
    {"slug": "ultomiris", "name": "Ultomiris Infusion Therapy",
     "title": "Ultomiris Infusion Palm Beach Gardens | RegenOrtho Infusion Center",
     "desc": "Ultomiris (ravulizumab) infusion therapy in a private, physician-supervised Palm Beach Gardens outpatient suite with insurance coordination.",
     "lede": "Ultomiris (ravulizumab) infusion therapy in a private outpatient suite, with clinical monitoring and insurance coordination.",
     "body": "Ultomiris is a physician-prescribed infusion used in the management of certain rare complement-mediated conditions. We administer it on your prescriber's protocol in a monitored, private infusion suite — a calmer, more convenient alternative to hospital-based infusion."},
]

SERVICES = [
    {
        "slug": "orthopedic-sports-medicine",
        "name": "Orthopedic & Sports Medicine",
        "nav": "Orthopedic & Sports Medicine",
        "title": "Orthopedic Surgeon Palm Beach Gardens | Sports Medicine",
        "desc": "Board-certified orthopedic surgeon and sports medicine care in Palm Beach Gardens — same-day injury consultations, joint preservation, arthroscopy, and personalized recovery plans.",
        "eyebrow": "Orthopedic & Sports Medicine",
        "h1": "Expert Care for Joints, Injuries & Recovery",
        "lede": "Advanced orthopedic and sports medicine solutions designed to restore mobility, treat injuries, and optimize performance with personalized, minimally invasive care.",
        "img": "svc-ortho.jpg",
        "img_alt": "Orthopedic specialist examining a patient's knee at RegenOrtho Palm Beach in Palm Beach Gardens",
        "why": [
            "Comprehensive care for orthopedic and sports-related conditions",
            "Focus on minimally invasive and joint-preserving treatments",
            "Immediate access to injury consultations and diagnostics",
            "Customized recovery programs designed for long-term results",
            "Patient-centered approach for comfort and confidence",
        ],
        "expertise": [
            ("Advanced Orthopedic Evaluation & Diagnostics", "In-depth evaluations using state-of-the-art imaging and testing methods ensure accurate identification of bone, muscle, and joint conditions for effective treatment planning."),
            ("Sports Medicine Care & Performance Optimization", "Care extends beyond injury treatment to include strength, mobility, and conditioning programs that help athletes and active individuals maximize performance and prevent future injuries."),
            ("Arthroscopic & Minimally Invasive Surgical Techniques", "When surgery is necessary, minimally invasive procedures reduce scarring, shorten recovery, and get you back to activity with less pain."),
            ("Joint Preservation Strategies", "Instead of jumping straight to surgery, we emphasize preserving natural joint function — regenerative therapies, advanced rehabilitation, and cartilage-protecting solutions."),
            ("Same-Day Injury Consultations", "Timely care is critical for orthopedic injuries. Same-day consultations mean rapid diagnosis and immediate treatment options without delay."),
            ("Concierge-Level Surgical Recovery Support", "Recovery doesn't stop after treatment — personalized post-care plans, ongoing monitoring, and guided rehabilitation ensure the smoothest healing process."),
        ],
        "steps": [
            ("Consultation & Diagnosis", "Book an appointment for a full orthopedic or sports medicine evaluation."),
            ("Personalized Treatment Plan", "Receive a care plan tailored to your injury, condition, or performance goals."),
            ("Recovery & Support", "Continue care with guided rehabilitation and long-term wellness strategies."),
        ],
        "faqs": [
            ("What conditions do orthopedic and sports medicine specialists treat?", "We treat joint pain, fractures, ligament injuries, tendon issues, arthritis, and sports-related injuries affecting muscles, bones, and joints."),
            ("Do I need surgery for every orthopedic problem?", "No — most conditions can be managed with non-surgical treatments such as physical therapy, medication, or minimally invasive procedures."),
            ("What is minimally invasive orthopedic surgery?", "A technique that uses small incisions and advanced tools, resulting in less pain, faster healing, and a quicker return to activity."),
            ("Can athletes return to sports after treatment?", "Yes — our recovery programs are designed to restore strength and mobility, helping athletes safely return to their sport or activity."),
            ("How quickly can I book an appointment for an injury?", "We offer same-day injury consultations whenever possible — call the office and we will prioritize acute injuries."),
        ],
        "cta": "Start Your Journey to <em>Pain-Free Living</em>",
        "cta_sub": "Take the first step toward better mobility and faster recovery. Book your consultation today and experience personalized orthopedic and sports medicine care.",
        "conditions": ["knee-pain", "shoulder-pain", "hip-pain", "sports-injuries", "arthritis-joint-pain", "tendon-ligament-injuries"],
    },
    {
        "slug": "podiatric-medicine-foot-ankle-surgery",
        "name": "Podiatric Medicine & Foot/Ankle Surgery",
        "nav": "Podiatric Medicine & Foot/Ankle Surgery",
        "title": "Podiatrist Palm Beach Gardens | Foot & Ankle Surgery",
        "desc": "Board-certified podiatric surgeon in Palm Beach Gardens — minimally invasive foot & ankle surgery, same-day custom orthotics, heel pain relief, and gait correction.",
        "eyebrow": "Podiatric Medicine & Foot/Ankle Surgery",
        "h1": "Precision Foot & Ankle Care for Active Lives",
        "lede": "Advanced podiatric treatment using minimally invasive procedures, same-day custom orthotics, and gait correction to relieve pain and restore confident movement.",
        "img": "svc-podiatry.jpg",
        "img_alt": "Podiatric surgeon assessing a patient's foot health in Palm Beach Gardens",
        "why": [
            "Complete care for common and complex foot & ankle issues",
            "Expertise in minimally invasive surgical procedures",
            "Onsite custom orthotics for same-day comfort",
            "Proven treatments for heel pain and gait correction",
            "Comprehensive recovery programs for long-term mobility",
        ],
        "expertise": [
            ("Comprehensive Podiatric Evaluation & Treatment", "Thorough clinical exams, imaging, and gait analysis identify the root cause of foot and ankle issues, combining evidence-based conservative care with targeted interventions."),
            ("Minimally Invasive In-Office Procedures (MIS)", "In-office minimally invasive techniques correct common conditions through small incisions and local anesthesia — minimizing pain and scarring while shortening recovery."),
            ("Sports Injury Management for Foot & Ankle", "Specialized protocols address sprains, stress fractures, and overuse injuries with focused rehabilitation, progressive strengthening, and return-to-play testing."),
            ("Same-Day Custom Orthotics — Onsite Fabrication", "Custom orthotics are measured, manufactured, and fitted during your visit for immediate biomechanical support, better alignment, and less strain on painful structures."),
            ("Heel Pain Treatment & Gait Correction", "Proven therapies for plantar fasciitis and heel pain combine with gait retraining, orthotic tuning, and tailored exercise plans to reduce symptoms and prevent recurrence."),
            ("Toenail, Bunion & Hammertoe Surgical Care", "Surgical care targets deformities and chronic nail problems with techniques designed to restore function, relieve pain, and support early mobility."),
        ],
        "steps": [
            ("Assessment & Diagnosis", "Comprehensive foot and ankle exam with imaging and gait review to define the problem."),
            ("Personalized Treatment Plan", "Options tailored to your needs: therapy, orthotics, a minimally invasive procedure, or surgery."),
            ("Recovery & Support", "Guided rehabilitation, progressive return-to-activity plans, and routine follow-ups for lasting results."),
        ],
        "faqs": [
            ("What foot and ankle conditions do you treat?", "We treat heel pain, bunions, hammertoes, toenail disorders, sprains, fractures, nerve pain, and biomechanical gait problems."),
            ("Are in-office minimally invasive procedures safe?", "Yes — with proper sterilization and local anesthesia, in-office MIS offers low complication rates and faster recovery versus more invasive surgery."),
            ("How quickly will custom orthotics help?", "Many patients feel improved comfort immediately; full biomechanical benefits develop over days to weeks as your body adapts."),
            ("Do you offer a free foot & ankle guide?", "Yes — download the RegenOrtho Palm Beach Foot & Ankle Guide from our Patient Resources page for prevention and care tips."),
        ],
        "cta": "Walk <em>Confidently</em> Again",
        "cta_sub": "Reclaim comfortable movement — book an assessment for same-day custom orthotics, targeted treatment, and guided rehabilitation for lasting mobility.",
        "conditions": ["foot-ankle-pain", "plantar-fasciitis", "sports-injuries", "peripheral-neuropathy"],
    },
    {
        "slug": "regenerative-medicine-orthobiologics",
        "name": "Regenerative Medicine & Orthobiologic Therapies",
        "nav": "Regenerative Medicine & Orthobiologics",
        "title": "PRP & Regenerative Medicine Palm Beach Gardens | RegenOrtho",
        "desc": "PRP injections, cellular and exosome therapies, peptides, and ultrasound-guided orthobiologics in Palm Beach Gardens — natural healing without surgery.",
        "eyebrow": "Regenerative Medicine & Orthobiologics",
        "h1": "Advanced Regenerative Therapies for Lasting Healing",
        "lede": "Experience natural healing with cutting-edge regenerative therapies designed to repair tissues, restore mobility, and promote faster recovery.",
        "img": "svc-regen.jpg",
        "img_alt": "Regenerative medicine specialist preparing an orthobiologic treatment at RegenOrtho Palm Beach",
        "why": [
            "Evidence-based biologic therapies for natural healing",
            "Non-surgical solutions with minimal downtime",
            "Ultrasound-guided precision treatments",
            "Personalized plans tailored to specific injuries",
            "Innovative therapies combining science and recovery",
        ],
        "expertise": [
            ("PRP (Platelet-Rich Plasma) Injections", "PRP therapy uses a patient's own blood platelets to boost repair — highly effective for tendons, ligaments, and chronic joint conditions."),
            ("Cellular & Exosome Therapies", "Cellular therapies and exosomes help regenerate damaged tissues at the cellular level, accelerating healing and supporting long-term tissue health."),
            ("Peptide Therapy for Recovery, Repair & Performance", "Peptide treatments support muscle recovery, tissue repair, and enhanced cellular communication to improve healing and physical performance."),
            ("Ultrasound-Guided Regenerative Procedures", "Real-time ultrasound guidance ensures treatments are placed exactly where needed — increasing accuracy and improving outcomes."),
            ("Therapies for Joint, Tendon, Ligament & Soft Tissue Injuries", "Targeted biologic treatment for sports injuries, arthritis, and chronic pain promotes natural regeneration where it's needed most."),
            ("Combination Surgical & Regenerative Treatment Plans", "For complex injuries, regenerative medicine can be combined with surgical care to maximize healing, shorten recovery, and improve outcomes."),
        ],
        "steps": [
            ("Comprehensive Evaluation", "A full assessment and imaging to determine the right regenerative therapy."),
            ("Personalized Treatment Plan", "Selection of PRP, cellular therapy, or combination approaches based on your condition."),
            ("Recovery & Monitoring", "Follow-up care and progressive rehabilitation ensure safe healing and long-term results."),
        ],
        "faqs": [
            ("What is regenerative medicine?", "Regenerative medicine uses biologic therapies like PRP, cellular treatments, and peptides to repair tissues and stimulate natural healing."),
            ("Are regenerative treatments safe?", "Most therapies use the patient's own cells or biologic materials, making them minimally invasive and well-tolerated. Every plan is personalized and physician-supervised."),
            ("What conditions benefit from regenerative therapies?", "They are used for arthritis, tendon injuries, ligament tears, soft tissue injuries, sports injuries, and chronic joint pain."),
            ("How long does it take to see results?", "Some patients experience improvement within weeks, while full benefits may develop over several months as tissues heal naturally."),
            ("What is the difference between PRP and cellular therapy?", "PRP stimulates healing with concentrated platelets from your own blood, while cellular and exosome therapies work at the cellular level to support tissue regeneration."),
            ("Can regenerative medicine replace surgery?", "In many cases regenerative therapies may delay or reduce the need for surgery by promoting natural healing — your specialist will advise what's realistic for your condition."),
        ],
        "cta": "Heal Naturally. <em>Recover Stronger.</em>",
        "cta_sub": "Discover the power of regenerative medicine. Schedule your consultation today and take the first step toward natural, lasting recovery.",
        "conditions": ["knee-pain", "shoulder-pain", "arthritis-joint-pain", "tendon-ligament-injuries", "sports-injuries"],
    },
    {
        "slug": "advanced-non-surgical-therapies",
        "name": "Advanced Non-Surgical Therapies",
        "nav": "Advanced Non-Surgical Therapies",
        "title": "EPAT Shockwave & Non-Surgical Therapy Palm Beach Gardens",
        "desc": "EPAT shockwave, cold laser, peptide, and exosome therapies in Palm Beach Gardens — non-surgical pain relief and faster healing with minimal downtime.",
        "eyebrow": "Advanced Non-Surgical Therapies",
        "h1": "Advanced Non-Surgical Therapies for Faster Recovery",
        "lede": "Non-surgical therapies using shockwave, cold laser, peptides, and exosomes to reduce pain, speed healing, and restore function with minimal downtime.",
        "img": "svc-nonsurgical.jpg",
        "img_alt": "Advanced non-surgical therapy session at RegenOrtho Palm Beach",
        "why": [
            "Clinically proven regenerative and energy-based therapies",
            "Targeted, image-guided delivery for precision results",
            "Faster return to daily life and sport versus traditional surgery",
            "Personalized protocols tailored to condition and goals",
            "Integrated rehab plans to maximize long-term outcomes",
        ],
        "expertise": [
            ("EPAT Shockwave Therapy", "High-energy acoustic pulses stimulate blood flow and collagen remodeling in tendons and soft tissue — effective for chronic tendon problems, plantar heel pain, and persistent sports injuries."),
            ("Cold Laser Therapy", "Low-level laser accelerates cellular repair while reducing inflammation and pain, promoting faster tissue regeneration and improved functional recovery."),
            ("Peptide Therapy for Recovery & Performance", "Targeted peptides support connective-tissue repair, reduce inflammation, and optimize recovery timelines — customized for rehabilitation and athletic performance."),
            ("Exosome Therapy", "Exosome treatments deliver cell-signaling vesicles to injured areas to enhance repair, modulate inflammation, and support long-term tissue health."),
            ("Ultrasound-Guided Delivery", "Real-time ultrasound ensures accurate placement of biologics and energy treatments for maximal benefit, safety, and effectiveness."),
            ("Combination & Integrative Protocols", "Shockwave, laser, peptides, and targeted rehab are combined for synergistic healing effects that shorten recovery and reduce recurrence."),
        ],
        "steps": [
            ("Evaluation & Diagnosis", "A focused exam — with imaging when needed — identifies the tissue at fault and whether energy-based or biologic therapy fits."),
            ("Personalized Protocol", "Your plan may combine shockwave, laser, peptides, or exosomes with guided rehabilitation."),
            ("Treatment & Progress Checks", "Most sessions are quick and in-office, with progress tracked visit to visit and the plan tuned as you heal."),
        ],
        "faqs": [
            ("What does EPAT shockwave therapy feel like?", "Most patients describe strong pulses over the treatment area — brief and well-tolerated, with no anesthesia needed and no downtime afterward."),
            ("How many sessions will I need?", "Protocols vary by condition; many tendon and heel-pain protocols involve a short series of weekly sessions. Your specialist will map this out at your evaluation."),
            ("Is there downtime after these therapies?", "Minimal — most patients return to normal activity right away, with temporary soreness possible after shockwave sessions."),
            ("Can these treatments be combined with PRP or other biologics?", "Yes — combination protocols are common and often produce synergistic results. Your plan will sequence therapies for the best outcome."),
        ],
        "cta": "Relief Without a <em>Scalpel</em>",
        "cta_sub": "Book an evaluation to find out whether shockwave, laser, peptide, or exosome therapy can get you moving comfortably again — without surgery.",
        "conditions": ["plantar-fasciitis", "tendon-ligament-injuries", "sports-injuries", "arthritis-joint-pain"],
    },
    {
        "slug": "vein-care",
        "name": "Vein Care — Medical & Cosmetic",
        "nav": "Vein Care — Medical & Cosmetic",
        "title": "Vein Treatment Palm Beach Gardens | Varicose & Spider Veins",
        "desc": "Ultrasound-guided vein care in Palm Beach Gardens — sclerotherapy, endovenous laser & RF ablation, phlebectomy, and cosmetic vein treatment with quick recovery.",
        "eyebrow": "Vein Care — Medical & Cosmetic",
        "h1": "Comprehensive Vein Care — Medical & Cosmetic",
        "lede": "Ultrasound-guided diagnosis and minimally invasive treatments to relieve symptoms, restore healthy circulation, and improve leg appearance with quick recovery.",
        "img": "svc-vein.jpg",
        "img_alt": "Vein specialist performing an ultrasound-guided leg vein evaluation in Palm Beach Gardens",
        "why": [
            "Duplex ultrasound mapping for targeted, evidence-based treatment",
            "Minimally invasive procedures performed in a comfortable office setting",
            "Integrated medical and cosmetic care for both symptoms and appearance",
            "Structured follow-up and prevention strategies to minimize recurrence",
        ],
        "expertise": [
            ("Comprehensive Ultrasound-Guided Vein Evaluation", "A detailed duplex ultrasound maps reflux and identifies the source of symptoms, allowing a precise, individualized treatment plan that avoids unnecessary procedures."),
            ("Sclerotherapy for Spider & Reticular Veins", "Targeted injections close small surface veins to improve leg appearance and reduce localized symptoms — quick, in-office, minimal recovery."),
            ("Endovenous Laser & Radiofrequency (RF) Ablation", "Thermal ablation seals diseased saphenous veins under ultrasound guidance, rerouting blood to healthy vessels and relieving pain, swelling, and the root cause of varicose veins."),
            ("Cosmetic Vein Procedures for Legs, Feet & Ankles", "From surface sclerotherapy to micro-laser treatments, cosmetic techniques refine leg contours and correct visible veins with natural, even results."),
            ("Advanced Wound Care for Venous Insufficiency", "For venous ulcers or skin changes, specialized wound management, compression strategies, and coordinated care promote healing and prevent recurrence."),
            ("Ambulatory Phlebectomy & In-Office Vein Removal", "Micro-incision phlebectomy removes superficial varicose veins in-office for immediate contour improvement and symptom relief with a quick return to activity."),
        ],
        "steps": [
            ("Evaluation & Mapping", "Duplex ultrasound identifies problematic veins and guides the treatment plan."),
            ("Targeted In-Office Treatment", "Ablation, sclerotherapy, phlebectomy, or wound care delivered with ultrasound precision."),
            ("Recovery & Prevention", "Post-procedure compression, activity guidance, and follow-up visits preserve results and reduce recurrence."),
        ],
        "faqs": [
            ("What causes varicose and spider veins?", "Weakened vein valves and venous reflux cause blood pooling; risk factors include genetics, pregnancy, prolonged standing, and age."),
            ("What is the difference between medical and cosmetic vein care?", "Medical care treats symptoms and circulation problems and is often covered by insurance; cosmetic care improves appearance and is usually elective."),
            ("Is vein treatment painful?", "Most procedures use local anesthesia or numbing techniques and involve minimal discomfort; post-procedure soreness is usually mild."),
            ("How long until I can resume normal activities?", "Patients often resume light activity the same day, with specific guidance based on the procedure performed."),
        ],
        "cta": "The First Step to <em>Healthier Legs</em>",
        "cta_sub": "Relief and cosmetic improvement start with a vascular evaluation — schedule your appointment for a personalized, evidence-based vein plan.",
        "conditions": ["varicose-spider-veins"],
    },
    {
        "slug": "misha-knee-system",
        "name": "MISHA Knee System",
        "nav": "MISHA Knee System",
        "title": "MISHA Knee System Palm Beach | Implantable Shock Absorber",
        "desc": "The MISHA Knee System — an implantable shock absorber for medial knee osteoarthritis — offered in Palm Beach Gardens for patients not ready for knee replacement.",
        "eyebrow": "MISHA Knee System",
        "h1": "The MISHA Knee System: A Shock Absorber for Your Knee",
        "lede": "An implantable shock absorber designed to relieve pain and improve function in patients with medial knee osteoarthritis — placed outside the joint in an outpatient procedure.",
        "img": "misha-device.jpg",
        "img_alt": "The MISHA Knee System implantable shock absorber device",
        "why": [
            "Reduces peak forces on the knee by over 30% during walking and standing",
            "Placed under the skin but outside the joint — an outpatient procedure",
            "Designed for patients not ready for knee replacement surgery",
            "An option when medication, injections, therapy, or braces haven't been enough",
        ],
        "expertise": [
            ("How It Works", "Overloading the knee joint can lead to the initiation or progression of osteoarthritis — and unloading it can reduce pain and symptoms. Like a car's shock absorber, the MISHA Knee System compresses as you walk or stand, reducing peak forces on the knee by over 30%."),
            ("Outside the Joint, Under the Skin", "The device is placed under the skin but outside the joint itself during an outpatient procedure — preserving your anatomy while offloading the painful medial compartment."),
            ("Who It's For", "If pain in the inner half of your knee limits daily activities, and you've already tried medication, knee injections, physical therapy, or off-loader braces — but you're not ready for knee replacement — you may be a candidate."),
            ("Backed by Research", "The MISHA Knee System's unloading approach is grounded in published biomechanics research on load distribution in early osteoarthritis and medial knee unloading during walking."),
        ],
        "steps": [
            ("Candidacy Evaluation", "Imaging and examination confirm medial-compartment osteoarthritis and whether unloading is right for you."),
            ("Outpatient Procedure", "The shock absorber is placed under the skin, outside the joint, in an outpatient setting."),
            ("Recovery & Follow-Up", "A structured recovery plan restores mobility while your care team monitors progress."),
        ],
        "faqs": [
            ("Am I a candidate for the MISHA Knee System?", "You may be if pain in the inner (medial) half of your knee limits daily activity, you've tried conservative care such as medication, injections, therapy, or braces, and you're not ready for knee replacement. An in-office evaluation confirms candidacy."),
            ("Is the MISHA Knee System a knee replacement?", "No — nothing is removed from your joint. The implant sits under the skin, outside the joint, and works by absorbing load like a shock absorber."),
            ("How much does it reduce knee load?", "During walking or standing, the shock absorber reduces peak forces on the knee by over 30% based on published biomechanical research."),
            ("Where can I learn more?", "Visit MISHAknee.com for device details, then call 833-783-6561 to schedule a candidacy consultation in Palm Beach Gardens."),
        ],
        "cta": "Not Ready for a <em>Knee Replacement?</em>",
        "cta_sub": "Find out if the MISHA Knee System's implantable shock absorber can relieve your medial knee pain — schedule a candidacy evaluation today.",
        "conditions": ["knee-pain", "arthritis-joint-pain"],
    },
    {
        "slug": "mako-robotic-knee-replacement",
        "name": "Mako Robotic-Assisted Total Knee Replacement",
        "nav": "Mako Robotic Knee Replacement",
        "title": "Mako Robotic Knee Replacement Palm Beach Gardens | RegenOrtho",
        "desc": "Mako robotic-arm assisted total knee replacement in Palm Beach Gardens — 3D CT planning, haptic precision, and personalized implant placement by a certified surgeon.",
        "eyebrow": "Mako Robotic-Assisted Surgery",
        "h1": "Mako Robotic-Assisted Total Knee Replacement",
        "lede": "State-of-the-art robotic-arm assisted knee replacement with 3D CT-based planning and haptic guidance — improving surgical accuracy to help you get back to your active life sooner.",
        "img": "knee-implant.jpg",
        "img_alt": "Knee implant model illustrating robotic-assisted total knee replacement",
        "why": [
            "3D CT-based planning personalizes implant placement to your anatomy",
            "Haptic guidance (AccuStop™) keeps bone cuts within your personalized plan",
            "Aims to cut less healthy bone and preserve soft tissue versus manual techniques",
            "Dr. Matarazzo is certified in the MAKO robotic-assisted knee replacement system",
        ],
        "expertise": [
            ("Preoperative CT Scan & Planning", "A high-resolution CT scan builds a 3D model of your knee — bone, cartilage, and alignment — which your surgeon uses to plan implant positioning and joint balance before ever entering the operating room."),
            ("Robotic Precision in the Operating Room", "During surgery, the robotic arm guides bone cuts within the constraints of your personalized plan; haptic feedback (AccuStop™) prevents deviation beyond safe boundaries."),
            ("Implant Placement & Fine Adjustments", "Once bone preparation is complete, the implant is placed and the surgeon fine-tunes alignment and balance based on real-time feedback."),
            ("Recovery & Rehabilitation", "Hospital stays are typically 1–2 nights, with physical therapy often beginning the day after surgery — focusing on range of motion, gait training, and strengthening."),
        ],
        "steps": [
            ("Consultation & Imaging", "Your surgeon reviews your history, exam, and imaging to confirm you're a candidate for robotic-assisted TKA."),
            ("3D Planning & Surgery", "A CT-based 3D plan personalizes your procedure; the robotic arm executes it with haptic precision."),
            ("Guided Recovery", "Structured rehabilitation begins right away, with your care team monitoring milestones through full recovery."),
        ],
        "faqs": [
            ("What is the Mako system?", "Mako is a robotic-arm assisted surgical system developed by Stryker that combines CT-based 3D planning, haptic guidance, and real-time feedback to assist your surgeon in performing precise bone cuts and implant placement."),
            ("Who is a candidate for Mako robotic knee replacement?", "Patients with severe knee arthritis or joint degeneration unresponsive to conservative treatment, persistent pain or stiffness, and sufficient general health for joint replacement surgery."),
            ("Is robotic knee replacement safer than traditional surgery?", "All surgery carries risks — infection, bleeding, clot formation, and implant-related complications among them. Mako's precision aims to reduce cut error and preserve healthy tissue; your surgeon will discuss the risks and benefits for your case."),
            ("How long is recovery?", "Hospital stays are typically 1–2 nights, physical therapy usually starts the next day, and your team guides a progressive return to activity over the following weeks."),
        ],
        "cta": "Precision You Can <em>Stand On</em>",
        "cta_sub": "Considering knee replacement? Ask whether Mako robotic-assisted surgery is right for you — we'll review your imaging, history, and goals together.",
        "conditions": ["knee-pain", "arthritis-joint-pain"],
    },
    {
        "slug": "neuropathy-program",
        "name": "Neuropathy Restoration Program",
        "nav": "Neuropathy Restoration Program",
        "title": "Neuropathy Treatment Palm Beach Gardens | Nerve Restoration",
        "desc": "The Neuropathy Restoration Program in Palm Beach Gardens — IV-enhanced, regenerative nerve repair for burning, tingling, and numbness. Non-surgical and personalized.",
        "eyebrow": "Neuropathy Restoration Program™",
        "h1": "A Comprehensive Nerve Repair & Regenerative Therapy Program",
        "lede": "Reduce burning, tingling, and numbness. Improve nerve function and mobility. Non-surgical, personalized treatment plans that target the root cause of nerve damage — not just the symptoms.",
        "img": "neuro-exam.jpg",
        "img_alt": "Clinician performing a neuropathy evaluation on a patient's foot",
        "why": [
            "Targets the root cause of nerve damage, not just symptom masking",
            "IV-enhanced program pairing systemic support with local treatment",
            "Advanced diagnostics distinguish nerve compression from metabolic causes",
            "Non-surgical, personalized plans with structured follow-up",
        ],
        "expertise": [
            ("IV Therapy with B12", "Systemic nutrient support nourishes nerves from within — high-dose B-complex and methylcobalamin (B12) support myelin regeneration and nerve conduction."),
            ("Regenerative Injections & Advanced Biologics", "Regenerative injections reduce inflammation at the source, with advanced biologic options to support nerve tissue repair."),
            ("Cold Laser & Therapeutic Ultrasound", "Cold laser stimulates nerve repair while therapeutic ultrasound improves circulation and healing in affected regions."),
            ("Advanced Diagnostics", "Careful testing identifies whether symptoms stem from nerve compression or metabolic causes — so treatment targets the actual problem."),
            ("Peptide Protocols", "Targeted peptide protocols are customized to each patient's presentation and treatment goals to support the body's natural healing and regenerative processes."),
            ("Ongoing Optimization", "Twice-monthly systemic nerve support infusions and structured re-evaluation keep your plan tuned — with maintenance, escalation, or targeted-procedure pathways depending on your response."),
        ],
        "steps": [
            ("Consultation & Diagnostics", "A comprehensive evaluation identifies the type and source of your neuropathy."),
            ("Personalized Program", "Your plan combines IV support, regenerative injections, laser, ultrasound, and peptides as indicated."),
            ("Reassess & Maintain", "Progress is measured and the program adapts — maintenance for responders, escalation or targeted evaluation for persistent focal issues."),
        ],
        "faqs": [
            ("What symptoms does the program address?", "Peripheral neuropathy symptoms including burning or tingling, numbness, sharp or shooting pain, and weakness or instability."),
            ("How is this different from just taking nerve pain medication?", "Medications often mask symptoms. This program combines systemic IV support, regenerative injections, laser, ultrasound, and diagnostics to target the root cause of nerve damage."),
            ("What happens after the program?", "If improved, monthly maintenance options are available. Partial improvement may warrant additional regenerative injections. A persistent focal nerve issue may be evaluated for a targeted nerve release procedure."),
            ("Do I need a referral?", "No referral is needed — book a consultation directly and our team will evaluate whether the program fits your situation."),
        ],
        "cta": "Feel Your <em>Feet</em> Again",
        "cta_sub": "Burning, tingling, and numbness deserve more than another prescription. Book a neuropathy consultation and get a plan that targets the root cause.",
        "conditions": ["peripheral-neuropathy", "foot-ankle-pain"],
    },
    {
        "slug": "medical-weight-loss",
        "name": "Medical Weight Loss & GLP-1 Program",
        "nav": "Medical Weight Loss & GLP-1",
        "title": "Medical Weight Loss Palm Beach Gardens | GLP-1 Program",
        "desc": "Physician-supervised medical weight loss in Palm Beach Gardens — GLP-1 therapy, personalized dosing, and ongoing monitoring. Plans starting at $239/month.",
        "eyebrow": "Physician-Supervised Weight Loss",
        "h1": "Physician-Supervised Medical Weight Loss",
        "lede": "Achieve sustainable weight loss with personalized, medically guided treatment designed to support your overall health, mobility, and long-term wellness — plans starting at $239/month.",
        "img": "weightloss.jpg",
        "img_alt": "Physician-supervised medical weight loss consultation in Palm Beach Gardens",
        "why": [
            "Doctor-led weight loss programs with ongoing medical monitoring",
            "Personalized treatment and dosing plans",
            "Focus on metabolism, appetite control, and wellness",
            "Options include compounded therapies and FDA-approved GLP-1 medications",
        ],
        "expertise": [
            ("How GLP-1 Medications Work", "GLP-1 receptor agonists mimic a naturally occurring hormone that regulates blood sugar, appetite, and digestion. By activating GLP-1 receptors, these medications support healthier blood sugar control and reduce hunger signals."),
            ("Personalized Medical Solutions", "From compounded therapies to FDA-approved medications such as Ozempic®, Zepbound®, and Wegovy®, each plan is tailored to your health profile with ongoing medical oversight."),
            ("What to Expect", "Appetite awareness often begins in weeks 1–2, with steadier control and early progress typically developing over the first month — always under physician monitoring."),
            ("Beyond the Medication", "Weight loss connects directly to joint health and mobility. As an integrative practice, we pair your program with orthopedic, wellness, and IV support when it helps your bigger picture."),
        ],
        "steps": [
            ("Intake Assessment", "A medical intake and screening determine whether GLP-1 therapy or another program fits you safely."),
            ("Personalized Plan & Dosing", "Your physician selects the medication and dosing plan matched to your health profile and goals."),
            ("Monitoring & Support", "Regular check-ins track progress, manage side effects, and adjust your plan for sustainable results."),
        ],
        "faqs": [
            ("What medications are available?", "Our physician-supervised solutions include compounded therapies and FDA-approved GLP-1 medications such as Ozempic®, Zepbound®, and Wegovy® — prescribed only when appropriate for you."),
            ("How much does the program cost?", "Plans start at $239 per month; your exact program depends on the medication and monitoring plan your physician recommends."),
            ("Is GLP-1 therapy safe?", "GLP-1 therapy should always be prescribed and monitored by a qualified medical professional. Outcomes and treatment response differ from person to person — our physicians screen carefully and monitor you throughout."),
            ("When will I see results?", "Many patients notice appetite changes within the first two weeks and early weight loss over the first month; individual results vary."),
        ],
        "cta": "Take Control of Your <em>Weight</em> Today",
        "cta_sub": "The first step toward your personalized weight loss goals is a physician intake assessment — book your consultation today.",
        "conditions": ["arthritis-joint-pain", "knee-pain"],
    },
    {
        "slug": "peptide-therapy",
        "name": "Peptide Therapy",
        "nav": "Peptide Therapy",
        "title": "Peptide Therapy Palm Beach Gardens | Physician-Supervised",
        "desc": "Physician-supervised peptide therapy in Palm Beach Gardens — targeted protocols for joint & tendon repair, inflammation, sleep, skin, muscle, and immunity. From $249/month.",
        "eyebrow": "Peptide Therapy",
        "h1": "Targeted Healing, Condition by Condition",
        "lede": "Physician-supervised peptide protocols matched to what you are actually trying to fix — repair, recovery, longevity, and aesthetics. Programs from $249/month.",
        "img": "cells-macro.jpg",
        "img_alt": "Cellular-level view illustrating peptide therapy at RegenOrtho Palm Beach",
        "why": [
            "Physician-supervised from screening through follow-up",
            "Protocols matched to your specific concern, not a one-size stack",
            "Compounds sourced from licensed U.S. 503A/503B pharmacies",
            "Pairs with regenerative injections, IV therapy, and rehab",
            "Programs from $249 per month",
        ],
        "expertise": [
            ("Joint &amp; Tendon Pain", "Protocols built around BPC-157 and TB-500 to support connective-tissue repair alongside your regenerative or rehabilitation plan."),
            ("Chronic Inflammation", "KPV and Thymosin Alpha-1 protocols aimed at calming systemic inflammatory load so other treatments can work."),
            ("Poor Sleep &amp; Fatigue", "DSIP and Epithalon protocols supporting sleep quality and recovery — the foundation most healing depends on."),
            ("Aging Skin &amp; Hair", "GHK-Cu and PT-141 protocols for skin quality, collagen support, and aesthetic goals."),
            ("Muscle Loss", "CJC-1295 and Ipamorelin protocols supporting lean mass retention and training recovery."),
            ("Low Immunity", "Thymosin Beta-4 and LL-37 protocols to support immune resilience."),
        ],
        "steps": [
            ("Consultation &amp; Screening", "A physician reviews your history, goals, and labs where indicated to determine whether peptide therapy is appropriate."),
            ("Your Protocol", "You receive a protocol matched to your concern, with dosing, administration, and timeline explained in plain language."),
            ("Monitoring &amp; Adjustment", "Progress is reviewed and the protocol is adjusted — peptides work best as part of a coordinated plan."),
        ],
        "faqs": [
            ("What is peptide therapy?", "Peptides are short chains of amino acids that act as signaling molecules in the body. Peptide therapy uses targeted, physician-prescribed protocols to support processes like tissue repair, inflammation control, sleep, and recovery."),
            ("How much does it cost?", "Peptide programs start at $249 per month. Your exact protocol and cost are set at consultation based on your goals."),
            ("Is it supervised by a physician?", "Yes. Every protocol is prescribed and monitored by our physicians, and compounds are sourced from licensed U.S. 503A/503B pharmacies."),
            ("Can peptides be combined with other treatments?", "Yes — peptide protocols are frequently paired with regenerative injections, shockwave or laser therapy, IV therapy, and rehabilitation. Our team coordinates the timing."),
            ("Who is not a candidate?", "Candidacy depends on your medical history, medications, and goals. Some patients are not appropriate for peptide therapy, and our physicians will tell you honestly at consultation."),
        ],
        "cta": "Healing, <em>signalled</em>",
        "cta_sub": "Book a consultation to find out whether a physician-supervised peptide protocol fits your recovery, performance, or longevity goals.",
        "conditions": ["tendon-ligament-injuries", "arthritis-joint-pain", "sports-injuries"],
    },
    {
        "slug": "concierge-care",
        "name": "Concierge & Direct-Pay Care",
        "nav": "Concierge & Direct-Pay Care",
        "title": "Concierge Orthopedic Care Palm Beach | Direct-Pay Medicine",
        "desc": "Private concierge and direct-pay orthopedic care in Palm Beach Gardens — same-day diagnostics, private suites, transparent bundled pricing, and direct specialist access.",
        "eyebrow": "Concierge & Cash-Pay Services",
        "h1": "Private Concierge & Direct-Pay Care",
        "lede": "Private, direct-pay care offering same-day diagnostics, tailored treatment planning, private suites, and transparent bundled pricing for streamlined, personalized recovery.",
        "img": "clinic-lounge.jpg",
        "img_alt": "Private concierge lounge inside RegenOrtho Palm Beach",
        "why": [
            "Direct access to board-certified specialists with one-on-one consultations",
            "Same-day diagnostic workup and treatment planning for urgent needs",
            "Private infusion and procedure suites for comfort and safety",
            "Transparent direct-pay and bundled pricing to avoid surprises",
            "Customized recovery pathways designed for faster, measurable outcomes",
        ],
        "expertise": [
            ("One-on-One Consultations with Board-Certified Surgeons", "Private, undivided consultation time with senior clinicians to review history, imaging, and individualized goals — allowing deeper evaluation and immediate clinical decision-making."),
            ("Same-Day Diagnostics & Treatment Planning", "Imaging, labs, and functional testing arranged and reviewed in a single visit when needed, with a personalized treatment plan produced the same day."),
            ("Private IV Therapy & Procedure Suites", "Dedicated infusion and procedure rooms provide a discreet, comfortable environment — staffed and monitored to clinical standards."),
            ("Transparent Bundled Pricing", "Clear, upfront pricing with bundled packages for procedures and recovery programs removes billing uncertainty for private-pay patients."),
            ("Customized Recovery Protocols", "Recovery plans tailored to your lifestyle and goals combine medical, rehab, and wellness components with milestone tracking."),
            ("Concierge Coordination & Aftercare", "Appointments, imaging, home-care instructions, follow-ups, and referrals — managed for you by dedicated care coordinators."),
        ],
        "steps": [
            ("Book & Pre-Screen", "Schedule your concierge visit and complete a brief medical pre-screen to prioritize immediate needs."),
            ("Same-Day Evaluation & Plan", "Comprehensive diagnostics and a tailored treatment plan delivered during the visit."),
            ("Therapy & Coordinated Recovery", "Procedures or therapies in private suites, followed by structured aftercare and scheduled follow-ups."),
        ],
        "faqs": [
            ("Who is concierge care best for?", "Patients who value speed, privacy, and direct clinician access — including executives, athletes, and anyone wanting streamlined, bespoke care."),
            ("Are diagnostics and procedures performed the same day?", "When clinically appropriate, yes — imaging, labs, and treatment planning are frequently completed in a single visit."),
            ("Do you take insurance for concierge services?", "Concierge and bundled services are direct-pay with transparent pricing; many other services at the practice do work with major insurance — our team will walk you through both paths."),
            ("What is included in bundled pricing?", "Bundles are structured around procedures and recovery programs so you know the full cost upfront — your coordinator will detail inclusions before you commit."),
        ],
        "cta": "Fast, Private, <em>Transparent</em> Care",
        "cta_sub": "Reserve a concierge appointment for same-day evaluation, private procedures, and a personalized recovery plan with transparent direct-pay pricing.",
        "conditions": ["sports-injuries", "knee-pain", "shoulder-pain"],
    },
]

CONDITIONS = [
    {"slug": "knee-pain", "name": "Knee Pain",
     "title": "Knee Pain Treatment Palm Beach Gardens | RegenOrtho",
     "desc": "Knee pain treatment in Palm Beach Gardens — from PRP and joint preservation to the MISHA shock absorber and Mako robotic knee replacement. Same-week consultations.",
     "h1": "Knee Pain, Treated at Every Stage",
     "lede": "From early arthritis to bone-on-bone — a full spectrum of knee care under one roof, so your treatment matches your stage, not a one-size-fits-all protocol.",
     "img": "knee-implant.jpg",
     "symptoms": ["Pain on stairs, standing, or first steps in the morning", "Swelling or stiffness after activity", "Instability, catching, or giving way", "Deep aching in the inner (medial) knee", "Pain that has outlasted rest, meds, or injections"],
     "body": "Knee pain is the most common reason patients walk through our doors — and the mistake most practices make is offering only the treatment they happen to sell. Because RegenOrtho Palm Beach spans orthopedic surgery, regenerative medicine, and advanced non-surgical therapies, your plan starts with your knee's actual stage: joint-preserving therapy and biologics when the joint can still be protected, the MISHA implantable shock absorber when medial arthritis needs unloading but you're not ready for replacement, and Mako robotic-assisted total knee replacement when the joint is truly at end stage.",
     "services": ["orthopedic-sports-medicine", "regenerative-medicine-orthobiologics", "misha-knee-system", "mako-robotic-knee-replacement"],
     "faqs": [("Can I avoid knee replacement?", "Often, yes — many knees respond to joint preservation, regenerative injections, or unloading with the MISHA Knee System. When replacement is genuinely the right call, robotic-assisted precision improves the experience. An evaluation tells you which stage you're in."),
              ("What happens at a knee evaluation?", "A focused exam plus imaging review — we identify the pain source, grade the arthritis or injury, and lay out every option that fits, from conservative care to surgery.")]},
    {"slug": "shoulder-pain", "name": "Shoulder Pain",
     "title": "Shoulder Pain Treatment Palm Beach Gardens | RegenOrtho",
     "desc": "Shoulder pain care in Palm Beach Gardens — rotator cuff injuries, arthritis, and sports injuries treated with arthroscopy, regenerative medicine, and expert diagnosis.",
     "h1": "Shoulder Pain & Rotator Cuff Care",
     "lede": "Fellowship-trained shoulder expertise — from minimally invasive arthroscopy to regenerative options for tendons that need help healing.",
     "img": "svc-ortho.jpg",
     "symptoms": ["Pain reaching overhead or behind your back", "Night pain that interrupts sleep", "Weakness lifting or carrying", "Clicking, catching, or stiffness", "Pain after a fall or throwing activity"],
     "body": "Dr. Matarazzo is an expert in minimally invasive procedures and complex reconstructions of the shoulder, with more than 23 years of clinical and surgical experience. Shoulder problems — rotator cuff injuries, arthritis, instability, sports overuse — respond best when the diagnosis is precise: our evaluations combine examination with advanced imaging, and treatment ranges from targeted rehabilitation and ultrasound-guided biologic injections to arthroscopic repair when the tissue genuinely needs it.",
     "services": ["orthopedic-sports-medicine", "regenerative-medicine-orthobiologics", "advanced-non-surgical-therapies"],
     "faqs": [("Do rotator cuff tears always need surgery?", "No — many partial tears and tendinopathies improve with guided rehabilitation and biologic support. Complete tears in active patients often do best with repair; imaging and examination guide the call."),
              ("What regenerative options exist for shoulders?", "PRP and other orthobiologics, delivered under ultrasound guidance, are used for rotator cuff tendinopathy and related soft-tissue problems.")]},
    {"slug": "hip-pain", "name": "Hip Pain",
     "title": "Hip Pain Treatment Palm Beach Gardens | RegenOrtho",
     "desc": "Hip pain evaluation and treatment in Palm Beach Gardens — arthritis, bursitis, and tendon problems addressed with precise diagnosis and joint-preserving care.",
     "h1": "Hip Pain, Diagnosed Precisely",
     "lede": "Groin, lateral hip, and buttock pain have different causes — precise diagnosis is the difference between months of guessing and a plan that works.",
     "img": "recovery-stretch.jpg",
     "symptoms": ["Groin pain with walking or rotation", "Lateral hip pain lying on your side", "Stiffness putting on shoes or socks", "Pain radiating from the back or SI joint", "Reduced stride length or limp"],
     "body": "Hip pain is a diagnostic puzzle: true joint arthritis, trochanteric bursitis, tendon problems, and referred spine pain all present differently and need different treatment. Our orthopedic evaluation locates the actual pain generator with examination and imaging, then matches treatment — activity modification and rehabilitation, image-guided injections, regenerative options for tendon and soft-tissue problems, or surgical referral pathways when the joint is beyond preservation.",
     "services": ["orthopedic-sports-medicine", "regenerative-medicine-orthobiologics"],
     "faqs": [("Why does my hip hurt in the groin?", "Groin pain with rotation is the classic pattern of true hip-joint pathology such as arthritis or labral problems — an exam and imaging distinguish it from tendon or referred pain."),
              ("Can hip arthritis be managed without replacement?", "Earlier stages often respond to a combination of activity strategy, strengthening, and injection-based care; when replacement becomes the right answer, we'll tell you honestly.")]},
    {"slug": "arthritis-joint-pain", "name": "Arthritis & Joint Pain",
     "title": "Arthritis Treatment Palm Beach Gardens | Joint Pain Relief",
     "desc": "Arthritis and chronic joint pain care in Palm Beach Gardens — regenerative medicine, joint preservation, unloading implants, and robotic replacement when needed.",
     "h1": "Arthritis Care Across the Whole Spectrum",
     "lede": "Steroids mask the pain — our goal is a joint environment that hurts less and functions better, stage by stage.",
     "img": "svc-regen.jpg",
     "symptoms": ["Morning stiffness that eases with movement", "Aching that worsens with weather or activity", "Grinding, creaking, or swelling in a joint", "Progressively shorter comfortable walking distance", "Reliance on anti-inflammatories to get through the day"],
     "body": "Osteoarthritis is progressive, but progression is not a straight line to surgery. The practice's philosophy: match the intervention to the stage. Early and moderate arthritis often responds to joint preservation — strengthening, biomechanical correction, and biologic injections such as PRP that address the joint environment rather than masking pain. Medial knee arthritis has a unique middle option in the MISHA implantable shock absorber. And when a joint is end-stage, robotic-assisted replacement offers a precision path back to activity.",
     "services": ["regenerative-medicine-orthobiologics", "orthopedic-sports-medicine", "misha-knee-system", "mako-robotic-knee-replacement"],
     "faqs": [("Are steroid injections bad for my joint?", "Cortisone can provide real short-term relief, but repeated injections in the same joint have been associated with cartilage thinning when overused — one reason we emphasize biologic and mechanical strategies for long-term management."),
              ("Which joints can regenerative medicine help?", "Knees, shoulders, hips, and smaller joints affected by arthritis or soft-tissue degeneration — candidacy depends on stage and imaging findings.")]},
    {"slug": "sports-injuries", "name": "Sports Injuries",
     "title": "Sports Injury Doctor Palm Beach Gardens | Same-Day Care",
     "desc": "Sports injury care in Palm Beach Gardens from a fellowship-trained sports medicine surgeon — same-day consultations, return-to-play programs, and regenerative support.",
     "h1": "Sports Injuries, From Sideline to Return-to-Play",
     "lede": "Care from a surgeon who has covered team sidelines for over two decades — built to get you back to your sport safely, not just out of pain.",
     "img": "sports-recovery.jpg",
     "symptoms": ["Acute injuries — sprains, strains, tears, fractures", "Overuse pain that worsens with training", "Instability or weakness after a prior injury", "Swelling or loss of range after activity", "Performance limited by a nagging problem"],
     "body": "Dr. Matarazzo completed his sports medicine and arthroscopy fellowship at Lenox Hill Hospital in New York City, where he served as an assistant team physician to the New York Jets and New York Islanders — and he has served as head team physician for college and high school athletic programs across two states. That sideline experience shapes how we treat every athlete: rapid access when injuries happen, accurate grading of the damage, and structured return-to-play programs that restore strength and confidence rather than just waiting out the pain.",
     "services": ["orthopedic-sports-medicine", "regenerative-medicine-orthobiologics", "advanced-non-surgical-therapies", "iv-lounge"],
     "faqs": [("How fast can I be seen after an injury?", "We offer same-day injury consultations whenever possible — call the office and acute injuries are prioritized."),
              ("Do you treat weekend athletes or just competitive ones?", "Both — the same diagnostic rigor and recovery structure applies whether you're chasing a championship or a personal best.")]},
    {"slug": "tendon-ligament-injuries", "name": "Tendon & Ligament Injuries",
     "title": "Tendon & Ligament Injury Care Palm Beach Gardens",
     "desc": "Tendonitis, tendinopathy, and ligament injury treatment in Palm Beach Gardens — EPAT shockwave, PRP, and guided rehabilitation for stubborn soft-tissue problems.",
     "h1": "Stubborn Tendon & Ligament Problems, Solved",
     "lede": "Chronic tendon pain rarely heals by resting harder — it responds to therapies that actually change the tissue.",
     "img": "ultrasound-guided.jpg",
     "symptoms": ["Tennis or golfer's elbow that won't quit", "Achilles or patellar tendon pain with activity", "Chronic ankle instability after sprains", "Pain that returns the moment you resume training", "Tenderness and thickening over a tendon"],
     "body": "Chronic tendinopathy is a failed-healing problem: the tissue gets stuck in a degenerative cycle that rest alone rarely breaks. Our toolkit is built for exactly this — EPAT shockwave therapy to stimulate blood flow and collagen remodeling, ultrasound-guided PRP to deliver concentrated growth factors into the damaged tissue, cold laser to calm inflammation, and progressive loading programs that rebuild capacity. Ligament injuries get the same structured approach, from grading through return-to-activity testing.",
     "services": ["advanced-non-surgical-therapies", "regenerative-medicine-orthobiologics", "orthopedic-sports-medicine"],
     "faqs": [("Why didn't rest fix my tendon pain?", "Chronic tendinopathy is degenerative rather than purely inflammatory — the tissue needs a stimulus to remodel, which is what shockwave, biologics, and progressive loading provide."),
              ("How many shockwave sessions do tendons need?", "Most protocols involve a short series of weekly sessions; your specialist will set expectations at your evaluation.")]},
    {"slug": "foot-ankle-pain", "name": "Foot & Ankle Pain",
     "title": "Foot & Ankle Pain Treatment Palm Beach Gardens",
     "desc": "Foot and ankle pain care in Palm Beach Gardens — bunions, hammertoes, sprains, fractures, and nerve pain treated by a board-certified podiatric surgeon.",
     "h1": "Foot & Ankle Pain, Treated at the Source",
     "lede": "Twenty-six bones, thirty-three joints — and one board-certified surgical specialist to figure out which one is ruining your day.",
     "img": "svc-podiatry.jpg",
     "symptoms": ["Bunions, hammertoes, or toe deformities", "Ankle sprains that never fully healed", "Stress fractures or activity-related pain", "Chronic toenail problems", "Pain that changes how you walk"],
     "body": "Dr. Cedeno is board certified in foot surgery by the American Board of Foot & Ankle Surgery and completed a three-year surgical residency in reconstructive and trauma surgery of the foot and ankle. That depth matters: foot pain is frequently misdiagnosed, and the practice's approach — clinical exam, imaging, and gait analysis — identifies the true source before treatment begins. Many conditions resolve with conservative care and same-day custom orthotics; when correction is needed, minimally invasive in-office procedures shorten recovery dramatically.",
     "services": ["podiatric-medicine-foot-ankle-surgery", "advanced-non-surgical-therapies", "neuropathy-program"],
     "faqs": [("Do bunions always need surgery?", "No — padding, footwear changes, and orthotics manage many bunions. When correction is warranted, modern techniques emphasize smaller incisions and faster recovery."),
              ("What if my ankle still feels unstable after a sprain?", "Chronic instability responds to structured strengthening and proprioception work; persistent mechanical instability may need further evaluation.")]},
    {"slug": "plantar-fasciitis", "name": "Plantar Fasciitis & Heel Pain",
     "title": "Plantar Fasciitis Treatment Palm Beach Gardens | Heel Pain",
     "desc": "Plantar fasciitis and heel pain treatment in Palm Beach Gardens — EPAT shockwave, same-day custom orthotics, and gait correction from a board-certified podiatrist.",
     "h1": "Heel Pain That Finally Gets Better",
     "lede": "Those first steps in the morning shouldn't be the hardest part of your day.",
     "img": "podiatry-exam.jpg",
     "symptoms": ["Stabbing heel pain with the first steps of the morning", "Pain after — not during — activity", "Tenderness along the arch or heel", "Pain that improves briefly then returns", "Months of failed home remedies"],
     "body": "Plantar fasciitis is among the most common — and most stubbornly mistreated — foot problems. Our protocol combines proven therapies: biomechanical gait correction and same-day custom orthotics fabricated onsite to offload the fascia, EPAT shockwave therapy to stimulate healing in chronic cases, and tailored stretching and loading plans that prevent recurrence. Patient outcomes speak for themselves — including patients whose plantar fasciitis resolved fully under Dr. Cedeno's care.",
     "services": ["podiatric-medicine-foot-ankle-surgery", "advanced-non-surgical-therapies"],
     "faqs": [("How long does plantar fasciitis take to heal?", "With a structured plan — orthotics, gait correction, and shockwave when indicated — many patients improve substantially within weeks, though chronic cases take longer."),
              ("Do cortisone shots fix plantar fasciitis?", "They can calm a flare but don't correct the mechanics that caused it; that's why our protocol pairs symptom relief with orthotics and gait correction.")]},
    {"slug": "peripheral-neuropathy", "name": "Peripheral Neuropathy",
     "title": "Peripheral Neuropathy Treatment Palm Beach Gardens",
     "desc": "Peripheral neuropathy treatment in Palm Beach Gardens — an IV-enhanced regenerative program targeting burning, tingling, and numbness at the root cause.",
     "h1": "Burning, Tingling, Numbness — Addressed at the Root",
     "lede": "Neuropathy symptoms occur when damaged nerves fail to send proper signals. Masking them isn't a plan — repairing the environment they live in is.",
     "img": "neuro-exam.jpg",
     "symptoms": ["Burning or tingling in the feet or hands", "Numbness or loss of sensation", "Sharp, shooting, or electric pain", "Weakness or balance instability", "Symptoms worse at night"],
     "body": "The Neuropathy Restoration Program is the practice's comprehensive answer to peripheral nerve damage: advanced diagnostics to distinguish compression from metabolic causes, IV therapy with B12 to nourish nerves systemically, regenerative injections to reduce inflammation at the source, cold laser to stimulate repair, therapeutic ultrasound to improve circulation, and customized peptide protocols. The program is structured with defined pathways after completion — maintenance for responders, escalation for partial response, and targeted evaluation for persistent focal nerve issues.",
     "services": ["neuropathy-program", "podiatric-medicine-foot-ankle-surgery", "iv-lounge"],
     "faqs": [("What causes peripheral neuropathy?", "Causes range from metabolic conditions to nerve compression — which is exactly why the program starts with diagnostics that identify your driver before treatment begins."),
              ("Is the program surgical?", "No — it's a non-surgical program. Only a persistent focal nerve issue would prompt evaluation for a targeted nerve release procedure.")]},
    {"slug": "varicose-spider-veins", "name": "Varicose & Spider Veins",
     "title": "Varicose & Spider Vein Treatment Palm Beach Gardens",
     "desc": "Varicose and spider vein treatment in Palm Beach Gardens — duplex ultrasound mapping, laser & RF ablation, sclerotherapy, and cosmetic vein care.",
     "h1": "Healthier, Better-Looking Legs",
     "lede": "Aching, heaviness, swelling, and visible veins usually trace back to one thing: valves that no longer close. We map them, then fix them.",
     "img": "vein-treatment.jpg",
     "symptoms": ["Bulging, rope-like varicose veins", "Visible spider or reticular veins", "Leg heaviness, aching, or swelling by day's end", "Night cramps or restless legs", "Skin changes or slow-healing spots near the ankle"],
     "body": "Vein disease is progressive and underdiagnosed — and treating the visible veins without finding the underlying reflux is why so many treatments elsewhere don't last. Every vein plan here starts with duplex ultrasound mapping to locate the failing valves. Treatment is minimally invasive and office-based: endovenous laser or radiofrequency ablation for diseased saphenous veins, sclerotherapy for spider and reticular veins, micro-incision phlebectomy for surface varicosities, and specialized wound care when venous insufficiency has affected the skin.",
     "services": ["vein-care", "podiatric-medicine-foot-ankle-surgery"],
     "faqs": [("Is vein treatment covered by insurance?", "Medical vein care — treating symptoms and circulation problems — is often covered; cosmetic treatment is usually elective. We verify your benefits before treatment."),
              ("Do varicose veins come back after treatment?", "Treated veins are closed permanently, but new veins can develop over time — structured follow-up and prevention strategies minimize recurrence.")]},
]

PATHWAYS = [
    ("Biologic Therapies", "Stem cells, exosomes &amp; Wharton&rsquo;s jelly for joints &amp; soft tissue.", "from $2,500", "services/regenerative-medicine-orthobiologics.html"),
    ("Peptide Therapy", "Repair, recovery, longevity &amp; aesthetics — physician-supervised.", "from $249/mo", "services/peptide-therapy.html"),
    ("Shockwave &amp; Cold Laser", "Drug-free, non-invasive pain relief — no needles, no downtime.", "from $900", "services/advanced-non-surgical-therapies.html"),
    ("GLP Therapy", "Medically supervised weight loss with GLP-1 &amp; dual-agonists.", "from $239/mo", "services/medical-weight-loss.html"),
    ("IV Therapy &amp; Wellness", "Infusions, IM shots &amp; concierge wellness memberships.", "from $149/mo", "iv-therapy.html"),
]

LOCATIONS = [
    {"slug": "jupiter", "city": "Jupiter",
     "blurb": "Just down the road from Jupiter's beaches, golf communities, and active neighborhoods — many of our sports medicine, foot & ankle, and vein patients make the short trip south along US-1 or I-95 to our Palm Beach Gardens clinic.",
     "angle": "Jupiter is one of the most active communities in South Florida — tennis, golf, boating, running. When injuries or joint pain interrupt that lifestyle, our board-certified specialists are minutes away."},
    {"slug": "north-palm-beach", "city": "North Palm Beach",
     "blurb": "Our clinic sits on Prosperity Farms Road at the edge of North Palm Beach — for most Village residents we're one of the closest orthopedic and vein practices there is.",
     "angle": "From the North Palm Beach Country Club to the marinas, this is a community that stays on its feet. We help keep it that way with same-week orthopedic access and concierge-level care."},
    {"slug": "juno-beach", "city": "Juno Beach",
     "blurb": "A short drive down US-1 from Juno Beach's pier and oceanfront neighborhoods, our Palm Beach Gardens clinic serves Juno Beach residents with orthopedic, podiatric, regenerative, and vein care.",
     "angle": "Beach walkers and pier regulars know what heel pain and joint stiffness can steal. Our specialists treat both — often without surgery."},
    {"slug": "tequesta", "city": "Tequesta",
     "blurb": "Tequesta residents reach us with an easy drive south — worth it for board-certified specialists in orthopedics, podiatry, vein care, and regenerative medicine under one roof.",
     "angle": "For a village built around the water — boating, fishing, paddling — mobility is everything. We offer Tequesta patients concierge access and personalized treatment plans."},
    {"slug": "palm-beach", "city": "Palm Beach",
     "blurb": "Palm Beach residents expect a concierge standard of medicine. Our private suites, same-day diagnostics, and direct-pay bundled pricing were designed for exactly that expectation.",
     "angle": "Discreet, efficient, and personal — concierge orthopedic and regenerative care matched to Palm Beach standards, twenty minutes from the island."},
    {"slug": "west-palm-beach", "city": "West Palm Beach",
     "blurb": "From downtown West Palm Beach, our Palm Beach Gardens clinic is a straight shot north on I-95 — with the full breadth of orthopedic, podiatric, regenerative, vein, and IV wellness care waiting at the other end.",
     "angle": "West Palm Beach professionals and families choose us for direct specialist access, same-day injury consultations, and treatment plans that don't default to surgery."},
    {"slug": "singer-island", "city": "Singer Island",
     "blurb": "Singer Island and Palm Beach Shores residents cross the bridge to reach our Prosperity Farms Road clinic — for vein care, foot & ankle treatment, joint preservation, and IV wellness.",
     "angle": "Island living is walking living. When heel pain, veins, or joints start protesting, our specialists get you back to the beach path."},
    {"slug": "lake-park", "city": "Lake Park",
     "blurb": "Lake Park sits minutes from our clinic — making RegenOrtho Palm Beach a natural choice for orthopedic urgencies, foot and ankle care, and ongoing joint treatment.",
     "angle": "Quick to reach and quick to respond: same-day injury consultations and a full regenerative toolkit, right up the road from Lake Park."},
]

IV_FAQS = [
    ("How long does an infusion take?", "Most IV sessions last 30–60 minutes depending on the formula and infusion rate chosen."),
    ("Are IV infusions safe?", "Yes. All treatments are clinician-supervised, start with a medical pre-screen, and use sterile, pharmaceutical-grade solutions."),
    ("When will I notice benefits?", "Many patients feel improvement within hours; some metabolic or cellular benefits develop over several days with follow-up sessions."),
    ("Can I combine IV therapy with other treatments?", "Yes. IV therapy can complement rehabilitation, recovery plans, or other medical treatments — we will coordinate timing and compatibility."),
    ("How often should I receive infusions?", "Frequency depends on goals: acute recovery may need a short series, while maintenance can be monthly or as advised by your clinician."),
    ("Are there side effects?", "Side effects are uncommon but can include mild bruising or temporary lightheadedness; clinicians monitor you closely during treatment."),
    ("Do you offer packages for athletes or post-op recovery?", "Yes — tailored packages and protocols are available for athletic recovery, surgical recuperation, and chronic support programs."),
]

GENERAL_FAQS = [
    ("What types of patients do you typically help?", "We treat individuals experiencing joint pain, sports injuries, foot and ankle concerns, vein issues, and those exploring regenerative medicine. Our goal is to help patients regain mobility, reduce discomfort, and improve quality of life."),
    ("Do I need a referral to book an appointment?", "No referral is required. You can book directly with our specialists for a consultation and begin your personalized treatment plan."),
    ("Will I definitely need surgery for my condition?", "Not necessarily. Many conditions can be treated with advanced, non-surgical, or minimally invasive procedures. Surgery is only recommended when it's the safest and most effective solution."),
    ("What can I expect at my first appointment?", "Your first visit includes a thorough consultation, medical history review, and diagnostic evaluation if needed. Our team will then create a personalized treatment plan and answer any questions you may have."),
    ("How soon can I see results from treatment?", "Results vary depending on the condition and type of treatment. Some patients notice improvement within days, while others may experience gradual progress over several weeks."),
    ("How safe are regenerative medicine treatments?", "All our regenerative therapies are backed by clinical research and performed by highly trained specialists. Every treatment plan is personalized and designed with patient safety as the top priority."),
    ("Where are you located?", "11380 Prosperity Farms Road, Suite 204–208, Palm Beach Gardens, FL 33410 — serving Jupiter, North Palm Beach, Juno Beach, Tequesta, Palm Beach, West Palm Beach, and surrounding communities."),
    ("What are your office hours?", "Monday through Friday, 8:00 AM to 5:00 PM. Call 833-783-6561 (833-STEM561) to schedule."),
]

INSURANCE_FAQS = [
    ("Do you accept insurance?", "Yes. We work with most major insurance providers and will help verify your coverage before treatment."),
    ("What if a service isn't covered by my plan?", "For uninsured services we offer flexible payment plans and transparent direct-pay options so care remains accessible."),
    ("What is bundled cash pricing?", "Concierge and direct-pay services are offered with clear, upfront bundled pricing for procedures and recovery programs — no billing surprises."),
    ("Is vein treatment covered by insurance?", "Medical vein care that treats symptoms and circulation problems is often covered; cosmetic vein care is usually elective. We verify benefits for you."),
    ("How much is the medical weight loss program?", "Physician-supervised weight loss plans start at $239 per month, depending on the medication and monitoring your physician recommends."),
]


def all_faq_categories():
    cats = [("Getting Started", "start", GENERAL_FAQS)]
    for s in SERVICES:
        cats.append((s["name"], s["slug"], s["faqs"]))
    cats.append(("IV Therapy & Wellness", "iv-therapy", IV_FAQS))
    cats.append(("Insurance & Payment", "insurance", INSURANCE_FAQS))
    return cats


def svc_href(slug, depth=0):
    p = "../" * depth
    if slug == "iv-lounge":
        return f"{p}iv-therapy.html"
    return f"{p}services/{slug}.html"


def svc_name(slug):
    if slug == "iv-lounge":
        return "IV Recovery & Wellness Lounge"
    for s in SERVICES:
        if s["slug"] == slug:
            return s["name"]
    return slug


# ---------------------------------------------------------------------------
# The hero anatomy figure — the moving centerpiece of the homepage
# ---------------------------------------------------------------------------

FIGURE_NODES = [
    # key, x, y, clinical label, href, blurb, label side
    ("shoulder", 292, 168, "Shoulder", "conditions/shoulder-pain.html",
     "Rotator cuff, arthritis & sports injuries — fellowship-trained shoulder care.", "r"),
    ("elbow", 302, 308, "Elbow", "conditions/tendon-ligament-injuries.html",
     "Tennis elbow & stubborn tendinopathy — shockwave, PRP & guided loading.", "r"),
    ("wrist", 144, 398, "Wrist", "services/orthopedic-sports-medicine.html",
     "Hand & wrist sprains, fractures & overuse — precise orthopedic evaluation.", "l"),
    ("spine", 230, 300, "Spine", "services/regenerative-medicine-orthobiologics.html",
     "PRP, cellular & peptide therapies that help the body repair itself.", "l"),
    ("hip", 264, 398, "Hip", "conditions/hip-pain.html",
     "Precise diagnosis for arthritis, bursitis & tendon problems.", "r"),
    ("knee", 207, 560, "Knee", "conditions/knee-pain.html",
     "From PRP to the MISHA shock absorber to Mako robotic replacement.", "l"),
    ("veins", 253, 646, "Veins", "conditions/varicose-spider-veins.html",
     "Ultrasound-guided ablation & sclerotherapy for healthier legs.", "r"),
    ("nerves", 211, 668, "Nerves", "conditions/peripheral-neuropathy.html",
     "The Neuropathy Restoration Program — burning & numbness at the root.", "l"),
    ("ankle", 248, 720, "Ankle & Foot", "conditions/foot-ankle-pain.html",
     "Board-certified foot & ankle surgery, orthotics & heel pain relief.", "r"),
]


def _capsule(x, y):
    """Articulated joint capsule: faint outer ring + condyle dot."""
    return (f'<circle class="fl bone cap-o" pathLength="1" cx="{x}" cy="{y}" r="7"/>'
            f'<circle class="fl bone cap-i" pathLength="1" cx="{x}" cy="{y}" r="2.8"/>')


def _bone(x1, y1, x2, y2, we, ws):
    """Contoured long bone: flared epiphyses, waisted shaft — closed outline."""
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy)
    px, py = -dy / L, dx / L

    def P(t, w):
        return (x1 + dx * t + px * w, y1 + dy * t + py * w)

    f = lambda pt: f"{pt[0]:.1f} {pt[1]:.1f}"
    d = (f"M {f(P(0, we))} C {f(P(.09, we * .8))} {f(P(.13, ws))} {f(P(.2, ws))} "
         f"L {f(P(.8, ws))} C {f(P(.87, ws))} {f(P(.91, we * .8))} {f(P(1, we))} "
         f"Q {f(P(1.055, 0))} {f(P(1, -we))} "
         f"C {f(P(.91, -we * .8))} {f(P(.87, -ws))} {f(P(.8, -ws))} "
         f"L {f(P(.2, -ws))} C {f(P(.13, -ws))} {f(P(.09, -we * .8))} {f(P(0, -we))} "
         f"Q {f(P(-.055, 0))} {f(P(0, we))} Z")
    return f'<path class="fl bone" pathLength="1" d="{d}"/>'


def _skeleton():
    """Anatomical skeleton, ~7.5 heads tall. Center x=230, viewBox 460x780.

    Landmarks (y): crown 32 · chin 134 · shoulders 172 · elbows ~308 ·
    wrists ~398 · hips 400 · knees 560 · ankles 720 · soles ~747.
    """
    P = []
    # ---- skull: dome, temples, zygomatic notches, maxilla, mandible
    P.append('<path class="fl bone" pathLength="1" d="M197 74 C197 46 212 32 230 32 '
             'C248 32 263 46 263 74 C263 85 260 93 255 98 C252 102 249 104 247 107 '
             'C249 113 247 119 243 123 C240 129 236 133 230 134 '
             'C224 133 220 129 217 123 C213 119 211 113 213 107 '
             'C211 104 208 102 205 98 C200 93 197 85 197 74 Z"/>')
    P.append('<rect class="fl bone faint" pathLength="1" x="209" y="76" width="15" height="11" rx="5"/>')
    P.append('<rect class="fl bone faint" pathLength="1" x="236" y="76" width="15" height="11" rx="5"/>')
    P.append('<path class="fl bone faint" pathLength="1" d="M227 95 C226 101 227 105 230 107 C233 105 234 101 233 95 C232 92 228 92 227 95 Z"/>')
    P.append('<path class="fl bone faint" pathLength="1" d="M220 119 L240 119 M222 126 L238 126 M226 119 L226 126 M230 119 L230 126 M234 119 L234 126"/>')
    # ---- vertebral column
    P.append('<path class="fl bone" pathLength="1" d="M230 140 C231 200 229 280 230 358"/>')
    for i in range(6):
        y = 145 + i * 5.2
        P.append(f'<line class="fl bone vert" pathLength="1" x1="{230 - 4.5}" y1="{y:.0f}" x2="{230 + 4.5}" y2="{y:.0f}"/>')
    for i in range(12):
        y = 178 + i * 10.6
        P.append(f'<line class="fl bone vert" pathLength="1" x1="{230 - 6}" y1="{y:.0f}" x2="{230 + 6}" y2="{y:.0f}"/>')
    for i in range(5):
        y = 308 + i * 12
        P.append(f'<line class="fl bone vert" pathLength="1" x1="{230 - 7.5}" y1="{y}" x2="{230 + 7.5}" y2="{y}"/>')
    # ---- sternum + xiphoid
    P.append('<path class="fl bone" pathLength="1" d="M230 178 L230 240"/>')
    P.append('<path class="fl bone faint" pathLength="1" d="M230 240 L230 249"/>')
    # ---- pubic symphysis detail
    P.append('<path class="fl bone faint" pathLength="1" d="M227 413 L233 413 M227 417 L233 417"/>')
    # ---- per-side structures
    for sgn in (-1, 1):
        X = lambda dx: 230 + sgn * dx
        # clavicle + scapular hint (spine + lateral border)
        P.append(f'<path class="fl bone" pathLength="1" d="M{X(4)} 174 C {X(22)} 168 {X(44)} 164 {X(62)} 166"/>')
        P.append(f'<path class="fl bone faint" pathLength="1" d="M{X(58)} 173 L {X(66)} 186 L {X(55)} 221"/>')
        # ribs: 8 tapering pairs
        for i, w in enumerate([24, 34, 42, 49, 54, 56, 53, 47]):
            ys = 184 + i * 12
            if i < 6:
                P.append(f'<path class="fl bone rib" pathLength="1" d="M{X(3)} {ys} C {X(int(w * .92))} {ys + 2} {X(w)} {ys + 10} {X(w - 7)} {ys + 15} C {X(w - 20)} {ys + 19} {X(14)} {ys + 21} {X(7)} {ys + 19}"/>')
            else:
                P.append(f'<path class="fl bone rib" pathLength="1" d="M{X(3)} {ys} C {X(int(w * .92))} {ys + 2} {X(w)} {ys + 10} {X(w - 9)} {ys + 16}"/>')
        # pelvic girdle: crest, ramus, inner fossa, ischial bump
        P.append(f'<path class="fl bone" pathLength="1" d="M{X(6)} 356 C {X(26)} 350 {X(42)} 354 {X(50)} 366 C {X(55)} 376 {X(53)} 390 {X(44)} 398"/>')
        P.append(f'<path class="fl bone" pathLength="1" d="M{X(44)} 398 C {X(38)} 412 {X(26)} 421 {X(12)} 424 C {X(5)} 425 {X(2)} 420 {X(3)} 413"/>')
        P.append(f'<path class="fl bone faint" pathLength="1" d="M{X(10)} 360 C {X(24)} 355 {X(35)} 359 {X(42)} 368"/>')
        P.append(f'<path class="fl bone faint" pathLength="1" d="M{X(20)} 423 C {X(17)} 427 {X(12)} 427 {X(9)} 424"/>')
        # arm: contoured humerus, radius + ulna, suggested hand
        P.append(_bone(X(63), 178, X(71), 298, 5, 2.2))
        P.append(_bone(X(69), 318, X(84), 394, 3.4, 1.5))
        P.append(_bone(X(76), 316, X(88), 392, 3, 1.3))
        P.append(f'<ellipse class="fl bone faint" pathLength="1" cx="{X(88)}" cy="403" rx="4.5" ry="6"/>')
        P.append(f'<path class="fl bone faint" pathLength="1" d="M{X(88)} 409 L {X(86)} 424 M{X(88)} 409 L {X(92)} 425 M{X(88)} 409 L {X(96)} 419"/>')
        # leg: femoral neck, contoured femur, patella, tibia + fibula, foot
        P.append(f'<path class="fl bone" pathLength="1" d="M{X(33)} 401 C {X(38)} 406 {X(41)} 412 {X(42)} 419"/>')
        P.append(_bone(X(43), 424, X(24), 548, 5.5, 2.4))
        P.append(f'<circle class="fl bone faint" pathLength="1" cx="{X(23)}" cy="559" r="4.5"/>')
        P.append(_bone(X(23), 570, X(18), 710, 4.4, 1.9))
        P.append(_bone(X(30), 572, X(24), 706, 2.4, 1.1))
        P.append(f'<path class="fl bone faint" pathLength="1" d="M{X(18)} 726 C {X(15)} 736 {X(19)} 743 {X(28)} 745 L {X(52)} 747 C {X(56)} 747 {X(56)} 743 {X(52)} 741 M{X(44)} 746 L {X(43)} 739 M{X(36)} 745 L {X(35)} 738"/>')
    # ---- sacrum
    P.append('<path class="fl bone" pathLength="1" d="M222 362 L230 400 L238 362"/>')
    # ---- joint capsules
    for dx, y in [(62, 168), (72, 308), (86, 398), (34, 398), (23, 560), (18, 720)]:
        P.append(_capsule(230 - dx, y))
        P.append(_capsule(230 + dx, y))
    return "\n      ".join(P)


def figure_svg(depth=0):
    p = "../" * depth
    nodes = []
    for key, x, y, label, href, blurb, side in FIGURE_NODES:
        lx = 84 if side == "l" else 376
        nx = x - 13 if side == "l" else x + 13
        anchor = "end" if side == "l" else "start"
        tx = lx - 8 if side == "l" else lx + 8
        nodes.append(f"""<a href="{p}{href}" class="bm-node" data-part="{key}" data-label="{label}" data-blurb="{html.escape(blurb)}" aria-label="{label} — explore care options">
      <line class="bm-leader" x1="{nx}" y1="{y}" x2="{lx}" y2="{y}"/>
      <circle class="bm-leader-tip" cx="{lx}" cy="{y}" r="2"/>
      <circle class="bm-halo" cx="{x}" cy="{y}" r="16"/>
      <circle class="bm-ring" cx="{x}" cy="{y}" r="10"/>
      <circle class="bm-dot" cx="{x}" cy="{y}" r="4"/>
      <text class="bm-label" x="{tx}" y="{y + 5}" text-anchor="{anchor}">{label}</text>
      <circle class="bm-hit" cx="{x}" cy="{y}" r="23"/>
    </a>""")
    nodes_html = "\n".join(nodes)
    return f"""<div class="figure-stage" aria-label="Interactive map of the body — choose an area to explore care options">
  <div class="figure-glow" aria-hidden="true"></div>
  <div class="figure-orbit" aria-hidden="true"></div>
  <div class="figure-orbit figure-orbit-2" aria-hidden="true"></div>
  <div class="figure-scan" aria-hidden="true"></div>
  <svg class="figure-svg" viewBox="0 0 460 780" role="group" aria-label="Areas we treat">
    <defs>
      <linearGradient id="boneStroke" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#F7DE8B"/>
        <stop offset=".5" stop-color="#FDC929"/>
        <stop offset="1" stop-color="#DFAF2B"/>
      </linearGradient>
      <radialGradient id="figGlow" cx=".5" cy=".42" r=".62">
        <stop offset="0" stop-color="#FDC929" stop-opacity=".12"/>
        <stop offset=".55" stop-color="#12457F" stop-opacity=".09"/>
        <stop offset="1" stop-color="#12457F" stop-opacity="0"/>
      </radialGradient>
    </defs>
    <ellipse cx="230" cy="390" rx="215" ry="372" fill="url(#figGlow)"/>
    <g class="fig-lines" fill="none" stroke="url(#boneStroke)" stroke-width="1.25" stroke-linecap="round" stroke-linejoin="round">
      {_skeleton()}
    </g>
    {nodes_html}
  </svg>
  <p class="figure-caption" aria-live="polite"><strong class="figure-caption-label">Where does it hurt?</strong><span class="figure-caption-blurb">Hover or tap a point of light to see how we treat it.</span></p>
  <a class="figure-go" href="{p}{FIGURE_NODES[0][4]}" hidden>Explore <span class="figure-go-label">{FIGURE_NODES[0][3]}</span> <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></a>
</div>"""


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------


SVC_ICONS = {
    "orthopedic-sports-medicine": '<g transform="rotate(45 12 12)"><path d="M7.2 10.6 h9.6 M7.2 13.4 h9.6"/><circle cx="5.9" cy="10.5" r="1.9"/><circle cx="5.9" cy="13.5" r="1.9"/><circle cx="18.1" cy="10.5" r="1.9"/><circle cx="18.1" cy="13.5" r="1.9"/></g>',
    "podiatric-medicine-foot-ankle-surgery": '<path d="M9.2 4 C12.4 4 13.9 6.9 13.5 9.8 C13.2 12.2 11.6 13.4 11.4 15.4 C11.2 17.4 12 19.3 10.3 20.4 C8.8 21.3 7 20.4 6.8 18.7 C6.5 16.9 7.6 15.8 7.5 13.8 C7.4 11.7 6.3 10.6 6.4 8.2 C6.5 5.8 7.6 4 9.2 4 Z"/><circle cx="15.6" cy="5.6" r=".9"/><circle cx="17.4" cy="7.3" r=".9"/><circle cx="18.3" cy="9.4" r=".9"/>',
    "regenerative-medicine-orthobiologics": '<path d="M12 3.4 C15 7 17.4 9.8 17.4 13 A5.4 5.4 0 0 1 6.6 13 C6.6 9.8 9 7 12 3.4 Z"/><path d="M9.4 13.2 a2.6 2.6 0 0 0 2.6 2.6"/>',
    "advanced-non-surgical-therapies": '<path d="M13.2 3 L7 13.2 h3.9 L9.4 21 L16.8 10.6 h-3.9 Z"/>',
    "vein-care": '<path d="M12 3 C10 6.8 14 9 12 12.6 C10 16.2 14 18.4 12 21"/><path d="M11.6 8.2 L8.4 10.4 M12.2 14.8 L15.6 17"/>',
    "misha-knee-system": '<path d="M12 3 v2.6 M8.2 6.4 h7.6 l-7.6 2.4 7.6 2.4 -7.6 2.4 7.6 2.4 h-7.6 M12 18.4 V21"/>',
    "mako-robotic-knee-replacement": '<circle cx="6.2" cy="17.8" r="2.1"/><path d="M7.8 16.2 L11 9.8 L15.6 7.2"/><circle cx="16.8" cy="6.4" r="1.7"/><path d="M15.2 9.4 l3 3.2 M18.2 12.6 l1.8 -.6"/>',
    "concierge-care": '<path d="M4.6 17.4 h14.8 M6.2 17.4 a5.8 5.8 0 0 1 11.6 0"/><path d="M12 8.4 V6.6"/><circle cx="12" cy="9.6" r="1.1"/>',
}

def build_home():
    d = 0
    svc_cards = []
    HOME_SVCS = [
        ("orthopedic-sports-medicine", "Same-day injury consults, arthroscopy & joint preservation from a fellowship-trained surgeon.",
         ["Same-day injury consultations", "Arthroscopy & joint preservation", "Sports performance & recovery programs"]),
        ("podiatric-medicine-foot-ankle-surgery", "Board-certified foot & ankle surgery with orthotics fabricated onsite.",
         ["Minimally invasive foot & ankle surgery", "Same-day custom orthotics", "Heel pain & gait correction"]),
        ("regenerative-medicine-orthobiologics", "Biologic therapies that help the body repair itself — without surgery.",
         ["PRP & orthobiologic injections", "Cellular & exosome therapies", "Ultrasound-guided precision"]),
        ("advanced-non-surgical-therapies", "Energy-based and biologic treatments that switch tissue back into repair mode.",
         ["EPAT shockwave therapy", "Cold laser therapy", "Peptide & exosome protocols"]),
        ("vein-care", "Medical & cosmetic vein care with quick, in-office recovery.",
         ["Duplex ultrasound mapping", "Laser & RF ablation", "Sclerotherapy & cosmetic care"]),
        ("misha-knee-system", "An implantable shock absorber for medial knee arthritis.",
         ["Placed outside the joint, outpatient", "Reduces peak knee load by 30%+", "For those not ready for replacement"]),
        ("mako-robotic-knee-replacement", "Robotic-arm assisted knee replacement, personalized to your anatomy.",
         ["3D CT-based surgical planning", "Haptic robotic precision", "Therapy often starts the next day"]),
        ("concierge-care", "Medicine on your timeline — private, fast, and transparent.",
         ["Same-day diagnostics & planning", "Private infusion & procedure suites", "Transparent bundled pricing"]),
    ]
    for i, (slug, blurb, feats) in enumerate(HOME_SVCS, 1):
        name = svc_name(slug)
        feat_html = "".join(f"<li>{f}</li>" for f in feats)
        icon = SVC_ICONS[slug]
        svc_cards.append(f"""<a class="svc-tile reveal" href="services/{slug}.html" style="--d:{(i % 4) * 90}ms" aria-label="{name} — explore this service">
        <span class="svc-ico" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{icon}</svg></span>
        <strong>{name}</strong>
        <span class="svc-tile-sub">{blurb}</span>
        <ul class="svc-tile-list">{feat_html}</ul>
        <span class="svc-tile-go" aria-hidden="true"><svg viewBox="0 0 16 12" width="15" height="11"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></span>
      </a>""")
    svc_cards_html = "\n".join(svc_cards)

    quotes = []
    for i, (text, who, src) in enumerate(TESTIMONIALS):
        quotes.append(f"""<figure class="quote-slide{' is-active' if i == 0 else ''}">
        <blockquote><p>“{text}”</p></blockquote>
        <figcaption><span class="quote-init" aria-hidden="true">{who[0]}</span><span><strong>{who}</strong><small>{src}</small></span></figcaption>
      </figure>""")
    quotes_html = "\n".join(quotes)

    assoc = "".join(
        f'<li><img src="assets/media/{img}?v={asset_v("assets/media/" + img)}" alt="{alt}" height="54" loading="lazy"></li>'
        for img, alt in ASSOCIATIONS
    )

    social_posts = [
        ("ig-ladder.jpg", "The traditional ladder — rest, physical therapy, cortisone, surgery"),
        ("ig-gap.jpg", "Between the last shot and the operating room, there used to be nothing"),
        ("ig-toolkit.jpg", "One toolkit, matched to your tissue — PRP, shockwave, biologics, peptides, laser"),
        ("ig-guide.jpg", "Dr. Cedeno wrote the book on feet that won't heal — a free 28-page patient guide"),
        ("ig-chapters.jpg", "Eight short chapters, zero jargon — inside the regenerative foot & ankle guide"),
        ("ig-peptides.jpg", "What peptide therapy can do for you — physician-supervised protocols"),
        ("ig-pathways.jpg", "Five pathways to recovery at RegenOrtho Palm Beach"),
        ("ig-careteam.jpg", "Meet your care team — Dr. Matarazzo and Dr. Cedeno"),
        ("ig-concierge.jpg", "Concierge care, by design — physician-led and precision-guided"),
    ]
    social_tiles = "".join(
        f"""<a class="social-tile" href="{INSTAGRAM}" rel="noopener" target="_blank" aria-label="Instagram post: {html.escape(cap)}">
        <img src="assets/social/{img}?v={asset_v('assets/social/' + img)}" alt="{html.escape(cap)}" loading="lazy">
      </a>"""
        for img, cap in social_posts
    )

    cond_chips = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in CONDITIONS_NAV)
    loc_chips = "".join(f'<li><a href="{href}">{label}</a></li>' for href, label in LOCATIONS_NAV)

    posts = __import__("blog_content").BLOG_POSTS[:3]
    blog_cards = "".join(
        f"""<a class="post-card reveal" href="blog/{p_['slug']}.html">
        <span class="post-media"><img src="assets/media/{p_['image']}?v={asset_v('assets/media/' + p_['image'])}" alt="" width="640" height="400" loading="lazy"></span>
        <span class="post-tag">{p_['category']}</span>
        <strong>{p_['title']}</strong>
        <em class="svc-more">Read article <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em>
      </a>"""
        for p_ in posts
    )

    body = f"""{nav(d)}
<main id="main">
<section class="hero" id="hero">
  <div class="hero-scene" aria-hidden="true">
    <div class="hero-video-slot">
      <!-- Video drop-in: place the file, then uncomment —
      <video class="hero-video" autoplay muted loop playsinline preload="none"
             poster="assets/video/hero-poster.jpg">
        <source src="assets/video/hero-beach.mp4" type="video/mp4">
      </video> -->
    </div>
    <div class="scene-sky"></div>
    <div class="scene-haze-violet"></div>
    <div class="scene-haze"></div>
    <div class="scene-clouds"><span></span><span></span><span></span></div>
    <div class="scene-cloudband"><span></span><span></span></div>
    <div class="scene-cirrus"></div>
    <div class="scene-birds"></div>
    <div class="scene-rays"></div>
    <div class="scene-sunglow"></div>
    <div class="scene-sun"></div>
    <div class="scene-horizon"></div>
    <div class="scene-headland"></div>
    <div class="scene-ocean"><span class="wave w1"></span><span class="wave w2"></span><span class="wave w3"></span></div>
    <div class="scene-swells"><span class="sw sw1"></span><span class="sw sw2"></span><span class="sw sw3"></span><span class="sw sw4"></span></div>
    <div class="scene-rollers"><span class="roller r1"></span><span class="roller r2"></span><span class="roller r3"></span></div>
    <div class="scene-reflection"></div>
    <div class="scene-sparkles"></div>
    <div class="scene-wash"></div>
    <div class="scene-shore"></div>
    <div class="scene-fronds"></div>
    <div class="scene-vignette"></div>
    <div class="scene-shimmer"></div>
    <div class="hero-scrim"></div>
  </div>
  <div class="hero-inner">
    <div class="hero-copy">
      <p class="eyebrow hero-eyebrow h-rise" style="--hd:.5s">{TAGLINE}</p>
      <h1 class="h-rise" style="--hd:.65s">Where surgery meets <em>innovative regeneration</em></h1>
      <p class="lede h-rise" style="--hd:.82s">Personalized orthopedic, podiatric, and regenerative care in Palm Beach Gardens — led by board-certified surgeons with over 40 years of combined experience.</p>
      <div class="hero-cta-row h-rise" style="--hd:1s">
        <a class="btn btn-gold" href="contact.html#book">Book a Consultation</a>
        <a class="btn btn-ghost-light" href="tel:{PHONE_TEL}">Call {PHONE_VANITY}</a>
      </div>
      <dl class="hero-stats h-rise" style="--hd:1.18s">
        <div><dt><span class="stat-num" data-count="40">40</span>+</dt><dd>years of combined surgical experience</dd></div>
        <div><dt><span class="stat-num" data-count="10000">10,000</span>+</dt><dd>patients helped in Palm Beach</dd></div>
        <div><dt>4.9<span aria-hidden="true">★</span></dt><dd>rated on Google reviews</dd></div>
      </dl>
    </div>
  </div>
  <div class="hero-marquee h-rise" style="--hd:1.35s" aria-hidden="true">
    <div class="marquee-track" data-marquee>
      <span>Orthopedics</span><span>·</span><span>Sports Medicine</span><span>·</span><span>Podiatry</span><span>·</span><span>Regenerative Medicine</span><span>·</span><span>Vein Care</span><span>·</span><span>IV Wellness</span><span>·</span><span>Concierge Care</span><span>·</span>
    </div>
  </div>
</section>

<section class="section section-dark section-anatomy" id="body-map">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="anatomy-inner">
    <div class="anatomy-copy reveal">
      <p class="eyebrow">The Body, Mapped</p>
      <h2>One practice for <em>every point</em> on this figure</h2>
      <p class="anatomy-lede">Most clinics treat one region and refer the rest away. RegenOrtho Palm Beach was built the other way around: orthopedic surgery, podiatry, regenerative medicine, vein care, nerve restoration, and IV wellness — one roof, one record, one team reading the whole picture.</p>
      <ul class="check-list anatomy-list">
        <li>Board-certified surgeons for shoulder, knee, hip, foot &amp; ankle</li>
        <li>Regenerative options before surgery is ever on the table</li>
        <li>Same-week evaluations — often same-day for acute injuries</li>
      </ul>
      <div class="cta-row anatomy-cta">
        <a class="btn btn-gold" href="contact.html#book">Book a Consultation</a>
        <a class="btn btn-ghost-light" href="services/index.html">Explore every service</a>
      </div>
    </div>
    <div class="anatomy-stage">
      {figure_svg(0)}
    </div>
  </div>
</section>

<section class="section section-services" id="services">
  <div class="section-head reveal">
    <p class="eyebrow">One Roof. Every Answer.</p>
    <h2>Specialized care, <em>seven ways</em></h2>
    <p class="section-sub">Orthopedics, podiatry, regenerative medicine, and vein care under one roof — so your plan is built around your body, not around a single specialty's toolkit.</p>
  </div>
  <div class="svc-grid">
    {svc_cards_html}
  </div>
  <p class="section-foot reveal"><a class="btn btn-navy" href="services/index.html">See every service</a></p>
</section>

<section class="section section-dark section-doctors" id="doctors">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="section-head reveal">
    <p class="eyebrow">Meet the Team</p>
    <h2>The specialists <em>behind your care</em></h2>
  </div>
  <div class="doc-grid">
    <a class="doc-card reveal" href="providers/dr-marc-matarazzo.html">
      <span class="doc-photo"><img src="assets/team/marc-matarazzo.jpg?v={asset_v('assets/team/marc-matarazzo.jpg')}" alt="Dr. Marc Matarazzo, MD — board-certified sports medicine and orthopedic surgeon in Palm Beach Gardens" width="450" height="560" loading="lazy"></span>
      <span class="doc-body">
        <strong>Dr. Marc Matarazzo, MD</strong>
        <span class="doc-role">Board-Certified Sports Medicine &amp; Orthopedic Surgeon</span>
        <span class="doc-bio">23+ years of clinical and surgical experience · sports medicine &amp; arthroscopy fellowship at Lenox Hill Hospital · former assistant team physician to the New York Jets and Islanders · certified in MAKO robotic-assisted knee replacement.</span>
        <em class="svc-more">Meet Dr. Matarazzo <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em>
      </span>
    </a>
    <a class="doc-card reveal" href="providers/dr-orlando-cedeno.html" style="--d:120ms">
      <span class="doc-photo"><img src="assets/team/orlando-cedeno.jpg?v={asset_v('assets/team/orlando-cedeno.jpg')}" alt="Dr. Orlando Cedeno, DPM — board-certified podiatric surgeon and vein specialist in Palm Beach Gardens" width="450" height="560" loading="lazy"></span>
      <span class="doc-body">
        <strong>Dr. Orlando Cedeno, DPM</strong>
        <span class="doc-role">Board-Certified Podiatric Surgeon &amp; Vein Specialist</span>
        <span class="doc-bio">Board certified by the American Board of Foot &amp; Ankle Surgery · fellowship-level training in reconstructive and trauma surgery of the foot and ankle at Chestnut Hill Hospital/University of Pennsylvania · fellow, American College of Foot and Ankle Surgeons.</span>
        <em class="svc-more">Meet Dr. Cedeno <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em>
      </span>
    </a>
    <a class="doc-card reveal" href="providers/emily-bahnick.html" style="--d:240ms">
      <span class="doc-photo"><img src="assets/team/emily-bahnick.jpg?v={asset_v('assets/team/emily-bahnick.jpg')}" alt="Emily Bahnick, MSN, RN — IV infusion nurse and care coordinator at RegenOrtho Palm Beach" width="450" height="560" loading="lazy"></span>
      <span class="doc-body">
        <strong>Emily Bahnick, MSN, RN</strong>
        <span class="doc-role">IV Infusion Nurse &amp; Care Coordinator</span>
        <span class="doc-bio">Your IV infusion nurse and care coordinator — passionate about regenerative health, focused on longevity, reducing reliance on pharmaceuticals, and healing from deep within through modern, innovative medicine.</span>
        <span class="doc-stats"><span>10+ years experience</span><span>MSN &middot; BSN</span><span>Registered Nurse</span></span>
        <em class="svc-more">Meet Emily <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em>
      </span>
    </a>
  </div>
  <div class="why-strip reveal">
    <div><strong>Board-Certified Expertise</strong><span>Decades of combined experience in sports orthopedics, podiatry, and vein care</span></div>
    <div><strong>Comprehensive Solutions</strong><span>From surgery to regenerative therapies, we treat the whole patient</span></div>
    <div><strong>Personalized Care</strong><span>Concierge-level access with tailored treatment plans</span></div>
    <div><strong>Advanced Technology</strong><span>State-of-the-art biologics, minimally invasive procedures, and custom recovery solutions</span></div>
  </div>
</section>

<section class="section section-quotes" id="testimonials">
  <div class="section-head reveal">
    <p class="eyebrow">What Our Patients Say</p>
    <h2>Real patients. <em>Real recoveries.</em></h2>
  </div>
  <div class="quote-stage reveal" data-quotes>
    {quotes_html}
    <div class="quote-dots" role="tablist" aria-label="Choose testimonial"></div>
  </div>
</section>

<section class="section section-dark section-pathfinder" id="explore" aria-label="Explore RegenOrtho Palm Beach">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="section-head reveal">
    <p class="eyebrow">Find Your Path</p>
    <h2>Everything, <em>two clicks away</em></h2>
    <p class="section-sub">Fifty-plus pages of care, conditions, and answers — mapped so you never hunt for anything.</p>
  </div>
  <div class="path-grid">
    <nav class="path-col reveal" aria-label="Conditions we treat">
      <h3>Conditions we treat</h3>
      <ul class="path-chips">
        {cond_chips}
      </ul>
    </nav>
    <nav class="path-col reveal" style="--d:90ms" aria-label="Care and wellness programs">
      <h3>Care &amp; wellness</h3>
      <ul class="path-links">
        <li><a href="iv-therapy.html">IV Lounge — full menu &amp; pricing</a></li>
        <li><a href="infusions/index.html">Specialty Infusion Center</a></li>
        <li><a href="services/medical-weight-loss.html">Medical Weight Loss &amp; GLP-1</a></li>
        <li><a href="services/neuropathy-program.html">Neuropathy Restoration Program</a></li>
        <li><a href="services/concierge-care.html">Concierge &amp; Direct-Pay Care</a></li>
      </ul>
    </nav>
    <nav class="path-col reveal" style="--d:180ms" aria-label="For patients">
      <h3>For patients</h3>
      <ul class="path-links">
        <li><a href="providers/dr-marc-matarazzo.html">Meet Dr. Matarazzo</a></li>
        <li><a href="providers/dr-orlando-cedeno.html">Meet Dr. Cedeno</a></li>
        <li><a href="patient-resources.html">Patient resources &amp; insurance</a></li>
        <li><a href="faq.html">Every question, answered</a></li>
        <li><a href="blog/index.html">Blog &amp; insights</a></li>
      </ul>
    </nav>
    <nav class="path-col reveal" style="--d:270ms" aria-label="Service areas near you">
      <h3>Areas we serve</h3>
      <ul class="path-chips">
        {loc_chips}
      </ul>
    </nav>
  </div>
</section>

<section class="section section-social" id="social">
  <div class="section-head reveal">
    <p class="eyebrow">@regenortho_palmbeach</p>
    <h2>Inside the clinic, <em>every week</em></h2>
    <p class="section-sub">Optimize. Recover. Thrive. ⚡ Peptides · weight loss · IV drips · pain modalities · biologic therapies.</p>
  </div>
  <div class="social-rail" data-marquee-rail>
    <div class="social-track" data-marquee>
      {social_tiles}
    </div>
  </div>
  <p class="section-foot reveal"><a class="btn btn-navy" href="{INSTAGRAM}" rel="noopener" target="_blank">Follow on Instagram</a></p>
</section>

<section class="section section-assoc reveal" aria-label="Our associations">
  <p class="eyebrow assoc-eyebrow">Our Associations</p>
  <ul class="assoc-row">
    {assoc}
  </ul>
</section>

<section class="section section-blog" id="from-the-blog">
  <div class="section-head reveal">
    <p class="eyebrow">From the Blog</p>
    <h2>Insights on <em>healing smarter</em></h2>
  </div>
  <div class="post-grid">
    {blog_cards}
  </div>
  <p class="section-foot reveal"><a class="btn btn-navy" href="blog/index.html">Read all articles</a></p>
</section>

{cta_band(d)}
</main>
{footer(d)}"""

    schema = breadcrumb_schema([("", "Home")])
    page = head(
        "Orthopedic, Regenerative & Vein Care Palm Beach Gardens | RegenOrtho",
        "RegenOrtho Palm Beach: concierge orthopedic, podiatric, regenerative & vein care in Palm Beach Gardens. Board-certified surgeons, 40+ years combined experience. 833-STEM561.",
        depth=d, canonical="index.html", extra_schema=schema,
    ) + f'<body class="page-home">\n' + body
    write("index.html", page)

def therapy_schema(svc):
    return extra_ld({
        "@context": "https://schema.org",
        "@type": "MedicalTherapy",
        "@id": f"{BASE}/services/{svc['slug']}.html#service",
        "name": svc["name"],
        "description": svc["desc"],
        "url": f"{BASE}/services/{svc['slug']}.html",
        "provider": {"@id": ORG_ID},
    })


def build_services():
    d = 1
    # ---- individual service pages ----
    for svc in SERVICES:
        why = "".join(f"<li>{w}</li>" for w in svc["why"])
        cards = "".join(
            f"""<article class="exp-card reveal" style="--d:{(i % 3) * 90}ms">
            <span class="exp-num" aria-hidden="true">{i + 1:02d}</span>
            <h3>{t}</h3><p>{b}</p>
          </article>"""
            for i, (t, b) in enumerate(svc["expertise"])
        )
        steps = "".join(
            f"""<li class="step reveal" style="--d:{i * 110}ms"><span class="step-num" aria-hidden="true">{i + 1}</span><h3>{t}</h3><p>{b}</p></li>"""
            for i, (t, b) in enumerate(svc["steps"])
        )
        faqs = "".join(
            f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
            for q, a in svc["faqs"]
        )
        conds = "".join(
            f'<li><a href="../conditions/{c}.html">{next(x["name"] for x in CONDITIONS if x["slug"] == c)}</a></li>'
            for c in svc.get("conditions", []) if any(x["slug"] == c for x in CONDITIONS)
        )
        conds_html = f"""<aside class="cond-links reveal"><h2>Conditions this helps</h2><ul>{conds}</ul></aside>""" if conds else ""
        crumbs_html = crumbs([("services/index.html", "Services"), ("", svc["name"])], depth=d)
        body = f"""{nav(d)}
<main id="main">
{page_hero(svc['eyebrow'], svc['h1'], svc['lede'], crumbs_html, depth=d)}
<section class="section svc-intro">
  <div class="svc-intro-grid">
    <figure class="svc-photo reveal"><img src="../assets/media/{svc['img']}?v={asset_v('assets/media/' + svc['img'])}" alt="{svc['img_alt']}" width="700" height="470"></figure>
    <div class="svc-why reveal" style="--d:120ms">
      <p class="eyebrow">Why patients choose us</p>
      <h2>Care built around <em>you</em></h2>
      <ul class="check-list">{why}</ul>
      <a class="btn btn-navy" href="../contact.html#book">Book a Consultation</a>
    </div>
  </div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Our Expertise</p><h2>What this service <em>includes</em></h2></div>
  <div class="exp-grid">{cards}</div>
</section>
<section class="section">
  <div class="section-head reveal"><p class="eyebrow">How It Works</p><h2>Three steps to <em>relief</em></h2></div>
  <ol class="steps">{steps}</ol>
</section>
{conds_html}
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Patient Guide &amp; Answers</p><h2>Common <em>questions</em></h2></div>
  <div class="faq-list">{faqs}</div>
  <p class="section-foot"><a href="../faq.html">Browse the full FAQ →</a></p>
</section>
{cta_band(d, heading=svc['cta'], sub=svc['cta_sub'])}
</main>
{footer(d)}"""
        schema = (
            therapy_schema(svc)
            + faq_schema(svc["faqs"])
            + breadcrumb_schema([("", "Home"), ("services/index.html", "Services"), (f"services/{svc['slug']}.html", svc["name"])])
        )
        page = head(svc["title"], svc["desc"], depth=d,
                    canonical=f"services/{svc['slug']}.html",
                    og_image=f"assets/media/{svc['img']}",
                    extra_schema=schema) + '<body class="page-service">\n' + body
        write(f"services/{svc['slug']}.html", page)

    # ---- services index ----
    tiles = "".join(
        f"""<a class="svc-card reveal" href="{s['slug']}.html" style="--d:{(i % 3) * 90}ms">
        <span class="svc-num" aria-hidden="true">{i + 1:02d}</span>
        <span class="svc-media"><img src="../assets/media/{s['img']}?v={asset_v('assets/media/' + s['img'])}" alt="" width="640" height="420" loading="lazy"></span>
        <span class="svc-body"><strong>{s['name']}</strong><span>{s['lede'][:130].rsplit(' ', 1)[0]}…</span><em class="svc-more">Explore <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></span>
      </a>"""
        for i, s in enumerate(SERVICES)
    )
    pathways = "".join(
        f"""<li class="pathway reveal" style="--d:{i * 70}ms">
      <span class="pathway-num" aria-hidden="true">{i + 1:02d}</span>
      <a class="pathway-name" href="../{href}"><strong>{nm}</strong><span>{sub}</span></a>
      <span class="pathway-price">{price}</span>
    </li>"""
        for i, (nm, sub, price, href) in enumerate(PATHWAYS)
    )
    crumbs_html = crumbs([("", "Our Services")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Our Services", "Specialized treatment, all under one roof", "Orthopedics, podiatry, regenerative medicine, vein care, IV wellness, and concierge programs — board-certified specialists with one shared goal: help you move better, heal faster, and live healthier.", crumbs_html, depth=d)}
<section class="section">
  <div class="svc-grid svc-grid-3">{tiles}
    <a class="svc-card reveal" href="../iv-therapy.html">
      <span class="svc-num" aria-hidden="true">{len(SERVICES) + 1:02d}</span>
      <span class="svc-media"><img src="../assets/media/iv-hero.jpg?v={asset_v('assets/media/iv-hero.jpg')}" alt="" width="640" height="420" loading="lazy"></span>
      <span class="svc-body"><strong>IV Recovery &amp; Wellness Lounge</strong><span>Twelve clinician-supervised drips — hydration, immunity, NAD⁺, athletic recovery…</span><em class="svc-more">Explore <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></span>
    </a>
    <a class="svc-card reveal" href="../infusions/index.html">
      <span class="svc-num" aria-hidden="true">{len(SERVICES) + 2:02d}</span>
      <span class="svc-media"><img src="../assets/media/infusion-room.jpg?v={asset_v('assets/media/infusion-room.jpg')}" alt="" width="640" height="420" loading="lazy"></span>
      <span class="svc-body"><strong>Specialty Infusion Center</strong><span>IVIG, Krystexxa, Ocrevus &amp; Ultomiris in a private, monitored outpatient suite…</span><em class="svc-more">Explore <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></span>
    </a>
  </div>
</section>
<section class="section section-dark section-pathways">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="section-head reveal">
    <p class="eyebrow">Our Services</p>
    <h2>Five pathways to <em>recovery</em></h2>
    <p class="section-sub">Starting prices as published by the practice. Your exact plan is quoted at consultation — many services are also insurance-eligible.</p>
  </div>
  <ol class="pathway-list">
    {pathways}
  </ol>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
    schema = breadcrumb_schema([("", "Home"), ("services/index.html", "Our Services")])
    page = head("Our Services | RegenOrtho Palm Beach — Palm Beach Gardens",
                "All RegenOrtho Palm Beach services: orthopedics, podiatry, regenerative medicine, vein care, IV therapy, MISHA & Mako knee solutions, weight loss, and concierge care.",
                depth=d, canonical="services/index.html", extra_schema=schema) + '<body class="page-services">\n' + body
    write("services/index.html", page)


def build_conditions():
    d = 1
    for c in CONDITIONS:
        symptoms = "".join(f"<li>{s}</li>" for s in c["symptoms"])
        svcs = "".join(
            f"""<a class="treat-card reveal" href="{svc_href(s, 0).replace('services/', '../services/').replace('iv-therapy.html', '../iv-therapy.html')}"><strong>{svc_name(s)}</strong><em class="svc-more">Learn more <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></a>"""
            for s in c["services"]
        )
        faqs = "".join(
            f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
            for q, a in c["faqs"]
        )
        crumbs_html = crumbs([("conditions/", "Conditions"), ("", c["name"])], depth=d)
        body = f"""{nav(d)}
<main id="main">
{page_hero("Conditions We Treat", c['h1'], c['lede'], crumbs_html, depth=d)}
<section class="section cond-layout">
  <div class="cond-grid">
    <div class="cond-main reveal">
      <h2>Understanding {c['name'].lower()}</h2>
      <p>{c['body']}</p>
      <h2>How we treat it</h2>
      <div class="treat-grid">{svcs}</div>
    </div>
    <aside class="cond-side reveal" style="--d:120ms">
      <div class="sym-card">
        <h2>Sound familiar?</h2>
        <ul class="check-list">{symptoms}</ul>
        <a class="btn btn-gold" href="../contact.html#book">Get it evaluated</a>
        <p class="sym-call">Or call <a href="tel:{PHONE_TEL}">{PHONE_VANITY}</a> — same-week consultations are usually available.</p>
      </div>
      <figure class="cond-photo"><img src="../assets/media/{c['img']}?v={asset_v('assets/media/' + c['img'])}" alt="{c['name']} care at RegenOrtho Palm Beach" width="520" height="380" loading="lazy"></figure>
    </aside>
  </div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Patient Questions</p><h2>{c['name']} <em>FAQs</em></h2></div>
  <div class="faq-list">{faqs}</div>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
        schema = (
            extra_ld({
                "@context": "https://schema.org",
                "@type": "MedicalCondition",
                "name": c["name"],
                "url": f"{BASE}/conditions/{c['slug']}.html",
                "possibleTreatment": [
                    {"@type": "MedicalTherapy", "name": svc_name(s)} for s in c["services"]
                ],
            })
            + faq_schema(c["faqs"])
            + breadcrumb_schema([("", "Home"), (f"conditions/{c['slug']}.html", c["name"])])
        )
        page = head(c["title"], c["desc"], depth=d,
                    canonical=f"conditions/{c['slug']}.html",
                    og_image=f"assets/media/{c['img']}",
                    page_type="article", extra_schema=schema) + '<body class="page-condition">\n' + body
        write(f"conditions/{c['slug']}.html", page)


def build_locations():
    d = 1
    for loc in LOCATIONS:
        city = loc["city"]
        others = "".join(
            f'<li><a href="{s}.html">{c2}</a></li>'
            for s, c2 in [(l["slug"], l["city"]) for l in LOCATIONS if l["slug"] != loc["slug"]]
        )
        svc_list = "".join(
            f'<a class="treat-card reveal" href="../services/{s["slug"]}.html"><strong>{s["name"]}</strong><em class="svc-more">Learn more <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></a>'
            for s in SERVICES[:6]
        )
        crumbs_html = crumbs([("locations/", "Areas We Serve"), ("", city)], depth=d)
        body = f"""{nav(d)}
<main id="main">
{page_hero(f"Serving {city}", f"Orthopedic, Regenerative &amp; Vein Care for {city}", loc['angle'], crumbs_html, depth=d)}
<section class="section">
  <div class="loc-grid">
    <div class="loc-main reveal">
      <h2>Care for {city} residents — minutes away in Palm Beach Gardens</h2>
      <p>{loc['blurb']}</p>
      <p>Our clinic at {ADDRESS_STREET}, {ADDRESS_CITY} brings together <strong>Dr. Marc Matarazzo, MD</strong> — a board-certified, fellowship-trained orthopedic surgeon with more than 23 years of experience in sports medicine and minimally invasive arthroscopic surgery — and <strong>Dr. Orlando Cedeno, DPM</strong>, board certified in foot surgery by the American Board of Foot &amp; Ankle Surgery with advanced expertise in vein care. Around them: an IV wellness lounge, regenerative medicine program, advanced non-surgical therapies, and concierge-level coordination.</p>
      <h2>What {city} patients come to us for</h2>
      <div class="treat-grid">{svc_list}</div>
      <p class="loc-more">Also available: the <a href="../services/misha-knee-system.html">MISHA Knee System</a>, <a href="../services/mako-robotic-knee-replacement.html">Mako robotic knee replacement</a>, <a href="../services/neuropathy-program.html">Neuropathy Restoration Program</a>, <a href="../services/medical-weight-loss.html">physician-supervised weight loss</a>, and the <a href="../iv-therapy.html">IV Recovery &amp; Wellness Lounge</a>.</p>
    </div>
    <aside class="loc-side reveal" style="--d:120ms">
      <div class="sym-card">
        <h2>Visiting from {city}</h2>
        <address>{ADDRESS_STREET}<br>{ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP}</address>
        <p class="loc-hours">{HOURS}</p>
        <a class="btn btn-gold" href="../contact.html#book">Book a Consultation</a>
        <p class="sym-call">Call <a href="tel:{PHONE_TEL}">{PHONE_VANITY} · {PHONE_DISPLAY}</a></p>
        <a class="loc-map-link" href="{MAP_URL}" rel="noopener" target="_blank">Get directions →</a>
      </div>
      <nav class="sym-card loc-others" aria-label="Other areas we serve">
        <h2>Areas we serve</h2>
        <ul><li><a href="../index.html">Palm Beach Gardens</a></li>{others}</ul>
      </nav>
    </aside>
  </div>
</section>
{cta_band(d, heading=f"{city}, your specialists are <em>closer than you think</em>")}
</main>
{footer(d)}"""
        schema = (
            extra_ld({
                "@context": "https://schema.org",
                "@type": "Service",
                "name": f"Orthopedic, Regenerative & Vein Care for {city}, FL",
                "serviceType": "Orthopedic and regenerative medicine",
                "provider": {"@id": ORG_ID},
                "areaServed": {"@type": "City", "name": city},
                "url": f"{BASE}/locations/{loc['slug']}.html",
            })
            + breadcrumb_schema([("", "Home"), (f"locations/{loc['slug']}.html", city)])
        )
        page = head(
            f"Orthopedic & Regenerative Care {city} FL | RegenOrtho",
            f"{city} residents: board-certified orthopedic, podiatric, regenerative & vein care minutes away in Palm Beach Gardens. Same-week consultations — call 833-STEM561.",
            depth=d, canonical=f"locations/{loc['slug']}.html", extra_schema=schema,
        ) + '<body class="page-location">\n' + body
        write(f"locations/{loc['slug']}.html", page)

MATARAZZO_BIO = [
    "Marc F. Matarazzo, MD is a Board Certified and Fellowship Trained Orthopedic Surgeon specializing in sports medicine and related injuries. He is an expert in minimally invasive procedures and complex reconstructions, as well as joint replacements, of the shoulder and knee. He is certified in the MAKO robotic-assisted knee replacement system and has more than 23 years of clinical and surgical experience. He has a special interest in combining regenerative medicine technology with cutting edge orthopedic surgical and non-surgical care.",
    "Dr. Matarazzo earned his medical degree from The Lewis Katz School of Medicine at Temple University and completed his general surgery internship and orthopedic surgery residency at the Medical College of Pennsylvania and Hahnemann University, now Drexel University in Philadelphia. He then completed a sports medicine and arthroscopy fellowship at Lenox Hill Hospital in New York City where he served as an Assistant Team Physician to the New York Jets, the New York Islanders, and the Hofstra University and Hunter College Athletic Departments.",
    "Dr. Matarazzo is the founder and principal of Elite Sports Medicine serving Palm Beach, Martin, and St Lucie counties of Florida. He has served South Florida since 2002. He held an academic appointment as the Medical Director of the Athletic Training Program at Palm Beach Atlantic University, where he served as their head team physician for over 10 years. Between 2007 and 2020 he served as head team physician for Palm Beach State College and several Palm Beach County high schools. In 2020 he was offered the opportunity to lead the inception of the Sports Medicine Department at Christus Trinity Clinic in Longview, Texas. There, he led a team of certified Athletic Trainers and was head team physician for the athletic departments of East Texas Baptist University and LeTourneau University, as well as over 10 local high schools. He spent countless hours covering Friday night and Saturday football games, supervising Saturday morning injury clinics, and making weekly training room visits.",
    "Dr. Matarazzo is a Fellow of the American Academy of Orthopedic Surgeons and active member of the American Orthopedic Society for Sports Medicine. He has presented both nationally and internationally on a variety of sports medicine topics since 1999.",
]

CEDENO_BIO = [
    "Dr. Cedeno brings a wealth of knowledge and experience to our practice, with a focus on both conservative and surgical treatments for diabetic conditions affecting the lower extremities. His commitment to excellence is evident in his extensive education and training, making him a trusted professional in the field.",
    "After earning his bachelor's degree in chemistry from the University of Pittsburgh in Pennsylvania, Dr. Cedeno pursued his passion for podiatric medicine and surgery at Barry University School of Podiatric Medicine & Surgery in Miami, Florida. Following his academic achievements, he completed a comprehensive three-year surgical residency in reconstructive and trauma surgery of the foot and ankle at the Chestnut Hill Hospital/University of Pennsylvania in Philadelphia. During this intensive program, Dr. Cedeno honed his skills in foot, ankle, and leg surgery under the guidance of renowned podiatric and orthopedic surgeons.",
    "As a testament to his dedication and proficiency, Dr. Cedeno is Board Certified in foot surgery by the American Board of Foot & Ankle Surgery. He is a fellow of the American College of Foot and Ankle Surgeons and a diplomate of the American Board of Podiatric Surgery. Dr. Cedeno is also an esteemed member of the American Podiatric Medical Association, as well as the Florida and Virginia Podiatric Medical Associations. Additionally, he holds the title of Associate of the American Podiatric Sports Medicine Association, showcasing his commitment to advancing podiatric care in all aspects.",
]


def physician_schema(name, photo, title_str, url_path, same_as=None, schema_type="Physician"):
    obj = {
        "@context": "https://schema.org",
        "@type": schema_type,
        "name": name,
        "jobTitle": title_str,
        "image": f"{BASE}/assets/{photo}",
        "url": f"{BASE}/{url_path}",
        "worksFor": {"@id": ORG_ID},
        "address": {
            "@type": "PostalAddress",
            "streetAddress": ADDRESS_STREET,
            "addressLocality": ADDRESS_CITY,
            "addressRegion": ADDRESS_STATE,
            "postalCode": ADDRESS_ZIP,
        },
        "telephone": "+1-833-783-6561",
    }
    if same_as:
        obj["sameAs"] = same_as
    return extra_ld(obj)


def provider_page(slug, name, role, photo, bio_paras, highlights, title, desc, focus_links,
                  schema_type="Physician", eyebrow="Meet Your Specialist",
                  creds_line="", tagline="", quote="", expertise=None, conditions=None):
    d = 1
    paras = "".join(f"<p>{b}</p>" for b in bio_paras)
    hl = "".join(f"<li>{h}</li>" for h in highlights)
    links = "".join(
        f'<a class="treat-card reveal" href="{href}"><strong>{label}</strong><em class="svc-more">Learn more <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></a>'
        for href, label in focus_links
    )
    tagline_html = f"<h2 class=\"provider-tagline\">{tagline}</h2>" if tagline else ""
    quote_html = (f'<blockquote class="provider-quote"><p>{quote}</p>'
                  f'<cite>— {name.split(",")[0]}</cite></blockquote>') if quote else ""
    lists_html = ""
    if expertise or conditions:
        cols = ""
        if expertise:
            cols += ('<div><h3>Areas of expertise</h3><ul class="spec-list">'
                     + "".join(f"<li>{x}</li>" for x in expertise) + "</ul></div>")
        if conditions:
            cols += ('<div><h3>Conditions treated</h3><ul class="spec-list">'
                     + "".join(f"<li>{x}</li>" for x in conditions) + "</ul></div>")
        lists_html = f'<div class="spec-grid">{cols}</div>'
    role_full = f"{role}<span class=\"provider-creds\">{creds_line}</span>" if creds_line else role
    crumbs_html = crumbs([("about.html", "About"), ("", name)], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero(eyebrow, name, role_full, crumbs_html, depth=d)}
<section class="section">
  <div class="provider-grid">
    <figure class="provider-photo reveal">
      <img src="../assets/{photo}?v={asset_v('assets/' + photo)}" alt="{name} — {role} at RegenOrtho Palm Beach" width="560" height="700">
    </figure>
    <div class="provider-bio reveal" style="--d:120ms">
      <div class="sym-card provider-card">
        <h2>Credentials at a glance</h2>
        <ul class="check-list">{hl}</ul>
        <a class="btn btn-gold" href="../contact.html#book">Book with {name.split(',')[0]}</a>
      </div>
      {tagline_html}{quote_html}
      <h2>About {name.split(',')[0]}</h2>
      {paras}
      {lists_html}
      <h2>Explore related care</h2>
      <div class="treat-grid">{links}</div>
    </div>
  </div>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
    schema = (
        physician_schema(name, photo, role, f"providers/{slug}.html", schema_type=schema_type)
        + breadcrumb_schema([("", "Home"), ("about.html", "About"), (f"providers/{slug}.html", name)])
    )
    page = head(title, desc, depth=d, canonical=f"providers/{slug}.html",
                og_image=f"assets/{photo}", page_type="profile",
                extra_schema=schema) + '<body class="page-provider">\n' + body
    write(f"providers/{slug}.html", page)


def build_providers():
    provider_page(
        "dr-marc-matarazzo", "Dr. Marc Matarazzo, MD",
        "Board-Certified Orthopedic Surgeon &amp; Sports Medicine Specialist",
        "team/marc-matarazzo.jpg", MATARAZZO_BIO,
        [
            "Board certified &amp; fellowship trained orthopedic surgeon",
            "23+ years of clinical and surgical experience",
            "Sports medicine &amp; arthroscopy fellowship — Lenox Hill Hospital, NYC",
            "Former assistant team physician: New York Jets &amp; New York Islanders",
            "Certified in the MAKO robotic-assisted knee replacement system",
            "Fellow, American Academy of Orthopedic Surgeons",
            "Member, American Orthopedic Society for Sports Medicine",
            "Medical Director &amp; Owner, RegenOrtho Palm Beach",
            "Owner, Elite Sports Medicine",
        ],
        "Dr. Marc Matarazzo MD | Orthopedic Surgeon Palm Beach Gardens",
        "Dr. Marc Matarazzo, MD — board-certified, fellowship-trained orthopedic surgeon in Palm Beach Gardens. Sports medicine, arthroscopy, shoulder & knee, MAKO robotic knee replacement.",
        [
            ("../services/orthopedic-sports-medicine.html", "Orthopedic & Sports Medicine"),
            ("../services/mako-robotic-knee-replacement.html", "Mako Robotic Knee Replacement"),
            ("../services/misha-knee-system.html", "MISHA Knee System"),
            ("../services/regenerative-medicine-orthobiologics.html", "Regenerative Medicine"),
            ("../conditions/shoulder-pain.html", "Shoulder Pain"),
            ("../conditions/knee-pain.html", "Knee Pain"),
        ],
        creds_line="MD, FAAOS · Medical Director &amp; Owner, RegenOrtho Palm Beach · Owner, Elite Sports Medicine",
        tagline="Surgical expertise. <em>Regenerative first.</em>",
        quote="Many patients facing surgery don&rsquo;t actually need it — and the ones who do deserve to know that honestly. My job is to know the difference.",
        expertise=[
            "Sports Medicine — athletes &amp; active patients",
            "Joint Preservation — knee, shoulder, hip",
            "Regenerative Therapies — biologics, peptides, shockwave, cold laser",
            "Arthroscopic &amp; Joint Surgery",
            "Ultrasound-Guided Injections",
            "Clinical Research — Pharmakon-affiliated",
        ],
        conditions=[
            "Knee osteoarthritis — delay or avoid replacement",
            "Rotator cuff tears &amp; chronic shoulder pain",
            "Tennis &amp; golfer&rsquo;s elbow",
            "Hip OA, impingement &amp; trochanteric pain",
            "Meniscus, ACL/MCL &amp; sports injuries",
            "Tendinopathy &amp; post-surgical pain",
        ],
    )
    build_emily()
    provider_page(
        "dr-orlando-cedeno", "Dr. Orlando Cedeno, DPM",
        "Board-Certified Podiatric Surgeon & Vein Specialist",
        "team/orlando-cedeno.jpg", CEDENO_BIO,
        [
            "Board Certified in foot surgery — American Board of Foot &amp; Ankle Surgery",
            "Three-year surgical residency in reconstructive &amp; trauma surgery of the foot and ankle — Chestnut Hill Hospital/University of Pennsylvania",
            "Fellow, American College of Foot and Ankle Surgeons",
            "Diplomate, American Board of Podiatric Surgery",
            "Member, American Podiatric Medical Association",
            "Associate, American Podiatric Sports Medicine Association",
            "Owner, RegenOrtho Palm Beach &amp; Abacoa Podiatry &amp; Leg Vein Center",
            "Author, <em>The Regenerative Foot &amp; Ankle Guide</em>",
        ],
        "Dr. Orlando Cedeno DPM | Podiatrist Palm Beach Gardens",
        "Dr. Orlando Cedeno, DPM — board-certified podiatric surgeon and vein specialist in Palm Beach Gardens. Foot & ankle surgery, heel pain, custom orthotics, and vein care.",
        [
            ("../services/podiatric-medicine-foot-ankle-surgery.html", "Podiatric Medicine & Foot/Ankle Surgery"),
            ("../services/vein-care.html", "Vein Care — Medical & Cosmetic"),
            ("../services/neuropathy-program.html", "Neuropathy Restoration Program"),
            ("../conditions/plantar-fasciitis.html", "Plantar Fasciitis & Heel Pain"),
            ("../conditions/foot-ankle-pain.html", "Foot & Ankle Pain"),
            ("../conditions/varicose-spider-veins.html", "Varicose & Spider Veins"),
        ],
        creds_line="DPM, FACFAS · Owner, RegenOrtho Palm Beach · Owner, Abacoa Podiatry &amp; Leg Vein Center",
        tagline="A surgeon who <em>treats before he operates.</em>",
        quote="A surgical evaluation doesn&rsquo;t mean a surgical recommendation. Many foot and ankle problems heal with the right regenerative protocol — my job is to know which.",
        expertise=[
            "Foot &amp; Ankle Surgery &amp; Reconstruction",
            "Sports Injuries — Achilles, ligament, tendon",
            "Regenerative Therapies — biologics, peptides, shockwave, cold laser",
            "Vein Care — medical &amp; cosmetic",
            "Diabetic Foot &amp; Wound Care",
            "Ultrasound-Guided Injections",
        ],
        conditions=[
            "Plantar fasciitis &amp; heel pain",
            "Achilles tendinopathy &amp; ruptures",
            "Ankle sprains &amp; chronic instability",
            "Morton&rsquo;s neuroma &amp; nerve pain",
            "Bunions, hammertoes &amp; deformity correction",
            "Varicose &amp; spider veins, venous insufficiency",
        ],
    )


def build_emily():
    provider_page(
        "emily-bahnick", "Emily Bahnick, MSN, RN",
        "IV Infusion Nurse & Care Coordinator",
        "team/emily-bahnick.jpg",
        [
            "Passionate about regenerative health for both people and animals, Emily tailors every care plan to the patient — focused on longevity, reducing reliance on pharmaceuticals, and healing from deep within through modern, innovative medicine.",
            "As the practice's IV infusion nurse and care coordinator, Emily is the clinician most patients see the most. She reviews your pre-treatment medical screen, helps match the infusion formula to your goals, administers and monitors your drip in the lounge, and keeps the details of your care moving between visits.",
            "Emily holds both MSN and BSN nursing degrees and brings more than ten years of nursing experience to RegenOrtho Palm Beach.",
        ],
        [
            "MSN &amp; BSN — advanced nursing degrees",
            "Registered Nurse (RN)",
            "10+ years of nursing experience",
            "IV infusion nurse &amp; care coordinator",
            "Focused on longevity and regenerative health",
        ],
        "Emily Bahnick, MSN, RN | IV Infusion Nurse Palm Beach Gardens",
        "Meet Emily Bahnick, MSN, RN — the IV infusion nurse and care coordinator at RegenOrtho Palm Beach in Palm Beach Gardens, with 10+ years of nursing experience.",
        [
            ("../iv-therapy.html", "IV Recovery & Wellness Lounge"),
            ("../infusions/index.html", "Specialty Infusion Center"),
            ("../services/neuropathy-program.html", "Neuropathy Restoration Program"),
            ("../services/medical-weight-loss.html", "Medical Weight Loss & GLP-1"),
            ("../services/concierge-care.html", "Concierge & Direct-Pay Care"),
        ],
        schema_type="Person", eyebrow="Meet Your Care Team",
    )


def build_about():
    d = 0
    team_cards = ""
    for t in TEAM:
        stats = ""
        if t.get("stats"):
            stats = '<span class="doc-stats">' + "".join(f"<span>{x}</span>" for x in t["stats"]) + "</span>"
        team_cards += f"""<a class="doc-card reveal" href="providers/{t['slug']}.html">
      <span class="doc-photo"><img src="assets/{t['photo']}?v={asset_v('assets/' + t['photo'])}" alt="{t['name']} — {t['role']}" width="450" height="560" loading="lazy"></span>
      <span class="doc-body"><strong>{t['name']}</strong><span class="doc-role">{t['role']}</span><span class="doc-bio">{t['short']}</span>{stats}<em class="svc-more">Full profile <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></span>
    </a>"""
    support = ""
    for s in SUPPORT_TEAM:
        photo = (
            f'<img src="assets/{s["photo"]}?v={asset_v("assets/" + s["photo"])}" alt="{s["name"]} — {s["role"]}" width="300" height="360" loading="lazy">'
            if s["photo"] else f'<span class="team-init" aria-hidden="true">{s["name"][0]}</span>'
        )
        support += f"""<figure class="team-tile reveal"><span class="team-photo">{photo}</span><figcaption><strong>{s['name']}</strong><span>{s['role']}</span></figcaption></figure>"""
    gallery = "".join(
        f"""<figure class="team-tile reveal" style="--d:{(i % 4) * 80}ms"><span class="team-photo"><img src="assets/team/member-{i}.jpg?v={asset_v(f'assets/team/member-{i}.jpg')}" alt="RegenOrtho Palm Beach care team member" width="300" height="400" loading="lazy"></span></figure>"""
        for i in range(1, 8)
    )
    quotes = "".join(
        f"""<figure class="quote-card reveal" style="--d:{(i % 2) * 100}ms"><blockquote><p>“{t}”</p></blockquote><figcaption><span class="quote-init" aria-hidden="true">{w[0]}</span><span><strong>{w}</strong><small>{s}</small></span></figcaption></figure>"""
        for i, (t, w, s) in enumerate(TESTIMONIALS[:4])
    )
    faqs = "".join(
        f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
        for q, a in GENERAL_FAQS[:6]
    )
    crumbs_html = crumbs([("", "About Us")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Our Story", "About RegenOrtho Palm Beach", "Our concierge-based practice blends orthopedic, podiatric, regenerative, and vein care — led by board-certified surgeons with decades of expertise.", crumbs_html, depth=d)}
<section class="section">
  <div class="svc-intro-grid">
    <figure class="svc-photo reveal"><img src="assets/media/clinic-interior.jpg?v={asset_v('assets/media/clinic-interior.jpg')}" alt="Inside the RegenOrtho Palm Beach clinic in Palm Beach Gardens" width="700" height="470"></figure>
    <div class="svc-why reveal" style="--d:120ms">
      <p class="eyebrow">Our Mission</p>
      <h2>Move better. Heal faster. <em>Live healthier.</em></h2>
      <p>At RegenOrtho Palm Beach, we believe every patient deserves personalized, innovative care. From advanced orthopedic and podiatric treatments to cutting-edge regenerative therapies, our mission is to help you move better, heal faster, and live healthier — all in a concierge-level environment.</p>
      <ul class="check-list">
        <li>Personalized treatment plans tailored to each patient's unique needs</li>
        <li>Cutting-edge orthopedic, podiatric, regenerative, and vein therapies</li>
        <li>Concierge-level care with a focus on comfort and convenience</li>
        <li>Board-certified specialists committed to patient success and recovery</li>
      </ul>
    </div>
  </div>
</section>
<section class="section section-dark section-doctors">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="section-head reveal"><p class="eyebrow">Meet the Team</p><h2>Dedicated to <em>your care</em></h2></div>
  <div class="doc-grid">{team_cards}</div>
  <div class="team-strip">
    {support}
  </div>
</section>
<section class="section">
  <div class="section-head reveal"><p class="eyebrow">Our Team</p><h2>The people <em>behind your recovery</em></h2></div>
  <figure class="team-hero reveal">
    <img src="assets/team/team-group.jpg?v={asset_v('assets/team/team-group.jpg')}" alt="The RegenOrtho Palm Beach care team at the Palm Beach Gardens clinic" width="1300" height="1304">
    <figcaption>Orthopedic, podiatric, regenerative, and vein care — one team, one roof, in Palm Beach Gardens.</figcaption>
  </figure>
  <div class="team-gallery">{gallery}</div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">What Our Patients Say</p><h2>Trusted by <em>your neighbors</em></h2></div>
  <div class="quote-grid">{quotes}</div>
</section>
<section class="section">
  <div class="section-head reveal"><p class="eyebrow">Patient Guide &amp; Answers</p><h2>Good to <em>know</em></h2></div>
  <div class="faq-list">{faqs}</div>
  <p class="section-foot"><a href="faq.html">Browse the full FAQ →</a></p>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
    schema = (
        faq_schema(GENERAL_FAQS[:6])
        + breadcrumb_schema([("", "Home"), ("about.html", "About Us")])
    )
    page = head("About Us | RegenOrtho Palm Beach — Palm Beach Gardens FL",
                "Meet RegenOrtho Palm Beach: a concierge practice blending orthopedic, podiatric, regenerative & vein care, led by board-certified surgeons in Palm Beach Gardens.",
                depth=d, canonical="about.html",
                og_image="assets/team/team-group.jpg",
                extra_schema=schema) + '<body class="page-about">\n' + body
    write("about.html", page)


def build_iv():
    d = 0
    cards = ""
    for i, item in enumerate(IV_MENU):
        cards += f"""<article class="iv-card reveal" style="--d:{(i % 3) * 90}ms" id="drip-{i + 1}">
      <span class="iv-bag"><img src="assets/media/{item['bag']}?v={asset_v('assets/media/' + item['bag'])}" alt="" width="150" height="220" loading="lazy"></span>
      <div class="iv-card-body">
        <h3>{item['name']}</h3>
        <p>{item['desc']}</p>
      </div>
      <div class="iv-card-foot"><span class="iv-price">${item['price']}</span><a class="btn btn-sm btn-navy" href="contact.html#book">Book this drip</a></div>
    </article>"""
    faqs = "".join(
        f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
        for q, a in IV_FAQS
    )
    offers = extra_ld({
        "@context": "https://schema.org",
        "@type": "MedicalTherapy",
        "@id": f"{BASE}/iv-therapy.html#service",
        "name": "IV Recovery & Wellness Therapy",
        "description": "Clinician-supervised IV vitamin and nutrient infusions in Palm Beach Gardens — hydration, immune support, NAD+, athletic recovery, and full-body wellness formulas.",
        "url": f"{BASE}/iv-therapy.html",
        "provider": {"@id": ORG_ID},
    })
    crumbs_html = crumbs([("", "IV Therapy Lounge")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("The IV Lounge", "Repair. Rehydrate. Renew.", "Revitalize your body and restore essential nutrients with IV treatments performed by our medical team — in a lounge designed for comfort, not a hospital corridor.", crumbs_html, depth=d)}
<section class="section">
  <div class="section-head reveal"><p class="eyebrow">The Menu</p><h2>Twelve formulas, <em>one goal: you at 100%</em></h2>
  <p class="section-sub">Every infusion starts with a short medical pre-screen and is administered by our clinical team using sterile, pharmaceutical-grade solutions.</p></div>
  <div class="iv-grid">{cards}</div>
</section>
<section class="section section-dark section-iv-how">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="section-head reveal"><p class="eyebrow">How It Works</p><h2>Concierge from <em>booking to boost</em></h2></div>
  <ol class="steps steps-light">
    <li class="step reveal"><span class="step-num" aria-hidden="true">1</span><h3>Schedule Your Appointment</h3><p>Book online or call our friendly team to reserve your spot.</p></li>
    <li class="step reveal" style="--d:110ms"><span class="step-num" aria-hidden="true">2</span><h3>Consultation</h3><p>A certified nurse or clinician discusses your goals and recommends the best IV formula for your needs.</p></li>
    <li class="step reveal" style="--d:220ms"><span class="step-num" aria-hidden="true">3</span><h3>Relax &amp; Receive Treatment</h3><p>Sit back in our comfortable lounge while our medical team administers your customized IV drip.</p></li>
    <li class="step reveal" style="--d:330ms"><span class="step-num" aria-hidden="true">4</span><h3>Feel Revitalized</h3><p>Experience improved hydration, energy, and overall wellness within minutes.</p></li>
  </ol>
</section>
<section class="section">
  <div class="nurse-credit reveal">
    <figure class="nurse-photo"><img src="assets/team/emily-bahnick.jpg?v={asset_v('assets/team/emily-bahnick.jpg')}" alt="Emily Bahnick, MSN, RN — IV infusion nurse at RegenOrtho Palm Beach" width="360" height="450" loading="lazy"></figure>
    <div class="nurse-copy">
      <p class="eyebrow">Your infusion nurse</p>
      <h2>Every drip placed by <em>Emily Bahnick, MSN, RN</em></h2>
      <p>Emily reviews your pre-treatment screen, helps match the formula to your goals, and monitors you through the infusion — with MSN and BSN nursing degrees and more than ten years of nursing experience behind every visit.</p>
      <a class="btn btn-navy" href="providers/emily-bahnick.html">Meet Emily</a>
    </div>
  </div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Patient Guide &amp; Answers</p><h2>IV therapy <em>questions</em></h2></div>
  <div class="faq-list">{faqs}</div>
</section>
{cta_band(d, heading="Feel better <em>today</em>", sub="Visit our infusion lounge for clinically guided IV therapy tailored to recovery, immune support, energy, and metabolic health.")}
</main>
{footer(d)}"""
    schema = offers + faq_schema(IV_FAQS) + breadcrumb_schema([("", "Home"), ("iv-therapy.html", "IV Therapy")])
    page = head("IV Therapy Palm Beach Gardens | Drip Lounge & NAD+ | RegenOrtho",
                "IV therapy in Palm Beach Gardens: hydration, immune boost, NAD+ 500mg, athletic recovery & more — clinician-supervised drips from $189 in a private lounge.",
                depth=d, canonical="iv-therapy.html",
                og_image="assets/media/iv-hero.jpg",
                extra_schema=schema) + '<body class="page-iv">\n' + body
    write("iv-therapy.html", page)


def build_infusions():
    d = 1
    # hub
    tiles = "".join(
        f"""<a class="svc-card reveal" href="{inf['slug']}.html" style="--d:{(i % 2) * 100}ms">
        <span class="svc-num" aria-hidden="true">{i + 1:02d}</span>
        <span class="svc-body svc-body-pad"><strong>{inf['name']}</strong><span>{inf['lede']}</span><em class="svc-more">Learn more <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em></span>
      </a>"""
        for i, inf in enumerate(INFUSIONS)
    )
    crumbs_html = crumbs([("", "Specialty Infusion Center")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Specialty Infusion Center", "Hospital-Grade Infusions. Boutique Setting.", "Physician-prescribed specialty infusions — IVIG, Krystexxa, Ocrevus, and Ultomiris — administered in a private, monitored outpatient suite with insurance coordination and flexible scheduling.", crumbs_html, depth=d)}
<section class="section">
  <div class="svc-intro-grid">
    <figure class="svc-photo reveal"><img src="../assets/media/infusion-room.jpg?v={asset_v('assets/media/infusion-room.jpg')}" alt="Private infusion suite at RegenOrtho Palm Beach" width="700" height="470"></figure>
    <div class="svc-why reveal" style="--d:120ms">
      <p class="eyebrow">Why infuse here</p>
      <h2>The alternative to the <em>hospital chair</em></h2>
      <ul class="check-list">
        <li>Private, monitored infusion suites — not an open hospital bay</li>
        <li>Clinical supervision and pre-infusion screening at every visit</li>
        <li>Coordination with your prescribing physician's protocol</li>
        <li>Insurance coordination and simple scheduling</li>
      </ul>
      <a class="btn btn-navy" href="../contact.html#book">Ask about your infusion</a>
    </div>
  </div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Available Therapies</p><h2>Specialty <em>infusions</em></h2></div>
  <div class="svc-grid svc-grid-2">{tiles}</div>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
    schema = breadcrumb_schema([("", "Home"), ("infusions/index.html", "Specialty Infusion Center")])
    page = head("Specialty Infusion Center Palm Beach Gardens | RegenOrtho",
                "IVIG, Krystexxa, Ocrevus & Ultomiris infusions in a private Palm Beach Gardens outpatient suite — clinician-monitored with insurance coordination.",
                depth=d, canonical="infusions/index.html",
                og_image="assets/media/infusion-room.jpg",
                extra_schema=schema) + '<body class="page-infusions">\n' + body
    write("infusions/index.html", page)

    # individual infusion pages
    for inf in INFUSIONS:
        crumbs_html = crumbs([("infusions/index.html", "Infusion Center"), ("", inf["name"])], depth=d)
        body = f"""{nav(d)}
<main id="main">
{page_hero("Specialty Infusion Center", inf['name'], inf['lede'], crumbs_html, depth=d)}
<section class="section">
  <div class="cond-grid">
    <div class="cond-main reveal">
      <h2>About this therapy</h2>
      <p>{inf['body']}</p>
      <h2>What every infusion visit includes</h2>
      <ul class="check-list">
        <li>Pre-infusion screening and vitals check</li>
        <li>Clinical monitoring throughout your infusion</li>
        <li>A private, comfortable suite — bring headphones, a book, or just rest</li>
        <li>Coordination with your prescribing physician on protocol and follow-up</li>
      </ul>
      <p class="note-line">Specialty infusions are administered on a physician's prescription. Our team helps coordinate referrals, insurance authorization, and scheduling — call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a> to get started.</p>
    </div>
    <aside class="cond-side reveal" style="--d:120ms">
      <div class="sym-card">
        <h2>Getting scheduled</h2>
        <ul class="check-list">
          <li>Have your prescription or referral ready</li>
          <li>We verify insurance and authorization</li>
          <li>Choose an appointment window that fits your week</li>
        </ul>
        <a class="btn btn-gold" href="../contact.html#book">Request scheduling</a>
        <p class="sym-call">Or call <a href="tel:{PHONE_TEL}">{PHONE_VANITY}</a></p>
      </div>
    </aside>
  </div>
</section>
{cta_band(d)}
</main>
{footer(d)}"""
        schema = (
            extra_ld({
                "@context": "https://schema.org",
                "@type": "MedicalTherapy",
                "name": inf["name"],
                "url": f"{BASE}/infusions/{inf['slug']}.html",
                "provider": {"@id": ORG_ID},
            })
            + breadcrumb_schema([("", "Home"), ("infusions/index.html", "Infusion Center"), (f"infusions/{inf['slug']}.html", inf["name"])])
        )
        page = head(inf["title"], inf["desc"], depth=d,
                    canonical=f"infusions/{inf['slug']}.html",
                    og_image="assets/media/infusion-room.jpg",
                    extra_schema=schema) + '<body class="page-infusion">\n' + body
        write(f"infusions/{inf['slug']}.html", page)

def build_faq():
    d = 0
    cats = all_faq_categories()
    chips = "".join(
        f'<button class="faq-chip{" is-active" if i == 0 else ""}" data-cat="{key}" role="tab" aria-selected="{"true" if i == 0 else "false"}">{name}</button>'
        for i, (name, key, _) in enumerate(cats)
    )
    panels = ""
    all_pairs = []
    for i, (name, key, pairs) in enumerate(cats):
        items = "".join(
            f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
            for q, a in pairs
        )
        panels += f"""<section class="faq-panel{' is-active' if i == 0 else ''}" data-cat="{key}" id="{key}" aria-label="{name}">
      <h2 class="faq-cat-title">{name}</h2>
      <div class="faq-list">{items}</div>
    </section>"""
        all_pairs.extend(pairs)
    crumbs_html = crumbs([("", "FAQ")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Patient Guide & Answers", "Frequently Asked Questions", "Everything patients ask us — about getting started, our services, insurance, and what to expect — in one searchable place. Can't find your answer? Call 833-STEM561 and a real person will help.", crumbs_html, depth=d)}
<section class="section faq-section">
  <div class="faq-tools reveal">
    <label class="faq-search"><svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15zM21 21l-5-5"/></svg>
      <span class="sr-only">Search the FAQ</span>
      <input type="search" id="faq-search" placeholder="Search questions… (e.g. PRP, insurance, orthotics)">
    </label>
    <div class="faq-chips" role="tablist" aria-label="FAQ categories">{chips}</div>
  </div>
  <div class="faq-panels" data-faq>
    {panels}
  </div>
  <p class="faq-empty" hidden>No matches — try a different word, or call <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
</section>
{cta_band(d, heading="Still have <em>questions?</em>", sub="Our front desk answers real questions from real humans, Monday through Friday 8–5.")}
</main>
{footer(d)}"""
    schema = faq_schema(all_pairs) + breadcrumb_schema([("", "Home"), ("faq.html", "FAQ")])
    page = head("FAQ | RegenOrtho Palm Beach — Patient Questions Answered",
                "Answers to the most common questions about RegenOrtho Palm Beach: appointments, insurance, regenerative medicine, IV therapy, podiatry, vein care & more.",
                depth=d, canonical="faq.html", extra_schema=schema) + '<body class="page-faq">\n' + body
    write("faq.html", page)


def build_contact():
    d = 0
    crumbs_html = crumbs([("", "Contact Us")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Contact Us", "Your Health Journey Starts Here", "We're here to answer your questions, guide your treatment options, and help you take the next step toward recovery and wellness.", crumbs_html, cta=False, depth=d)}
<section class="section" id="book">
  <div class="contact-grid">
    <div class="contact-info reveal">
      <h2>Get in touch to book your <em>first appointment</em></h2>
      <p>Book your first appointment today and experience personalized care, advanced treatments, and expert support tailored to your health needs.</p>
      <ul class="contact-list">
        <li><strong>Call or text</strong><a href="tel:{PHONE_TEL}">{PHONE_VANITY} · {PHONE_DISPLAY}</a></li>
        <li><strong>Email</strong><a href="mailto:{EMAIL}">{EMAIL}</a></li>
        <li><strong>Visit</strong><a href="{MAP_URL}" rel="noopener" target="_blank">{ADDRESS_STREET}<br>{ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP}</a></li>
        <li><strong>Office hours</strong><span>{HOURS}</span></li>
      </ul>
      <div class="contact-note sym-card">
        <h3>Prefer to chat?</h3>
        <p>Use the <strong>concierge assistant</strong> in the corner of your screen — it can answer common questions instantly and take your appointment request 24/7.</p>
        <button class="btn btn-navy" data-open-assist>Open the assistant</button>
      </div>
    </div>
    <form class="contact-form reveal" style="--d:120ms" action="https://formsubmit.co/{EMAIL}" method="POST">
      <h2 class="form-title">Request an appointment</h2>
      <input type="hidden" name="_subject" value="New appointment request — regenorthopb.com">
      <input type="hidden" name="_captcha" value="false">
      <input type="text" name="_honey" style="display:none" tabindex="-1" autocomplete="off" aria-hidden="true">
      <div class="form-row">
        <label>Name<input type="text" name="name" required autocomplete="name"></label>
        <label>Phone Number<input type="tel" name="phone" required autocomplete="tel"></label>
      </div>
      <label>Email<input type="email" name="email" required autocomplete="email"></label>
      <label>Select Your Service
        <select name="service">
          <option>Orthopedic &amp; Sports Medicine</option>
          <option>Podiatric Medicine &amp; Foot/Ankle Surgery</option>
          <option>Regenerative Medicine &amp; Orthobiologic Therapies</option>
          <option>IV Recovery &amp; Wellness Therapy</option>
          <option>Advanced Non-Surgical Therapies</option>
          <option>Vein Care</option>
          <option>MISHA Knee System</option>
          <option>Mako Robotic Knee Replacement</option>
          <option>Neuropathy Restoration Program</option>
          <option>Medical Weight Loss / GLP-1</option>
          <option>Concierge &amp; Cash-Pay Services</option>
          <option>Specialty Infusion (IVIG, Krystexxa, Ocrevus, Ultomiris)</option>
          <option>Not sure — help me choose</option>
        </select>
      </label>
      <label>Message<textarea name="message" rows="4" placeholder="Tell us briefly what's going on and when you'd like to come in."></textarea></label>
      <button class="btn btn-gold btn-block" type="submit">Book Appointment</button>
      <p class="form-fine">Submitting sends your request straight to our front desk. For anything urgent, call {PHONE_DISPLAY}. Please don't include detailed medical history in this form.</p>
    </form>
  </div>
</section>
<section class="section section-tint contact-map-section">
  <div class="section-head reveal"><p class="eyebrow">Find Us</p><h2>Prosperity Farms Road, <em>Palm Beach Gardens</em></h2></div>
  <div class="map-wrap reveal"><iframe src="https://maps.google.com/maps?q=RegenOrtho%20Palm%20Beach%20Palm%20Beach%20Gardens&t=m&z=13&output=embed&iwloc=near" title="Map to RegenOrtho Palm Beach — 11380 Prosperity Farms Road, Palm Beach Gardens" width="1200" height="420" loading="lazy" allowfullscreen referrerpolicy="no-referrer-when-downgrade"></iframe></div>
</section>
</main>
{footer(d)}"""
    schema = breadcrumb_schema([("", "Home"), ("contact.html", "Contact Us")])
    page = head("Contact RegenOrtho Palm Beach | Book a Consultation",
                "Book a consultation at RegenOrtho Palm Beach — 11380 Prosperity Farms Road, Palm Beach Gardens. Call 833-STEM561 (833-783-6561) or request an appointment online.",
                depth=d, canonical="contact.html", extra_schema=schema) + '<body class="page-contact">\n' + body
    write("contact.html", page)


def build_resources():
    d = 0
    crumbs_html = crumbs([("", "Patient Resources")], depth=d)
    faqs = [
        ("Do I need a referral to book an appointment?", "No referral is required. You can book directly with our specialists for a consultation and begin your personalized treatment plan."),
        ("How do regenerative treatments work?", "Regenerative therapies use your body's natural healing mechanisms — such as growth factors, peptides, or cellular repair — to restore damaged tissues and accelerate recovery."),
        ("How long is recovery after a minimally invasive procedure?", "Recovery is typically much faster than with traditional surgery. Most patients return to normal activities within a few days, depending on the treatment."),
        ("Will my insurance cover the treatment?", "Coverage varies by plan and procedure. Our team will guide you through your insurance options and also provide direct-pay packages."),
    ]
    faq_html = "".join(
        f"""<details class="faq-item"><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>"""
        for q, a in faqs
    )
    body = f"""{nav(d)}
<main id="main">
{page_hero("Patient Resources", "Confident, Informed, Supported", "Answers to common questions, guidance through the treatment process, and helpful tips for before and after your visits — all in one place.", crumbs_html, depth=d)}
<section class="section">
  <div class="res-grid">
    <article class="res-card reveal"><span class="res-num" aria-hidden="true">01</span>
      <h2>Getting Started</h2>
      <p>Whether it's your first visit or a follow-up, knowing what to expect makes your experience smoother.</p>
      <ul class="check-list"><li>What to expect during your first consultation</li><li>Preparing questions for your doctor</li><li>Understanding treatment timelines</li></ul>
    </article>
    <article class="res-card reveal" style="--d:90ms"><span class="res-num" aria-hidden="true">02</span>
      <h2>Insurance &amp; Payment Options</h2>
      <p>We accept a wide range of insurance providers and also offer concierge and direct-pay options for patients seeking flexible care.</p>
      <ul class="check-list"><li>Accepted insurance plans overview</li><li>Transparent billing practices</li><li>Flexible concierge &amp; cash-pay packages</li></ul>
    </article>
    <article class="res-card reveal" style="--d:180ms"><span class="res-num" aria-hidden="true">03</span>
      <h2>Preparing for Your Appointment</h2>
      <p>Your time with our specialists is valuable. Arriving prepared ensures you get the most out of your visit.</p>
      <ul class="check-list"><li>Bring a list of medications</li><li>Wear comfortable clothing for exams</li><li>Note any recent symptoms or health changes</li></ul>
      <p style="margin-top:1rem;"><a href="forms/index.html">Complete your patient forms before you arrive →</a></p>
    </article>
    <article class="res-card reveal" style="--d:270ms"><span class="res-num" aria-hidden="true">04</span>
      <h2>Post-Treatment Care</h2>
      <p>After your treatment, proper care and lifestyle adjustments support faster recovery and better outcomes.</p>
      <ul class="check-list"><li>General recovery tips</li><li>Nutrition and wellness guidance</li><li>When to follow up with your provider</li></ul>
    </article>
  </div>
</section>
<section class="section section-dark guide-band">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="guide-inner reveal">
    <div>
      <p class="eyebrow">Free Download</p>
      <h2>The RegenOrtho Palm Beach <em>Foot &amp; Ankle Guide</em></h2>
      <p>Prevention tips, common conditions, and when to see a specialist — from our board-certified podiatric surgery team.</p>
    </div>
    <a class="btn btn-gold" href="assets/media/foot-ankle-guide.pdf" download>Download the guide (PDF)</a>
  </div>
</section>
<section class="section section-tint">
  <div class="section-head reveal"><p class="eyebrow">Quick Answers</p><h2>Before your <em>first visit</em></h2></div>
  <div class="faq-list">{faq_html}</div>
  <p class="section-foot"><a href="faq.html">Browse the full FAQ →</a></p>
</section>
{cta_band(d, heading="Need more <em>help?</em>", sub="Our patient support team is always available to answer questions, explain treatment options, and guide you through every step of your journey.")}
</main>
{footer(d)}"""
    schema = faq_schema(faqs) + breadcrumb_schema([("", "Home"), ("patient-resources.html", "Patient Resources")])
    page = head("Patient Resources | RegenOrtho Palm Beach",
                "Patient resources for RegenOrtho Palm Beach — first-visit guidance, insurance & payment options, appointment prep, post-treatment care, and a free foot & ankle guide.",
                depth=d, canonical="patient-resources.html", extra_schema=schema) + '<body class="page-resources">\n' + body
    write("patient-resources.html", page)


# ---------------------------------------------------------------------------
# Patient forms
#
# HIPAA: these pages collect protected health information, so they are built to
# keep it in the patient's browser. Nothing is POSTed, no third-party form
# service is involved, and no analytics/tracking script is loaded on them.
# On finish the answers become a printable summary the patient saves or brings
# in. Read the HIPAA NOTES section of README.md before changing that.
# ---------------------------------------------------------------------------

def _field(f, depth=0):
    """Render one field. Clinical inputs default to autocomplete=off so the
    browser doesn't retain health answers for the next person on the device."""
    fid, t = f["id"], f["t"]
    req = f.get("req", False)
    req_attr = ' required aria-required="true"' if req else ""
    req_mark = ' <span class="req" aria-hidden="true">*</span>' if req else ""
    hint_id = f"{fid}-hint"
    hint = f'<span class="f-hint" id="{hint_id}">{f["hint"]}</span>' if f.get("hint") else ""
    described = f' aria-describedby="{hint_id}"' if f.get("hint") else ""
    ac = f' autocomplete="{f["ac"]}"' if f.get("ac") else ' autocomplete="off"'
    wide = " f-half" if f.get("w") == "half" else ""
    ph = f' placeholder="{f["ph"]}"' if f.get("ph") else ""

    if t in ("text", "tel", "email", "date"):
        return (f'<p class="f-row{wide}"><label for="{fid}">{f["label"]}{req_mark}</label>{hint}'
                f'<input type="{t}" id="{fid}" name="{fid}"{ac}{req_attr}{described}{ph}></p>')

    if t == "textarea":
        return (f'<p class="f-row"><label for="{fid}">{f["label"]}{req_mark}</label>{hint}'
                f'<textarea id="{fid}" name="{fid}" rows="3"{ac}{req_attr}{described}{ph}></textarea></p>')

    if t == "select":
        opts = "".join(f'<option value="{o}">{o}</option>' for o in f["opts"])
        return (f'<p class="f-row{wide}"><label for="{fid}">{f["label"]}{req_mark}</label>{hint}'
                f'<select id="{fid}" name="{fid}"{req_attr}{described}>'
                f'<option value="">Select</option>{opts}</select></p>')

    if t == "yesno":
        follow = ""
        if f.get("follow"):
            g = f["follow"]
            follow = (f'<div class="f-follow" id="{fid}-follow" data-follow-of="{fid}" hidden>'
                      f'<label for="{g["id"]}">{g["label"]}</label>'
                      f'<input type="text" id="{g["id"]}" name="{g["id"]}" autocomplete="off">'
                      f'</div>')
        # the hint sits inside the fieldset, so it is announced with the group —
        # no aria-describedby needed (and it must not point inside its own legend)
        return (f'<fieldset class="f-yesno">'
                f'<legend>{f["label"]}{req_mark}</legend>{hint}'
                f'<span class="f-seg">'
                f'<input type="radio" id="{fid}-yes" name="{fid}" value="Yes"{req_attr}>'
                f'<label for="{fid}-yes">Yes</label>'
                f'<input type="radio" id="{fid}-no" name="{fid}" value="No">'
                f'<label for="{fid}-no">No</label>'
                f'</span>{follow}</fieldset>')

    if t == "checks":
        boxes = "".join(
            f'<span class="f-check"><input type="checkbox" id="{fid}-{i}" name="{fid}" value="{o}">'
            f'<label for="{fid}-{i}">{o}</label></span>'
            for i, o in enumerate(f["opts"])
        )
        return (f'<fieldset class="f-checks"><legend>{f["label"]}{req_mark}</legend>{hint}'
                f'<span class="f-check-grid">{boxes}</span></fieldset>')

    raise ValueError(f"unknown field type {t}")


def _section(s, depth=0):
    intro = f'<p class="f-sec-intro">{s["intro"]}</p>' if s.get("intro") else ""
    grid = " f-sec-grid" if s.get("grid") else ""
    fields = "\n      ".join(_field(f, depth) for f in s["fields"])
    return f"""<section class="f-sec{grid}" data-step aria-labelledby="sec-{s['n']}" hidden>
    <p class="f-sec-num" aria-hidden="true">{s['n']}</p>
    <h2 id="sec-{s['n']}" tabindex="-1">{s['title']}</h2>
    {intro}
    <div class="f-fields">
      {fields}
    </div>
  </section>"""


def build_forms():
    from forms_content import FORMS
    d = 1

    # ---- hub -------------------------------------------------------------
    def _steps(f):
        return len(f["sections"]) + 1          # +1 for the acknowledgment step

    cards = "".join(f"""<article class="form-card reveal" style="--d:{i * 110}ms">
      <span class="form-card-icon" aria-hidden="true"><svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">{f['card']['icon']}</svg></span>
      <h2><a href="{f['slug']}.html">{f['name']}</a></h2>
      <p class="form-card-who">{f['card']['for_who']}</p>
      <ul class="form-card-list">{"".join(f'<li>{c}</li>' for c in f['card']['covers'])}</ul>
      <p class="form-card-meta"><span>{_steps(f)} sections</span><span>Save or resume anytime</span></p>
      <span class="form-card-go"><span class="btn btn-gold" aria-hidden="true">Start the form</span></span>
    </article>""" for i, f in enumerate(FORMS))

    hub_crumbs = crumbs([("", "Patient Forms")], depth=d)
    hub_body = f"""{nav(d)}
<main id="main">
{page_hero("Before Your Visit", "Patient Forms", "Complete your paperwork at home, in your own time. Both forms fill out right in your browser — your answers never leave your device until you choose to share them with us.", hub_crumbs, cta=False, depth=d)}
<section class="section form-hub">
  <div class="form-card-grid">{cards}</div>
</section>

<section class="section section-tint form-how">
  <div class="section-head reveal">
    <p class="eyebrow">How it works</p>
    <h2>Three steps, <em>no account needed</em></h2>
  </div>
  <ol class="form-steps-strip">
    <li class="reveal"><span class="fs-num" aria-hidden="true">1</span>
      <strong>Fill it out</strong>
      <span>Work through it a section at a time. Skip around, stop, come back — nothing is locked.</span></li>
    <li class="reveal" style="--d:100ms"><span class="fs-num" aria-hidden="true">2</span>
      <strong>Print or save it</strong>
      <span>Finishing builds a clean summary. Print it, save it as a PDF, or download it as a text file.</span></li>
    <li class="reveal" style="--d:200ms"><span class="fs-num" aria-hidden="true">3</span>
      <strong>Bring it with you</strong>
      <span>Hand it to our front desk when you arrive. That's it — you skip the clipboard entirely.</span></li>
  </ol>
</section>

<section class="section form-privacy-section">
  <div class="privacy-panel reveal">
    <div class="privacy-panel-head">
      <span class="privacy-shield" aria-hidden="true"><svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 4.5 6v5.5c0 4.4 3.1 8.4 7.5 9.5 4.4-1.1 7.5-5.1 7.5-9.5V6L12 3Z"/><path d="m8.8 12.2 2.2 2.2 4.2-4.4"/></svg></span>
      <div>
        <p class="eyebrow">Your privacy</p>
        <h2>How we protect what you write here</h2>
      </div>
    </div>
    <div class="privacy-grid">
      <div><strong>Nothing is transmitted</strong><p>These forms don't send your answers over the internet. Everything you type stays in your browser.</p></div>
      <div><strong>No tracking on form pages</strong><p>We don't load analytics, advertising, or session-recording scripts on any page that asks about your health.</p></div>
      <div><strong>You choose how it reaches us</strong><p>When you finish, the form builds a summary you print, save as a PDF, or bring to your appointment.</p></div>
      <div><strong>Saving is opt-in</strong><p>Your progress is only kept on your device if you switch it on — and a single button erases it.</p></div>
    </div>
    <p class="privacy-foot">Questions about your privacy? Read our <a href="../privacy-policy.html">privacy policy</a>, or call us at <a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a>.</p>
  </div>
</section>
{cta_band(d, heading="Prefer to fill these out <em>with us?</em>", sub="Arrive fifteen minutes early and our front desk will walk you through everything on a practice tablet. Either way works.")}
</main>
{footer(d)}"""
    hub = head("Patient Forms | RegenOrtho Palm Beach",
               "Complete your RegenOrtho Palm Beach patient forms before your visit in Palm Beach Gardens — new patient intake and the peptide & GLP-1 questionnaire, filled out privately in your browser.",
               depth=d, canonical="forms/index.html", extra_css="assets/css/forms.css",
               extra_schema=breadcrumb_schema([("", "Home"), ("forms/index.html", "Patient Forms")])
               ) + '<body class="page-forms">\n' + hub_body
    write("forms/index.html", hub)

    # ---- the forms themselves -------------------------------------------
    for f in FORMS:
        secs = "\n  ".join(_section(s, d) for s in f["sections"])
        steps = "".join(
            f'<li><button type="button" class="f-step" data-goto="{i}">'
            f'<span aria-hidden="true">{s["n"]}</span>'
            f'<span class="f-step-name">{s["title"]}</span></button></li>'
            for i, s in enumerate(f["sections"])
        )
        n_secs = len(f["sections"])
        steps += (f'<li><button type="button" class="f-step" data-goto="{n_secs}">'
                  f'<span aria-hidden="true">{n_secs + 1:02d}</span>'
                  f'<span class="f-step-name">Acknowledgment</span></button></li>')
        c = crumbs([("forms/index.html", "Patient Forms"), ("", f["plain_name"])], depth=d)
        body = f"""{nav(d)}
<main id="main">
{page_hero("Patient Forms", f['name'], f['lede'], c, cta=False, depth=d)}
<section class="section form-section">
  <div class="form-shell">
    <nav class="f-steps" aria-label="Form sections">
      <ol>{steps}</ol>
    </nav>
    <div class="form-main">
      <div class="f-privacy">
        <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.7" d="M12 3 4.5 6v5.5c0 4.4 3.1 8.4 7.5 9.5 4.4-1.1 7.5-5.1 7.5-9.5V6L12 3Z"/><path fill="none" stroke="currentColor" stroke-width="1.7" d="m8.8 12.2 2.2 2.2 4.2-4.4"/></svg>
        <p><strong>This form stays on your device.</strong> Your answers are not sent anywhere when you press Finish — the form builds a summary you print, save as a PDF, or bring with you. We load no tracking scripts on this page.</p>
      </div>

      <form id="patient-form" class="patient-form" data-form="{f['slug']}" novalidate autocomplete="off">
        <p class="f-required-note">Fields marked <span class="req" aria-hidden="true">*</span><span class="sr-only">with an asterisk</span> are required.</p>
        <div class="f-errors" role="alert" hidden></div>
        {secs}
        <section class="f-sec" data-step aria-labelledby="sec-ack" hidden>
          <p class="f-sec-num" aria-hidden="true">{n_secs + 1:02d}</p>
          <h2 id="sec-ack" tabindex="-1">Patient Acknowledgment</h2>
          <div class="f-fields">
            <p class="f-ack-text">{f['ack']}</p>
            <fieldset class="f-checks f-ack">
              <legend class="sr-only">Acknowledgment</legend>
              <span class="f-check">
                <input type="checkbox" id="acknowledgment" name="acknowledgment" value="Acknowledged" required aria-required="true">
                <label for="acknowledgment">I acknowledge and agree to the above statement <span class="req" aria-hidden="true">*</span></label>
              </span>
            </fieldset>
            <p class="f-save-opt">
              <span class="f-check">
                <input type="checkbox" id="save-local">
                <label for="save-local">Save my progress in this browser</label>
              </span>
              <span class="f-hint">Only turn this on if this device is yours — your answers will stay in this browser until you erase them.</span>
            </p>
          </div>
        </section>

        <div class="f-nav">
          <button type="button" class="btn btn-ghost" data-prev hidden>Back</button>
          <p class="f-progress" aria-live="polite">Section <span data-cur>1</span> of {n_secs + 1}</p>
          <button type="button" class="btn btn-gold" data-next>Continue</button>
          <button type="submit" class="btn btn-gold" data-finish hidden>Finish &amp; review</button>
        </div>
      </form>

      <div class="f-done" hidden>
        <h2 tabindex="-1">Your {f['plain_name']} is ready</h2>
        <p>Nothing has been sent. Print this summary or save it as a PDF, then bring it to your appointment or hand it to our front desk — whichever is easier.</p>
        <div class="f-done-actions">
          <button type="button" class="btn btn-gold" data-print>Print / save as PDF</button>
          <button type="button" class="btn btn-ghost" data-download>Download as a text file</button>
          <button type="button" class="btn btn-ghost" data-edit>Go back and edit</button>
        </div>
        <div class="f-summary" id="form-summary"></div>
        <p class="f-erase-row"><button type="button" class="f-erase" data-erase>Erase my answers from this device</button></p>
      </div>
    </div>
  </div>
</section>
</main>
{footer(d, extra_js="assets/js/forms.js")}"""
        page = head(f["title"], f["desc"], depth=d, canonical=f"forms/{f['slug']}.html",
                    extra_css="assets/css/forms.css",
                    extra_schema=breadcrumb_schema([("", "Home"), ("forms/index.html", "Patient Forms"),
                                                    (f"forms/{f['slug']}.html", f["plain_name"])])
                    ) + '<body class="page-form">\n' + body
        write(f"forms/{f['slug']}.html", page)


def build_blog():
    from blog_content import BLOG_POSTS
    d = 1
    # index
    cards = ""
    for i, p_ in enumerate(BLOG_POSTS):
        date_h = "{}/{}/{}".format(p_["date"][5:7], p_["date"][8:10], p_["date"][:4])
        cards += f"""<a class="post-card reveal" href="{p_['slug']}.html" style="--d:{(i % 3) * 90}ms">
      <span class="post-media"><img src="../assets/media/{p_['image']}?v={asset_v('assets/media/' + p_['image'])}" alt="" width="640" height="400" loading="lazy"></span>
      <span class="post-tag">{p_['category']}</span>
      <strong>{p_['title']}</strong>
      <span class="post-date">{date_h}</span>
      <em class="svc-more">Read article <svg viewBox="0 0 16 12" width="14" height="10" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="2" d="M1 6h13M9 1l5 5-5 5"/></svg></em>
    </a>"""
    crumbs_html = crumbs([("", "Blog")], depth=d)
    body = f"""{nav(d)}
<main id="main">
{page_hero("Blog & Insights", "Healing, Explained", "Practical, physician-reviewed writing on orthopedics, regenerative medicine, podiatry, vein care, and wellness — no hype, no jargon.", crumbs_html, depth=d)}
<section class="section"><div class="post-grid post-grid-3">{cards}</div></section>
{cta_band(d)}
</main>
{footer(d)}"""
    schema = breadcrumb_schema([("", "Home"), ("blog/index.html", "Blog")])
    page = head("Blog | RegenOrtho Palm Beach — Orthopedic & Wellness Insights",
                "Articles from RegenOrtho Palm Beach on PRP, regenerative medicine, foot & ankle care, vein treatment, IV therapy, and staying active in South Florida.",
                depth=d, canonical="blog/index.html", extra_schema=schema) + '<body class="page-blog">\n' + body
    write("blog/index.html", page)

    # posts
    for p_ in BLOG_POSTS:
        body_html = p_["body"]
        if "<h2" not in body_html:          # ported copy that starts at h3
            body_html = re.sub(r"<(/?)h4\b", r"<\1h3", body_html)
            body_html = re.sub(r"<(/?)h3\b", r"<\1h2", body_html)
        date_h = "{}/{}/{}".format(p_["date"][5:7], p_["date"][8:10], p_["date"][:4])
        crumbs_html = crumbs([("blog/index.html", "Blog"), ("", p_["title"])], depth=d)
        related = [x for x in BLOG_POSTS if x["slug"] != p_["slug"] and x["category"] == p_["category"]][:2]
        rel_html = "".join(
            f"""<a class="post-card" href="{r['slug']}.html"><span class="post-tag">{r['category']}</span><strong>{r['title']}</strong><em class="svc-more">Read article →</em></a>"""
            for r in related
        )
        rel_sec = f"""<section class="section section-tint"><div class="section-head reveal"><p class="eyebrow">Keep Reading</p><h2>Related <em>articles</em></h2></div><div class="post-grid">{rel_html}</div></section>""" if related else ""
        body = f"""{nav(d)}
<main id="main">
<article class="post">
  <header class="page-hero post-hero">
    <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
    <div class="page-hero-inner reveal">
      {crumbs_html}
      <p class="eyebrow">{p_['category']} · {date_h}</p>
      <h1>{p_['title']}</h1>
      <p class="lede">By the RegenOrtho Palm Beach care team</p>
    </div>
  </header>
  <div class="post-body">
    <figure class="post-figure reveal"><img src="../assets/media/{p_['image']}?v={asset_v('assets/media/' + p_['image'])}" alt="" width="1100" height="620"></figure>
    {body_html}
    <div class="post-cta sym-card">
      <h2>Talk to the team</h2>
      <p>Questions about whether this applies to you? Book a consultation or call <a href="tel:{PHONE_TEL}">{PHONE_VANITY} · {PHONE_DISPLAY}</a>.</p>
      <a class="btn btn-gold" href="../contact.html#book">Book a Consultation</a>
    </div>
  </div>
</article>
{rel_sec}
{cta_band(d)}
</main>
{footer(d)}"""
        schema = (
            extra_ld({
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": p_["title"],
                "description": p_["desc"],
                "datePublished": p_["date"],
                "image": f"{BASE}/assets/media/{p_['image']}",
                "url": f"{BASE}/blog/{p_['slug']}.html",
                "author": {"@type": "Organization", "name": NAME, "@id": ORG_ID},
                "publisher": {"@id": ORG_ID},
                "mainEntityOfPage": f"{BASE}/blog/{p_['slug']}.html",
            })
            + breadcrumb_schema([("", "Home"), ("blog/index.html", "Blog"), (f"blog/{p_['slug']}.html", p_["title"])])
        )
        page = head(f"{p_['title']} | RegenOrtho Palm Beach"[:97],
                    p_["desc"], depth=d, canonical=f"blog/{p_['slug']}.html",
                    og_image=f"assets/media/{p_['image']}",
                    page_type="article", extra_schema=schema) + '<body class="page-post">\n' + body
        write(f"blog/{p_['slug']}.html", page)


def build_legal_and_404():
    d = 0
    for slug, title_, h1 in [("privacy-policy", "Privacy Policy", "Privacy Policy"), ("terms", "Terms & Conditions", "Terms & Conditions")]:
        body = f"""{nav(d)}
<main id="main">
{page_hero(NAME, h1, "How we handle your information and the terms that govern use of this website.", crumbs([("", h1)], depth=d), cta=False, depth=d)}
<section class="section legal-body">
  <div class="legal-inner reveal">
    <p><strong>{NAME}</strong> — {ADDRESS_STREET}, {ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP} · {PHONE_DISPLAY} · {EMAIL}</p>
    <h2>Website use</h2>
    <p>The content on this website is provided for general information about our practice and services. It is not medical advice and does not create a doctor–patient relationship. For medical questions, please contact our office or consult a qualified healthcare provider.</p>
    <h2>Appointment requests &amp; forms</h2>
    <p>Information you submit through appointment request forms or the site assistant is used only to contact you about scheduling and your care, and is transmitted to our front desk email. Please do not include detailed medical history, insurance numbers, or other sensitive records in web forms — we will collect anything needed through secure channels during intake.</p>
    <h2>Patient forms</h2>
    <p>The new patient intake form and the peptide &amp; GLP-1 questionnaire on this site work differently from the appointment request forms above: <strong>they do not transmit anything.</strong> Everything you type stays in your own browser. When you finish, the form assembles your answers into a summary that you print, save as a PDF, or download — you decide how and when it reaches us. Your progress is stored on your device only if you switch that option on, and the "Erase my answers" button removes it.</p>
    <h2>Analytics</h2>
    <p>This site may use privacy-friendly, cookieless analytics to understand aggregate site usage. We do not load analytics, advertising, or session-recording scripts on the patient form pages. We do not sell visitor information.</p>
    <h2>Emergencies</h2>
    <p>If you are experiencing a medical emergency, call 911 or go to the nearest emergency room. This website and its assistant are not monitored in real time.</p>
    <h2>Questions</h2>
    <p>For any questions about this policy or these terms, contact us at <a href="mailto:{EMAIL}">{EMAIL}</a> or {PHONE_DISPLAY}.</p>
  </div>
</section>
</main>
{footer(d)}"""
        page = head(f"{title_} | {NAME}",
                    f"{title_} for {NAME} — how we handle your information and the terms governing use of regenorthopb.com.",
                    depth=d, canonical=f"{slug}.html") + '<body class="page-legal">\n' + body
        write(f"{slug}.html", page)

    body = f"""{nav(0)}
<main id="main">
<section class="page-hero hero-404">
  <div class="aurora" aria-hidden="true"><span></span><span></span><span></span></div>
  <div class="page-hero-inner reveal">
    <p class="eyebrow">404 — Page not found</p>
    <h1>This page has healed and <em>moved on</em></h1>
    <p class="lede">The page you're looking for doesn't exist here anymore. Try one of these instead:</p>
    <div class="hero-cta-row">
      <a class="btn btn-gold" href="index.html">Go to the homepage</a>
      <a class="btn btn-ghost-light" href="services/index.html">Browse services</a>
      <a class="btn btn-ghost-light" href="contact.html#book">Book a consultation</a>
    </div>
  </div>
</section>
</main>
{footer(0)}"""
    page = head("Page Not Found | RegenOrtho Palm Beach",
                "The page you're looking for could not be found. Explore RegenOrtho Palm Beach services, conditions, and booking.",
                depth=0, canonical="404.html") + '<body class="page-404">\n' + body
    write("404.html", page)


# ---------------------------------------------------------------------------
# Site meta: sitemap, robots, llms.txt, manifest
# ---------------------------------------------------------------------------

def build_meta():
    from blog_content import BLOG_POSTS
    pages = ["index.html", "about.html", "contact.html", "faq.html", "iv-therapy.html",
             "patient-resources.html", "privacy-policy.html", "terms.html",
             "forms/index.html", "forms/new-patient.html",
             "forms/peptide-glp-questionnaire.html",
             "services/index.html", "infusions/index.html", "blog/index.html",
             "providers/dr-marc-matarazzo.html", "providers/dr-orlando-cedeno.html",
             "providers/emily-bahnick.html"]
    pages += [f"services/{s['slug']}.html" for s in SERVICES]
    pages += [f"conditions/{c['slug']}.html" for c in CONDITIONS]
    pages += [f"locations/{l['slug']}.html" for l in LOCATIONS]
    pages += [f"infusions/{i['slug']}.html" for i in INFUSIONS]
    pages += [f"blog/{p['slug']}.html" for p in BLOG_POSTS]

    urls = "\n".join(
        f"  <url><loc>{BASE}/{p}</loc></url>" for p in pages
    )
    write("sitemap.xml", f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}
</urlset>
""")

    write("robots.txt", f"""User-agent: *
Allow: /

Sitemap: {BASE}/sitemap.xml
""")

    write("site.webmanifest", json.dumps({
        "name": NAME,
        "short_name": "RegenOrtho",
        "icons": [
            {"src": "/assets/media/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/assets/media/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
        "theme_color": "#071A38",
        "background_color": "#F9F7F2",
        "display": "browser",
    }, indent=1))

    svc_lines = "\n".join(f"- {s['name']}: {BASE}/services/{s['slug']}.html — {s['desc']}" for s in SERVICES)
    cond_lines = "\n".join(f"- {c['name']}: {BASE}/conditions/{c['slug']}.html" for c in CONDITIONS)
    loc_lines = "\n".join(f"- {l['city']}: {BASE}/locations/{l['slug']}.html" for l in LOCATIONS)
    write("llms.txt", f"""# {NAME}

> Concierge orthopedic, podiatric, regenerative, and vein care in Palm Beach Gardens, Florida. Slogan: "{TAGLINE}".

## Key facts
- Address: {ADDRESS_STREET}, {ADDRESS_CITY}, {ADDRESS_STATE} {ADDRESS_ZIP}
- Phone: {PHONE_DISPLAY} (vanity: {PHONE_VANITY})
- Email: {EMAIL}
- Hours: {HOURS}
- Instagram: {INSTAGRAM}
- Specialists: Dr. Marc Matarazzo, MD (board-certified sports medicine & orthopedic surgeon, 23+ years, MAKO-certified) and Dr. Orlando Cedeno, DPM (board-certified podiatric surgeon & vein specialist).
- New patients accepted; no referral required; most major insurance accepted; concierge/direct-pay bundles available.

## Services
{svc_lines}
- IV Recovery & Wellness Lounge: {BASE}/iv-therapy.html — 12 clinician-supervised infusions, $189–$499.
- Specialty Infusion Center: {BASE}/infusions/index.html — IVIG, Krystexxa, Ocrevus, Ultomiris.

## Conditions treated
{cond_lines}

## Service areas
Palm Beach Gardens (clinic location) plus:
{loc_lines}

## Booking
Book online: {BASE}/contact.html — or call {PHONE_DISPLAY}.
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    build_home()
    build_about()
    build_providers()
    build_services()
    build_conditions()
    build_locations()
    build_iv()
    build_infusions()
    build_faq()
    build_contact()
    build_resources()
    build_forms()
    build_blog()
    build_legal_and_404()
    build_meta()
    print("\nDone.")


if __name__ == "__main__":
    main()
