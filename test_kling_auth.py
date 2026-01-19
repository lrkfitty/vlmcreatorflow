import os
import jwt
import time
import requests
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Kling API Authentication...")

ak = os.getenv("KLING_ACCESS_KEY")
sk = os.getenv("KLING_SECRET_KEY")

if not ak or not sk:
    print("❌ Keys Missing in .env")
    exit(1)

print(f"✅ Found Access Key: {ak[:5]}...")

try:
    # Generate Token
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, sk, algorithm="HS256", headers=headers)
    print("✅ JWT Token Generated Successfully.")
except Exception as e:
    print(f"❌ JWT Generation Failed: {e}")
    exit(1)

# Test API Connectivity
url = "https://api.klingai.com/v1/videos/image2video"
headers_api = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Sending empty body to provoke a 400 (Bad Request) which confirms Auth works.
# If Auth fails, we get 401/403.
print("📡 Sending Test Request to Kling API...")
response = requests.post(url, json={}, headers=headers_api)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code in [400, 422]:
    print("✅ Authentication Passed! (Error 400/422 is expected for empty body).")
elif response.status_code == 401:
    print("❌ Authorization Failed (401). Check Secret Key.")
else:
    print("⚠️ Unexpected Response.")
