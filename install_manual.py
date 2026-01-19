import os
import shutil
import subprocess

def install_manual():
    print("🕵️ SEARCHING FOR DOWNLOADED FILE...")
    
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    repo_dir = os.path.join(home, "stable-diffusion-webui", "repositories")
    target_dir = os.path.join(repo_dir, "stable-diffusion-stability-ai")
    
    # Check for possible folder names in Downloads
    candidates = [
        "stablediffusion-main",
        "stable-diffusion-main",
        "stablediffusion-master",
        "stablediffusion-cf1d67a6fd5ea1aa600c4df58e5b47da45f6bdbf"
    ]
    
    found_path = None
    for name in candidates:
        candidate_path = os.path.join(downloads, name)
        if os.path.exists(candidate_path):
            found_path = candidate_path
            break
            
    # Also check for ZIP files if they didn't unzip
    if not found_path:
        print("Folder not found in Downloads. Checking for ZIPs...")
        # WE NEED 'stablediffusion-main.zip' (The Official One)
        zips = ["stablediffusion-main.zip", "stablediffusion-main-1.zip", "stable-diffusion-main.zip"]
        for z in zips:
            z_path = os.path.join(downloads, z)
            if os.path.exists(z_path):
                print(f"📦 Found ZIP: {z_path}. Unzipping...")
                subprocess.run(["unzip", "-o", "-q", z_path, "-d", downloads], check=True)
                # After unzip, check candidates again
                for name in candidates:
                    candidate_path = os.path.join(downloads, name)
                    if os.path.exists(candidate_path):
                        found_path = candidate_path
                        break
                if found_path: break

    if not found_path:
        print("\n❌ COULD NOT FIND THE FILE IN YOUR DOWNLOADS FOLDER.")
        print("Please make sure you downloaded the file and unzipped it (if needed).")
        return

    print(f"✅ Found source: {found_path}")
    
    # Clean destination
    if os.path.exists(target_dir):
        print("🗑️  Cleaning old broken folder...")
        shutil.rmtree(target_dir)
        
    os.makedirs(repo_dir, exist_ok=True)
    
    print("🚚 Moving to correct location...")
    shutil.move(found_path, target_dir)
    
    # 🧹 CLEANUP GIT CONFIG (The Undo)
    try:
        subprocess.run(["git", "config", "--global", "--unset", 
                       "url.https://github.com/CompVis/stable-diffusion.git.insteadOf"], 
                       capture_output=True)
        print("🧹 Cleaned up Git configurations.")
    except:
        pass

    print("\n✨ INSTALLATION COMPLETE! ✨")
    print("You can now run: bash \"Desktop/AI Cnntent Creator workflow/start_painter.sh\"")

if __name__ == "__main__":
    install_manual()
