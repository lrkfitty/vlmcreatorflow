"""
Alzuri BKK — Targeted Reshoot
Uses actual main room photo as scene ref. No Angeil.
Generates 4 replacement images with correct orientations.
Run: /opt/homebrew/bin/python3.11 execution/alzuri_targeted_reshoot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

MODELS = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/assets/AI Content Creators/Friends/Black Influencer Models"
SCENE  = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/alzuri-main-room.jpg"
OUT    = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/generated"

SHOTS = [
    {
        # ABOUT section — portrait card (tall)
        "name": "05_two_women_dining",
        "model": f"{MODELS}/Carli.jpg",
        "aspect": "9:16",
        "prompt": (
            "Two stylish Black women laughing and sharing soul food at a lounge table. "
            "Warm candlelit atmosphere, mural art visible on wall behind them. "
            "Red booth seating, copper table lamp glowing. Food plates on the table. "
            "Intimate, joyful, editorial portrait. The actual Alzuri lounge in Bangkok."
        ),
    },
    {
        # MUSIC section — portrait card (tall)
        "name": "06_bar_nightlife",
        "model": f"{MODELS}/Brown girl big chest.jpg",
        "aspect": "9:16",
        "prompt": (
            "A gorgeous Brown-skin woman in an elegant dress stands confidently at a lounge bar, "
            "cocktail in hand. Behind her: the open Alzuri main room with its colorful murals and "
            "blue ambient stage lighting. Live music happening in the background. "
            "Nightlife editorial portrait. Moody warm tones."
        ),
    },
    {
        # EVENTS banner — full-width landscape
        "name": "04_brunch_table",
        "model": f"{MODELS}/Jazmine.jpg",
        "aspect": "16:9",
        "prompt": (
            "A group of Black friends laughing and toasting at a Sunday soul food brunch. "
            "Wide shot of the table — plates of chicken and waffles, cocktails, people reaching "
            "across the table. Alzuri lounge interior with murals on the walls, blue ambient light, "
            "warm candles on tables. Candid, joyful, community energy. Editorial wide angle."
        ),
    },
    {
        # FOOD section pull banner — full-width landscape
        "name": "03_man_soul_food",
        "model": f"{MODELS}/Black Man Lightskin Beard .png",
        "aspect": "16:9",
        "prompt": (
            "A light-skin Black man with a beard sits at a lounge table, looking down at a "
            "cast iron skillet of mac and cheese. Pure satisfaction on his face. "
            "The Alzuri main room surrounds him — mural wall, blue ambient lighting, "
            "other diners visible softly in background. Editorial food portrait, wide framing."
        ),
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/{len(SHOTS)}] Generating: {shot['name']} ({shot['aspect']})")
    result = generate_image_from_prompt(
        prompt_data={
            "positive_prompt": shot["prompt"],
            "aspect_ratio": shot["aspect"],
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
    else:
        print(f"  ✗ FAILED — no image returned")

print("\n✅ Done.")
