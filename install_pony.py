import os
import requests
import sys

def download_file(url, filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_length = int(r.headers.get('content-length'))
        print(f"⬇️  Downloading {os.path.basename(filename)} ({total_length / 1024 / 1024:.1f} MB)...")
        
        with open(filename, 'wb') as f:
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192): 
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Simple progress bar
                    done = int(50 * downloaded / total_length)
                    sys.stdout.write(f"\r[{'=' * done}{' ' * (50-done)}] {int(downloaded/total_length*100)}%")
                    sys.stdout.flush()
    print("\n✅ Download complete!")

def install_model():
    home = os.path.expanduser("~")
    models_dir = os.path.join(home, "stable-diffusion-webui", "models", "Stable-diffusion")
    
    if not os.path.exists(models_dir):
        print(f"❌ Could not find models directory: {models_dir}")
        return

    # Pony Realism v2.1 (SDXL) - The "God Tier" NSFW/Realism Hybrid
    # This is a large file (~6GB)
    model_url = "https://huggingface.co/LyliaEngine/ponyRealism_v21MainVAE/resolve/main/ponyRealism_v21MainVAE.safetensors"
    target_path = os.path.join(models_dir, "ponyRealism_v21MainVAE.safetensors")

    if os.path.exists(target_path):
        print("ℹ️  Model already exists.")
    else:
        print("🚀 Starting Pony Realism Download (This is BIG - ~6GB)...")
        try:
            download_file(model_url, target_path)
            print(f"🎉 Installed to: {target_path}")
            print("👉 You must Restart the Server for it to see the new model.")
        except Exception as e:
            print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    install_model()
