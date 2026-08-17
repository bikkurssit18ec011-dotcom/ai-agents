#!/usr/bin/env python3
"""Build the Dezmos -> KSFE pitch deck: HTML -> PDF via headless Chromium.

All campaign numbers come from Meta Ads Manager (ad account 590232006572483)
and live in CAMPAIGNS below. Nothing here is estimated or illustrative.

Usage:
    python deck/build_deck.py
"""

import subprocess
import pathlib
import shutil

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent
OUT_HTML = HERE / "ksfe-pitch-deck.html"
OUT_PDF = HERE / "Dezmos-KSFE-Performance-Marketing-Proposal.pdf"

CHROME_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
    "/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell",
    shutil.which("chromium") or "",
    shutil.which("google-chrome") or "",
]

# ── Real Meta Ads Manager data ────────────────────────────────────────────
# branch, label, objective, period, spend, impressions, reach, clicks,
# ctr, cpc, cpm, result_value, result_label, cost_per_result
CAMPAIGNS = [
    ("—", "KSFE Awareness ad", "Awareness", "Sep 2024",
     1449.78, 115123, 88698, 231, "0.20%", "₹6.28", "₹12.59",
     "88,698", "people reached", "₹16.35"),
    ("Pettah", "ksfe pettah campaign", "Awareness", "Jan 2025",
     1379.10, 582650, 277033, 266, "0.05%", "₹5.18", "₹2.37",
     "277,033", "people reached", "₹4.98"),
    ("Pettah", "KSFE Pettah WA Tailored", "WhatsApp", "Jun 2025",
     2758.27, 33522, 15489, 780, "2.33%", "₹3.54", "₹82.28",
     "23", "WhatsApp enquiries", "₹119.92"),
    ("Kolayad", "KSFE Kolayad WA 17/06", "WhatsApp", "Jun–Jul 2025",
     2326.57, 63104, 23876, 743, "1.18%", "₹3.13", "₹36.87",
     "24", "WhatsApp enquiries", "₹96.94"),
    ("Kolayad", "KSFE Kolayad WA 26/07", "WhatsApp", "Jul–Aug 2025",
     2542.36, 30752, 11807, 387, "1.26%", "₹6.57", "₹82.67",
     "21", "WhatsApp enquiries", "₹121.06"),
    ("Kolayad", "KSFE Kolayad WA 25/10", "WhatsApp", "Oct 2025",
     660.29, 4163, 2401, 65, "1.56%", "₹10.16", "₹158.61",
     "15", "WhatsApp enquiries", "₹44.02"),
    ("Kolayad", "KSFE Kollayad 24/01", "WhatsApp", "Jan–Feb 2026",
     2542.39, 63519, 24053, 576, "0.91%", "₹4.41", "₹40.03",
     "66", "WhatsApp enquiries", "₹38.52"),
]

# Cost per WhatsApp enquiry, Kolayad branch, chronological.
TREND = [
    ("Jun 2025", 96.94),
    ("Jul 2025", 121.06),
    ("Oct 2025", 44.02),
    ("Jan 2026", 38.52),
]

TOTAL_SPEND = sum(c[4] for c in CAMPAIGNS)
TOTAL_IMPR = sum(c[5] for c in CAMPAIGNS)
TOTAL_REACH = sum(c[6] for c in CAMPAIGNS)
TOTAL_CLICKS = sum(c[7] for c in CAMPAIGNS)
TOTAL_CONV = 23 + 24 + 21 + 15 + 66
WA_SPEND = 2758.27 + 2326.57 + 2542.36 + 660.29 + 2542.39
BLENDED_CPE = WA_SPEND / TOTAL_CONV

LOGO = (ROOT / "assets" / "dezmos-logo.svg").read_text()
LOGO = LOGO.split("?>")[-1].strip()
FONT_CSS = (HERE / "manrope-embed.css").read_text()


def logo(cls="", word="#C9A227"):
    svg = LOGO.replace("<svg ", f'<svg class="logo {cls}" style="--logo-word:{word}" ')
    return svg


