# KSFE Trivandrum — Lead Data & Provenance

Lead list of **KSFE (Kerala State Financial Enterprises Ltd.)** branches in
Thiruvananthapuram district, built for a performance-marketing pitch around
their chitty (chit fund) products.

**File:** `ksfe-trivandrum-branches.csv` — 35 rows (33 branches + 2 regional offices)

---

## Read this before you send anything

KSFE is a **Kerala Government PSU**, not a private chit fund. Three things follow
from that, and they change how you should pitch:

1. **Branch managers cannot buy marketing.** Media spend and agency
   appointments are decided at Head Office (Thrissur) / Regional Office level,
   and above a threshold they go through **tender or GeM procurement** — not a
   sales call. Cold-emailing 33 branch managers will mostly generate polite
   silence.
2. **The real entry path is the Regional Office** (`rotvm@ksfe.com` /
   `roatl@ksfe.com`) and, for anything real, HO Marketing at Thrissur. Branch
   contacts are best used as *evidence-gathering and warm-intro* channels, not
   as the buying centre.
3. **Chit fund promotion is regulated** (Chit Funds Act 1982 + state rules; ASCI
   codes on financial advertising). Any creative you propose must avoid implied
   return guarantees. Say this in the pitch — it signals you know the sector and
   differentiates you from generic agencies.

Practical sequence: **RO email → HO Marketing → watch GeM/state tender portals
for KSFE advertising & digital-media tenders.** The branch list below supports
that, it doesn't replace it.

---

## Data provenance

`ksfe.com` (and `admin.ksfe.com`, plus the third-party directories that mirror
it) is **blocked by this environment's network egress proxy**, so I could not
crawl the site directly. Everything here was reconstructed from public search
indexes of KSFE's own pages (`ksfe.com/location/<slug>-<code>`), KSFE's public
SPIO/Appellate-Authority PDF, and business directories.

**Two contact fields are derived, not scraped.** KSFE uses strict, verifiable
conventions:

| Field | Pattern | Confirmed against |
|---|---|---|
| `email` | `<branch_code>@ksfe.com` | codes 15, 94, 106, 109, 130, 141, 156, 185 |
| `mobile` | `9447797` + 3-digit zero-padded code | codes 015, 069, 094 |

Both patterns held on every independent sample found, so derived values are
high-probability — but they are **inferred**. Verify before a paid send;
a bounce on `<code>@ksfe.com` costs you domain reputation.

### `confidence` column

| Value | Meaning |
|---|---|
| `fully_confirmed` | Address + landline + mobile + email all seen in a source |
| `address_phone_confirmed` | Address and landline seen; mobile/email derived |
| `address_confirmed` | Address seen; phone/email derived |
| `phone_confirmed` / `email_confirmed` | That one field seen; rest derived |
| `code_confirmed` | Branch name + code confirmed from KSFE's own page title; address is the locality only, contacts derived |

Landline blanks are genuine gaps, not zeros — fill them with the crawler below.

### Known gaps

Branches likely in the district that I could **not** confirm a code for, so they
are deliberately absent rather than guessed: Pattom, Ulloor, Poojappura,
Karamana, Vanchiyoor, Nemom, Malayinkeezhu, Venjaramoodu, Palode,
Chirayinkeezhu, Vamanapuram, Aryanad, Aruvikkara, Anad, Vizhinjam/Kovalam,
Perumkadavila, Amaravila, Vakkom, Nalanchira, Attipra. Expect the true district
count to be **~45–55**, not 33.

`vannapuram (359)` was found and **excluded** — it is Vamanapuram-lookalike but
sits in Idukki district.

---

## Completing the dataset

`../scripts/crawl_ksfe_branches.py` closes both gaps — missing branches and
unverified contacts. Run it from a normal network connection:

```bash
pip install requests beautifulsoup4
python scripts/crawl_ksfe_branches.py --out leads/ksfe-trivandrum-crawled.csv
```

It enumerates `ksfe.com/branch-list` + `ksfe.com/branch-locator`, follows every
`/location/<slug>-<code>` page, filters to Thiruvananthapuram by pincode range
(`695xxx`, `696xxx`) and locality keywords, and regex-extracts address, phone
and email. It writes a `verified_*` column per field so you can diff scraped
truth against the derived values in the committed CSV.

**It is untested against the live site** — egress was blocked here, so I could
not inspect KSFE's actual HTML. Extraction is regex-based specifically so it
degrades gracefully rather than breaking on unknown markup, but budget a few
minutes to adjust selectors on first run.

---

## Suggested working order

1. Run the crawler; reconcile against this CSV.
2. Verify P1 emails with a validation tool before any bulk send.
3. Open at **RO Urban + RO Rural** (`outreach/email-sequence.md`).
4. Use P1 branches for the audit hook — visible, checkable, local proof.
5. Track KSFE tenders in parallel; that is where the actual budget lives.
