# Outreach Automation — Directive

## Goal
Fully autonomous B2B cold outreach for VLM. Only Ty touches the sales call.

## Pipeline Overview

```
Explorium API → .tmp/leads.json → send_outreach.py → SMTP → reply/click → book call
                                       ↓
                               vlm-crm/leads_local.json (CRM)
```

## Step 1: Source Leads

Script: `execution/source_leads.py`

```bash
python3 execution/source_leads.py
```

Pulls 10 leads per vertical (30 total) from Explorium API:
- Ad Agencies: NAICS 541810/541830/541840, founder/owner/cxo, 1-50 employees, US
- Financial Advisors: NAICS 523930/523120/523110, founder/owner/partner, 1-50 employees, US
- Coaches/Consultants: NAICS 541611-541613/611430, founder/owner/cxo, 1-50 employees, US

Auth: `api_key` header. API: `POST https://api.explorium.ai/v1/prospects`
Email enrichment: `POST https://api.explorium.ai/v1/prospects/contacts_information/bulk_enrich`
Response: emails nested under `item["data"]["professions_email"]`

**Credit note:** 100 API credits available. Each fetch batch of 10 costs ~10 credits.
When credits run out: export leads from app.vibeprospecting.ai (chat credits) as CSV,
then run `python3 vlm-crm/import_leads.py path/to/leads.csv`

## Step 2: Push to CRM

Run this after sourcing leads:
```bash
python3 -c "
import json
from pathlib import Path
# [see inline push logic in main project context or re-run the push_crm block]
"
```

Or use the import script with a CSV export:
```bash
python3 vlm-crm/import_leads.py .tmp/leads.csv
```

CRM lives at crm.vlmcreateflow.com. Backed by Google Sheets (prod) or
`vlm-crm/leads_local.json` (fallback). Commit leads_local.json and push to
lrkfitty/vlm-crm to update the deployed CRM.

## Step 3: Email Sequences

Templates: `execution/email_templates/`

| File | Vertical | Day |
|------|----------|-----|
| agency_email_1.txt | Ad Agency | 0 |
| agency_email_2.txt | Ad Agency | 3 |
| agency_email_3.txt | Ad Agency | 7 |
| financial_email_1.txt | Financial Advisor | 0 |
| financial_email_2.txt | Financial Advisor | 3 |
| financial_email_3.txt | Financial Advisor | 7 |
| coaching_email_1.txt | Coach / Consultant | 0 |
| coaching_email_2.txt | Coach / Consultant | 3 |
| coaching_email_3.txt | Coach / Consultant | 7 |

Pricing anchor: $1,500-$3,000/mo. Never mention $997.
CTA: b2b.vlmcreateflow.com
From: hello@vlmcreateflow.com

## Step 4: Automated Sender

Script: `execution/send_outreach.py`
Cron: `0 9 * * *` (9:00 AM Bangkok time)
Log: `.tmp/outreach_cron.log`
Full log: `.tmp/outreach_log.json`

```bash
# Manual test
python3 execution/send_outreach.py --dry-run

# Fire immediately (no dry run)
python3 execution/send_outreach.py
```

SMTP: mail.privateemail.com:587, user=hello@vlmcreateflow.com

Sequence logic:
- emails_sent=0 → send email 1 immediately
- emails_sent=1 → send email 2 after 3 days from last_sent_at
- emails_sent=2 → send email 3 after 4 more days (day 7 total)
- emails_sent=3 → sequence complete, no more sends
- If lead.replied=True or lead.booked=True → skip

## Step 5: Appointment Setting

When a lead replies or books, update leads.json:
```json
{ "replied": true, "booked": true, "status": "booked" }
```

Email 3 in all sequences contains a direct CTA: b2b.vlmcreateflow.com
Build a Calendly link or booking flow on the B2B landing page for Ty's calls.

## Month 1 Target
- 50 outreaches sent
- 2-3 booked calls
- Anchor all conversations at $1,500-$3,000/mo

## Edge Cases Learned
- Explorium enrichment response nests data: `item["data"]["professions_email"]` not `item["professions_email"]`
- has_email filter on /prospects doesn't guarantee enrichment success — always enrich separately
- 100 API credits run out fast (30 fetches ≈ 30+ credits). Use chat credits at app.vibeprospecting.ai for larger pulls
