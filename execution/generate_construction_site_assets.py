"""
Generate image assets for the Medina Brothers Roofing Co preview site.
Output: templates/construction_site/assets/

Images:
  hero.jpg       — dramatic hero (wide, moody)
  project-1.jpg  — metal roof install (wide gallery card)
  project-2.jpg  — roof repair / maintenance
  project-3.jpg  — insurance claim replacement
  project-4.jpg  — skylight installation
  project-5.jpg  — full shingle re-roof
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from generate_image import generate_image_from_prompt

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../templates/construction_site/assets")

SHOTS = [
    {
        "filename": "hero.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Cinematic wide-angle photograph of a luxury Arizona home at golden hour, "
                "featuring a freshly completed dark charcoal standing-seam metal roof. "
                "Dramatic sky with deep orange and burnt amber tones. Low angle looking up. "
                "Hyper-realistic architectural photography. Premium construction quality. "
                "Desert landscape, palm tree silhouettes. No people. Award-winning composition."
            ),
            "aspect_ratio": "16:9",
            "image_size": "2K"
        }
    },
    {
        "filename": "project-1.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Wide-angle architectural photo of a completed red standing-seam metal roof "
                "on a modern Arizona ranch-style home. Bright sunny day, clear blue sky. "
                "Clean crisp lines, perfect installation quality. Hyper-realistic. "
                "Professional real estate photography style. No people. Surprise Arizona suburb."
            ),
            "aspect_ratio": "4:3",
            "image_size": "2K"
        }
    },
    {
        "filename": "project-2.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Close-up professional photo of a roofer's hands carefully laying new asphalt "
                "shingles on a roof. Detailed texture of dark charcoal shingles, precision workmanship. "
                "Warm sunlight. Tools visible. No face visible, just hands and roof surface. "
                "Hyper-realistic trades photography. Shallow depth of field."
            ),
            "aspect_ratio": "4:3",
            "image_size": "1K"
        }
    },
    {
        "filename": "project-3.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Before and after style: fresh new asphalt shingle roof being installed on an Arizona "
                "suburban home after storm damage. Sunny afternoon. Half old weathered shingles, "
                "half clean new dark gray architectural shingles being laid. "
                "Hyper-realistic residential roofing photo. No people. Clear blue sky."
            ),
            "aspect_ratio": "4:3",
            "image_size": "1K"
        }
    },
    {
        "filename": "project-4.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Professional photo of a newly installed modern skylight on a tile roof in Arizona. "
                "Crystal clear glass, perfect flashing and sealing around the frame. "
                "Bright blue sky visible through the glass. Warm afternoon light. "
                "Hyper-realistic architectural detail photography. No people."
            ),
            "aspect_ratio": "4:3",
            "image_size": "1K"
        }
    },
    {
        "filename": "project-5.jpg",
        "prompt_data": {
            "positive_prompt": (
                "Aerial-style photo looking down at a freshly completed full roof replacement on a "
                "large Arizona home. New dark architectural shingles, crisp ridge line, clean gutters. "
                "Suburban neighborhood visible below, blue sky. Top-down perspective. "
                "Hyper-realistic drone photography style. No people. Perfect symmetry."
            ),
            "aspect_ratio": "4:3",
            "image_size": "1K"
        }
    }
]

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Generating {len(SHOTS)} images → {OUTPUT_DIR}\n")

    for shot in SHOTS:
        filename = shot["filename"]
        out_path = os.path.join(OUTPUT_DIR, filename)

        print(f"  Generating {filename}...")
        result = generate_image_from_prompt(
            prompt_data=shot["prompt_data"],
            output_folder=OUTPUT_DIR
        )

        if result["status"] == "success" and result.get("image_path"):
            # Rename to target filename if generator used a temp name
            generated = result["image_path"]
            if os.path.abspath(generated) != os.path.abspath(out_path):
                os.rename(generated, out_path)
            print(f"  ✓ {filename} saved")
        else:
            print(f"  ✗ {filename} FAILED — {result.get('logs', '')}")

    print(f"\nDone. All assets in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
