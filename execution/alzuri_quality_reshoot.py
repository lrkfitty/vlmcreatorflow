"""
Alzuri — Quality reshoot: 4K, no real people in scene, clothing specified.
Fixes: tie-dye real person (use real-interior not main-room), shirtless man.
Run: /opt/homebrew/bin/python3.11 execution/alzuri_quality_reshoot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

MODELS = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/assets/AI Content Creators/Friends/Black Influencer Models"
SCENE  = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/real-interior.jpg"
OUT    = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/generated"

SHOTS = [
    {
        "name": "05_two_women_dining",
        "model": f"{MODELS}/East African Rich Girl .jpg",
        "prompt": (
            "Two stylish Black women laughing and sharing soul food at a dark lounge table. "
            "Both wearing elegant dressed-up outfits — one in a fitted dress, one in stylish separates. "
            "No tie-dye. Warm candlelight, mural art on wall behind them, copper table lamp glowing. "
            "Soul food plates on the table — chicken, mac and cheese. "
            "Intimate, joyful, editorial portrait. Alzuri Bangkok lounge ambiance."
        ),
    },
    {
        "name": "04_brunch_table",
        "model": f"{MODELS}/Jazmine.jpg",
        "prompt": (
            "A group of stylish Black women and friends laughing, clinking champagne glasses at a "
            "Sunday soul food brunch table. All wearing cute brunch outfits — dresses, stylish tops. "
            "No tie-dye clothing. Food and mimosas on the table. "
            "Dark moody lounge background, mural wall, warm candles. "
            "Candid joyful group shot. Alzuri Bangkok soul food lounge vibes."
        ),
    },
    {
        "name": "03_man_soul_food",
        "model": f"{MODELS}/Black Man Lightskin Beard .png",
        "prompt": (
            "A well-dressed light-skin Black man with a beard sitting at a lounge table, "
            "wearing a stylish button-up shirt or fitted polo — fully clothed. "
            "He looks down at a plate of mac and cheese with pure satisfaction. "
            "Dark lounge interior, mural wall in background, warm amber lighting. "
            "Editorial food portrait. Alzuri Bangkok restaurant."
        ),
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/{len(SHOTS)}] Generating 4K: {shot['name']}")
    result = generate_image_from_prompt(
        prompt_data={
            "positive_prompt": shot["prompt"],
            "aspect_ratio": "16:9",
            "image_size": "4K",
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
    else:
        print(f"  ✗ FAILED — {result.get('error', 'no info')}")

print("\n✅ Done.")
