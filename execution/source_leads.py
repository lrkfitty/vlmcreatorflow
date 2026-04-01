#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
source_leads.py — Pull leads from Explorium API across 3 verticals.

Verticals:
  - ad_agency        : Boutique US ad agencies, 1-50 employees, founder/owner/CEO
  - financial_advisor: RIAs / wealth management, 1-50 employees, US
  - coach_consultant : Business coaches & consultants, US

Usage:
    python3 execution/source_leads.py [--dry-run]
    python3 execution/source_leads.py --from-csv <path>   # import leads from CSV via vlm-crm/import_leads.py

Outputs:
    .tmp/leads.json  — full lead list (new leads appended, no duplicates by email)
"""

import os, sys, json, time, argparse, requests, subprocess
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TMP_DIR  = BASE_DIR / ".tmp"
TMP_DIR.mkdir(exist_ok=True)
LEADS_FILE = TMP_DIR / "leads.json"

EXPLORIUM_API_KEY = "6547e4ec-8cfa-4a94-a205-b47593591d50"
BASE_URL = "https://api.explorium.ai/v1"
HEADERS  = {
    "api_key": EXPLORIUM_API_KEY,
    "Content-Type": "application/json",
}

# ── Vertical configs ──────────────────────────────────────────────────────────
VERTICALS = {
    "ad_agency": {
        "label": "Ad Agency",
        "filters": {
            "has_email": {"value": True},
            "job_level": {"values": ["founder", "owner", "cxo", "president"]},
            "country_code": {"values": ["US"]},
            "company_size": {"values": ["1-10", "11-50"]},
            "naics_category": {"values": ["541810", "541830", "541840", "541820"]},
        },
        "target": 10,
    },
    "financial_advisor": {
        "label": "Financial Advisor",
        "filters": {
            "has_email": {"value": True},
            "job_level": {"values": ["founder", "owner", "cxo", "president", "partner"]},
            "country_code": {"values": ["US"]},
            "company_size": {"values": ["1-10", "11-50"]},
            "naics_category": {"values": ["523930", "523120", "523110"]},
        },
        "target": 10,
    },
    "coach_consultant": {
        "label": "Coach / Consultant",
        "filters": {
            "has_email": {"value": True},
            "job_level": {"values": ["founder", "owner", "cxo", "president"]},
            "country_code": {"values": ["US"]},
            "company_size": {"values": ["1-10", "11-50"]},
            "naics_category": {"values": ["541611", "541612", "541613", "611430"]},
        },
        "target": 10,
    },
}


# ── API helpers ───────────────────────────────────────────────────────────────
def fetch_prospects(config: dict) -> list:
    """Fetch prospect basic data for one vertical. Returns list of dicts."""
    payload = {
        "mode": "full",
        "size": config["target"],
        "page_size": config["target"],
        "page": 1,
        "filters": config["filters"],
    }
    resp = requests.post(f"{BASE_URL}/prospects", headers=HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    prospects = data.get("data", [])
    print(f"    API returned {len(prospects)} / {data.get('total_results', '?')} available")
    return prospects


def enrich_emails(prospect_ids: list) -> dict:
    """Bulk-enrich prospect IDs for contact info. Returns {prospect_id: {email, status}}."""
    result = {}
    for i in range(0, len(prospect_ids), 50):
        chunk = prospect_ids[i:i+50]
        resp = requests.post(
            f"{BASE_URL}/prospects/contacts_information/bulk_enrich",
            headers=HEADERS,
            json={"prospect_ids": chunk},
            timeout=30,
        )
        resp.raise_for_status()
        for item in resp.json().get("data", []):
            pid  = item.get("prospect_id", "")
            # Response nests contact data under item["data"]
            info = item.get("data") or item
            email = (info.get("professions_email")
                     or info.get("professional_email")
                     or "")
            if pid and email:
                result[pid] = {
                    "email":        email,
                    "email_status": info.get("professional_email_status", ""),
                }
        time.sleep(0.5)
    return result


# ── Lead builder ──────────────────────────────────────────────────────────────
def build_lead(raw: dict, vertical: str, label: str, email_map: dict) -> dict:
    pid   = raw.get("prospect_id", "")
    edata = email_map.get(pid, {})
    ts    = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "id":            f"VP-{vertical[:3].upper()}-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "timestamp":     ts,
        "funnel_type":   "B2B",
        "name":          raw.get("full_name", "").strip(),
        "email":         edata.get("email", ""),
        "email_status":  edata.get("email_status", ""),
        "company":       raw.get("company_name", "").strip(),
        "role":          raw.get("job_title", "").strip(),
        "niche":         label,
        "vertical":      vertical,
        "country":       raw.get("country_name", ""),
        "prospect_id":   pid,
        "status":        "new",
        "drip_day":      0,       # which email in sequence to send next (0, 3, 7)
        "last_sent_at":  None,
        "emails_sent":   0,
        "replied":       False,
        "booked":        False,
        "notes":         "",
    }


def load_existing_emails() -> set:
    if not LEADS_FILE.exists():
        return set()
    with open(LEADS_FILE) as f:
        return {l.get("email", "").lower() for l in json.load(f) if l.get("email")}


def load_existing_leads() -> list:
    if not LEADS_FILE.exists():
        return []
    with open(LEADS_FILE) as f:
        return json.load(f)


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would happen without calling the API")
    parser.add_argument("--from-csv", metavar="PATH",
                        help="Import leads from a CSV file via vlm-crm/import_leads.py (skips Explorium API)")
    args = parser.parse_args()

    # ── CSV import mode ───────────────────────────────────────────────────────
    if args.from_csv:
        csv_path = Path(args.from_csv)
        if not csv_path.exists():
            print(f"ERROR: CSV file not found: {csv_path}")
            sys.exit(1)
        import_script = BASE_DIR / "vlm-crm" / "import_leads.py"
        if not import_script.exists():
            print(f"ERROR: import script not found: {import_script}")
            sys.exit(1)
        print(f"=== VLM Lead Import — CSV ===\n", flush=True)
        print(f"Delegating to {import_script} with {csv_path}\n", flush=True)
        result = subprocess.run(
            [sys.executable, str(import_script), str(csv_path)],
            cwd=str(BASE_DIR),
        )
        sys.exit(result.returncode)

    print("=== VLM Lead Sourcing — Explorium API ===\n")

    existing_emails = load_existing_emails()
    existing_leads  = load_existing_leads()
    new_leads       = []

    for vertical, config in VERTICALS.items():
        print(f"[{config['label']}] fetching {config['target']} prospects...")

        if args.dry_run:
            print("  DRY RUN — skipping API call\n")
            continue

        try:
            prospects = fetch_prospects(config)
        except requests.HTTPError as e:
            print(f"  ERROR fetching: {e.response.status_code} {e.response.text[:200]}\n")
            continue
        except Exception as e:
            print(f"  ERROR: {e}\n")
            continue

        ids = [p["prospect_id"] for p in prospects if p.get("prospect_id")]
        print(f"    Enriching {len(ids)} prospects for emails...")

        try:
            email_map = enrich_emails(ids)
            print(f"    Got {len(email_map)} verified emails")
        except Exception as e:
            print(f"    WARNING: email enrichment failed ({e}), continuing without emails")
            email_map = {}

        added = 0
        for p in prospects:
            lead  = build_lead(p, vertical, config["label"], email_map)
            email = lead["email"].lower()
            if email and email in existing_emails:
                print(f"    SKIP duplicate: {email}")
                continue
            new_leads.append(lead)
            if email:
                existing_emails.add(email)
            added += 1

        print(f"    {added} new leads added.\n")
        time.sleep(1)

    if not args.dry_run:
        all_leads = existing_leads + new_leads
        with open(LEADS_FILE, "w") as f:
            json.dump(all_leads, f, indent=2)
        with_email = [l for l in all_leads if l.get("email")]
        print(f"Saved {len(all_leads)} total leads to {LEADS_FILE}")
        print(f"  {len(with_email)} have verified emails — ready for outreach")
    else:
        print("DRY RUN complete. No files written.")


if __name__ == "__main__":
    main()
