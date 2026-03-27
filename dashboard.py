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
SHAY_LOG  = PROJECT_ROOT / ".tmp" / "shay_post_log.json"
NEO_LOG   = PROJECT_ROOT / ".tmp" / "neo_post_log.json"

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
    """Return list of (carousel_id, [shot_paths], caption) grouped by carousel.
    Groups *_shot*.jpg files together; falls back to treating each jpg as its own entry."""
    if not NEO_IG.exists():
        return []
    carousels = []
    seen = set()
    # First pass: find carousels that have caption files
    for caption_path in sorted(NEO_IG.glob("*_caption.txt")):
        carousel_id = caption_path.stem.replace("_caption", "")
        caption = caption_path.read_text(encoding="utf-8").strip()
        shot_paths = sorted(NEO_IG.glob(f"{carousel_id}_shot*.jpg"))
        if not shot_paths:
            single = NEO_IG / f"{carousel_id}.jpg"
            if single.exists():
                shot_paths = [single]
        if shot_paths:
            carousels.append((carousel_id, shot_paths, caption))
            for sp in shot_paths:
                seen.add(sp.name)
    # Second pass: lone jpgs not grouped
    for img in sorted(NEO_IG.glob("*.jpg"), key=lambda p: p.stat().st_mtime, reverse=True):
        if "_thumb" in img.name or img.name in seen:
            continue
        stem = img.stem
        cap_path = NEO_IG / f"{stem}_caption.txt"
        cap = cap_path.read_text(encoding="utf-8").strip() if cap_path.exists() else ""
        carousels.append((stem, [img], cap))
        seen.add(img.name)
    return carousels


def render_content_calendar(schedule_items: list, posted_ids: set, approved_ids: set) -> str:
    """Render a compact visual 30-day calendar grid as HTML colored day squares."""
    if not schedule_items:
        return "<div style='color:#334455;font-size:12px;'>No schedule loaded</div>"

    cells = []
    for item in schedule_items:
        cid  = item.get("carousel_id", "")
        day  = item.get("day", "?")
        dt   = item.get("date", "")
        if cid in posted_ids:
            bg, border, dot = "#003366", "#0066cc", "🔵"
        elif cid in approved_ids:
            bg, border, dot = "#003322", "#00aa44", "✅"
        else:
            bg, border, dot = "#221a00", "#aa7700", "⏳"
        cells.append(
            f"<div title='Day {day} · {dt}' style='"
            f"display:inline-flex;flex-direction:column;align-items:center;justify-content:center;"
            f"width:32px;height:38px;margin:2px;background:{bg};border:1px solid {border};"
            f"border-radius:4px;cursor:default;'>"
            f"<span style='font-size:8px;font-family:Share Tech Mono;color:{border};'>{day}</span>"
            f"<span style='font-size:10px;'>{dot}</span>"
            f"</div>"
        )
    legend = (
        "<div style='display:flex;gap:14px;font-size:10px;color:#556677;font-family:Share Tech Mono;"
        "margin-top:6px;margin-bottom:2px;'>"
        "<span>🔵 Posted</span><span>✅ Approved</span><span>⏳ Pending</span>"
        "</div>"
    )
    return f"<div style='padding:4px 0;flex-wrap:wrap;'>{''.join(cells)}</div>{legend}"


def _kling_queue_done_videos(video_queue: dict) -> list:
    """Return list of (carousel_id, video_path) for completed Kling generations."""
    done = []
    for cid, entry in video_queue.items():
        if entry.get("status") == "done":
            vp = entry.get("video_path", "")
            if vp and Path(vp).exists():
                done.append((cid, vp, entry))
    return done


def _remove_ty_carousel(carousel_id: str, search_dirs: list):
    """Delete all files belonging to a Ty carousel (shots + caption)."""
    for d in search_dirs:
        for f in list(Path(d).glob(f"{carousel_id}*")):
            try:
                f.unlink()
            except Exception:
                pass


