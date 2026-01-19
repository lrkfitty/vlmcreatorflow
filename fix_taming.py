import os
import subprocess
import sys

def fix_taming():
    print("🚑 STARTING TAMING REPAIR...")
    
    home = os.path.expanduser("~")
    webui_dir = os.path.join(home, "stable-diffusion-webui")
    venv_python = os.path.join(webui_dir, "venv", "bin", "python")
    taming_path = os.path.join(webui_dir, "repositories", "taming-transformers")
    
    if not os.path.exists(taming_path):
        print(f"❌ Error: Folder not found at {taming_path}")
        return

    print(f"🔧 Installing taming-transformers from: {taming_path}")
    
    # Force pip install using the venv python
    try:
        subprocess.run([venv_python, "-m", "pip", "install", "-e", taming_path], check=True)
        print("✅ Installation command finished.")
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return

    print("\n✨ REPAIR ATTEMPT COMPLETE! ✨")
    print("Try running the ./webui.sh start command again now.")

if __name__ == "__main__":
    fix_taming()
