"""
Neo Instagram Launch Grid — 9 Posts
Generates editorial images using Neo's reference + CreateFlow pipeline.
"""
import os
import sys
import json
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from execution.generate_image import generate_image_from_prompt

NEO_REF = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "AI Content Creators", "Friends", "Mens Friends", "Neo.png"
)

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "output", "users", "Neo", "Instagram"
)

# 9-post launch grid: 3 portrait, 3 editorial 3/4, 3 environmental wide
LAUNCH_POSTS = [
    # --- PORTRAITS (Personal brand anchors) ---
    {
        "id": "portrait_01",
        "type": "portrait",
        "positive_prompt": (
            "Close-up portrait photograph of this man in a modern creative studio. "
            "Moody dramatic lighting, dark background with subtle warm rim light. "
            "He wears a fitted black turtleneck. Tattoos visible on his neck. "
            "Expression: calm, confident, direct eye contact with camera. "
            "Shot on Sony A7IV, 85mm f/1.4, shallow depth of field. "
            "Editorial fashion photography, high contrast, film grain. "
            "Aspect ratio 4:5 (Instagram portrait)."
        ),
        "aspect_ratio": "4:5",
        "caption": "The work speaks. Everything else is noise.\n\n#AIMedia #VisualStorytelling #CreativeDirection #VLM #Neo",
    },
    {
        "id": "portrait_02",
        "type": "portrait",
        "positive_prompt": (
            "Portrait photograph of this man, golden hour natural light streaming through floor-to-ceiling windows. "
            "He wears an earth-tone linen shirt, slightly unbuttoned. Tattoos visible on forearms and chest. "
            "Warm, contemplative expression. Looking slightly off-camera. "
            "Clean minimal interior background — concrete and glass. "
            "Shot on Hasselblad medium format, 80mm, soft bokeh. "
            "Luxury lifestyle editorial. Warm color grading. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "Built different. Not louder — sharper.\n\n#AIInfluencer #CreativeDirector #VisualStorytelling #MediaProduction #VLM",
    },
    {
        "id": "portrait_03",
        "type": "portrait",
        "positive_prompt": (
            "Headshot photograph of this man against a solid charcoal grey backdrop. "
            "Clean studio lighting — soft key light with subtle fill. "
            "He wears a tailored black blazer over a white crew neck t-shirt. "
            "Confident half-smile. Direct gaze. Tattoos visible on hands and neck. "
            "Campaign-style portrait. Ultra sharp. Minimal post-processing. "
            "Shot on Phase One IQ4, 110mm. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "Every frame is a decision. Make it count.\n\n#AIMedia #CreateFlow #DigitalCreative #VLM #Neo",
    },

    # --- EDITORIAL 3/4 (Lifestyle, environment-forward) ---
    {
        "id": "editorial_01",
        "type": "editorial",
        "positive_prompt": (
            "Three-quarter body shot of this man walking through a sleek modern art gallery. "
            "White walls, concrete floors, large abstract paintings visible behind him. "
            "He wears fitted black trousers, a dark olive bomber jacket, and clean white sneakers. "
            "Tattoos visible. Mid-stride, natural movement. Looking ahead with purpose. "
            "Natural overhead gallery lighting with warm accents. "
            "Cinematic street style photography. Shot on Leica SL2, 50mm Summilux. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "Moved through the space like it was built for this moment. It wasn't. That's the point.\n\n#AIMedia #VisualStorytelling #CreativeLife #ArtDirection #VLM",
    },
    {
        "id": "editorial_02",
        "type": "editorial",
        "positive_prompt": (
            "Three-quarter editorial shot of this man seated on a modern leather chair in a high-end co-working space. "
            "Laptop open on the table beside him, but his attention is elsewhere — looking out a large window. "
            "He wears a monochrome outfit — black fitted joggers, charcoal crew neck sweater. "
            "Tattoos on arms visible. Relaxed but intentional posture. "
            "Soft diffused daylight. Clean, minimal space with plants and concrete accents. "
            "Aspirational tech-creative lifestyle. Shot on Canon R5, 35mm f/1.4. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "Quiet work. Loud results.\n\n#AIInfluencer #CreateFlow #TechCreative #DigitalMedia #Neo",
    },
    {
        "id": "editorial_03",
        "type": "editorial",
        "positive_prompt": (
            "Three-quarter body shot of this man standing on a rooftop terrace at blue hour (dusk). "
            "City skyline behind him, slightly blurred. Warm string lights in background. "
            "He wears a fitted black henley shirt and dark denim. Tattoos on forearms. "
            "Leaning against a concrete railing, coffee in hand. Calm, stoic expression. "
            "Cinematic blue-orange color grade. Shot on Sony A7IV, 50mm f/1.2. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "The city doesn't sleep. Neither does the vision.\n\n#AIMedia #VisualStorytelling #CreativeDirection #Nightlife #VLM",
    },

    # --- ENVIRONMENTAL WIDE (World is the story) ---
    {
        "id": "wide_01",
        "type": "wide",
        "positive_prompt": (
            "Wide environmental shot of this man in a dark, professional photography studio. "
            "He stands reviewing images on a large monitor, back partially to camera. "
            "Studio lights, equipment, and camera gear visible. "
            "He wears all black — fitted black t-shirt and black cargo pants. Tattoos visible. "
            "The monitor shows a grid of editorial photographs. "
            "Documentary-style behind-the-scenes. Moody, atmospheric. "
            "Shot on 24mm wide angle. Slight film grain. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "Shot this entire campaign without a single photographer. The world is different now.\n\n#AIMedia #CreateFlow #BehindTheScenes #AIPhotography #VLM",
    },
    {
        "id": "wide_02",
        "type": "wide",
        "positive_prompt": (
            "Wide shot of this man walking down a quiet city street at dawn. "
            "Empty sidewalk, modern architecture, soft morning light casting long shadows. "
            "He wears a long dark overcoat over a simple white t-shirt, dark trousers, boots. "
            "Tattoos visible on hands. Walking with purpose, looking ahead. "
            "Cinematic composition — subject slightly off-center. "
            "Urban fashion editorial. Desaturated, cool tones with warm highlights. "
            "Shot on 35mm film stock, Kodak Portra 400 look. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "First light. First move. Everything starts before anyone's watching.\n\n#AIInfluencer #UrbanStyle #CreativeLife #VisualStorytelling #Neo",
    },
    {
        "id": "wide_03",
        "type": "wide",
        "positive_prompt": (
            "Wide environmental photograph of this man in a luxury minimalist apartment. "
            "Floor-to-ceiling windows overlooking a city at night. Interior is dark with selective warm lighting. "
            "He sits in a designer armchair, reviewing something on a tablet. "
            "He wears a simple fitted grey t-shirt and black pants. Tattoos visible. "
            "Reflections of city lights on the glass. Atmosphere of focus and solitude. "
            "High-end lifestyle editorial. Shot on Leica M11, 28mm Summicron. "
            "Aspect ratio 4:5."
        ),
        "aspect_ratio": "4:5",
        "caption": "AI didn't change creativity. It changed who gets to create.\n\n#AIMedia #CreateFlow #DigitalCreative #FutureOfMedia #VLM",
    },
]


def generate_post(post, index):
    """Generate a single post image."""
    print(f"\n{'='*60}")
    print(f"[{index+1}/9] Generating: {post['id']} ({post['type']})")
    print(f"{'='*60}")
    
    prompt_data = {
        "positive_prompt": post["positive_prompt"],
        "aspect_ratio": post.get("aspect_ratio", "4:5"),
        "image_size": "1K",
        "assets": [
            {
                "path": NEO_REF,
                "label": "Main Character"
            }
        ]
    }
    
    result = generate_image_from_prompt(prompt_data, output_folder=OUTPUT_DIR)
    
    if result["status"] == "success":
        print(f"✅ SUCCESS: {result['image_path']}")
        # Save caption alongside
        caption_path = result["image_path"].rsplit(".", 1)[0] + "_caption.txt"
        with open(caption_path, "w") as f:
            f.write(post["caption"])
        print(f"📝 Caption saved: {caption_path}")
    else:
        print(f"❌ FAILED: {post['id']}")
        print(result.get("logs", "No logs"))
    
    return result


def main():
    print(f"🚀 Neo Instagram Launch Grid Generator")
    print(f"Reference: {NEO_REF}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Posts to generate: {len(LAUNCH_POSTS)}")
    print()
    
    if not os.path.exists(NEO_REF):
        print(f"❌ Neo reference image not found at: {NEO_REF}")
        return
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    results = []
    for i, post in enumerate(LAUNCH_POSTS):
        result = generate_post(post, i)
        results.append({"id": post["id"], "status": result["status"], "path": result.get("image_path")})
        
        # Brief pause between generations to avoid rate limiting
        if i < len(LAUNCH_POSTS) - 1:
            print("⏳ Cooling down 3s...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 GENERATION SUMMARY")
    print(f"{'='*60}")
    success = sum(1 for r in results if r["status"] == "success")
    print(f"✅ Success: {success}/9")
    print(f"❌ Failed: {9 - success}/9")
    for r in results:
        status_icon = "✅" if r["status"] == "success" else "❌"
        print(f"  {status_icon} {r['id']}: {r.get('path', 'N/A')}")
    
    # Save manifest
    manifest_path = os.path.join(OUTPUT_DIR, "launch_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n📋 Manifest saved: {manifest_path}")


if __name__ == "__main__":
    main()
