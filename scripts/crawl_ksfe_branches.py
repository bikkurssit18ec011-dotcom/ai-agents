#!/usr/bin/env python3
"""Crawl KSFE branch data for Thiruvananthapuram district.

KSFE publishes one page per branch at ksfe.com/location/<slug>-<code>. This
script discovers those pages, keeps the ones in Thiruvananthapuram district,
and extracts address / phone / email from each.

Usage:
    pip install requests beautifulsoup4
    python scripts/crawl_ksfe_branches.py --out leads/ksfe-trivandrum-crawled.csv

Notes:
    Extraction is regex-based rather than selector-based on purpose: KSFE's
    markup is not documented here, and regex over page text degrades to
    "field missing" instead of crashing when the layout differs. If a field
    comes back consistently empty, print --debug output for one branch and
    tighten the pattern for that field only.
"""

import argparse
import csv
import re
import sys
import time
from urllib.parse import urljoin

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing deps. Run: pip install requests beautifulsoup4")

BASE = "https://ksfe.com"
SEED_PAGES = ["/branch-list", "/branch-locator", "/ho-ro-address"]

# /location/<slug>-<code>  e.g. /location/vazhuthacaud-94
LOCATION_RE = re.compile(r"/location/([a-z0-9\-]+?)-(\d{1,4})/?$", re.I)

# Thiruvananthapuram district PIN codes are 695xxx (a few edge areas 696xxx).
PIN_RE = re.compile(r"\b(69[56])\s?(\d{3})\b")
# Handles "0471-2544832", "(0471) 2327381", "0471 2437245" and bare mobiles.
PHONE_RE = re.compile(r"\b(?:0\d{2,4}\)?[\s\-]?\d{6,8}|[6-9]\d{9})\b")
EMAIL_RE = re.compile(r"\b[\w.\-]+@ksfe\.com\b", re.I)

# Localities used to keep branches whose page omits a PIN.
TVM_KEYWORDS = {
    "thiruvananthapuram", "trivandrum", "tvm", "attingal", "neyyattinkara",
    "nedumangad", "varkala", "kattakada", "balaramapuram", "parassala",
    "kilimanoor", "vellanad", "vellarada", "kazhakuttom", "kazhakoottam",
    "peroorkada", "sasthamangalam", "vazhuthacaud", "kesavadasapuram",
    "pattom", "sreekariyam", "sreekaryam", "pothencode", "mangalapuram",
    "vattiyoorkavu", "kudappanakunnu", "kodappanakunnu", "pappanamcode",
    "pravachambalam", "kanjiramkulam", "kallambalam", "kadakkavoor",
    "chirayinkeezhu", "venjaramoodu", "palode", "aryanad", "vizhinjam",
    "kovalam", "perumkadavila", "amaravila", "vakkom", "nalanchira",
    "karamana", "poojappura", "vanchiyoor", "thampanoor", "chala", "chalai",
    "statue", "nemom", "malayinkeezhu", "aruvikkara", "anad", "attipra",
    "medical college", "technopark", "ulloor", "santhi nagar",
}

# Lookalike branches that sit in other districts.
EXCLUDE_SLUGS = {"vannapuram"}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; branch-directory-research/1.0)"
})


def get(url, retries=3):
    for attempt in range(retries):
        try:
            r = session.get(url, timeout=25)
            if r.status_code == 200:
                return r.text
            if r.status_code == 404:
                return None
        except requests.RequestException as exc:
            if attempt == retries - 1:
                print(f"  ! {url}: {exc}", file=sys.stderr)
        time.sleep(2 ** attempt)
    return None


def discover():
    """Collect every /location/<slug>-<code> URL reachable from the seed pages."""
    found = {}
    for page in SEED_PAGES:
        html = get(urljoin(BASE, page))
        if not html:
            print(f"  ! could not load {page}", file=sys.stderr)
            continue
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            url = urljoin(BASE, a["href"])
            m = LOCATION_RE.search(url)
            if m:
                slug, code = m.group(1).lower(), int(m.group(2))
                found[code] = (slug, url.rstrip("/"))
        print(f"  {page}: running total {len(found)} branch pages")
    return found


