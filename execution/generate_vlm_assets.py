#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
VLM Website Asset Generator
Generates 5 B2B + 5 B2C hero images for vlmcreateflow.com and enterprise.vlmcreateflow.com
Then generates 2 Kling hero videos using the first image from each set as source.

Usage:
    python3.11 execution/generate_vlm_assets.py --mode images
    python3.11 execution/generate_vlm_assets.py --mode videos
    python3.11 execution/generate_vlm_assets.py --mode all
"""
import sys
import os
import shutil
import argparse
import pathlib

# Run from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

B2B_DIR = ".tmp/website_assets/b2b"
B2C_DIR = ".tmp/website_assets/b2c"

B2B_PROMPTS = [
    "Photorealistic luxury brand ad creative materializing on a massive dark studio display screen, neon green scan line effect sweeping across, deep blacks, cool blue ambient glow, cinematic 4K, no people, no text",
    "Split composition, left: chaotic traditional photo shoot with crew cables hot lights, right: sleek dark interface generating a photorealistic image cleanly, sharp dividing line, dramatic contrast, cinematic",
    "Three floating premium ad creatives in dark negative space, magazine quality photography, subtle depth of field, dark background, no text",
    "Close-up of a large dark display screen showing a photorealistic model in a high-end lifestyle environment, screen glow illuminating a dark room, cinematic bokeh, 4K",
    "Abstract dark background with faint data grid lines, photorealistic brand visuals emerging and materializing from the dark surface, glowing edges, cinematic",
]

B2C_PROMPTS = [
    "Young entrepreneur at a minimal clean desk with warm amber lighting, floating content tiles and social media posts populating the air around their laptop, aspirational and modern, vibrant, 4K",
    "Phone mockup showing a polished Instagram feed of high-quality AI-generated lifestyle content, clean minimal background, warm tones",
    "Side by side: left is generic stock photo face, right is a custom photorealistic AI avatar, same pose, confident, branded, dramatic studio lighting",
    "Young founder in modern workspace, social media follower metrics floating around them like a HUD display, warm gold and white tones, aspirational, cinematic",
    "Confident photorealistic AI avatar portrait, personal brand energy, clean studio background, professional lighting, magazine quality, no text",
]

B2B_VIDEO_PROMPT = (
    "Cinematic dark studio, massive display screen showing photorealistic AI-generated brand images "
    "appearing one by one with a subtle scan effect, slow push-in camera motion, deep blacks and cool "
    "blue tones, soft ambient screen glow, premium agency aesthetic, 4K, no text, no people"
)

B2C_VIDEO_PROMPT = (
    "Creator at minimal clean desk with warm amber lighting, laptop screen showing social media content "
    "appearing rapidly, images posts videos generating automatically, follower counter increasing, "
    "fast energetic motion, warm vibrant tones, aspirational modern, 4K"
)


def generate_images():
    from execution.generate_image import generate_image_from_prompt

    pathlib.Path(B2B_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(B2C_DIR).mkdir(parents=True, exist_ok=True)

    results = {"b2b": [], "b2c": []}

    for category, prompts, target_dir in [("B2B", B2B_PROMPTS, B2B_DIR), ("B2C", B2C_PROMPTS, B2C_DIR)]:
        for i, prompt in enumerate(prompts, 1):
            print(f"\n[{category}] Generating image {i}/5...")
            print(f"  Prompt: {prompt[:80]}...")

            prompt_data = {
                "positive_prompt": prompt,
                "aspect_ratio": "16:9",
                "image_size": "1K",
            }

            result = generate_image_from_prompt(prompt_data, output_folder=target_dir)

            if result["status"] == "success" and result.get("image_path"):
                src = result["image_path"]
                dst = os.path.join(target_dir, f"img-{i}.jpg")
                shutil.move(src, dst)

                # Remove thumbnail if created alongside
                thumb = src.replace(".jpg", "_thumb.jpg")
                if os.path.exists(thumb):
                    os.remove(thumb)

                print(f"  Saved: {dst}")
                results[category.lower()].append(dst)
            else:
                logs = result.get("logs", "no logs")
                print(f"  FAILED img-{i}: {logs[-300:]}")
                results[category.lower()].append(None)

    print("\n=== IMAGE GENERATION COMPLETE ===")
    print("B2B:", results["b2b"])
    print("B2C:", results["b2c"])
    return results


def generate_videos():
    from execution.generate_video import generate_video_kling

    pathlib.Path(B2B_DIR).mkdir(parents=True, exist_ok=True)
    pathlib.Path(B2C_DIR).mkdir(parents=True, exist_ok=True)

    b2b_src = os.path.join(B2B_DIR, "img-1.jpg")
    b2c_src = os.path.join(B2C_DIR, "img-1.jpg")

    if not os.path.exists(b2b_src):
        print(f"ERROR: B2B source image not found: {b2b_src}")
        print("Run --mode images first.")
        return

    if not os.path.exists(b2c_src):
        print(f"ERROR: B2C source image not found: {b2c_src}")
        print("Run --mode images first.")
        return

    for label, src_image, prompt, out_dir in [
        ("B2B Hero", b2b_src, B2B_VIDEO_PROMPT, B2B_DIR),
        ("B2C Hero", b2c_src, B2C_VIDEO_PROMPT, B2C_DIR),
    ]:
        print(f"\n[VIDEO] Generating {label}...")
        print(f"  Source: {src_image}")
        print(f"  Prompt: {prompt[:80]}...")

        result = generate_video_kling(
            image_path=src_image,
            prompt=prompt,
            duration=10,
            model_version="3.0",
            quality_mode="pro",
            output_folder=out_dir,
        )

        if result.get("status") == "success" and result.get("video_path"):
            src_vid = result["video_path"]
            dst_vid = os.path.join(out_dir, "hero-video.mp4")
            shutil.move(src_vid, dst_vid)
            print(f"  Saved: {dst_vid}")
        else:
            print(f"  FAILED: {result.get('error', result.get('logs', 'unknown'))}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["images", "videos", "all"], default="all")
    args = parser.parse_args()

    if args.mode in ("images", "all"):
        generate_images()

    if args.mode in ("videos", "all"):
        generate_videos()
