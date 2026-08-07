#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
send_outreach.py — Automated cold email sender for VLM B2B outreach.

Sequence:
  Day 0  → Email 1 (initial cold email)
  Day 3  → Email 2 (follow-up with proof)
  Day 7  → Email 3 (final, booking CTA)

Usage:
    python3 execution/send_outreach.py [--dry-run]

Run daily at 9:00 AM Bangkok time via cron.
Reads from:   .tmp/leads.json
Logs to:      .tmp/outreach_log.json
SMTP:         mail.privateemail.com:587
From:         hello@vlmcreateflow.com
"""

import os, sys, json, smtplib, argparse
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

BASE_DIR  = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

TMP_DIR   = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

LEADS_FILE = TMP_DIR / "leads.json"
LOG_FILE   = TMP_DIR / "outreach_log.json"

TEMPLATES_DIR = Path(__file__).resolve().parent / "email_templates"

# ── SMTP config ───────────────────────────────────────────────────────────────
SMTP_HOST = "mail.privateemail.com"
SMTP_PORT = 587
SMTP_USER = "hello@vlmcreateflow.com"
SMTP_PASS = os.getenv("SMTP_HELLO_PASS", "PLACEHOLDER")
FROM_ADDR = "hello@vlmcreateflow.com"
FROM_NAME = "Ty | Viral Lense Media"
REPLY_TO  = "virallensemediavlm@gmail.com"   # Gmail MCP monitors this for replies

# ── Sequence schedule ─────────────────────────────────────────────────────────
# Maps (vertical, emails_sent) -> (template_file, day_offset_from_last_send)
SEQUENCE = {
    # Escape-to-Arrival framework — 4 emails per lead
    # emails_sent=0 → email 1 (day 0):  Escape frame — their pain
    # emails_sent=1 → email 2 (day 3):  Arrival frame — the result
    # emails_sent=2 → email 3 (day 7):  Setup call CTA + setup fee framing
    # emails_sent=3 → email 4 (day 14): Breakup email
    "ad_agency": [
        "agency_email_1.txt",
        "agency_email_2.txt",
        "agency_email_3.txt",
        "agency_email_4.txt",
    ],
    "financial_advisor": [
        "financial_email_1.txt",
        "financial_email_2.txt",
        "financial_email_3.txt",
        "financial_email_4.txt",
    ],
    "coach_consultant": [
        "coaching_email_1.txt",
        "coaching_email_2.txt",
        "coaching_email_3.txt",
        "coaching_email_4.txt",
    ],
}

# Gap (days) from previous send before sending this email index
# Index 0=day 0, 1=+3 days, 2=+4 days (day 7 total), 3=+7 days (day 14 total)
SEND_GAPS = [0, 3, 4, 7]


# ── Template loader ───────────────────────────────────────────────────────────
def load_template(filename: str) -> dict:
    """Load a template file, parse subject line and body."""
    path = TEMPLATES_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    content = path.read_text(encoding="utf-8")
    lines   = content.strip().splitlines()

    subject = ""
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("subject:"):
            subject = line.split(":", 1)[1].strip()
        elif line.strip() == "" and subject:
            body_start = i + 1
            break

    body = "\n".join(lines[body_start:]).strip()
    return {"subject": subject, "body": body}


def render(template: dict, lead: dict) -> dict:
    """Fill {{variable}} placeholders in subject and body."""
    first_name = lead.get("name", "").split()[0] if lead.get("name") else "there"
    subs = {
        "{{first_name}}": first_name,
        "{{name}}":       lead.get("name", ""),
        "{{company}}":    lead.get("company", "your company"),
        "{{role}}":       lead.get("role", ""),
    }
    subject = template["subject"]
    body    = template["body"]
    for k, v in subs.items():
        subject = subject.replace(k, v)
        body    = body.replace(k, v)
    return {"subject": subject, "body": body}


# ── Email sender ──────────────────────────────────────────────────────────────
def send_email(to_addr: str, subject: str, body: str, dry_run: bool = False) -> bool:
    """Send a plain-text email. Returns True on success."""
    if dry_run:
        print(f"    [DRY RUN] Would send to {to_addr}: {subject}")
        return True

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"{FROM_NAME} <{FROM_ADDR}>"
    msg["To"]      = to_addr
    msg["Reply-To"] = REPLY_TO

    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_ADDR, [to_addr], msg.as_string())
        return True
    except Exception as e:
        print(f"    SMTP ERROR to {to_addr}: {e}")
        return False


# ── Log helpers ───────────────────────────────────────────────────────────────
def load_log() -> list:
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE) as f:
        return json.load(f)


def append_log(entry: dict):
    log = load_log()
    log.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


# ── Scheduling logic ──────────────────────────────────────────────────────────
def should_send(lead: dict) -> bool:
    """Return True if this lead is due for their next email today."""
    emails_sent = lead.get("emails_sent", 0)
    vertical    = lead.get("vertical", "")

    if vertical not in SEQUENCE:
        return False

    # Already completed the sequence
    if emails_sent >= len(SEQUENCE[vertical]):
        return False

    # Replied or booked — skip
    if lead.get("replied") or lead.get("booked"):
        return False

    # Email is required
    if not lead.get("email"):
        return False

    # Day 0 — never sent — always eligible
    if emails_sent == 0:
        return True

    # Check if enough days have passed since last send
    last_sent_str = lead.get("last_sent_at")
    if not last_sent_str:
        return True  # data gap, send anyway

    last_sent = datetime.fromisoformat(last_sent_str)
    required_gap = SEND_GAPS[emails_sent]  # days needed before sending this email
    return datetime.now() >= last_sent + timedelta(days=required_gap)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview emails without sending")
    args = parser.parse_args()

    if not LEADS_FILE.exists():
        print("No leads.json found. Run source_leads.py first.")
        sys.exit(0)

    with open(LEADS_FILE) as f:
        leads = json.load(f)

    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    print(f"=== VLM Outreach Sender — {now_str} ===\n")
    if args.dry_run:
        print("[DRY RUN mode — no emails will be sent]\n")

    sent_count  = 0
    skip_count  = 0
    error_count = 0

    for lead in leads:
        if not should_send(lead):
            skip_count += 1
            continue

        vertical    = lead.get("vertical", "")
        emails_sent = lead.get("emails_sent", 0)
        template_file = SEQUENCE[vertical][emails_sent]

        try:
            tpl      = load_template(template_file)
            rendered = render(tpl, lead)
        except Exception as e:
            print(f"  ERROR loading template {template_file}: {e}")
            error_count += 1
            continue

        to_addr  = lead["email"]
        seq_num  = emails_sent + 1  # human-readable (1, 2, 3)

        print(f"  Sending email {seq_num}/3 to {lead.get('name', '?')} "
              f"<{to_addr}> [{lead.get('niche', '')}]")

        success = send_email(to_addr, rendered["subject"], rendered["body"], args.dry_run)

        if success:
            lead["emails_sent"]  = emails_sent + 1
            lead["last_sent_at"] = now_str
            if lead.get("status") == "new":
                lead["status"] = "contacted"
            sent_count += 1

            append_log({
                "timestamp":    now_str,
                "lead_id":      lead.get("id"),
                "name":         lead.get("name"),
                "email":        to_addr,
                "company":      lead.get("company"),
                "vertical":     vertical,
                "seq_email_num": seq_num,
                "subject":      rendered["subject"],
                "status":       "sent",
            })
        else:
            error_count += 1
            append_log({
                "timestamp":    now_str,
                "lead_id":      lead.get("id"),
                "email":        to_addr,
                "seq_email_num": seq_num,
                "status":       "failed",
            })

    # Persist updated leads
    if not args.dry_run and sent_count > 0:
        with open(LEADS_FILE, "w") as f:
            json.dump(leads, f, indent=2)

        # Sync outreach fields → vlm-crm/leads_local.json (keeps CRM dashboard live)
        crm_path = Path(__file__).parent.parent / "vlm-crm" / "leads_local.json"
        if crm_path.exists():
            with open(crm_path) as f:
                crm_leads = json.load(f)
            outreach_map = {l["id"]: l for l in leads}
            for cl in crm_leads:
                src = outreach_map.get(cl["id"], {})
                cl["emails_sent"]  = src.get("emails_sent", 0)
                cl["drip_day"]     = src.get("drip_day", 0)
                cl["last_sent_at"] = src.get("last_sent_at", "")
                cl["replied"]      = src.get("replied", False)
                cl["booked"]       = src.get("booked", False)
                cl["vertical"]     = src.get("vertical", cl.get("niche", ""))
            with open(crm_path, "w") as f:
                json.dump(crm_leads, f, indent=2)
            print(f"CRM synced → {crm_path}")

    print(f"\nDone. Sent: {sent_count} | Skipped: {skip_count} | Errors: {error_count}")


if __name__ == "__main__":
    main()
