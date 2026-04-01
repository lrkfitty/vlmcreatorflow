"""
Ty + Angeil — Couple Content Batch Generator
AI-generated couple lifestyle content for cross-posting.
Ty: heavily muscular, full-body tattoos, athletic build.
Angeil: curvy, long wavy black hair, arm tattoos.
Each post = 3 images (carousel).
"""
import os
import sys
import time
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

from execution.generate_image import generate_image_from_prompt

BASE          = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYRIE_REF     = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Tyrie Master", "Tyrie Hero", "Tyrie.png")
ANGEIL_REF    = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Angeil Master ", "Angeil Hero image", "Angeil.png")
TY_CLOTHING   = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Tyrie Master", "Tyrie Clothing")
ANG_CLOTHING  = os.path.join(BASE, "assets", "AI Content Creators", "Friends", "Angeil Master ", "Angeil Clothing")
ENVS_DIR      = os.path.join(BASE, "assets", "AI Content Creators", "Environments")
OUTPUT_DIR    = os.path.join(BASE, "output", "users", "Tyrie", "Instagram", "couple")

HASHTAGS = (
    "#AICouple #AIContent #AICreator #AIInfluencer #CreateFlow "
    "#AIGeneratedContent #AIMedia #CoupleGoals #DigitalCreator "
    "#BuildInPublic #AITools #SkoolCommunity #CreatorEconomy #VLM #Bangkok"
)
CTA = "AI-generated content. Built with CreateFlow.\nJoin the community → link in bio."

CHAR_TY = (
    "The male subject is a tall, heavily muscular Black man with full-body tattoos covering both arms, chest, and back. "
    "Athletic physique, defined muscle, natural confidence. Short fade haircut. "
)
CHAR_ANGEIL = (
    "The female subject is a curvy Black woman with long flowing wavy black hair, "
    "tattoos on her arm, beautiful natural features, confident and elegant presence. "
)
BOTH = f"{CHAR_TY}{CHAR_ANGEIL}They are a couple — natural chemistry, not posed or stiff. "

