import boto3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

bucket_name = "vlmcreateflowbucket" 
# Key from the log error
key = "users/Tytheguyttg/Assets/Characters/Shay blonde bob back.png"

print(f"--- DEBUGGING KEY: {key} ---")

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWSAccessKeyId"), # trying env var naming or default AWS_ACCESS_KEY_ID
    aws_secret_access_key=os.getenv("AWSSecretKey"), 
    region_name="ap-southeast-2",
    endpoint_url="https://s3.ap-southeast-2.amazonaws.com" # FORCE REGIONAL ENDPOINT
)

# 1. Check if object exists
try:
    head = s3.head_object(Bucket=bucket_name, Key=key)
    size_mb = head['ContentLength'] / (1024 * 1024)
    print(f"✅ Object Exists. Size: {size_mb:.2f} MB")
    
    # 2. Try Direct Boto Download (Bypassing Presigned URL)
    print("Attempting Direct Boto3 Download...")
    s3.download_file(Bucket=bucket_name, Key=key, Filename="debug_download_test.png")
    print("✅ Boto3 Download Success!")
    
except Exception as e:
    print(f"❌ Direct Access Failed: {e}")

# 3. Generate URL (Skip if direct failed, but useful for logs)
try:
    url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': key},
        ExpiresIn=3600
    )
    print(f"Generated URL: {url}")
    
    # 3. Try Downloading
    print("Attempting Download...")
    r = requests.get(url, timeout=10)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        print(f"✅ Success! Content-Length: {r.headers.get('Content-Length')}")
    else:
        print(f"❌ Failed: {r.text}")
except Exception as e:
    print(f"❌ Gen/DL Error: {e}")
