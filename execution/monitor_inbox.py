#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
monitor_inbox.py — Monitor virallensemediavlm@gmail.com for replies to outreach.

For each reply from a known lead:
  1. Classify intent: interested / not_now / objection / unsubscribe / other
  2. Draft a reply using Claude
  3. Save draft to .tmp/reply_drafts/{lead_id}_{ts}.json
  4. Update lead status in .tmp/leads.json
  5. Log everything to .tmp/inbox_monitor.log

Usage:
    python3 execution/monitor_inbox.py [--dry-run]

Requirements in .env:
    GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx   (Google Account > Security > App Passwords)
    ANTHROPIC_API_KEY=sk-ant-...

Cron (run after outreach sender, same time):
    5 3 * * * python3 execution/monitor_inbox.py
"""

import os, sys, json, imaplib, email, argparse, logging
from email.header import decode_header
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR    = Path(__file__).resolve().parent.parent
TMP_DIR     = BASE_DIR / ".tmp"
DRAFTS_DIR  = TMP_DIR / "reply_drafts"
LEADS_FILE  = TMP_DIR / "leads.json"
LOG_FILE    = TMP_DIR / "inbox_monitor.log"

TMP_DIR.mkdir(exist_ok=True)
DRAFTS_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
GMAIL_USER     = "virallensemediavlm@gmail.com"
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")   # App Password, not account password
ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "")

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

BOOKING_LINK = "b2b.vlmcreateflow.com"
FROM_NAME    = "Ty | Viral Lense Media"
FROM_EMAIL   = "hello@vlmcreateflow.com"

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
    sender_email = sender_email.lower().strip()
    return next((l for l in leads if l.get("email","").lower() == sender_email), None)


# ── Gmail IMAP ────────────────────────────────────────────────────────────────
def connect_gmail() -> imaplib.IMAP4_SSL:
    if not GMAIL_PASSWORD:
        raise RuntimeError(
            "GMAIL_APP_PASSWORD not set in .env.\n"
            "Go to myaccount.google.com > Security > 2-Step Verification > App Passwords\n"
            "Generate one for 'Mail' and add: GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx"
        )
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(GMAIL_USER, GMAIL_PASSWORD)
    return mail


def decode_str(value: str | bytes) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value or ""


def parse_sender(from_header: str) -> tuple[str, str]:
    """Return (name, email) from a From: header."""
    import re
    m = re.search(r"<([^>]+)>", from_header)
    if m:
        addr = m.group(1).strip()
        name = from_header[:m.start()].strip().strip('"').strip("'")
    else:
        addr = from_header.strip()
        name = ""
    return name, addr


def get_text_body(msg: email.message.Message) -> str:
    """Extract plain-text body from an email.Message object."""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                charset = part.get_content_charset() or "utf-8"
                body += part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        body = msg.get_payload(decode=True).decode(charset, errors="replace")
    return body.strip()


def fetch_unread_replies(mail: imaplib.IMAP4_SSL, lead_emails: set) -> list:
    """
    Fetch unread messages in INBOX where the sender is a known lead.
    Returns list of dicts: {uid, sender_name, sender_email, subject, body, date}
    """
    mail.select("INBOX")
    _, data = mail.search(None, "UNSEEN")
    uids = data[0].split()
    replies = []

    for uid in uids:
        _, msg_data = mail.fetch(uid, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        from_raw = decode_str(msg.get("From", ""))
        sender_name, sender_email = parse_sender(from_raw)

        if sender_email.lower() not in lead_emails:
            # Not from a known lead — leave unread, skip
            mail.store(uid, "-FLAGS", "\\Seen")
            continue

        subject_parts = decode_header(msg.get("Subject", ""))
        subject = "".join(
            p.decode(enc or "utf-8") if isinstance(p, bytes) else p
            for p, enc in subject_parts
        )
        body = get_text_body(msg)
        date = msg.get("Date", "")

        replies.append({
            "uid":          uid.decode(),
            "sender_name":  sender_name,
            "sender_email": sender_email.lower(),
            "subject":      subject,
            "body":         body[:3000],   # cap at 3K chars for Claude
            "date":         date,
        })

    return replies


# ── Claude classification + drafting ─────────────────────────────────────────
def call_claude(prompt: str, model: str = "claude-haiku-4-5-20251001") -> str:
    if not ANTHROPIC_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set in .env.\n"
            "Get your key at console.anthropic.com and add: ANTHROPIC_API_KEY=sk-ant-..."
        )
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def classify_reply(body: str) -> str:
    """
    Returns one of: interested / not_now / objection / unsubscribe / other
    """
    prompt = f"""You are classifying a cold email reply for a B2B sales team.

Categories:
- interested: They want to learn more, book a call, ask questions, or express genuine interest
- not_now: They're not ready but not hostile — "maybe later", "reach out in Q3", "we're tied up"
- objection: They push back on price, question the value, express skepticism, ask to justify
- unsubscribe: They ask to be removed, say stop emailing, or are clearly not interested ever
- other: Unclear, out of office, accidental reply, not a real response

Reply email body:
\"\"\"
{body}
\"\"\"