CAROUSELS = [
    {
        "id": "couple01_rooftop_sunset",
        "ty_outfit": "Monaco Outfit.jpg",
        "ang_outfit": "saints lady fit .jpg",
        "caption": f"Built this together.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Standing together on a Bangkok rooftop at golden hour. He's behind her, arms around her. Both looking out at the city skyline. Intimate and powerful. Shot on 85mm f/1.4. Aspect ratio 4:5.",
            f"{BOTH}Side-by-side at the rooftop railing, both looking at camera. Confident couple energy. Tattoos visible on both. Bangkok sunset behind them. Editorial lifestyle. Aspect ratio 4:5.",
            f"{BOTH}Wide rooftop shot — the two of them small against the massive Bangkok skyline at dusk. Scale and intimacy. 24mm cinematic. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple02_luxury_dinner",
        "ty_outfit": "Monaco Outfit.jpg",
        "ang_outfit": "brown dainty fit .jpg",
        "caption": f"The real flex is who you're building with.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Seated across from each other at an upscale Bangkok restaurant. Candlelight, dark intimate atmosphere. Both impeccably dressed. Leaning in, mid-conversation. Warm amber tones. Shot on 85mm. Aspect ratio 4:5.",
            f"{BOTH}His tattooed hand reaching across the table to hold her hand. Wine glasses and elegant table setting visible. Romantic detail shot. Close-up. Aspect ratio 4:5.",
            f"{BOTH}Wide restaurant shot — the couple at their table, the full elegant dining room behind them. Luxury and intimacy. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple03_beach_thailand",
        "ty_outfit": "drip khaki .png",
        "ang_outfit": "orange 2 fit.jpg",
        "caption": f"When the work takes you here, you bring the right person.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Walking along a Thai island beach together, hand in hand. Turquoise water, white sand. Both relaxed and happy. Tattoos vivid in the tropical light. Aspect ratio 4:5.",
            f"{BOTH}She's looking back at him over her shoulder, playful smile. He's watching her, natural smile. Candid beach moment. Golden light. Aspect ratio 4:5.",
            f"{BOTH}Wide beach shot — the two of them small against dramatic limestone cliffs and ocean. Epic travel photography. 24mm. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple04_street_style",
        "ty_outfit": "blue Outfit .png",
        "ang_outfit": "orange blue jean fit .jpg",
        "caption": f"Two creators. One vision.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Walking Bangkok streets at night together, side by side. Neon reflections on wet pavement. Both stylish, confident. Tattoos catching the neon. Cinematic. Aspect ratio 4:5.",
            f"{BOTH}He's leaning against a Bangkok wall, she's leaning back into him. Both looking at camera. Street art behind them. High contrast light. Aspect ratio 4:5.",
            f"{BOTH}Wide urban night shot — the two of them in the foreground, Bangkok neon city spreading behind. Moody and cinematic. 35mm. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple05_morning_routine",
        "ty_outfit": "Grren casual fit .jpg",
        "ang_outfit": "white green floral .jpg",
        "caption": f"The morning routine hits different when you share it.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}At a bright minimalist Bangkok cafe, morning light streaming through. Sitting together over coffee, laughing. Natural, candid. Warm and intimate. Shot on 50mm. Aspect ratio 4:5.",
            f"{BOTH}Close-up — their two coffee cups touching. His tattooed hand and her hand with rings visible. Detail lifestyle shot. Aspect ratio 4:5.",
            f"{BOTH}Wider cafe shot — both at the table, notebooks open, working together. The ideal creator morning. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple06_penthouse",
        "ty_outfit": "ALl saints beige fit.jpg",
        "ang_outfit": "saints lady fit .jpg",
        "caption": f"Different people. Same frequency.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Standing at floor-to-ceiling penthouse windows together, full Bangkok skyline behind them. His arm around her shoulder. Both looking out. Power and calm. Dusk light. Aspect ratio 4:5.",
            f"{BOTH}She's looking up at him, he's looking at the city. Candid intimate moment. Tattoos and city lights. 85mm. Aspect ratio 4:5.",
            f"{BOTH}Wide penthouse interior — the couple at the far window, the full luxury space visible around them. Aspirational. 24mm. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple07_gym_together",
        "ty_outfit": "Crop vibes fit.png",
        "ang_outfit": "bandana ties fit.jpg",
        "caption": f"We don't just build content. We build ourselves.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}In a modern Bangkok gym together. He's spotting her on a lift, focused and supportive. Both athletic. Gym lighting is dramatic. Aspect ratio 4:5.",
            f"{BOTH}Post-workout — both standing in front of the gym mirror, his arm around her. Confident, accomplished. Tattoos on display. Aspect ratio 4:5.",
            f"{BOTH}Wide gym shot — the couple in the foreground, the full modern gym visible behind them. Fitness couple goals. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple08_creator_studio",
        "ty_outfit": "Crop vibes fit.png",
        "ang_outfit": "white green floral .jpg",
        "caption": f"This is what AI content creation looks like behind the scenes.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}In a dark creative studio together, both looking at screens showing AI-generated content. Screen glow on their faces. Collaborating, engaged. Blue and cyan light. Aspect ratio 4:5.",
            f"{BOTH}She's pointing at the screen, he's watching. Creative discussion, natural energy. Tattoos lit by screen glow. Close-up. Aspect ratio 4:5.",
            f"{BOTH}Wide studio shot — both at the desk, multiple screens, the full creative setup visible. This is the operation. 24mm. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple09_pool_resort",
        "ty_outfit": "drip khaki .png",
        "ang_outfit": "orange 2 fit.jpg",
        "caption": f"The lifestyle is the proof of concept.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}At a luxury Thai resort pool surrounded by jungle. Both in the pool, relaxed. Her back against his chest, his tattooed arms around her. Serene and beautiful. Aspect ratio 4:5.",
            f"{BOTH}Poolside — he's on the edge, she's in the water looking up at him. Playful moment. Lush greenery behind. Natural light. Aspect ratio 4:5.",
            f"{BOTH}Wide resort shot — the couple at the pool, the full luxury jungle resort visible around them. Travel editorial. Aspect ratio 4:5.",
        ],
    },
    {
        "id": "couple10_sunset_silhouette",
        "ty_outfit": "green crop fitted .png",
        "ang_outfit": "brown dainty fit .jpg",
        "caption": f"Every sunset is a reminder the best is still ahead.\n\n{CTA}\n\n{HASHTAGS}",
        "shots": [
            f"{BOTH}Silhouette of the couple against a dramatic Bangkok sunset. His arm around her, both facing the orange and pink sky. Powerful outlines. Cinematic. Aspect ratio 4:5.",
            f"{BOTH}Half-lit golden hour portrait — both faces catching the last light. Warm and intimate. Tattoos glowing. 85mm f/1.4. Aspect ratio 4:5.",
            f"{BOTH}Wide golden hour shot — the couple on a rooftop, full Bangkok skyline bathed in sunset behind them. Epic. 24mm. Aspect ratio 4:5.",
        ],
    },
]


