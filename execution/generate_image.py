import os
import time
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_image_from_prompt(prompt_data, output_folder="output", reference_image_path=None, outfit_path=None, vibe_path=None):
    """
    Main Entry Point. Dispatches to the correct model engine.
    Returns: dict {"status": "success"|"failed", "image_path": str|None, "logs": str}
    """
    
    # 1. Dispatch
    target_model = prompt_data.get("model_type", "nano") 
    
    if target_model == "sd_local":
        return generate_image_sd_local(
            prompt_data, 
            output_folder, 
            reference_image_path, 
            checkpoint_name=prompt_data.get("checkpoint")
        )
    else:
        # Default to Nano Banana Pro
        return generate_image_nano(prompt_data, output_folder, reference_image_path, outfit_path, vibe_path)

def generate_image_sd_local(prompt_data, output_folder, reference_image_path=None, checkpoint_name=None):
    """
    Connects to Automatic1111 Local API.
    Supports both txt2img and img2img.
    """
    logs = ["--- Attempting Local Stable Diffusion ---"]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 1. Map Aspect Ratio to Resolution
    ar_map = {
        "9:16": (512, 768),   # Reduced slightly for speed/compatibility
        "16:9": (768, 512),
        "1:1":  (512, 512),
        "4:5":  (512, 640)
    }
    ar_str = prompt_data.get("aspect_ratio", "9:16")
    width, height = ar_map.get(ar_str, (512, 768))
    
    # 2. Config Common Payload
    payload = {
        "prompt": prompt_data.get("positive_prompt", ""),
        "negative_prompt": prompt_data.get("negative_prompt", ""),
        "steps": 30,
        "sampler_name": "Euler a",
        "width": width,
        "height": height,
        "cfg_scale": 9, 
        "restore_faces": True,
        "override_settings": {
            "sd_model_checkpoint": checkpoint_name if checkpoint_name else "Realistic_Vision_V6.0_NV_B1_fp16.safetensors"
        }
    }

    # 3. Mode Switch: Text vs Image
    if reference_image_path and os.path.exists(reference_image_path):
        # --- IMG2IMG MODE ---
        url = "http://127.0.0.1:7860/sdapi/v1/img2img"
        logs.append(f"📸 Image Input Detected: {os.path.basename(reference_image_path)}")
        logs.append("⚡ Switching to img2img mode")
        
        # Encode Image
        import base64
        with open(reference_image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
        payload["init_images"] = [encoded_string]
        
        # Likeness Logic: 1.0 = Strict, 0.0 = Creative
        likeness = prompt_data.get("likeness_strength", 0.60)
        denoising = max(0.1, min(1.0 - likeness, 0.9))
        payload["denoising_strength"] = denoising
        logs.append(f"🎚️ Likeness: {likeness} -> Denoising: {denoising:.2f}")
    else:
        # --- TXT2IMG MODE ---
        url = "http://127.0.0.1:7860/sdapi/v1/txt2img"
        logs.append("📝 Text-to-Image Mode (No reference image provided)")

    try:
        # Increased timeout for Mac M1/M2 cold starts
        response = requests.post(url, json=payload, timeout=600) 
        if response.status_code != 200:
            raise Exception(f"SD API Error {response.status_code}: {response.text}")
            
        r = response.json()
        
        # SD returns base64 images
        if "images" in r:
            import base64
            image_data = base64.b64decode(r["images"][0])
            
            timestamp = int(time.time())
            filename = f"gen_sd_local_{timestamp}.png"
            filepath = os.path.join(output_folder, filename)
            
            with open(filepath, "wb") as f:
                f.write(image_data)
                
            return {
                "status": "success",
                "image_path": filepath,
                "model_used": "stable-diffusion-local",
                "logs": "\n".join(logs)
            }

        else:
             raise Exception("No images returned in SD response.")
             
    except Exception as e:
        logs.append(f"❌ Local SD Failed: {e}")
        logs.append("Tip: Ensure './webui.sh --api' is running in terminal.")
        return {
            "status": "failed",
            "image_path": None,
            "model_used": "stable-diffusion-local",
            "logs": "\n".join(logs)
        }

def generate_image_nano(prompt_data, output_folder, reference_image_path, outfit_path, vibe_path):
    """
    Generates using Google Nano Banana Pro (Gemini).
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    logs = ["--- Attempting Generation with Nano Banana Pro ---"]
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    positive_prompt = prompt_data.get("positive_prompt", "")
    aspect_ratio = prompt_data.get("aspect_ratio", "9:16")

    try:
        # Switching to explicit Image Generation model from list (Nano/1.5 aliases are unstable)
        model_name = 'gemini-3-pro-image-preview'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = { "Content-Type": "application/json" }

        # Construct Payload
        parts = []
        
        # 1. Add Text Prompt with Explicit Aspect Ratio and Likeness Instruction
        # 1. Add Text Prompt with Explicit Aspect Ratio and Likeness Instruction
        # We inject it at the start to ensure adherence
        instruction = f"""
        Generate a {aspect_ratio} aspect ratio image.
        
        CRITICAL REFERENCE RULES:
        1. **IDENTITY LOCK (HIGHEST PRIORITY):** You will be provided with a reference image labeled "Main Character" (and optionally "Cast"). You MUST generate these EXACT people. Copy their facial features, bone structure, skin tone, and hair style 1:1.
        2. **OUTFIT SWAP RULE:** If an image is labeled "Outfit", you must DRESS the character in that specific outfit. IGNORE the clothes the character is wearing in their "Identity" reference photo. The "Outfit" image takes 100% precedence for clothing.
        3. **RELATIONS:** If "Cast" or "Friend" images are provided, include them in the scene interacting with the Main Character. Apply the same Identity Lock and Outfit Swap rules to them.
        
        STYLE GUIDE:
        - 8k Resolution, RAW Photo, Ultra-Realistic.
        - TEXTURES: Skin pores, individual hair strands, iris details, fabric threads must be visible. 
        - LIGHTING: Ray-traced lighting, soft shadows, subsurface scattering on skin.
        - NO: Cartoonish, smooth, plastic, blur, or oversaturated looks.
        
        PROMPT SCENE DESCRIPTION: 
        {positive_prompt}
        """
        parts.append({ "text": instruction })
        
        # Helper to attach image or text context to payload
        def add_image_part(img_path, label):
            import base64
            
            b64_data = None
            mime_type = "image/jpeg"
            
            # Case A: URL
            if img_path and img_path.startswith(('http://', 'https://')):
                try:
                    resp = requests.get(img_path)
                    resp.raise_for_status()
                    b64_data = base64.b64encode(resp.content).decode('utf-8')
                    if img_path.lower().endswith(".png"): mime_type = "image/png"
                    elif img_path.lower().endswith(".webp"): mime_type = "image/webp"
                    logs.append(f"multimodal: Downloaded {label} from URL")
                except Exception as e:
                    logs.append(f"⚠️ Failed to downoad {label}: {e}")
            
            # Case B: Local File
            elif img_path and os.path.exists(img_path) and img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                with open(img_path, "rb") as image_file:
                    b64_data = base64.b64encode(image_file.read()).decode('utf-8')
                    if img_path.lower().endswith(".png"): mime_type = "image/png"
                    elif img_path.lower().endswith(".webp"): mime_type = "image/webp"
                logs.append(f"multimodal: Included {label} reference (Local)")

            # Add to Payload if we have data
            if b64_data:
                # INJECT LABEL AS TEXT CONTEXT BEFORE IMAGE
                parts.append({
                    "text": f"Reference Image for: {label}"
                })
                    
                parts.append({
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64_data
                    }
                })
            
            # Case C: Text-only Context (e.g. Outfit description without image)
            elif not b64_data and label and "Outfit for" in label:
                 parts.append({
                     "text": f"IMPORTANT VISUAL CONTEXT: {label}"
                 })
                 logs.append(f"multimodal: Included text context: {label}")

        # 2. Add Reference Images
        # Check for new 'assets' list (World Builder) or fallback to legacy args
        if prompt_data.get("assets"):
             for asset in prompt_data["assets"]:
                 add_image_part(asset.get("path"), asset.get("label", "Context"))
        else:
             # Legacy Wizard Flow
             add_image_part(reference_image_path, "Character")
             add_image_part(outfit_path, "Outfit")
             add_image_part(vibe_path, "Vibe")
        
        # Log the full prompt for debugging
        logs.append(f"Prompt sent to Nano: 'Generate a {aspect_ratio} aspect ratio image of: {positive_prompt}'")
        
        # NOTE: WE ARE USING RAW BLOCK_NONE SETTINGS (User Request)
        payload = {
            "contents": [{
                "parts": parts
            }],
            "generationConfig": {
                "temperature": 0.9,
            },
            "safetySettings": [
                { "category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE" },
                { "category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE" }
            ]
        }
        
        # logs.append(f"Sending request to: {url}")
        
        max_retries = 4 
        retry_delay = 2 # Start with 2s, double it
        
        for attempt in range(max_retries + 1):
            try:
                # Increased timeout to 120s for heavy multimodal payloads (5+ images)
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                
                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get("candidates", [])
                    
                    if not candidates:
                         raise Exception("No Content Candidates Returned.")
                         
                    finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                    
                    # SAFETY CHECK
                    if finish_reason == "SAFETY":
                        if attempt < max_retries:
                            safety_ratings = candidates[0].get("safetyRatings", [])
                            logs.append(f"⚠️ Blocked by Safety Filters (Attempt {attempt+1}/{max_retries}). Retrying in {retry_delay}s...")
                            time.sleep(retry_delay)
                            retry_delay = min(retry_delay * 1.5, 10)
                            continue
                        else:
                            safety_ratings = candidates[0].get("safetyRatings", [])
                            raise Exception(f"Blocked by Safety Filters after {max_retries} retries. Ratings: {safety_ratings}")
                    
                    # SUCCESS - EXTRACT AND RETURN
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    
                    if not parts:
                         raise Exception(f"Model returned no content parts. Finish Reason: {finish_reason}")

                    for part in parts:
                        # Case A: Inline Image Data
                        if "inlineData" in part:
                            import base64
                            mime_type = part["inlineData"]["mimeType"]
                            data = part["inlineData"]["data"]
                            
                            image_bytes = base64.b64decode(data)
                            timestamp = int(time.time())
                            import uuid
                            ext = ".jpg" if "jpeg" in mime_type else ".png"
                            filename = f"gen_nano_{timestamp}_{str(uuid.uuid4())[:8]}{ext}"
                            filepath = os.path.join(output_folder, filename)
                            
                            with open(filepath, "wb") as f:
                                f.write(image_bytes)
                                
                            return {
                                "status": "success",
                                "image_path": filepath,
                                "model_used": "nano-banana-pro",
                                "logs": "\n".join(logs)
                            }

                        # Case B: Text (Warning)
                        if "text" in part:
                            text_content = part["text"]
                            snippet = text_content[:100].replace('\n', ' ')
                            logs.append(f"Nano Response Text: '{snippet}...'")
                    
                    # If loop finishes without returning image
                    logs.append("Warning: Model returned response but no inlineData found.")
                    raise Exception("Model returned valid response but no image data.")

                elif response.status_code == 503:
                    if attempt < max_retries:
                        logs.append(f"⚠️ Model Overloaded (503). Retrying in {retry_delay}s... ({attempt+1}/{max_retries})")
                        time.sleep(retry_delay)
                        retry_delay *= 2
                        continue
                    else:
                        raise Exception(f"Model Overloaded (503) after {max_retries} retries.")
                elif response.status_code == 429:
                     raise Exception("Quota Exceeded (429). You are on the free tier or hit a rate limit.")
                else:
                     raise Exception(f"API Error {response.status_code}: {response.text}")

            except requests.exceptions.RequestException as e:
                # Handle network glitches specifically during retry
                if attempt < max_retries:
                    logs.append(f"⚠️ Network error: {e}. Retrying...")
                    time.sleep(retry_delay)
                    continue
                raise e
        
        else:
             # No candidates returned
             raise Exception("No Content Candidates Returned. Likely Safety Filter or API Glitch.")
            
    except Exception as e:
        logs.append(f"❌ Nano Model Failed: {e}")
        return {
            "status": "failed",
            "image_path": None,
            "model_used": "nano-banana-pro",
            "logs": "\n".join(logs)
        }
    
    # Critical Failsafe
    return {
        "status": "failed",
        "image_path": None,
        "model_used": "nano-banana-pro",
        "logs": "CRITICAL ERROR: Function exited without return. Logic Fallthrough."
    }

# DALL-E Fallback (Unused but preserved if needed later)
def generate_image_dalle(prompt_data, output_folder):
    pass

