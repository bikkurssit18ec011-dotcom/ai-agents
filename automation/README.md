# Dezmos Email Automation (n8n)

A reusable cold-outreach engine for Dezmos Digital Marketing, configured out of
the box to send the KSFE performance-marketing proposal to the branch leads in
`leads/ksfe-trivandrum-branches.csv`.

It is **one workflow, not one campaign**. Every campaign-specific value lives in
a single node, so a new campaign is a duplicate of the workflow plus a new CSV
and template — no rewiring.

```
automation/
├── n8n/
│   ├── dezmos-email-automation.workflow.json   <- the workflow
│   ├── setup-n8n.py                            <- imports + configures it for you
│   └── test-logic.js                           <- offline test for the Code nodes
├── templates/
│   ├── ksfe-regional-office.html               <- P0 - the real decision makers
│   └── ksfe-branch-outreach.html               <- P1-P3 - asks for a referral
└── data/
    ├── suppression.csv                         <- unsubscribes + hard bounces
    └── send-log.csv                            <- append-only audit trail
```

---

## Read this before you send anything

**1. Most of the email addresses are derived, not verified.** Only a handful of
`<code>@ksfe.com` addresses in the leads CSV were actually observed in a source;
the rest were inferred from KSFE's naming convention (see `leads/README.md`).
Bulk-sending to unverified addresses produces bounces, and bounces on a young
sending domain are how you get filtered permanently. Run an email-verification
pass on the P0/P1 addresses first, or start with the two Regional Office
addresses only — both of those are confirmed.

**2. Do not mail all 35 rows on day one.** KSFE is a government PSU. Branch
managers cannot buy marketing; the Regional Offices and Head Office can. Thirty-five
near-identical emails hitting one organisation in an hour reads as spam and gets
your domain blocked internally. The workflow ships configured for exactly this:
`priorityFilter=P0`, `dailyLimit=2`, `throttleSeconds=90`.

**3. `dryRun` ships as `true`.** Nothing leaves the server until you deliberately
turn it off. Run it once as-is and read the execution log before changing that.

**4. The 892 KB PDF attachment is a deliverability cost.** Attachments on cold
mail raise spam scores. Once you have the deck hosted somewhere public, set
`attachDeck=false` and put the link in `deckUrl`; the templates already accept a
`{{deck_url}}` placeholder.

---

## How the workflow is built

```
Manual Trigger
  └─ Campaign Config ──────────────┬─────────────────────────────┐
                                   │                             │
        Read Template ──> Template To Text                 Read Deck PDF
              └─> Read Suppression ──> Suppression To Rows        │
                    └─> Read Leads CSV ──> Leads To Rows          │
                          └─> Build Send List                     │
                                └─> Loop Over Leads ──────────────│───┐
                                      │ (loop)                    │   │
                                      ├─> Render Email ──> Attach Deck│
                                      │                        └─> Dry Run?
                                      │            dry ──> Preview Only ──┤
                                      │           live ──> Send Email     │
                                      │                      └─> Throttle ┘
                                      │ (done)
                                      └─> Build Log Rows ──> Log To CSV ──> Write Send Log
```

### What each node does

| Node | Why it exists |
|---|---|
| **Campaign Config** | The only node you edit per campaign. 16 settings — paths, sender, subject, filters, throttle, dry-run. |
| **Read Template → Template To Text** | Loads the HTML template off disk as text, so copy changes never require touching the workflow. |
| **Read Suppression → Suppression To Rows** | Loads the unsubscribe / bounce list. |
| **Read Leads CSV → Leads To Rows** | Loads the lead list. Any CSV with an `email` column works. |
| **Build Send List** | The gatekeeper. Validates address format, applies the priority filter, drops suppressed addresses and duplicates, caps at `dailyLimit`. Logs a reason for every row it rejects, so a short send is never silent. |
| **Read Deck PDF** | Loads the attachment once into binary property `deck`. |
| **Loop Over Leads** | Batch size 1 — one email per iteration, which is what makes throttling possible. |
| **Render Email** | Substitutes `{{placeholders}}`, builds the subject, and derives a plain-text alternative from the HTML. **Throws if any placeholder is left unresolved** rather than mailing a broken `{{branch_name}}` to a client. |
| **Attach Deck** | Merges the rendered email with the PDF binary by position. |
| **Dry Run?** | Routes to a no-op preview or to the real send. |
| **Send Email** | SMTP. Sends `both` HTML and plain text, sets Reply-To, attaches `deck` only if `attachDeck` is true. Retries 3× and continues on error so one bad address cannot kill the run. |
| **Throttle** | Waits `throttleSeconds` between sends. Only on the live path. |
| **Build Log Rows → Log To CSV → Write Send Log** | Appends an audit row per message to `send-log.csv`. |

