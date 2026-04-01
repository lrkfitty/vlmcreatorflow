import streamlit as st
import os, sys, hashlib, io, json, time
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env")
try:
    for _k, _v in st.secrets.items():
        if isinstance(_v, str):
            os.environ.setdefault(_k, _v)
except Exception:
    pass
import pandas as pd
import plotly.graph_objects as go
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.sheets import get_all_leads, update_lead

LEADS_LOCAL = Path(__file__).parent / "leads_local.json"
STAGES      = ["New", "Contacted", "Demo Booked", "Closed Won", "Closed Lost"]
CRM_USER    = os.getenv("CRM_USERNAME", "admin")
CRM_PASS    = os.getenv("CRM_PASSWORD", "admin")
SESSION_TTL = 86400  # 24 hours in seconds

def _hash(s): return hashlib.sha256(s.encode()).hexdigest()
def _check(u, p): return u == CRM_USER and _hash(p) == _hash(CRM_PASS)
def _make_token(u): return _hash(u + CRM_PASS + str(int(time.time() // SESSION_TTL)))
def _valid_token(token, u):
    # Accept tokens from current and previous 24h window
    now = int(time.time() // SESSION_TTL)
    return token in (_hash(u + CRM_PASS + str(now)), _hash(u + CRM_PASS + str(now - 1)))

import extra_streamlit_components as stx

st.set_page_config(page_title="VLM Command Center", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #07070f; }
.block-container { padding: 1.5rem 2rem !important; max-width: 100% !important; }
[data-testid="stAppViewContainer"] { background: #07070f; }
[data-testid="stHeader"] { background: rgba(7,7,15,0.9) !important; backdrop-filter: blur(10px); }
[data-testid="stSidebar"] { display: none; }
section[data-testid="stSidebar"] { display: none; }

/* ── HEADER ── */
.cmd-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 28px; padding-bottom: 20px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.cmd-title {
    font-size: 1.1rem; font-weight: 900; letter-spacing: 0.08em;
    text-transform: uppercase; color: #ffffff;
    font-family: 'Space Mono', monospace;
}
.cmd-sub { font-size: 0.72rem; color: #2a2a4a; margin-top: 3px; letter-spacing: 0.05em; }

/* ── LIVE INDICATOR ── */
@keyframes pulse-ring { 0% { transform: scale(0.8); opacity: 0.8; } 100% { transform: scale(2.6); opacity: 0; } }
@keyframes pulse-dot  { 0%,100% { opacity: 1; } 50% { opacity: 0.5; } }
.live-wrap { display: flex; align-items: center; gap: 10px; }
.live-badge {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(0,255,136,0.06); border: 1px solid rgba(0,255,136,0.15);
    border-radius: 20px; padding: 5px 12px;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #00ff88;
}
.live-dot { position: relative; width: 7px; height: 7px; flex-shrink: 0; }
.live-dot::before {
    content: ''; position: absolute; inset: 0; border-radius: 50%;
    background: #00ff88; animation: pulse-dot 2s infinite;
}
.live-dot::after {
    content: ''; position: absolute; inset: 0; border-radius: 50%;
    background: #00ff88; opacity: 0.4; animation: pulse-ring 2s infinite;
}
.ts { font-size: 0.68rem; color: #2a2a4a; font-family: 'Space Mono', monospace; }

/* ── METRIC CARDS ── */
@keyframes count-glow { 0%,100% { text-shadow: 0 0 20px var(--c); } 50% { text-shadow: 0 0 40px var(--c), 0 0 60px var(--c); } }
.mc {
    background: #0d0d1c;
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px; padding: 22px 20px;
    position: relative; overflow: hidden; height: 100%;
}
.mc::before {
    content: ''; position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--accent, #00ff88);
    box-shadow: 0 0 16px var(--accent, #00ff88);
}
.mc-icon { font-size: 1.6rem; margin-bottom: 12px; opacity: 0.8; }
.mc-label {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: #6a6a9a; margin-bottom: 10px;
}
.mc-num {
    font-size: 3rem; font-weight: 900; line-height: 1;
    color: var(--accent, #ffffff);
    font-variant-numeric: tabular-nums;
}
.mc-sub { font-size: 0.82rem; color: #6a6a9a; margin-top: 8px; }
.mc-pill {
    display: inline-block; font-size: 0.72rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px; margin-top: 8px;
    background: rgba(0,255,136,0.08); color: #00ff88;
    border: 1px solid rgba(0,255,136,0.15);
}

/* ── SECTION HEADERS ── */
.sec {
    font-size: 0.78rem; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: #7a7aaa;
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 16px;
}
.sec::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.06); }

/* ── CHART CONTAINERS ── */
.chart-card {
    background: #0d0d1c; border: 1px solid rgba(255,255,255,0.05);
    border-radius: 14px; padding: 20px; height: 100%;
}
.chart-title {
    font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #3a3a5a; margin-bottom: 4px;
}

/* ── VERTICAL BARS ── */
.vb-row { display: flex; align-items: center; gap: 14px; margin-bottom: 18px; }
.vb-label { font-size: 0.88rem; color: #9a9abf; width: 160px; flex-shrink: 0; }
.vb-bg { flex: 1; height: 6px; background: rgba(255,255,255,0.06); border-radius: 3px; overflow: hidden; }
.vb-fill {
    height: 100%; border-radius: 3px;
    background: var(--c, #00ff88);
    box-shadow: 0 0 8px var(--c, #00ff88);
    transition: width 1s ease;
}
.vb-pct { font-size: 0.82rem; font-weight: 700; color: var(--c, #00ff88); width: 42px; text-align: right; }
.vb-ct  { font-size: 0.8rem; color: #5a5a8a; width: 26px; text-align: right; }

/* ── NEXT ACTION CARDS ── */
.na-card {
    background: #0a0a18; border: 1px solid rgba(255,255,255,0.05);
    border-radius: 10px; padding: 16px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 14px;
}
.na-icon { font-size: 1.1rem; flex-shrink: 0; }
.na-title { font-size: 0.9rem; font-weight: 700; color: #d8d8ff; }
.na-sub   { font-size: 0.8rem; color: #7a7aaa; margin-top: 3px; }
.na-badge {
    margin-left: auto; flex-shrink: 0;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.06em;
    padding: 3px 9px; border-radius: 20px;
}

/* ── DRIP TIMELINE ── */
.drip-row { display: flex; align-items: center; gap: 0; margin-bottom: 20px; }
.drip-step {
    flex: 1; text-align: center; position: relative;
}
.drip-step::after {
    content: ''; position: absolute;
    top: 14px; left: 50%; width: 100%; height: 2px;
    background: rgba(255,255,255,0.05);
}
.drip-step:last-child::after { display: none; }
.drip-dot {
    width: 28px; height: 28px; border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.08);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 0.65rem; font-weight: 700; color: #3a3a5a;
    background: #0a0a18; position: relative; z-index: 1;
    margin-bottom: 8px;
}
.drip-dot.sent {
    border-color: #00ff88; color: #00ff88;
    background: rgba(0,255,136,0.08);
    box-shadow: 0 0 12px rgba(0,255,136,0.3);
}
.drip-dot.next {
    border-color: #ffd700; color: #ffd700;
    background: rgba(255,215,0,0.06);
    box-shadow: 0 0 12px rgba(255,215,0,0.2);
    animation: pulse-dot 2s infinite;
}
.drip-label { font-size: 0.72rem; color: #6a6a9a; }
.drip-label.sent  { color: #00ff88; }
.drip-label.next  { color: #ffd700; }
.drip-day { font-size: 0.68rem; color: #5a5a7a; margin-top: 3px; }

/* ── STREAMLIT OVERRIDES ── */
.stTextInput > div > input {
    background: #0a0a18 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    color: #c0c0e0 !important; border-radius: 8px !important; padding: 12px 16px !important;
}
.stSelectbox > div > div {
    background: #0a0a18 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    color: #c0c0e0 !important; border-radius: 8px !important;
}
.stTextArea > div > textarea {
    background: #0a0a18 !important; border: 1px solid rgba(255,255,255,0.07) !important;
    color: #c0c0e0 !important; border-radius: 8px !important;
}
label { color: #3a3a5a !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.04em !important; }
.stButton > button {
    background: #00ff88 !important; color: #07070f !important; border: none !important;
    border-radius: 8px !important; font-weight: 800 !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover { background: #00e67a !important; }
.btn-ghost > button { background: rgba(255,255,255,0.04) !important; color: #4a4a6a !important; font-size: 0.8rem !important; }
h1,h2,h3 { color: #ffffff !important; }
[data-testid="stDataFrame"] { border-radius: 12px; }
.stExpander { border: 1px solid rgba(255,255,255,0.05) !important; border-radius: 12px !important; background: #0d0d1c !important; }
.divider { border: none; border-top: 1px solid rgba(255,255,255,0.04); margin: 24px 0; }

/* Login */
.login-card {
    max-width: 360px; margin: 120px auto 0;
    background: #0d0d1c; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 20px; padding: 44px 36px;
}
.login-logo {
    font-family: 'Space Mono', monospace; font-size: 0.65rem; font-weight: 700;
    letter-spacing: 0.2em; text-transform: uppercase;
    color: #00ff88; text-align: center; margin-bottom: 24px;
}
.login-title { color: #ffffff; font-size: 1.3rem; font-weight: 800; text-align: center; margin-bottom: 4px; }
.login-sub   { color: #2a2a4a; font-size: 0.82rem; text-align: center; margin-bottom: 28px; }
</style>
""", unsafe_allow_html=True)

# ── LOGIN ───────────────────────────────────────────────────────────────────
cookies = stx.CookieManager()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Auto-login from cookie
if not st.session_state.authenticated:
    saved_token = cookies.get("vlm_session")
    saved_user  = cookies.get("vlm_user") or CRM_USER
    if saved_token and _valid_token(saved_token, saved_user):
        st.session_state.authenticated = True
        st.session_state.staff_user    = saved_user

if not st.session_state.authenticated:
    st.markdown('<div class="login-card"><div class="login-logo">⚡ Viral Lense Media</div><div class="login-title">Command Center</div><div class="login-sub">Staff access only</div></div>', unsafe_allow_html=True)
    _, col, _ = st.columns([1, 1.4, 1])
    with col:
        with st.form("login"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Sign In →", use_container_width=True):
                if _check(u, p):
                    token = _make_token(u)
                    expires = datetime.now() + timedelta(hours=24)
                    cookies.set("vlm_session", token,   expires_at=expires)
                    cookies.set("vlm_user",    u,        expires_at=expires)
                    st.session_state.authenticated = True
                    st.session_state.staff_user    = u
                    st.rerun()
                else:
                    st.error("Incorrect credentials.")
    st.stop()

# ── DATA ────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def load_leads(): return get_all_leads()

def load_local():
    if LEADS_LOCAL.exists():
        with open(LEADS_LOCAL) as f: return json.load(f)
    return []

raw  = load_leads()
lraw = load_local()
df   = pd.DataFrame(raw)  if raw  else pd.DataFrame()
ldf  = pd.DataFrame(lraw) if lraw else pd.DataFrame()

for c in ["id","timestamp","funnel_type","name","email","company","role","niche","budget",
          "challenge","team_size","status","notes"]:
    if not df.empty and c not in df.columns: df[c] = ""

for c in ["emails_sent","replied","booked","vertical","last_sent_at"]:
    if not ldf.empty and c not in ldf.columns: ldf[c] = 0 if c == "emails_sent" else False if c in ("replied","booked") else ""

total     = len(ldf) if not ldf.empty else 0
contacted = int((ldf["emails_sent"] > 0).sum()) if not ldf.empty else 0
replied   = int(ldf["replied"].sum())  if not ldf.empty else 0
booked    = int(ldf["booked"].sum())   if not ldf.empty else 0
e1 = int((ldf["emails_sent"] >= 1).sum()) if not ldf.empty else 0
e2 = int((ldf["emails_sent"] >= 2).sum()) if not ldf.empty else 0
e3 = int((ldf["emails_sent"] >= 3).sum()) if not ldf.empty else 0
e4 = int((ldf["emails_sent"] >= 4).sum()) if not ldf.empty else 0

contact_rate = round(contacted / total * 100, 1) if total else 0
reply_rate   = round(replied / contacted * 100, 1) if contacted else 0
book_rate    = round(booked / contacted * 100, 1)  if contacted else 0

verticals = {}
if not ldf.empty and "vertical" in ldf.columns:
    for v, g in ldf.groupby("vertical"):
        if v: verticals[str(v)] = len(g)

now_str = datetime.now().strftime("%b %d, %Y  %H:%M")

# ── HEADER ──────────────────────────────────────────────────────────────────
hc1, hc2, hc3 = st.columns([4, 2, 1])
with hc1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:14px;padding-bottom:20px;border-bottom:1px solid rgba(255,255,255,0.04);margin-bottom:28px;">
      <div>
        <div class="cmd-title">⚡ VLM Command Center</div>
        <div class="cmd-sub">Outreach Pipeline  ·  B2B Enterprise  ·  {now_str}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
with hc2:
    st.markdown(f"""
    <div style="padding-top:4px;display:flex;gap:10px;align-items:center;">
      <div class="live-badge"><div class="live-dot"></div>System Live</div>
      <span class="ts">3 AM BKK</span>
    </div>
    """, unsafe_allow_html=True)
with hc3:
    st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
    if st.button("Sign Out", use_container_width=True):
        cookies.delete("vlm_session")
        cookies.delete("vlm_user")
        st.session_state.authenticated = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    if st.button("↻ Refresh", use_container_width=True):
        st.cache_data.clear(); st.rerun()

# ── HERO METRICS ────────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
cards = [
    (m1, "🎯", "#00ff88", "Total Pipeline",  total,     "leads sourced",     "Active"),
    (m2, "📨", "#2d9cff", "Contacted",       contacted, f"{contact_rate}% of pipeline", f"Email 1 sent"),
    (m3, "💬", "#ffd700", "Replies",         replied,   f"{reply_rate}% reply rate",    "Monitoring inbox"),
    (m4, "📅", "#ff2d78", "Booked",          booked,    f"{book_rate}% book rate",      "Setup calls"),
    (m5, "⚡", "#a855f7", "Seq Complete",    e4,        f"{e2} on email 2",             "Full drip done"),
]
for col, icon, accent, label, num, sub, pill in cards:
    with col:
        st.markdown(f"""
        <div class="mc" style="--accent:{accent}">
          <div class="mc-icon">{icon}</div>
          <div class="mc-label">{label}</div>
          <div class="mc-num" style="--c:{accent}">{num}</div>
          <div class="mc-sub">{sub}</div>
          <div class="mc-pill" style="background:rgba(255,255,255,0.04);color:{accent};border-color:{accent}33">{pill}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)

# ── CHARTS ROW ──────────────────────────────────────────────────────────────
cc1, cc2 = st.columns([1, 1])

with cc1:
    st.markdown('<div class="sec">Pipeline Funnel</div>', unsafe_allow_html=True)
    funnel_vals   = [total, contacted, max(replied, 0) or 0, booked]
    funnel_labels = ["Sourced", "Contacted", "Replied", "Booked"]
    funnel_colors = ["#2d9cff", "#00ff88", "#ffd700", "#ff2d78"]
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_labels,
        x=funnel_vals,
        textinfo="value+percent initial",
        marker=dict(color=funnel_colors, line=dict(width=0)),
        connector=dict(line=dict(color="rgba(255,255,255,0.04)", width=1)),
        textfont=dict(color="white", size=14),
    ))
    fig_funnel.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,0.7)", height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        yaxis=dict(tickfont=dict(color="rgba(255,255,255,0.6)", size=13)),
    )
    st.plotly_chart(fig_funnel, use_container_width=True, config={"displayModeBar": False})

with cc2:
    st.markdown('<div class="sec">Drip Sequence Progress</div>', unsafe_allow_html=True)
    seq_labels = ["Email 1<br>Day 0 — Escape", "Email 2<br>Day 3 — Arrival", "Email 3<br>Day 7 — Setup CTA", "Email 4<br>Day 14 — Breakup"]
    seq_vals   = [e1, e2, e3, e4]
    seq_colors = ["#00ff88", "#2d9cff", "#ffd700", "#ff2d78"]
    fig_drip = go.Figure()
    for i, (label, val, color) in enumerate(zip(seq_labels, seq_vals, seq_colors)):
        fig_drip.add_trace(go.Bar(
            x=[val], y=[label], orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            name=label.split("<br>")[0],
            showlegend=False,
            text=[str(val)], textposition="outside",
            textfont=dict(color=color, size=13),
        ))
    fig_drip.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="rgba(255,255,255,0.7)", height=280,
        margin=dict(t=10, b=10, l=10, r=60),
        xaxis=dict(range=[0, max(total+5, 10)], tickfont=dict(color="rgba(255,255,255,0.4)", size=11),
                   gridcolor="rgba(255,255,255,0.05)", zeroline=False),
        yaxis=dict(tickfont=dict(color="rgba(255,255,255,0.6)", size=11), gridcolor="rgba(0,0,0,0)"),
        barmode="overlay", bargap=0.3,
    )
    st.plotly_chart(fig_drip, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── GAUGE ROW ───────────────────────────────────────────────────────────────
g1, g2, g3 = st.columns(3)
gauges = [
    (g1, "Contact Rate",  contact_rate, "#00ff88", "% of leads contacted"),
    (g2, "Reply Rate",    reply_rate,   "#ffd700", "% replied to email 1"),
    (g3, "Booking Rate",  book_rate,    "#ff2d78", "% booked setup call"),
]
for col, title, val, color, sub in gauges:
    with col:
        fig_g = go.Figure(go.Indicator(
            mode="gauge+number",
            value=val,
            number={"suffix": "%", "font": {"color": color, "size": 48, "family": "Inter"}},
            title={"text": f"<b>{title}</b><br><span style='font-size:0.85em;color:#9a9abf'>{sub}</span>",
                   "font": {"color": "rgba(255,255,255,0.85)", "size": 14}},
            gauge={
                "axis": {"range": [0, 100], "tickcolor": "rgba(255,255,255,0.15)",
                         "tickfont": {"color": "rgba(255,255,255,0.4)", "size": 10},
                         "nticks": 5},
                "bar":  {"color": color, "thickness": 0.25},
                "bgcolor": "rgba(0,0,0,0)",
                "bordercolor": "rgba(0,0,0,0)",
                "steps": [{"range": [0, 100], "color": f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.05)"}],
                "threshold": {"line": {"color": color, "width": 2}, "thickness": 0.9, "value": val},
            }
        ))
        fig_g.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=220, margin=dict(t=30, b=10, l=30, r=30),
            font_color="white",
        )
        st.plotly_chart(fig_g, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

# ── BREAKDOWN + NEXT ACTIONS ─────────────────────────────────────────────────
bc1, bc2 = st.columns([1, 1])

with bc1:
    st.markdown('<div class="sec">Leads by Vertical</div>', unsafe_allow_html=True)
    vert_colors = {"financial_advisor": "#2d9cff", "coach_consultant": "#a855f7", "ad_agency": "#ff2d78"}
    vert_max    = max(verticals.values()) if verticals else 1
    vert_html   = ""
    for v, ct in sorted(verticals.items(), key=lambda x: -x[1]):
        pct  = round(ct / total * 100) if total else 0
        fill = round(ct / vert_max * 100)
        c    = vert_colors.get(v, "#00ff88")
        label= v.replace("_", " ").title()
        vert_html += f"""
        <div class="vb-row">
          <div class="vb-label">{label}</div>
          <div class="vb-bg"><div class="vb-fill" style="--c:{c};width:{fill}%"></div></div>
          <div class="vb-pct" style="color:{c}">{pct}%</div>
          <div class="vb-ct">{ct}</div>
        </div>"""
    st.markdown(vert_html, unsafe_allow_html=True)

    # Drip timeline
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="sec">Drip Timeline</div>', unsafe_allow_html=True)
    steps = [
        ("D0",  "Email 1",   "Sent",    "Mar 26",  "sent"),
        ("D3",  "Email 2",   "Arrival", "Mar 29",  "next"),
        ("D7",  "Email 3",   "CTA",     "Apr 2",   ""),
        ("D14", "Email 4",   "Breakup", "Apr 5",   ""),
    ]
    dots = "".join([f"""
    <div class="drip-step">
      <div class="drip-dot {state}">{day}</div>
      <div class="drip-label {state}">{label}</div>
      <div class="drip-day">{date}</div>
    </div>""" for day, label, _, date, state in steps])
    st.markdown(f'<div class="drip-row">{dots}</div>', unsafe_allow_html=True)

with bc2:
    st.markdown('<div class="sec">Upcoming Actions</div>', unsafe_allow_html=True)
    actions = [
        ("📨", "#00ff88", "Email 2 — Arrival Frame",   "50 leads · Mar 29 at 3:00 AM BKK",         "SCHEDULED"),
        ("📨", "#2d9cff", "Email 3 — Setup Call CTA",  "50 leads · Apr 2 at 3:00 AM BKK",          "SCHEDULED"),
        ("📨", "#ffd700", "Email 4 — Breakup",          "50 leads · Apr 5 at 3:00 AM BKK",          "SCHEDULED"),
        ("🔍", "#a855f7", "Inbox Monitor",              "Hourly · Next run at :05",                  "LIVE"),
        ("🔄", "#ff2d78", "CRM Sync",                   "Hourly · Next run at :07",                  "LIVE"),
    ]
    for icon, color, title, sub, badge in actions:
        bg = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.06)"
        st.markdown(f"""
        <div class="na-card">
          <div class="na-icon">{icon}</div>
          <div><div class="na-title">{title}</div><div class="na-sub">{sub}</div></div>
          <div class="na-badge" style="background:{bg};color:{color};border:1px solid {color}33">{badge}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── LEAD PIPELINE TABLE ──────────────────────────────────────────────────────
with st.expander("📋  Lead Pipeline — View & Update", expanded=False):
    if not ldf.empty:
        fc1, fc2, fc3, fc4 = st.columns(4)
        with fc1: f_vert   = st.selectbox("Vertical", ["All"] + sorted([v for v in ldf["vertical"].dropna().unique() if v]))
        with fc2: f_status = st.selectbox("Status",   ["All"] + STAGES)
        with fc3: f_sent   = st.selectbox("Emails Sent", ["All","0","1","2","3","4"])
        with fc4: f_search = st.text_input("Search")

        fdf = ldf.copy()
        if f_vert   != "All": fdf = fdf[fdf["vertical"] == f_vert]
        if f_status != "All" and "status" in fdf.columns: fdf = fdf[fdf["status"] == f_status]
        if f_sent   != "All": fdf = fdf[fdf["emails_sent"].astype(str) == f_sent]
        if f_search.strip():
            q = f_search.strip().lower()
            fdf = fdf[fdf.apply(lambda r: q in str(r.get("name","")).lower() or q in str(r.get("email","")).lower() or q in str(r.get("company","")).lower(), axis=1)]

        st.markdown(f"<p style='color:#2a2a4a;font-size:0.78rem;'>Showing {len(fdf)} of {total}</p>", unsafe_allow_html=True)

        show_cols = ["name","email","company","vertical","emails_sent","last_sent_at","replied","booked","status"]
        avail = [c for c in show_cols if c in fdf.columns]
        st.dataframe(
            fdf[avail].sort_values("emails_sent", ascending=False).reset_index(drop=True),
            use_container_width=True, height=300,
            column_config={
                "name":         st.column_config.TextColumn("Name",       width="medium"),
                "email":        st.column_config.TextColumn("Email",      width="large"),
                "company":      st.column_config.TextColumn("Company",    width="medium"),
                "vertical":     st.column_config.TextColumn("Vertical",   width="medium"),
                "emails_sent":  st.column_config.NumberColumn("Sent",     width="small"),
                "last_sent_at": st.column_config.TextColumn("Last Sent",  width="medium"),
                "replied":      st.column_config.CheckboxColumn("Replied",width="small"),
                "booked":       st.column_config.CheckboxColumn("Booked", width="small"),
                "status":       st.column_config.TextColumn("Status",     width="medium"),
            }
        )

        buf = io.StringIO(); fdf[avail].to_csv(buf, index=False)
        st.download_button("Export CSV", buf.getvalue(), "vlm_leads.csv", "text/csv")

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sec">Update Lead</div>', unsafe_allow_html=True)

        if "id" in fdf.columns and not fdf.empty:
            options = fdf.apply(lambda r: f"{r.get('id','?')} — {r.get('name','?')} ({r.get('company','?')})", axis=1).tolist()
            sel    = st.selectbox("Select lead", options)
            sel_id = sel.split(" — ")[0]
            row    = fdf[fdf["id"] == sel_id]
            if not row.empty:
                r = row.iloc[0]
                d1, d2 = st.columns(2)
                with d1:
                    st.markdown(f"**{r.get('name','')}** · {r.get('email','')}")
                    st.markdown(f"{r.get('company','')} · {r.get('vertical','')}")
                with d2:
                    st.markdown(f"Emails sent: **{r.get('emails_sent',0)}** · Replied: **{r.get('replied',False)}** · Booked: **{r.get('booked',False)}**")

                cur = r.get("status","New")
                if cur not in STAGES: cur = "New"
                new_status = st.selectbox("Stage", STAGES, index=STAGES.index(cur))
                new_notes  = st.text_area("Notes", value=r.get("notes",""), height=80)
                if st.button("Save Changes"):
                    update_lead(sel_id, new_status, new_notes)
                    st.cache_data.clear(); st.success("Saved."); st.rerun()
    else:
        st.info("No local lead data found.")
