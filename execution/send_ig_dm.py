"""
Instagram DM outreach script for local trade business leads.

Sends cold DMs via the VLM account (@virallensemediavlm) to handles sourced
from Google Maps prospecting. Tracks all sends in .tmp/ig_dm_log.json to
prevent duplicates across runs.

Usage:
    # Dry run — preview messages, no API calls
    python3.11 execution/send_ig_dm.py --dry-run --handles medina_roofing_co

    # Send to specific handles
    python3.11 execution/send_ig_dm.py --handles handle1 handle2 --max 10

    # Send from leads file
    python3.11 execution/send_ig_dm.py --from-file .tmp/ig_dm_leads.json

    # Custom message
    python3.11 execution/send_ig_dm.py --from-file .tmp/ig_dm_leads.json --message "Hey {name}! Custom message here."

Leads file format (.tmp/ig_dm_leads.json):
    [
      {"handle": "medina_roofing_co", "business_name": "Medina Brothers Roofing", "vertical": "roofing"},
      {"handle": "tx_dallas_electrics"}
    ]
    Plain string arrays also work: ["handle1", "handle2"]

IG safety: max 25 DMs/run (default), 45s ± 15s delay between sends.
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"
DM_LOG_FILE = TMP_DIR / "ig_dm_log.json"

load_dotenv(PROJECT_ROOT / ".env")

sys.path.insert(0, str(PROJECT_ROOT))
from execution.instagram_client import get_client

DEFAULT_MESSAGE = (
    "Hey{name_part}! Saw your{vertical_part} business on Google Maps — great reviews.\n\n"
    "We build professional websites for trade companies that actually bring in leads. "
    "Take a look at what we've done: instagram.com/virallensemediavlm\n\n"
    "Reply here if you want a free custom mockup built for your business."
)


def load_log() -> list:
    if DM_LOG_FILE.exists():
        with open(DM_LOG_FILE) as f:
            return json.load(f)
    return []


def save_log(log: list):
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    with open(DM_LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)


def already_sent(log: list, handle: str, account: str) -> bool:
    handle = handle.lstrip("@").lower()
    return any(
        e["handle"].lower() == handle and e["account"] == account and e["status"] == "sent"
        for e in log
    )


def build_message(template: str, business_name: str = "", vertical: str = "") -> str:
    name_part = f" {business_name}" if business_name else ""
    vertical_part = f" {vertical}" if vertical else ""
    return template.format(name_part=name_part, vertical_part=vertical_part)


def normalize_leads(raw) -> list[dict]:
    """Accept list of dicts or list of strings."""
    leads = []
    for item in raw:
        if isinstance(item, str):
            leads.append({"handle": item.lstrip("@")})
        elif isinstance(item, dict):
            item["handle"] = item["handle"].lstrip("@")
            leads.append(item)
    return leads


def load_leads_from_file(path: str) -> list[dict]:
    with open(path) as f:
        raw = json.load(f)
    return normalize_leads(raw)


def run(args):
    # Build lead list
    leads = []
    if args.from_file:
        leads = load_leads_from_file(args.from_file)
        print(f"Loaded {len(leads)} leads from {args.from_file}")
    if args.handles:
        leads += normalize_leads(args.handles)

    if not leads:
        print("No leads provided. Use --handles or --from-file.")
        sys.exit(1)

    log = load_log()
    sent_count = 0
    skipped_count = 0
    failed_count = 0

    if args.dry_run:
        print("\n[DRY RUN] No DMs will be sent.\n")

    cl = None
    if not args.dry_run:
        print(f"Authenticating as '{args.account}'...")
        cl = get_client(account=args.account)
        print(f"Authenticated.\n")

    for lead in leads:
        handle = lead.get("handle", "").strip()
        if not handle:
            continue

        business_name = lead.get("business_name", "")
        vertical = lead.get("vertical", "")

        if already_sent(log, handle, args.account):
            print(f"[SKIP] @{handle} — already sent")
            skipped_count += 1
            continue

        if sent_count >= args.max:
            print(f"\nReached --max {args.max} limit. Stopping.")
            break

        message = build_message(
            args.message or DEFAULT_MESSAGE,
            business_name=business_name,
            vertical=vertical,
        )

        if args.dry_run:
            print(f"[DRY RUN] → @{handle}")
            print(f"  Message:\n{message}\n")
            sent_count += 1
            continue

        try:
            user_id = cl.user_id_from_username(handle)
            cl.direct_send(message, [user_id])
            log.append({
                "handle": handle,
                "business_name": business_name,
                "vertical": vertical,
                "sent_at": datetime.now().isoformat(timespec="seconds"),
                "status": "sent",
                "account": args.account,
            })
            save_log(log)
            print(f"[SENT] @{handle}" + (f" ({business_name})" if business_name else ""))
            sent_count += 1

            # Jittered delay — avoids bot-pattern detection
            sleep_secs = args.delay + random.randint(-15, 15)
            sleep_secs = max(10, sleep_secs)
            print(f"  Waiting {sleep_secs}s...")
            time.sleep(sleep_secs)

        except Exception as e:
            log.append({
                "handle": handle,
                "business_name": business_name,
                "sent_at": datetime.now().isoformat(timespec="seconds"),
                "status": "failed",
                "error": str(e),
                "account": args.account,
            })
            save_log(log)
            print(f"[FAIL] @{handle} — {e}")
            failed_count += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done — sent: {sent_count} | skipped: {skipped_count} | failed: {failed_count}")
    if not args.dry_run:
        print(f"Log: {DM_LOG_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Send Instagram DMs to local trade leads via VLM account.")
    parser.add_argument("--handles", nargs="+", metavar="HANDLE", help="Instagram handles to DM")
    parser.add_argument("--from-file", metavar="PATH", help="JSON file of leads (array of handles or lead objects)")
    parser.add_argument("--account", default="vlm", help="IG account to send from (default: vlm)")
    parser.add_argument("--max", type=int, default=25, help="Max DMs per run (default: 25)")
    parser.add_argument("--delay", type=int, default=45, help="Seconds between DMs, ±15s jitter (default: 45)")
    parser.add_argument("--message", help="Override default message template. Use {name_part} and {vertical_part} placeholders.")
    parser.add_argument("--dry-run", action="store_true", help="Preview messages without sending")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
