"""
Alzuri BKK — Instagram Grid Shoot (6 images)
Generates composite scenes: real Alzuri models inside the actual restaurant.
Output: /Users/tylarkin/Desktop/alzuri-bkk/public/images/ig-*.jpg
Run: /opt/homebrew/bin/python3.11 execution/alzuri_ig_grid_shoot.py
"""
import sys, os, shutil
sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

FOOD    = "/Users/tylarkin/Downloads/Alzuri Files /FOOD"
MODELS  = f"{FOOD}/Main room and Models"
OUT_TMP = "/Users/tylarkin/Desktop/AI Cnntent Creator workflow/output/alzuri_ig"
OUT_WEB = "/Users/tylarkin/Desktop/alzuri-bkk/public/images"

os.makedirs(OUT_TMP, exist_ok=True)
os.makedirs(OUT_WEB, exist_ok=True)

# THE main room: blue lighting, Eddie Murphy / Biggie / Lil Wayne mural, ALZURI banquette signage
MAIN_ROOM   = f"{MODELS}/IMG_8386.jpg"
MAIN_ROOM_2 = f"{MODELS}/IMG_8385.jpg"  # wide jazz mural shot, same blue-lit room

# 6 unique models — no repeats
M1 = f"{MODELS}/gen_dalle_1776974404_0502f67f.jpg"   # woman, black zip-up jumpsuit
M2 = f"{MODELS}/gen_dalle_1776973592_4aec4e3a.jpg"   # woman, navy mini dress
M3 = f"{MODELS}/gen_dalle_1777406738_af31f2c1.jpg"   # woman, braids, white crop top
M4 = f"{MODELS}/gen_nano2_1778179644_488eef13.jpg"   # duo: hat+bob blonde & sleek ponytail
M5 = f"{MODELS}/gen_nano2_1778178726_cd5dc04b.jpg"   # duo: two women, colorful fits

SHOTS = [
    {
        "name": "ig-room-1",
        "prompt": (
            "Photorealistic candid lifestyle Instagram photo shot inside a moody upscale lounge. "
            "The woman from the reference image is seated at a small black round table, leaning forward "
            "mid-laugh at something someone said off camera — she is NOT looking at the camera. "
            "Her cocktail glass is in hand. Behind her: the exact black leather chairs, "
            "black-and-white hip-hop icon portrait murals on white walls, blue accent lighting, "
            "and 'ALZURI' lettering on the dark banquette from the location reference. "
            "Candid, 35mm editorial, bokeh background. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Cast: Model (FACE & IDENTITY SOURCE - MATCH EXACTLY)", "path": M1},
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM},
        ],
    },
    {
        "name": "ig-room-2",
        "prompt": (
            "Photorealistic candid lifestyle Instagram photo shot inside a moody upscale lounge. "
            "The woman from the reference image is standing near the back of the room, looking up "
            "at the large painted jazz mural on the wall — her side profile visible, NOT facing camera. "
            "She holds a wine glass, admiring the mural art. "
            "Behind her: the exact jazz scene mural, black circular tables, black leather chairs, "
            "deep blue overhead lighting from the location reference. "
            "Candid, editorial. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Cast: Model (FACE & IDENTITY SOURCE - MATCH EXACTLY)", "path": M2},
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM_2},
        ],
    },
    {
        "name": "ig-model-1",
        "prompt": (
            "Photorealistic candid lifestyle Instagram photo shot inside a moody upscale soul food lounge. "
            "The woman from the reference image is seated at a booth, looking down at a plate of food "
            "being set on the table — she is NOT looking at the camera. "
            "Her braids fall to one side. The 'ALZURI' banquette lettering and the black-and-white "
            "portrait murals of Eddie Murphy and rappers are clearly visible in the background, "
            "with vivid blue accent lighting exactly as in the location reference. "
            "Candid, film photography aesthetic. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Cast: Model (FACE & IDENTITY SOURCE - MATCH EXACTLY)", "path": M3},
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM},
        ],
    },
    {
        "name": "ig-girls",
        "prompt": (
            "Photorealistic candid lifestyle Instagram photo shot inside a moody upscale lounge. "
            "The two women from the reference image are seated across from each other at a black table — "
            "one is whispering something into the other's ear and they are both laughing. "
            "Neither is looking at the camera. Cocktails and a plate of soul food are on the table. "
            "Behind them: the black-and-white hip-hop legend murals, blue accent lights, dark banquette "
            "with 'ALZURI' lettering, exactly as shown in the location reference. "
            "Candid, editorial, warm mood lighting. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Cast: Models (FACE & IDENTITY SOURCE - MATCH EXACTLY)", "path": M4},
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM},
        ],
    },
    {
        "name": "ig-crab",
        "prompt": (
            "Photorealistic close-up food Instagram photo. King crab legs piled dramatically in a white "
            "bowl with corn, Cajun butter glaze, green onion garnish — shot on a dark table. "
            "Background: blurred black leather chairs and the exact black-and-white portrait murals "
            "with blue accent lighting from the location reference. No models. "
            "Food magazine quality. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM},
            {"label": "Food Reference", "path": f"{FOOD}/Untitled design - 12.png"},
        ],
    },
    {
        "name": "ig-mac",
        "prompt": (
            "Photorealistic candid lifestyle Instagram photo shot inside a moody upscale lounge. "
            "The two women from the reference image are both looking at a large cast iron skillet of "
            "melting mac and cheese being placed on their table — reacting with excitement, mouths open, "
            "NOT looking at camera. Blue ambient lighting illuminates their faces. "
            "Behind them: the hip-hop legend murals and blue accent wall from the location reference. "
            "Candid lifestyle editorial. Square 1:1. No watermarks."
        ),
        "assets": [
            {"label": "Cast: Models (FACE & IDENTITY SOURCE - MATCH EXACTLY)", "path": M5},
            {"label": "Location Reference - MATCH THIS ROOM EXACTLY", "path": MAIN_ROOM},
            {"label": "Food Reference", "path": f"{FOOD}/Untitled design - 9.png"},
        ],
    },
]

for i, shot in enumerate(SHOTS):
    print(f"\n[{i+1}/{len(SHOTS)}] Generating: {shot['name']}")
    result = generate_image_from_prompt(
        prompt_data={
            "positive_prompt": shot["prompt"],
            "aspect_ratio":    "1:1",
            "image_size":      "1K",
            "assets":          shot["assets"],
        },
        output_folder=OUT_TMP,
        engine="gemini",
    )
    status = result.get("status")
    path   = result.get("image_path")
    print(f"  → {status} | {path}")

    if path and os.path.exists(path):
        ext  = os.path.splitext(path)[1] or ".jpg"
        dest = os.path.join(OUT_TMP, f"{shot['name']}{ext}")
        os.rename(path, dest)
        web  = os.path.join(OUT_WEB, f"{shot['name']}-v3.jpg")
        shutil.copy2(dest, web)
        size = os.path.getsize(web) // 1024
        print(f"  → Web: {web} ({size}KB)")
    else:
        print(f"  ✗ FAILED: {result.get('logs','')}")

print("\n✅ Done — images in:", OUT_WEB)
