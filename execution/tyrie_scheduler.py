"""
Tyrie (Ty Larkin) — 30-Day Auto-Poster Scheduler
Posts daily to @tytheguyyttg from the generated batch.

Schedule file: .tmp/tyrie_schedule.json
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

BASE         = Path(__file__).parent.parent
TYRIE_IG     = BASE / "output" / "users" / "Tyrie" / "Instagram"
SCHEDULE_FILE = BASE / ".tmp" / "tyrie_schedule.json"
POST_LOG_FILE = BASE / ".tmp" / "tyrie_post_log.json"


def load_json(path, default=None):
    if default is None:
        default = {}
    try:
        if path.exists():
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def get_posts():
    """
    Get all generated carousel posts from the output folder.
    Groups shot1/shot2/shot3 files under their carousel ID.
    """
    posts = []
    if not TYRIE_IG.exists():
        return posts

    # Find all carousel IDs from caption files
    for caption_path in sorted(TYRIE_IG.glob("*_caption.txt")):
        carousel_id = caption_path.stem.replace("_caption", "")
        caption = caption_path.read_text().strip()

        # Collect all shots for this carousel
        shot_paths = sorted(TYRIE_IG.glob(f"{carousel_id}_shot*.jpg"))
        if not shot_paths:
            # Fallback: single image with same ID
            single = TYRIE_IG / f"{carousel_id}.jpg"
            if single.exists():
                shot_paths = [single]

        if shot_paths:
            posts.append({
                "stem": carousel_id,
                "image_paths": [str(p) for p in shot_paths],
                "caption": caption,
            })

    return posts


def build_schedule(start_date=None):
    """Assign all generated posts to consecutive days starting from start_date."""
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")

    posts = get_posts()
    if not posts:
        print("No posts found. Run tyrie_30day_batch.py first.")
        return []

    schedule = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")

    for i, post in enumerate(posts):
        entry = {
            "day": i + 1,
            "date": (current_date + timedelta(days=i)).strftime("%Y-%m-%d"),
            "weekday": (current_date + timedelta(days=i)).strftime("%A"),
            "stem": post["stem"],
            "image_paths": post["image_paths"],
            "caption": post["caption"],
            "status": "scheduled",
            "posted_at": None,
            "post_url": None,
        }
        schedule.append(entry)

    save_json(SCHEDULE_FILE, schedule)
    end_date = (current_date + timedelta(days=len(schedule) - 1)).strftime("%Y-%m-%d")
    print(f"Schedule built: {len(schedule)} posts | {start_date} -> {end_date}")
    return schedule


def post_todays_content():
    """Check if there's a post scheduled for today and post it to @tytheguyyttg."""
    schedule = load_json(SCHEDULE_FILE, [])
    if not schedule:
        print("No schedule found. Run build_schedule() first.")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    todays_post = next(
        (e for e in schedule if e["date"] == today and e["status"] == "scheduled"),
        None
    )

    if not todays_post:
        print(f"No post scheduled for today ({today}), or already posted.")
        return None

    print(f"Posting Day {todays_post['day']}: {todays_post['stem']}")
    print(f"Caption: {todays_post['caption'][:80]}...")

    try:
        from execution.instagram_client import post_photo, post_carousel

        image_paths = todays_post.get("image_paths", [])

        # Check if a video was generated for one of the shots — swap it in
        video_queue_path = BASE / ".tmp" / "tyrie_video_queue.json"
        if video_queue_path.exists():
            import json as _json
            vq = _json.loads(video_queue_path.read_text())
            vid_entry = vq.get(todays_post["stem"], {})
            if vid_entry.get("status") == "done" and vid_entry.get("video_path"):
                shot_index = vid_entry.get("shot_index", 0)
                video_path = vid_entry["video_path"]
                if Path(video_path).exists() and shot_index < len(image_paths):
                    image_paths = list(image_paths)
                    image_paths[shot_index] = video_path  # replace that slot with the video

        if len(image_paths) > 1:
            media = post_carousel(image_paths, todays_post["caption"], account="ty")
        else:
            media = post_photo(image_paths[0] if image_paths else todays_post.get("image_path", ""), todays_post["caption"], account="ty")

        todays_post["status"] = "posted"
        todays_post["posted_at"] = datetime.now().isoformat()
        todays_post["post_url"] = f"https://www.instagram.com/p/{media.code}/"
        save_json(SCHEDULE_FILE, schedule)

        post_log = load_json(POST_LOG_FILE, [])
        post_log.append({
            "date": today,
            "day": todays_post["day"],
            "stem": todays_post["stem"],
            "url": todays_post["post_url"],
            "posted_at": todays_post["posted_at"],
        })
        save_json(POST_LOG_FILE, post_log)

        print(f"Posted: {todays_post['post_url']}")
        return todays_post

    except Exception as e:
        todays_post["status"] = "failed"
        save_json(SCHEDULE_FILE, schedule)
        print(f"Failed to post: {e}")
        return None


def view_schedule():
    schedule = load_json(SCHEDULE_FILE, [])
    if not schedule:
        print("No schedule found.")
        return

    print(f"\n{'='*70}")
    print(f"TYRIE 30-DAY POSTING SCHEDULE — @tytheguyyttg")
    print(f"{'='*70}")
    for entry in schedule:
        icon = {"scheduled": "...", "posted": "OK", "failed": "!!!"}.get(entry["status"], "?")
        print(f"  Day {entry['day']:2d} | {entry['date']} ({entry['weekday'][:3]}) | {icon} {entry['status']:10s} | {entry['caption'][:50]}...")

    posted    = sum(1 for e in schedule if e["status"] == "posted")
    scheduled = sum(1 for e in schedule if e["status"] == "scheduled")
    print(f"\n  Posted: {posted} | Scheduled: {scheduled} | Total: {len(schedule)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tyrie 30-Day Scheduler")
    parser.add_argument("action", choices=["build", "post", "view"])
    parser.add_argument("--start", default=None, help="Start date YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    if args.action == "build":
        build_schedule(start_date=args.start)
        view_schedule()
    elif args.action == "post":
        post_todays_content()
    elif args.action == "view":
        view_schedule()