### Placeholders available in templates

`{{branch_name}}` `{{branch_code}}` `{{contact_name}}` `{{locality}}`
`{{region_office}}` `{{campaign}}` `{{sender_name}}` `{{sender_email}}`
`{{deck_url}}` `{{unsubscribe_email}}`

`contact_name` resolves to `Sir/Madam` for Regional Offices and `Branch Manager`
otherwise. `locality` is the first line of the address column.

---

## Setup

> **Verified end-to-end against n8n 2.34.6.** The workflow was imported into a
> live instance and executed in dry-run mode; the full chain runs green and
> writes the audit log. The two fixes that took to get there are baked in below.

### Automated: `setup-n8n.py`

One script imports the workflow, creates the SMTP credential, wires it to the
Send Email node, and rewrites the file paths for your machine. Python 3 stdlib
only — nothing to install. Re-running **updates** the workflow rather than
creating a duplicate.

```bash
# n8n -> Settings -> n8n API -> Create an API key
export N8N_API_KEY='n8n_api_...'
export SMTP_PASS='your-app-password'

# see exactly what it would do, without touching n8n
python3 automation/n8n/setup-n8n.py --dry-run \
    --smtp-host smtp.zoho.in --smtp-port 587

# do it
python3 automation/n8n/setup-n8n.py \
    --smtp-host smtp.zoho.in --smtp-port 587
```

Useful flags:

| Flag | Purpose |
|---|---|
| `--data-root` | Repo path **as n8n sees it**. For Docker this is the container-side mount (`/data/dezmos`), not the host path. |
| `--template` | Swap templates, e.g. `--template ksfe-branch-outreach.html` |
| `--leads` | Point at a different lead CSV |
| `--priority` / `--daily-limit` / `--throttle` | Campaign pacing |
| `--live` | Sets `dryRun=false`. **Without it the workflow imports in dry-run and sends nothing.** |
| `--skip-credential` | Import the workflow only; wire SMTP by hand |
| `--dry-run` | Print the plan, write nothing |

### Required: let n8n read your files

**n8n blocks filesystem access for the Read/Write File node by default.** Without
this the workflow fails on its first node with `Access to the file is not
allowed.` — this is the single most likely reason your import "does not work".

Set `N8N_RESTRICT_FILE_ACCESS_TO` to the directory holding this repo:

```bash
# npm / systemd install
export N8N_RESTRICT_FILE_ACCESS_TO=/path/to/ai-agents
```

For Docker, pass it alongside the volume mount:

```bash
docker run -d --name n8n -p 5678:5678 \
  -v ~/.n8n:/home/node/.n8n \
  -v /path/to/ai-agents:/data/dezmos \
  -e N8N_RESTRICT_FILE_ACCESS_TO=/data/dezmos \
  -e N8N_SECURE_COOKIE=false \
  docker.n8n.io/n8nio/n8n
```

That mount makes `--data-root /data/dezmos` the correct value, and the config
paths resolve to:

| Setting | Resolves to |
|---|---|
| `leadsCsvPath` | `/data/dezmos/leads/ksfe-trivandrum-branches.csv` |
| `templatePath` | `/data/dezmos/automation/templates/ksfe-regional-office.html` |
| `attachmentPath` | `/data/dezmos/deck/Dezmos-KSFE-Performance-Marketing-Proposal.pdf` |
| `suppressionPath` | `/data/dezmos/automation/data/suppression.csv` |
| `logPath` | `/data/dezmos/automation/data/send-log.csv` |

On **n8n Cloud** there is no filesystem at all. Replace the three `Read …` file
nodes with HTTP Request nodes pointing at raw URLs, or with Google Drive / Google
Sheets nodes. Everything downstream is unchanged.

### SMTP credential

`setup-n8n.py` creates this for you. To do it by hand: **Credentials → New → SMTP**.

| Field | Value |
|---|---|
| User | `info@dezmosdigitalmarketing.com` |
| Password | app password / SMTP key — **not** the mailbox login password |
| Host | Google Workspace `smtp.gmail.com`, Zoho `smtp.zoho.in` |
| Port | `587` |
| SSL/TLS | off — 587 uses STARTTLS. Turn it on only for port 465. |

