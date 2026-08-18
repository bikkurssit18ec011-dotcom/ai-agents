#!/usr/bin/env python3
"""Import the Dezmos email workflow into a self-hosted n8n and configure it.

Talks to the n8n public REST API. Python 3 stdlib only - no pip installs.

  1. Rewrites the file paths in the Campaign Config node so they point at this
     repo on the machine n8n can actually see.
  2. Creates (or reuses) the SMTP credential for info@dezmosdigitalmarketing.com.
  3. Imports the workflow, wiring the Send Email node to that credential.
  4. Re-running updates the existing workflow instead of making a duplicate.

Quick start:
    # n8n -> Settings -> n8n API -> Create an API key
    export N8N_API_KEY='n8n_api_...'
    export SMTP_PASS='your-app-password'

    python3 automation/n8n/setup-n8n.py \
        --smtp-host smtp.zoho.in --smtp-port 587

Run with --dry-run first to see exactly what it would send.
"""

import argparse
import getpass
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

WORKFLOW_NAME = "Dezmos - Email Outreach Automation"
CRED_NAME = "Dezmos SMTP (info@dezmosdigitalmarketing.com)"
HERE = pathlib.Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
WORKFLOW_FILE = HERE / "dezmos-email-automation.workflow.json"


def api(base, key, method, path, payload=None):
    url = f"{base.rstrip('/')}/api/v1{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("X-N8N-API-KEY", key)
    req.add_header("Accept", "application/json")
    if data:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:600]
        raise SystemExit(
            f"\n  n8n API {method} {path} failed: HTTP {e.code}\n  {detail}\n"
            + ("  -> 401 means a bad or missing API key. Create one at\n"
               "     Settings -> n8n API -> Create an API key.\n" if e.code == 401 else "")
        )
    except urllib.error.URLError as e:
        raise SystemExit(
            f"\n  Cannot reach n8n at {base} ({e.reason}).\n"
            "  Is it running? Try: curl -sS "
            f"{base.rstrip('/')}/healthz\n"
        )


def rewrite_paths(wf, data_root, template=None, leads=None):
    """Point the Campaign Config paths at the real filesystem."""
    mapping = {
        "leadsCsvPath":    "leads/ksfe-trivandrum-branches.csv",
        "templatePath":    "automation/templates/ksfe-regional-office.html",
        "attachmentPath":  "deck/Dezmos-KSFE-Performance-Marketing-Proposal.pdf",
        "suppressionPath": "automation/data/suppression.csv",
        "logPath":         "automation/data/send-log.csv",
    }
    if template:
        mapping["templatePath"] = (template if template.startswith("/")
                                   else f"automation/templates/{template}")
    if leads:
        mapping["leadsCsvPath"] = leads

    cfg = next(n for n in wf["nodes"] if n["name"] == "Campaign Config")
    changed = []
    for a in cfg["parameters"]["assignments"]["assignments"]:
        if a["name"] in mapping:
            v = mapping[a["name"]]
            a["value"] = v if v.startswith("/") else f"{data_root.rstrip('/')}/{v}"
            changed.append((a["name"], a["value"]))
    return changed


