#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
send_draft.py — Review and send a reply draft from .tmp/reply_drafts/.

Usage:
    python3 execution/send_draft.py                    # list all pending drafts
    python3 execution/send_draft.py <draft_file.json>  # send a specific draft
    python3 execution/send_draft.py --all              # send all pending drafts

The draft body is shown before sending. Press Enter to confirm or Ctrl+C to abort.
"""

import os, sys, json, smtplib, argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR   = Path(__file__).resolve().parent.parent
DRAFTS_DIR = BASE_DIR / ".tmp" / "reply_drafts"

load_dotenv(BASE_DIR / ".env")

SMTP_HOST = "mail.privateemail.com"
SMTP_PORT = 587
SMTP_USER = "hello@vlmcreateflow.com"
SMTP_PASS = "Vlmcreateflow1!"
FROM_ADDR = "hello@vlmcreateflow.com"
FROM_NAME = "Ty | Viral Lense Media"


def list_pending():
    drafts = sorted(DRAFTS_DIR.glob("*.json"))
    pending = []
    for d in drafts:
        with open(d) as f:
            obj = json.load(f)
        if obj.get("status") == "pending_review":
            pending.append((d, obj))
    return pending


def send_reply(draft_path: Path, draft: dict, auto: bool = False) -> bool:
    to_addr  = draft["lead_email"]
    subject  = f"Re: {draft['their_subject']}"
    body     = draft["draft_reply"]
    name     = draft.get("lead_name", "")
    company  = draft.get("company", "")
    intent   = draft.get("intent", "")

    print(f"\n{'='*60}")
    print(f"TO:      {name} <{to_addr}>  [{company}]")
    print(f"INTENT:  {intent.upper()}")
    print(f"SUBJECT: {subject}")
    print(f"{'─'*60}")
    print(body)
    print(f"{'='*60}")

    if not auto:
        try:
            confirm = input("\nSend this? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            return False
        if confirm != "y":
            print("Skipped.")
            return False

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
        print(f"Sent to {to_addr}")
    except Exception as e:
        print(f"SMTP ERROR: {e}")
        return False

    # Mark draft as sent
    draft["status"]    = "sent"
    draft["sent_at"]   = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    with open(draft_path, "w") as f:
        json.dump(draft, f, indent=2)

    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("draft_file", nargs="?", help="Specific draft JSON file to send")
    parser.add_argument("--all", action="store_true", help="Send all pending drafts (with confirmation per draft)")
    parser.add_argument("--auto", action="store_true", help="Skip confirmation prompts (use carefully)")
    args = parser.parse_args()

    if args.draft_file:
        p = Path(args.draft_file)
        if not p.is_absolute():
            p = DRAFTS_DIR / p
        if not p.exists():
            print(f"File not found: {p}")
            sys.exit(1)
        with open(p) as f:
            draft = json.load(f)
        send_reply(p, draft, auto=args.auto)
        return

    pending = list_pending()

    if not pending:
        print("No pending drafts. Inbox is clear.")
        return

    print(f"\n{len(pending)} pending draft(s):\n")
    for i, (path, obj) in enumerate(pending, 1):
        print(f"  {i}. {obj.get('lead_name','?')} <{obj.get('lead_email','?')}> "
              f"[{obj.get('intent','?').upper()}] — {path.name}")

    if not args.all:
        print("\nRun with --all to send all, or pass a filename to send one.")
        return

    sent = 0
    for path, draft in pending:
        if send_reply(path, draft, auto=args.auto):
            sent += 1

    print(f"\nDone. {sent}/{len(pending)} drafts sent.")


if __name__ == "__main__":
    main()