Respond with ONLY the single category word. Nothing else."""

    result = call_claude(prompt)
    valid = {"interested", "not_now", "objection", "unsubscribe", "other"}
    return result.lower().strip() if result.lower().strip() in valid else "other"


def draft_reply(lead: dict, reply_body: str, intent: str) -> str:
    """Draft a response using Claude based on the intent."""

    context = {
        "interested": (
            "They're interested. Write a warm, short reply. Thank them briefly, then "
            f"give them the booking link: {BOOKING_LINK}. Mention it's a 30-minute setup call "
            "and there's a one-time setup fee before the monthly retainer. Keep it under 80 words. "
            "Do not oversell — they're already leaning in."
        ),
        "not_now": (
            "They're open but not ready right now. Write a graceful, no-pressure reply. "
            "Acknowledge their timing, leave the door open, and let them know we'll check back in. "
            "Under 60 words. No pushy close."
        ),
        "objection": (
            "They have an objection or concern. Write a calm, confident rebuttal. "
            "Don't be defensive. Address the concern directly, bring it back to the value, "
            f"and offer to talk through it on a quick call: {BOOKING_LINK}. Under 100 words."
        ),
        "unsubscribe": (
            "They want to unsubscribe or stop receiving emails. Write a short, gracious reply "
            "acknowledging their request. No pitch. Just respectful and brief. Under 30 words."
        ),
        "other": (
            "The reply is unclear. Write a friendly, short response acknowledging their message "
            "and asking a simple clarifying question. Under 50 words."
        ),
    }

    instruction = context.get(intent, context["other"])

    prompt = f"""You are drafting a reply email on behalf of Ty at Viral Lense Media (VLM).

VLM sells AI content creation for agencies, financial advisors, and coaches/consultants.
Products: done-for-you AI content systems. Pricing: $1,500–$3,000/mo + one-time setup fee.
Booking link: {BOOKING_LINK}

Lead: {lead.get('name','there')} at {lead.get('company','their company')} ({lead.get('niche','')})
Their reply:
\"\"\"
{reply_body}
\"\"\"

Task: {instruction}

Write ONLY the email body. No subject line. Start with "Hi {{first_name}}," or similar.
Sign off as: "— Ty\\nViral Lense Media\\nhello@vlmcreateflow.com"
"""

    return call_claude(prompt, model="claude-sonnet-4-6")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Fetch and classify but don't mark emails as read or save drafts")
    args = parser.parse_args()

    log.info("=== VLM Inbox Monitor ===")

    if not GMAIL_PASSWORD:
        log.error("GMAIL_APP_PASSWORD not set. Add it to .env and re-run.")
        log.error("  myaccount.google.com > Security > 2-Step Verification > App Passwords")
        sys.exit(1)

    if not ANTHROPIC_KEY:
        log.error("ANTHROPIC_API_KEY not set. Add it to .env and re-run.")
        log.error("  console.anthropic.com > API Keys")
        sys.exit(1)

    leads = load_leads()
    if not leads:
        log.info("No leads loaded. Nothing to monitor.")
        return

    lead_emails = {l.get("email","").lower() for l in leads if l.get("email")}
    log.info(f"Monitoring inbox for replies from {len(lead_emails)} known leads...")

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
        log.info(f"\nProcessing: {r['sender_name']} <{r['sender_email']}>")
        log.info(f"  Subject: {r['subject']}")
        log.info(f"  Body preview: {r['body'][:120].replace(chr(10),' ')}...")

        # Classify
        intent = classify_reply(r["body"])
        log.info(f"  Intent: {intent.upper()}")

        # Find lead
        lead = find_lead_by_email(leads, r["sender_email"])
        if not lead:
            log.warning(f"  Lead not found for {r['sender_email']} — skipping")
            continue

        # Draft reply
        if intent == "unsubscribe":
            draft_body = f"Hi {lead.get('name','').split()[0] or 'there'},\n\nAbsolutely — removing you now. Sorry for the interruption.\n\n— Ty\nViral Lense Media\nhello@vlmcreateflow.com"
        else:
            try:
                draft_body = draft_reply(lead, r["body"], intent)
            except Exception as e:
                log.error(f"  Draft failed: {e}")
                draft_body = "[DRAFT FAILED — reply manually]"

        # Build draft object
        draft = {
            "timestamp":     now_str,
            "lead_id":       lead.get("id"),
            "lead_name":     lead.get("name"),
            "lead_email":    r["sender_email"],
            "company":       lead.get("company"),
            "vertical":      lead.get("vertical"),
            "intent":        intent,
            "their_subject": r["subject"],
            "their_body":    r["body"],
            "draft_reply":   draft_body,
            "status":        "pending_review",
        }

        # Save draft
        ts_slug = datetime.now().strftime("%Y%m%d%H%M%S")
        draft_path = DRAFTS_DIR / f"{lead.get('id','unknown')}_{ts_slug}.json"

        if not args.dry_run:
            with open(draft_path, "w") as f:
                json.dump(draft, f, indent=2)
            log.info(f"  Draft saved: {draft_path.name}")
        else:
            log.info(f"  [DRY RUN] Would save draft to {draft_path.name}")

        log.info(f"  Draft preview:\n    {draft_body[:200].replace(chr(10), chr(10)+'    ')}")

        # Update lead status
        if not args.dry_run:
            if intent == "interested":
                lead["status"]  = "replied_interested"
                lead["replied"] = True
            elif intent == "unsubscribe":
                lead["status"]  = "unsubscribed"
                lead["replied"] = True
            elif intent == "not_now":
                lead["status"]  = "replied_not_now"
                lead["replied"] = True
            elif intent == "objection":
                lead["status"]  = "replied_objection"
                lead["replied"] = True
            leads_updated = True

    if leads_updated and not args.dry_run:
        save_leads(leads)
        log.info("\nLeads updated.")

    log.info(f"\nDone. {len(replies)} replies processed. Drafts in .tmp/reply_drafts/")
    log.info("Review drafts and send manually, or run send_draft.py <draft_file>")


if __name__ == "__main__":
    main()
