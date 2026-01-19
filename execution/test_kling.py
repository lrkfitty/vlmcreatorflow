import os
import requests
import jwt
import time
from dotenv import load_dotenv

load_dotenv()

def get_kling_token(access_key, secret_key):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)
    return token

def test_connection():
    print("--- Testing Kling API Connection ---")
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    
    if not ak or not sk:
        print("❌ Error: Missing KLING_ACCESS_KEY or KLING_SECRET_KEY in .env")
        return

    print(f"🔑 Access Key found: {ak[:5]}...")
    
    try:
        token = get_kling_token(ak, sk)
        print("✅ JWT Token generated successfully.")
    except Exception as e:
        print(f"❌ JWT Generation Failed: {e}")
        return

    # Try to hit a benign endpoint, e.g. list tasks (if available) or just check if generation endpoint accepts request (400 vs 401)
    # Kling doesn't have a simple "whoami", so we'll assume Token is valid if JWT works, 
    # but let's try to fetch a specific non-existent task to check auth vs 404.
    
    url = "https://api.klingai.com/v1/tasks/test_dummy_id"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"📡 API Response Code: {response.status_code}")
    print(f"📄 Response Text: {response.text}")
    
    if response.status_code == 401 or response.status_code == 403:
        print("❌ Authentication Failed (401/403). Check Key permissions.")
    elif response.status_code == 404 or response.status_code == 400: # 404 means Auth passed but task not found
        print("✅ Connection Successful (Auth Passed, Endpoint Reachable).")
    else:
        print("⚠️ Unexpected Response. Check logs.")

if __name__ == "__main__":
    test_connection()
