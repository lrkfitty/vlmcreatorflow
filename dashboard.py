"""
VLM Mission Control Dashboard
CreateFlow Ecosystem — Cyberpunk Command Center
Port: 8502
"""

import streamlit as st
import os
import json
import glob
import base64
from datetime import datetime, date
from pathlib import Path
from io import BytesIO

# ── env vars ──────────────────────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=Path(__file__).parent / ".env")
except ImportError:
    pass

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ── constants ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
OUTPUT_USERS = PROJECT_ROOT / "output" / "users"
NEO_IG = PROJECT_ROOT / "output" / "users" / "Neo" / "Instagram"
SHAY_IG = PROJECT_ROOT / "output" / "users" / "Shay" / "Instagram"
TYRIE_IG = PROJECT_ROOT / "output" / "users" / "Tyrie" / "Instagram"
ASSETS_ROOT = PROJECT_ROOT / "assets" / "AI Content Creators"
NEO_ASSETS = ASSETS_ROOT / "Friends" / "Mens Friends"
SHAY_ASSETS = ASSETS_ROOT / "Shay.So.Fine"
TYRIE_ASSETS = ASSETS_ROOT / "Friends" / "Tyrie Master"
ACTIVITY_LOG = PROJECT_ROOT / ".tmp" / "activity_log.json"
CAMPAIGN_JSON = PROJECT_ROOT / "current_campaign.json"
APPROVED_FILE = PROJECT_ROOT / ".tmp" / "approved_posts.json"
TYRIE_SCHEDULE = PROJECT_ROOT / ".tmp" / "tyrie_schedule.json"
TYRIE_LOG = PROJECT_ROOT / ".tmp" / "tyrie_post_log.json"

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="VLM Mission Control",
    page_icon="⚡",
    initial_sidebar_state="collapsed",
)

# ── cyberpunk CSS ─────────────────────────────────────────────────────────────
CYBER_CSS = """
<style>
/* === GLOBAL RESET === */
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@400;600;700&display=swap');

html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #0a0a0f !important;
    color: #c8d6e5 !important;
}

[data-testid="stSidebar"] {
    background-color: #0d0d15 !important;
    border-right: 1px solid rgba(0,255,255,0.15) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #00ffff44; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #00ffff88; }

/* === TYPOGRAPHY === */
h1, h2, h3, .cyber-header {
    font-family: 'Share Tech Mono', monospace !important;
    letter-spacing: 0.08em;
    font-size: 1.6em !important;
    font-weight: 800 !important;
}
h1 { font-size: 2.4em !important; }
h2 { font-size: 1.8em !important; }
h3 { font-size: 1.5em !important; }
body, p, div, span, label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 16px;
    font-weight: 500;
}
/* Streamlit overrides for bolder text */
.stMarkdown p, .stMarkdown div { font-size: 16px !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; }
button[kind="primary"], button[kind="secondary"], .stButton button {
    font-weight: 700 !important;
    font-size: 14px !important;
    border-radius: 12px !important;
    letter-spacing: 0.04em;
}

/* === CARDS === */
.cyber-card {
    background: #12121a;
    border: 1px solid rgba(0,255,255,0.2);
    border-radius: 16px;
    padding: 20px 24px;
    margin-bottom: 14px;
    position: relative;
    overflow: hidden;
}
.cyber-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00ffff, transparent);
    opacity: 0.6;
}
.cyber-card-magenta {
    border-color: rgba(255,0,255,0.3) !important;
}
.cyber-card-magenta::before {
    background: linear-gradient(90deg, transparent, #ff00ff, transparent) !important;
}
.cyber-card-green {
    border-color: rgba(0,255,136,0.3) !important;
}
.cyber-card-green::before {
    background: linear-gradient(90deg, transparent, #00ff88, transparent) !important;
}
.cyber-card-orange {
    border-color: rgba(255,170,0,0.3) !important;
}
.cyber-card-orange::before {
    background: linear-gradient(90deg, transparent, #ffaa00, transparent) !important;
}

/* === STATUS BAR === */
.status-bar {
    background: #0d0d17;
    border: 1px solid rgba(0,255,255,0.25);
    border-radius: 16px;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 24px;
    flex-wrap: wrap;
    margin-bottom: 20px;
}
.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.05em;
    padding: 6px 14px;
    border-radius: 10px;
    background: rgba(0,0,0,0.3);
}
.dot-online  { color: #00ff88; text-shadow: 0 0 8px #00ff88; }
.dot-offline { color: #ff3366; text-shadow: 0 0 8px #ff3366; }
.dot-warn    { color: #ffaa00; text-shadow: 0 0 8px #ffaa00; }

/* === SECTION HEADERS === */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #00ffff;
    text-shadow: 0 0 15px rgba(0,255,255,0.6);
    border-bottom: 2px solid rgba(0,255,255,0.3);
    padding-bottom: 10px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

/* === IG GRID === */
.ig-grid-item {
    background: #12121a;
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 14px;
    overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
    margin-bottom: 8px;
}
.ig-grid-item:hover {
    border-color: rgba(0,255,255,0.5);
    box-shadow: 0 0 12px rgba(0,255,255,0.15);
}
.ig-caption {
    padding: 10px 14px;
    font-size: 15px;
    font-weight: 600;
    color: #99aabb;
    font-family: 'Rajdhani', sans-serif;
    line-height: 1.5;
    max-height: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* === STAT BADGES === */
.stat-box {
    background: #0d0d17;
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 14px;
    padding: 16px 20px;
    text-align: center;
}
.stat-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 36px;
    font-weight: 900;
    color: #00ffff;
    text-shadow: 0 0 15px rgba(0,255,255,0.4);
    display: block;
}
.stat-label {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #667788;
    display: block;
    margin-top: 2px;
}

/* === LOG ENTRIES === */
.log-entry {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    padding: 10px 12px;
    margin-bottom: 4px;
    border-bottom: 1px solid rgba(255,255,255,0.04);
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    font-family: 'Share Tech Mono', monospace;
}
.log-entry:hover { background: rgba(0,255,255,0.03); }
.log-ts { color: #556677; min-width: 150px; font-weight: 500; }
.log-action { color: #00ffff; min-width: 140px; font-weight: 800; }
.log-detail { color: #aabbcc; flex: 1; font-weight: 500; }
.log-status-success { color: #00ff88; min-width: 80px; text-align: right; font-weight: 800; }
.log-status-failed  { color: #ff3366; min-width: 80px; text-align: right; font-weight: 800; }
.log-status-pending { color: #ffaa00; min-width: 80px; text-align: right; font-weight: 800; }

/* === STATUS BADGE === */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 10px;
    font-size: 13px;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 0.06em;
    font-weight: 800;
}
.badge-ready     { background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid rgba(0,255,136,0.3); }
.badge-posted    { background: rgba(0,128,255,0.15); color: #0088ff; border: 1px solid rgba(0,128,255,0.3); }
.badge-scheduled { background: rgba(255,170,0,0.15); color: #ffaa00; border: 1px solid rgba(255,170,0,0.3); }
.badge-approved  { background: rgba(0,255,255,0.15); color: #00ffff; border: 1px solid rgba(0,255,255,0.3); }

/* === COMING SOON === */
.coming-soon {
    background: #0d0d17;
    border: 1px dashed rgba(255,0,255,0.2);
    border-radius: 14px;
    padding: 28px;
    text-align: center;
    color: #556677;
    font-family: 'Share Tech Mono', monospace;
    font-size: 15px;
    font-weight: 700;
    letter-spacing: 0.1em;
}
.coming-soon-value {
    font-size: 32px;
    color: #223344;
    display: block;
    margin-bottom: 6px;
    text-shadow: 0 0 8px rgba(255,0,255,0.1);
}

/* === ASSET THUMBNAIL === */
.asset-thumb {
    background: #12121a;
    border: 1px solid rgba(255,0,255,0.15);
    border-radius: 12px;
    padding: 8px;
    text-align: center;
    font-size: 13px;
    font-weight: 600;
    color: #778899;
    font-family: 'Share Tech Mono', monospace;
    overflow: hidden;
}
.asset-count-chip {
    background: rgba(255,0,255,0.1);
    border: 1px solid rgba(255,0,255,0.2);
    color: #ff00ff;
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 10px;
    display: inline-block;
}

/* === PIPELINE ITEM === */
.pipeline-item {
    background: #0f0f1a;
    border-left: 3px solid #00ffff;
    padding: 8px 12px;
    margin-bottom: 6px;
    font-family: 'Rajdhani', sans-serif;
    font-size: 13px;
}
.pipeline-item-failed  { border-left-color: #ff3366 !important; }
.pipeline-item-pending { border-left-color: #ffaa00 !important; }

/* === STREAMLIT OVERRIDES === */
.stButton > button {
    background: transparent !important;
    border: 1px solid rgba(0,255,255,0.4) !important;
    color: #00ffff !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.08em !important;
    padding: 4px 14px !important;
    border-radius: 2px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: rgba(0,255,255,0.1) !important;
    border-color: #00ffff !important;
    box-shadow: 0 0 8px rgba(0,255,255,0.2) !important;
}
[data-testid="stMarkdown"] h1 {
    font-family: 'Share Tech Mono', monospace !important;
    color: #00ffff !important;
    text-shadow: 0 0 20px rgba(0,255,255,0.3);
}
[data-testid="stMarkdown"] h2 {
    font-family: 'Share Tech Mono', monospace !important;
    color: #cc88ff !important;
}
[data-testid="stMarkdown"] h3 {
    font-family: 'Share Tech Mono', monospace !important;
    color: #00ff88 !important;
    font-size: 14px !important;
}
.stTabs [data-baseweb="tab-list"] {
    background: #0d0d17 !important;
    border-bottom: 1px solid rgba(0,255,255,0.15) !important;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    color: #445566 !important;
    letter-spacing: 0.08em !important;
    background: transparent !important;
    border: none !important;
    padding: 8px 16px !important;
}
.stTabs [aria-selected="true"] {
    color: #00ffff !important;
    border-bottom: 2px solid #00ffff !important;
    text-shadow: 0 0 8px rgba(0,255,255,0.4) !important;
}
[data-testid="stMetric"] {
    background: #12121a;
    border: 1px solid rgba(0,255,255,0.15);
    border-radius: 4px;
    padding: 12px !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Share Tech Mono', monospace !important;
    color: #00ffff !important;
    font-size: 24px !important;
}
[data-testid="stMetricLabel"] {
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 11px !important;
    color: #445566 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
div[data-testid="column"] { gap: 8px; }
.stDivider { border-color: rgba(0,255,255,0.1) !important; }

/* === HEADER GLOW === */
.main-title {
    font-family: 'Share Tech Mono', monospace;
    font-size: 28px;
    color: #00ffff;
    text-shadow: 0 0 30px rgba(0,255,255,0.6), 0 0 60px rgba(0,255,255,0.2);
    letter-spacing: 0.15em;
}
.main-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #334455;
    letter-spacing: 0.2em;
    text-transform: uppercase;
}

/* === SCAN LINE EFFECT === */
.scanline {
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0,0,0,0.03) 2px,
        rgba(0,0,0,0.03) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* image fills */
.ig-img-wrap img { width: 100%; height: auto; max-height: 450px; object-fit: contain; display: block; cursor: pointer; }
.ig-img-wrap img:hover { opacity: 0.9; }

/* Lightbox overlay */
.lightbox-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: rgba(0,0,0,0.92); z-index: 99999;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
}
.lightbox-overlay img {
    max-width: 90vw; max-height: 90vh; object-fit: contain;
    border: 1px solid rgba(0,255,255,0.3); border-radius: 4px;
    box-shadow: 0 0 40px rgba(0,255,255,0.15);
}
</style>
<div class="scanline"></div>
"""

