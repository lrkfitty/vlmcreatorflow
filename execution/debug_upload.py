import os
import boto3
from dotenv import load_dotenv
import sys

# Mocking app.py context
sys.path.append(os.getcwd())
load_dotenv()

from execution.s3_uploader import upload_file_obj

username = "angeil.lark@gmail.com"
target_cat = "Outfits"
cat_map = {"Outfits": "Outfits"}
filename = "debug_test_upload.png"

print(f"--- DEBUG UPLOAD TEST ---")
print(f"User: {username}")
print(f"Bucket: {os.getenv('S3_BUCKET_NAME')}")

# Create dummy file
with open(filename, "wb") as f:
    f.write(b"DATA")

try:
    s3_key = f"users/{username}/Assets/{cat_map[target_cat]}/{filename}"
    print(f"Attempting Upload to key: {s3_key}")
    
    with open(filename, "rb") as f_up:
        url = upload_file_obj(f_up, object_name=s3_key)
    
    if url:
        print("✅ SUCCESS: Upload returned URL")
        print(url)
    else:
        print("❌ FAILURE: Upload returned None")

except Exception as e:
    print(f"❌ CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()

# Cleanup
if os.path.exists(filename):
    os.remove(filename)
