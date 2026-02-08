import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_IMAGE_KEY")

def test_model():
    model_name = 'gemini-2.0-flash-exp-image-generation' # Potential Level 2?
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    # Test 1: Simple text
    print("--- Test 1: Text Prompt ---")
    payload = {
        "contents": [{"parts": [{"text": "Hello, what are you?"}]}]
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"Status: {r.status_code}")
        print(json.dumps(r.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Image Request
    print("\n--- Test 2: Image Prompt ---")
    payload = {
        "contents": [{"parts": [{"text": "Generate an image of a banana."}]}]
    }
    try:
        r = requests.post(url, headers=headers, json=payload)
        print(f"Status: {r.status_code}")
        # Only print a snippet if it's huge (image data)
        res = r.json()
        print(json.dumps(res, indent=2)[:500] + "...") 
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_model()
