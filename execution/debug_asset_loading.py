import os
import sys
import json
from dotenv import load_dotenv

# Mock Streamlit secrets if needed? Load Assets relies on os.environ usually.
load_dotenv()

# Fix path to include current directory (execution)
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from load_assets import load_assets
except ImportError:
    # If running from root without package context
    from execution.load_assets import load_assets

# Update this to match your username in the path
USER_ASSETS_DIR = "output/users/TyTheGuyTTG/Assets"

print("--- DEBUGGING ASSET LOADING ---")

# 1. Load Base Assets
print("\n1. Loading Base Assets...")
base_assets = load_assets(user_assets_dir=None, skip_base=False)
if 'characters' in base_assets:
    print(f"Base Characters: {len(base_assets['characters'])}")
    print(f"Sample: {list(base_assets['characters'].keys())[:5]}")
else:
    print("Base Characters: 0")

if 'outfits' in base_assets:
    print(f"Base Outfits: {len(base_assets['outfits'])}")
    print(f"Sample: {list(base_assets['outfits'].keys())[:5]}")


# 2. Load User Assets
print(f"\n2. Loading User Assets from {USER_ASSETS_DIR}...")

# DELETE MANIFEST TO FORCE SCAN
manifest_path = os.path.join(USER_ASSETS_DIR, "user_manifest.json")
if os.path.exists(manifest_path):
    print("🗑️ Deleting stale manifest for debug...")
    os.remove(manifest_path)

user_assets = load_assets(user_assets_dir=USER_ASSETS_DIR, skip_base=True)

if 'characters' in user_assets:
    print(f"User Characters: {len(user_assets['characters'])}")
    print(f"Sample: {list(user_assets['characters'].keys())[:5]}")
else:
    print("User Characters: 0")

if 'outfits' in user_assets:
    print(f"User Outfits: {len(user_assets['outfits'])}")
    print(f"Sample: {list(user_assets['outfits'].keys())[:5]}")

# 3. Simulate Merge
print("\n3. Simulating Merge...")
assets = base_assets.copy()
for cat, items in user_assets.items():
    if cat in assets:
        assets[cat].update(items)
    else:
        assets[cat] = items

characters_all = list(assets.get('characters', {}).keys())
print(f"Total Characters: {len(characters_all)}")
print(f"Sample: {characters_all[:10]}")

# Check for obvious cross-contamination
print("\n--- CONTAMINATION CHECK ---")
outfit_keywords = ["dress", "suit", "jacket", "shirt", "pant", "nightout"]
bad_chars = [c for c in characters_all if any(x in c.lower() for x in outfit_keywords) and "wearing" not in c.lower()]
if bad_chars:
    print(f"⚠️ POSSIBLY BAD CHARACTERS (might be outfits): {bad_chars[:10]}")
else:
    print("✅ No obvious outfit keywords found in character list.")
