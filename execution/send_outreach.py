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
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

BASE_DIR  = Path(__file__).resolve().parent.parent
TMP_DIR   = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)

LEADS_FILE = TMP_DIR / "leads.json"
LOG_FILE   = TMP_DIR / "outreach_log.json"

TEMPLATES_DIR = Path(__file__).resolve().parent / "email_templates"

# ── SMTP config ───────────────────────────────────────────────────────────────
SMTP_HOST = "mail.privateemail.com"
SMTP_PORT = 587
SMTP_USER = "hello@vlmcreateflow.com"
SMTP_PASS = "Vlmcreateflow1!"
FROM_ADDR = "hello@vlmcreateflow.com"
FROM_NAME = "Ty | Viral Lense Media"

# ── Sequence schedule ─────────────────────────────────────────────────────────
# Maps (vertical, emails_sent) -> (template_file, day_offset_from_last_send)
SEQUENCE = {
    # emails_sent=0 means nothing sent yet — send email 1 immediately (day 0)
    # emails_sent=1 means email 1 sent — send email 2 after 3 days
    # emails_sent=2 means email 2 sent — send email 3 after 7 days from email 1
    "ad_agency": [
        "agency_email_1.txt",
        "agency_email_2.txt",
        "agency_email_3.txt",
    ],
    "financial_advisor": [
        "financial_email_1.txt",
        "financial_email_2.txt",
        "financial_email_3.txt",
    ],
    "coach_consultant": [
        "coaching_email_1.txt",
        "coaching_email_2.txt",
        "coaching_email_3.txt",
    ],
}

# Days between emails: email 2 sends 3 days after email 1, email 3 sends 4 days after email 2 (7 total)
SEND_GAPS = [0, 3, 4]   # gap from previous send (day 0, then +3, then +4 = day 7)


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
    msg["Reply-To"] = FROM_ADDR

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

    print(f"\nDone. Sent: {sent_count} | Skipped: {skip_count} | Errors: {error_count}")


if __name__ == "__main__":
    main()
