"""
Neo Instagram Launch Grid V2 — 9 Posts with REAL outfit & environment refs
Uses Neo's actual wardrobe and custom environments.
"""
import os
import sys
import json
import time
import random

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from execution.generate_image import generate_image_from_prompt

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NEO_REF = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo.png")
OUTFITS_DIR = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo Outfits", "Mens clothing")
ENVS_DIR = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo Environments")
OUTPUT_DIR = os.path.join(BASE, "output", "users", "Neo", "Instagram")

# Map real assets to posts
LAUNCH_POSTS = [
    # --- POST 1: Inside the car, counting money ---
    {
        "id": "lifestyle_car",
        "positive_prompt": (
            "Cinematic photograph of this man sitting in the driver seat of a luxury car interior. "
            "He's casually counting a stack of cash, relaxed expression, one hand on the steering wheel. "
            "Interior lit by warm ambient light. Leather seats visible. "
            "Shot through the driver window at a slight angle. Shallow depth of field. "
            "Luxury lifestyle editorial. Film grain. Shot on 50mm f/1.2. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "burgundy outfit .png",
        "environment": "inside Neos car counting.jpg",
        "caption": "Moved in silence. Let the numbers talk.\n\n#AIMedia #VisualStorytelling #LuxuryLife #VLM #Neo",
    },

    # --- POST 2: Runway / Fashion forward ---
    {
        "id": "fashion_runway",
        "positive_prompt": (
            "Full body editorial photograph of this man walking down a fashion runway or high-end corridor. "
            "Confident stride, stoic expression, commanding presence. "
            "Dramatic fashion show lighting — spotlights from above, dark surroundings. "
            "High fashion editorial. Clean composition. Professional runway photography. "
            "Shot on Canon R5, 70-200mm f/2.8. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Rick Owens Fit .jpg",
        "environment": "neo runway.jpg",
        "caption": "Didn't walk into fashion. Fashion walked into the frame I built.\n\n#AIInfluencer #FashionEditorial #RunwayReady #CreateFlow #VLM",
    },

    # --- POST 3: With his girl, intimate ---
    {
        "id": "couple_intimate",
        "positive_prompt": (
            "Intimate editorial photograph of this man with a beautiful woman. "
            "They're close together, natural chemistry, warm lighting. "
            "He has his arm around her waist. Both looking off-camera with subtle smiles. "
            "Lifestyle couple shot. Warm golden tones, soft bokeh background. "
            "Aspirational relationship content. Shot on 85mm f/1.4. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "West Coast Floral Shirt .png",
        "environment": "with his girl.jpg",
        "caption": "Some things you don't caption. You just live them.\n\n#AIMedia #CoupleGoals #VisualStorytelling #LifestyleContent #Neo",
    },

    # --- POST 4: Office setup, working ---
    {
        "id": "office_creative",
        "positive_prompt": (
            "Editorial photograph of this man at a modern creative workstation. "
            "Multiple monitors showing design work and analytics. Clean desk setup. "
            "He's focused, reviewing content on screen. One hand on the mouse. "
            "Moody ambient lighting from the screens. Professional but creative atmosphere. "
            "Behind-the-scenes of a digital creative director. "
            "Shot on 35mm, shallow depth of field. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Simple Tanke and Green .png",
        "environment": "office setup.jpg",
        "caption": "The studio at 2 AM hits different. This is where the work lives.\n\n#AIMedia #CreativeDirector #StudioLife #CreateFlow #VLM",
    },

    # --- POST 5: Front yard, casual flex ---
    {
        "id": "casual_frontyard",
        "positive_prompt": (
            "Casual lifestyle photograph of this man standing in front of a modern house entrance. "
            "Relaxed pose, one hand in pocket. Warm natural daylight. "
            "Clean landscaping visible. Aspirational home lifestyle. "
            "Street style meets luxury living. Natural, unstaged feel. "
            "Shot on 50mm, golden hour light. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Everyday black and Red .png",
        "environment": "front yard.jpg",
        "caption": "Home base. Where the vision starts before anyone sees it.\n\n#AIInfluencer #LifestyleContent #StreetStyle #VLM #Neo",
    },

    # --- POST 6: Louis Vuitton fit, portrait ---
    {
        "id": "portrait_lv",
        "positive_prompt": (
            "Close-up portrait photograph of this man in designer clothing. "
            "Dramatic studio lighting — single key light from the side. "
            "Dark background. Confident, piercing gaze directly into camera. "
            "Tattoos visible. Ultra sharp detail. "
            "High fashion portrait. Campaign-quality. "
            "Shot on Hasselblad, 80mm, f/2.8. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Louis Vutton Brown fit .png",
        "environment": None,
        "caption": "Every detail is a decision. Nothing accidental.\n\n#AIMedia #HighFashion #CreativeDirection #VisualStorytelling #VLM",
    },

    # --- POST 7: Brown Jordan hoodie, street ---
    {
        "id": "street_hoodie",
        "positive_prompt": (
            "Street style photograph of this man walking through an urban environment. "
            "Modern architecture, clean lines, concrete and glass. "
            "Mid-stride, natural movement. Confident body language. "
            "Overcast day, soft diffused light. Slight desaturation, cool tones. "
            "Streetwear editorial. Shot on Leica Q3, 28mm. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Brow Jordan hoodie.png",
        "environment": None,
        "caption": "Streets raised the aesthetic. AI refined it.\n\n#AIInfluencer #StreetStyle #UrbanEditorial #CreateFlow #Neo",
    },

    # --- POST 8: Hoop fit, active lifestyle ---
    {
        "id": "active_hoops",
        "positive_prompt": (
            "Action lifestyle photograph of this man on a basketball court. "
            "He's standing with a basketball under one arm, post-game vibe. "
            "Warm afternoon sun casting long shadows on the court. "
            "Slight sweat visible. Relaxed, confident posture. "
            "Athletic lifestyle editorial. Vibrant but not oversaturated. "
            "Shot on 70mm, wide aperture. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "Hoop Fit 1 Pink AE.png",
        "environment": None,
        "caption": "Balance. Court and canvas. Both require vision.\n\n#AIMedia #ActiveLifestyle #BasketballCulture #VLM #Neo",
    },

    # --- POST 9: Neo with his girl V2, power couple ---
    {
        "id": "couple_power",
        "positive_prompt": (
            "Editorial photograph of this man and a beautiful woman together, power couple energy. "
            "Both well-dressed, standing close. Modern luxury setting. "
            "She's looking at him, he's looking at the camera. Quiet confidence. "
            "Warm, cinematic lighting. Shallow depth of field. "
            "Aspirational couple content. High-end lifestyle magazine aesthetic. "
            "Shot on 85mm f/1.4, slight film grain. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "outfit": "mens fsll brown fit.png",
        "environment": "neo with his girl.jpg",
        "caption": "Built something worth sharing. Not everything — just enough.\n\n#AIInfluencer #PowerCouple #VisualStorytelling #LifestyleContent #VLM",
    },
]


def generate_post(post, index):
    """Generate a single post with outfit and environment refs."""
    print(f"\n{'='*60}")
    print(f"[{index+1}/9] Generating: {post['id']}")
    print(f"{'='*60}")

    assets = [
        {"path": NEO_REF, "label": "Main Character"}
    ]

    # Add outfit reference
    if post.get("outfit"):
        outfit_path = os.path.join(OUTFITS_DIR, post["outfit"])
        if os.path.exists(outfit_path):
            assets.append({"path": outfit_path, "label": "Outfit for Main Character"})
            print(f"  👔 Outfit: {post['outfit']}")
        else:
            print(f"  ⚠️ Outfit not found: {outfit_path}")

    # Add environment reference
    if post.get("environment"):
        env_path = os.path.join(ENVS_DIR, post["environment"])
        if os.path.exists(env_path):
            assets.append({"path": env_path, "label": "Scene Location/Vibe"})
            print(f"  🌆 Environment: {post['environment']}")
        else:
            print(f"  ⚠️ Environment not found: {env_path}")

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
        print(f"  📝 Caption saved")
    else:
        print(f"  ❌ FAILED: {post['id']}")
        print(result.get("logs", "No logs")[:500])

    return result


def main():
    print("🚀 Neo Instagram Launch Grid V2 — With Real Assets")
    print(f"Reference: {NEO_REF}")
    print(f"Outfits: {OUTFITS_DIR}")
    print(f"Environments: {ENVS_DIR}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    if not os.path.exists(NEO_REF):
        print(f"❌ Neo reference not found")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    results = []
    for i, post in enumerate(LAUNCH_POSTS):
        result = generate_post(post, i)
        results.append({"id": post["id"], "status": result["status"], "path": result.get("image_path")})
        if i < len(LAUNCH_POSTS) - 1:
            print("  ⏳ Cooling down 3s...")
            time.sleep(3)

    # Summary
    print(f"\n{'='*60}")
    print("📊 GENERATION SUMMARY V2")
    print(f"{'='*60}")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"✅ Success: {success}/9")
    print(f"❌ Failed: {9 - success}/9")
    for r in results:
        icon = "✅" if r["status"] == "success" else "❌"
        print(f"  {icon} {r['id']}: {r.get('path', 'N/A')}")

    manifest_path = os.path.join(OUTPUT_DIR, "launch_manifest_v2.json")
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📋 Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
