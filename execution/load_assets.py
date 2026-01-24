import os
import json

def scan_directory(directory):
    """Recursively finds all image files in a directory. Returns {RelativePath / Name: absolute_path}."""
    items = {}
    if not os.path.exists(directory):
        return items
    
    base_dir_abs = os.path.abspath(directory)
        
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')) and not file.startswith('._'):
                full_path = os.path.abspath(os.path.join(root, file))
                
                # Calculate relative path
                rel_dir = os.path.relpath(root, base_dir_abs)
                
                # Base filename
                name = os.path.splitext(file)[0].replace('_', ' ').title()
                
                if rel_dir == ".":
                    final_name = name
                else:
                    # Make relative path readable
                    # e.g. "Summer/Beach" -> "Summer / Beach / Name"
                    rel_parts = [p.replace('_', ' ').title() for p in rel_dir.split(os.sep)]
                    prefix = " / ".join(rel_parts)
                    final_name = f"{prefix} / {name}"
                
                items[final_name] = full_path
    
    # Sort by name
    return dict(sorted(items.items()))

# --- CLOUD MANIFEST LOGIC ---
# (scan_manifest function removed - logic moved to Single Pass loop below)

def load_assets(base_path="assets", user_assets_dir=None):
    """
    Dynamically loads assets.
    If 'assets_manifest.json' exists, uses S3 URLs (Cloud Mode).
    Otherwise scans local 'assets/' folder (Local Mode).
    """
    
    data = {
        "vibes": {},
        "outfits": {},
        "characters": {},
        "locations": {},
        "relations": {},
        "pets": {},
        "props": {},
        "vehicles": {},
        "foods": {}
    }
    
    # 1. CHECK FOR CLOUD MANIFEST
    manifest_path = "assets_manifest.json"
    use_cloud = False
    
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
            
            bucket = os.getenv("S3_BUCKET_NAME")
            if bucket:
                region = os.getenv("AWS_REGION", "ap-southeast-2")
                s3_base = f"https://{bucket}.s3.{region}.amazonaws.com/assets"
                print(f"☁️ Cloud Mode Activated: Using {s3_base}")
                use_cloud = True
            else:
                print("⚠️ Manifest found but S3_BUCKET_NAME missing. Falling back to local.")
        except Exception as e:
            print(f"⚠️ Error reading manifest: {e}")
            
    if use_cloud:
        # --- CLOUD LOADING (Single Pass) ---
        print(f"☁️ Cloud Mode: Scanning {len(manifest)} items from manifest...")
        
        # explicit mapping of Folder Name (in manifest) -> Data Category Key
        folder_map = {
            "environments": "locations",
            "vibes": "vibes",
            "outfits": "outfits",
            "influencer clothing": "outfits",
            "influencer clothing ": "outfits", # Handle trailing space
            "characters": "characters",
            "shay.so.fine": "characters", # Legacy Mapping
            "friends": "relations",
            "pets": "pets",
            "props": "props",
            "vehicles": "vehicles",
            "foods": "foods"
        }

        for rel_path in manifest:
            # manifest path: "AI Content Creators/Category/Sub/File.png"
            parts = rel_path.split("/")
            
            # Skip root if present
            start_idx = 0
            if len(parts) > 0 and parts[0] == "AI Content Creators":
                start_idx = 1
            
            if len(parts) <= start_idx + 1: continue # Need at least Category + File
            
            # Identify Category Folder
            cat_folder = parts[start_idx].lower().strip()
            
            # Map to App Category
            target_key = folder_map.get(cat_folder)
            
            if target_key:
                # Generate Name
                # Everything after Category Folder and before Filename is "SubPath"
                sub_parts = parts[start_idx+1 : -1]
                filename = os.path.splitext(parts[-1])[0].replace('_', ' ').title()
                
                if not sub_parts:
                    final_name = filename
                else:
                    prefix_str = " / ".join([p.replace('_', ' ').title() for p in sub_parts])
                    final_name = f"{prefix_str} / {filename}"
                
                # Generate URL
                url = f"{s3_base}/{rel_path.replace(' ', '%20')}"
                
                # Add to Data
                data[target_key][final_name] = url
        
        # Fallback: If Vibes empty, use Locations
        if not data["vibes"]:
            data["vibes"] = data["locations"]
            
        return data

    # --- LOCAL FALLBACK (Existing Logic) ---
    
    if not os.path.exists(base_path):
        cwd_path = os.path.join(os.getcwd(), "assets/AI Content Creators") # Try old path
        if os.path.exists(cwd_path):
            base_path = cwd_path
        elif os.path.exists("assets"):
             base_path = "assets"
        else:
            print(f"Warning: Base path {base_path} not found.")
            return data

    # --- 1. Vibes / Locations ---
    env_path = os.path.join(base_path, "Environments")
    if os.path.exists(env_path):
        data["locations"] = scan_directory(env_path)
    
    vibes_path = os.path.join(base_path, "Vibes")
    if os.path.exists(vibes_path):
        data["vibes"] = scan_directory(vibes_path)
    else:
        data["vibes"] = data["locations"]
    
    # --- 2. Outfits ---
    outfits_path = os.path.join(base_path, "Outfits")
    if not os.path.exists(outfits_path):
        # Handle typo folders
        for typo in ["Influencer CLothing ", "Influencer CLothing"]:
             p = os.path.join(base_path, typo)
             if os.path.exists(p): outfits_path = p; break
             
    data["outfits"] = scan_directory(outfits_path)
    
    # --- 3. Characters ---
    # A. New Standard Structure
    chars_path_strict = os.path.join(base_path, "Characters")
    if os.path.exists(chars_path_strict):
        data["characters"].update(scan_directory(chars_path_strict))
    
    # B. Legacy Fallback (Root Folders)
    exclude = [
        "Environments", "Influencer CLothing ", "Influencer CLothing", 
        "Random Influencer Models", "Vibes", "Outfits", "Characters",
        "Friends", "Pets", "Props", "Vehicles", "Foods", ".DS_Store"
    ]
    
    if os.path.exists(base_path):
        root_folders = [d for d in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, d))]
        for folder in root_folders:
            if folder not in exclude:
                c_path = os.path.join(base_path, folder)
                c_images = scan_directory(c_path)
                for relative_key, full_path in c_images.items():
                    full_key = f"{folder} / {relative_key}"
                    if full_key not in data["characters"]:
                         data["characters"][full_key] = full_path
            
    # --- 4. Others (Standard) ---
    data["relations"] = scan_directory(os.path.join(base_path, "Friends"))
    data["pets"] = scan_directory(os.path.join(base_path, "Pets"))
    data["props"] = scan_directory(os.path.join(base_path, "Props"))
    data["vehicles"] = scan_directory(os.path.join(base_path, "Vehicles"))
    data["foods"] = scan_directory(os.path.join(base_path, "Foods"))

    # --- 5. User Assets (If Logged In) ---
    if user_assets_dir and os.path.exists(user_assets_dir):
        # Scan standard folders in user directory
        user_cats = {
            "Characters": "characters",
            "Environments": "locations",
            "Outfits": "outfits",
            "Vibes": "vibes",
            "Friends": "relations",
            "Pets": "pets",
            "Props": "props",
            "Vehicles": "vehicles",
            "Foods": "foods"
        }
        
        for folder_name, data_key in user_cats.items():
            u_path = os.path.join(user_assets_dir, folder_name)
            if os.path.exists(u_path):
                user_items = scan_directory(u_path)
                # Merge with prefix to identify them easily
                for name, path in user_items.items():
                    # Prefix with (User) or similar if desired, or just list them.
                    # Using a subtle prefix helps grouping in dropdowns
                    final_key = f"(My) {name}"
                    data[data_key][final_key] = path

    return data

if __name__ == "__main__":
    assets = load_assets()
    print(json.dumps(assets, indent=2))
