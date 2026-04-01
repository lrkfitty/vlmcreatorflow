"""
Neo x Shay — Official Couple Content (6 Posts)
Cross-promotional content for both accounts.
Uses both character references for consistent identity.
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from execution.generate_image import generate_image_from_prompt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEO_REF = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo.png")
SHAY_REF = os.path.join(BASE, "assets", "AI Content Creators", "Shay.So.Fine", "SHAY STOCK Photo", "Shay blonde bob back.png")
SHAY_FRONT = os.path.join(BASE, "assets", "AI Content Creators", "Shay.So.Fine", "SHAY STOCK Photo", "Shay blonde bob front .png")
NEO_OUTFITS = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo Outfits", "Mens clothing")
SHAY_OUTFITS_2026 = os.path.join(BASE, "assets", "AI Content Creators", "2026 Jan CLothing ")
NEO_ENVS = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo Environments")
OUTPUT_DIR = os.path.join(BASE, "output", "users", "Neo", "Instagram")

POSTS = [
    # --- 1: Power couple portrait ---
    {
        "id": "couple_01_power_portrait",
        "positive_prompt": (
            "High fashion editorial photograph of this man and this woman together. "
            "Studio setting with dark background and dramatic single key light from the side. "
            "They stand close, facing the camera. He's slightly behind her, one hand on her waist. "
            "Both have confident, composed expressions. Direct eye contact with camera. "
            "She has a blonde bob hairstyle. He has visible tattoos. "
            "Power couple energy. Vogue-level fashion editorial. "
            "Shot on Hasselblad, 80mm f/2.8. High contrast, minimal color palette. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "burgundy outfit .png",
        "shay_outfit": "Green Christian Dior .jpg",
        "environment": None,
        "caption": "Two visions. One frame. The math doesn't lie.\n\n#AIMedia #PowerCouple #VisualStorytelling #VLM #Neo #ShaySoFine",
    },
    # --- 2: Date night / dinner ---
    {
        "id": "couple_02_date_night",
        "positive_prompt": (
            "Intimate cinematic photograph of this man and this woman at an upscale restaurant. "
            "Candlelit table, warm amber tones. They're seated across from each other. "
            "She's laughing naturally, he's smiling watching her. Genuine chemistry. "
            "She has a blonde bob. Wine glasses on the table. Bokeh lights in background. "
            "Romantic luxury date night. Shot on 85mm f/1.4. Film grain. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "Louis Vutton Brown fit .png",
        "shay_outfit": "Pink Brunch Villa .jpg",
        "environment": None,
        "caption": "She makes the moment. I just set the scene.\n\n#AIInfluencer #DateNight #CoupleGoals #VisualStorytelling #VLM",
    },
    # --- 3: Street walk together ---
    {
        "id": "couple_03_street_walk",
        "positive_prompt": (
            "Street style candid photograph of this man and this woman walking down a city sidewalk together. "
            "Both stylishly dressed. He has his arm around her shoulders. "
            "She has a blonde bob, looking up at him smiling. He's looking ahead, slight smile. "
            "Modern urban architecture. Golden hour side lighting casting warm tones. "
            "Couple street style editorial. Natural movement, mid-stride. "
            "Shot on Leica Q3, 28mm. Warm color grade. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "West Coast Floral Shirt .png",
        "shay_outfit": "Jean Outfit with Strings .jpg",
        "environment": None,
        "caption": "Streets know us before the algorithm does.\n\n#AIMedia #CoupleStyle #StreetFashion #ShaySoFine #Neo",
    },
    # --- 4: Matching fit, home/lifestyle ---
    {
        "id": "couple_04_matching_home",
        "positive_prompt": (
            "Lifestyle photograph of this man and this woman in a modern luxury living room. "
            "They're on a large sectional couch together. He's behind her, she's leaning back into him. "
            "Both relaxed and comfortable. Natural daylight from large windows. "
            "She has a blonde bob. Modern minimal interior, neutral tones. "
            "Intimate but aspirational couple content. Authentic, not overly posed. "
            "Shot on 50mm f/1.8. Clean, warm tones. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "Simple Tanke and Green .png",
        "shay_outfit": "Salmon Jogging SUit.jpg",
        "environment": None,
        "caption": "Home is wherever we build the next thing.\n\n#AIInfluencer #CoupleGoals #HomeVibes #LifestyleContent #VLM",
    },
    # --- 5: Poolside / vacation couple ---
    {
        "id": "couple_05_poolside",
        "positive_prompt": (
            "Luxury lifestyle photograph of this man and this woman at an infinity pool overlooking the ocean. "
            "He's in the pool, she's sitting on the edge with her feet in the water. "
            "She has a blonde bob. Bright tropical sunlight, turquoise water. "
            "Both laughing, playful energy. Palm trees in background. "
            "Resort vacation couple content. Vibrant, saturated colors. "
            "Shot on 35mm, wide angle to capture the setting. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "green swim shorts .jpg",
        "shay_outfit": "Scrunch Marble.png",
        "environment": None,
        "caption": "Location scouting. For the content and for us.\n\n#AIMedia #TravelCouple #PoolVibes #VacationMode #ShaySoFine #Neo",
    },
    # --- 6: Working together / creative partners ---
    {
        "id": "couple_06_creative_partners",
        "positive_prompt": (
            "Editorial photograph of this man and this woman in a modern creative studio. "
            "They're both looking at a large monitor showing visual content. She's pointing at the screen. "
            "He's standing beside her, one hand on the desk. Collaborative energy. "
            "She has a blonde bob. Dark studio with screen glow illuminating their faces. "
            "Creative partnership. Behind-the-scenes tech content. "
            "Shot on 35mm, documentary style. Cool tones with warm screen light. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "neo_outfit": "Everyday black and Red .png",
        "shay_outfit": "Green Womens Tech Track Suit .jpg",
        "environment": "office setup.jpg",
        "caption": "She sees the detail I miss. That's not luck — that's design.\n\n#AIMedia #CreativePartners #StudioLife #CreateFlow #VLM",
    },
]


def generate_post(post, index, total):
    print(f"\n{'='*60}")
    print(f"[{index+1}/{total}] Generating: {post['id']}")
    print(f"{'='*60}")

    # Both characters as cast members
    assets = [
        {"path": NEO_REF, "label": "Cast: Neo"},
        {"path": SHAY_REF, "label": "Cast: Shay"},
        {"path": SHAY_FRONT, "label": "Cast: Shay (Ref 2)"},
    ]

    # Neo outfit
    if post.get("neo_outfit"):
        outfit_path = os.path.join(NEO_OUTFITS, post["neo_outfit"])
        if os.path.exists(outfit_path):
            assets.append({"path": outfit_path, "label": "Outfit for Neo"})
            print(f"  👔 Neo outfit: {post['neo_outfit']}")

    # Shay outfit
    if post.get("shay_outfit"):
        outfit_path = os.path.join(SHAY_OUTFITS_2026, post["shay_outfit"])
        if os.path.exists(outfit_path):
            assets.append({"path": outfit_path, "label": "Outfit for Shay"})
            print(f"  👗 Shay outfit: {post['shay_outfit']}")

    # Environment
    if post.get("environment"):
        env_path = os.path.join(NEO_ENVS, post["environment"])
        if os.path.exists(env_path):
            assets.append({"path": env_path, "label": "Scene Location/Vibe"})
            print(f"  🌆 Environment: {post['environment']}")

    prompt_data = {
        "positive_prompt": post["positive_prompt"],
        "aspect_ratio": post.get("aspect_ratio", "4:5"),
        "image_size": "1K",
        "assets": assets
    }

    result = generate_image_from_prompt(prompt_data, output_folder=OUTPUT_DIR)

    if result["status"] == "success":
        print(f"  ✅ SUCCESS: {result['image_path']}")
        caption_path = result["image_path"].rsplit(".", 1)[0] + "_caption.txt"
        with open(caption_path, "w") as f:
            f.write(post["caption"])
        meta_path = result["image_path"].rsplit(".", 1)[0] + "_meta.json"
        with open(meta_path, "w") as f:
            json.dump({"id": post["id"], "type": "couple", "caption": post["caption"]}, f, indent=2)
        print(f"  📝 Caption + meta saved")
    else:
        print(f"  ❌ FAILED")
        print(result.get("logs", "")[:500])

    return result


def main():
    print("💑 Neo x Shay — Official Couple Content (6 Posts)")
    print(f"Neo ref: {NEO_REF}")
    print(f"Shay ref: {SHAY_REF}")
    print(f"Output: {OUTPUT_DIR}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []
    total = len(POSTS)
    for i, post in enumerate(POSTS):
        result = generate_post(post, i, total)
        results.append({"id": post["id"], "status": result["status"], "path": result.get("image_path")})
        if i < total - 1:
            print("  ⏳ Cooling down 4s...")
            time.sleep(4)

    print(f"\n{'='*60}")
    print("📊 COUPLE CONTENT SUMMARY")
    print(f"{'='*60}")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"✅ Success: {success}/{total}")
    for r in results:
        icon = "✅" if r["status"] == "success" else "❌"
        print(f"  {icon} {r['id']}")

    manifest_path = os.path.join(OUTPUT_DIR, "couple_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📋 Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