def bar_chart():
    """Cost per WhatsApp enquiry, Kolayad. Single series -> no legend."""
    base_y, top_y = 400, 110
    span = base_y - top_y
    vmax = 148.0
    bw, x0, gap = 110, 130, 50
    bars, labels, values = [], [], []
    for i, (period, val) in enumerate(TREND):
        x = x0 + i * (bw + gap)
        h = val / vmax * span
        y = base_y - h
        bars.append(
            f'<path d="M{x} {base_y} V{y + 4} Q{x} {y} {x + 4} {y} '
            f'H{x + bw - 4} Q{x + bw} {y} {x + bw} {y + 4} V{base_y} Z" '
            f'fill="#C1FF72"/>'
        )
        values.append(
            f'<text x="{x + bw / 2}" y="{y - 16}" text-anchor="middle" '
            f'class="cv">₹{val:,.2f}</text>'
        )
        labels.append(
            f'<text x="{x + bw / 2}" y="{base_y + 32}" text-anchor="middle" '
            f'class="cl">{period}</text>'
        )
    return f"""
<svg viewBox="0 0 800 470" class="chart" role="img"
     aria-label="Cost per WhatsApp enquiry at KSFE Kolayad fell from
                 ₹96.94 in June 2025 to ₹38.52 in January 2026">
  <line x1="100" y1="{base_y}" x2="770" y2="{base_y}" class="axis"/>
  {''.join(bars)}
  {''.join(values)}
  {''.join(labels)}
  <text x="100" y="44" class="cn">Cost per WhatsApp enquiry · KSFE Kolayad branch</text>
</svg>"""


def campaign_rows():
    out = []
    for (br, name, obj, per, spend, impr, reach, clicks,
         ctr, cpc, cpm, rv, rl, cpr) in CAMPAIGNS:
        tag = "wa" if obj == "WhatsApp" else "aw"
        out.append(f"""<tr>
  <td class="nm">{name}<span class="br">{br}</span></td>
  <td><span class="pill {tag}">{obj}</span></td>
  <td class="num">₹{spend:,.0f}</td>
  <td class="num">{impr:,}</td>
  <td class="num">{reach:,}</td>
  <td class="num">{clicks:,}</td>
  <td class="num">{ctr}</td>
  <td class="num strong">{rv}</td>
  <td class="num strong">{cpr}</td>
</tr>""")
    return "".join(out)


HTML = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Dezmos × KSFE — Performance Marketing Proposal</title>
<style>
{FONT_CSS}
:root {{
  --lime:#C1FF72; --forest:#1F2A2E; --white:#fff; --gray:#F4F8FA;
  --muted:rgba(31,42,46,.7); --border:rgba(31,42,46,.12); --lime-tint:#f3ffe3;
  --font:'Manrope',sans-serif;
}}
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
@page {{ size:1280px 720px; margin:0; }}
html,body{{background:var(--white)}}
body{{font-family:var(--font);color:var(--forest);-webkit-font-smoothing:antialiased}}
.slide{{width:1280px;height:720px;position:relative;overflow:hidden;
  page-break-after:always;background:var(--white);padding:64px 72px}}
.slide:last-child{{page-break-after:auto}}
.dark{{background:var(--forest);color:var(--white)}}
.dark h1,.dark h2,.dark h3{{color:var(--white)}}
h1{{font-size:4.6rem;font-weight:800;line-height:1.05;letter-spacing:-.02em}}
h2{{font-size:2.6rem;font-weight:800;line-height:1.15;letter-spacing:-.015em}}
h3{{font-size:1.35rem;font-weight:700}}
p{{font-size:1rem;line-height:1.55;color:var(--muted)}}
.dark p{{color:rgba(255,255,255,.72)}}
.logo{{width:120px;height:auto;color:var(--forest)}}
.dark .logo{{color:var(--white)}}
.eyebrow{{font-size:.82rem;font-weight:700;letter-spacing:.16em;
  text-transform:uppercase;color:var(--muted)}}
.dark .eyebrow{{color:var(--lime)}}
.accent{{color:var(--lime)}}
.rule{{width:64px;height:4px;background:var(--lime);border-radius:2px;margin:22px 0}}
.foot{{position:absolute;left:72px;right:72px;bottom:34px;display:flex;
  justify-content:space-between;font-size:.72rem;color:var(--muted);
  border-top:1px solid var(--border);padding-top:12px}}