def _norm_phone(raw):
    """'0471) 2327381' -> '0471-2327381'; drop stray brackets and spacing."""
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 10 and digits[0] != "0":
        return digits
    if digits.startswith("0") and len(digits) >= 10:
        return f"{digits[:4]}-{digits[4:]}"
    return digits


def is_trivandrum(text, slug):
    if slug in EXCLUDE_SLUGS:
        return False
    if PIN_RE.search(text):
        return True
    low = text.lower()
    return any(k in low for k in TVM_KEYWORDS)


def parse_branch(code, slug, url, debug=False):
    html = get(url)
    if not html:
        return None

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True))

    if debug:
        print(f"\n--- {slug} ({code}) ---\n{text[:1200]}\n")

    if not is_trivandrum(text, slug):
        return None

    title = soup.find("h1") or soup.find("title")
    name = title.get_text(strip=True) if title else slug.replace("-", " ").title()
    name = re.sub(r"\s*\(\d+\)\s*$", "", name).strip()

    pin = PIN_RE.search(text)
    phones = list(dict.fromkeys(
        _norm_phone(p) for p in PHONE_RE.findall(text)
    ))
    emails = list(dict.fromkeys(e.lower() for e in EMAIL_RE.findall(text)))

    landline = next((p for p in phones if p.startswith("0")), "")
    mobile = next((p for p in phones if not p.startswith("0")), "")

    # Address: the window of text around the PIN code is reliably the address
    # block on these pages.
    address = ""
    if pin:
        start = max(0, pin.start() - 180)
        address = text[start:pin.end()].strip()
        address = re.sub(r"^\S*\s", "", address)

    derived_email = f"{code}@ksfe.com"
    derived_mobile = f"9447797{code:03d}" if code < 1000 else ""

    return {
        "branch_code": code,
        "branch_name": name,
        "url": url,
        "address": address,
        "pincode": f"{pin.group(1)}{pin.group(2)}" if pin else "",
        "landline": landline,
        "mobile_scraped": mobile,
        "mobile_derived": derived_mobile,
        "email_scraped": emails[0] if emails else "",
        "email_derived": derived_email,
        "verified_mobile": "yes" if mobile and mobile == derived_mobile else
                           ("MISMATCH" if mobile else "no"),
        "verified_email": "yes" if derived_email in emails else
                          ("MISMATCH" if emails else "no"),
        "all_phones": " | ".join(phones),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ksfe-trivandrum-crawled.csv")
    ap.add_argument("--delay", type=float, default=1.0,
                    help="seconds between requests (be polite)")
    ap.add_argument("--debug", action="store_true",
                    help="dump extracted page text for tuning")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    print("Discovering branch pages...")
    branches = discover()
    if not branches:
        sys.exit("No branch pages found - check connectivity or update SEED_PAGES.")

    print(f"\n{len(branches)} branch pages found. Filtering to Thiruvananthapuram...\n")

    rows = []
    items = sorted(branches.items())
    if args.limit:
        items = items[:args.limit]

    for code, (slug, url) in items:
        row = parse_branch(code, slug, url, debug=args.debug)
        if row:
            rows.append(row)
            flag = "" if row["verified_email"] == "yes" else "  <- check"
            print(f"  [{code:>4}] {row['branch_name']}{flag}")
        time.sleep(args.delay)

    if not rows:
        sys.exit("No Thiruvananthapuram branches matched - loosen TVM_KEYWORDS.")

    rows.sort(key=lambda r: r["branch_code"])
    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    mismatches = sum(1 for r in rows
                     if "MISMATCH" in (r["verified_email"], r["verified_mobile"]))
    print(f"\nWrote {len(rows)} branches to {args.out}")
    print(f"Pattern mismatches needing review: {mismatches}")


if __name__ == "__main__":
    main()
