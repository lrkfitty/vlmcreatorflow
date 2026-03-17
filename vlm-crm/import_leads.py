"""
import_leads.py — One-time script to bulk-import a CSV of leads into the CRM.

Usage:
    python3 import_leads.py path/to/leads.csv

The CSV must have at minimum an "email" column.
Any columns matching CRM headers are imported; missing columns default to "".
Existing leads with the same email are skipped (no duplicates).
"""
from __future__ import annotations
import sys, os, csv, json
from pathlib import Path
from datetime import datetime

# Load env so Google creds / GOOGLE_CREDENTIALS_JSON are available
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")

sys.path.insert(0, str(Path(__file__).parent))
from utils.sheets import _sheet, _load, HEADERS, LOCAL_FILE, SHEET_NAME

CSV_HEADERS_MAP = {
    # CSV column name → CRM header (add more mappings if your CSV uses different names)
    "first_name": "name", "full_name": "name", "contact_name": "name",
    "company_name": "company", "organization": "company",
    "job_title": "role", "title": "role",
    "industry": "niche", "vertical": "niche",
}


def normalise_row(raw: dict) -> dict:
    """Map CSV columns → CRM headers, fill defaults."""
    row: dict = {h: "" for h in HEADERS}
    for k, v in raw.items():
        key = k.strip().lower().replace(" ", "_")
        mapped = CSV_HEADERS_MAP.get(key, key)
        if mapped in HEADERS:
            row[mapped] = v.strip() if v else ""
    # Defaults
    row["funnel_type"] = row.get("funnel_type") or "B2B"
    row["status"]      = row.get("status") or "New"
    row["drip_day"]    = ""
    row["notes"]       = ""
    row["id"]          = f"CF-IMP-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    row["timestamp"]   = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return row


def existing_emails(sheet) -> set:
    if sheet:
        try:
            return {r.get("email", "").lower() for r in sheet.get_all_records()}
        except Exception:
            pass
    if os.path.exists(LOCAL_FILE):
        with open(LOCAL_FILE) as f:
            return {r.get("email", "").lower() for r in json.load(f)}
    return set()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 import_leads.py path/to/leads.csv")
        sys.exit(1)

    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    sheet = _sheet()
    if sheet:
        print(f"Connected to Google Sheet: {SHEET_NAME}")
    else:
        print(f"Google Sheets not connected — importing to local {LOCAL_FILE}")

    seen = existing_emails(sheet)
    rows_to_add = []

    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            row = normalise_row(raw)
            email = row.get("email", "").lower()
            if not email:
                continue
            if email in seen:
                print(f"  SKIP (duplicate): {email}")
                continue
            rows_to_add.append(row)
            seen.add(email)

    if not rows_to_add:
        print("No new leads to import.")
        return

    if sheet:
        for row in rows_to_add:
            sheet.append_row([row[h] for h in HEADERS])
            print(f"  ADDED to Sheet: {row['email']}")
    else:
        leads = []
        if os.path.exists(LOCAL_FILE):
            with open(LOCAL_FILE) as f:
                leads = json.load(f)
        leads.extend(rows_to_add)
        with open(LOCAL_FILE, "w") as f:
            json.dump(leads, f, indent=2)
        for row in rows_to_add:
            print(f"  ADDED to local JSON: {row['email']}")

    print(f"\nDone. {len(rows_to_add)} leads imported.")


if __name__ == "__main__":
    main()