def _mark_posted_ty(carousel_id: str, caption: str, log_path: Path):
    """Append carousel_id to Ty's post log as manually posted."""
    log = load_json(log_path, default=[])
    if not any(e.get("stem") == carousel_id for e in log):
        log.append({"stem": carousel_id, "url": "", "posted_at": datetime.now().isoformat(), "manual": True})
        log_path.write_text(json.dumps(log, indent=2))


def _mark_posted_shay(carousel_id: str, log_path: Path, schedule_path: Path):
    """Append carousel_id to Shay's post log and update schedule status."""
    log = load_json(log_path, default=[])
    if not any(e.get("carousel_id") == carousel_id for e in log):
        log.append({"carousel_id": carousel_id, "url": "", "posted_at": datetime.now().isoformat(), "manual": True})
        log_path.write_text(json.dumps(log, indent=2))
    # Also update schedule status
    schedule = load_json(schedule_path, default=[])
    for item in schedule:
        if item.get("carousel_id") == carousel_id:
            item["status"] = "posted"
            item["posted_at"] = datetime.now().isoformat()
    schedule_path.write_text(json.dumps(schedule, indent=2))


def _remove_shay_carousel(carousel_id: str, schedule_path: Path):
    """Remove carousel from Shay schedule JSON."""
    schedule = load_json(schedule_path, default=[])
    schedule = [s for s in schedule if s.get("carousel_id") != carousel_id]
    schedule_path.write_text(json.dumps(schedule, indent=2))


