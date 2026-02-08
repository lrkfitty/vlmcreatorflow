import sys
import os
# Mock Streamlit session state if needed, or just import logic
from execution.load_assets import load_assets

try:
    print("Loading assets...")
    data = load_assets(skip_base=False)
    chars = data.get("characters", {})
    print(f"Loaded {len(chars)} characters.")
    
    # Print first 5 items to check structure
    for k, v in list(chars.items())[:5]:
        print(f"Key: {k}")
        print(f"Type: {type(v)}")
        print(f"Value: {v}")
        print("-" * 20)
        
except Exception as e:
    print(f"Error: {e}")
