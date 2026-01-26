import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()

def list_user_images_from_s3(username):
    """
    Lists all images for a specific user from S3.
    Returns list of dicts: [{"url": str, "key": str, "timestamp": int}, ...]
    """
    bucket = os.getenv("S3_BUCKET_NAME")
    region = os.getenv("AWS_REGION", "ap-southeast-2")
    
    if not bucket:
        return []
    
    try:
        s3 = boto3.client('s3', region_name=region)
        prefix = f"user_generated/"
        
        response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
        
        if 'Contents' not in response:
            return []
        
        images = []
        for obj in response['Contents']:
            key = obj['Key']
            # Only include image files
            if key.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                url = f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
                images.append({
                    "url": url,
                    "key": key,
                    "timestamp": int(obj['LastModified'].timestamp()),
                    "filename": os.path.basename(key)
                })
        
        # Sort by timestamp (newest first)
        images.sort(key=lambda x: x['timestamp'], reverse=True)
        return images
        
    except ClientError as e:
        print(f"Error listing S3 images: {e}")
        return []

def is_cloud_mode():
    """Detects if running on Streamlit Cloud"""
    return bool(os.getenv("STREAMLIT_SHARING_MODE")) or not os.path.exists("/Users")
