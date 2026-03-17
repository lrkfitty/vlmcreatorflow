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

st.set_page_config(page_title="CreateFlow Enterprise", page_icon="✦", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 3.5rem; max-width: 820px; }

.eyebrow {
    font-size: 0.85rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #10B981; margin-bottom: 16px;
}
h1 {
    font-family: 'Playfair Display', serif;
    color: #F8FAFC; font-size: 3.4rem; line-height: 1.12; font-weight: 700; margin-bottom: 22px;
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
    border-left: 3px solid #10B981; padding: 20px 28px;
    background: #0a1a12; border-radius: 0 10px 10px 0; margin: 32px 0;
}
.pain-numbers { display: flex; gap: 14px; margin: 24px 0; }
.pain-card {
    background: #0f0f1a; border: 1px solid #1e1e2e;
    border-radius: 12px; padding: 26px 16px; flex: 1; text-align: center;
}
.pain-num { color: #F87171; font-size: 2rem; font-weight: 800; }
.pain-label { color: #475569; font-size: 0.88rem; margin-top: 8px; line-height: 1.4; }

.niche-card {
    background: #0f0f1a; border: 1px solid #1e2d3d;
    border-radius: 14px; padding: 28px 22px; margin-bottom: 4px;
    height: 100%;
}
.niche-card-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #10B981; margin-bottom: 10px;
}
.niche-card-title { color: #E2E8F0; font-size: 1.05rem; font-weight: 700; margin-bottom: 8px; }
.niche-card-escape { color: #94A3B8; font-size: 0.88rem; line-height: 1.6; margin-bottom: 12px; }
.niche-card-arrival {
    color: #34D399; font-size: 0.88rem; line-height: 1.6;
    border-top: 1px solid #1a3028; padding-top: 12px; margin-top: 4px;
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
.check { color: #10B981; font-weight: 700; flex-shrink: 0; margin-top: 2px; font-size: 1.1rem; }
.value-title { color: #E2E8F0; font-weight: 700; font-size: 1.05rem; }
.value-desc { color: #64748B; font-size: 0.95rem; line-height: 1.65; margin-top: 4px; }

.roi-block {
    background: #0a1a12; border: 1px solid #1a3028;
    border-radius: 12px; padding: 28px; margin: 24px 0;
}
.roi-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 12px 0; border-bottom: 1px solid #0d2018; font-size: 1rem;
}
.roi-row:last-child { border-bottom: none; }
.roi-label { color: #64748B; }
.roi-old { color: #F87171; font-weight: 700; }
.roi-new { color: #34D399; font-weight: 700; }

.price-block {
    background: #0a0f1a; border: 1px solid #1e2d3d;
    border-radius: 14px; padding: 40px; margin: 24px 0;
}
.price-main { font-size: 3.8rem; font-weight: 800; color: #F8FAFC; line-height: 1; }
.price-period { font-size: 1.2rem; color: #475569; font-weight: 400; }
.price-note { color: #475569; font-size: 0.95rem; margin-top: 12px; }

.guarantee {
    background: #0a1a10; border: 1px solid #1a3020;
    border-radius: 10px; padding: 22px 26px; margin: 20px 0;
    color: #6EE7B7; font-size: 1rem; line-height: 1.7;
}
.divider { border: none; border-top: 1px solid #1a1a2e; margin: 40px 0; }

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
    width: 100%; background: #059669; color: white; border: none;
    border-radius: 10px; padding: 18px; font-size: 1.1rem; font-weight: 700;
    font-family: 'Inter', sans-serif;
}
.stButton > button:hover { background: #047857; border: none; }
.secure { text-align: center; color: #2d3748; font-size: 0.82rem; margin-top: 12px; }
</style>
""", unsafe_allow_html=True)

if "submitted" not in st.session_state: st.session_state.submitted = False
if "lead"      not in st.session_state: st.session_state.lead      = {}

# ─── SALES LETTER ────────────────────────────────────────────────────────────
if not st.session_state.submitted:

    st.markdown('<div class="eyebrow">CreateFlow — Enterprise</div>', unsafe_allow_html=True)
    st.markdown("# Your last photo shoot cost how much — and you got one campaign out of it.")
    st.markdown('<p class="lede">There\'s nothing wrong with your team. The production process is the problem. It was never designed for the volume modern marketing actually demands — and you\'re absorbing that cost every month.</p>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## What it actually costs to run visual production the old way.")
    st.markdown("""
You book the studio. Brief the photographer. Cast the talent, coordinate wardrobe, schedule the shoot,
wait two weeks for edited deliverables — and what you get back is enough for one campaign.

Then the client asks for a variation. A different mood. Three more formats for paid media.
And the whole machine spins up again.
    """)
    st.markdown("""
<div class="pain-numbers">
  <div class="pain-card"><div class="pain-num">$8k–$15k</div><div class="pain-label">Average cost per commercial shoot</div></div>
  <div class="pain-card"><div class="pain-num">2–3 weeks</div><div class="pain-label">Turnaround before assets are usable</div></div>
  <div class="pain-card"><div class="pain-num">1 campaign</div><div class="pain-label">What you walk away with after all of that</div></div>
</div>
""", unsafe_allow_html=True)
    st.markdown('<div class="pull-quote">"The agencies scaling fastest right now aren\'t working harder.<br>They\'ve removed the production bottleneck entirely."</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## Build a visual production asset your team owns permanently.")
    st.markdown("""
CreateFlow Enterprise gives your team a private, blank-canvas studio. You upload your brand's reference
assets — your talent, your spaces, your products — and the platform locks them in.

From that point, your team generates campaign-ready visuals from a desk. Same faces. Same environments.
Same brand integrity. In minutes, not weeks. No shoot coordination. No model fees. No two-week waits.
    """)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">How it works across industries</div>', unsafe_allow_html=True)

    niches_data = [
        ("niche_agency.jpg",    "Ad Agencies",        "Burning budget on studios and talent for every new client campaign.",                          "Generate 50 ad creative variations before lunch. Own the digital talent permanently."),
        ("niche_finance.jpg",   "Finance & Wealth",   "Compliance-safe lifestyle shots are expensive and hard to source without stock photo risks.",   "Generate bespoke advisors in high-end offices — brand-owned, compliant, photorealistic."),
        ("niche_realestate.jpg","Real Estate",         "Staging lifestyle scenes with actors for every luxury listing isn't scalable.",                 "Digitally place aspirational characters into any property. Sell the lifestyle instantly."),
        ("niche_ecommerce.jpg", "E-Commerce & Fashion","$20k+ per seasonal lookbook to book models, locations, and photographers.",                    "Build your brand's own digital models. Generate a full lookbook in an afternoon."),
        ("niche_healthcare.jpg","Healthcare",          "Stock photos of 'smiling doctors' destroy credibility. Real clinic shoots are a privacy risk.", "Render bespoke medical professionals in modern clinical environments. Private. Compliant."),
        ("niche_fitness.jpg",   "Fitness & Wellness",  "App visual content goes stale fast. You need massive volume across diverse talent.",            "Build a roster of brand ambassadors. Generate them in any gym, any workout, any apparel."),
    ]

    for i in range(0, len(niches_data), 2):
        col_a, col_b = st.columns(2)
        for col, idx in [(col_a, i), (col_b, i+1)]:
            if idx < len(niches_data):
                img_file, title, escape, arrival = niches_data[idx]
                img_path = ASSETS / img_file
                with col:
                    if img_path.exists():
                        st.image(str(img_path), width=500)
                    st.markdown(f"""
                    <div class="niche-card">
                        <div class="niche-card-label">{title}</div>
                        <div class="niche-card-escape">The problem: {escape}</div>
                        <div class="niche-card-arrival">With CreateFlow: {arrival}</div>
                    </div>
                    """, unsafe_allow_html=True)
        st.markdown("&nbsp;")

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Everything included in CreateFlow Enterprise</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="value-stack">
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Private Blank-Canvas Dashboard</div>
    <div class="value-desc">No shared libraries, no generic presets. Your account starts empty — you build it with your own brand assets.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Proprietary Talent Roster</div>
    <div class="value-desc">Upload reference images of your talent or executives. Lock in their likeness and generate them across any scene, forever.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Brand Environment Library</div>
    <div class="value-desc">Your office. Your retail space. Your aesthetic. Locked in and reusable across every campaign your team runs.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Multi-Shot Campaign Generation</div>
    <div class="value-desc">One scene brief produces wide, medium, and close-up coverage. Full campaign assets in a single session.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Secure Enterprise Asset Vault</div>
    <div class="value-desc">S3-backed cloud storage for all generated assets. Organized and accessible to your whole team.</div>
  </div></div>
  <div class="value-item"><div class="check">&#10003;</div><div>
    <div class="value-title">Priority Onboarding Session</div>
    <div class="value-desc">A dedicated call to get your first brand asset locked in and your team generating on day one.</div>
  </div></div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## The math is straightforward.")
    st.markdown("""
<div class="roi-block">
  <div class="roi-row"><span class="roi-label">Single commercial shoot (studio + talent + post)</span><span class="roi-old">$8,000–$15,000</span></div>
  <div class="roi-row"><span class="roi-label">Turnaround time</span><span class="roi-old">2–3 weeks</span></div>
  <div class="roi-row"><span class="roi-label">Campaigns produced per shoot</span><span class="roi-old">1</span></div>
  <div class="roi-row"><span class="roi-label">CreateFlow Enterprise — unlimited generations</span><span class="roi-new">$997/mo</span></div>
  <div class="roi-row"><span class="roi-label">Turnaround time</span><span class="roi-new">Same session</span></div>
  <div class="roi-row"><span class="roi-label">Campaigns produced per month</span><span class="roi-new">Unlimited</span></div>
</div>
""", unsafe_allow_html=True)
    st.markdown("One shoot pays for nearly a year of CreateFlow Enterprise. Most teams recoup the cost in the first campaign they don't have to book a studio for.")
    st.markdown('<div class="guarantee">If your team doesn\'t produce campaign-ready assets in your first session, we\'ll work with you personally until you do — or refund your first month. No debate.</div>', unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("## Tell us about your team.")
    st.markdown("<p style='color:#64748B;font-size:0.93rem;margin-top:-8px;'>A few quick questions. No pitch — just making sure CreateFlow is the right fit and we set it up properly for how your team works.</p>", unsafe_allow_html=True)

    with st.form("b2b_form"):
        c1, c2 = st.columns(2)
        with c1: name    = st.text_input("Your Name")
        with c2: email   = st.text_input("Work Email")
        c3, c4 = st.columns(2)
        with c3: company = st.text_input("Company Name")
        with c4: role    = st.selectbox("Your Role", ["— Select —","Founder / CEO","Creative Director","Marketing Manager","Brand Manager","Head of Content","Other"])
        niche     = st.selectbox("Your industry", ["— Select —","Marketing / Advertising Agency","Finance & Wealth Management","Real Estate","E-Commerce / Fashion","Healthcare & Medical","Fitness & Wellness","Business Consulting / Coaching","Other"])
        budget    = st.selectbox("Monthly visual content spend", ["— Select —","Under $2,000","$2,000–$5,000","$5,000–$10,000","$10,000–$25,000","$25,000+"])
        team_size = st.selectbox("Team size", ["— Select —","Just me","2–10","11–50","51–200","200+"])
        challenge = st.selectbox("Biggest bottleneck in your visual production?", ["— Select —","Cost — shoots and agencies eat the budget","Speed — turnaround is too slow","Consistency — brand visuals drift campaign to campaign","Scale — can't produce enough creative to test","Talent access — hard to find and book the right people","Other"])

        if st.form_submit_button("See the Enterprise Setup"):
            errs = []
            if not name.strip():          errs.append("Name required.")
            if "@" not in email:          errs.append("Valid work email required.")
            if not company.strip():       errs.append("Company name required.")
            if role    == "— Select —":   errs.append("Select your role.")
            if niche   == "— Select —":   errs.append("Select your industry.")
            if budget  == "— Select —":   errs.append("Select your monthly budget.")
            if challenge == "— Select —": errs.append("Select your main challenge.")
            if errs:
                for e in errs: st.error(e)
            else:
                lead = {"funnel_type":"B2B","name":name.strip(),"email":email.strip(),
                        "company":company.strip(),"role":role,"niche":niche,"budget":budget,
                        "challenge":challenge,"content_type":"","frequency":"",
                        "team_size":team_size,"how_heard":""}
                lead["id"] = add_lead(lead)
                send_lead_notification(lead)
                st.session_state.lead = lead
                st.session_state.submitted = True
                st.rerun()

# ─── CHECKOUT ────────────────────────────────────────────────────────────────
else:
    lead    = st.session_state.lead
    first   = lead.get("name","").split()[0]
    company = lead.get("company","your team")

    st.markdown('<div class="eyebrow">You\'re almost in</div>', unsafe_allow_html=True)
    st.markdown(f"# Here's your Enterprise setup, {first}.")
    st.markdown(f'<p class="lede">Everything below is included from day one. We\'ll reach out to schedule your onboarding call so {company} is generating on the first day.</p>', unsafe_allow_html=True)

    st.markdown("""
<div class="value-stack">
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Private Blank-Canvas Dashboard</div><div class="value-desc">Your account. Your assets. Nothing shared.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Proprietary Talent & Environment Locking</div><div class="value-desc">Upload your references. Own them forever.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Unlimited Multi-Shot Campaign Generation</div><div class="value-desc">Full coverage. One session.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Secure Enterprise Asset Vault</div><div class="value-desc">Organized and accessible to your whole team.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Priority Onboarding Session</div><div class="value-desc">Live call to get your team generating on day one.</div></div></div>
  <div class="value-item"><div class="check">&#10003;</div><div><div class="value-title">Cancel Anytime</div><div class="value-desc">No contracts. No lock-in.</div></div></div>
</div>
<div class="price-block">
  <div class="price-main">$997 <span class="price-period">/ month</span></div>
  <div class="price-note">Includes onboarding session &nbsp;·&nbsp; Cancel anytime</div>
</div>
""", unsafe_allow_html=True)

    handle_stripe_button("Start CreateFlow Enterprise →", email=st.session_state.lead.get("email",""), company=st.session_state.lead.get("company",""))
    st.markdown('<p class="secure">Payments processed by Stripe. Onboarding call scheduled within 24 hours of signup.</p>', unsafe_allow_html=True)
    if st.button("← Back"): st.session_state.submitted = False; st.rerun()
