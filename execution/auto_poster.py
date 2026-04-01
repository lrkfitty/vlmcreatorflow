#!/opt/homebrew/bin/python3.11
"""
VLM Auto-Poster — Unified 2x/day posting engine
Posts approved content for Neo, Shay, and Ty to Instagram.
Tracks outfit usage. Warns when content runs low.

Cron schedule: 10:00 and 22:00 Bangkok time
Usage: python3.11 auto_poster.py --account all
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent.parent
sys.path.insert(0, str(BASE))

from dotenv import load_dotenv
load_dotenv(BASE / ".env")

TMP          = BASE / ".tmp"
TMP.mkdir(exist_ok=True)

OUTFIT_LOG   = TMP / "outfit_usage.json"
ACTIVITY_LOG = TMP / "activity_log.json"

NEO_IG       = BASE / "output/users/Neo/Instagram"
SHAY_IG      = BASE / "output/users/Shay/Instagram"
TYRIE_IG     = BASE / "output/users/Tyrie/Instagram"

NEO_POST_LOG   = TMP / "neo_post_log.json"
SHAY_POST_LOG  = TMP / "shay_post_log.json"
TYRIE_POST_LOG = TMP / "tyrie_post_log.json"

APPROVED_FILE   = TMP / "approved_posts.json"
TYRIE_APPROVED  = TMP / "tyrie_approved.json"

# ── Shay outfit lookup (from shay_30day_batch CAROUSELS list) ─────────────────
SHAY_OUTFIT_MAP = {
    "maldives_lewk":       "Scrunch Marble",
    "phi_phi_travel":      "Jamaica Shorts",
    "jamaica_river":       "Jamaica Shorts",
    "night_out_chanel":    "Chanel Nude Dress",
    "amalfi_coast":        "Pink Brunch Villa",
    "private_jet":         "Baby Blue Outfit",
    "desert_pool":         "Swimsuit",
    "beach_paradise":      "Montce Swimsuit",
    "elephant_adventure":  "Green Christian Dior",
    "lakers_game":         "Pink Leopard Tracksuit",
    "pink_bedroom_glam":   "Pink Student Uniform",
    "matching_set_dior":   "Christian Rainbow Dior Set",
    "horse_riding":        "White Short Jogging Suit",
    "night_out_red":       "Leather Red Bodysuit",
    "podcast_studio":      "Gray Biker Girl Fit",
    "waterfall_cave":      "Swimsuit",
    "van_cleef_set":       "VanCleef Rainbow Set",
    "atl_airport":         "Orange Sherbet Tracksuit",
    "pink_petal_bath":     "White Christian Dior",
    "braves_game":         "Blue Jean Skirt Fit",
    "dior_green_editorial":"Green Christian Dior",
    "night_out_animal":    "Animal Print Floor Length",
    "bathroom_selfie_glam":"Blue and White Bodysuit",
    "vacay_bedroom_morning":"White Tube Bodysuit",
    "rich_girl_set":       "Rich Girl Matching Set",
    "fur_boots_winter":    "Fur Boots and Boyshorts",
    "neo_shay_collab":     "Green Christian Dior",
    "body_suit_yellow":    "Yellow Bodysuit",
    "night_out_pink_dress":"Pink Dress",
    "brazil_nike_casual":  "Brazil Nike Socks Fit",
    "soft_girl_lounge":    "Pink Leopard Tracksuit",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_json(path, default=None):
    try:
        p = Path(path)
        if p.exists():
            return json.loads(p.read_text())
    except Exception:
        pass
    return default if default is not None else {}


def save_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, indent=2))


def log_activity(action, details, status="success"):
    log = load_json(ACTIVITY_LOG, [])
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action":    action,
        "details":   details,
        "status":    status,
    }
    log.append(entry)
    save_json(ACTIVITY_LOG, log)
    print(f"[{status.upper()}] {action}: {details}")


def track_outfit(account, post_id, outfit):
    usage = load_json(OUTFIT_LOG, {})
    if account not in usage:
        usage[account] = []
    usage[account].append({
        "post_id":   post_id,
        "outfit":    outfit,
        "posted_at": datetime.now().isoformat(),
    })
    save_json(OUTFIT_LOG, usage)


# ── NEO ───────────────────────────────────────────────────────────────────────

def get_neo_queue():
    approved  = load_json(APPROVED_FILE, {})
    post_log  = load_json(NEO_POST_LOG, [])
    posted    = {e["stem"] for e in post_log}

    queue = []
    for stem, val in approved.items():
        if stem == "shay":
            continue
        if val is not True or stem in posted:
            continue
        img = NEO_IG / f"{stem}.jpg"
        if not img.exists():
            continue
        caption_path = NEO_IG / f"{stem}_caption.txt"
        caption = caption_path.read_text().strip() if caption_path.exists() else ""
        queue.append({"stem": stem, "image": str(img), "caption": caption})

    return queue


def post_neo():
    queue = get_neo_queue()
    if not queue:
        log_activity("NEO_POST", "No approved content remaining — approve more posts in dashboard", "pending")
        return None

    post = queue[0]
    try:
        from execution.instagram_client import post_photo
        media = post_photo(post["image"], post["caption"], account="neo")

        log = load_json(NEO_POST_LOG, [])
        log.append({
            "stem":      post["stem"],
            "url":       f"https://www.instagram.com/p/{media.code}/",
            "posted_at": datetime.now().isoformat(),
        })
        save_json(NEO_POST_LOG, log)

        track_outfit("neo", post["stem"], "")
        log_activity("NEO_POST", f"Posted {post['stem']} — instagram.com/p/{media.code}/", "success")
        return media

    except Exception as e:
        log_activity("NEO_POST", f"Failed: {e}", "failed")
        return None


# ── SHAY ──────────────────────────────────────────────────────────────────────

def get_shay_queue():
    approved  = load_json(APPROVED_FILE, {}).get("shay", {})
    post_log  = load_json(SHAY_POST_LOG, [])
    posted    = {e["carousel_id"] for e in post_log}

    queue = []
    for carousel_path in sorted(SHAY_IG.glob("*_carousel.json")):
        try:
            data = json.loads(carousel_path.read_text())
        except Exception:
            continue
        cid = data.get("id", carousel_path.stem.replace("_carousel", ""))
        if cid not in approved or cid in posted:
            continue
        images = [p for p in data.get("images", []) if Path(p).exists()]
        if not images:
            continue
        queue.append({
            "carousel_id": cid,
            "images":      images,
            "caption":     data.get("caption", ""),
            "outfit":      SHAY_OUTFIT_MAP.get(cid, "Unknown"),
        })

    return queue


def post_shay():
    queue = get_shay_queue()
    if not queue:
        log_activity("SHAY_POST", "No approved content remaining — approve more carousels in dashboard", "pending")
        return None

    post = queue[0]
    try:
        from execution.instagram_client import post_carousel, post_photo
        if len(post["images"]) > 1:
            media = post_carousel(post["images"], post["caption"], account="shay")
        else:
            media = post_photo(post["images"][0], post["caption"], account="shay")

        log = load_json(SHAY_POST_LOG, [])
        log.append({
            "carousel_id": post["carousel_id"],
            "outfit":      post["outfit"],
            "url":         f"https://www.instagram.com/p/{media.code}/",
            "posted_at":   datetime.now().isoformat(),
        })
        save_json(SHAY_POST_LOG, log)

        track_outfit("shay", post["carousel_id"], post["outfit"])
        log_activity("SHAY_POST", f"Posted {post['carousel_id']} (outfit: {post['outfit']}) — instagram.com/p/{media.code}/", "success")
        return media

    except Exception as e:
        log_activity("SHAY_POST", f"Failed: {e}", "failed")
        return None


# ── TY ────────────────────────────────────────────────────────────────────────

def get_ty_queue():
    approved  = load_json(TYRIE_APPROVED, {})
    post_log  = load_json(TYRIE_POST_LOG, [])
    posted    = {e["stem"] for e in post_log}

    queue = []
    search_dirs = [TYRIE_IG, TYRIE_IG / "couple"]
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        for caption_path in sorted(search_dir.glob("*_caption.txt")):
            cid = caption_path.stem.replace("_caption", "")
            if cid not in approved or cid in posted:
                continue
            caption     = caption_path.read_text().strip()
            shot_paths  = sorted(search_dir.glob(f"{cid}_shot*.jpg"))
            if not shot_paths:
                single = search_dir / f"{cid}.jpg"
                if single.exists():
                    shot_paths = [single]
            if shot_paths:
                queue.append({
                    "stem":        cid,
                    "image_paths": [str(p) for p in shot_paths if Path(p).exists()],
                    "caption":     caption,
                })

    return queue


def post_ty():
    queue = get_ty_queue()
    if not queue:
        log_activity("TY_POST", "No approved content remaining — approve more carousels in dashboard", "pending")
        return None

    post = queue[0]
    images = post["image_paths"]
    if not images:
        log_activity("TY_POST", f"Image files missing for {post['stem']}", "failed")
        return None

    try:
        from execution.instagram_client import post_carousel, post_photo
        if len(images) > 1:
            media = post_carousel(images, post["caption"], account="ty")
        else:
            media = post_photo(images[0], post["caption"], account="ty")

        log = load_json(TYRIE_POST_LOG, [])
        log.append({
            "stem":      post["stem"],
            "url":       f"https://www.instagram.com/p/{media.code}/",
            "posted_at": datetime.now().isoformat(),
        })
        save_json(TYRIE_POST_LOG, log)

        track_outfit("ty", post["stem"], "")
        log_activity("TY_POST", f"Posted {post['stem']} — instagram.com/p/{media.code}/", "success")
        return media

    except Exception as e:
        log_activity("TY_POST", f"Failed: {e}", "failed")
        return None


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VLM Auto-Poster")
    parser.add_argument(
        "--account",
        choices=["neo", "shay", "ty", "all"],
        default="all",
        help="Which account to post for",
    )
    args = parser.parse_args()

    accounts = ["neo", "shay", "ty"] if args.account == "all" else [args.account]

    print(f"\n=== VLM AUTO-POSTER — {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    for account in accounts:
        print(f"\n--- {account.upper()} ---")
        if account == "neo":
            post_neo()
        elif account == "shay":
            post_shay()
        elif account == "ty":
            post_ty()

    print("\n=== DONE ===")
