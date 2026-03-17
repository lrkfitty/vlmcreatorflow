import os, json
from datetime import datetime

SHEET_NAME = "CreateFlow CRM"
LOCAL_FILE  = os.path.join(os.path.dirname(__file__), "..", "leads_local.json")
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
HEADERS = [
    "id","timestamp","funnel_type","name","email","company","role",
    "niche","budget","challenge","content_type","frequency","team_size",
    "how_heard","status","notes","drip_day"
]


def _client():
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        # Streamlit Cloud: full JSON stored as env var / secret
        creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON", "")
        if creds_json:
            info = json.loads(creds_json)
            creds = Credentials.from_service_account_info(info, scopes=SCOPES)
        else:
            # Local: path to credentials file
            p = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
            if not os.path.exists(p):
                return None
            creds = Credentials.from_service_account_file(p, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception:
        return None


def _sheet():
    c = _client()
    if not c:
        return None
    try:
        return c.open(SHEET_NAME).sheet1
    except Exception:
        return None


def get_all_leads() -> list:
    s = _sheet()
    if s:
        try:
            return s.get_all_records()
        except Exception:
            pass
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE) as f:
        return json.load(f)


def update_lead(lead_id: str, status: str, notes: str):
    s = _sheet()
    if s:
        try:
            records = s.get_all_records()
            for i, r in enumerate(records):
                if r.get("id") == lead_id:
                    s.update_cell(i + 2, HEADERS.index("status") + 1, status)
                    s.update_cell(i + 2, HEADERS.index("notes") + 1, notes)
                    return
        except Exception:
            pass
    if not os.path.exists(LOCAL_FILE):
        return
    with open(LOCAL_FILE) as f:
        leads = json.load(f)
    for lead in leads:
        if lead.get("id") == lead_id:
            lead["status"] = status
            lead["notes"] = notes
    with open(LOCAL_FILE, "w") as f:
        json.dump(leads, f, indent=2)
