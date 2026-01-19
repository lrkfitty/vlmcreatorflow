import os
import sys
import time
import requests
import jwt
import base64
from dotenv import load_dotenv

load_dotenv()

def get_kling_token(access_key, secret_key):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": access_key,
        "exp": int(time.time()) + 1800, # 30 mins
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)
    return token

def fetch_video(task_id):
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    
    if not ak or not sk:
        print("Error: Missing KLING keys")
        return

    try:
        token = get_kling_token(ak, sk)
    except Exception as e:
        print(f"Token Error: {e}")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print(f"🔍 Checking Status for Task: {task_id} (using List Strategy)")
    # Direct endpoint gives 404, must list recent
    url = "https://api.klingai.com/v1/videos/image2video"
    params = {"page": 1, "page_size": 20}
    
    try:
        resp = requests.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            print(f"API Error: {resp.text}")
            return
            
        data = resp.json()
        
        # Robust Parsing
        tasks = []
        if isinstance(data, dict):
            if "data" in data and isinstance(data["data"], dict) and "tasks" in data["data"]:
                tasks = data["data"]["tasks"]
            elif "data" in data and isinstance(data["data"], list):
                tasks = data["data"]
            elif "tasks" in data:
                tasks = data["tasks"]
                
        # Find Target
        target_task = None
        for t in tasks:
            if t.get("task_id") == task_id:
                target_task = t
                break
                
        if not target_task:
            print(f"⚠️ Task {task_id} not found in recent 20 videos.")
            print("Try checking older pages? (Script defaults to page 1)")
            return
            
        status = target_task.get("task_status") or target_task.get("status")
        print(f"Status: {status}")
        
        if status == "succeed":
            result = target_task.get("task_result")
            video_url = None
            if result and "videos" in result and len(result["videos"]) > 0:
                video_url = result["videos"][0].get("url")
            
            if video_url:
                print(f"🎥 Video URL Found: {video_url}")
                
                # Download
                filename = f"output/manual_kling_{task_id}.mp4"
                if not os.path.exists("output"): os.makedirs("output")
                
                print(f"⬇️ Downloading to {filename}...")
                v_resp = requests.get(video_url, stream=True)
                if v_resp.status_code == 200:
                    with open(filename, 'wb') as f:
                        for chunk in v_resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("✅ Download Complete!")
                else:
                    print(f"❌ Download Failed: {v_resp.status_code}")
            else:
                print("⚠️ No video URL in result payload.")
                print(data)
        else:
            print(f"Task result payload: {data}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 fetch_kling_video.py <TASK_ID>")
    else:
        fetch_video(sys.argv[1])
