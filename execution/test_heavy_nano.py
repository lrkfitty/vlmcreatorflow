import os
import sys
import requests
import time
from dotenv import load_dotenv

# Mock the environment
load_dotenv()
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))
from generate_image import generate_image_nano

# Use a small public image to simulate 5 different assets (Character, Outfit, Extras)
dummy_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png"

prompt_data = {
    "positive_prompt": "A complex scene with 5 reference assets.",
    "aspect_ratio": "9:16",
    # Simulate 5 assets
    "assets": [
        {"path": dummy_url, "label": "Main Char"},
        {"path": dummy_url, "label": "Outfit"},
        {"path": dummy_url, "label": "Friend"},
        {"path": dummy_url, "label": "Friend Outfit"},
        {"path": dummy_url, "label": "Location"}
    ],
    "model_type": "nano"
}

print("--- STARTING HEAVY LOAD TEST (5 Images) ---")
start_time = time.time()

result = generate_image_nano(
    prompt_data, 
    "output_test", 
    reference_image_path=None, 
    outfit_path=None, 
    vibe_path=None
)

end_time = time.time()
print(f"\n--- TOTAl TIME: {end_time - start_time:.4f} seconds ---")

print("\n--- RESULT ---")
# Only print status and logs, not the full massive JSON if successful
print(f"Status: {result.get('status')}")
print("Logs:")
print(result.get("logs"))