.dark .foot{{color:rgba(255,255,255,.5);border-color:rgba(255,255,255,.16)}}
/* corner mark is the monogram only — the wordmark is illegible at this size */
.corner{{position:absolute;top:40px;right:72px;width:62px;color:var(--forest);opacity:.9}}
.corner text{{display:none}}
.dark .corner{{color:var(--white)}}
/* cover */
.cover-wrap{{height:100%;display:flex;flex-direction:column;justify-content:center;
  padding-bottom:34px}}
.cover-logo{{width:184px;margin-bottom:44px}}
.cover-meta{{display:flex;gap:14px;margin-top:34px;flex-wrap:wrap}}
.chip{{background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.2);
  border-radius:999px;padding:8px 18px;font-size:.86rem;font-weight:600;color:#fff}}
.chip.hi{{background:var(--lime);color:var(--forest);border-color:var(--lime)}}
/* stats */
.stats{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;margin-top:34px}}
.stat{{background:var(--gray);border-radius:14px;padding:26px 24px}}
.dark .stat{{background:rgba(255,255,255,.07)}}
.stat .v{{font-size:2.7rem;font-weight:800;line-height:1;letter-spacing:-.02em}}
.dark .stat .v{{color:var(--lime)}}
.stat .k{{font-size:.82rem;color:var(--muted);margin-top:10px;font-weight:600;
  line-height:1.35}}
.dark .stat .k{{color:rgba(255,255,255,.66)}}
/* table */
table{{width:100%;border-collapse:collapse;margin-top:26px;font-size:.8rem}}
th{{background:var(--forest);color:#fff;font-weight:700;text-align:left;
  padding:12px 10px;font-size:.72rem;letter-spacing:.04em;text-transform:uppercase}}
th.num,td.num{{text-align:right}}
td{{padding:9px 10px;border-bottom:1px solid var(--border);color:var(--muted)}}
tbody tr:nth-child(even) td{{background:var(--gray)}}
td.nm{{color:var(--forest);font-weight:700;font-size:.82rem}}
td.strong{{color:var(--forest);font-weight:800}}
.br{{display:block;font-weight:500;font-size:.68rem;color:var(--muted);
  margin-top:2px;letter-spacing:.04em;text-transform:uppercase}}
.pill{{display:inline-block;border-radius:999px;padding:3px 11px;font-size:.68rem;
  font-weight:700;border:1px solid var(--border)}}
.pill.wa{{background:var(--lime);color:var(--forest);border-color:var(--lime)}}
.pill.aw{{background:var(--lime-tint);color:var(--forest)}}
tfoot td{{background:var(--forest)!important;color:#fff;font-weight:800;
  border:none;font-size:.82rem}}
/* chart */
.chart{{width:800px;height:470px}}
.chart .axis{{stroke:var(--border);stroke-width:1.5}}
.chart .cv{{font-family:var(--font);font-size:20px;font-weight:800;fill:var(--forest)}}
.chart .cl{{font-family:var(--font);font-size:16px;font-weight:600;fill:var(--muted)}}
.chart .cn{{font-family:var(--font);font-size:17px;font-weight:700;fill:var(--forest)}}
.split{{display:grid;grid-template-columns:800px 1fr;gap:44px;align-items:center;
  margin-top:12px}}
.callout{{background:var(--lime-tint);border-left:3px solid var(--lime);
  padding:22px 24px;border-radius:0 10px 10px 0}}
.callout .big{{font-size:3.4rem;font-weight:800;line-height:1;letter-spacing:-.02em}}
.callout p{{margin-top:12px;font-size:.9rem}}
/* packages */
.pkgs{{display:grid;grid-template-columns:1fr 1fr;gap:28px;margin-top:30px}}
.pkg{{border:1px solid var(--border);border-radius:16px;padding:30px 30px 26px;
  position:relative;display:flex;flex-direction:column}}
