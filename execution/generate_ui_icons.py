"""
Generate photorealistic UI icons for the visual grid selectors.
Uses Google Gemini's image generation API.
Run: python3 execution/generate_ui_icons.py
"""
import os
import sys
import time
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# -- Config --
ICONS_ROOT = Path(__file__).parent.parent / "assets" / "ui_icons"
CATEGORIES = {
    "camera_angles": {
        "Eye Level (Neutral)":        "Photorealistic cinematic photo, eye-level camera angle straight on, woman in neutral standing pose, camera at eye height, studio lighting, dark background, clean composition",
        "Low Angle (Heroic/Power)":   "Photorealistic cinematic photo, dramatic low angle shot looking up at confident woman, heroic powerful perspective, studio lighting, dark background",
        "High Angle (Vulnerable/CDM)":"Photorealistic cinematic photo, high angle shot looking down at woman from above, vulnerable perspective, studio lighting, dark background",
        "Bird's Eye View (Overhead)": "Photorealistic cinematic photo, bird's eye view looking straight down at woman on dark floor, overhead perspective, studio lighting",
        "Worm's Eye View (Ground Level)": "Photorealistic cinematic photo, extreme low ground-level shot looking up at woman towering above, worm's eye view, dark background",
        "Dutch Angle (Dynamic/Uneven)": "Photorealistic cinematic photo, tilted dutch angle shot of woman, dynamic diagonal framing, studio lighting, dark background",
        "Profile / Side View":        "Photorealistic cinematic photo, perfect side profile view of woman, clean silhouette, studio lighting, dark background",
        "Over the Shoulder":          "Photorealistic cinematic photo, over-the-shoulder shot, camera behind one person looking at subject, studio lighting, dark background",
        "Point of View (POV)":        "Photorealistic cinematic photo, first person POV perspective, hands visible reaching forward, immersive viewpoint, dark moody setting",
        "Selfie Angle (High)":        "Photorealistic photo, selfie angle from slightly above, woman holding camera arm extended, natural warm lighting, casual setting",
        "Mirror Selfie":              "Photorealistic photo, mirror selfie shot, woman photographing reflection, phone visible in mirror, stylish interior, moody lighting",
        "Straight On (Talking Head)": "Photorealistic cinematic photo, straight-on centered talking head framing, woman facing camera directly, professional studio lighting, dark background",
        "Slightly Off-Center (Interview)": "Photorealistic cinematic photo, slightly off-center interview framing, subject offset to one side with headroom, studio lighting, dark background",
        "3/4 View (Flattering Angle)":"Photorealistic cinematic photo, classic three-quarter view angle, woman turned 45 degrees, flattering portrait framing, studio lighting, dark background",
    },
    "shot_types": {
        "Close Up":         "Photorealistic cinematic close-up shot of woman's face filling frame, sharp facial detail, studio lighting, dark background, professional portrait",
        "Medium Shot":      "Photorealistic cinematic medium shot of woman from waist up, balanced composition, studio lighting, dark background, professional",
        "Full Body":        "Photorealistic cinematic full body shot of woman head to toe, complete figure visible, studio lighting, dark background, fashion photography",
        "Wide Shot":        "Photorealistic cinematic wide shot showing woman small in large environment, establishing shot, dramatic space, dark moody setting",
        "Extreme Close Up": "Photorealistic cinematic extreme close-up of woman's eyes and partial face, intense detail, macro-like, studio lighting, dark background",
        "Cowboy Shot":      "Photorealistic cinematic cowboy shot of woman from mid-thigh up, western film style framing, studio lighting, dark background, confident pose",
        "Overhead":         "Photorealistic cinematic overhead shot looking straight down, flat lay perspective, woman on dark surface, dramatic top-down view",
    },
    "lighting": {
        "Golden Hour (Warm/Soft)":       "Photorealistic portrait in golden hour warm sunset lighting, soft orange glow on face, backlit, dreamy atmosphere, natural outdoor",
        "Blue Hour (Moody/Cold)":        "Photorealistic portrait in blue hour twilight, cool blue moody tones, ethereal atmosphere, dusk lighting on face",
        "Noon (Harsh/High Contrast)":    "Photorealistic portrait in harsh noon sunlight, strong shadows under eyes and nose, high contrast, bright direct light from above",
        "Midnight (Dark/Mystery)":       "Photorealistic portrait in midnight darkness, minimal dramatic lighting, mysterious shadows, only rim light visible, noir atmosphere",
        "Studio Lighting (Perfect/Softbox)": "Photorealistic portrait with perfect studio softbox lighting, even illumination, professional beauty lighting setup, clean shadows",
        "Ring Light (Influencer/Flat)":   "Photorealistic portrait with ring light, circular catchlight in eyes, flat even lighting, influencer style, bright and clean",
        "Neon (Cyberpunk/Colorful)":      "Photorealistic portrait with vibrant neon lighting, pink and blue cyberpunk glow, colorful light on face, futuristic atmosphere",
        "Cinematic (Rembrandt/Dramatic)": "Photorealistic portrait with Rembrandt lighting, dramatic triangle light on cheek, chiaroscuro, cinematic moody atmosphere",
        "Overcast (Diffused/Flat)":       "Photorealistic portrait in overcast diffused natural light, soft flat lighting, no harsh shadows, cloudy day atmosphere",
        "Flash Photography (Direct/Harsh)":"Photorealistic portrait with direct flash photography, harsh flat frontal light, strong specular highlights, party/paparazzi style",
    },
}

