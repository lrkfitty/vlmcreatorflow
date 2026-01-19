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
    # Correct path for Automatic1111 models
    models_dir = os.path.join(home, "stable-diffusion-webui", "models", "Stable-diffusion")
    
    if not os.path.exists(models_dir):
        print(f"❌ Could not find models directory: {models_dir}")
        return

    # Realistic Vision V6.0 B1 (FP16 Version - 2GB, Faster)
    model_url = "https://huggingface.co/SG161222/Realistic_Vision_V6.0_B1_noVAE/resolve/main/Realistic_Vision_V6.0_NV_B1_fp16.safetensors"
    target_path = os.path.join(models_dir, "Realistic_Vision_V6.0_NV_B1_fp16.safetensors")

    if os.path.exists(target_path):
        print("ℹ️  Model already exists.")
    else:
        print("🚀 Starting High-Speed Download...")
        try:
            download_file(model_url, target_path)
            print(f"🎉 Installed to: {target_path}")
            print("👉 You must Restart the Server for it to see the new model.")
        except Exception as e:
            print(f"❌ Download failed: {e}")

if __name__ == "__main__":
    install_model()