.pkg.prem{{background:var(--forest);border-color:var(--forest);color:#fff}}
.pkg h3{{font-size:1.5rem}}
.pkg.prem h3{{color:#fff}}
.tagline{{font-size:.8rem;color:var(--muted);margin-top:6px;font-weight:600}}
.pkg.prem .tagline{{color:rgba(255,255,255,.66)}}
.price{{font-size:2.5rem;font-weight:800;margin:20px 0 4px;letter-spacing:-.02em}}
.pkg.prem .price{{color:var(--lime)}}
.per{{font-size:.78rem;color:var(--muted);font-weight:600}}
.pkg.prem .per{{color:rgba(255,255,255,.6)}}
ul{{list-style:none;margin-top:20px;display:flex;flex-direction:column;gap:9px}}
li{{font-size:.85rem;color:var(--muted);padding-left:22px;position:relative;
  line-height:1.4}}
.pkg.prem li{{color:rgba(255,255,255,.82)}}
li::before{{content:'';position:absolute;left:0;top:7px;width:9px;height:9px;
  border-radius:2px;background:var(--lime)}}
.badge{{position:absolute;top:-11px;right:26px;background:var(--lime);
  color:var(--forest);font-size:.68rem;font-weight:800;padding:5px 13px;
  border-radius:999px;letter-spacing:.06em;text-transform:uppercase}}
/* generic grids */
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:32px}}
.card{{background:var(--gray);border-radius:14px;padding:26px 24px}}
.card h3{{font-size:1.05rem;margin-bottom:10px}}
.card p{{font-size:.86rem}}
.num-badge{{width:34px;height:34px;border-radius:8px;background:var(--lime);
  color:var(--forest);font-weight:800;font-size:.95rem;display:flex;
  align-items:center;justify-content:center;margin-bottom:14px}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:40px;margin-top:30px}}
.note{{font-size:.72rem;color:var(--muted);margin-top:18px;line-height:1.5}}
.dark .note{{color:rgba(255,255,255,.55)}}
.cta-box{{background:var(--lime);color:var(--forest);border-radius:16px;
  padding:32px 36px;margin-top:30px}}
.cta-box .big{{font-size:1.7rem;font-weight:800;letter-spacing:-.01em}}
.cta-box p{{color:rgba(31,42,46,.78);margin-top:8px;font-size:.92rem}}
.contact{{display:flex;gap:40px;margin-top:24px;font-size:.9rem;font-weight:600}}
.contact span{{color:rgba(255,255,255,.6);font-weight:500;display:block;
  font-size:.72rem;margin-bottom:3px;text-transform:uppercase;letter-spacing:.08em}}
</style></head><body>

<!-- 1 COVER -->
<section class="slide dark">
  <div class="cover-wrap">
    {logo("cover-logo")}
    <div class="eyebrow">Performance Marketing Proposal</div>
    <h1>Filling KSFE branches<br>with <span class="accent">measurable</span><br>enquiries.</h1>
    <div class="rule"></div>
    <p style="max-width:680px;font-size:1.08rem">
      Prepared for KSFE branch network and Regional Offices, Thiruvananthapuram.
      Built on results Dezmos has already delivered for live KSFE branches.
    </p>
    <div class="cover-meta">
      <div class="chip hi">2 KSFE branches already served</div>
      <div class="chip">7 campaigns run</div>
      <div class="chip">Sep 2024 – Feb 2026</div>
    </div>
  </div>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>Confidential</span></div>
</section>

<!-- 2 THE GAP -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">The opportunity</div>
  <h2 style="margin-top:14px;max-width:900px">KSFE has the strongest trust
    position in Kerala — and the quietest digital presence.</h2>
  <div class="rule"></div>
  <div class="grid3">
    <div class="card">
      <div class="num-badge">1</div>
      <h3>Competitors own the intent moment</h3>
      <p>When someone searches or scrolls for a chitty or a monthly savings
         plan, the ads they see are private operators and gold-loan NBFCs.
         They already trust KSFE — they are simply not being shown it at the
         moment they act.</p>
    </div>
    <div class="card">
      <div class="num-badge">2</div>
      <h3>Every branch is a distinct market</h3>
      <p>A Technopark-catchment branch and a handloom-town branch do not share
         an audience. Radius targeting lets each branch run its own campaign,
         in Malayalam, against its own catchment — at branch-scale budgets.</p>
    </div>
    <div class="card">
      <div class="num-badge">3</div>
      <h3>Enquiries can be counted</h3>
      <p>Print and hoardings cannot tell you what one enquiry cost. A WhatsApp
         campaign can — down to the rupee, per branch, per month. That is the
         whole basis of this proposal.</p>
    </div>
  </div>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>02</span></div>
</section>

<!-- 3 PROOF -->
<section class="slide dark">
  {logo("corner")}
  <div class="eyebrow">Track record with KSFE</div>
  <h2 style="margin-top:14px;max-width:920px">We are not proposing this from
    theory. We already run ads for KSFE branches.</h2>
  <div class="rule"></div>
  <p style="max-width:900px">Seven campaigns for the <strong
     style="color:#fff">KSFE Pettah</strong> and <strong
     style="color:#fff">KSFE Kolayad</strong> branches, from September 2024 to
     February 2026. Every figure on the next pages is pulled directly from
     Meta Ads Manager — none of it is modelled or illustrative.</p>
  <div class="stats">
    <div class="stat"><div class="v">₹{TOTAL_SPEND:,.0f}</div>
      <div class="k">Managed ad spend for KSFE branches</div></div>
    <div class="stat"><div class="v">{TOTAL_REACH:,}</div>
      <div class="k">People reached across Kerala</div></div>
    <div class="stat"><div class="v">{TOTAL_CONV}</div>
      <div class="k">WhatsApp enquiries delivered to branches</div></div>
    <div class="stat"><div class="v">₹{BLENDED_CPE:,.0f}</div>
      <div class="k">Blended cost per WhatsApp enquiry</div></div>
  </div>
  <div class="callout" style="margin-top:38px;background:rgba(193,255,114,.1);
       border-left-color:var(--lime)">
    <p style="font-size:.95rem;color:rgba(255,255,255,.85)">
      <strong style="color:#C1FF72">₹73 per enquiry</strong> is the blended
      average across the whole learning period, including our first campaigns.
      The most recent campaign — KSFE Kollayad, January 2026 — delivered
      <strong style="color:#C1FF72">66 enquiries at ₹38.52 each</strong>.
      That is the number a new branch should expect to work toward.</p>
  </div>
  <div class="foot"><span>Source: Meta Ads Manager · account 590232006572483</span><span>03</span></div>
</section>

<!-- 4 TABLE -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">Campaign record</div>
  <h2 style="margin-top:12px">Every KSFE campaign we have run.</h2>
  <table>
    <thead><tr>
      <th>Campaign</th><th>Type</th><th class="num">Spend</th>
      <th class="num">Impressions</th><th class="num">Reach</th>
      <th class="num">Clicks</th><th class="num">CTR</th>
      <th class="num">Result</th><th class="num">Cost / result</th>
    </tr></thead>
    <tbody>{campaign_rows()}</tbody>
    <tfoot><tr>
      <td>Total — 7 campaigns</td><td></td>
      <td class="num">₹{TOTAL_SPEND:,.0f}</td>
      <td class="num">{TOTAL_IMPR:,}</td>
      <td class="num">{TOTAL_REACH:,}</td>
      <td class="num">{TOTAL_CLICKS:,}</td>
      <td class="num">—</td>
      <td class="num">{TOTAL_CONV} enquiries</td>
      <td class="num">₹{BLENDED_CPE:,.2f}</td>
    </tr></tfoot>
  </table>
  <p class="note" style="margin-top:12px">Awareness campaigns are optimised for
    reach, so cost is per 1,000 reached. WhatsApp campaigns are optimised for
    conversations started, so the result is enquiries.</p>
  <div class="foot"><span>Source: Meta Ads Manager · account 590232006572483</span><span>04</span></div>
</section>

<!-- 5 CHART -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">What optimisation actually buys</div>
  <h2 style="margin-top:12px">Same branch — cost per enquiry cut by two thirds.</h2>
  <div class="split">
    {bar_chart()}
    <div>
      <div class="callout">
        <div class="big">−68%</div>
        <p>Cost per WhatsApp enquiry at KSFE Kolayad, from the July 2025 peak of
           ₹121.06 to ₹38.52 in January 2026.</p>
      </div>
      <p style="margin-top:24px;font-size:.9rem">The first campaigns bought
        learning. Once creative, audience and placement were tuned against real
        branch data, the January 2026 campaign delivered <strong
        style="color:#1F2A2E">66 enquiries — more than the previous three
        campaigns combined</strong>, at the lowest cost per enquiry of the
        entire run — the compounding a retained engagement produces and a
        one-off campaign cannot.</p>
    </div>
  </div>
  <div class="foot"><span>Source: Meta Ads Manager · account 590232006572483</span><span>05</span></div>
</section>

<!-- 6 REACH -->
<section class="slide dark">
  {logo("corner")}
  <div class="eyebrow">Reach economics</div>
  <h2 style="margin-top:14px;max-width:900px">When the goal is visibility, the
    numbers get very cheap.</h2>
  <div class="rule"></div>
  <div class="stats" style="grid-template-columns:repeat(3,1fr)">
    <div class="stat"><div class="v">277,033</div>
      <div class="k">People reached for KSFE Pettah on ₹1,379 of spend</div></div>
    <div class="stat"><div class="v">₹2.37</div>
      <div class="k">Cost per 1,000 impressions — Pettah awareness campaign</div></div>
    <div class="stat"><div class="v">2.33%</div>
      <div class="k">Best click-through rate — KSFE Pettah WhatsApp campaign</div></div>
  </div>
  <div class="two" style="margin-top:40px">
    <div>
      <h3 style="color:#fff;margin-bottom:10px">What that means at branch scale</h3>
      <p>A single branch running an awareness campaign at Pettah's efficiency
         reaches a quarter of a million people in its district for less than the
         cost of one newspaper insertion — and unlike the insertion, it reports
         exactly who saw it, where, and on what device.</p>
    </div>
    <div>
      <h3 style="color:#fff;margin-bottom:10px">And where the enquiries come from</h3>
      <p>Awareness builds the pool; the WhatsApp campaigns convert it. Run
         together, the awareness audience becomes the retargeting pool for the
         enquiry campaign — which is precisely why the Kolayad cost per enquiry
         fell as the account matured.</p>
    </div>
  </div>
  <div class="foot"><span>Source: Meta Ads Manager · account 590232006572483</span><span>06</span></div>
</section>

<!-- 7 APPROACH -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">How we would run it</div>
  <h2 style="margin-top:12px">A repeatable four-step cycle, per branch.</h2>
  <div class="rule"></div>
  <div class="grid3" style="grid-template-columns:repeat(4,1fr)">
    <div class="card"><div class="num-badge">1</div>
      <h3>Catchment mapping</h3>
      <p>Radius and interest targeting built around the individual branch —
         its pincodes, its commuter flows, its subscriber profile.</p></div>
    <div class="card"><div class="num-badge">2</div>
      <h3>Malayalam-first creative</h3>
      <p>Static and video creative in Malayalam and English, written for chitty
         products and cleared against advertising norms before it runs.</p></div>
    <div class="card"><div class="num-badge">3</div>
      <h3>WhatsApp enquiry capture</h3>
      <p>Every click lands in a WhatsApp conversation routed to the branch, so
         staff receive a named enquiry rather than an anonymous impression.</p></div>
    <div class="card"><div class="num-badge">4</div>
      <h3>Monthly optimisation</h3>
      <p>Creative and audience refreshed against live cost-per-enquiry data —
         the mechanism behind the 68% reduction at Kolayad.</p></div>
  </div>
  <div class="callout" style="margin-top:34px">
    <p style="font-size:.92rem"><strong style="color:#1F2A2E">Compliance is
      built in.</strong> All creative avoids implied or guaranteed-return
      messaging, in line with the Chit Funds Act 1982 and ASCI codes on
      financial advertising. Copy is submitted for branch or Regional Office
      approval before any spend is released.</p>
  </div>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>07</span></div>
</section>

<!-- 8 PACKAGES -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">Choose your engagement</div>
  <h2 style="margin-top:12px">Two packages. Both reported on cost per enquiry.</h2>
  <div class="pkgs">
    <div class="pkg">
      <h3>Basic</h3>
      <div class="tagline">Single branch · steady enquiry flow</div>
      <div class="price">₹15,000</div>
      <div class="per">per month + ad spend</div>
      <ul>
        <li>1 branch, 1 catchment</li>
        <li>2 campaigns live — awareness + WhatsApp enquiry</li>
        <li>4 creatives per month, Malayalam and English</li>
        <li>WhatsApp enquiry routing to the branch</li>
        <li>Monthly performance report — spend, reach, enquiries, cost per enquiry</li>
        <li>Compliance pre-check on all copy</li>
        <li>Recommended ad budget: ₹5,000–8,000 per month</li>
      </ul>
    </div>
    <div class="pkg prem">
      <div class="badge">Recommended</div>
      <h3>Premium</h3>
      <div class="tagline">Multi-branch or Regional Office</div>
      <div class="price">₹35,000</div>
      <div class="per">per month + ad spend</div>
      <ul>
        <li>Up to 6 branches, each with its own catchment and creative</li>
        <li>Always-on awareness + WhatsApp enquiry + retargeting</li>
        <li>12 creatives per month, including video</li>
        <li>Pravasi Chitty campaigns targeted at Gulf geographies</li>
        <li>Offline attribution — ad click through to branch walk-in</li>
        <li>Branch-by-branch dashboard, reviewed fortnightly</li>
        <li>Dedicated account manager + quarterly review at the Regional Office</li>
        <li>Recommended ad budget: ₹30,000–50,000 per month</li>
      </ul>
    </div>
  </div>
  <p class="note">Retainers exclude GST and media spend, which is billed at cost
    directly to the platform. Pricing is indicative for a 90-day pilot and can be
    restructured to suit tender or GeM procurement requirements.</p>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>08</span></div>
</section>

<!-- 9 GOVERNANCE -->
<section class="slide">
  {logo("corner")}
  <div class="eyebrow">Working with a public-sector institution</div>
  <h2 style="margin-top:12px">Built for how KSFE actually procures.</h2>
  <div class="rule"></div>
  <div class="two">
    <div>
      <h3 style="margin-bottom:12px">What we bring</h3>
      <ul style="margin-top:6px">
        <li>An existing, verifiable record with two KSFE branches</li>
        <li>All reporting exported directly from Meta Ads Manager — auditable,
            not agency-generated</li>
        <li>Creative approval workflow with the branch or Regional Office
            before any spend</li>
        <li>Media billed at cost, with platform invoices attached</li>
        <li>Malayalam-language creative produced in-house</li>
      </ul>
    </div>
    <div>
      <h3 style="margin-bottom:12px">What we would ask of KSFE</h3>
      <ul style="margin-top:6px">
        <li>A nominated point of contact at branch or Regional Office level</li>
        <li>Access to the branch WhatsApp number for enquiry routing</li>
        <li>Approval on creative and claims before publication</li>
        <li>Guidance on the correct procurement route — direct engagement,
            tender, or GeM — which we will follow as specified</li>
      </ul>
      <div class="callout" style="margin-top:22px">
        <p style="font-size:.86rem">We are happy to begin with a single-branch
          pilot at Basic scope so performance can be judged on evidence before
          any wider commitment.</p>
      </div>
    </div>
  </div>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>09</span></div>
</section>

<!-- 10 CTA -->
<section class="slide dark">
  <div class="cover-wrap">
    {logo("cover-logo")}
    <div class="eyebrow">Next step</div>
    <h2 style="font-size:3.3rem;max-width:940px;margin-top:12px">
      Let us run one branch for 90 days<br>and report the <span class="accent">cost
      per enquiry</span>.</h2>
    <div class="cta-box">
      <div class="big">A free digital audit of your branch catchment</div>
      <p>No cost and no obligation — competitor ad activity in your catchment,
         search demand for chitty products, and a projected cost per enquiry
         based on our live KSFE campaign data.</p>
    </div>
    <div class="contact">
      <div><span>Email</span>hello@dezmos.in</div>
      <div><span>Phone</span>+91 00000 00000</div>
      <div><span>Web</span>dezmos.in</div>
    </div>
  </div>
  <div class="foot"><span>Dezmos Digital Marketing</span><span>10</span></div>
</section>

</body></html>"""


def main():
    OUT_HTML.write_text(HTML, encoding="utf-8")
    print(f"HTML written: {OUT_HTML}  ({OUT_HTML.stat().st_size:,} bytes)")

    chrome = next((c for c in CHROME_CANDIDATES if c and pathlib.Path(c).exists()), None)
    if not chrome:
        raise SystemExit("No Chromium binary found; set CHROME_CANDIDATES.")

    cmd = [
        chrome, "--headless", "--disable-gpu", "--no-sandbox",
        "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=10000",
        f"--print-to-pdf={OUT_PDF}", OUT_HTML.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if not OUT_PDF.exists():
        print(res.stdout, res.stderr)
        raise SystemExit("PDF was not produced.")
    print(f"PDF written:  {OUT_PDF}  ({OUT_PDF.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
