"""
Alzuri — portrait shots retry with 1:1 aspect ratio
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

MODELS = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/assets/AI Content Creators/Friends/Black Influencer Models"
SCENE  = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/alzuri-main-room.jpg"
OUT    = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/generated"

SHOTS = [
    {
        "name": "05_two_women_dining",
        "model": f"{MODELS}/Carli.jpg",
        "prompt": (
            "Two stylish Black women laughing and sharing soul food at a lounge table. "
            "Warm candlelit atmosphere, colorful mural art visible on wall behind them. "
            "Red booth seating, copper table lamp glowing. Food plates on the table. "
            "Intimate, joyful, editorial portrait. The Alzuri lounge, Bangkok."
        ),
    },
    {
        "name": "06_bar_nightlife",
        "model": f"{MODELS}/Brown girl big chest.jpg",
        "prompt": (
            "A gorgeous brown-skin woman in an elegant outfit at a lounge, "
            "cocktail in hand, smiling confidently. The Alzuri main room behind her — "
            "colorful murals, blue ambient stage lighting, open lounge floor. "
            "Nightlife editorial. Moody warm tones mixed with blue ambient light."
        ),
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/{len(SHOTS)}] Generating: {shot['name']} (1:1)")
    result = generate_image_from_prompt(
        prompt_data={
            "positive_prompt": shot["prompt"],
            "aspect_ratio": "1:1",
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
        print(f"  ✗ FAILED")

print("\n✅ Done.")
