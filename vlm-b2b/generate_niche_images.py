"""
Generate niche hero images for the B2B sales page using Google Imagen.
Run once: python3 generate_niche_images.py
"""
import os, sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    sys.exit("GOOGLE_API_KEY not found in .env")

ASSETS = Path(__file__).parent / "assets"
ASSETS.mkdir(exist_ok=True)

NICHES = [
    {
        "filename": "niche_finance.jpg",
        "prompt": (
            "Cinematic editorial photograph of a sophisticated Black female financial advisor "
            "in a tailored navy suit, sitting at a sleek glass desk in a high-rise Manhattan office "
            "overlooking the city skyline at golden hour. Confident posture, warm professional smile, "
            "laptop and documents on desk. Photorealistic, soft natural lighting, shallow depth of field, "
            "luxury corporate aesthetic, 4K quality."
        ),
    },
    {
        "filename": "niche_agency.jpg",
        "prompt": (
            "Cinematic editorial photo of a diverse creative team in a modern open-plan advertising agency, "
            "reviewing large mood boards and digital screens showing brand campaign visuals. "
            "Exposed brick walls, pendant lighting, MacBooks and tablets visible. "
            "Energetic collaborative atmosphere, warm tones, photorealistic, 4K quality."
        ),
    },
    {
        "filename": "niche_realestate.jpg",
        "prompt": (
            "Cinematic lifestyle photograph of an aspirational young professional couple "
            "standing in the living room of a luxury modern penthouse apartment, floor-to-ceiling windows "
            "with city skyline view, minimalist white interior, warm sunset light filling the space. "
            "Photorealistic, architectural photography style, 4K quality."
        ),
    },
    {
        "filename": "niche_ecommerce.jpg",
        "prompt": (
            "High-fashion editorial photograph of a confident Black female model wearing a sleek, "
            "minimalist designer outfit, standing on the streets of Paris near the Eiffel Tower at dusk. "
            "Luxury fashion campaign aesthetic, cinematic color grading, shallow depth of field, "
            "photorealistic, 4K quality."
        ),
    },
    {
        "filename": "niche_healthcare.jpg",
        "prompt": (
            "Clean editorial photograph of a professional Black female doctor in a crisp white coat "
            "in a modern, bright medical clinic. Warm confident smile, stethoscope, tablet in hand. "
            "Premium healthcare aesthetic, soft studio lighting, credible and trustworthy feel, "
            "photorealistic, 4K quality."
        ),
    },
    {
        "filename": "niche_fitness.jpg",
        "prompt": (
            "Dynamic lifestyle photograph of a fit athletic Black woman in premium branded activewear "
            "doing a powerful yoga pose in a luxury modern gym with floor-to-ceiling windows and natural light. "
            "Motivational energy, cinematic lighting, fitness app campaign aesthetic, "
            "photorealistic, 4K quality."
        ),
    },
    {
        "filename": "niche_consulting.jpg",
        "prompt": (
            "Professional editorial photograph of a confident Black female business coach "
            "giving a keynote presentation on a sleek modern stage, large screen behind her showing "
            "data visualizations, engaged audience silhouettes in foreground. "
            "Cinematic stage lighting, authority and expertise aesthetic, photorealistic, 4K quality."
        ),
    },
]

from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

print(f"Generating {len(NICHES)} niche images...\n")

for niche in NICHES:
    out_path = ASSETS / niche["filename"]
    if out_path.exists():
        print(f"  Skipping {niche['filename']} (already exists)")
        continue

    print(f"  Generating {niche['filename']}...")
    try:
        result = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=niche["prompt"],
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="3:4",
                person_generation="ALLOW_ADULT",
            ),
        )
        if result.generated_images:
            img = result.generated_images[0].image
            with open(out_path, "wb") as f:
                f.write(img.image_bytes)
            print(f"  Saved {niche['filename']}")
        else:
            print(f"  No image returned for {niche['filename']}")
    except Exception as e:
        print(f"  Error generating {niche['filename']}: {e}")

print("\nDone. Images saved to vlm-b2b/assets/")
