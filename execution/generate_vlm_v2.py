#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
VLM Website Asset Generator v2 — Character-Driven, 4K
Uses real character reference images (Angeil, Shay, Neo, Tyrie) with saved outfits.

B2C: Characters in futuristic influencer environments
B2B: Epic industry problem-solving scenes

Usage:
    python3.11 execution/generate_vlm_v2.py --mode images
    python3.11 execution/generate_vlm_v2.py --mode clips      (after images done)
    python3.11 execution/generate_vlm_v2.py --mode all
"""
import sys, os, shutil, argparse, pathlib, json, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(BASE, "assets", "AI Content Creators")
FRIENDS = os.path.join(ASSETS, "Friends")

ANGEIL_REF    = os.path.join(FRIENDS, "Angeil Master ", "Angeil Hero image", "Angeil.png")
ANGEIL_CLOTH  = os.path.join(FRIENDS, "Angeil Master ", "Angeil Clothing")

NEO_REF       = os.path.join(FRIENDS, "Mens Friends", "Neo.png")
NEO_CLOTH     = os.path.join(FRIENDS, "Mens Friends", "Neo Outfits", "Mens clothing")

TYRIE_REF     = os.path.join(FRIENDS, "Tyrie Master", "Tyrie Hero", "Tyrie.png")
TYRIE_CLOTH   = os.path.join(FRIENDS, "Tyrie Master", "Tyrie Clothing")

SHAY_REF      = os.path.join(ASSETS, "Shay.So.Fine", "SHAY STOCK Photo", "Shay blonde bob back.png")
SHAY_FRONT    = os.path.join(ASSETS, "Shay.So.Fine", "SHAY STOCK Photo", "Shay blonde bob front .png")
SHAY_CLOTH    = os.path.join(ASSETS, "2026 Jan CLothing ")

OUTDIR_B2C    = ".tmp/website_assets/v2/b2c"
OUTDIR_B2B    = ".tmp/website_assets/v2/b2b"
CLIPS_B2C     = ".tmp/website_assets/v2/clips/b2c"
CLIPS_B2B     = ".tmp/website_assets/v2/clips/b2b"

# ─── B2C Image Specs (futuristic influencer aesthetics) ───────────────────────
B2C_SPECS = [
    {
        "id": "angeil_holographic_studio",
        "ref": ANGEIL_REF,
        "outfit": os.path.join(ANGEIL_CLOTH, "dior dress.jpg"),
        "prompt": (
            "Full-length editorial photograph of this woman in a jaw-dropping futuristic content creation studio. "
            "She is center frame, exuding supreme confidence and star power. "
            "Around her: massive floating holographic social media panels showing viral posts, "
            "glowing follower count displays, AI-generated content tiles populating in real-time, "
            "a cascade of luminous content materializing from thin air. "
            "The studio itself is otherworldly — deep midnight blue and electric violet lighting, "
            "transparent curved walls revealing a cityscape, holographic particles drifting. "
            "Her expression: she owns this world. "
            "Shot on Hasselblad H6D, 50mm, cinematic grade. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "shay_neon_creator_loft",
        "ref": SHAY_REF,
        "outfit": os.path.join(SHAY_CLOTH, "Green Christian Dior .jpg"),
        "prompt": (
            "Cinematic full-body shot of this blonde woman standing in an ultra-futuristic neon-lit creator loft. "
            "She is poised, glamorous, commanding. "
            "The space around her: a cascade of AI-generated Instagram content tiles floating like constellations, "
            "glowing screens displaying her brand aesthetic in perfect resolution, "
            "neon strips of mint green, electric pink, and white light framing the room. "
            "Holographic analytics panels hover beside her showing explosive follower growth. "
            "The floor is polished dark marble reflecting the neon glow. "
            "Futuristic minimal furniture. Premium creator energy. "
            "Shot on Phase One XF IQ4, 75mm, sharp detail. "
            "Ultra-realistic editorial. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "angeil_cyberpunk_rooftop",
        "ref": ANGEIL_REF,
        "outfit": os.path.join(ANGEIL_CLOTH, "pink two piece .jpg"),
        "prompt": (
            "Epic editorial photograph of this woman standing on a futuristic cyberpunk rooftop terrace at night. "
            "Below her: an enormous glowing megacity with towering digital billboards. "
            "Around her floating in mid-air: holographic social media content she has generated, "
            "portrait tiles of herself in different AI-crafted settings, engagement metrics rendered in light. "
            "A massive glowing display behind her reads follower counts surging in real-time. "
            "She stands powerful and relaxed, hand on hip, knowing she controls the algorithm. "
            "Deep blue-black sky, neon purples and cyans, atmospheric haze. "
            "Shot on Sony A1, 24mm, ultra-wide cinematic. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "shay_ai_content_mirror",
        "ref": SHAY_FRONT,
        "outfit": os.path.join(SHAY_CLOTH, "Baby Blue OutFit .png"),
        "prompt": (
            "Conceptual editorial fashion photograph of this blonde woman standing in a sleek white futuristic room. "
            "Surrounding her in a perfect arc: dozens of AI-generated portrait images of herself in different "
            "luxury locations — Maldives, Paris, Tokyo rooftop, yacht — all created by AI, flawlessly real. "
            "She smiles knowingly at the camera. The message: unlimited professional content, infinite locations, "
            "no passport needed. The room is minimalist white with soft glowing light. "
            "The floating images form a halo around her like a crown of content. "
            "One screen shows a posting schedule automatically filling up. "
            "Premium, aspirational, powerful. "
            "Shot on Canon EOS R5, 50mm. "
            "Ultra-realistic editorial. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "angeil_shay_vlm_studio",
        "ref": ANGEIL_REF,
        "outfit": os.path.join(ANGEIL_CLOTH, "orange 2 fit.jpg"),
        "prompt": (
            "Wide cinematic shot of this woman in a premium futuristic VLM creator studio — the ultimate content factory. "
            "She is the protagonist of this world: surrounded by a living ecosystem of AI-powered content creation. "
            "Walls of screens display brand campaigns being generated in real-time. "
            "Holographic timelines showing scheduled posts populating across social platforms. "
            "The studio is dark and dramatic with warm amber accent lighting cutting through. "
            "Gold and black aesthetic. The feeling: this is the future of the influencer economy. "
            "She is the product. The AI is the engine. "
            "Long-lens cinematic shot, shallow depth of field, magazine quality. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
]

# ─── B2B Image Specs (epic industry problem → solution scenes) ────────────────
# Tyrie char desc (injected since he has high tattoo detail to describe)
TYRIE_DESC = (
    "The subject is a tall, heavily muscular Black man with full-body tattoos across both arms, chest, and back. "
    "Athletic build, defined physique, sharp fade haircut, natural dominant presence. "
)
NEO_DESC = (
    "The subject is a light-skinned Black man with a well-groomed beard, medium build, sharp confident demeanor. "
)

B2B_SPECS = [
    {
        "id": "tyrie_ad_agency_pitch",
        "ref": TYRIE_REF,
        "outfit": os.path.join(TYRIE_CLOTH, "Monaco Outfit.jpg"),
        "char_desc": TYRIE_DESC,
        "prompt": (
            "{char_desc}"
            "Epic cinematic photograph of this man standing in a high-end dark ad agency pitch room. "
            "He faces the camera with supreme authority — arms folded, slight smirk. "
            "Behind him: an enormous floor-to-ceiling display wall showing a full AI-generated brand campaign "
            "— photorealistic models, luxury product shots, aspirational lifestyle imagery — "
            "all produced by AI in hours, not weeks. "
            "LEFT side of frame: a physical moodboard showing an old-school photo shoot invoice for $15,000, "
            "a calendar blocked with 3 weeks of shoot prep, tired looking results. "
            "RIGHT side: the wall of stunning AI-generated content produced in a single day. "
            "The contrast tells the story. "
            "Deep blacks, dramatic single-source key lighting, cinematic blue rim light. "
            "Shot on ARRI Alexa, anamorphic lens. Cinematic. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "neo_financial_advisor_transform",
        "ref": NEO_REF,
        "outfit": os.path.join(NEO_CLOTH, "Rick Owens Fit .jpg"),
        "char_desc": NEO_DESC,
        "prompt": (
            "{char_desc}"
            "Powerful cinematic photograph of this man in a sleek modern financial advisor's office. "
            "He sits at a clean glass desk, forward-leaning, completely in control. "
            "On the wall behind him: before and after — left panel shows a financial advisor's old "
            "generic stock photo marketing — boring headshots, clip art, budget-looking email templates. "
            "Right panel: his firm's new AI-powered brand visuals — cinematic portraits, editorial-quality "
            "lifestyle imagery, luxury-tier marketing materials generated by VLM's content engine. "
            "His expression: this is exactly why clients stay and referrals multiply. "
            "Warm wood tones, brass accents, premium office aesthetic. "
            "Late evening light through floor-to-ceiling windows. "
            "Shot on Sony A7RV, 85mm. Business editorial. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "tyrie_coaching_brand_reveal",
        "ref": TYRIE_REF,
        "outfit": os.path.join(TYRIE_CLOTH, "ALl saints beige fit.jpg"),
        "char_desc": TYRIE_DESC,
        "prompt": (
            "{char_desc}"
            "Dramatic cinematic portrait of this man in a dark luxury consulting space — "
            "standing before a massive curved display screen. "
            "The screen shows a transformation: on the left, a faceless coaching brand with "
            "generic Canva graphics; on the right, a fully realized personal brand — "
            "cinematic photography, cohesive visual identity, authority-level content. "
            "His arms are wide gesturing toward the transformation on the screen. "
            "The energy: revolutionary. This is what we do. "
            "Dark dramatic space, single spotlight on him, the screen as the only other light source. "
            "Deep black background, premium minimal. "
            "Shot on RED Cinema camera, 50mm. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "neo_tyrie_vlm_command",
        "ref": NEO_REF,
        "outfit": os.path.join(NEO_CLOTH, "Louis Vutton Brown fit .png"),
        "char_desc": NEO_DESC,
        "prompt": (
            "{char_desc}"
            "Wide cinematic shot of this man in a futuristic dark operations center — the VLM content engine HQ. "
            "He stands at the center of a curved command console, screens arcing around him "
            "displaying AI-generated brand campaigns for multiple clients simultaneously: "
            "a financial firm, a coaching brand, an ad agency. "
            "Each screen shows professional editorial-quality content being generated and scheduled automatically. "
            "His posture radiates precision and power — the architect of this machine. "
            "Deep navy and charcoal tones, dramatic backlight, data visualizations glowing. "
            "This is what replacing a $15,000 shoot looks like. "
            "Shot on ARRI, ultra-wide anamorphic. Cinematic sci-fi meets luxury brand. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
    {
        "id": "tyrie_neo_enterprise_reveal",
        "ref": TYRIE_REF,
        "outfit": os.path.join(TYRIE_CLOTH, "drip khaki .png"),
        "char_desc": TYRIE_DESC,
        "prompt": (
            "{char_desc}"
            "Epic two-act wide cinematic image: "
            "This powerful tattooed man standing in a split-frame composition. "
            "LEFT HALF: the old world — a small business owner surrounded by "
            "chaotic stacks of paper, a cheap photographer, generic mediocre content, faded brand materials. "
            "A visible price tag: $15,000 photography invoice. "
            "RIGHT HALF: the new world — the same business identity "
            "transformed with VLM — cinematic AI-generated brand imagery flooding every screen, "
            "unlimited photorealistic assets, a content engine running on autopilot. "
            "He stands exactly at the split line, one hand in the chaos, one hand in the future. "
            "Dramatic directional lighting emphasizes the contrast. "
            "Deep, cinematic, editorial. "
            "Ultra-realistic. 4K. Aspect ratio 16:9. No text."
        ),
    },
]


def generate_images():
    from execution.generate_image import generate_image_from_prompt

    pathlib.Path(OUTDIR_B2C).mkdir(parents=True, exist_ok=True)
    pathlib.Path(OUTDIR_B2B).mkdir(parents=True, exist_ok=True)

    results = {"b2c": [], "b2b": []}

    for category, specs, out_dir in [
        ("B2C", B2C_SPECS, OUTDIR_B2C),
        ("B2B", B2B_SPECS, OUTDIR_B2B),
    ]:
        for i, spec in enumerate(specs, 1):
            print(f"\n[{category}] Image {i}/5 — {spec['id']}")

            # Build prompt (inject char_desc if present)
            prompt_text = spec["prompt"]
            if "{char_desc}" in prompt_text:
                prompt_text = prompt_text.format(char_desc=spec.get("char_desc", ""))

            # Build assets list for character + outfit
            assets = []
            if os.path.exists(spec["ref"]):
                assets.append({"label": "Main Character", "path": spec["ref"]})
            else:
                print(f"  WARNING: ref missing: {spec['ref']}")

            outfit_path = spec.get("outfit")
            if outfit_path and os.path.exists(outfit_path):
                assets.append({"label": "Outfit: Primary", "path": outfit_path})
            elif outfit_path:
                print(f"  WARNING: outfit missing: {outfit_path}")

            prompt_data = {
                "positive_prompt": prompt_text,
                "aspect_ratio": "16:9",
                "image_size": "4K",
                "assets": assets,
            }

            result = generate_image_from_prompt(prompt_data, output_folder=out_dir)

            if result["status"] == "success" and result.get("image_path"):
                src = result["image_path"]
                dst = os.path.join(out_dir, f"img-{i}.jpg")
                shutil.move(src, dst)
                # Remove auto-generated thumbnail
                thumb = src.replace(".jpg", "_thumb.jpg")
                if os.path.exists(thumb):
                    os.remove(thumb)
                print(f"  Saved: {dst}")
                results[category.lower()].append(dst)
            else:
                print(f"  FAILED: {str(result.get('logs',''))[-300:]}")
                results[category.lower()].append(None)

    print("\n=== IMAGE GENERATION COMPLETE ===")
    print("B2C:", results["b2c"])
    print("B2B:", results["b2b"])

    # Save manifest
    manifest = {
        "b2c": results["b2c"],
        "b2b": results["b2b"],
        "b2c_specs": [s["id"] for s in B2C_SPECS],
        "b2b_specs": [s["id"] for s in B2B_SPECS],
    }
    manifest_path = ".tmp/website_assets/v2/manifest.json"
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest saved: {manifest_path}")
    return results


def generate_clips(b2c_indices=(0, 1, 2), b2b_indices=(0, 1, 2)):
    """
    Generate Kling 5s clips from selected images.
    Indices refer to img-N.jpg (0-based → img-1.jpg, img-2.jpg, etc.)
    """
    from execution.generate_video import generate_video_kling

    pathlib.Path(CLIPS_B2C).mkdir(parents=True, exist_ok=True)
    pathlib.Path(CLIPS_B2B).mkdir(parents=True, exist_ok=True)

    B2C_VIDEO_PROMPTS = [
        (
            "Cinematic slow push-in on a stunning woman in a futuristic holographic influencer studio. "
            "Floating social media content tiles drift around her, follower counts pulse upward in light. "
            "Warm purple and blue ambient glow, dreamy motion. Premium, aspirational. 4K."
        ),
        (
            "Cinematic tracking shot — beautiful blonde woman in a neon-lit creator loft, "
            "AI-generated content tiles cascading around her like a constellation. "
            "She turns to camera with supreme confidence. Green and white neon, luxury atmosphere. 4K."
        ),
        (
            "Slow aerial pull-back revealing a woman on a futuristic cyberpunk rooftop, "
            "holographic brand content floating around her, megacity glowing below. "
            "Cyberpunk purples and cyan, epic scale. 4K."
        ),
        (
            "Close push-in on a woman surrounded by an arc of AI-generated portrait images of herself "
            "in different exotic locations — all AI-created. She smiles knowingly at the camera. "
            "Clean white futuristic room, soft luminous glow. 4K."
        ),
        (
            "Wide to close cinematic shot of a woman in a dark premium creator studio, "
            "screens behind her cycling through stunning AI-generated brand campaigns. "
            "Warm amber accent lighting, dramatic. 4K."
        ),
    ]

    B2B_VIDEO_PROMPTS = [
        (
            "Cinematic slow push-in on a powerful man standing in a dark ad agency pitch room. "
            "The display wall behind him lights up with stunning AI-generated brand visuals. "
            "He turns slightly toward the camera — confident, authoritative. "
            "Deep blacks, dramatic key lighting, cinematic blue rim light. 4K."
        ),
        (
            "Slow dolly-in on a sharp man sitting in a financial advisor's office. "
            "On the wall behind: transformation from generic stock photos to premium AI-generated visuals. "
            "His expression radiates control and satisfaction. Warm office tones. 4K."
        ),
        (
            "Cinematic arc shot around a powerful tattooed man standing before a massive screen "
            "showing a brand transformation. Dramatic single spotlight, deep black space. "
            "The screen pulses from chaos to premium content. 4K."
        ),
        (
            "Wide cinematic push-in on a man standing at a curved command console, "
            "arc of screens around him showing AI brand campaigns for multiple clients. "
            "Deep navy tones, data visualizations glowing. Architect of the machine. 4K."
        ),
        (
            "Epic slow zoom revealing a man standing at a split-frame moment — "
            "chaos on one side, AI-powered brand content revolution on the other. "
            "He stands at the exact dividing line, commanding both worlds. "
            "Dramatic directional lighting. Cinematic. 4K."
        ),
    ]

    clip_results = {"b2c": [], "b2b": []}

    for label, category, indices, img_dir, clip_dir, video_prompts in [
        ("B2C", "b2c", b2c_indices, OUTDIR_B2C, CLIPS_B2C, B2C_VIDEO_PROMPTS),
        ("B2B", "b2b", b2b_indices, OUTDIR_B2B, CLIPS_B2B, B2B_VIDEO_PROMPTS),
    ]:
        for slot, idx in enumerate(indices, 1):
            img_path = os.path.join(img_dir, f"img-{idx+1}.jpg")
            prompt = video_prompts[idx]

            if not os.path.exists(img_path):
                print(f"  [{label}] SKIP clip {slot}: source image not found: {img_path}")
                clip_results[category].append(None)
                continue

            print(f"\n[{label}] Generating clip {slot}/3 from img-{idx+1}.jpg...")
            print(f"  Prompt: {prompt[:80]}...")

            result = generate_video_kling(
                image_path=img_path,
                prompt=prompt,
                duration=5,
                model_version="2.6",
                quality_mode="pro",
                output_folder=clip_dir,
            )

            if result.get("status") == "success" and result.get("video_path"):
                src = result["video_path"]
                dst = os.path.join(clip_dir, f"clip-{slot}.mp4")
                shutil.move(src, dst)
                print(f"  Saved: {dst}")
                clip_results[category].append(dst)
            else:
                print(f"  FAILED: {result.get('error', 'unknown')}")
                clip_results[category].append(None)

    print("\n=== CLIP GENERATION COMPLETE ===")
    print("B2C:", clip_results["b2c"])
    print("B2B:", clip_results["b2b"])

    # Update manifest
    manifest_path = ".tmp/website_assets/v2/manifest.json"
    manifest = {}
    if os.path.exists(manifest_path):
        with open(manifest_path) as f:
            manifest = json.load(f)
    manifest["b2c_clips"] = clip_results["b2c"]
    manifest["b2b_clips"] = clip_results["b2b"]
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"Manifest updated: {manifest_path}")
    return clip_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["images", "clips", "all"], default="all")
    parser.add_argument("--b2c_indices", type=str, default="0,1,2",
                        help="Comma-separated 0-based indices of B2C images to use for clips")
    parser.add_argument("--b2b_indices", type=str, default="0,1,2",
                        help="Comma-separated 0-based indices of B2B images to use for clips")
    args = parser.parse_args()

    b2c_idx = [int(x) for x in args.b2c_indices.split(",")]
    b2b_idx = [int(x) for x in args.b2b_indices.split(",")]

    if args.mode in ("images", "all"):
        generate_images()

    if args.mode in ("clips", "all"):
        generate_clips(b2c_indices=b2c_idx, b2b_indices=b2b_idx)
