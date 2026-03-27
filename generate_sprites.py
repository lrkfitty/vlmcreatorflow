#!/usr/bin/env python3
"""
VLM Office Sprite Generator
Generates 16-bit pixel art sprite sheets for office agents
using Gemini Image API (Nano Banana 2 / gemini-3.1-flash-image-preview)

Usage:
  python3 generate_sprites.py --agent claude --type base
  python3 generate_sprites.py --agent claude --type idle
  python3 generate_sprites.py --agent all --type base
  python3 generate_sprites.py --agent all --type all
"""
import os, sys, json, time, base64, argparse, subprocess
from pathlib import Path
import requests
from dotenv import load_dotenv

load_dotenv()
BASE = Path(__file__).parent
SPRITES = BASE / 'assets' / 'sprites'
SPRITES.mkdir(parents=True, exist_ok=True)

API_KEY = os.getenv("GOOGLE_IMAGE_KEY") or os.getenv("GOOGLE_API_KEY")
MODEL   = 'gemini-3.1-flash-image-preview'
URL     = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={API_KEY}"

# ── AGENT DEFINITIONS ──────────────────────────────────────────────────────────
# Colors match visual_office.html AGENTS object
AGENTS = {
    'claude': {
        'label': 'CLAUDE CODE',
        'description': 'male office executive, dark brown skin (#d4a870), very short near-black hair, authoritative confident stance',
        'clothing': 'dark navy double-breasted blazer, gold necktie, white dress shirt, black dress pants, black oxford shoes',
    },
    'gemini': {
        'label': 'GEMINI',
        'description': 'male creative designer, warm brown skin (#c48050), short black hair, artistic creative energy',
        'clothing': 'deep purple dress shirt, dark charcoal pants, white canvas sneakers',
    },
    'kling': {
        'label': 'KLING AI',
        'description': 'male cinematographer, medium brown skin (#b87048), very short dark brown hair, focused intense look',
        'clothing': 'dark navy casual bomber jacket, very dark navy pants, dark leather boots',
    },
    'outreach': {
        'label': 'OUTREACH BOT',
        'description': 'male sales representative, medium warm brown skin (#c07838), very short dark hair, energetic sales personality',
        'clothing': 'dark forest green polo shirt, very dark green-black slacks, black leather loafers',
    },
    'autoposter': {
        'label': 'AUTO-POSTER',
        'description': 'female social media manager, light brown skin (#d4a870), straight black hair in sleek ponytail, stylish modern look',
        'clothing': 'dark magenta-purple fitted blouse, very dark charcoal pants, black pointed heels',
    },
    'crm': {
        'label': 'CRM SYNC',
        'description': 'male data analyst, medium brown skin (#b07840), short cropped black hair, precise methodical demeanor',
        'clothing': 'dark navy blue dress shirt, very dark navy pants, black oxford shoes',
    },
    'gmail': {
        'label': 'GMAIL MONITOR',
        'description': 'female receptionist, warm tan skin (#c8a06a), medium-length dark brown hair worn down, welcoming professional look',
        'clothing': 'dark red blouse, very dark burgundy pants, black ballet flats',
    },
}

# ── API CALL ───────────────────────────────────────────────────────────────────
def call_gemini(prompt, ref_path=None, layout_ref_path=None):
    """Call Gemini image generation. Returns raw PNG bytes or None."""
    parts = []

    def encode_image(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()

    if ref_path and Path(ref_path).exists():
        parts.append({"text": "[CHARACTER REFERENCE — match this character's appearance exactly]"})
        parts.append({"inlineData": {"mimeType": "image/png", "data": encode_image(ref_path)}})

    if layout_ref_path and Path(layout_ref_path).exists():
        parts.append({"text": "[SPRITE SHEET LAYOUT REFERENCE — match this exact grid layout]"})
        parts.append({"inlineData": {"mimeType": "image/png", "data": encode_image(layout_ref_path)}})

    parts.append({"text": prompt})

    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE", "TEXT"],
        }
    }

    try:
        resp = requests.post(URL, json=payload, headers={"Content-Type": "application/json"}, timeout=180)
        resp.raise_for_status()
        data = resp.json()

        for candidate in data.get('candidates', []):
            for part in candidate.get('content', {}).get('parts', []):
                if 'inlineData' in part:
                    return base64.b64decode(part['inlineData']['data'])
        print(f"  No image in response. Response keys: {list(data.keys())}")
        return None
    except Exception as e:
        print(f"  API error: {e}")
        return None

def save_image(img_bytes, path):
    with open(path, 'wb') as f:
        f.write(img_bytes)
    print(f"  Saved → {path}")
    return path