def generate_icons():
    """Generate all icons using Gemini image generation."""
    try:
        import google.generativeai as genai
    except ImportError:
        print("ERROR: google-generativeai not installed. Run: pip install google-generativeai")
        return

    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY or GEMINI_API_KEY not set in .env")
        return

    genai.configure(api_key=api_key)

    # Use Imagen 3 for high quality
    try:
        imagen = genai.ImageGenerationModel("imagen-3.0-generate-002")
    except Exception:
        print("Falling back to gemini-2.0-flash for image gen...")
        imagen = None

    total = sum(len(v) for v in CATEGORIES.values())
    generated = 0
    failed = []

    for category, options in CATEGORIES.items():
        cat_dir = ICONS_ROOT / category
        cat_dir.mkdir(parents=True, exist_ok=True)

        for option_name, prompt in options.items():
            # Create safe filename
            safe_name = option_name.lower()
            for char in "()/ ":
                safe_name = safe_name.replace(char, "_")
            safe_name = safe_name.strip("_").replace("__", "_")
            filepath = cat_dir / f"{safe_name}.png"

            if filepath.exists():
                print(f"  SKIP (exists): {filepath.name}")
                generated += 1
                continue

            print(f"  [{generated+1}/{total}] Generating: {category}/{safe_name}...")

            try:
                if imagen:
                    result = imagen.generate_images(
                        prompt=prompt + ", square format, thumbnail icon style",
                        number_of_images=1,
                        aspect_ratio="1:1",
                    )
                    if result.images:
                        result.images[0]._pil_image.save(str(filepath))
                        print(f"    ✅ Saved: {filepath.name}")
                    else:
                        print(f"    ⚠️ No image returned")
                        failed.append(option_name)
                else:
                    # Fallback: use Gemini 2.0 Flash
                    model = genai.GenerativeModel("gemini-2.0-flash-exp")
                    response = model.generate_content(
                        f"Generate a photorealistic image: {prompt}",
                        generation_config={"response_mime_type": "image/png"}
                    )
                    if response.parts:
                        for part in response.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                with open(filepath, 'wb') as f:
                                    f.write(part.inline_data.data)
                                print(f"    ✅ Saved: {filepath.name}")
                                break

                generated += 1
                time.sleep(2)  # Rate limit

            except Exception as e:
                print(f"    ❌ Error: {e}")
                failed.append(option_name)
                time.sleep(3)

    print(f"\n{'='*50}")
    print(f"Generated: {generated}/{total}")
    if failed:
        print(f"Failed ({len(failed)}): {', '.join(failed)}")
    print(f"Icons saved to: {ICONS_ROOT}")


if __name__ == "__main__":
    generate_icons()
