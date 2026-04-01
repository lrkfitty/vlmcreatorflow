import os, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

NOTIFY        = "tylarkin@vlmcreateflow.com"
NOTIFY_GMAIL  = "virallensemediavlm@gmail.com"
USER          = os.getenv("SMTP_USER", "noreply@vlmcreateflow.com")
PASS          = os.getenv("SMTP_PASS", "PLACEHOLDER")
HELLO_USER    = "hello@vlmcreateflow.com"
HELLO_PASS    = os.getenv("SMTP_HELLO_PASS", "Vlmcreateflow1!")


def _send_from(subject: str, body: str, to: str, from_user: str, from_pass: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = from_user
    msg["To"]      = to
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("mail.privateemail.com", 587) as s:
            s.starttls(); s.login(from_user, from_pass); s.sendmail(from_user, to, msg.as_string())
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


def _send(subject: str, body: str, to: str):
    if PASS == "PLACEHOLDER":
        print(f"[EMAIL PLACEHOLDER] To: {to} | {subject}")
        return
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = USER
    msg["To"]      = to
    msg.attach(MIMEText(body, "plain"))
    try:
        with smtplib.SMTP("mail.privateemail.com", 587) as s:
            s.starttls(); s.login(USER, PASS); s.sendmail(USER, to, msg.as_string())
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


def send_lead_notification(lead: dict):
    body = f"""New B2B Lead — CreateFlow Enterprise

Name:      {lead.get('name')}
Company:   {lead.get('company')}
Role:      {lead.get('role')}
Email:     {lead.get('email')}
Niche:     {lead.get('niche')}
Budget:    {lead.get('budget')}
Challenge: {lead.get('challenge')}
Team Size: {lead.get('team_size')}
Lead ID:   {lead.get('id')}
"""
    subject = f"New B2B Lead — {lead.get('name')} @ {lead.get('company')}"
    _send(subject, body, NOTIFY)
    _send(subject, body, NOTIFY_GMAIL)


def send_booking_notification(booking: dict):
    body = f"""New Setup Call Booking — VLM

Name:        {booking.get('name')}
Email:       {booking.get('email')}
Company:     {booking.get('company')}
Availability:{booking.get('availability')}
Message:     {booking.get('message')}
"""
    subject = f"Setup Call Request — {booking.get('name')} @ {booking.get('company')}"
    _send(subject, body, NOTIFY_GMAIL)
    _send(subject, body, NOTIFY)


def send_booking_confirmation(booking: dict):
    name = booking.get('name', '').split()[0] or booking.get('name', 'there')
    body = f"""Hey {name},

Got your request — you're on the list.

I'll reach out within 24 hours to confirm a time that works for your setup call.

On the call we'll:
- Walk through the system live
- Scope your first use case
- Map your onboarding from day one

If you have anything you want me to look at before we talk — your current content setup, past campaigns, your positioning — feel free to reply and send it over.

Talk soon.

— Ty
Viral Lense Media
hello@vlmcreateflow.com
"""
    subject = "Your VLM setup call request — confirmed"
    _send_from(subject, body, booking.get('email'), HELLO_USER, HELLO_PASS)