**Set up SPF, DKIM and DMARC on `dezmosdigitalmarketing.com` before the first
live send.** Cold mail from a domain without them lands in spam regardless of
how good the copy is.

### Manual import

If you would rather not use the script: **Workflows → Import from File →**
`automation/n8n/dezmos-email-automation.workflow.json`, then open the Send Email
node and select your SMTP credential, and fix the five paths in Campaign Config.

---

## Running a campaign

1. **Test the logic offline first** (no n8n, no SMTP, nothing sent):

   ```bash
   node automation/n8n/test-logic.js
   ```

   Runs the two Code nodes against the real CSV and asserts the filters, the
   suppression list, and both templates. 18 checks. Run it after any edit to a
   template or to `Build Send List`.

2. **Dry run in n8n.** Leave `dryRun=true`, hit **Execute Workflow**, then open
   the **Build Send List** node output and read the console log — it prints every
   lead it accepted and a reason for every one it skipped. Open **Render Email**
   and read the actual HTML that would have gone out.

3. **Go live, small.** Re-run the setup script with `--live` (or flip `dryRun`
   in the UI), keeping `priorityFilter=P0` and `dailyLimit=2`:

   ```bash
   python3 automation/n8n/setup-n8n.py --live --skip-credential
   ```

   That sends two emails — to the Urban and Rural Regional
   Offices, the only two confirmed addresses in the file.

4. **Wait a week.** Check bounces and replies before widening.

5. **Widen.** Five a day for three days covers the P1 tier:

   ```bash
   python3 automation/n8n/setup-n8n.py --live --skip-credential \
       --template ksfe-branch-outreach.html \
       --priority P1 --daily-limit 5 --throttle 120
   ```

### Recommended pacing

| Stage | priorityFilter | dailyLimit | Template |
|---|---|---|---|
| Week 1 | `P0` | 2 | `ksfe-regional-office.html` |
| Week 2 | `P1` | 5 | `ksfe-branch-outreach.html` |
| Week 3 | `P2` | 5 | `ksfe-branch-outreach.html` |
| Later | `P3` | 5 | `ksfe-branch-outreach.html` |

---

## Reusing it for other clients

This is the point of the build. For a new campaign:

1. Duplicate the workflow in n8n, rename it.
2. Drop a new lead CSV anywhere — it needs an `email` column, and a `priority`
   column if you want tiering. `branch_name`, `branch_code`, `address` and
   `region_office` feed the placeholders; missing ones degrade gracefully except
   where a template references them.
3. Write a new HTML template in `automation/templates/`.
4. Update **Campaign Config**: `campaignName`, `leadsCsvPath`, `templatePath`,
   `attachmentPath`, `subjectTemplate`, `priorityFilter`.
5. Dry run, then send.

Nothing else changes. The suppression list and the send log are shared across all
campaigns on purpose — someone who unsubscribes from one Dezmos campaign should
not receive the next one.

### To schedule it

Add a **Schedule Trigger** node and wire it into **Campaign Config** alongside
the Manual Trigger. With `dailyLimit` set, a daily 10:00 schedule drains the list
at a safe rate on its own. Rows already sent are *not* automatically excluded —
either add sent addresses to the suppression list, or split the CSV per batch.

---

## Handling replies and unsubscribes

- **Unsubscribe:** add the address to `automation/data/suppression.csv` with a
  reason and date. The next run drops it automatically.
- **Hard bounce:** same file, reason `hard bounce`. Do not retry — repeated
  sends to a dead address are the fastest way to damage the sending domain.
- **A reply:** stop the automation for that branch and answer by hand. This
  workflow opens conversations; it should not try to hold them.

---

## Known limits

- **No built-in de-duplication across runs.** Re-running with the same config
  re-sends. Use the suppression list or split CSVs between batches.
- **The send log is written once at the end of a run**, so a run that crashes
  mid-way records nothing. The per-message record is the SMTP server's own log.
- **`Send Email` is set to `continueRegularOutput`**, so a failed address is
  skipped rather than aborting the run — but the log will still mark it `SENT`.
  Cross-check against bounce mail in the inbox.
- **The dry-run path skips the throttle**, so a dry run finishes immediately.
  That is intentional, but it means a dry run does not rehearse the real timing.
- **`setup-n8n.py` creates a new SMTP credential every time it runs** unless you
  pass `--skip-credential`. Use that flag on re-runs so you do not accumulate
  duplicates in the credential list.
