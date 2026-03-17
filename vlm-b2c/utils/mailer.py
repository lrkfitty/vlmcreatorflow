import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

NOTIFY  = "virallensemediavlm@gmail.com"
USER    = os.getenv("GMAIL_USER", "virallensemediavlm@gmail.com")
PASS    = os.getenv("GMAIL_APP_PASSWORD", "PLACEHOLDER")

def send_lead_notification(lead: dict):
    if PASS == "PLACEHOLDER":
        print(f"[EMAIL PLACEHOLDER] {lead.get('funnel_type')} lead: {lead.get('name')} <{lead.get('email')}>")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"New B2C Lead — {lead.get('name')}"
    msg["From"] = USER; msg["To"] = NOTIFY
    body = f"""New B2C lead — CreateFlow Creator

Name:      {lead.get('name')}
Email:     {lead.get('email')}
Content:   {lead.get('content_type')}
Challenge: {lead.get('challenge')}
Frequency: {lead.get('frequency')}
Lead ID:   {lead.get('id')}
"""
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
            s.login(USER, PASS); s.sendmail(USER, NOTIFY, msg.as_string())
    except Exception as e: print(f"[EMAIL ERROR] {e}")
