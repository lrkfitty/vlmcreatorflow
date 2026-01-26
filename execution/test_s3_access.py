import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from load_assets import load_assets

print("--- LOADING ASSETS ---")
assets = load_assets()
# Pick a character
chars = assets.get("characters", {})
if not chars:
    print("No characters found!")
    sys.exit(1)

first_key = list(chars.keys())[0]
url = chars[first_key]
print(f"Testing Asset: {first_key}")
print(f"URL: {url}")

if url.startswith("http"):
    try:
        resp = requests.get(url)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ Access successful!")
        else:
            print("❌ Access Failed.")
    except Exception as e:
        print(f"❌ Error: {e}")
else:
    print("Asset is a local path, skipping network test.")