# ── SPRITE PROMPTS ─────────────────────────────────────────────────────────────
def prompt_base(agent):
    return (
        f"16-bit pixel art game sprite of a {agent['description']}, "
        f"front view facing camera, {agent['clothing']}, "
        "simple friendly face, small character suitable for top-down office game, "
        "retro SNES/Genesis style pixel art, standing idle pose with arms at sides, "
        "isolated on solid magenta background #FF00FF, "
        "SHARP CRISP PIXEL EDGES WITH ABSOLUTELY NO ANTI-ALIASING NO SMOOTHING NO BLENDING, "
        "each pixel is a solid color with hard edges, centered composition, "
        "no text no shadows on background, 64x80 pixel scale"
    )

def prompt_idle_sheet(agent, name):
    return (
        f"16-bit pixel art sprite sheet, EXACTLY 928x1152 pixels total, "
        "divided into 8 columns and 8 rows grid, each cell is EXACTLY 116x144 pixels "
        "with NO borders NO padding NO gaps between cells, "
        f"character is {agent['description']}, {agent['clothing']}, "
        "EXACTLY as shown in the first reference image, "
        "8 DIRECTIONS IN EXACT ORDER from top to bottom: "
        "ROW 0 south facing toward camera, ROW 1 south-west diagonal, "
        "ROW 2 west facing left profile, ROW 3 north-west diagonal, "
        "ROW 4 north facing away back view, ROW 5 north-east diagonal, "
        "ROW 6 east facing right profile, ROW 7 south-east diagonal, "
        "each row has 8 frames of subtle idle breathing animation, "
        "cells touch edge-to-edge with no visible grid lines, "
        "retro SNES Genesis 16-bit pixel art, "
        "SHARP CRISP PIXEL EDGES WITH ABSOLUTELY NO ANTI-ALIASING NO SMOOTHING NO BLENDING, "
        "each pixel is a solid color with hard edges, "
        "consistent character in every cell matching reference, "
        "solid magenta #FF00FF background fills all empty space in each cell, "
        "game sprite sheet asset, no text no watermarks"
    )

def prompt_typing_sheet(agent, name):
    return (
        f"16-bit pixel art sprite sheet for TYPING animation, EXACTLY 928x144 pixels total, "
        "horizontal strip with 8 equal cells of EXACTLY 116x144 pixels each "
        "with NO borders NO padding NO gaps between cells, "
        f"character is {agent['description']}, {agent['clothing']}, "
        "EXACTLY as shown in the reference image, "
        "character seen from behind (back view) in seated typing pose with arms extended forward, "
        "CHARACTER ONLY no desk no chair no keyboard no furniture, "
        "8 frame typing animation showing hands and arms making typing movements, "
        "cells touch edge-to-edge with no visible grid lines, "
        "retro SNES Genesis 16-bit pixel art, "
        "SHARP CRISP PIXEL EDGES WITH ABSOLUTELY NO ANTI-ALIASING NO SMOOTHING NO BLENDING, "
        "each pixel is a solid color with hard edges, "
        "solid magenta #FF00FF background fills all empty space, "
        "game sprite sheet asset, no text no watermarks"
    )

def prompt_walk_sheet(agent, name):
    return (
        f"16-bit pixel art sprite sheet for WALKING animation, EXACTLY 928x1152 pixels total, "
        "8 columns and 8 rows grid, each cell EXACTLY 116x144 pixels, NO borders NO gaps, "
        f"character is {agent['description']}, {agent['clothing']}, "
        "EXACTLY as shown in the reference image, "
        "8 DIRECTIONS: ROW 0 walking south, ROW 1 south-west, ROW 2 west, ROW 3 north-west, "
        "ROW 4 north, ROW 5 north-east, ROW 6 east, ROW 7 south-east, "
        "8 frames of walk cycle with alternating legs and natural arm swing, "
        "cells touch edge-to-edge, retro SNES Genesis 16-bit pixel art, "
        "SHARP CRISP PIXEL EDGES NO ANTI-ALIASING, solid magenta #FF00FF background, "
        "game sprite sheet asset, no text no watermarks"
    )

