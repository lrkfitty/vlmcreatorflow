import os
import json
import time
import requests
import jwt
import datetime

def get_kling_token(access_key, secret_key):
    """
    Generates a JWT token for Kling API authentication.
    """
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

def generate_video_kling(
    image_path,
    prompt,
    duration=5,
    model_version="2.6",
    quality_mode="pro",
    camera_control=None,
    ref_video_path=None,
    ref_orientation="image",
    output_folder="output",
    # ── Kling 3.0 New Features ─────────────────────────────────────
    image_references=None,      # List of local paths or URLs — character/element refs (up to 7)
                                # Reference them in prompt as @image_1, @image_2 etc.
    image_tail=None,            # Path/URL to use as the END FRAME of the video
    native_audio=False,         # True = Kling generates lip-sync audio natively
    audio_url=None,             # URL to custom audio file (.mp3/.wav, max 5MB, 2-60s)
    negative_prompt=None,       # Text describing what NOT to include
):
    """
    Generates video using Kling AI API.
    Supports full Kling 3.0 feature set: native audio, character references,
    end-frame control, custom audio, and negative prompts.
    """

    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")

    if not ak or not sk:
        return {"status": "failed", "error": "Missing KLING_ACCESS_KEY or KLING_SECRET_KEY"}

    try:
        token = get_kling_token(ak, sk)
    except Exception as e:
        return {"status": "failed", "error": f"Token Generation Failed: {e}"}

    url = "https://api.klingai.com/v1/videos/image2video"

    import base64

    def encode_image(path_or_url):
        """Returns base64 string for local file, or URL string for remote."""
        if not path_or_url:
            return None
        if isinstance(path_or_url, str) and path_or_url.startswith(('http://', 'https://')):
            return path_or_url  # Pass URL directly for image_tail / references
        elif os.path.exists(str(path_or_url)):
            with open(path_or_url, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        return None

    # Encode primary source image (always base64)
    encoded_string = ""
    if image_path.startswith(('http://', 'https://')):
        try:
            resp = requests.get(image_path)
            resp.raise_for_status()
            encoded_string = base64.b64encode(resp.content).decode('utf-8')
        except Exception as e:
            return {"status": "failed", "error": f"Failed to download source image: {e}"}
    elif os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        return {"status": "failed", "error": f"Image path not found: {image_path}"}

    # --- MODEL NAME MAPPING ---
    MODEL_NAME_MAP = {
        "3.0":        "kling-v3",
        "2.6":        "kling-v2-6",
        "2.5":        "kling-v2-5",
        "2.5-turbo":  "kling-v2-5-turbo",
        "2.1":        "kling-v2-1",
        "2.1-master": "kling-v2-1-master",
        "2.0":        "kling-v2",
        "2.0-master": "kling-v2-master",
        "1.6":        "kling-v1-6",
        "1.5":        "kling-v1-5",
        "1.0":        "kling-v1",
    }
    target_model_name = MODEL_NAME_MAP.get(model_version.strip(), f"kling-v{model_version.replace('.', '-')}")

    # --- DURATION SAFETY ---
    duration_int = int(str(duration).replace("s", ""))
    if duration_int == 15 and "v3" not in target_model_name:
        duration_int = 10

    # --- MODE SELECTION ---
    if ref_video_path:
        # MOTION CONTROL MODE
        if not ref_video_path.startswith(('http', 'https')):
            return {"status": "failed", "error": "Motion Control requires a public URL for the reference video."}

        url = "https://api.klingai.com/v1/videos/motion-control"
        payload = {
            "image_url": encoded_string,
            "video_url": ref_video_path,
            "character_orientation": ref_orientation,
            "mode": quality_mode,
            "prompt": prompt,
            "model_name": target_model_name
        }

    else:
        # STANDARD IMAGE-TO-VIDEO
        payload = {
            "model_name": target_model_name,
            "image": encoded_string,
            "prompt": prompt,
            "duration": duration_int,
            "mode": quality_mode,
            "cfg_scale": 0.5
        }

        # ── Kling 3.0: Negative Prompt ───────────────────────────────
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt

        # ── Kling 3.0: Native Audio ──────────────────────────────────
        # enable_audio=True — Kling generates lip-sync / ambient audio (verified param name)
        # Requires Pro mode on Kling 2.6+
        if native_audio:
            payload["enable_audio"] = True

        # ── Kling 3.0: Custom Audio URL ──────────────────────────────
        # Provide a public audio URL — mutually exclusive with enable_audio
        if audio_url:
            payload["audio_url"] = audio_url

        # ── Kling 3.0: End Frame (image_tail) ────────────────────────
        # Sets the LAST frame of the video — drives the motion path
        if image_tail:
            tail_encoded = encode_image(image_tail)
            if tail_encoded:
                if image_tail.startswith(('http', 'https')):
                    payload["image_tail"] = tail_encoded  # URL passthrough
                else:
                    payload["image_tail"] = tail_encoded  # base64

        # ── Kling 3.0: Character / Element Reference Images ──────────
        # Up to 7 images. Reference in prompt as @image_1, @image_2 etc.
        if image_references:
            refs_payload = []
            for i, ref_path in enumerate(image_references[:7], start=1):
                ref_enc = encode_image(ref_path)
                if ref_enc:
                    refs_payload.append({
                        "image": ref_enc,
                        "label": f"@image_{i}"
                    })
            if refs_payload:
                payload["image_references"] = refs_payload

        if camera_control:
            payload["camera_control"] = camera_control

    """
    Generates video using Kling AI API.
    camera_control: Optional dict for 'type' and 'config'.
    ref_video_path: Optional path/URL to a REFERENCE VIDEO for 'Motion Control'.
    ref_orientation: 'image' (max 10s) or 'video' (max 30s) for Motion Control.
    output_folder: Path to save result.
    """

    ak = os.getenv("KLING_ACCESS_KEY")
    sk = os.getenv("KLING_SECRET_KEY")
    
    if not ak or not sk:
        return {"status": "failed", "error": "Missing KLING_ACCESS_KEY or KLING_SECRET_KEY"}

    # Generate Bearer Token
    try:
        token = get_kling_token(ak, sk)
    except Exception as e:
        return {"status": "failed", "error": f"Token Generation Failed: {e}"}

    # API Endpoint (Default)
    url = "https://api.klingai.com/v1/videos/image2video"  
    
    # Check if we are doing Motion Transfer (Video + Image)
    # The 'camera_control' arg is reused here as a general 'options' dict, 
    # but strictly speaking we need a 'ref_video_path' argument to trigger this mode.
    # We will need to update the function signature in the next step.
    
    # Encode Image (Standard Logic) ...
    import base64
    # Encode Image
    import base64
    encoded_string = ""
    
    if image_path.startswith(('http://', 'https://')):
        try:
            resp = requests.get(image_path)
            resp.raise_for_status()
            encoded_string = base64.b64encode(resp.content).decode('utf-8')
        except Exception as e:
            return {"status": "failed", "error": f"Failed to download source image: {e}"}
    elif os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    else:
        return {"status": "failed", "error": f"Image path not found: {image_path}"}

    # --- MODEL NAME MAPPING ---
    # Official Kling API model_name identifiers (verified from klingai.com docs).
    MODEL_NAME_MAP = {
        # Kling 3.0 Series (latest) — 3–15s, multi-shot
        "3.0":        "kling-v3",
        # Kling 2.x Series
        "2.6":        "kling-v2-6",           # stable workhorse
        "2.5":        "kling-v2-5",
        "2.5-turbo":  "kling-v2-5-turbo",
        "2.1":        "kling-v2-1",
        "2.1-master": "kling-v2-1-master",    # pro only
        "2.0":        "kling-v2",             # "Master Edition" launch name
        "2.0-master": "kling-v2-master",
        # Kling 1.x (legacy, still supported)
        "1.6":        "kling-v1-6",
        "1.5":        "kling-v1-5",
        "1.0":        "kling-v1",
    }
    target_model_name = MODEL_NAME_MAP.get(model_version.strip(), f"kling-v{model_version.replace('.', '-')}")

    # --- DURATION SAFETY ---
    # Kling 3.0 supports 5s, 10s, 15s. Older models only support 5s / 10s.
    duration_int = int(str(duration).replace("s", ""))
    if duration_int == 15 and "v3" not in target_model_name:
        duration_int = 10  # Clamp to 10s for non-3.0 models

    # --- MODE SELECTION ---
    if ref_video_path:
        # MOTION CONTROL MODE (Video + Image)
        if not ref_video_path.startswith(('http', 'https')):
             return {"status": "failed", "error": "For Motion Control, the Reference Video MUST be a public URL (S3). Local files not supported yet."}
             
        url = "https://api.klingai.com/v1/videos/motion-control"
        
        # Motion Control Payload
        payload = {
            "image_url": encoded_string, 
            "video_url": ref_video_path,
            "character_orientation": ref_orientation, # "image" or "video"
            "mode": quality_mode,
            "prompt": prompt,
            "model_name": target_model_name 
        }
        print(f"DEBUG: Using Motion Control Endpoint: {url}")
        
    else:
        # STANDARD IMAGE-TO-VIDEO MODE
        payload = {
            "model_name": target_model_name, 
            "image": encoded_string,
            "prompt": prompt,
            "duration": duration_int,
            "mode": quality_mode, # "std" or "pro"
            "cfg_scale": 0.5
        }
        
        if camera_control:
             payload["camera_control"] = camera_control
             print(f"DEBUG: Adding Camera Control: {camera_control}")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    logs = []
    
    try:
        # 1. Submit Task
        response = requests.post(url, json=payload, headers=headers)
        
        try:
             resp_json = response.json()
             logs.append(f"DEBUG: RAW API RESPONSE: {resp_json}")
             print(logs[-1])
        except:
             resp_json = {}
             logs.append(f"DEBUG: RAW API RESPONSE TEXT: {response.text}")
             print(logs[-1])
             
        if response.status_code != 200:
            return {"status": "failed", "error": f"HTTP {response.status_code}: {response.text}", "logs": logs}
            
        # Extract ID (Handle different structures if needed)
        task_id = resp_json.get("task_id") or resp_json.get("data", {}).get("task_id")
        
        if not task_id:
             return {"status": "failed", "error": f"No Task ID returned. Payload: {resp_json}", "logs": logs}
             
        logs.append(f"🎬 Video Task Started: {task_id} (Model: {target_model_name}, Mode: {quality_mode})")
        print(logs[-1])
        
        # 2. Poll for Completion
        # Increased check frequency to 5s for better responsiveness
        logs.append(f"⏳ Polling Kling Task {task_id} for completion...")
        print(logs[-1])
        
        for i in range(240): # 240 * 5s = 20 mins
            time.sleep(5)
            
            # POLL STRATEGY: List recent tasks
            # If using Motion Control, we MUST poll the motion-control list endpoint
            check_url = "https://api.klingai.com/v1/videos/image2video"
            if "motion-control" in url:
                check_url = "https://api.klingai.com/v1/videos/motion-control"

            params = {"page": 1, "page_size": 20} 
            
            try:
                status_resp = requests.get(check_url, headers=headers, params=params)
                if status_resp.status_code != 200:
                     logs.append(f"⚠️ Polling Error: {status_resp.status_code}")
                     continue
                     
                status_data = status_resp.json()
             
                # Extract Tasks: Handle Both Formats
                # Standard: data['data']['tasks'] (List)
                # Motion: data['data'] (List)
                tasks = []
                response_data = status_data.get("data", {})
                
                if isinstance(response_data, list):
                    tasks = response_data
                elif isinstance(response_data, dict):
                    tasks = response_data.get("tasks", [])

                # Find our task definition in the list
                target_task = None
                
                for t in tasks:
                     if t.get("task_id") == task_id:
                          target_task = t
                          break
                
                if not target_task:
                     logs.append(f"⚠️ Task {task_id} not found in recent list. Waiting...")
                     continue
                     
                status_data = target_task
                
            except Exception as e:
                logs.append(f"⚠️ Polling connection error: {e}")
                continue
            
            status = status_data.get("task_status") or status_data.get("status")
            
            if i % 6 == 0: 
                 logs.append(f"   ... [{i+1}/240] Status: {status}")

            if status == "succeed":
                # Check output structure
                video_url = None
                
                # Structure: { "task_result": { "videos": [{ "url": ... }] } }
                if "task_result" in status_data:
                     try: video_url = status_data["task_result"]["videos"][0]["url"]
                     except: pass
                elif "output" in status_data:
                     try: video_url = status_data["output"]["video_url"]
                     except: pass
                
                if not video_url:
                     logs.append(f"⚠️ Status Succeeded but No URL Found. Dump: {status_data}")

                # DOWNLOAD THE VIDEO
                local_video_path = None
                if video_url:
                    logs.append(f"🎥 Found URL: {video_url}")
                    logs.append(f"🎥 Found URL: {video_url}")
                    try:
                        import uuid
                        filename = f"kling_video_{int(time.time())}_{str(uuid.uuid4())[:8]}.mp4"
                        if not os.path.exists(output_folder):
                            os.makedirs(output_folder)
                        local_video_path = os.path.join(output_folder, filename)
                        
                        logs.append(f"⬇️ Downloading video from {video_url}...")
                        print(logs[-1])
                        
                        v_resp = requests.get(video_url, stream=True)
                        if v_resp.status_code == 200:
                            with open(local_video_path, 'wb') as f:
                                for chunk in v_resp.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            logs.append(f"✅ Video saved to: {local_video_path}")
                            print(logs[-1])
                        else:
                            logs.append(f"❌ Failed to download video: {v_resp.status_code}")
                            print(logs[-1])
                            local_video_path = None # Fallback to URL only
                    except Exception as e:
                        logs.append(f"❌ Error downloading video: {e}")
                        print(logs[-1])
                        local_video_path = None

                return {
                    "status": "success", 
                    "video_url": video_url,
                    "video_path": local_video_path, # Return local path
                    "task_id": task_id,
                    "logs": logs
                }
            elif status == "failed":
                return {"status": "failed", "error": status_data.get("task_status_msg") or status_data.get("error"), "logs": logs}
                
        return {"status": "success", "warning": "Polling Timed Out", "task_id": task_id, "logs": logs}

    except Exception as e:
        return {"status": "failed", "error": str(e)}

if __name__ == "__main__":
    import argparse
    import json as _json
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--carousel_id", required=True)
    parser.add_argument("--queue_file", required=True)
    parser.add_argument("--model_version", default="3.0")
    parser.add_argument("--output_folder", default="output")
    args = parser.parse_args()

    queue_path = Path(args.queue_file)

    def _update_queue(updates):
        try:
            q = _json.loads(queue_path.read_text()) if queue_path.exists() else {}
            if args.carousel_id in q:
                q[args.carousel_id].update(updates)
                queue_path.write_text(_json.dumps(q, indent=2))
        except Exception as ex:
            print(f"Queue update error: {ex}")

    result = generate_video_kling(
        image_path=args.image,
        prompt=args.prompt,
        model_version=args.model_version,
        quality_mode="pro",
        output_folder=args.output_folder,
    )

    if result.get("status") == "success" and result.get("video_path"):
        _update_queue({"status": "done", "video_path": result["video_path"]})
        print(f"Done: {result['video_path']}")
    else:
        _update_queue({"status": "failed"})
        print(f"Failed: {result.get('error', result.get('logs', ''))}")


def generate_video_humo(image_path, prompt, audio_path=None, num_frames=49, num_inference_steps=50, guidance_scale=5.0, audio_guidance_scale=5.5, output_folder="output"):
    """
    Generates a video using the HuMo model via Replicate.
    """
    import replicate
    import time
    import requests
    from datetime import datetime
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    logs = []
    
    try:
        if not os.environ.get("REPLICATE_API_TOKEN"):
             return {"status": "failed", "error": "Missing REPLICATE_API_TOKEN", "logs": logs}
             
        # Prepare inputs
        logs.append(f"Debug - Image Input Type: {type(image_path)}, Value: {image_path}")
        
        # Ensure primitive types
        prompt = str(prompt)
        image_path = str(image_path)
        
        input_data = {"prompt": prompt}
        if image_path.startswith(("http://", "https://")):
            input_data["reference_image"] = image_path
        else:
            input_data["reference_image"] = open(image_path, "rb")
            
        input_data["num_frames"] = num_frames
        input_data["num_inference_steps"] = num_inference_steps
        input_data["guidance_scale"] = guidance_scale
        input_data["seed"] = int(time.time())

        
        if audio_path:
            audio_path = str(audio_path)
            if audio_path.startswith(("http://", "https://")):
                 input_data["audio"] = audio_path
                 input_data["audio_guidance_scale"] = audio_guidance_scale
            elif os.path.exists(audio_path):
                 input_data["audio"] = open(audio_path, "rb")
                 input_data["audio_guidance_scale"] = audio_guidance_scale

        logs.append(f"Starting HuMo generation with prompt: {prompt}")
        
        # Create prediction (async) instead of running blockingly
        model = replicate.models.get("zsxkib/humo")
        version = model.versions.get("d9b5555b1e87f11ef46b96834ecc379fabdaff97006b48564fe3d841561ab4ef")
        prediction = replicate.predictions.create(
            version=version,
            input=input_data
        )
        
        logs.append(f"Prediction started. ID: {prediction.id}")
        
        # Polling loop
        max_retries = 100 # Approx 5 mins (3s * 100)
        
        for _ in range(max_retries):
            prediction.reload()
            current_status = prediction.status
            
            if current_status == "succeeded":
                output = prediction.output
                video_url = output
                if isinstance(output, list):
                    video_url = output[0]
                logs.append(f"Generation succeeded! URL: {video_url}")
                break
            elif current_status == "failed":
                return {"status": "failed", "error": f"Replicate task failed: {prediction.error}", "logs": logs}
            elif current_status == "canceled":
                return {"status": "failed", "error": "Replicate task canceled.", "logs": logs}
            else:
                # status is 'starting' or 'processing'
                time.sleep(3)
        
        if prediction.status != "succeeded":
             return {"status": "failed", "error": "Timeout waiting for generation.", "logs": logs}

        # Download video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"humo_{timestamp}.mp4"
        local_path = os.path.join(output_folder, filename)
        
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logs.append(f"Video saved to {local_path}")
            
            return {
                "status": "success",
                "video_path": local_path,
                "video_url": video_url,
                "task_id": prediction.id,
                "logs": logs
            }
        else:
            return {
                "status": "failed",
                "error": f"Failed to download video: {response.status_code}",
                "logs": logs
            }

    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "logs": logs
        }

