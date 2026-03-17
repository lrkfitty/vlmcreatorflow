import streamlit as st
import os, sys, hashlib, io
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
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.sheets import get_all_leads, update_lead

st.set_page_config(page_title="VLM — CRM", page_icon="✦", layout="wide")

# ─── Auth helpers ─────────────────────────────────────────────────────────────
CRM_USER = os.getenv("CRM_USERNAME", "admin")
CRM_PASS = os.getenv("CRM_PASSWORD", "admin")

def _hash(s): return hashlib.sha256(s.encode()).hexdigest()
def _check(u, p): return u == CRM_USER and _hash(p) == _hash(CRM_PASS)

# ─── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.block-container { padding-top: 2rem; }

/* Login card */
.login-wrap {
    max-width: 400px; margin: 80px auto 0;
    background: #0f0f1a; border: 1px solid #1e1e2e;
    border-radius: 16px; padding: 40px;
}
.login-logo {
    text-align: center; margin-bottom: 28px;
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #4F46E5;
}
.login-title { color: #F8FAFC; font-size: 1.4rem; font-weight: 700; text-align: center; margin-bottom: 6px; }
.login-sub { color: #475569; font-size: 0.85rem; text-align: center; margin-bottom: 28px; }

/* Dashboard */
.metric-card {
    background: #0f0f1a; border: 1px solid #1e1e2e;
    border-radius: 12px; padding: 20px 22px; text-align: center;
}
.metric-num { color: #F8FAFC; font-size: 2rem; font-weight: 800; line-height: 1; }
.metric-label { color: #475569; font-size: 0.78rem; margin-top: 6px; letter-spacing: 0.04em; }
.metric-b2c { border-top: 3px solid #4F46E5; }
.metric-b2b { border-top: 3px solid #10B981; }
.metric-new { border-top: 3px solid #FBBF24; }
.metric-won { border-top: 3px solid #34D399; }

.section-label {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #334155; margin-bottom: 14px;
}
.divider { border: none; border-top: 1px solid #1a1a2e; margin: 28px 0; }

.stSelectbox > div > div {
    background: #13131f !important; border: 1px solid #252538 !important;
    color: #E2E8F0 !important; border-radius: 8px !important;
}
.stTextInput > div > input {
    background: #13131f !important; border: 1px solid #252538 !important;
    color: #E2E8F0 !important; border-radius: 8px !important; padding: 10px 14px !important;
}
.stTextArea > div > textarea {
    background: #13131f !important; border: 1px solid #252538 !important;
    color: #E2E8F0 !important; border-radius: 8px !important;
}
label { color: #64748B !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.03em !important; }
h1 { color: #F8FAFC; font-size: 1.6rem; font-weight: 800; }
h2, h3 { color: #E2E8F0; }

.stButton > button {
    background: #4F46E5; color: white; border: none;
    border-radius: 8px; padding: 9px 22px;
    font-size: 0.88rem; font-weight: 700; font-family: 'Inter', sans-serif;
}
.stButton > button:hover { background: #4338CA; border: none; }
.btn-logout > button { background: #1e1e2e !important; color: #64748B !important; }
.btn-logout > button:hover { background: #252538 !important; }

[data-testid="stDataFrame"] { border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

STAGES = ["New", "Contacted", "Demo Booked", "Closed Won", "Closed Lost"]

# ─── LOGIN GATE ───────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("""
    <div class="login-wrap">
      <div class="login-logo">Viral Lense Media</div>
      <div class="login-title">Staff Access</div>
      <div class="login-sub">CRM — CreateFlow</div>
    </div>
    """, unsafe_allow_html=True)

    # Center the form under the card
    _, col, _ = st.columns([1, 1.6, 1])
    with col:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In", use_container_width=True):
                if _check(username, password):
                    st.session_state.authenticated = True
                    st.session_state.staff_user     = username
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")
    st.stop()

# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_leads(): return get_all_leads()

# Header
hc1, hc2 = st.columns([6, 1])
with hc1:
    st.markdown("# Viral Lense Media — CRM")
    st.markdown(f"<p style='color:#334155;font-size:0.82rem;margin-top:-12px;'>Signed in as <b style='color:#64748B'>{st.session_state.get('staff_user','')}</b></p>", unsafe_allow_html=True)
with hc2:
    st.markdown('<div class="btn-logout">', unsafe_allow_html=True)
    if st.button("Sign Out"):
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

rc1, rc2 = st.columns([1, 1])
with rc1:
    if st.button("↻  Refresh"):
        st.cache_data.clear(); st.rerun()

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Load data
raw = load_leads()
if not raw:
    st.info("No leads yet. They'll appear here once someone submits a funnel.")
    st.stop()

df = pd.DataFrame(raw)
for col in ["id","timestamp","funnel_type","name","email","company","role","niche",
            "budget","challenge","team_size","status","notes"]:
    if col not in df.columns: df[col] = ""

# ─── METRICS ──────────────────────────────────────────────────────────────────
total    = len(df)
b2c      = len(df[df["funnel_type"]=="B2C"])
b2b      = len(df[df["funnel_type"]=="B2B"])
new_ct   = len(df[df["status"]=="New"])
won_ct   = len(df[df["status"]=="Closed Won"])

m1,m2,m3,m4,m5 = st.columns(5)
for col, num, label, cls in [
    (m1, total,  "Total Leads",    ""),
    (m2, b2c,    "B2C Creator",    "metric-b2c"),
    (m3, b2b,    "B2B Enterprise", "metric-b2b"),
    (m4, new_ct, "Uncontacted",    "metric-new"),
    (m5, won_ct, "Closed Won",     "metric-won"),
]:
    with col:
        st.markdown(f'<div class="metric-card {cls}"><div class="metric-num">{num}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── FILTERS ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Pipeline</div>', unsafe_allow_html=True)

fc1,fc2,fc3,fc4 = st.columns(4)
with fc1: f_type   = st.selectbox("Funnel",  ["All","B2C","B2B"])
with fc2: f_status = st.selectbox("Status",  ["All"]+STAGES)
with fc3:
    niches = ["All"] + sorted([n for n in df["niche"].dropna().unique() if n])
    f_niche = st.selectbox("Niche", niches)
with fc4: f_search = st.text_input("Search name / email / company")

fdf = df.copy()
if f_type   != "All": fdf = fdf[fdf["funnel_type"]==f_type]
if f_status != "All": fdf = fdf[fdf["status"]==f_status]
if f_niche  != "All": fdf = fdf[fdf["niche"]==f_niche]
if f_search.strip():
    q = f_search.strip().lower()
    fdf = fdf[fdf.apply(lambda r: q in str(r.get("name","")).lower()
                                  or q in str(r.get("email","")).lower()
                                  or q in str(r.get("company","")).lower(), axis=1)]

st.markdown(f"<p style='color:#334155;font-size:0.82rem;'>Showing {len(fdf)} of {total} leads</p>", unsafe_allow_html=True)

# ─── TABLE ────────────────────────────────────────────────────────────────────
show_cols = ["id","timestamp","funnel_type","name","email","company","niche","budget","challenge","status"]
avail = [c for c in show_cols if c in fdf.columns]

st.dataframe(
    fdf[avail].reset_index(drop=True),
    use_container_width=True, height=300,
    column_config={
        "id":          st.column_config.TextColumn("ID",       width="small"),
        "timestamp":   st.column_config.TextColumn("Date",     width="medium"),
        "funnel_type": st.column_config.TextColumn("Type",     width="small"),
        "name":        st.column_config.TextColumn("Name",     width="medium"),
        "email":       st.column_config.TextColumn("Email",    width="large"),
        "company":     st.column_config.TextColumn("Company",  width="medium"),
        "niche":       st.column_config.TextColumn("Niche",    width="medium"),
        "budget":      st.column_config.TextColumn("Budget",   width="medium"),
        "challenge":   st.column_config.TextColumn("Challenge",width="large"),
        "status":      st.column_config.TextColumn("Status",   width="medium"),
    }
)

buf = io.StringIO()
fdf[avail].to_csv(buf, index=False)
st.download_button("Export CSV", buf.getvalue(), "vlm_leads.csv", "text/csv")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── LEAD EDITOR ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Update Lead</div>', unsafe_allow_html=True)

if not fdf.empty and "id" in fdf.columns:
    options = fdf.apply(lambda r: f"{r.get('id','?')} — {r.get('name','?')} ({r.get('funnel_type','?')})", axis=1).tolist()
    sel     = st.selectbox("Select lead", options)
    sel_id  = sel.split(" — ")[0]
    row     = fdf[fdf["id"]==sel_id]

    if not row.empty:
        r = row.iloc[0]
        with st.expander("Lead Details", expanded=True):
            d1,d2 = st.columns(2)
            with d1:
                st.markdown(f"**Name:** {r.get('name','')}")
                st.markdown(f"**Email:** {r.get('email','')}")
                st.markdown(f"**Company:** {r.get('company','')}")
                st.markdown(f"**Role:** {r.get('role','')}")
            with d2:
                st.markdown(f"**Funnel:** {r.get('funnel_type','')}")
                st.markdown(f"**Niche:** {r.get('niche','')}")
                st.markdown(f"**Budget:** {r.get('budget','')}")
                st.markdown(f"**Submitted:** {r.get('timestamp','')}")
            st.markdown(f"**Challenge:** {r.get('challenge','')}")

        cur = r.get("status","New")
        if cur not in STAGES: cur = "New"
        new_status = st.selectbox("Pipeline Stage", STAGES, index=STAGES.index(cur))
        new_notes  = st.text_area("Notes", value=r.get("notes",""), height=100,
                                  placeholder="Next steps, call notes, context...")

        if st.button("Save Changes"):
            update_lead(sel_id, new_status, new_notes)
            st.cache_data.clear()
            st.success("Lead updated.")
            st.rerun()
else:
    st.info("No leads match the current filters.")

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# ─── STAGE BREAKDOWN ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Stage Breakdown</div>', unsafe_allow_html=True)
cols = st.columns(len(STAGES))
for i, stage in enumerate(STAGES):
    ct = len(df[df["status"]==stage])
    with cols[i]:
        st.markdown(f'<div class="metric-card"><div class="metric-num">{ct}</div><div class="metric-label">{stage}</div></div>', unsafe_allow_html=True)