def apply_overrides(wf, args):
    cfg = next(n for n in wf["nodes"] if n["name"] == "Campaign Config")
    overrides = {
        "fromEmail":       args.from_email,
        "replyTo":         args.reply_to or args.from_email,
        "priorityFilter":  args.priority,
        "dailyLimit":      args.daily_limit,
        "throttleSeconds": args.throttle,
        "dryRun":          not args.live,
    }
    applied = []
    for a in cfg["parameters"]["assignments"]["assignments"]:
        if a["name"] in overrides and overrides[a["name"]] is not None:
            a["value"] = overrides[a["name"]]
            applied.append((a["name"], a["value"]))
    return applied


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default=os.environ.get("N8N_URL", "http://localhost:5678"))
    p.add_argument("--api-key", default=os.environ.get("N8N_API_KEY"))
    p.add_argument("--data-root", default=str(REPO_ROOT),
                   help="Path to this repo AS n8n SEES IT. For Docker this is the "
                        "container-side mount (e.g. /data/dezmos), not the host path.")
    p.add_argument("--from-email", default="info@dezmosdigitalmarketing.com")
    p.add_argument("--reply-to", default=None)
    p.add_argument("--smtp-host", default=os.environ.get("SMTP_HOST"))
    p.add_argument("--smtp-port", type=int, default=int(os.environ.get("SMTP_PORT", 587)))
    p.add_argument("--smtp-user", default=None, help="defaults to --from-email")
    p.add_argument("--smtp-pass", default=os.environ.get("SMTP_PASS"))
    p.add_argument("--template", default=None,
                   help="template filename under automation/templates/, or an "
                        "absolute path. Default: ksfe-regional-office.html")
    p.add_argument("--leads", default=None,
                   help="lead CSV path relative to --data-root, or absolute")
    p.add_argument("--priority", default="P0")
    p.add_argument("--daily-limit", type=int, default=2)
    p.add_argument("--throttle", type=int, default=90)
    p.add_argument("--live", action="store_true",
                   help="set dryRun=false. Without this the workflow imports in "
                        "dry-run mode and sends nothing.")
    p.add_argument("--skip-credential", action="store_true",
                   help="import the workflow only; wire SMTP by hand in the UI")
    p.add_argument("--dry-run", action="store_true",
                   help="show what would happen, contact n8n only to read")
    args = p.parse_args()

    if not WORKFLOW_FILE.exists():
        raise SystemExit(f"Workflow file not found: {WORKFLOW_FILE}")
    if not args.api_key:
        raise SystemExit(
            "No API key. Create one in n8n at Settings -> n8n API, then:\n"
            "  export N8N_API_KEY='n8n_api_...'")

    wf = json.loads(WORKFLOW_FILE.read_text())
    print(f"n8n            {args.url}")
    print(f"workflow file  {WORKFLOW_FILE.name} ({len(wf['nodes'])} nodes)")

    print("\nPaths written into Campaign Config:")
    for name, val in rewrite_paths(wf, args.data_root, args.template, args.leads):
        print(f"  {name:16} {val}")

    print("\nCampaign settings:")
    for name, val in apply_overrides(wf, args):
        print(f"  {name:16} {val}")
    if not args.live:
        print("  -> dryRun is TRUE. Nothing will be emailed. Re-run with --live to send.")

    # ---- credential ------------------------------------------------------
    cred_id = None
    if not args.skip_credential:
        if not args.smtp_host:
            raise SystemExit("\n--smtp-host is required (or use --skip-credential).")
        smtp_pass = args.smtp_pass or getpass.getpass("SMTP password (app password): ")
        if not smtp_pass:
            raise SystemExit("SMTP password is required.")
        smtp_user = args.smtp_user or args.from_email

        payload = {
            "name": CRED_NAME,
            "type": "smtp",
            "data": {
                "user": smtp_user,
                "password": smtp_pass,
                "host": args.smtp_host,
                "port": args.smtp_port,
                # 465 = implicit TLS; 587 = STARTTLS, which means secure=false
                "secure": args.smtp_port == 465,
                "disableStartTls": False,
            },
        }
        print(f"\nSMTP credential  {smtp_user} @ {args.smtp_host}:{args.smtp_port} "
              f"(secure={payload['data']['secure']})")

        if args.dry_run:
            redacted = {**payload, "data": {**payload["data"], "password": "***"}}
            print("  [dry-run] would POST /credentials")
            print("  " + json.dumps(redacted))
        else:
            created = api(args.url, args.api_key, "POST", "/credentials", payload)
            cred_id = created.get("id")
            print(f"  created, id={cred_id}")

    if cred_id:
        send = next(n for n in wf["nodes"] if n["name"] == "Send Email")
        send["credentials"] = {"smtp": {"id": str(cred_id), "name": CRED_NAME}}
        print(f"  Send Email node wired to credential {cred_id}")
    elif not args.dry_run:
        print("\n  NOTE: no credential attached. Open the Send Email node in the UI "
              "and pick your SMTP credential before sending.")

    # ---- workflow --------------------------------------------------------
    # The public API rejects unknown top-level keys, so send only these four.
    body = {
        "name": WORKFLOW_NAME,
        "nodes": wf["nodes"],
        "connections": wf["connections"],
        "settings": wf.get("settings", {"executionOrder": "v1"}),
    }

    if args.dry_run:
        print(f"\n[dry-run] would import '{WORKFLOW_NAME}' "
              f"({len(body['nodes'])} nodes). Nothing was written.")
        return

    existing = api(args.url, args.api_key, "GET", "/workflows?limit=250").get("data", [])
    match = next((w for w in existing if w.get("name") == WORKFLOW_NAME), None)

    if match:
        result = api(args.url, args.api_key, "PUT", f"/workflows/{match['id']}", body)
        print(f"\nUpdated existing workflow id={result.get('id', match['id'])}")
    else:
        result = api(args.url, args.api_key, "POST", "/workflows", body)
        print(f"\nImported new workflow id={result.get('id')}")

    wf_id = result.get("id", match["id"] if match else "")
    print(f"Open it:  {args.url.rstrip('/')}/workflow/{wf_id}")
    print("\nNext:")
    print("  1. Execute Workflow once with dryRun=true and read the")
    print("     Build Send List node log.")
    print("  2. Confirm SPF/DKIM/DMARC on dezmosdigitalmarketing.com.")
    print("  3. Re-run this script with --live to flip dryRun off.")


if __name__ == "__main__":
    sys.exit(main())
