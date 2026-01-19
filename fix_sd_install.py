import os
import shutil
import subprocess
import sys

def fix_sd():
    print("🚑 STARTING AUTOMATIC REPAIR...")
    
    # 1. Locate the WebUI
    home = os.path.expanduser("~")
    webui_dir = os.path.join(home, "stable-diffusion-webui")
    repo_dir = os.path.join(webui_dir, "repositories")
    target_dir = os.path.join(repo_dir, "stable-diffusion-stability-ai")
    
    if not os.path.exists(webui_dir):
        print(f"❌ Could not find folder: {webui_dir}")
        print("Make sure you cloned it to your home folder!")
        return

    # 2. Delete the broken folder
    if os.path.exists(target_dir):
        print(f"🗑️  Deleting broken repository: {target_dir}")
        shutil.rmtree(target_dir) # Nukes it completely
    
    # 3. Download from RUNWAYML (Mirror) because Stability-AI is blocking you
    print("⬇️  Downloading fresh copy from RUNWAYML (Mirror)...")
    zip_url = "https://github.com/runwayml/stable-diffusion/archive/refs/heads/main.zip"
    zip_path = os.path.join(repo_dir, "temp_fix.zip")
    
    # Ensure repo dir exists
    os.makedirs(repo_dir, exist_ok=True)
    
    # Clean up old bad zip if exists
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    subprocess.run(["curl", "-L", "-o", zip_path, zip_url], check=True)
    
    # Check file size (If it's tiny, it failed)
    if os.path.getsize(zip_path) < 1000:
        print("❌ Error: Download was too small (likely blocked).")
        with open(zip_path, 'r') as f:
            print(f"File content: {f.read()}")
        return

    # 4. Unzip
    print("📦 Unzipping...")
    try:
        subprocess.run(["unzip", "-o", "-q", zip_path, "-d", repo_dir], check=True)
    except subprocess.CalledProcessError:
        print("❌ Error: Valid Zip not found. Trying another method...")
        return
    
    # 5. Rename/Move
    # RunwayML zip extracts to 'stable-diffusion-main' usually
    extracted_name = os.path.join(repo_dir, "stable-diffusion-main")
    
    if os.path.exists(extracted_name):
        print("Rename folder to 'stable-diffusion-stability-ai'...")
        shutil.move(extracted_name, target_dir)
        print("✅ Fixed Stable Diffusion repository.")
    else:
        print(f"❌ Error: Unzip succeeded but folder names are unexpected. Found: {os.listdir(repo_dir)}")
        return

    # --- PART 2: FIX TAMING TRANSFORMERS (The 'taming' error) ---
    print("\n🚑 FIXING TAMING TRANSFORMERS...")
    taming_dir = os.path.join(repo_dir, "taming-transformers")
    # Exact commit hash for Taming
    taming_zip_url = "https://github.com/CompVis/taming-transformers/archive/24268930bf1dce879235a7fddd0b2355b84d7ea6.zip"
    taming_zip_path = os.path.join(repo_dir, "taming_fix.zip")
    
    if os.path.exists(taming_dir):
        print(f"🗑️  Cleaning old taming folder...")
        shutil.rmtree(taming_dir)
        
    print("⬇️  Downloading Taming Transformers (Commit 2426893)...")
    subprocess.run(["curl", "-L", "-o", taming_zip_path, taming_zip_url], check=True)
    
    print("📦 Unzipping...")
    subprocess.run(["unzip", "-o", "-q", taming_zip_path, "-d", repo_dir], check=True)
    
    # Zip extracts to 'taming-transformers-<commit_hash>'
    taming_extracted = os.path.join(repo_dir, "taming-transformers-24268930bf1dce879235a7fddd0b2355b84d7ea6")
    if os.path.exists(taming_extracted):
         shutil.move(taming_extracted, taming_dir)
         print("✅ Fixed Taming Transformers.")
    else:
         print(f"❌ Error: Could not find extracted taming folder: {taming_extracted}")
    
    # Cleanup Zips
    if os.path.exists(zip_path): os.remove(zip_path)
    if os.path.exists(taming_zip_path): os.remove(taming_zip_path)
        
    print("\n✨ ALL REPAIRS COMPLETE! ✨")
    print("You can now run the server command again.")

if __name__ == "__main__":
    fix_sd()
