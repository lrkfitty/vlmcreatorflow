from execution.world_manager import get_assets_by_category
import json

def verify():
    print("Testing get_assets_by_category('relations')...")
    rels = get_assets_by_category('relations')
    print(f"Found {len(rels)} relations.")
    
    # Print first 3 keys
    for k in list(rels.keys())[:3]:
        val = rels[k]
        # Check if it's a dict (DB) or string (FS)
        val_type = type(val)
        print(f"  - {k} ({val_type}): {str(val)[:50]}...")

    print("\nTesting get_assets_by_category('locations')...")
    locs = get_assets_by_category('locations')
    print(f"Found {len(locs)} locations.")

if __name__ == "__main__":
    verify()
