"""
VLM Command Center — Master Dashboard
One screen to rule everything: Instagram, Funnel, Revenue, Content Queue, CRM.
Run: streamlit run vlm_command_center.py --server.port 8503
"""

import streamlit as st
import json
import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

ROOT      = Path(__file__).parent
TMP       = ROOT / ".tmp"
NEO_IG    = ROOT / "output/users/Neo/Instagram"
SHAY_IG   = ROOT / "output/users/Shay/Instagram"
TYRIE_IG  = ROOT / "output/users/Tyrie/Instagram"

st.set_page_config(
    page_title="VLM Command Center",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700;800&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0a0a0f !important;
    color: #c8d6e5 !important;
    font-family: 'Rajdhani', sans-serif;
}
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #00ffff44; border-radius: 3px; }

h1,h2,h3 { font-family: 'Share Tech Mono', monospace !important; letter-spacing: 0.06em; }

.cmd-header {
    text-align: center; padding: 28px 0 8px;
    border-bottom: 1px solid rgba(0,255,255,0.15);
    margin-bottom: 28px;
}
.cmd-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2rem; color: #00ffff;
    text-shadow: 0 0 20px rgba(0,255,255,0.5);
    letter-spacing: 0.12em;
}
.cmd-sub { color: #445566; font-size: 0.85rem; letter-spacing: 0.1em; margin-top: 4px; }

/* Metric cards */
.metric-card {
    background: #0d0d18;
    border: 1px solid rgba(0,255,255,0.12);
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
    position: relative;
}
.metric-card.green  { border-color: rgba(0,255,128,0.25); }
.metric-card.yellow { border-color: rgba(255,200,0,0.25); }
.metric-card.red    { border-color: rgba(255,80,80,0.25); }
.metric-card.purple { border-color: rgba(160,80,255,0.25); }

.metric-val  { font-family: 'Share Tech Mono', monospace; font-size: 2.2rem; color: #00ffff; }
.metric-val.green  { color: #00ff80; }
.metric-val.yellow { color: #ffc800; }
.metric-val.red    { color: #ff5050; }
.metric-val.purple { color: #a050ff; }
.metric-lbl  { font-size: 0.72rem; color: #445566; letter-spacing: 0.09em; text-transform: uppercase; margin-top: 4px; }
.metric-sub  { font-size: 0.78rem; color: #334455; margin-top: 2px; }

/* Section headers */
.section-hdr {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.8rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: #334455; border-bottom: 1px solid #111122; padding-bottom: 8px; margin-bottom: 16px;
}

/* Account row */
.acct-row {
    background: #0d0d18; border: 1px solid #1a1a2e;
    border-radius: 8px; padding: 14px 18px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 8px;
}
.acct-name { font-family: 'Share Tech Mono', monospace; color: #00ffff; font-size: 0.88rem; }
.acct-handle { color: #334455; font-size: 0.78rem; }
.acct-stat { font-size: 0.82rem; }

/* Log entries */
.log-entry {
    background: #0a0a14; border-left: 2px solid #1a1a2e;
    padding: 8px 14px; margin-bottom: 6px; border-radius: 0 6px 6px 0;
    font-size: 0.8rem;
}
.log-entry.success { border-left-color: #00ff80; }
.log-entry.failed  { border-left-color: #ff5050; }
.log-entry.pending { border-left-color: #ffc800; }

/* Pipeline stages */
.stage-bar {
    background: #0d0d18; border: 1px solid #1a1a2e;
    border-radius: 8px; padding: 12px 16px; margin-bottom: 6px;
}
.stage-label { font-size: 0.75rem; color: #445566; text-transform: uppercase; letter-spacing: 0.08em; }
.stage-count { font-family: 'Share Tech Mono', monospace; color: #00ffff; font-size: 1.2rem; }

/* Revenue block */
.rev-block {
    background: #0a1a0a; border: 1px solid rgba(0,255,128,0.2);
    border-radius: 10px; padding: 20px 24px; margin-bottom: 10px;
}
.rev-main { font-family: 'Share Tech Mono', monospace; font-size: 2.4rem; color: #00ff80; }
.rev-label { font-size: 0.75rem; color: #335533; letter-spacing: 0.08em; text-transform: uppercase; }

/* Quick action buttons */
.stButton > button {
    background: #0d1a2a !important;
    border: 1px solid rgba(0,255,255,0.2) !important;
    color: #00ffff !important;
    border-radius: 6px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.05em !important;
    width: 100%;
}
.stButton > button:hover {
    background: #132030 !important;
    border-color: rgba(0,255,255,0.5) !important;
}
.stButton > button[kind="primary"] {
    background: #0a1a0f !important;
    border-color: rgba(0,255,128,0.4) !important;
    color: #00ff80 !important;
}

[data-testid="stTab"] { font-family: 'Rajdhani', sans-serif !important; }
[data-testid="stMetric"] { background: transparent !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_json(path, default=None):
    try:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return default if default is not None else {}


def time_ago(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str)
        diff = datetime.now() - dt
        if diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        if diff.days == 0:
            return f"{diff.seconds // 3600}h ago"
        return f"{diff.days}d ago"
    except Exception:
        return "—"


def post_now(account):
    result = subprocess.run(
        ["/opt/homebrew/bin/python3.11", "execution/auto_poster.py", "--account", account],
        cwd=str(ROOT), capture_output=True, text=True, timeout=120
    )
    return result.stdout + result.stderr


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="cmd-header">
    <div class="cmd-title">⚡ VLM COMMAND CENTER</div>
    <div class="cmd-sub">VIRAL LENSE MEDIA · {datetime.now().strftime("%Y-%m-%d %H:%M")} BKK</div>
</div>
""", unsafe_allow_html=True)

# ── Load all data ─────────────────────────────────────────────────────────────
approved_raw     = load_json(TMP / "approved_posts.json", {})
tyrie_approved   = load_json(TMP / "tyrie_approved.json", {})
shay_schedule    = load_json(TMP / "shay_schedule.json", [])
neo_log          = load_json(TMP / "neo_post_log.json", [])
shay_log         = load_json(TMP / "shay_post_log.json", [])
tyrie_log        = load_json(TMP / "tyrie_post_log.json", [])
activity_log     = load_json(TMP / "activity_log.json", [])
outfit_usage     = load_json(TMP / "outfit_usage.json", {})
outreach_leads   = load_json(TMP / "leads.json", [])
outreach_log     = load_json(TMP / "outreach_log.json", [])

neo_posted   = {e["stem"] for e in neo_log}
shay_posted  = {e["carousel_id"] for e in shay_log}
tyrie_posted = {e["stem"] for e in tyrie_log}

# Neo queue
neo_approved_raw = {k: v for k, v in approved_raw.items() if k != "shay"}
neo_ready = sum(1 for stem, val in neo_approved_raw.items()
                if val is True and stem not in neo_posted and (NEO_IG / f"{stem}.jpg").exists())

# Shay queue
shay_approved_ids = set(approved_raw.get("shay", {}).keys())
shay_ready = sum(1 for p in SHAY_IG.glob("*_carousel.json")
                 if json.loads(p.read_text()).get("id", p.stem.replace("_carousel","")) in shay_approved_ids
                 and json.loads(p.read_text()).get("id", p.stem.replace("_carousel","")) not in shay_posted
                 ) if SHAY_IG.exists() else 0

# Ty queue
tyrie_ready = 0
for d in [TYRIE_IG, TYRIE_IG / "couple"]:
    if not d.exists(): continue
    for cp in d.glob("*_caption.txt"):
        cid = cp.stem.replace("_caption", "")
        if cid in tyrie_approved and cid not in tyrie_posted:
            shots = list(d.glob(f"{cid}_shot*.jpg")) or ([d / f"{cid}.jpg"] if (d / f"{cid}.jpg").exists() else [])
            if shots: tyrie_ready += 1

total_queued = neo_ready + shay_ready + tyrie_ready
total_posted = len(neo_log) + len(shay_log) + len(tyrie_log)

# CRM leads (from local file if Google Sheets unavailable)
crm_b2c_leads, crm_b2b_leads = [], []
for crm_dir in [ROOT / "vlm-b2c", ROOT / "vlm-b2b"]:
    lf = crm_dir / "leads_local.json"
    if lf.exists():
        data = load_json(lf, [])
        for lead in data:
            if lead.get("funnel_type") == "B2C":
                crm_b2c_leads.append(lead)
            elif lead.get("funnel_type") == "B2B":
                crm_b2b_leads.append(lead)

# Try Google Sheets CRM
try:
    sys.path.insert(0, str(ROOT / "vlm-crm"))
    from utils.sheets import get_all_leads
    all_leads = get_all_leads() or []
    if all_leads:
        crm_b2c_leads = [l for l in all_leads if l.get("funnel_type") == "B2C"]
        crm_b2b_leads = [l for l in all_leads if l.get("funnel_type") == "B2B"]
except Exception:
    pass

total_leads = len(crm_b2c_leads) + len(crm_b2b_leads)
new_leads   = sum(1 for l in crm_b2c_leads + crm_b2b_leads if l.get("status","") in ["New",""])
won_leads   = sum(1 for l in crm_b2c_leads + crm_b2b_leads if l.get("status","") == "Closed Won")

# Outreach stats
outreach_total   = len(outreach_leads)
outreach_emailed = sum(1 for l in outreach_leads if l.get("email"))
outreach_sent    = sum(l.get("emails_sent", 0) for l in outreach_leads)
outreach_replied = sum(1 for l in outreach_leads if l.get("replied"))
outreach_booked  = sum(1 for l in outreach_leads if l.get("booked"))

# Revenue (manual for now — update as Stripe webhooks come in)
b2c_subs = st.session_state.get("b2c_subs", 0)
b2b_subs = st.session_state.get("b2b_subs", 0)
mrr = (b2c_subs * 49) + (b2b_subs * 997)


# ── TOP METRICS ROW ───────────────────────────────────────────────────────────
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    st.markdown(f"""<div class="metric-card green">
        <div class="metric-val green">{total_posted}</div>
        <div class="metric-lbl">Posts Live</div>
        <div class="metric-sub">All 3 accounts</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="metric-card yellow">
        <div class="metric-val yellow">{total_queued}</div>
        <div class="metric-lbl">Queued Content</div>
        <div class="metric-sub">Neo {neo_ready} · Shay {shay_ready} · Ty {tyrie_ready}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-val">{outreach_total}</div>
        <div class="metric-lbl">Outreach Leads</div>
        <div class="metric-sub">{outreach_emailed} w/ email · {outreach_total - outreach_emailed} pending</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="metric-card yellow">
        <div class="metric-val yellow">{outreach_sent}</div>
        <div class="metric-lbl">Emails Sent</div>
        <div class="metric-sub">{outreach_replied} replied · {outreach_booked} booked</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""<div class="metric-card green">
        <div class="metric-val green">{outreach_booked}</div>
        <div class="metric-lbl">Calls Booked</div>
        <div class="metric-sub">{won_leads} closed won</div>
    </div>""", unsafe_allow_html=True)

with c6:
    st.markdown(f"""<div class="metric-card purple">
        <div class="metric-val purple">${mrr:,}</div>
        <div class="metric-lbl">MRR</div>
        <div class="metric-sub">Update below</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_ig, tab_funnel, tab_crm, tab_revenue, tab_outreach, tab_actions = st.tabs([
    "📸  Instagram",
    "🎯  Funnel",
    "📋  CRM Pipeline",
    "💰  Revenue",
    "📧  Outreach",
    "⚡  Quick Actions",
])


# ═══════════════════════════════════════════════════════
# TAB 1 — INSTAGRAM
# ═══════════════════════════════════════════════════════
with tab_ig:
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown('<div class="section-hdr">Account Status</div>', unsafe_allow_html=True)

        accounts = [
            ("NEO",  "@neoismyname1",  neo_ready,  len(neo_log),  neo_log,   "🟡" if neo_ready == 0 else "🟢"),
            ("SHAY", "@shay.so.fine",  shay_ready, len(shay_log), shay_log,  "🟡" if shay_ready == 0 else "🟢"),
            ("TY",   "@tytheguyyttg",  tyrie_ready,len(tyrie_log),tyrie_log, "🟡" if tyrie_ready == 0 else "🟢"),
        ]

        for name, handle, queued, posted, log, dot in accounts:
            last = time_ago(log[-1]["posted_at"]) if log else "Never"
            last_url = log[-1].get("url", "") if log else ""
            st.markdown(f"""
            <div class="acct-row">
                <div>
                    <div class="acct-name">{dot} {name}</div>
                    <div class="acct-handle">{handle}</div>
                </div>
                <div style="text-align:center">
                    <div class="acct-stat" style="color:#00ff80;">{posted}</div>
                    <div class="acct-handle">posted</div>
                </div>
                <div style="text-align:center">
                    <div class="acct-stat" style="color:#ffc800;">{queued}</div>
                    <div class="acct-handle">queued</div>
                </div>
                <div style="text-align:right">
                    <div class="acct-stat" style="color:#445566;">Last: {last}</div>
                    {"<a href='" + last_url + "' target='_blank' style='color:#334455;font-size:0.72rem;'>view post</a>" if last_url else ""}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Cron status
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Cron Schedule</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="stage-bar">
            <div class="acct-handle" style="margin-bottom:6px;">Auto-poster runs 2× daily · Bangkok time</div>
            <div style="display:flex;gap:16px;margin-top:8px;">
                <div style="background:#0a1a0a;border:1px solid rgba(0,255,128,0.2);border-radius:6px;padding:8px 16px;font-family:'Share Tech Mono',monospace;color:#00ff80;font-size:0.9rem;">10:00 AM</div>
                <div style="background:#0a1a0a;border:1px solid rgba(0,255,128,0.2);border-radius:6px;padding:8px 16px;font-family:'Share Tech Mono',monospace;color:#00ff80;font-size:0.9rem;">10:00 PM</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="section-hdr">Recent Activity</div>', unsafe_allow_html=True)
        recent = sorted(activity_log, key=lambda x: x.get("timestamp",""), reverse=True)[:15]
        if recent:
            for entry in recent:
                status = entry.get("status", "")
                cls = "success" if status == "success" else ("failed" if status == "failed" else "pending")
                ts = time_ago(entry.get("timestamp", ""))
                action = entry.get("action", "")
                details = entry.get("details", "")[:60]
                st.markdown(f"""
                <div class="log-entry {cls}">
                    <span style="color:#334455;font-size:0.7rem;">{ts}</span>
                    <span style="color:#556677;margin:0 6px;">·</span>
                    <span style="color:#c8d6e5;">{action}</span><br>
                    <span style="color:#445566;font-size:0.75rem;">{details}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="acct-handle">No activity yet.</div>', unsafe_allow_html=True)

        # Recent posts
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Last 5 Posts</div>', unsafe_allow_html=True)
        all_posts = []
        for log, acct in [(neo_log, "Neo"), (shay_log, "Shay"), (tyrie_log, "Ty")]:
            for e in log:
                all_posts.append({**e, "account": acct})
        all_posts.sort(key=lambda x: x.get("posted_at", ""), reverse=True)
        for p in all_posts[:5]:
            url = p.get("url", "")
            ts  = time_ago(p.get("posted_at", ""))
            stem = p.get("stem") or p.get("carousel_id", "")
            acct = p.get("account", "")
            st.markdown(f"""
            <div class="log-entry success">
                <span style="color:#00ff80;font-size:0.72rem;">{acct}</span>
                <span style="color:#334455;margin:0 6px;">·</span>
                <span style="color:#445566;font-size:0.72rem;">{ts}</span>
                {"<br><a href='" + url + "' target='_blank' style='color:#224433;font-size:0.7rem;'>" + url.replace("https://","") + "</a>" if url else ""}
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 2 — FUNNEL
# ═══════════════════════════════════════════════════════
with tab_funnel:
    fc1, fc2 = st.columns(2)

    with fc1:
        st.markdown('<div class="section-hdr">B2C — Creator Plan ($49/mo)</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="rev-block" style="background:#0a0a1a;border-color:rgba(79,70,229,0.25);">
            <div class="rev-main" style="color:#818CF8;">{len(crm_b2c_leads)}</div>
            <div class="rev-label" style="color:#2d2d5a;">Total B2C Leads</div>
        </div>
        """, unsafe_allow_html=True)

        b2c_stages = {}
        for lead in crm_b2c_leads:
            s = lead.get("status", "New") or "New"
            b2c_stages[s] = b2c_stages.get(s, 0) + 1

        stage_colors = {
            "New": "#60A5FA", "Contacted": "#FBBF24",
            "Demo Booked": "#A78BFA", "Closed Won": "#34D399", "Closed Lost": "#F87171"
        }
        for stage in ["New", "Contacted", "Demo Booked", "Closed Won", "Closed Lost"]:
            count = b2c_stages.get(stage, 0)
            color = stage_colors.get(stage, "#445566")
            pct   = int((count / len(crm_b2c_leads) * 100)) if crm_b2c_leads else 0
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="stage-label">{stage}</span>
                    <span class="stage-count" style="color:{color};">{count}</span>
                </div>
                <div style="background:#111122;height:3px;border-radius:2px;margin-top:8px;">
                    <div style="width:{pct}%;height:3px;background:{color};border-radius:2px;opacity:0.7;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with fc2:
        st.markdown('<div class="section-hdr">B2B — Enterprise Plan ($997/mo)</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="rev-block">
            <div class="rev-main">{len(crm_b2b_leads)}</div>
            <div class="rev-label">Total B2B Leads</div>
        </div>
        """, unsafe_allow_html=True)

        b2b_stages = {}
        for lead in crm_b2b_leads:
            s = lead.get("status", "New") or "New"
            b2b_stages[s] = b2b_stages.get(s, 0) + 1

        for stage in ["New", "Contacted", "Demo Booked", "Closed Won", "Closed Lost"]:
            count = b2b_stages.get(stage, 0)
            color = stage_colors.get(stage, "#445566")
            pct   = int((count / len(crm_b2b_leads) * 100)) if crm_b2b_leads else 0
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span class="stage-label">{stage}</span>
                    <span class="stage-count" style="color:{color};">{count}</span>
                </div>
                <div style="background:#111122;height:3px;border-radius:2px;margin-top:8px;">
                    <div style="width:{pct}%;height:3px;background:{color};border-radius:2px;opacity:0.7;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Recent leads table
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">Recent Leads</div>', unsafe_allow_html=True)
    all_leads_combined = sorted(
        crm_b2c_leads + crm_b2b_leads,
        key=lambda x: x.get("timestamp", ""), reverse=True
    )[:10]
    if all_leads_combined:
        import pandas as pd
        df_leads = pd.DataFrame(all_leads_combined)[
            ["timestamp", "funnel_type", "name", "email", "company", "status"]
        ].rename(columns={
            "timestamp": "Time", "funnel_type": "Type", "name": "Name",
            "email": "Email", "company": "Company", "status": "Status"
        })
        df_leads["Time"] = df_leads["Time"].apply(lambda x: x[:16] if x else "")
        st.dataframe(df_leads, use_container_width=True, hide_index=True)
    else:
        st.markdown('<div class="acct-handle">No leads yet. Funnels need to be deployed and live.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 3 — CRM PIPELINE
# ═══════════════════════════════════════════════════════
with tab_crm:
    st.markdown('<div class="section-hdr">Pipeline — All Leads</div>', unsafe_allow_html=True)

    if all_leads_combined:
        stage_cols = st.columns(5)
        stage_names = ["New", "Contacted", "Demo Booked", "Closed Won", "Closed Lost"]
        stage_colors_bg = {
            "New": "#0a1020", "Contacted": "#1a150a",
            "Demo Booked": "#130a1a", "Closed Won": "#0a1a0a", "Closed Lost": "#1a0a0a"
        }
        stage_colors_border = {
            "New": "rgba(96,165,250,0.3)", "Contacted": "rgba(251,191,36,0.3)",
            "Demo Booked": "rgba(167,139,250,0.3)", "Closed Won": "rgba(52,211,153,0.3)",
            "Closed Lost": "rgba(248,113,113,0.3)"
        }
        stage_text_colors = {
            "New": "#60A5FA", "Contacted": "#FBBF24",
            "Demo Booked": "#A78BFA", "Closed Won": "#34D399", "Closed Lost": "#F87171"
        }

        stage_buckets = {s: [] for s in stage_names}
        for lead in all_leads_combined:
            s = lead.get("status", "New") or "New"
            if s not in stage_buckets:
                s = "New"
            stage_buckets[s].append(lead)

        for col, stage in zip(stage_cols, stage_names):
            with col:
                leads_in_stage = stage_buckets[stage]
                color = stage_text_colors[stage]
                bg    = stage_colors_bg[stage]
                border= stage_colors_border[stage]
                st.markdown(f"""
                <div style="background:{bg};border:1px solid {border};border-radius:8px;padding:10px 12px;margin-bottom:10px;">
                    <div style="font-size:0.7rem;letter-spacing:0.1em;text-transform:uppercase;color:{color};margin-bottom:4px;">{stage}</div>
                    <div style="font-family:'Share Tech Mono',monospace;color:{color};font-size:1.6rem;">{len(leads_in_stage)}</div>
                </div>
                """, unsafe_allow_html=True)
                for lead in leads_in_stage[:5]:
                    name    = lead.get("name", "Unknown")[:18]
                    company = lead.get("company", "")[:18]
                    ftype   = lead.get("funnel_type", "")
                    type_color = "#818CF8" if ftype == "B2C" else "#10B981"
                    st.markdown(f"""
                    <div style="background:#0a0a14;border:1px solid #1a1a2e;border-radius:6px;padding:8px 10px;margin-bottom:5px;">
                        <div style="color:#c8d6e5;font-size:0.78rem;font-weight:600;">{name}</div>
                        <div style="color:#334455;font-size:0.7rem;">{company}</div>
                        <div style="color:{type_color};font-size:0.65rem;margin-top:3px;">{ftype}</div>
                    </div>
                    """, unsafe_allow_html=True)
                if len(leads_in_stage) > 5:
                    st.markdown(f'<div style="color:#334455;font-size:0.7rem;text-align:center;">+{len(leads_in_stage)-5} more</div>', unsafe_allow_html=True)
    else:
        st.info("No CRM data yet. Leads will appear here once funnels are live.")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-hdr">CRM Quick Links</div>', unsafe_allow_html=True)
    lc1, lc2, lc3 = st.columns(3)
    with lc1:
        st.link_button("Open B2C Funnel →", "http://localhost:8501", use_container_width=True)
    with lc2:
        st.link_button("Open B2B Funnel →", "http://localhost:8502", use_container_width=True)
    with lc3:
        st.link_button("Open CRM →", "http://localhost:8504", use_container_width=True)


# ═══════════════════════════════════════════════════════
# TAB 4 — REVENUE
# ═══════════════════════════════════════════════════════
with tab_revenue:
    rc1, rc2 = st.columns([2, 1])

    with rc1:
        st.markdown('<div class="section-hdr">Monthly Recurring Revenue</div>', unsafe_allow_html=True)

        rev_c1, rev_c2 = st.columns(2)
        with rev_c1:
            b2c_subs_input = st.number_input("B2C Subscribers ($49/mo)", min_value=0, value=b2c_subs, step=1)
            st.session_state["b2c_subs"] = b2c_subs_input
        with rev_c2:
            b2b_subs_input = st.number_input("B2B Subscribers ($997/mo)", min_value=0, value=b2b_subs, step=1)
            st.session_state["b2b_subs"] = b2b_subs_input

        b2c_rev = b2c_subs_input * 49
        b2b_rev = b2b_subs_input * 997
        total_mrr = b2c_rev + b2b_rev

        st.markdown(f"""
        <div class="rev-block">
            <div class="rev-label">Total MRR</div>
            <div class="rev-main">${total_mrr:,}</div>
        </div>
        """, unsafe_allow_html=True)

        rr1, rr2 = st.columns(2)
        with rr1:
            st.markdown(f"""
            <div class="rev-block" style="background:#0a0a1a;border-color:rgba(79,70,229,0.25);">
                <div class="rev-label" style="color:#2d2d5a;">B2C Revenue</div>
                <div class="rev-main" style="color:#818CF8;">${b2c_rev:,}</div>
                <div style="color:#1a1a3a;font-size:0.75rem;margin-top:4px;">{b2c_subs_input} × $49</div>
            </div>
            """, unsafe_allow_html=True)
        with rr2:
            st.markdown(f"""
            <div class="rev-block">
                <div class="rev-label">B2B Revenue</div>
                <div class="rev-main">${b2b_rev:,}</div>
                <div style="color:#1a3320;font-size:0.75rem;margin-top:4px;">{b2b_subs_input} × $997</div>
            </div>
            """, unsafe_allow_html=True)

    with rc2:
        st.markdown('<div class="section-hdr">Revenue Targets</div>', unsafe_allow_html=True)
        targets = [
            ("$10K MRR",  10000,  "First milestone"),
            ("$25K MRR",  25000,  "Ramen profitable"),
            ("$50K MRR",  50000,  "Agency-level"),
            ("$100K MRR", 100000, "Scale mode"),
            ("$500K MRR", 500000, "VLM vision"),
        ]
        for label, target, note in targets:
            pct = min(int((total_mrr / target) * 100), 100)
            color = "#00ff80" if pct >= 100 else ("#ffc800" if pct > 50 else "#334455")
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;">
                    <span class="stage-label">{label} <span style="color:#223322;font-weight:400;">({note})</span></span>
                    <span style="font-size:0.75rem;color:{color};">{pct}%</span>
                </div>
                <div style="background:#111122;height:3px;border-radius:2px;margin-top:8px;">
                    <div style="width:{pct}%;height:3px;background:{color};border-radius:2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Offer Summary</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="stage-bar">
            <div style="color:#c8d6e5;font-size:0.82rem;margin-bottom:8px;">B2C Creator Plan</div>
            <div style="color:#818CF8;font-family:'Share Tech Mono',monospace;font-size:1.1rem;">$49 / month</div>
            <div style="color:#334455;font-size:0.72rem;margin-top:4px;">Unlimited AI image gen · Consistent characters</div>
        </div>
        <div class="stage-bar">
            <div style="color:#c8d6e5;font-size:0.82rem;margin-bottom:8px;">B2B Enterprise Plan</div>
            <div style="color:#00ff80;font-family:'Share Tech Mono',monospace;font-size:1.1rem;">$997 / month</div>
            <div style="color:#334455;font-size:0.72rem;margin-top:4px;">Private workspace · Onboarding · Unlimited gen</div>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 5 — OUTREACH
# ═══════════════════════════════════════════════════════
with tab_outreach:
    oc1, oc2, oc3, oc4, oc5 = st.columns(5)
    def _omet(col, val, label, sub, color=""):
        col.markdown(f"""<div class="metric-card {color}">
            <div class="metric-val {color}">{val}</div>
            <div class="metric-lbl">{label}</div>
            <div class="metric-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

    _omet(oc1, outreach_total,   "Leads Sourced",  "from Explorium API")
    _omet(oc2, outreach_emailed, "Have Email",      "ready to contact", "yellow")
    _omet(oc3, outreach_sent,    "Emails Sent",     "across all sequences", "green" if outreach_sent > 0 else "")
    _omet(oc4, outreach_replied, "Replied",         f"{int(outreach_replied/outreach_sent*100) if outreach_sent else 0}% reply rate", "purple")
    _omet(oc5, outreach_booked,  "Calls Booked",    "conversion goal", "green")

    st.markdown("<br>", unsafe_allow_html=True)
    ol1, ol2 = st.columns([1, 1])

    with ol1:
        # Vertical breakdown
        st.markdown('<div class="section-hdr">Vertical Breakdown</div>', unsafe_allow_html=True)
        verticals_cfg = [
            ("ad_agency",         "Ad Agency",         "#00ffff"),
            ("financial_advisor", "Financial Advisor",  "#a050ff"),
            ("coach_consultant",  "Coach / Consultant", "#ffc800"),
        ]
        for vkey, vlabel, vcolor in verticals_cfg:
            v_leads    = [l for l in outreach_leads if l.get("vertical") == vkey]
            v_total    = len(v_leads)
            v_sent     = sum(l.get("emails_sent", 0) for l in v_leads)
            v_replied  = sum(1 for l in v_leads if l.get("replied"))
            v_booked   = sum(1 for l in v_leads if l.get("booked"))
            v_emailed  = sum(1 for l in v_leads if l.get("email"))
            v_pct      = int(v_sent / (v_total * 3) * 100) if v_total else 0
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
                    <span style="font-family:'Share Tech Mono',monospace;color:{vcolor};font-size:0.85rem;">{vlabel}</span>
                    <span style="color:#445566;font-size:0.75rem;">{v_total} leads · {v_emailed} w/email</span>
                </div>
                <div style="display:flex;gap:16px;font-size:0.75rem;color:#334455;margin-bottom:8px;">
                    <span>📧 {v_sent} sent</span>
                    <span>↩ {v_replied} replied</span>
                    <span>📅 {v_booked} booked</span>
                </div>
                <div style="background:#111122;height:2px;border-radius:2px;">
                    <div style="width:{v_pct}%;height:2px;background:{vcolor};border-radius:2px;opacity:0.6;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Drip sequence progress
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Drip Sequence Progress</div>', unsafe_allow_html=True)
        seq_counts = [0, 0, 0]  # how many leads have received email 1, 2, 3
        for l in outreach_leads:
            sent = l.get("emails_sent", 0)
            for i in range(min(sent, 3)):
                seq_counts[i] += 1

        seq_labels = [("Email 1", "Day 0 — Cold intro", "#00ffff"),
                      ("Email 2", "Day 3 — Proof + follow-up", "#a050ff"),
                      ("Email 3", "Day 7 — Final CTA", "#ffc800")]
        for (label, note, color), count in zip(seq_labels, seq_counts):
            pct = int(count / outreach_emailed * 100) if outreach_emailed else 0
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="font-family:'Share Tech Mono',monospace;color:{color};font-size:0.82rem;">{label}</span>
                        <span style="color:#334455;font-size:0.7rem;margin-left:8px;">{note}</span>
                    </div>
                    <span style="font-family:'Share Tech Mono',monospace;color:{color};font-size:1.1rem;">{count}</span>
                </div>
                <div style="background:#111122;height:2px;border-radius:2px;margin-top:8px;">
                    <div style="width:{pct}%;height:2px;background:{color};border-radius:2px;opacity:0.5;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Actions
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Run Outreach Bot</div>', unsafe_allow_html=True)
        ac1, ac2 = st.columns(2)
        with ac1:
            if st.button("⚡ Source New Leads", key="source_leads"):
                with st.spinner("Sourcing leads from Explorium..."):
                    r = subprocess.run(
                        ["/opt/homebrew/bin/python3.11", "execution/source_leads.py"],
                        cwd=str(ROOT), capture_output=True, text=True, timeout=120
                    )
                out = r.stdout + r.stderr
                if "new leads added" in out.lower() or "saved" in out.lower():
                    st.success("Leads sourced!")
                else:
                    st.error(out[-400:])
                st.code(out, language=None)
        with ac2:
            if st.button("📧 Send Outreach Emails", key="send_outreach"):
                with st.spinner("Sending emails..."):
                    r = subprocess.run(
                        ["/opt/homebrew/bin/python3.11", "execution/send_outreach.py"],
                        cwd=str(ROOT), capture_output=True, text=True, timeout=120
                    )
                out = r.stdout + r.stderr
                st.code(out, language=None)

    with ol2:
        # Recent outreach log
        st.markdown('<div class="section-hdr">Recent Outreach Activity</div>', unsafe_allow_html=True)
        recent_outreach = sorted(outreach_log, key=lambda x: x.get("timestamp", ""), reverse=True)[:20]
        if recent_outreach:
            for entry in recent_outreach:
                status = entry.get("status", "")
                cls    = "success" if status == "sent" else "failed"
                ts     = time_ago(entry.get("timestamp", ""))
                name   = entry.get("name", "?")
                company= entry.get("company", "")[:22]
                seq    = entry.get("seq_email_num", "?")
                vert   = entry.get("vertical", "").replace("_", " ")
                subj   = entry.get("subject", "")[:45]
                st.markdown(f"""
                <div class="log-entry {cls}">
                    <div style="display:flex;justify-content:space-between;">
                        <span style="color:#c8d6e5;font-size:0.78rem;">{name}</span>
                        <span style="color:#334455;font-size:0.7rem;">{ts}</span>
                    </div>
                    <div style="color:#445566;font-size:0.72rem;">{company} · {vert}</div>
                    <div style="color:#556677;font-size:0.7rem;margin-top:2px;">Email {seq}/3 · {subj}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="acct-handle">No emails sent yet. Run the outreach bot to start.</div>', unsafe_allow_html=True)

        # Lead table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Lead Pipeline</div>', unsafe_allow_html=True)
        if outreach_leads:
            import pandas as pd
            df_out = pd.DataFrame(outreach_leads)[[
                "name", "company", "role", "niche", "email", "emails_sent", "replied", "booked", "status"
            ]].rename(columns={
                "name": "Name", "company": "Company", "role": "Role",
                "niche": "Vertical", "email": "Email",
                "emails_sent": "Sent", "replied": "Reply", "booked": "Booked", "status": "Status"
            })
            df_out["Email"] = df_out["Email"].apply(lambda x: x[:28] if x else "—")
            st.dataframe(df_out, use_container_width=True, hide_index=True, height=420)
        else:
            st.markdown('<div class="acct-handle">No leads yet. Click "Source New Leads" to start.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════
# TAB 6 — QUICK ACTIONS
# ═══════════════════════════════════════════════════════
with tab_actions:
    qa1, qa2 = st.columns(2)

    with qa1:
        st.markdown('<div class="section-hdr">Instagram — Post Now</div>', unsafe_allow_html=True)

        if st.button("⚡ Post Neo Now", key="post_neo"):
            with st.spinner("Posting to Neo..."):
                out = post_now("neo")
            if "SUCCESS" in out:
                st.success("Neo posted!")
            elif "pending" in out.lower():
                st.warning("Neo queue empty — approve more content.")
            else:
                st.error(f"Failed: {out[-300:]}")

        if st.button("⚡ Post Shay Now", key="post_shay"):
            with st.spinner("Posting to Shay..."):
                out = post_now("shay")
            if "SUCCESS" in out:
                st.success("Shay posted!")
            elif "pending" in out.lower():
                st.warning("Shay queue empty — approve more content.")
            else:
                st.error(f"Failed: {out[-300:]}")

        if st.button("⚡ Post Ty Now", key="post_ty"):
            with st.spinner("Posting to Ty..."):
                out = post_now("ty")
            if "SUCCESS" in out:
                st.success("Ty posted!")
            elif "pending" in out.lower():
                st.warning("Ty queue empty — approve more content.")
            else:
                st.error(f"Failed: {out[-300:]}")

        if st.button("⚡ Post ALL Now", key="post_all", type="primary"):
            with st.spinner("Posting to all accounts..."):
                out = post_now("all")
            st.code(out, language=None)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Open Dashboards</div>', unsafe_allow_html=True)
        st.link_button("Open Content Dashboard →", "http://localhost:8502", use_container_width=True)
        st.link_button("Open CreateFlow Platform →", "http://localhost:8501", use_container_width=True)

    with qa2:
        st.markdown('<div class="section-hdr">Deployment Status</div>', unsafe_allow_html=True)

        deploy_items = [
            ("B2C Funnel",       "createnow.streamlit.app → b2c.vlmcreateflow.com",  True),
            ("B2B Funnel",       "vlmforbusiness.streamlit.app → b2b.vlmcreateflow.com", True),
            ("CRM",              "vlmcreator.streamlit.app → crm.vlmcreateflow.com", True),
            ("Funnel Router",    "flowleads.streamlit.app → vlmcreateflow.com",      True),
            ("Stripe",           "B2B $997 + B2C $49 — payment links live",          True),
            ("Lead Sourcing",    f"{outreach_total} leads in pipeline",               outreach_total > 0),
            ("Outreach Bot",     f"{outreach_sent} emails sent — daily cron 9AM",     outreach_sent > 0),
            ("Neo IG Session",   "Needs fresh login",                                 False),
            ("Shay auto-poster", "Live ✓",                                            True),
            ("Ty auto-poster",   "Live ✓",                                            True),
        ]

        for item, note, done in deploy_items:
            icon  = "🟢" if done else "🔴"
            color = "#00ff80" if done else "#ff5050"
            note_color = "#224422" if done else "#334455"
            st.markdown(f"""
            <div class="stage-bar">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <span style="color:{color};font-size:0.8rem;">{icon} {item}</span>
                        <div style="color:{note_color};font-size:0.7rem;margin-top:2px;">{note}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-hdr">Credentials</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="stage-bar">
            <div style="color:#445566;font-size:0.75rem;">CRM Password</div>
            <div style="font-family:'Share Tech Mono',monospace;color:#ffc800;font-size:0.9rem;margin-top:4px;">VLM5BA2C052</div>
        </div>
        <div class="stage-bar">
            <div style="color:#445566;font-size:0.75rem;">CRM Login</div>
            <div style="font-family:'Share Tech Mono',monospace;color:#ffc800;font-size:0.9rem;margin-top:4px;">admin / VLM5BA2C052</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("↻ Refresh All Data"):
            st.cache_data.clear()
            st.rerun()
