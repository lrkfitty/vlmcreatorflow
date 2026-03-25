#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
sync_crm.py — Sync outreach state from .tmp/leads.json → vlm-crm/leads_local.json
and push to GitHub so crm.vlmcreateflow.com reflects live pipeline data.

Run hourly via cron (after monitor_inbox.py).
"""

import json, subprocess, sys
from pathlib import Path

ROOT      = Path(__file__).parent.parent
LEADS     = ROOT / ".tmp" / "leads.json"
CRM_LEADS = ROOT / "vlm-crm" / "leads_local.json"
CRM_DIR   = ROOT / "vlm-crm"


def sync():
    if not LEADS.exists():
        print("[sync_crm] No leads.json found — skipping.")
        return

    with open(LEADS) as f:
        outreach = {l["id"]: l for l in json.load(f)}

    if not CRM_LEADS.exists():
        print("[sync_crm] No leads_local.json found — skipping.")
        return

    with open(CRM_LEADS) as f:
        crm = json.load(f)

    changed = 0
    for lead in crm:
        src = outreach.get(lead["id"], {})
        before = (lead.get("emails_sent"), lead.get("replied"), lead.get("booked"))
        lead["emails_sent"]  = src.get("emails_sent", lead.get("emails_sent", 0))
        lead["drip_day"]     = src.get("drip_day",    lead.get("drip_day", 0))
        lead["last_sent_at"] = src.get("last_sent_at", lead.get("last_sent_at", ""))
        lead["replied"]      = src.get("replied",  lead.get("replied", False))
        lead["booked"]       = src.get("booked",   lead.get("booked", False))
        lead["vertical"]     = src.get("vertical", lead.get("vertical", lead.get("niche", "")))
        after = (lead.get("emails_sent"), lead.get("replied"), lead.get("booked"))
        if before != after:
            changed += 1

    with open(CRM_LEADS, "w") as f:
        json.dump(crm, f, indent=2)

    print(f"[sync_crm] Synced {len(crm)} leads ({changed} changed).")

    if changed == 0:
        print("[sync_crm] No changes — skipping git push.")
        return

    # Commit and push
    result = subprocess.run(
        ["git", "add", "leads_local.json"],
        cwd=CRM_DIR, capture_output=True, text=True
    )
    result = subprocess.run(
        ["git", "commit", "-m", f"sync: outreach state update ({changed} leads changed)"],
        cwd=CRM_DIR, capture_output=True, text=True
    )
    if "nothing to commit" in result.stdout:
        print("[sync_crm] Nothing to commit.")
        return

    result = subprocess.run(
        ["git", "push"],
        cwd=CRM_DIR, capture_output=True, text=True
    )
    if result.returncode == 0:
        print("[sync_crm] Pushed to GitHub — CRM will update shortly.")
    else:
        print(f"[sync_crm] Push failed: {result.stderr}")


if __name__ == "__main__":
    sync()