def _mark_posted_neo(stem: str, log_path: Path):
    """Append stem to Neo's post log."""
    log = load_json(log_path, default=[])
    if not any(e.get("stem") == stem for e in log):
        log.append({"stem": stem, "url": "", "posted_at": datetime.now().isoformat(), "manual": True})
        log_path.write_text(json.dumps(log, indent=2))


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

    neo_log = load_json(NEO_LOG, default=[])
    neo_posted_stems = {e.get("stem", "") for e in neo_log if e.get("stem")}

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
        _neo_posts_count = len(get_neo_ig_posts())
        st.markdown(
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ff00ff;text-shadow:0 0 15px rgba(255,0,255,0.4);'>{_neo_posts_count}</span>"
            f"<span class='stat-label'>Carousels Ready</span>"
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
            f"<div class='stat-box'>"
            f"<span class='stat-value' style='color:#ffaa00;text-shadow:0 0 15px rgba(255,170,0,0.4);'>{len(neo_log)}</span>"
            f"<span class='stat-label'>Posted</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── NEO 30-DAY CALENDAR ───────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;'>⚡ CONTENT CALENDAR</div>",
        unsafe_allow_html=True,
    )
    posts = get_neo_ig_posts()
    neo_cal_items = [{"carousel_id": cid, "day": i+1, "date": ""} for i, (cid, _, _) in enumerate(posts)]
    neo_approved_ids = {k for k, v in approved.items() if v}
    st.markdown(render_content_calendar(neo_cal_items, neo_posted_stems, neo_approved_ids), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── NEO CAROUSEL QUEUE ────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;'>⚡ CONTENT QUEUE</div>",
        unsafe_allow_html=True,
    )

    if not posts:
        st.markdown(
            "<div class='coming-soon'>"
            "<span class='coming-soon-value'>📷</span>"
            "No images found in output/users/Neo/Instagram/"
            "</div>",
            unsafe_allow_html=True,
        )
    else:
        neo_filter = st.radio(
            "Filter",
            ["Unposted", "All", "Approved", "Posted"],
            horizontal=True,
            key="neo_filter_status",
            label_visibility="collapsed",
        )

        for idx, (carousel_id, shot_paths, caption) in enumerate(posts):
            is_approved = approved.get(carousel_id, False)
            is_posted   = carousel_id in neo_posted_stems

            if neo_filter == "Unposted" and is_posted:
                continue
            if neo_filter == "Approved" and not is_approved:
                continue
            if neo_filter == "Posted" and not is_posted:
                continue

            if is_posted:
                status_label, badge_class = "🔵 POSTED", "badge-approved"
            elif is_approved:
                status_label, badge_class = "✓ APPROVED", "badge-approved"
            else:
                status_label, badge_class = "READY", "badge-ready"

            caption_short = caption[:180] + "…" if len(caption) > 180 else caption

            st.markdown(
                f"<div style='background:rgba(0,255,255,0.03);border:1px solid rgba(0,255,255,0.15);"
                f"border-radius:4px;padding:12px;margin-bottom:12px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<span class='badge {badge_class}'>{status_label}</span>"
                f"<span style='font-size:10px;color:#556677;font-family:Share Tech Mono;'>Post {idx+1} · {carousel_id}</span>"
                f"</div>"
                f"<div style='color:#aabbcc;font-size:13px;line-height:1.4;'>{caption_short or '<em style=color:#334455>No caption</em>'}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # All shots in expander
            if shot_paths:
                with st.expander(f"🖼️ View {len(shot_paths)} images"):
                    img_cols = st.columns(min(len(shot_paths), 4))
                    for si, sp in enumerate(shot_paths[:4]):
                        with img_cols[si]:
                            st.image(str(sp), use_container_width=True)
                            if not is_posted:
                                if st.button("🎬 Kling", key=f"neo_kling_{carousel_id}_{si}"):
                                    st.info("Queue Kling — wire to kling_client when ready")

            # Action buttons
            if not is_posted:
                nc1, nc2, nc3, _ = st.columns([2, 2, 2, 3])
                with nc1:
                    if st.button("✓ Approve" if not is_approved else "✓ Approved", key=f"approve_{carousel_id}"):
                        approved[carousel_id] = not is_approved
                        save_approved(approved)
                        st.rerun()
                with nc2:
                    if st.button("🔵 Mark Posted", key=f"neo_posted_{carousel_id}"):
                        _mark_posted_neo(carousel_id, NEO_LOG)
                        st.success("Marked as posted")
                        st.rerun()
                with nc3:
                    if st.button("🗑️ Remove", key=f"neo_remove_{carousel_id}"):
                        for sp in shot_paths:
                            try: Path(sp).unlink()
                            except Exception: pass
                        cap_file = NEO_IG / f"{carousel_id}_caption.txt"
                        try: cap_file.unlink()
                        except Exception: pass
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2: SHAY INSTAGRAM PANEL
# ══════════════════════════════════════════════════════════════════════════════

def get_shay_ig_posts():
    """Scan disk for Shay carousels grouped by caption file — same pattern as Neo."""
    if not SHAY_IG.exists():
        return []
    carousels = []
    seen = set()
    for caption_path in sorted(SHAY_IG.glob("*_caption.txt")):
        carousel_id = caption_path.stem.replace("_caption", "")
        caption = caption_path.read_text(encoding="utf-8").strip()
        shot_paths = sorted(SHAY_IG.glob(f"{carousel_id}_shot*.jpg"))
        if not shot_paths:
            single = SHAY_IG / f"{carousel_id}.jpg"
            if single.exists():
                shot_paths = [single]
        if shot_paths:
            carousels.append((carousel_id, shot_paths, caption))
            for sp in shot_paths:
                seen.add(sp.name)
    return carousels

with tab_shay:
    st.markdown(
        "<div class='section-header'>💎 SHAY · INSTAGRAM COMMAND</div>",
        unsafe_allow_html=True,
    )

    # Load post log + approvals
    shay_log = load_json(SHAY_LOG, default=[])
    shay_posted_ids = {e.get("carousel_id", "") for e in shay_log if e.get("carousel_id")}
    approved_data = load_approved()
    shay_approvals = approved_data.get("shay", {})
    shay_approved_ids = set(shay_approvals.keys())

    # Discover carousels from disk
    shay_posts = get_shay_ig_posts()
    approved_count = sum(1 for cid, _, _ in shay_posts if cid in shay_approved_ids)

    stat_cols = st.columns(4)
    with stat_cols[0]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>150</span><span class='stat-label'>Followers</span></div>", unsafe_allow_html=True)
    with stat_cols[1]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>{approved_count}/{len(shay_posts)}</span><span class='stat-label'>Approved</span></div>", unsafe_allow_html=True)
    with stat_cols[2]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#00ff88;'>{len(shay_log)}</span><span class='stat-label'>Posted</span></div>", unsafe_allow_html=True)
    with stat_cols[3]:
        st.markdown(f"<div class='stat-box'><span class='stat-value' style='color:#ff00ff;'>{len(shay_posts)}</span><span class='stat-label'>Scheduled</span></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 30-DAY CALENDAR ───────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;'>💫 30-DAY CONTENT CALENDAR</div>",
        unsafe_allow_html=True,
    )
    shay_cal_items = [{"carousel_id": cid, "day": i+1, "date": ""} for i, (cid, _, _) in enumerate(shay_posts)]
    shay_cal_html = render_content_calendar(shay_cal_items, shay_posted_ids, shay_approved_ids)
    st.markdown(shay_cal_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        "<div class='section-header' style='font-size:12px;margin-top:8px;'>💫 30-DAY CAROUSEL QUEUE</div>",
        unsafe_allow_html=True,
    )

    if not shay_posts:
        st.markdown("<div class='coming-soon'><span class='coming-soon-value'>📋</span>Generating content… check back soon</div>", unsafe_allow_html=True)
    else:
        filter_status = st.radio(
            "Filter",
            ["Unposted", "All", "Approved", "Posted"],
            horizontal=True,
            key="shay_filter_status",
            label_visibility="collapsed"
        )

        for idx, (carousel_id, shot_paths, caption) in enumerate(shay_posts):
            images = [str(p) for p in shot_paths]
            is_approved = carousel_id in shay_approved_ids
            is_posted   = carousel_id in shay_posted_ids

            if filter_status == "Unposted" and is_posted:
                continue
            if filter_status == "Approved" and not is_approved:
                continue
            if filter_status == "Posted" and not is_posted:
                continue

            if is_posted:
                badge_class, status_label = "badge-approved", "🔵 POSTED"
            elif is_approved:
                badge_class, status_label = "badge-approved", "✓ APPROVED"
            else:
                badge_class, status_label = "badge-pending", "⊙ PENDING"

            st.markdown(
                f"<div style='background:rgba(255,0,255,0.05);border:1px solid rgba(255,0,255,0.2);"
                f"border-radius:4px;padding:12px;margin-bottom:12px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<span style='color:#00ffff;font-family:Share Tech Mono;font-size:11px;'>Day {idx+1} · {carousel_id}</span>"
                f"<span class='{badge_class}' style='padding:2px 8px;border-radius:2px;font-size:10px;'>{status_label}</span>"
                f"</div>"
                f"<div style='color:#aabbcc;font-size:13px;line-height:1.4;'>{caption[:180]}...</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            if images:
                with st.expander(f"🖼️ View {len(images)} images"):
                    img_cols = st.columns(min(len(images), 4))
                    for im_idx, img_path in enumerate(images[:4]):
                        with img_cols[im_idx]:
                            st.image(str(img_path), use_container_width=True)
                            if not is_posted:
                                if st.button("🎬 Kling", key=f"shay_kling_{carousel_id}_{im_idx}"):
                                    st.info("Queue Kling from this image — wire to kling_client when ready")

            if not is_posted:
                ac1, ac2, ac3 = st.columns([2, 2, 2])
                with ac1:
                    if st.button("✓ Approve" if not is_approved else "✓ Approved", key=f"shay_approve_{carousel_id}"):
                        shay_approvals[carousel_id] = {"approved_at": datetime.now().isoformat()}
                        approved_data["shay"] = shay_approvals
                        save_approved(approved_data)
                        st.rerun()
                with ac2:
                    if st.button("🔵 Mark Posted", key=f"shay_posted_{carousel_id}"):
                        _mark_posted_shay(carousel_id, SHAY_LOG, PROJECT_ROOT / ".tmp" / "shay_schedule.json")
                        st.success("Marked as posted")
                        st.rerun()
                with ac3:
                    if st.button("🗑️ Remove", key=f"shay_remove_{carousel_id}"):
                        for sp in shot_paths:
                            sp.unlink(missing_ok=True)
                        cap_file = SHAY_IG / f"{carousel_id}_caption.txt"
                        if cap_file.exists():
                            cap_file.unlink()
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

    # Build set of already-posted stems
    posted_stems = {e.get("stem", "") for e in tyrie_log if e.get("stem")}

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

    # ── KLING REELS SECTION ───────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;'>🎬 KLING VIDEO CLIPS</div>",
        unsafe_allow_html=True,
    )
    VIDEO_QUEUE_FILE = PROJECT_ROOT / ".tmp" / "tyrie_video_queue.json"
    video_queue = load_json(VIDEO_QUEUE_FILE, default={})
    tyrie_approved_save_path = PROJECT_ROOT / ".tmp" / "tyrie_approved.json"

    done_videos = _kling_queue_done_videos(video_queue)
    if done_videos:
        vc = st.columns(min(len(done_videos), 3))
        for ri, (cid, vp, entry) in enumerate(done_videos[:6]):
            with vc[ri % 3]:
                st.video(vp)
                st.caption(f"{cid} · {entry.get('camera_move','')}")
    else:
        st.markdown(
            "<div class='coming-soon' style='padding:12px;'>No Kling clips yet — use 🎬 Make Clip buttons below</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 30-DAY CALENDAR ───────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;margin-top:8px;'>◭ 30-DAY CONTENT CALENDAR</div>",
        unsafe_allow_html=True,
    )
    # Build schedule-like list from tyrie_carousels for the calendar
    ty_cal_items = [{"carousel_id": cid, "day": i+1, "date": ""} for i, (cid, _, _) in enumerate(tyrie_carousels)]
    cal_html = render_content_calendar(ty_cal_items, posted_stems, set(tyrie_approved.keys()))
    st.markdown(cal_html, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── CAROUSEL APPROVAL ─────────────────────────────────────────────────────
    st.markdown(
        "<div class='section-header' style='font-size:12px;margin-top:8px;'>◭ 30-DAY CAROUSEL QUEUE</div>",
        unsafe_allow_html=True,
    )

    if not tyrie_carousels:
        st.markdown(
            "<div class='coming-soon'><span class='coming-soon-value'>◭</span>"
            "No carousels yet — generation is running in the background.</div>",
            unsafe_allow_html=True,
        )
    else:
        filter_ty = st.radio(
            "Filter",
            ["Unposted", "All", "Approved", "Posted"],
            horizontal=True,
            key="tyrie_filter",
            label_visibility="collapsed",
        )

        for idx, (carousel_id, shot_paths, caption) in enumerate(tyrie_carousels):
            is_approved = bool(tyrie_approved.get(carousel_id))
            is_posted   = carousel_id in posted_stems

            if filter_ty == "Unposted" and is_posted:
                continue
            if filter_ty == "Approved" and not is_approved:
                continue
            if filter_ty == "Posted" and not is_posted:
                continue

            if is_posted:
                badge_class, status_label = "badge-posted", "🔵 POSTED"
            elif is_approved:
                badge_class, status_label = "badge-approved", "✓ APPROVED"
            else:
                badge_class, status_label = "badge-pending", "⊙ PENDING"

            vid_entry = video_queue.get(carousel_id, {})

            # Carousel card header (no images shown by default)
            st.markdown(
                f"<div style='background:rgba(255,136,0,0.05);border:1px solid rgba(255,136,0,0.2);"
                f"border-radius:4px;padding:12px;margin-bottom:12px;'>"
                f"<div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;'>"
                f"<span style='color:#00ffff;font-family:Share Tech Mono;font-size:11px;'>Post {idx+1} · {carousel_id}</span>"
                f"<span class='{badge_class}' style='padding:2px 8px;border-radius:2px;font-size:10px;'>{status_label}</span>"
                f"</div>"
                f"<div style='color:#aabbcc;font-size:13px;line-height:1.4;'>{caption[:180]}...</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Images hidden in expander
            if shot_paths:
                with st.expander(f"🖼️ View {len(shot_paths)} images"):
                    img_cols = st.columns(min(len(shot_paths), 4))
                    for i, sp in enumerate(shot_paths[:4]):
                        with img_cols[i]:
                            if Path(sp).exists():
                                st.image(str(sp), use_container_width=True)

            # Kling video status / buttons
            kling_status = vid_entry.get("status", "")
            if kling_status == "done":
                vp = vid_entry.get("video_path", "")
                if vp and Path(vp).exists():
                    st.video(vp)
            elif kling_status == "generating":
                st.markdown(
                    "<div style='color:#00ffff;font-size:11px;font-family:Share Tech Mono;'>⏳ Kling generating...</div>",
                    unsafe_allow_html=True,
                )
            elif kling_status == "failed":
                st.markdown(
                    "<div style='color:#ff4444;font-size:11px;font-family:Share Tech Mono;'>❌ Generation failed</div>",
                    unsafe_allow_html=True,
                )
            elif not is_posted:
                # Show "Make 2 Kling clips" button
                kling_col, _ = st.columns([2, 3])
                with kling_col:
                    if st.button("🎬 Make Kling Clips", key=f"kling_auto_{carousel_id}"):
                        picks = [str(sp) for sp in shot_paths[:2] if Path(sp).exists()]
                        if picks:
                            with st.spinner("Queueing Kling generations..."):
                                for ki, shot_key in enumerate(picks):
                                    try:
                                        from execution.generate_video_prompt import generate_motion_prompt
                                        ai_prompt = generate_motion_prompt(
                                            image_path=shot_key,
                                            movement_type="Slow push in",
                                            physics_focus="High Physics",
                                            emotion="Confident",
                                            additional_context="AI influencer, Bangkok lifestyle.",
                                        )
                                    except Exception as e:
                                        ai_prompt = f"Slow cinematic push in. Natural breathing. Atmospheric light. 5 seconds."
                                    entry_key = f"{carousel_id}_clip{ki}"
                                    video_queue[entry_key] = {
                                        "shot": shot_key,
                                        "shot_index": ki,
                                        "status": "approved",
                                        "prompt": ai_prompt,
                                        "camera_move": "Slow push in",
                                        "physics": "High Physics",
                                        "emotion": "Confident",
                                        "video_path": "",
                                        "parent_carousel": carousel_id,
                                    }
                                VIDEO_QUEUE_FILE.write_text(json.dumps(video_queue, indent=2))
                                st.success(f"Queued {len(picks)} Kling clips for {carousel_id}")
                                st.rerun()

            # Action buttons: Approve | Mark Posted | Remove
            if not is_posted:
                act_c1, act_c2, act_c3, act_c4 = st.columns([2, 2, 2, 3])
                with act_c1:
                    btn_label = "✓ Approved" if is_approved else "✓ Approve"
                    if st.button(btn_label, key=f"ty_approve_{carousel_id}"):
                        tyrie_approved[carousel_id] = {"approved_at": datetime.now().isoformat()}
                        tyrie_approved_save_path.parent.mkdir(exist_ok=True)
                        tyrie_approved_save_path.write_text(json.dumps(tyrie_approved, indent=2))
                        st.rerun()
                with act_c2:
                    if st.button("🔵 Mark Posted", key=f"ty_posted_{carousel_id}"):
                        _mark_posted_ty(carousel_id, caption, TYRIE_LOG)
                        st.success("Marked as posted")
                        st.rerun()
                with act_c3:
                    if st.button("🗑️ Remove", key=f"ty_remove_{carousel_id}"):
                        _remove_ty_carousel(carousel_id, [TYRIE_IG, TYRIE_IG / "couple"])
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
        for i, (img_path, user) in enumerate(all_imgs[:6]):
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
