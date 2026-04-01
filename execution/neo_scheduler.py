"""
Neo 30-Day Auto-Poster Scheduler
Reads approved posts from the dashboard, assigns them to dates,
and posts them via instagram_client.py on schedule.

Schedule file: .tmp/neo_schedule.json
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

BASE = Path(__file__).parent.parent
NEO_IG = BASE / "output" / "users" / "Neo" / "Instagram"
SCHEDULE_FILE = BASE / ".tmp" / "neo_schedule.json"
APPROVED_FILE = BASE / ".tmp" / "approved_posts.json"
POST_LOG_FILE = BASE / ".tmp" / "neo_post_log.json"


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


def get_approved_posts():
    """Get all approved posts with their images and captions."""
    approved = load_json(APPROVED_FILE, {})
    posts = []
    
    if not NEO_IG.exists():
        return posts
    
    for img_path in sorted(NEO_IG.glob("*.jpg")):
        if "_thumb" in img_path.name:
            continue
        stem = img_path.stem
        if approved.get(stem, False):
            caption_path = NEO_IG / f"{stem}_caption.txt"
            caption = ""
            if caption_path.exists():
                caption = caption_path.read_text().strip()
            posts.append({
                "stem": stem,
                "image_path": str(img_path),
                "caption": caption
            })
    
    return posts


def build_schedule(start_date=None, posts_per_day=1):
    """
    Assign approved posts to consecutive days starting from start_date.
    30-day daily posting challenge.
    """
    if start_date is None:
        start_date = datetime.now().strftime("%Y-%m-%d")
    
    posts = get_approved_posts()
    if not posts:
        print("❌ No approved posts found. Approve posts in the dashboard first.")
        return []
    
    schedule = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    
    for i, post in enumerate(posts):
        scheduled_date = current_date + timedelta(days=i)
        entry = {
            "day": i + 1,
            "date": scheduled_date.strftime("%Y-%m-%d"),
            "weekday": scheduled_date.strftime("%A"),
            "stem": post["stem"],
            "image_path": post["image_path"],
            "caption": post["caption"],
            "status": "scheduled",  # scheduled | posted | failed
            "posted_at": None,
            "post_url": None,
        }
        schedule.append(entry)
    
    save_json(SCHEDULE_FILE, schedule)
    print(f"✅ Schedule built: {len(schedule)} posts over {len(schedule)} days")
    print(f"📅 Start: {start_date}")
    print(f"📅 End: {(current_date + timedelta(days=len(schedule)-1)).strftime('%Y-%m-%d')}")
    
    return schedule


def post_todays_content():
    """
    Check if there's a post scheduled for today and post it.
    Called by cron/heartbeat daily.
    """
    schedule = load_json(SCHEDULE_FILE, [])
    if not schedule:
        print("⚠️ No schedule found. Run build_schedule() first.")
        return None
    
    today = datetime.now().strftime("%Y-%m-%d")
    todays_post = None
    
    for entry in schedule:
        if entry["date"] == today and entry["status"] == "scheduled":
            todays_post = entry
            break
    
    if not todays_post:
        print(f"📭 No post scheduled for today ({today}), or already posted.")
        return None
    
    print(f"📸 Posting Day {todays_post['day']}: {todays_post['stem']}")
    print(f"📝 Caption: {todays_post['caption'][:80]}...")
    
    try:
        from execution.instagram_client import post_photo
        media = post_photo(todays_post["image_path"], todays_post["caption"])
        
        # Update schedule
        todays_post["status"] = "posted"
        todays_post["posted_at"] = datetime.now().isoformat()
        todays_post["post_url"] = f"https://www.instagram.com/p/{media.code}/"
        save_json(SCHEDULE_FILE, schedule)
        
        # Log it
        post_log = load_json(POST_LOG_FILE, [])
        post_log.append({
            "date": today,
            "day": todays_post["day"],
            "stem": todays_post["stem"],
            "url": todays_post["post_url"],
            "posted_at": todays_post["posted_at"]
        })
        save_json(POST_LOG_FILE, post_log)
        
        print(f"✅ Posted: {todays_post['post_url']}")
        return todays_post
        
    except Exception as e:
        todays_post["status"] = "failed"
        save_json(SCHEDULE_FILE, schedule)
        print(f"❌ Failed to post: {e}")
        return None


def view_schedule():
    """Print the current schedule."""
    schedule = load_json(SCHEDULE_FILE, [])
    if not schedule:
        print("No schedule found.")
        return
    
    print(f"\n{'='*70}")
    print(f"📅 NEO 30-DAY POSTING SCHEDULE")
    print(f"{'='*70}")
    
    for entry in schedule:
        status_icon = {"scheduled": "⏳", "posted": "✅", "failed": "❌"}.get(entry["status"], "❓")
        print(f"  Day {entry['day']:2d} | {entry['date']} ({entry['weekday'][:3]}) | {status_icon} {entry['status']:10s} | {entry['caption'][:50]}...")
    
    posted = sum(1 for e in schedule if e["status"] == "posted")
    scheduled = sum(1 for e in schedule if e["status"] == "scheduled")
    print(f"\n  📊 Posted: {posted} | Scheduled: {scheduled} | Total: {len(schedule)}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Neo 30-Day Scheduler")
    parser.add_argument("action", choices=["build", "post", "view"], help="build=create schedule, post=post today's content, view=show schedule")
    parser.add_argument("--start", default=None, help="Start date YYYY-MM-DD (default: today)")
    args = parser.parse_args()
    
    if args.action == "build":
        build_schedule(start_date=args.start)
        view_schedule()
    elif args.action == "post":
        post_todays_content()
    elif args.action == "view":
        view_schedule()