# ── PROCESSING ────────────────────────────────────────────────────────────────
def process_sprite(raw_path, out_path, skip_trim=False):
    """Remove magenta bg, convert to transparent PNG using ImageMagick."""
    magick = '/opt/homebrew/bin/magick'
    trim_flag = '+repage' if skip_trim else '-trim +repage'

    cmd = [
        magick, str(raw_path),
        '-alpha', 'set', '-channel', 'RGBA',
        '-fuzz', '20%', '-transparent', 'magenta',
        '-fuzz', '15%', '-transparent', '#CC00CC',
        '-fuzz', '15%', '-transparent', '#880088',
    ]
    if not skip_trim:
        cmd += ['-trim', '+repage']
    else:
        cmd += ['+repage']
    cmd += ['-type', 'TrueColorAlpha', '-strip', str(out_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ImageMagick error: {result.stderr}")
        return False
    print(f"  Processed → {out_path}")
    return True

def open_image(path):
    """Open image in Preview for user inspection."""
    subprocess.run(['open', str(path)], check=False)

# ── GENERATORS ────────────────────────────────────────────────────────────────
def gen_base(name):
    """Generate base front-idle character design."""
    agent = AGENTS[name]
    raw = SPRITES / f"{name}_front_idle_raw.png"
    out = SPRITES / f"{name}_front_idle.png"

    print(f"\n{'='*50}")
    print(f"  Generating BASE sprite: {agent['label']}")
    print(f"{'='*50}")

    img = call_gemini(prompt_base(agent))
    if not img:
        print("  FAILED — no image returned")
        return None

    save_image(img, raw)
    process_sprite(raw, out)
    open_image(out)
    return out

def gen_idle(name):
    """Generate full idle sprite sheet (requires approved base)."""
    agent = AGENTS[name]
    base_ref = SPRITES / f"{name}_front_idle.png"
    raw = SPRITES / f"{name}_idle_sheet_raw.png"
    out = SPRITES / f"{name}_idle_sheet.png"

    if not base_ref.exists():
        print(f"  Need base sprite first. Run: --agent {name} --type base")
        return None

    print(f"\n{'='*50}")
    print(f"  Generating IDLE sheet: {agent['label']}")
    print(f"{'='*50}")

    img = call_gemini(prompt_idle_sheet(agent, name), ref_path=str(base_ref))
    if not img:
        print("  FAILED")
        return None

    save_image(img, raw)
    process_sprite(raw, out, skip_trim=True)
    # Verify dimensions
    verify = subprocess.run(['/opt/homebrew/bin/magick', str(raw), '-format', '%wx%h', 'info:'],
                            capture_output=True, text=True)
    print(f"  Raw dimensions: {verify.stdout} (target: 928x1152)")
    open_image(out)
    return out

def gen_typing(name):
    """Generate typing animation strip."""
    agent = AGENTS[name]
    base_ref = SPRITES / f"{name}_front_idle.png"
    raw = SPRITES / f"{name}_typing_sheet_raw.png"
    out = SPRITES / f"{name}_typing_sheet.png"

    if not base_ref.exists():
        print(f"  Need base sprite first. Run: --agent {name} --type base")
        return None

    print(f"\n{'='*50}")
    print(f"  Generating TYPING sheet: {agent['label']}")
    print(f"{'='*50}")

    img = call_gemini(prompt_typing_sheet(agent, name), ref_path=str(base_ref))
    if not img:
        print("  FAILED")
        return None

    save_image(img, raw)
    process_sprite(raw, out, skip_trim=True)
    open_image(out)
    return out

def gen_walk(name):
    """Generate walk cycle sprite sheet."""
    agent = AGENTS[name]
    base_ref = SPRITES / f"{name}_front_idle.png"
    raw = SPRITES / f"{name}_walk_sheet_raw.png"
    out = SPRITES / f"{name}_walk_sheet.png"

    if not base_ref.exists():
        print(f"  Need base sprite first. Run: --agent {name} --type base")
        return None

    print(f"\n{'='*50}")
    print(f"  Generating WALK sheet: {agent['label']}")
    print(f"{'='*50}")

    img = call_gemini(prompt_walk_sheet(agent, name), ref_path=str(base_ref))
    if not img:
        print("  FAILED")
        return None

    save_image(img, raw)
    process_sprite(raw, out, skip_trim=True)
    open_image(out)
    return out

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='VLM Office Sprite Generator')
    parser.add_argument('--agent', default='claude',
                        help=f'Agent name or "all". Options: {", ".join(AGENTS.keys())}')
    parser.add_argument('--type', default='base',
                        help='Sprite type: base | idle | typing | walk | all')
    args = parser.parse_args()

    names = list(AGENTS.keys()) if args.agent == 'all' else [args.agent]

    for name in names:
        if name not in AGENTS:
            print(f"Unknown agent: {name}. Options: {', '.join(AGENTS.keys())}")
            continue

        if args.type == 'base':
            gen_base(name)
        elif args.type == 'idle':
            gen_idle(name)
        elif args.type == 'typing':
            gen_typing(name)
        elif args.type == 'walk':
            gen_walk(name)
        elif args.type == 'all':
            if gen_base(name):
                input(f"\n  Review {name} base sprite then press Enter to continue...")
                gen_idle(name)
                gen_typing(name)
                gen_walk(name)
        else:
            print(f"Unknown type: {args.type}")

    print("\nDone. Check assets/sprites/")

if __name__ == '__main__':
    main()