def run_batch():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    total = len(CAROUSELS)

    for i, carousel in enumerate(CAROUSELS):
        print(f"\n[Carousel {i+1}/{total}] {carousel['id']}")

        caption_path = os.path.join(OUTPUT_DIR, f"{carousel['id']}_caption.txt")
        with open(caption_path, "w") as f:
            f.write(carousel["caption"])

        ty_outfit_path  = os.path.join(TY_CLOTHING, carousel["ty_outfit"]) if carousel.get("ty_outfit") else None
        ang_outfit_path = os.path.join(ANG_CLOTHING, carousel["ang_outfit"]) if carousel.get("ang_outfit") else None

        for j, shot_prompt in enumerate(carousel["shots"]):
            shot_id  = f"{carousel['id']}_shot{j+1}"
            out_path = os.path.join(OUTPUT_DIR, f"{shot_id}.jpg")

            if os.path.exists(out_path):
                print(f"  [SKIP] shot {j+1} already exists")
                continue

            print(f"  Generating shot {j+1}/3...")

            # Pass both characters and both outfits via the assets system.
            # Outfit labels must use "Outfit for {char_name}" format to trigger pairing.
            # char_name is extracted from "Cast: {name}" → everything after "Cast: "
            assets = [
                {"path": TYRIE_REF,   "label": "Cast: Ty"},
                {"path": ANGEIL_REF,  "label": "Cast: Angeil"},
            ]
            if ty_outfit_path and os.path.exists(ty_outfit_path):
                assets.append({"path": ty_outfit_path,  "label": "Outfit for Ty"})
            if ang_outfit_path and os.path.exists(ang_outfit_path):
                assets.append({"path": ang_outfit_path, "label": "Outfit for Angeil"})

            result = generate_image_from_prompt(
                prompt_data={
                    "positive_prompt": shot_prompt,
                    "aspect_ratio": "4:5",
                    "image_size": "4K",
                    "assets": assets,
                },
                output_folder=OUTPUT_DIR,
                reference_image_path=None,
                outfit_path=None,
                vibe_path=None,
            )

            if result.get("status") == "success" and result.get("image_path"):
                src = result["image_path"]
                if src != out_path:
                    shutil.move(src, out_path)
                print(f"  Saved: {out_path}")
            else:
                print(f"  FAILED shot {j+1}: {result.get('logs', '')}")

            time.sleep(2)

    print(f"\nDone. {total} couple carousels -> {OUTPUT_DIR}")


if __name__ == "__main__":
    run_batch()
