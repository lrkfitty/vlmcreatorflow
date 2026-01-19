import os
import time
import requests
import jwt
import json
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
    return jwt.encode(payload, secret_key, algorithm="HS256", headers=headers)

def probe_endpoints():
    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    if not ak or not sk:
        print("Missing credentials")
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

    # List of endpoints to try (Restoring full list because it works)
    endpoints = [
        "https://api.klingai.com/v1/videos",
        "https://api.klingai.com/v1/videos/image2video", 
        "https://api.klingai.com/v1/tasks",
        "https://api.klingai.com/v1/images/videos" 
    ]

    print("🕵️‍♂️ Fetching Video List (Voodoo Mode)...")
    
    for url in endpoints:
        print(f"\nRequesting {url} ...")
        try:
            resp = requests.get(url, headers=headers)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Robust Parsing (Ported from Recovery Script)
                tasks = []
                if isinstance(data, dict):
                    # Format A: data['data']['tasks']
                    if "data" in data and isinstance(data["data"], dict) and "tasks" in data["data"]:
                        tasks = data["data"]["tasks"]
                    # Format B: data['data'] is list
                    elif "data" in data and isinstance(data["data"], list):
                        tasks = data["data"]
                    # Format C: data['tasks']
                    elif "tasks" in data:
                        tasks = data["tasks"]
                
                print(f"✅ Found {len(tasks)} tasks.")
                
                if tasks:
                     print(f"DEBUG: Sample Task Dump: {json.dumps(tasks[0], indent=2)}")
                     
                for t in tasks:
                    tid = t.get("task_id")
                    status = t.get("task_status")
                    model_used = t.get("task_info", {}).get("model") or t.get("model") or "Unknown"
                    print(f"Task {tid} | Status: {status} | Model: {model_used}")
                    
                    if status == "succeed":
                         result = t.get("task_result")
                         video_url = None
                         if result and "videos" in result and len(result["videos"]) > 0:
                              video_url = result["videos"][0].get("url")
                         
                         if video_url:
                              filename = f"output/kling_{tid}.mp4"
                              if os.path.exists(filename):
                                  print(f"  ⏭️  Exists: {tid}")
                                  continue
                                  
                              print(f"  ⬇️  Downloading {tid}...")
                              try:
                                  v_resp = requests.get(video_url, stream=True)
                                  if v_resp.status_code == 200:
                                      with open(filename, 'wb') as f:
                                          for chunk in v_resp.iter_content(chunk_size=8192):
                                              f.write(chunk)
                                      print(f"     ✅ Saved")
                                      count += 1
                                  else:
                                      print(f"     ❌ Download Failed: {v_resp.status_code}")
                              except Exception as e:
                                  print(f"     ❌ Error: {e}")
                print(f"\n🎉 Downloaded {count} videos.")
                
            else:
                print(f"Error: {resp.text[:200]}")
        except Exception as e:
            print(f"Request failed: {e}")

if __name__ == "__main__":
    probe_endpoints()
