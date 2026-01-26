
import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

# Add execution dir to path so we can import load_assets
sys.path.append(os.path.join(os.getcwd(), 'execution'))

from load_assets import load_assets

try:
    print("🔄 Loading Assets...")
    assets = load_assets()
    
    outfits = assets.get('outfits', {})
    print(f"📊 Total Outfits Loaded: {len(outfits)}")
    
    print("\n🔍 Checking for 'Matching Sets'...")
    found = 0
    for name, url in outfits.items():
        if "Matching Sets" in name:
            print(f"   ✅ Found: {name}")
            print(f"      🔗 URL: {url}")
            found += 1
            
    if found == 0:
        print("❌ 'Matching Sets' NOT found in loaded assets.")
    else:
        print(f"✅ Found {found} matching items.")

except Exception as e:
    print(f"❌ Error: {e}")
