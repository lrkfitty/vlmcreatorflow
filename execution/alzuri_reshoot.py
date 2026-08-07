"""
Alzuri BKK — Reshoot 3 shots (no Angeil)
Regenerates shots 01, 06, 08 with new model refs.
Run: /opt/homebrew/bin/python3.11 execution/alzuri_reshoot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

BASE   = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow"
MODELS = f"{BASE}/assets/AI Content Creators/Friends/Black Influencer Models"
SCENE  = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/real-interior.jpg"
OUT    = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/generated"

SHOTS = [
    {
        "name": "01_bar_cocktail",
        "model": f"{MODELS}/light skin curly hair .jpg",
        "prompt": "A beautiful light-skin woman with curly natural hair sits at a dark moody bar, holding a craft cocktail. She is smiling and relaxed. Warm amber and orange lighting. The background shows a lounge interior with murals. Candid, editorial, film photography feel. Soul food lounge Bangkok vibes.",
    },
    {
        "name": "06_bar_nightlife",
        "model": f"{MODELS}/East African Rich Girl .jpg",
        "prompt": "A stunning East African woman in an elegant outfit stands at a dark lounge bar. Cocktail in hand, confident energy. Live music happening in the background. Orange and amber lounge lighting. Nightlife editorial photography.",
    },
    {
        "name": "08_natural_hair_brunch",
        "model": f"{MODELS}/Jazmine.jpg",
        "prompt": "A beautiful Black woman laughing joyfully at brunch. Big energy, food and drinks on the table, friends around her (implied). Natural light mixed with warm lounge ambience. Candid lifestyle shot. Soul food culture.",
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/{len(SHOTS)}] Generating: {shot['name']}")
    result = generate_image_from_prompt(
        prompt_data={
            "positive_prompt": shot["prompt"],
            "aspect_ratio": "16:9",
            "image_size": "1K",
        },
        output_folder=OUT,
        reference_image_path=shot["model"],
        vibe_path=SCENE,
        engine="gemini",
    )
    status = result.get("status")
    path   = result.get("image_path")
    print(f"  → {status} | {path}")
    if path and os.path.exists(path):
        ext  = os.path.splitext(path)[1]
        dest = os.path.join(OUT, f"{shot['name']}{ext}")
        if os.path.exists(dest):
            os.remove(dest)
        os.rename(path, dest)
        print(f"  → Saved: {dest}")

print("\n✅ Done. Check: /Users/tylarkin/Desktop/alzuri-bkk/public/images/generated/")
