import os
import sys
from dotenv import load_dotenv

# Mock the environment
load_dotenv()

# Add execution dir to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from generate_image import generate_image_nano

# Mock Data
prompt_data = {
    "positive_prompt": "A cinematic shot of a woman in a cafe.",
    "aspect_ratio": "9:16",
    # Simulate what app.py sends
    "model_type": "nano" 
}

# Mock Paths (Use a real URL if possible, or a local dummy)
# Using a placeholder URL to see if it attempts to download or logs it
test_url = "https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png" 

print("--- TESTING LEGACY ARGS ---")
result = generate_image_nano(
    prompt_data, 
    "output", 
    reference_image_path=test_url, 
    outfit_path=None, 
    vibe_path=None
)

print("\n--- RESULT ---")
print(result)
