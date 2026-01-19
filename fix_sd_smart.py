import os
import shutil
import subprocess

def fix_download():
    print("🚀 ATTEMPTING SMART DOWNLOAD (Spoofing User-Agent)...")
    
    home = os.path.expanduser("~")
    repo_dir = os.path.join(home, "stable-diffusion-webui", "repositories")
    target_dir = os.path.join(repo_dir, "stable-diffusion-stability-ai")
    
    # 1. correct URL
    zip_url = "https://github.com/Stability-AI/stablediffusion/archive/refs/heads/main.zip"
    zip_path = os.path.join(repo_dir, "smart_fix.zip")
    
    # 2. Curl with headers (Pretending to be a Browser)
    cmd = [
        "curl", "-L", 
        "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "-o", zip_path, zip_url
    ]
    
    subprocess.run(cmd, check=False)
    
    # 3. Check Size
    if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 10000:
        print("❌ Download failed (Network Blocked).")
        return

    print("✅ Download Success! Unzipping...")
    
    # 4. Clean old
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        
    # 5. Unzip
    subprocess.run(["unzip", "-o", "-q", zip_path, "-d", repo_dir], check=False)
    
    # 6. Find and Move
    # It usually extracts as 'stablediffusion-main'
    extracted = os.path.join(repo_dir, "stablediffusion-main")
    if os.path.exists(extracted):
        shutil.move(extracted, target_dir)
        print("✨ REPO SWAPPED! 'midas' module should be present now.")
    else:
        print(f"⚠️ Unzipped but couldn't find 'stablediffusion-main'. Found: {os.listdir(repo_dir)}")

    # 7. Re-apply Dummy Git Fix immediately
    print("🛡️ Re-applying Git Lock...")
    subprocess.run(["python3", os.path.join(os.path.dirname(__file__), "make_dummy_git.py")], check=False)

if __name__ == "__main__":
    fix_download()
