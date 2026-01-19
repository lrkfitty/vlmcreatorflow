import os
import json
from load_assets import load_assets
from dotenv import load_dotenv

load_dotenv()

def debug_urls():
    print("🔎 Debugging Asset URLs...")
    
    # Load assets using the actual function
    data = load_assets()
    
    print("\n--- SAMPLE URLs ---")
    
    # Print 1 sample from each category
    for category, items in data.items():
        if items:
            name, url = list(items.items())[0]
            print(f"\n📂 [{category.upper()}] example:")
            print(f"   Name: {name}")
            print(f"   URL:  {url}")
            
            # Try to fetch it?
            # import requests
            # r = requests.head(url)
            # print(f"   Status: {r.status_code}")
        else:
            print(f"\n⚠️ [{category.upper()}] is EMPTY!")

if __name__ == "__main__":
    debug_urls()