st.markdown(CYBER_CSS, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def img_to_b64(path: Path, max_dim: int = 800):
    if not path.exists():
        return None
    try:
        if PIL_AVAILABLE:
            img = Image.open(path)
            img.thumbnail((max_dim, max_dim))
            buf = BytesIO()
            fmt = "JPEG"
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(buf, format=fmt, quality=90)
            return base64.b64encode(buf.getvalue()).decode()
        else:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def img_to_b64_full(path: Path):
    """Full resolution base64 for lightbox view."""
    if not path.exists():
        return None
    try:
        if PIL_AVAILABLE:
            img = Image.open(path)
            img.thumbnail((1600, 1600))
            buf = BytesIO()
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(buf, format="JPEG", quality=92)
            return base64.b64encode(buf.getvalue()).decode()
        else:
            with open(path, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        return None


def load_json(path: Path, default=None):
    if default is None:
        default = []
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default


def ensure_activity_log():
    log_dir = PROJECT_ROOT / ".tmp"
    log_dir.mkdir(exist_ok=True)
    if not ACTIVITY_LOG.exists():
        with open(ACTIVITY_LOG, "w") as f:
            json.dump([
                {
                    "timestamp": datetime.now().isoformat(),
                    "action": "SYSTEM_START",
                    "details": "VLM Mission Control dashboard initialized",
                    "status": "success"
                }
            ], f, indent=2)


def load_approved():
    data = load_json(APPROVED_FILE, default={})
    if isinstance(data, list):
        return {}
    return data


def save_approved(data: dict):
    APPROVED_FILE.parent.mkdir(exist_ok=True)
    with open(APPROVED_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_neo_ig_posts():
    """Return list of (img_path, caption, base_name) tuples for Neo IG."""
    posts = []
    if not NEO_IG.exists():
        return posts
    imgs = sorted(
        [f for f in NEO_IG.glob("*.jpg") if "_thumb" not in f.name],
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for img in imgs:
        stem = img.stem
        caption_path = NEO_IG / f"{stem}_caption.txt"
        caption = ""
        if caption_path.exists():
            caption = caption_path.read_text(encoding="utf-8").strip()
        posts.append((img, caption, stem))
    return posts


def count_images_in(folder: Path) -> int:
    if not folder.exists():
        return 0
    return len([f for f in folder.rglob("*") if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")])


def get_all_user_images():
    imgs = []
    if not OUTPUT_USERS.exists():
        return imgs
    for user_dir in sorted(OUTPUT_USERS.iterdir()):
        if not user_dir.is_dir() or user_dir.name.startswith("."):
            continue
        for img in sorted(user_dir.rglob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True)[:6]:
            if "_thumb" not in img.name:
                imgs.append((img, user_dir.name))
    return imgs


def today_image_count() -> int:
    today = date.today()
    count = 0
    if not OUTPUT_USERS.exists():
        return 0
    for img in OUTPUT_USERS.rglob("*.jpg"):
        try:
            if date.fromtimestamp(img.stat().st_mtime) == today:
                count += 1
        except Exception:
            pass
    return count


# ══════════════════════════════════════════════════════════════════════════════
#  ENV CHECK
# ══════════════════════════════════════════════════════════════════════════════

INTEGRATIONS = {
    "INSTAGRAM":  ["INSTAGRAM_ACCESS_TOKEN", "INSTAGRAM_BUSINESS_ACCOUNT_ID"],
    "GEMINI":     ["GOOGLE_AI_API_KEY", "GEMINI_API_KEY"],
    "REPLICATE":  ["REPLICATE_API_TOKEN"],
    "S3":         ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "S3_BUCKET_NAME"],
    "OPENAI":     ["OPENAI_API_KEY"],
}


def check_integration(keys: list[str]) -> str:
    """Returns 'online', 'offline', or 'warn'."""
    found = [k for k in keys if os.getenv(k)]
    if len(found) == len(keys):
        return "online"
    elif len(found) > 0:
        return "warn"
    return "offline"


# ══════════════════════════════════════════════════════════════════════════════
#  INIT
# ══════════════════════════════════════════════════════════════════════════════

ensure_activity_log()
approved = load_approved()

# ══════════════════════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════════════════════

col_logo, col_title, col_clock = st.columns([1, 6, 2])
with col_logo:
    st.markdown(
        "<div style='font-size:48px;text-align:center;line-height:1;padding-top:8px;"
        "text-shadow:0 0 20px rgba(0,255,255,0.8);'>⚡</div>",
        unsafe_allow_html=True,
    )
with col_title:
    st.markdown(
        "<div class='main-title'>VLM MISSION CONTROL</div>"
        "<div class='main-sub'>CreateFlow Ecosystem · Autonomous Content Operations</div>",
        unsafe_allow_html=True,
    )
with col_clock:
    now = datetime.now()
    st.markdown(
        f"<div style='font-family:Share Tech Mono,monospace;font-size:22px;color:#00ffff;"
        f"text-align:right;text-shadow:0 0 10px rgba(0,255,255,0.4);padding-top:4px;'>"
        f"{now.strftime('%H:%M:%S')}</div>"
        f"<div style='font-family:Share Tech Mono,monospace;font-size:11px;color:#334455;"
        f"text-align:right;letter-spacing:0.1em;'>{now.strftime('%Y-%m-%d · UTC+7')}</div>",
        unsafe_allow_html=True,
    )

st.markdown("<hr style='border-color:rgba(0,255,255,0.1);margin:8px 0 16px 0;'>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 1: SYSTEM STATUS BAR
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(
    "<div class='section-header'>◈ SYSTEM STATUS · INTEGRATION HEALTH</div>",
    unsafe_allow_html=True,
)

status_cols = st.columns(len(INTEGRATIONS) + 2)
status_html = ""
dot_icons = {"online": "●", "warn": "◐", "offline": "○"}
dot_classes = {"online": "dot-online", "warn": "dot-warn", "offline": "dot-offline"}
dot_labels  = {"online": "ONLINE", "warn": "PARTIAL", "offline": "OFFLINE"}

for i, (name, keys) in enumerate(INTEGRATIONS.items()):
    state = check_integration(keys)
    with status_cols[i]:
        st.markdown(
            f"<div class='cyber-card' style='padding:10px 14px;text-align:center;'>"
            f"<span class='{dot_classes[state]}' style='font-size:18px;'>{dot_icons[state]}</span><br>"
            f"<span style='font-family:Share Tech Mono,monospace;font-size:10px;letter-spacing:0.1em;"
            f"color:#aabbcc;'>{name}</span><br>"
            f"<span style='font-family:Share Tech Mono,monospace;font-size:9px;color:#334455;'>"
            f"{dot_labels[state]}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

with status_cols[-2]:
    neo_ig_count = len(get_neo_ig_posts())
    st.markdown(
        f"<div class='cyber-card cyber-card-green' style='padding:10px 14px;text-align:center;'>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:18px;color:#00ff88;'>◉</span><br>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:10px;letter-spacing:0.1em;color:#aabbcc;'>"
        f"PIPELINE</span><br>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:9px;color:#00ff88;'>{neo_ig_count} READY</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

with status_cols[-1]:
    st.markdown(
        f"<div class='cyber-card cyber-card-magenta' style='padding:10px 14px;text-align:center;'>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:18px;color:#ff00ff;'>▣</span><br>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:10px;letter-spacing:0.1em;color:#aabbcc;'>"
        f"DASHBOARD</span><br>"
        f"<span style='font-family:Share Tech Mono,monospace;font-size:9px;color:#ff00ff;'>LIVE</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════════════════════

tab_neo, tab_shay, tab_tyrie, tab_pipeline, tab_log, tab_gtm, tab_assets = st.tabs([
    "⚡ NEO INSTAGRAM",
    "💎 SHAY INSTAGRAM",
    "◭ TY INSTAGRAM",
    "◈ CONTENT PIPELINE",
    "▣ ACTIVITY LOG",
    "◐ GTM STACK",
    "◉ ASSET BROWSER",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1: NEO INSTAGRAM PANEL
# ══════════════════════════════════════════════════════════════════════════════

with tab_neo:
    st.markdown(
        "<div class='section-header'>⚡ NEO · INSTAGRAM COMMAND</div>",
        unsafe_allow_html=True,
    )

    # Stats row
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(
            "<div class='stat-box'>"
            "<span class='stat-value'>—</span>"
            "<span class='stat-label'>Followers</span>"
            "</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[1]:
        posts = get_neo_ig_posts()
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ff00ff;text-shadow:0 0 15px rgba(255,0,255,0.4);'>{len(posts)}</span>"
            f"<span class='stat-label'>Posts Ready</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[2]:
        approved_count = sum(1 for k, v in approved.items() if v)
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#00ff88;text-shadow:0 0 15px rgba(0,255,136,0.4);'>{approved_count}</span>"
            f"<span class='stat-label'>Approved</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[3]:
        st.markdown(
            "<div class='stat-box'>"
            "<span class='stat-value' style='color:#ffaa00;text-shadow:0 0 15px rgba(255,170,0,0.4);'>—</span>"
            "<span class='stat-label'>Engagement %</span>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    posts = get_neo_ig_posts()
    if not posts:
        st.markdown(
            "<div class='coming-soon'>"
            "<span class='coming-soon-value'>📷</span>"
            "No images found in output/users/Neo/Instagram/"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        # View mode toggle
        view_mode = st.radio("View", ["Grid (3-col)", "Large (1-col)"], horizontal=True, key="neo_view_mode", label_visibility="collapsed")

        if view_mode == "Large (1-col)":
            # Full-size single column view
            for idx, (img_path, caption, stem) in enumerate(posts):
                is_approved = approved.get(stem, False)
                status_label = "APPROVED" if is_approved else "READY"
                badge_class = "badge-approved" if is_approved else "badge-ready"

                st.markdown(
                    f"<div style='margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;'>"
                    f"<span class='badge {badge_class}'>{status_label}</span>"
                    f"<span style='font-size:11px;color:#556677;font-family:Share Tech Mono,monospace;'>Post {idx+1} · {stem[-12:]}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                st.image(str(img_path), use_container_width=True)
                if caption:
                    st.markdown(
                        f"<div style='padding:8px 4px 4px;color:#8899aa;font-size:13px;line-height:1.5;'>{caption}</div>",
                        unsafe_allow_html=True,
                    )
                btn_label = "✓ APPROVED" if is_approved else "APPROVE"
                if st.button(btn_label, key=f"approve_large_{stem}"):
                    approved[stem] = not is_approved
                    save_approved(approved)
                    st.rerun()
                st.markdown("<hr style='border-color:rgba(0,255,255,0.1);margin:20px 0;'>", unsafe_allow_html=True)
        else:
            # 3-col grid
            grid_cols = st.columns(3)
            for idx, (img_path, caption, stem) in enumerate(posts):
                col = grid_cols[idx % 3]
                with col:
                    is_approved = approved.get(stem, False)
                    b64 = img_to_b64(img_path)
                    status_label = "APPROVED" if is_approved else "READY"
                    badge_class  = "badge-approved" if is_approved else "badge-ready"
                    caption_short = caption[:120] + "…" if len(caption) > 120 else caption

                    img_html = (
                        f'<img src="data:image/jpeg;base64,{b64}" '
                        f'style="width:100%;height:auto;max-height:350px;object-fit:contain;display:block;">'
                    ) if b64 else '<div style="height:200px;background:#1a1a2a;display:flex;align-items:center;justify-content:center;color:#334455;">NO IMAGE</div>'

                    no_caption_html = '<em style="color:#334455;">No caption</em>'
                    caption_div = f"<div class='ig-caption'>{caption_short if caption_short else no_caption_html}</div>"
                    st.markdown(
                        f"<div class='ig-grid-item'>"
                        f"<div class='ig-img-wrap'>{img_html}</div>"
                        f"{caption_div}"
                        f"<div style='padding:6px 10px;display:flex;justify-content:space-between;align-items:center;'>"
                        f"<span class='badge {badge_class}'>{status_label}</span>"
                        f"<span style='font-size:10px;color:#334455;font-family:Share Tech Mono,monospace;'>{stem[-8:]}</span>"
                        f"</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                    # Expander to see full image
                    with st.expander(f"🔍 View full"):
                        st.image(str(img_path), use_container_width=True)
                        if caption:
                            st.caption(caption)

                    btn_label = "✓ APPROVED" if is_approved else "APPROVE"
                    if st.button(btn_label, key=f"approve_{stem}"):
                        approved[stem] = not is_approved
                        save_approved(approved)
                        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2: SHAY INSTAGRAM PANEL
# ══════════════════════════════════════════════════════════════════════════════

def get_shay_ig_posts():
    if not SHAY_IG.exists():
        return []
    posts = [
        (f, f.stem)
        for f in sorted(SHAY_IG.glob("*.jpg"), reverse=True)
        if "_thumb" not in f.name and "_carousel" not in f.name
    ]
    result = []
    for img_path, stem in posts:
        caption_path = SHAY_IG / f"{stem}_caption.txt"
        caption = caption_path.read_text().strip() if caption_path.exists() else ""
        result.append((img_path, caption, stem))
    return result

with tab_shay:
    st.markdown(
        "<div class='section-header'>💎 SHAY · INSTAGRAM COMMAND</div>",
        unsafe_allow_html=True,
    )
    
    # Load Shay schedule
    shay_schedule_path = PROJECT_ROOT / ".tmp" / "shay_schedule.json"
    shay_schedule = load_json(shay_schedule_path, default=[])
    
    # Count approvals
    approved_data = load_approved()
    shay_approvals = approved_data.get("shay", {})
    approved_count = sum(1 for post in shay_schedule if post.get("carousel_id") in shay_approvals)
    
    posts = get_shay_ig_posts()
    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>150</span><span class='stat-label'>Followers</span></div>", unsafe_allow_html=True)
    with stat_cols[1]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>{approved_count}/{len(shay_schedule)}</span><span class='stat-label'>Approved</span></div>", unsafe_allow_html=True)
    with stat_cols[2]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>17.2%</span><span class='stat-label'>Engagement</span></div>", unsafe_allow_html=True)
    with stat_cols[3]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>30</span><span class='stat-label'>Scheduled</span></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Approval interface
    st.markdown(
        "<div class='section-header' style='font-size:12px;margin-top:20px;'>💫 30-DAY CAROUSEL APPROVAL</div>",
        unsafe_allow_html=True,
    )
    
    if not shay_schedule:
        st.markdown("<div class='coming-soon'><span class='coming-soon-value'>📋</span>No carousel schedule found</div>", unsafe_allow_html=True)
    else:
        # Filter by status
        filter_status = st.radio(
            "Filter",
            ["All", "Pending", "Approved"],
            horizontal=True,
            key="shay_filter_status",
            label_visibility="collapsed"
        )
        
        for post in shay_schedule:
            carousel_id = post.get("carousel_id")
            day = post.get("day")
            date_str = post.get("date")
            caption = post.get("caption", "")
            images = post.get("images", [])
            is_approved = carousel_id in shay_approvals
            
            # Filter logic
            if filter_status == "Pending" and is_approved:
                continue
            if filter_status == "Approved" and not is_approved:
                continue
            
            badge_class = "badge-approved" if is_approved else "badge-pending"
            status_label = "✓ APPROVED" if is_approved else "⊙ PENDING"
            
            # Carousel card
            st.markdown(
                f"<div style='background:rgba(255,0,255,0.05);border:1px solid rgba(255,0,255,0.2);border-radius:4px;padding:12px;margin-bottom:12px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                f"<span style='color:#00ffff;font-family:Share Tech Mono;font-size:11px;'>Day {day} · {date_str}</span>"
                f"<span class='{badge_class}' style='padding:2px 8px;border-radius:2px;font-size:10px;'>{status_label}</span>"
                f"</div>"
                f"<div style='color:#aabbcc;font-size:13px;line-height:1.4;margin-bottom:10px;'>{caption[:150]}...</div>"
                f"<div style='color:#667788;font-size:11px;'>{len(images)} images in carousel</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            
            # Show carousel images
            if images:
                img_cols = st.columns(min(len(images), 4))
                for idx, img_path in enumerate(images[:4]):
                    with img_cols[idx]:
                        if Path(img_path).exists():
                            st.image(str(img_path), use_container_width=True)
            
            # Approval button
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                if not is_approved:
                    if st.button(f"✓ Approve", key=f"approve_{carousel_id}"):
                        shay_approvals[carousel_id] = {"approved_at": datetime.now().isoformat()}
                        approved_data["shay"] = shay_approvals
                        save_approved(approved_data)
                        st.success("Approved!")
                        st.rerun()
            with col3:
                if is_approved:
                    if st.button(f"✗ Reject", key=f"reject_{carousel_id}"):
                        if carousel_id in shay_approvals:
                            del shay_approvals[carousel_id]
                        approved_data["shay"] = shay_approvals
                        save_approved(approved_data)
                        st.info("Approval removed")
                        st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3: TYRIE INSTAGRAM
# ══════════════════════════════════════════════════════════════════════════════

def get_tyrie_carousels():
    """Return list of (carousel_id, [shot_paths], caption) for Tyrie IG.
    Scans main folder + couple/ subfolder."""
    if not TYRIE_IG.exists():
        return []
    carousels = []
    search_dirs = [TYRIE_IG, TYRIE_IG / "couple"]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for caption_path in sorted(search_dir.glob("*_caption.txt")):
            carousel_id = caption_path.stem.replace("_caption", "")
            caption = caption_path.read_text().strip()
            shot_paths = sorted(search_dir.glob(f"{carousel_id}_shot*.jpg"))
            if not shot_paths:
                single = search_dir / f"{carousel_id}.jpg"
                if single.exists():
                    shot_paths = [single]
            if shot_paths:
                carousels.append((carousel_id, shot_paths, caption))
    return carousels

with tab_tyrie:
    st.markdown(
        "<div class='section-header'>◭ TY · INSTAGRAM COMMAND · @tytheguyyttg</div>",
        unsafe_allow_html=True,
    )

    tyrie_carousels = get_tyrie_carousels()
    tyrie_approved  = load_json(PROJECT_ROOT / ".tmp" / "tyrie_approved.json", default={})
    tyrie_log       = load_json(TYRIE_LOG, default=[])

    approved_ty_count = sum(1 for cid, _, _ in tyrie_carousels if tyrie_approved.get(cid))

    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ff8800;text-shadow:0 0 15px rgba(255,136,0,0.4);'>—</span>"
            f"<span class='stat-label'>Followers</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[1]:
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ff00ff;text-shadow:0 0 15px rgba(255,0,255,0.4);'>{len(tyrie_carousels)}</span>"
            f"<span class='stat-label'>Posts Ready</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[2]:
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#00ff88;text-shadow:0 0 15px rgba(0,255,136,0.4);'>{approved_ty_count}</span>"
            f"<span class='stat-label'>Approved</span>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with stat_cols[3]:
        posted_ty = len(tyrie_log)
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ffaa00;text-shadow:0 0 15px rgba(255,170,0,0.4);'>{posted_ty}</span>"
            f"<span class='stat-label'>Posted</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-header' style='font-size:12px;margin-top:20px;'>◭ 30-DAY CAROUSEL APPROVAL</div>",
        unsafe_allow_html=True,
    )

    VIDEO_QUEUE_FILE = PROJECT_ROOT / ".tmp" / "tyrie_video_queue.json"
    video_queue = load_json(VIDEO_QUEUE_FILE, default={})
    tyrie_approved_save_path = PROJECT_ROOT / ".tmp" / "tyrie_approved.json"

    if not tyrie_carousels:
        st.markdown(
            "<div class='coming-soon'>"
            "<span class='coming-soon-value'>◭</span>"
            "No carousels yet — generation is running in the background."
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        filter_ty = st.radio(
            "Filter",
            ["All", "Pending", "Approved"],
            horizontal=True,
            key="tyrie_filter",
            label_visibility="collapsed",
        )

        for idx, (carousel_id, shot_paths, caption) in enumerate(tyrie_carousels):
            is_approved = bool(tyrie_approved.get(carousel_id))

            if filter_ty == "Pending" and is_approved:
                continue
            if filter_ty == "Approved" and not is_approved:
                continue

            badge_class  = "badge-approved" if is_approved else "badge-pending"
            status_label = "✓ APPROVED" if is_approved else "⊙ PENDING"
            vid_entry    = video_queue.get(carousel_id, {})

            # Carousel card header
            st.markdown(
                f"<div style='background:rgba(255,136,0,0.05);border:1px solid rgba(255,136,0,0.2);border-radius:4px;padding:12px;margin-bottom:8px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;'>"
                f"<span style='color:#00ffff;font-family:Share Tech Mono;font-size:11px;'>Post {idx+1} · {carousel_id}</span>"
                f"<span class='{badge_class}' style='padding:2px 8px;border-radius:2px;font-size:10px;'>{status_label}</span>"
                f"</div>"
                f"<div style='color:#aabbcc;font-size:13px;line-height:1.4;margin-bottom:10px;'>{caption[:150]}...</div>"
                f"<div style='color:#667788;font-size:11px;'>{len(shot_paths)} images in carousel</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Show all shots side by side with per-shot video button below each
            if shot_paths:
                img_cols = st.columns(min(len(shot_paths), 4))
                for i, sp in enumerate(shot_paths[:4]):
                    with img_cols[i]:
                        if Path(sp).exists():
                            st.image(str(sp), use_container_width=True)

                        shot_key   = str(sp)
                        # Queue may store relative or absolute path — match by filename
                        queued_shot = vid_entry.get("shot", "")
                        is_vid_sel = queued_shot == shot_key or Path(queued_shot).name == Path(shot_key).name
                        vid_status = vid_entry.get("status", "") if is_vid_sel else ""
                        vid_color  = {"approved": "#ffaa00", "generating": "#00ffff", "done": "#00ff88", "failed": "#ff4444"}.get(vid_status, "")

                        if vid_status == "done":
                            st.markdown(f"<div style='color:#00ff88;font-size:10px;font-family:Share Tech Mono;text-align:center;margin-bottom:4px;'>VIDEO READY</div>", unsafe_allow_html=True)
                            vid_path = vid_entry.get("video_path", "")
                            if vid_path and Path(vid_path).exists():
                                st.video(vid_path)
                        elif vid_status == "failed":
                            log_path = PROJECT_ROOT / ".tmp" / f"video_{carousel_id}.log"
                            err_hint = ""
                            if log_path.exists():
                                err_hint = log_path.read_text()[-300:]
                            st.markdown(f"<div style='color:#ff4444;font-size:10px;font-family:Share Tech Mono;text-align:center;'>FAILED</div>", unsafe_allow_html=True)
                            if err_hint:
                                st.code(err_hint, language=None)
                            if st.button("Retry", key=f"vid_retry_{carousel_id}_{i}"):
                                video_queue[carousel_id]["status"] = "approved"
                                VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                                st.rerun()
                        elif vid_status == "generating":
                            st.markdown(f"<div style='color:#00ffff;font-size:10px;font-family:Share Tech Mono;text-align:center;'>GENERATING...</div>", unsafe_allow_html=True)
                        elif vid_status == "approved":
                            st.markdown(f"<div style='color:#ffaa00;font-size:10px;font-family:Share Tech Mono;text-align:center;'>QUEUED FOR VIDEO</div>", unsafe_allow_html=True)
                            if st.button("Generate Now", key=f"vid_gen_{carousel_id}_{i}"):
                                import subprocess
                                video_queue[carousel_id]["status"] = "generating"
                                VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                                log_path = PROJECT_ROOT / ".tmp" / f"video_{carousel_id}.log"
                                log_path.parent.mkdir(exist_ok=True)
                                with open(log_path, "w") as log_f:
                                    subprocess.Popen([
                                        "python3", "execution/generate_video.py",
                                        "--image", shot_key,
                                        "--prompt", vid_entry.get("prompt", ""),
                                        "--carousel_id", carousel_id,
                                        "--queue_file", str(VIDEO_QUEUE_FILE),
                                        "--model_version", "3.0",
                                        "--output_folder", str(TYRIE_IG),
                                    ], cwd=str(PROJECT_ROOT), stdout=log_f, stderr=log_f)
                                st.rerun()
                        else:
                            if st.button(f"🎬 Make Video", key=f"vid_sel_{carousel_id}_{i}"):
                                with st.spinner("Director AI analyzing image..."):
                                    try:
                                        from execution.generate_video_prompt import generate_motion_prompt
                                        ai_prompt = generate_motion_prompt(
                                            image_path=shot_key,
                                            movement_type="Slow push in",
                                            physics_focus="High Physics",
                                            emotion="Confident",
                                            additional_context="AI content creator, personal brand, Bangkok lifestyle.",
                                        )
                                    except Exception as e:
                                        ai_prompt = f"Cinematic motion. Slow push in. Subject breathes naturally. Atmospheric light. Photorealistic. 5 seconds. Error generating AI prompt: {e}"
                                video_queue[carousel_id] = {
                                    "shot": shot_key,
                                    "shot_index": i,
                                    "status": "prompt_pending",
                                    "prompt": ai_prompt,
                                    "camera_move": "Slow push in",
                                    "physics": "High Physics",
                                    "emotion": "Confident",
                                    "video_path": "",
                                }
                                VIDEO_QUEUE_FILE.parent.mkdir(exist_ok=True)
                                VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                                st.rerun()

            # If a shot is selected for video but not yet approved, show director AI prompt editor
            if vid_entry.get("status") == "prompt_pending" and vid_entry.get("shot"):
                st.markdown(
                    "<div style='background:rgba(0,255,255,0.03);border:1px solid rgba(0,255,255,0.15);border-radius:4px;padding:14px;margin-top:8px;'>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='color:#00ffff;font-family:Share Tech Mono;font-size:11px;margin-bottom:10px;'>🎬 DIRECTOR AI — Shot {vid_entry.get('shot_index',0)+1}</div>",
                    unsafe_allow_html=True,
                )

                # Parameter controls
                param_c1, param_c2, param_c3 = st.columns(3)
                with param_c1:
                    camera_move = st.selectbox(
                        "Camera",
                        ["Slow push in", "Pull back", "Orbit left", "Orbit right", "Static locked", "Handheld drift", "Crane up", "Dutch tilt"],
                        index=["Slow push in", "Pull back", "Orbit left", "Orbit right", "Static locked", "Handheld drift", "Crane up", "Dutch tilt"].index(vid_entry.get("camera_move", "Slow push in")),
                        key=f"vid_cam_{carousel_id}",
                    )
                with param_c2:
                    physics = st.selectbox(
                        "Physics",
                        ["High Physics", "Jiggle", "Water/Liquids", "standard"],
                        index=["High Physics", "Jiggle", "Water/Liquids", "standard"].index(vid_entry.get("physics", "High Physics")),
                        key=f"vid_phys_{carousel_id}",
                    )
                with param_c3:
                    emotion = st.selectbox(
                        "Vibe",
                        ["Confident", "Neutral", "Intense", "Relaxed", "Mysterious", "Joyful"],
                        index=["Confident", "Neutral", "Intense", "Relaxed", "Mysterious", "Joyful"].index(vid_entry.get("emotion", "Confident")),
                        key=f"vid_emo_{carousel_id}",
                    )

                if st.button("↺ Regenerate Prompt", key=f"vid_regen_{carousel_id}"):
                    with st.spinner("Director AI regenerating..."):
                        try:
                            from execution.generate_video_prompt import generate_motion_prompt
                            ai_prompt = generate_motion_prompt(
                                image_path=vid_entry["shot"],
                                movement_type=camera_move,
                                physics_focus=physics,
                                emotion=emotion,
                                additional_context="AI content creator, personal brand, Bangkok lifestyle.",
                            )
                        except Exception as e:
                            ai_prompt = vid_entry.get("prompt", "")
                    video_queue[carousel_id]["prompt"]      = ai_prompt
                    video_queue[carousel_id]["camera_move"] = camera_move
                    video_queue[carousel_id]["physics"]     = physics
                    video_queue[carousel_id]["emotion"]     = emotion
                    VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                    st.rerun()

                new_prompt = st.text_area(
                    "Prompt (editable)",
                    value=vid_entry.get("prompt", ""),
                    height=160,
                    key=f"vid_prompt_{carousel_id}",
                    label_visibility="collapsed",
                )

                approve_col, cancel_col = st.columns(2)
                with approve_col:
                    if st.button("✓ Approve for Video", key=f"vid_approve_{carousel_id}"):
                        video_queue[carousel_id]["status"] = "approved"
                        video_queue[carousel_id]["prompt"] = new_prompt
                        VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                        st.rerun()
                with cancel_col:
                    if st.button("✗ Cancel", key=f"vid_cancel_{carousel_id}"):
                        video_queue.pop(carousel_id, None)
                        VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # Approve / Reject carousel buttons
            col1, col2, col3 = st.columns([3, 1, 1])
            with col2:
                if not is_approved:
                    if st.button("✓ Approve", key=f"ty_approve_{carousel_id}"):
                        tyrie_approved[carousel_id] = {"approved_at": datetime.now().isoformat()}
                        tyrie_approved_save_path.parent.mkdir(exist_ok=True)
                        tyrie_approved_save_path.write_text(json.dumps(tyrie_approved, indent=2))
                        st.success("Approved!")
                        st.rerun()
            with col3:
                if is_approved:
                    if st.button("✗ Reject", key=f"ty_reject_{carousel_id}"):
                        tyrie_approved.pop(carousel_id, None)
                        tyrie_approved_save_path.write_text(json.dumps(tyrie_approved, indent=2))
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4: CONTENT PIPELINE
# ══════════════════════════════════════════════════════════════════════════════

with tab_pipeline:
    st.markdown(
        "<div class='section-header'>◈ CONTENT PIPELINE · GENERATION STATUS</div>",
        unsafe_allow_html=True,
    )

    # quick stats
    all_user_imgs = get_all_user_images()
    total_imgs = sum(
        count_images_in(u) for u in OUTPUT_USERS.iterdir()
        if u.is_dir() and not u.name.startswith(".")
    ) if OUTPUT_USERS.exists() else 0
    today_imgs = today_image_count()

    stat_c = st.columns(4)
    with stat_c[0]:
        st.metric("TOTAL IMAGES", total_imgs)
    with stat_c[1]:
        st.metric("IMAGES TODAY", today_imgs)
    with stat_c[2]:
        users_count = len([
            u for u in OUTPUT_USERS.iterdir()
            if u.is_dir() and not u.name.startswith(".")
        ]) if OUTPUT_USERS.exists() else 0
        st.metric("ACTIVE USERS", users_count)
    with stat_c[3]:
        campaign = load_json(CAMPAIGN_JSON, default=[])
        completed = sum(1 for j in campaign if isinstance(j, dict) and j.get("status") == "completed") if campaign else 0
        st.metric("CAMPAIGN JOBS", completed)

    st.markdown("<br>", unsafe_allow_html=True)

    # Campaign queue — interactive job cards
    st.markdown(
        "<div class='section-header' style='font-size:11px;'>◈ CAMPAIGN QUEUE</div>",
        unsafe_allow_html=True,
    )
    campaign = load_json(CAMPAIGN_JSON, default=[])
    if campaign:
        try:
            from execution.campaign_runner import CampaignManager
            _mgr = CampaignManager()
        except Exception:
            _mgr = None

        for i, job in enumerate(campaign[:20]):
            if not isinstance(job, dict):
                continue
            job_status = job.get("status", "unknown")
            job_type   = job.get("type", "image")
            name       = job.get("name", job.get("id", "Unknown Job"))
            created    = job.get("created_at", "")
            companions = job.get("data", {}).get("extra_images", [])

            type_icon  = "🎬" if job_type == "reel" else "🎥" if "video" in job_type else "🖼️"
            status_icon = "✅" if job_status == "completed" else "❌" if job_status == "failed" else "⏳"
            cast_note   = f" · {len(companions)} cast" if companions else ""

            border_color = {
                "completed": "#00ff88",
                "failed":    "#ff3366",
                "pending":   "#ffaa00",
                "running":   "#00ccff",
            }.get(job_status, "#334455")

            with st.expander(f"{status_icon} {type_icon}  {name[:60]}  [{job_status.upper()}]{cast_note}"):
                st.caption(f"Created: {created[:19]}  ·  Type: {job_type}")

                # ── Reel results ──
                for r in job.get("results", []):
                    reel_path = r.get("reel_path")
                    if reel_path and os.path.exists(reel_path):
                        st.video(reel_path)
                        script = r.get("script", "")
                        dur    = r.get("duration", 0)
                        if script:
                            st.caption(f"🎙️ _{script[:200]}_  ({dur:.1f}s)")

                # ── Image results ──
                img_paths = [
                    r.get("image_path") for r in job.get("results", [])
                    if r.get("image_path") and os.path.exists(r.get("image_path", ""))
                ]
                if img_paths:
                    img_cols = st.columns(min(len(img_paths), 3))
                    for ci, ip in enumerate(img_paths[:3]):
                        with img_cols[ci]:
                            st.image(ip, use_container_width=True)
                            # QC badge
                            r = next((x for x in job.get("results", []) if x.get("image_path") == ip), {})
                            qc = r.get("qc")
                            if qc:
                                scores = qc.get("scores", {})
                                lap = scores.get("laplacian")
                                aes = scores.get("aesthetic_score")
                                if qc["pass"]:
                                    badge = "🟡 Review" if qc.get("needs_review") else "✅ QC Pass"
                                else:
                                    badge = f"❌ {qc.get('reason','Fail')[:40]}"
                                parts = [badge]
                                if lap is not None: parts.append(f"blur={lap:.0f}")
                                if aes is not None: parts.append(f"aes={aes:.2f}")
                                st.caption("  ·  ".join(parts))

                # ── Controls ──
                c1, c2, c3, c4 = st.columns([1, 1, 1, 4])
                with c1:
                    if i > 0 and _mgr and st.button("↑", key=f"pl_up_{i}"):
                        _mgr.move_job(i, -1); st.rerun()
                with c2:
                    if i < len(campaign) - 1 and _mgr and st.button("↓", key=f"pl_dn_{i}"):
                        _mgr.move_job(i, 1); st.rerun()
                with c3:
                    if job_status != "running" and _mgr and st.button("✕", key=f"pl_del_{i}"):
                        _mgr.remove_job(i); st.rerun()
    else:
        st.markdown(
            "<div class='coming-soon'>No jobs in queue — add from the Content creation tabs</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Recent images across all users
    st.markdown(
        "<div class='section-header' style='font-size:11px;'>◈ RECENT GENERATED IMAGES</div>",
        unsafe_allow_html=True,
    )
    all_imgs = get_all_user_images()
    if all_imgs:
        img_cols = st.columns(6)
        for i, (img_path, user) in enumerate(all_imgs[:12]):
            with img_cols[i % 6]:
                b64 = img_to_b64(img_path)
                if b64:
                    st.markdown(
                        f"<div style='background:#12121a;border:1px solid rgba(0,255,255,0.1);"
                        f"border-radius:4px;overflow:hidden;margin-bottom:4px;'>"
                        f"<img src='data:image/jpeg;base64,{b64}' "
                        f"style='width:100%;height:110px;object-fit:cover;display:block;'>"
                        f"<div style='padding:4px 6px;font-family:Share Tech Mono,monospace;"
                        f"font-size:9px;color:#334455;'>{user}</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            "<div class='coming-soon'>No user images found in output/users/</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3: ACTIVITY LOG
# ══════════════════════════════════════════════════════════════════════════════

with tab_log:
    st.markdown(
        "<div class='section-header'>▣ ACTIVITY LOG · SYSTEM EVENTS</div>",
        unsafe_allow_html=True,
    )

    log_data = load_json(ACTIVITY_LOG, default=[])

    ctrl_c1, ctrl_c2, ctrl_c3 = st.columns([4, 1, 1])
    with ctrl_c2:
        filter_status = st.selectbox("Filter", ["ALL", "success", "failed", "pending"], label_visibility="collapsed")
    with ctrl_c3:
        if st.button("↻ REFRESH"):
            st.rerun()

    if isinstance(log_data, list):
        entries = list(reversed(log_data))  # newest first
        if filter_status != "ALL":
            entries = [e for e in entries if e.get("status") == filter_status]

        if not entries:
            st.markdown(
                "<div class='coming-soon'>No log entries found.</div>",
                unsafe_allow_html=True,
            )
        else:
            log_html = "<div class='cyber-card' style='max-height:500px;overflow-y:auto;'>"
            for entry in entries[:100]:
                ts = entry.get("timestamp", "")[:19]
                action = entry.get("action", "UNKNOWN")
                detail = entry.get("details", "")
                status = entry.get("status", "pending")
                sc = {"success": "log-status-success", "failed": "log-status-failed"}.get(status, "log-status-pending")
                log_html += (
                    f"<div class='log-entry'>"
                    f"<span class='log-ts'>{ts}</span>"
                    f"<span class='log-action'>{action}</span>"
                    f"<span class='log-detail'>{detail[:100]}</span>"
                    f"<span class='{sc}'>{status.upper()}</span>"
                    f"</div>"
                )
            log_html += "</div>"
            st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='coming-soon'>Invalid log format.</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4: GTM STACK
# ══════════════════════════════════════════════════════════════════════════════

with tab_gtm:
    st.markdown(
        "<div class='section-header'>◐ GTM STACK · GO-TO-MARKET OPERATIONS</div>",
        unsafe_allow_html=True,
    )

    gtm_cols = st.columns(3)
    gtm_modules = [
        ("LEADS ENGINE", "Total prospects identified and scraped from target niches", "◈", "#00ffff"),
        ("OUTREACH AUTOMATION", "AI-powered cold DM + email sequences across platforms", "▣", "#ff00ff"),
        ("INBOX MONITOR", "Unified reply tracking across IG, email, and LinkedIn", "◉", "#00ff88"),
        ("CRM PIPELINE", "Deal stages: Aware → Interested → Demo → Closed", "◐", "#ffaa00"),
        ("AD CREATIVES", "Performance tracking for paid social campaigns", "⬡", "#cc88ff"),
        ("ANALYTICS", "Revenue attribution and conversion tracking", "△", "#00ffff"),
    ]

    for i, (title, desc, icon, color) in enumerate(gtm_modules):
        with gtm_cols[i % 3]:
            st.markdown(
                f"<div class='cyber-card' style='border-color:rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.25);min-height:140px;'>"
                f"<div style='font-family:Share Tech Mono,monospace;font-size:10px;"
                f"letter-spacing:0.1em;color:{color};margin-bottom:8px;'>{icon} {title}</div>"
                f"<div style='font-size:12px;color:#445566;line-height:1.5;margin-bottom:12px;'>{desc}</div>"
                f"<div class='coming-soon' style='padding:8px;border-color:rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.15);'>"
                f"<span style='font-size:10px;'>⚠ COMING SOON</span>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Placeholder stats
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header' style='font-size:11px;'>◈ PLACEHOLDER METRICS (WIRES ONLY)</div>",
        unsafe_allow_html=True,
    )
    ph_cols = st.columns(4)
    ph_data = [
        ("LEADS", "—", "#00ffff"),
        ("OUTREACH SENT", "—", "#ff00ff"),
        ("REPLIES", "—", "#00ff88"),
        ("DEMOS BOOKED", "—", "#ffaa00"),
    ]
    for j, (label, val, color) in enumerate(ph_data):
        with ph_cols[j]:
            st.markdown(
                f"<div class='stat-box'>"
                f"<span class='stat-value' style='color:{color};text-shadow:0 0 15px {color}44;'>{val}</span>"
                f"<span class='stat-label'>{label}</span>"
                f"</div>",
                unsafe_allow_html=True,
            )


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5: ASSET BROWSER
# ══════════════════════════════════════════════════════════════════════════════

with tab_assets:
    st.markdown(
        "<div class='section-header'>◉ ASSET BROWSER · CHARACTER LIBRARY</div>",
        unsafe_allow_html=True,
    )

    # ── Neo highlight ──────────────────────────────────────────────────────────
    neo_col, info_col = st.columns([1, 2])

    neo_png = NEO_ASSETS / "Neo.png"
    with neo_col:
        b64 = img_to_b64(neo_png)
        if b64:
            st.markdown(
                f"<div style='background:#12121a;border:2px solid rgba(0,255,255,0.3);"
                f"border-radius:4px;padding:8px;box-shadow:0 0 20px rgba(0,255,255,0.1);'>"
                f"<img src='data:image/png;base64,{b64}' style='width:100%;max-height:300px;object-fit:contain;'>"
                f"<div style='text-align:center;font-family:Share Tech Mono,monospace;"
                f"font-size:11px;color:#00ffff;padding-top:8px;letter-spacing:0.1em;'>NEO.PNG</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='coming-soon'><span class='coming-soon-value'>👤</span>Neo.png not found</div>",
                unsafe_allow_html=True,
            )

    with info_col:
        st.markdown(
            "<div class='cyber-card cyber-card-green'>"
            "<div style='font-family:Share Tech Mono,monospace;font-size:14px;"
            "color:#00ffff;letter-spacing:0.1em;margin-bottom:12px;'>⚡ NEO — CHARACTER PROFILE</div>"
            "<div style='font-size:13px;color:#aabbcc;line-height:1.8;'>"
            "Name: <span style='color:#00ffff;'>Neo</span><br>"
            "Handle: <span style='color:#ff00ff;'>@neoismyname1</span><br>"
            "Platform: <span style='color:#00ff88;'>Instagram · TikTok</span><br>"
            "Role: <span style='color:#ffaa00;'>AI Influencer · Creative Director</span><br>"
            "Vibe: <span style='color:#cc88ff;'>Calm · Stoic · Charismatic</span>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

        # Asset folder counts
        outfits_dir = NEO_ASSETS / "Neo Outfits"
        envs_dir    = NEO_ASSETS / "Neo Environments"
        outfit_count = count_images_in(outfits_dir)
        env_count    = count_images_in(envs_dir)
        mens_count   = len([f for f in NEO_ASSETS.iterdir() if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")])

        folder_rows = [
            ("Neo Outfits", outfit_count, "#ff00ff"),
            ("Neo Environments", env_count, "#00ff88"),
            ("Mens Friends (refs)", mens_count, "#ffaa00"),
        ]
        for fname, cnt, color in folder_rows:
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:8px 12px;background:#0d0d17;border:1px solid rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.15);border-radius:4px;margin-bottom:6px;'>"
                f"<span style='font-family:Share Tech Mono,monospace;font-size:12px;color:#aabbcc;'>{fname}</span>"
                f"<span class='asset-count-chip' style='background:rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.1);border-color:rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.25);color:{color};'>{cnt} assets</span>"
                f"</div>",
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Full asset library overview ────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:11px;'>◈ FULL ASSET LIBRARY</div>",
        unsafe_allow_html=True,
    )

    asset_categories = [
        ("Environments", ASSETS_ROOT / "Environments", "#00ffff"),
        ("Influencer Clothing", ASSETS_ROOT / "Influencer CLothing ", "#ff00ff"),
        ("Friends", ASSETS_ROOT / "Friends", "#00ff88"),
        ("Vehicles", ASSETS_ROOT / "Vehicles", "#ffaa00"),
        ("Foods", ASSETS_ROOT / "Foods", "#cc88ff"),
        ("Props", ASSETS_ROOT / "Props", "#ff3366"),
        ("Pets", ASSETS_ROOT / "Pets", "#00aaff"),
        ("Shay.So.Fine", ASSETS_ROOT / "Shay.So.Fine", "#ff88aa"),
        ("Tyrie Master", ASSETS_ROOT / "Friends" / "Tyrie Master", "#ff8800"),
    ]

    lib_cols = st.columns(4)
    for i, (cat_name, cat_path, color) in enumerate(asset_categories):
        cnt = count_images_in(cat_path)
        with lib_cols[i % 4]:
            st.markdown(
                f"<div class='cyber-card' style='border-color:rgba({int(color[1:3],16)},"
                f"{int(color[3:5],16)},{int(color[5:7],16)},0.2);padding:14px;text-align:center;'>"
                f"<div style='font-family:Share Tech Mono,monospace;font-size:22px;color:{color};"
                f"text-shadow:0 0 12px {color}44;'>{cnt}</div>"
                f"<div style='font-family:Share Tech Mono,monospace;font-size:10px;color:#445566;"
                f"letter-spacing:0.08em;margin-top:4px;'>{cat_name.upper()}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # Show some environment thumbnails
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        "<div class='section-header' style='font-size:11px;'>◈ ENVIRONMENT PREVIEWS</div>",
        unsafe_allow_html=True,
    )
    env_imgs = sorted([
        f for f in (ASSETS_ROOT / "Environments").glob("*.jpg")
        if not f.name.startswith("._")
    ])[:12]

    if env_imgs:
        env_cols = st.columns(6)
        for i, ep in enumerate(env_imgs):
            with env_cols[i % 6]:
                b64 = img_to_b64(ep)
                if b64:
                    label = ep.stem[:16]
                    st.markdown(
                        f"<div class='asset-thumb'>"
                        f"<img src='data:image/jpeg;base64,{b64}' "
                        f"style='width:100%;height:90px;object-fit:cover;border-radius:2px;margin-bottom:4px;'>"
                        f"{label}"
                        f"</div>",
                        unsafe_allow_html=True,
                    )
    else:
        st.markdown(
            "<div class='coming-soon'>No environment images found.</div>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;font-family:Share Tech Mono,monospace;font-size:10px;"
    "color:#1a2233;letter-spacing:0.15em;border-top:1px solid rgba(0,255,255,0.05);padding-top:16px;'>"
    "VLM MISSION CONTROL · CREATEFLOW ECOSYSTEM · PORT 8502 · ⚡ NEO OPS"
    "</div>",
    unsafe_allow_html=True,
)
