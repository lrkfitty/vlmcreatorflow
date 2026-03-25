#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
monitor_inbox.py — Monitor virallensemediavlm@gmail.com for replies to outreach.

For each reply from a known lead:
  1. Classify intent via keywords: interested / not_now / objection / unsubscribe / other
  2. Save raw reply + classification to .tmp/reply_drafts/{lead_id}_{ts}.json
  3. Update lead status in .tmp/leads.json
  4. Log everything to .tmp/inbox_monitor.log

Drafting is handled interactively via Claude Code + Gmail MCP — no API key needed here.

Usage:
    python3 execution/monitor_inbox.py [--dry-run]

Requirements in .env:
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
    (myaccount.google.com > Security > 2-Step Verification > App Passwords)
    Note: your regular Gmail login password does NOT work for IMAP.

Cron (runs 5 min after outreach sender):
    5 3 * * * /opt/homebrew/bin/python3.11 "/.../execution/monitor_inbox.py"
"""

import os, sys, json, imaplib, email, argparse, logging
from email.header import decode_header
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR   = Path(__file__).resolve().parent.parent
TMP_DIR    = BASE_DIR / ".tmp"
DRAFTS_DIR = TMP_DIR / "reply_drafts"
LEADS_FILE = TMP_DIR / "leads.json"
LOG_FILE   = TMP_DIR / "inbox_monitor.log"

TMP_DIR.mkdir(exist_ok=True)
DRAFTS_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

GMAIL_USER     = "virallensemediavlm@gmail.com"
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
IMAP_HOST      = "imap.gmail.com"
IMAP_PORT      = 993


# ── Lead helpers ──────────────────────────────────────────────────────────────
def load_leads() -> list:
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE) as f:
        return json.load(f)

def save_leads(leads: list):
    with open(LEADS_FILE, "w") as f:
        json.dump(leads, f, indent=2)

def find_lead_by_email(leads: list, sender_email: str) -> dict | None:
    return next((l for l in leads if l.get("email","").lower() == sender_email.lower()), None)


# ── Gmail IMAP ────────────────────────────────────────────────────────────────
def connect_gmail() -> imaplib.IMAP4_SSL:
    if not GMAIL_PASSWORD:
        raise RuntimeError(
            "GMAIL_APP_PASSWORD not set in .env\n"
            "  1. Enable 2-Step Verification on virallensemediavlm@gmail.com\n"
            "  2. Go to myaccount.google.com > Security > App Passwords\n"
            "  3. Generate one for Mail > Mac\n"
            "  4. Add to .env:  GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx"
        )
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(GMAIL_USER, GMAIL_PASSWORD)
    return mail

def decode_str(value) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""

def parse_sender(from_header: str) -> tuple:
    import re
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        return from_header[:m.start()].strip().strip('"'), m.group(1).strip()
    return "", from_header.strip()

def get_text_body(msg: email.message.Message) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct  = part.get_content_type()
            cd  = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")
    return body.strip()

def fetch_unread_replies(mail: imaplib.IMAP4_SSL, lead_emails: set) -> list:
    mail.select("INBOX")
    _, data = mail.search(None, "UNSEEN")
    uids = data[0].split()
    replies = []
    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])
        from_raw = decode_str(msg.get("From", ""))
        sender_name, sender_email = parse_sender(from_raw)
        if sender_email.lower() not in lead_emails:
            mail.store(uid, "-FLAGS", "\\Seen")   # put back as unread
            continue
        parts = decode_header(msg.get("Subject", ""))
        subject = "".join(
            p.decode(enc or "utf-8") if isinstance(p, bytes) else p
            for p, enc in parts
        )
        replies.append({
            "uid":          uid.decode(),
            "sender_name":  sender_name,
            "sender_email": sender_email.lower(),
            "subject":      subject,
            "body":         get_text_body(msg)[:3000],
            "date":         msg.get("Date", ""),
        })
    return replies


# ── Keyword classifier (no API needed) ───────────────────────────────────────
_INTERESTED = [
    "interested", "tell me more", "sounds good", "let's talk", "lets talk",
    "book", "schedule", "calendar", "available", "demo", "call", "yes",
    "how does", "how much", "pricing", "love to", "would like", "sign me up",
    "when can", "reach out", "set something up",
]
_NOT_NOW = [
    "not right now", "not a good time", "reach back", "check back", "later",
    "next quarter", "next year", "busy", "tied up", "not in the budget",
    "maybe", "possibly", "future", "not currently",
]
_OBJECTION = [
    "too expensive", "can't afford", "price", "cost", "how do i know",
    "prove", "skeptical", "not sure", "concerned", "question", "unclear",
    "what exactly", "how does it work", "results", "guarantee",
]
_UNSUB = [
    "unsubscribe", "remove me", "take me off", "stop emailing", "stop contacting",
    "do not contact", "do not email", "not interested", "please don't",
    "opt out", "opt-out",
]

def classify_reply(body: str) -> str:
    text = body.lower()
    if any(k in text for k in _UNSUB):
        return "unsubscribe"
    if any(k in text for k in _INTERESTED):
        return "interested"
    if any(k in text for k in _OBJECTION):
        return "objection"
    if any(k in text for k in _NOT_NOW):
        return "not_now"
    return "other"

STATUS_MAP = {
    "interested":  "replied_interested",
    "not_now":     "replied_not_now",
    "objection":   "replied_objection",
    "unsubscribe": "unsubscribed",
    "other":       "replied_other",
}


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    log.info("=== VLM Inbox Monitor ===")

    if not GMAIL_PASSWORD:
        log.error(
            "GMAIL_APP_PASSWORD not set.\n"
            "  Enable 2FA on virallensemediavlm@gmail.com, then generate an App Password\n"
            "  at myaccount.google.com > Security > App Passwords\n"
            "  Add to .env: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx"
        )
        sys.exit(1)

    leads = load_leads()
    if not leads:
        log.info("No leads loaded.")
        return

    lead_emails = {l.get("email","").lower() for l in leads if l.get("email")}
    log.info(f"Watching for replies from {len(lead_emails)} leads...")

    try:
        mail = connect_gmail()
    except Exception as e:
        log.error(f"Gmail connection failed: {e}")
        sys.exit(1)

    try:
        replies = fetch_unread_replies(mail, lead_emails)
    finally:
        mail.logout()

    log.info(f"Found {len(replies)} new replies from known leads")

    if not replies:
        log.info("Inbox clear. Done.")
        return

    now_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    leads_updated = False

    for r in replies:
        intent = classify_reply(r["body"])
        lead   = find_lead_by_email(leads, r["sender_email"])

        log.info(
            f"  {r['sender_name']} <{r['sender_email']}> → {intent.upper()}\n"
            f"    Subject: {r['subject']}\n"
            f"    Preview: {r['body'][:100].replace(chr(10),' ')}"
        )

        if not lead:
            log.warning(f"  Lead not found for {r['sender_email']} — saving anyway")

        # Unsubscribe gets an instant canned reply — everything else gets flagged
        # for Claude Code to draft interactively (free, no API cost)
        if intent == "unsubscribe":
            first      = (lead.get("name","").split()[0] if lead else "") or "there"
            draft_body = (f"Hi {first},\n\nAbsolutely — removing you now. "
                          f"Sorry for the interruption.\n\n"
                          f"— Ty\nViral Lense Media\nhello@vlmcreateflow.com")
            status = "pending_review"
        else:
            draft_body = ""   # Claude Code drafts this in session via Gmail MCP
            status = "needs_draft"

        draft = {
            "timestamp":     now_str,
            "lead_id":       lead.get("id") if lead else None,
            "lead_name":     r["sender_name"] or (lead.get("name") if lead else ""),
            "lead_email":    r["sender_email"],
            "company":       lead.get("company", "") if lead else "",
            "vertical":      lead.get("vertical", "") if lead else "",
            "niche":         lead.get("niche", "") if lead else "",
            "intent":        intent,
            "their_subject": r["subject"],
            "their_body":    r["body"],
            "draft_reply":   draft_body,
            "status":        status,
        }

        if not args.dry_run:
            ts_slug    = datetime.now().strftime("%Y%m%d%H%M%S")
            draft_path = DRAFTS_DIR / f"{(lead.get('id','unknown') if lead else 'unknown')}_{ts_slug}.json"
            with open(draft_path, "w") as f:
                json.dump(draft, f, indent=2)
            log.info(f"  Saved: {draft_path.name}")

            if lead:
                lead["status"]  = STATUS_MAP.get(intent, "replied_other")
                lead["replied"] = True
                leads_updated   = True
        else:
            log.info(f"  [DRY RUN] Would save draft, intent={intent}")

    if leads_updated and not args.dry_run:
        save_leads(leads)

    # Print summary so it's visible in cron log
    interested = sum(1 for r in replies if classify_reply(r["body"]) == "interested")
    log.info(
        f"\nSummary: {len(replies)} replies | "
        f"{interested} interested | "
        f"Drafts in .tmp/reply_drafts/ — open Claude Code to draft responses"
    )


if __name__ == "__main__":
    main()
