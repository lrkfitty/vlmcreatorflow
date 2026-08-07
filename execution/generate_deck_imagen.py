import os
import requests
import json
import base64
from dotenv import load_dotenv

os.chdir("/Users/tylarkin/Desktop/AI Cnntent Creator workflow")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def generate_photorealistic_image(filename, prompt):
    print(f"Generating {filename}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "instances": [
            {"prompt": prompt}
        ],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "16:9"
        }
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code == 200:
            res = r.json()
            try:
                base64_img = res['predictions'][0]['bytesBase64Encoded']
                img_data = base64.b64decode(base64_img)
                filepath = f"/Users/tylarkin/Desktop/AI Cnntent Creator workflow/pitch_deck_assets/{filename}"
                with open(filepath, "wb") as f:
                    f.write(img_data)
                print(f"SUCCESS: Saved to {filepath}")
            except Exception as parse_e:
                print("Error parsing image data. Response structure might differ:")
                print(json.dumps(res, indent=2)[:1000])
        else:
            print(f"Error HTTP {r.status_code}: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    cover_prompt = "Ultra-realistic 4K raw photography of a Black man with short hair and tattoos, and a Black woman with long wavy hair standing side-by-side looking incredibly fit and stylish. Unedited documentary style, shot on Sony A7R IV, 85mm lens. Natural skin texture, subtle imperfections, realistic sunlight. They are outdoors on a modern fitness rooftop at late afternoon. Authentic, real, not over polished or shiny. Heavy negative space on the left side. 16:9 ratio."
    
    stage_prompt = "Ultra-realistic 4K raw photography of a Black man with short hair and tattoos, and a Black woman with long wavy hair standing side-by-side on a masterclass stage giving a passionate business talk. Unedited documentary speaking event style, shot on Sony A7R IV, 85mm lens. Natural skin texture, realistic stage lighting and soft shadows. Professional but authentic corporate speaking event, real, not overly polished or shiny. Heavy negative space on the left side. 16:9 ratio."
    
    generate_photorealistic_image("raw_cover_slide.png", cover_prompt)
    generate_photorealistic_image("raw_stage_slide.png", stage_prompt)
