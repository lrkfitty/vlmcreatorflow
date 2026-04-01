import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

NOTIFY  = "tylarkin@vlmcreateflow.com"
USER    = os.getenv("SMTP_USER", "noreply@vlmcreateflow.com")
PASS    = os.getenv("SMTP_PASS", "PLACEHOLDER")

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
        with smtplib.SMTP("mail.privateemail.com", 587) as s:
            s.starttls(); s.login(USER, PASS); s.sendmail(USER, NOTIFY, msg.as_string())
    except Exception as e: print(f"[EMAIL ERROR] {e}")
