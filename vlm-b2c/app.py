import streamlit as st
import os, sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
# Streamlit Cloud: bridge st.secrets → os.environ so all getenv() calls work
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.sheets import add_lead
from utils.mailer import send_lead_notification
from utils.stripe_checkout import handle_stripe_button

ASSETS = Path(__file__).parent / "assets"

st.set_page_config(page_title="CreateFlow Creator", page_icon="✦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

html, body, [class*="css"], p, li, span, div { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 3.5rem; max-width: 820px; }

.eyebrow {
    font-size: 0.85rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #6366F1; margin-bottom: 16px;
}
h1 {
    font-family: 'Playfair Display', serif;
    color: #F8FAFC; font-size: 3.4rem; line-height: 1.12;
    font-weight: 700; margin-bottom: 22px;
}
h2 {
    font-family: 'Playfair Display', serif;
    color: #E2E8F0; font-size: 2.2rem; line-height: 1.2; font-weight: 700;
}
p, li { color: #94A3B8; font-size: 1.15rem; line-height: 1.85; }
.lede { font-size: 1.3rem; color: #94A3B8; line-height: 1.85; margin-bottom: 28px; }

.pull-quote {
    font-family: 'Playfair Display', serif; font-style: italic;
    font-size: 1.4rem; color: #E2E8F0; line-height: 1.6;
    border-left: 3px solid #4F46E5; padding: 20px 28px;
    background: #0f0f1a; border-radius: 0 10px 10px 0; margin: 32px 0;
}
.section-label {
    font-size: 0.85rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #334155; margin-bottom: 18px;
}
.value-stack {
    background: #0d1117; border: 1px solid #1e2d3d;
    border-radius: 14px; padding: 36px; margin: 24px 0;
}
.value-item {
    display: flex; gap: 16px; align-items: flex-start;
    margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #0f172a;
}
.value-item:last-child { border-bottom: none; margin-bottom: 0; padding-bottom: 0; }
.check { color: #4F46E5; font-weight: 700; flex-shrink: 0; margin-top: 2px; font-size: 1.1rem; }
.value-title { color: #E2E8F0; font-weight: 700; font-size: 1.05rem; }
.value-desc { color: #64748B; font-size: 0.95rem; line-height: 1.65; margin-top: 4px; }

.price-block {
    background: #0a0f1a; border: 1px solid #1e2d3d;
    border-radius: 14px; padding: 40px; margin: 24px 0;
}
.price-cross { color: #334155; font-size: 0.95rem; text-decoration: line-through; margin-bottom: 6px; }
.price-main { font-size: 3.8rem; font-weight: 800; color: #F8FAFC; line-height: 1; }
.price-period { font-size: 1.2rem; color: #475569; font-weight: 400; }
.price-note { color: #475569; font-size: 0.95rem; margin-top: 12px; }

.guarantee {
    background: #0a1a10; border: 1px solid #1a3020;
    border-radius: 10px; padding: 22px 26px; margin: 20px 0;
    color: #6EE7B7; font-size: 1rem; line-height: 1.7;
}
.divider { border: none; border-top: 1px solid #1a1a2e; margin: 40px 0; }

/* Form */
.stTextInput > div > input {
    background: #13131f !important; border: 1px solid #252538 !important;
    color: #E2E8F0 !important; border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important; font-size: 1rem !important; padding: 13px 16px !important;
}
.stSelectbox > div > div {
    background: #13131f !important; border: 1px solid #252538 !important;
    color: #E2E8F0 !important; border-radius: 8px !important; font-size: 1rem !important;
}
label { color: #64748B !important; font-size: 0.9rem !important; font-weight: 600 !important; letter-spacing: 0.02em !important; }
.stButton > button {
    width: 100%; background: #4F46E5; color: white; border: none;
    border-radius: 10px; padding: 18px; font-size: 1.1rem; font-weight: 700;
    font-family: 'Inter', sans-serif; letter-spacing: 0.02em;
}
.stButton > button:hover { background: #4338CA; border: none; }
.secure { text-align: center; color: #2d3748; font-size: 0.82rem; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

if "submitted" not in st.session_state: st.session_state.submitted = False
if "lead"      not in st.session_state: st.session_state.lead      = {}

# ─── SALES LETTER ────────────────────────────────────────────────────────────
if not st.session_state.submitted:

    st.markdown('<div class="eyebrow">CreateFlow — Creator Plan</div>', unsafe_allow_html=True)
    st.markdown("# The consistent visual brand you've been trying to build — without starting over every time.")
    st.markdown('<p class="lede">If you\'ve ever spent an afternoon trying to get an AI character to look anything like the one you made yesterday — you already know the problem. And you know how much time it eats.</p>', unsafe_allow_html=True)

    # ── HERO SHOWCASE ────────────────────────────────────────────
    st.markdown("""
    <div style="background:#0d1117;border:1px solid #1e2d3d;border-radius:14px;padding:24px 24px 16px;margin:0 0 8px;">
      <p style="font-size:0.7rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#334155;margin-bottom:16px;">
        Same character. 4 completely different worlds.
      </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.image(str(ASSETS / "shay_pool_tracksuit.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Poolside — Athletic</p>", unsafe_allow_html=True)
    with c2:
        st.image(str(ASSETS / "shay_boat.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Ocean — Luxury</p>", unsafe_allow_html=True)

    c3, c4 = st.columns(2)
    with c3:
        st.image(str(ASSETS / "shay_redcarpet.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Red Carpet — Glam</p>", unsafe_allow_html=True)
    with c4:
        st.image(str(ASSETS / "shay_villa.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Villa — Brand Collab</p>", unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center;font-size:0.82rem;color:#475569;margin:12px 0 32px;'>
        One Brand Ambassador. Unlimited scenes. Generated with CreateFlow.
    </p>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## Here's the thing nobody says out loud about AI image tools.")
    st.markdown("""
Most were built for one-off generations. Type a prompt, get an image, move on.

That works fine if you need a single piece of art. It falls apart completely when you're a creator who needs the
**same character, same world, same brand feel** — repeated across dozens of pieces of content every week.

Every session starts from scratch. Every result drifts slightly. By the time you get close to what you wanted,
you've burned the one resource you don't have: time.
    """)

    st.markdown("""
<div class="pull-quote">
"You're not slow because you're inefficient.<br>You're slow because the tool was never built for what you're actually trying to do."
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## CreateFlow works differently.")
    st.markdown("""
Instead of a blank prompt every time, you build your creative world once — and generate from it indefinitely.

Lock in a character. Lock in an environment. Lock in a wardrobe. Then produce as many scenes, angles,
and variations as your content calendar demands. Same face. Same vibe. Same brand. Every time.

No prompting from scratch. No inconsistency. No rabbit holes.
    """)

    # ── MID-PAGE PROOF ───────────────────────────────────────────
    c5, c6 = st.columns(2)
    with c5:
        st.image(str(ASSETS / "shay_dive.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Action — Same character, different moment</p>", unsafe_allow_html=True)
    with c6:
        st.image(str(ASSETS / "shay_market.jpg"), use_container_width=True)
        st.markdown("<p style='text-align:center;font-size:0.75rem;color:#334155;margin-top:4px;'>Street — Same character, different world</p>", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Everything included in the Creator Plan</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="value-stack">
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Locked Character Studio</div>
    <div class="value-desc">Build a Brand Ambassador once — face, hair, skin tone, body type. Generate them across any scene forever, without re-prompting.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Pre-Built Environment Library</div>
    <div class="value-desc">Offices, studios, streets, lifestyle settings — ready to drop your character into. No world-building required.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Dynamic Wardrobe Sets</div>
    <div class="value-desc">Swap your character's outfit without touching their face. Business, casual, branded — all pre-mapped and reusable.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Multi-Shot Batch Generation</div>
    <div class="value-desc">One scene brief. Wide shots, medium shots, close-ups — back in a single run. Full coverage without repeating yourself.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Cloud Asset Gallery</div>
    <div class="value-desc">Every image you've ever generated — organized, searchable, downloadable in one click. Nothing gets lost.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Cancel Anytime</div>
    <div class="value-desc">No contracts. No lock-in. Cancel in two clicks.</div>
  </div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## What it costs — and why it's an easy call.")
    st.markdown("""
Most creators are spending $80–$150 a month across Midjourney, Runway, stock subscriptions, and other tools —
and still not getting consistency. CreateFlow replaces all of it.
    """)
    st.markdown("""
<div class="price-block">
  <div class="price-cross">$80–$150+/mo across multiple tools</div>
  <div class="price-main">$49 <span class="price-period">/ month</span></div>
  <div class="price-note">Unlimited generations &nbsp;·&nbsp; Cancel anytime &nbsp;·&nbsp; No contracts</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div class="guarantee">If CreateFlow doesn\'t save you meaningful time in your first 14 days, reach out and we\'ll make it right — or refund your first month. No questions.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## One quick step before you start.")
    st.markdown("<p style='color:#64748B; font-size:0.93rem; margin-top:-8px;'>Takes 60 seconds. Helps us make sure CreateFlow is set up right for how you work.</p>", unsafe_allow_html=True)

    with st.form("b2c_form"):
        c1, c2 = st.columns(2)
        with c1: name  = st.text_input("Your Name")
        with c2: email = st.text_input("Email Address")
        content_type = st.selectbox("What type of content do you mainly create?", ["— Select —","Social Media Content","YouTube / Video","Brand Photography","E-commerce / Product","Marketing Campaigns","Coaching / Course Content","Other"])
        frequency    = st.selectbox("How often do you need new visuals?", ["— Select —","Daily","A few times a week","Weekly","A few times a month"])
        challenge    = st.selectbox("What slows you down most right now?", ["— Select —","Getting consistent characters across generations","Prompting takes too long with inconsistent results","Tools are too complex","Content looks generic","Cost of existing tools","Other"])
        how_heard    = st.selectbox("How did you find CreateFlow?", ["— Select —","Social Media","Referral","Search","Skool / Community","Other"])

        if st.form_submit_button("Get My Creator Plan"):
            errs = []
            if not name.strip():             errs.append("Name is required.")
            if "@" not in email:             errs.append("Valid email required.")
            if content_type == "— Select —": errs.append("Select your content type.")
            if frequency    == "— Select —": errs.append("Select how often you need visuals.")
            if challenge    == "— Select —": errs.append("Select your main challenge.")
            if errs:
                for e in errs: st.error(e)
            else:
                lead = {"funnel_type":"B2C","name":name.strip(),"email":email.strip(),
                        "company":"","role":"","niche":"","budget":"",
                        "challenge":challenge,"content_type":content_type,
                        "frequency":frequency,"team_size":"","how_heard":how_heard}
                lead["id"] = add_lead(lead)
                send_lead_notification(lead)
                st.session_state.lead = lead
                st.session_state.submitted = True
                st.rerun()

# ─── CHECKOUT ────────────────────────────────────────────────────────────────
else:
    first = st.session_state.lead.get("name","").split()[0]
    st.markdown('<div class="eyebrow">You\'re almost in</div>', unsafe_allow_html=True)
    st.markdown(f"# Welcome, {first}.")
    st.markdown('<p class="lede">Here\'s everything included in your Creator plan. One step left.</p>', unsafe_allow_html=True)

    st.markdown("""
<div class="value-stack">
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Locked Character Studio</div><div class="value-desc">Build once. Generate forever.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Environment & Wardrobe Library</div><div class="value-desc">Hundreds of settings and outfits, ready to use.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Multi-Shot Batch Generation</div><div class="value-desc">Full scene coverage from a single prompt.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Cloud Asset Gallery</div><div class="value-desc">Everything organized and downloadable.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Cancel Anytime</div><div class="value-desc">No contracts.</div></div></div>
</div>
<div class="price-block">
  <div class="price-main">$49 <span class="price-period">/ month</span></div>
  <div class="price-note">Secured by Stripe &nbsp;·&nbsp; Cancel anytime</div>
</div>
""", unsafe_allow_html=True)

    handle_stripe_button("Start My CreateFlow Creator Plan →", email=st.session_state.lead.get("email",""))
    st.markdown('<p class="secure">Payments processed by Stripe. We never store your card details.</p>', unsafe_allow_html=True)
    if st.button("← Back"): st.session_state.submitted = False; st.rerun()
