# Dezmos → KSFE Pitch Deck

**Deliverable:** `Dezmos-KSFE-Performance-Marketing-Proposal.pdf` — 10 slides, 16:9
(960×540pt), one deck for the whole KSFE branch network and both Regional Offices.

```bash
python3 deck/build_deck.py     # regenerates HTML + PDF
```

Rendered with headless Chromium. Manrope is base64-embedded in
`manrope-embed.css`, so the PDF renders identically offline.

---

## Slides

| # | Slide |
|---|---|
| 1 | Cover |
| 2 | The opportunity — why KSFE's trust advantage is under-marketed |
| 3 | Track record — headline KSFE numbers |
| 4 | Campaign record — all 7 KSFE campaigns, full table |
| 5 | Cost per enquiry down 68% at Kolayad (chart) |
| 6 | Reach economics |
| 7 | The four-step delivery cycle + compliance |
| 8 | **Basic vs Premium packages** |
| 9 | Procurement / governance |
| 10 | Next step — free branch audit + contact |

---

## Where the numbers come from

Every figure is pulled from **Meta Ads Manager, ad account `590232006572483`**,
maximum date range, via the Meta MCP connector. Nothing is modelled, estimated,
or illustrative. The source array is `CAMPAIGNS` in `build_deck.py`.

Seven real KSFE campaigns across **two branches**:

| Branch | Campaigns | Period |
|---|---|---|
| KSFE Pettah (Thiruvananthapuram) | 2 | Jan 2025, Jun 2025 |
| KSFE Kolayad (Kannur) | 4 | Jun 2025 – Feb 2026 |
| Unlabelled "KSFE Awareness ad" | 1 | Sep 2024 |

Totals: **₹13,659 spend · 892,833 impressions · 443,357 reach · 3,048 clicks ·
149 WhatsApp enquiries · ₹72.68 blended cost per enquiry.**

The headline proof point is the Kolayad trend — cost per WhatsApp enquiry fell
₹121.06 (Jul 2025) → ₹38.52 (Jan 2026), a **68% reduction**, with the final
campaign delivering 66 enquiries, more than the previous three combined.

**Note on Kolayad:** it is in **Kannur** district, not Thiruvananthapuram. The
deck presents it accurately as a KSFE branch without claiming it is local. Only
Pettah is a Trivandrum branch. If a prospect asks, the honest framing is
"two KSFE branches across two districts."

---

## Before you send this

Three placeholders must be replaced — they are in the slide 8 and slide 10
markup inside `build_deck.py`:

1. **Pricing** — `₹15,000` (Basic) and `₹35,000` (Premium) per month are
   indicative figures I set for the Kerala market. Confirm or change them.
2. **Contact details** — `hello@dezmos.in`, `+91 00000 00000`, `dezmos.in` are
   placeholders.
3. **Recommended ad budgets** — ₹5,000–8,000 and ₹30,000–50,000 per month.

---

## Logo

`../assets/dezmos-logo.svg` — the ZD monogram plus wordmark, rebuilt as vector.
The uploaded image was not present on this machine's filesystem, so it was
reconstructed from the reference: black/`currentColor` monogram strokes, gold
`#C9A227` wordmark. It inherits `currentColor`, so it renders white on dark
slides and forest on light ones automatically. **If you have the original PNG/SVG
file, drop it in and it will be used instead.**

The gold wordmark is the only non-brand colour in the deck; it is internal to the
logo asset. Every other accent is Dezmos lime `#C1FF72` per the brand system. The
corner mark on content slides is monogram-only — the wordmark is illegible at
62px and was clipping.
