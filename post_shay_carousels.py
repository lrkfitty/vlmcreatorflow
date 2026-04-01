#!/usr/bin/env python3
"""Post approved Shay carousels to Instagram"""

import json
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path.cwd() / "execution"))

BASE = Path.cwd()
SHAY_SCHEDULE = BASE / ".tmp" / "shay_schedule.json"
APPROVED_FILE = BASE / ".tmp" / "approved_posts.json"

# Load schedule
with open(SHAY_SCHEDULE) as f:
    schedule = json.load(f)

# Load approvals
with open(APPROVED_FILE) as f:
    approved = json.load(f)
shay_approvals = approved.get("shay", {})

# Get first 2 approved carousels
approved_carousels = [p for p in schedule if p.get("carousel_id") in shay_approvals and p.get("status") != "posted"][:2]

if not approved_carousels:
    print("✗ No approved unpublished carousels")
    sys.exit(0)

try:
    from instagram_client import post_carousel
    from dotenv import load_dotenv
    load_dotenv()
    
    for carousel in approved_carousels:
        carousel_id = carousel.get("carousel_id")
        day = carousel.get("day")
        images = carousel.get("images", [])
        caption = carousel.get("caption", "")
        
        image_paths = [str(img) for img in images if Path(img).exists()]
        if not image_paths:
            print(f"✗ Day {day}: Images missing")
            continue
        
        try:
            print(f"📤 Day {day}: Posting {len(image_paths)} images to Shay...")
            post_carousel(image_paths, caption, account="shay")
            
            for post in schedule:
                if post.get("carousel_id") == carousel_id:
                    post["status"] = "posted"
                    post["posted_at"] = datetime.now().isoformat()
            
            print(f"✓ Day {day}: Posted!")
        except Exception as e:
            print(f"✗ Day {day}: {str(e)[:100]}")
    
    with open(SHAY_SCHEDULE, 'w') as f:
        json.dump(schedule, f, indent=2)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
