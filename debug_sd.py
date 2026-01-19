import os
import sys

def debug():
    print("🕵️‍♂️ DIAGNOSTIC REPORT")
    home = os.path.expanduser("~")
    repo = os.path.join(home, "stable-diffusion-webui", "repositories", "taming-transformers")
    
    # 1. Check Folder
    if os.path.exists(repo):
        print(f"✅ Repo exists: {repo}")
        files = os.listdir(repo)
        print(f"📂 Contents: {files}")
        
        if "taming" in files:
            print("✅ 'taming' subfolder found. Structure looks correct.")
        else:
            print("❌ 'taming' subfolder NOT found. It might be nested inside another folder!")
    else:
        print("❌ Repo folder MISSING.")
        
    # 2. Check Virtual Environment
    venv_site = os.path.join(home, "stable-diffusion-webui", "venv", "lib", "python3.10", "site-packages")
    # Note: version might vary (3.9 or 3.10). Quick check.
    if not os.path.exists(venv_site):
         # Try 3.9
         venv_site = os.path.join(home, "stable-diffusion-webui", "venv", "lib", "python3.9", "site-packages")
    
    if os.path.exists(venv_site):
        print(f"✅ Venv site-packages found: {venv_site}")
        links = os.listdir(venv_site)
        has_taming = any("taming" in s for s in links)
        if has_taming:
            print("✅ 'taming' appears to be installed in venv.")
        else:
            print("❌ 'taming' is NOT installed in venv.")
    else:
        print("❌ Venv site-packages folder not found.")

if __name__ == "__main__":
    debug()
