import boto3
import requests
import os
from dotenv import load_dotenv
from botocore.config import Config

load_dotenv()

bucket = "vlmcreateflowbucket"
key = "users/Tytheguyttg/Assets/Characters/Shay blonde bob back.png"

print("--- TESTING S3 URL STYLES ---")

# Test 1: SKIPPED (Known Issue)
# print("\n1. Testing PATH STYLE (Current Broken Setup)...")
# s3_path = boto3.client(...)
# ...


# Test 2: Proposed Fix (Virtual Host Style with Region)
print("\n2. Testing VIRTUAL HOST STYLE (Regional)...")
s3_virtual = boto3.client(
    's3', 
    region_name="ap-southeast-2",
    # NO explicit endpoint_url, just region + config
    config=Config(s3={'addressing_style': 'virtual', 'signature_version': 's3v4'})
)
url_virtual = s3_virtual.generate_presigned_url(
    'get_object',
    Params={'Bucket': bucket, 'Key': key},
    ExpiresIn=3600
)
print(f"URL: {url_virtual}")
try:
    # Simulate Browser Request with Origin
    headers = {'Origin': 'http://localhost:8501'} 
    r = requests.get(url_virtual, headers=headers, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Headers: {r.headers}")
    if 'Access-Control-Allow-Origin' in r.headers:
        print("✅ CORS Header Present")
    else:
        print("⚠️ CORS HEADER MISSING (Likely Browser Block)")

    if r.status_code == 200:
        print("✅ SUCCESS (Python)")
except Exception as e:
    print(f"Error: {e}")
