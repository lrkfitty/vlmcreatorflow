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
        try:
            s = c.create(SHEET_NAME).sheet1
            s.append_row(HEADERS)
            return s
        except Exception:
            return None


def add_lead(data: dict) -> str:
    lid = f"CF-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    row = {h: data.get(h, "") for h in HEADERS}
    row.update({"id": lid, "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                "status": "New", "notes": "", "drip_day": ""})
    s = _sheet()
    if s:
        s.append_row([row[h] for h in HEADERS])
    else:
        leads = _load()
        leads.append(row)
        with open(LOCAL_FILE, "w") as f:
            json.dump(leads, f, indent=2)
    _trigger_make_webhook(row)
    return lid


def _trigger_make_webhook(lead: dict):
    """POST to Make.com webhook so the B2B drip sequence starts."""
    url = os.getenv("MAKE_B2B_WEBHOOK_URL", "")
    if not url:
        return
    try:
        import requests
        requests.post(url, json=lead, timeout=5)
    except Exception:
        pass


def _load():
    if not os.path.exists(LOCAL_FILE):
        return []
    with open(LOCAL_FILE) as f:
        return json.load(f)
