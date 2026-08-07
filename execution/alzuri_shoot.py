"""
Alzuri BKK — Lifestyle Shoot Batch
Generates 10 "lived-in" images for the website using character refs + interior scene.
Output: /Users/tylarkin/Desktop/alzuri-bkk/public/images/generated/
Run: /opt/homebrew/bin/python3.11 execution/alzuri_shoot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

BASE  = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow"
MODELS = f"{BASE}/assets/AI Content Creators/Friends/Black Influencer Models"
FOOD  = "/Users/tylarkin/Downloads/Alzuri Files /FOOD"
SCENE = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/real-interior.jpg"
OUT   = "/Users/tylarkin/Desktop/alzuri-bkk/public/images/generated"
os.makedirs(OUT, exist_ok=True)

SHOTS = [
    {
        "name": "01_bar_cocktail",
        "model": f"{MODELS}/light skin curly hair .jpg",
        "prompt": "A beautiful light-skin woman with curly natural hair sits at a dark moody bar, holding a craft cocktail. She is smiling and relaxed. Warm amber and orange lighting. The background shows a lounge interior with murals. Candid, editorial, film photography feel. Soul food lounge Bangkok vibes.",
    },
    {
        "name": "02_friends_toast",
        "model": f"{MODELS}/Carli.jpg",
        "prompt": "A group of Black friends laughing and clinking cocktail glasses at a lounge table. Stylish, dressed up but relaxed. Jazz and R&B lounge atmosphere. Warm moody lighting, mural wall visible in background. Candid lifestyle photography.",
    },
    {
        "name": "03_man_soul_food",
        "model": f"{MODELS}/Black Man Lightskin Beard .png",
        "prompt": "A light-skin Black man with a beard sits at a dark lounge table, looking down at a cast iron skillet of mac and cheese. His expression is pure satisfaction. Moody warm light. Soul food restaurant Bangkok. Editorial photography.",
    },
    {
        "name": "04_brunch_table",
        "model": f"{MODELS}/Jazmine.jpg",
        "prompt": "A beautiful Black woman smiling brightly during Sunday soul food brunch. Food-filled plates of chicken and waffles on the table. Warm family energy, relaxed dressed-up style. Lounge setting with mural art on walls. Film photography aesthetic.",
    },
    {
        "name": "05_two_women_dining",
        "model": f"{MODELS}/East African Rich Girl .jpg",
        "prompt": "Two stylish women sharing a plate of soul food, laughing together. One reaching across the table. Intimate, warm, joyful. Dark moody lounge background. Candid editorial shot. Bangkok soul food vibes.",
    },
    {
        "name": "06_bar_nightlife",
        "model": f"{MODELS}/East African Rich Girl .jpg",
        "prompt": "A stunning East African woman in an elegant outfit stands at a dark lounge bar. Cocktail in hand, confident energy. Live music happening in the background. Orange and amber lounge lighting. Nightlife editorial photography.",
    },
    {
        "name": "07_couple_dinner",
        "model": f"{MODELS}/Black Man medium curly.png",
        "prompt": "A Black couple at a dinner table in a soulful lounge. Man with medium curly hair, woman across from him smiling. Southern soul food on the table between them. Warm intimate lighting. Mural wall behind them. Date night vibes.",
    },
    {
        "name": "08_natural_hair_brunch",
        "model": f"{MODELS}/Jazmine.jpg",
        "prompt": "A beautiful Black woman laughing joyfully at brunch. Big energy, food and drinks on the table, friends around her (implied). Natural light mixed with warm lounge ambience. Candid lifestyle shot. Soul food culture.",
    },
    {
        "name": "09_music_vibe",
        "model": f"{MODELS}/Black Man Lightskin Beard .png",
        "prompt": "A Black man in a stylish outfit nods to the music in a soulful lounge. Eyes slightly closed, feeling the beat. Live music stage visible in the soft background. Moody blue and orange lounge lighting. Hip-hop R&B atmosphere. Film grain editorial.",
    },
    {
        "name": "10_family_table",
        "model": f"{MODELS}/Carli.jpg",
        "prompt": "A warm family-style table scene at a soul food lounge. Multiple generations — young adults and a family vibe. Plates of soul food covering the table. Everyone laughing and sharing food. Homey but elevated. Bangkok restaurant interior with art murals. Candid photography.",
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/10] Generating: {shot['name']}")
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
        os.rename(path, dest)
        print(f"  → Saved: {dest}")

print("\n✅ Done. Check: /Users/tylarkin/Desktop/alzuri-bkk/public/images/generated/")
