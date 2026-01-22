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
    
    # 1. Dispatch (Strictly Cloud)
    # Default to Nano Banana Pro
    return generate_image_nano(prompt_data, output_folder, reference_image_path, outfit_path, vibe_path)

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
        # Use known stable version
        model_name = 'gemini-1.5-pro'
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        headers = { "Content-Type": "application/json" }

        # Helper to attach image or text context to payload
        def add_image_part(img_path, label):
            import base64
            
            b64_data = None
            mime_type = "image/jpeg"
            
            # Helper to resize and encode
            def process_and_encode(img_bytes, mime_type):
                from PIL import Image
                from io import BytesIO
                
                try:
                    img = Image.open(BytesIO(img_bytes))
                    
                    # Resize if too large (Max 1536px long edge)
                    max_dim = 1536
                    if max(img.width, img.height) > max_dim:
                        img.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                        logs.append(f"multimodal: Resized {label} to {img.width}x{img.height}")
                        
                    # Convert to RGB (Strip Alpha) for JPEG optimization
                    if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
                    
                    # Save to Buffer as JPEG 85%
                    buffer = BytesIO()
                    img.save(buffer, format="JPEG", quality=85)
                    return base64.b64encode(buffer.getvalue()).decode('utf-8'), "image/jpeg"
                    
                except Exception as e:
                    logs.append(f"⚠️ Resize Warning for {label}: {e}. Using raw bytes.")
                    return base64.b64encode(img_bytes).decode('utf-8'), mime_type

            # Case A: URL
            if img_path and img_path.startswith(('http://', 'https://')):
                try:
                    resp = requests.get(img_path, timeout=10)
                    resp.raise_for_status()
                    b64_data, mime_type = process_and_encode(resp.content, "image/jpeg") 
                    logs.append(f"multimodal: Downloaded {label} from URL")
                except Exception as e:
                    logs.append(f"⚠️ Failed to downoad {label}: {e}")
            
            # Case B: Local File
            elif img_path and os.path.exists(img_path) and img_path.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                with open(img_path, "rb") as image_file:
                    raw_bytes = image_file.read()
                    b64_data, mime_type = process_and_encode(raw_bytes, "image/jpeg")
                logs.append(f"multimodal: Included {label} reference (Local)")

            # Add to Payload if we have data
            if b64_data:
                # FIX: STRONG BINDING - Explicitly tag the image for the model
                parts.append({
                    "text": f"\n[VISUAL ID: {label}]\n"
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

            # Case D: Failure / Skip
            elif not b64_data:
                 logs.append(f"⚠️ SKIPPED ASSET: {label}. Path/URL invalid or inaccessible: '{img_path}'")

        # 1. Initialize Parts
        parts = []

        # 2. Add Reference Images (VISUAL CONTEXT FIRST)
        # Check for new 'assets' list (World Builder) or fallback to legacy args
        if prompt_data.get("assets"):
             for asset in prompt_data["assets"]:
                 add_image_part(asset.get("path"), asset.get("label", "Context"))
        else:
             # Legacy Wizard Flow
             add_image_part(reference_image_path, "Character")
             add_image_part(outfit_path, "Outfit")
             add_image_part(vibe_path, "Vibe")
        
        # 3. Add Master Instruction with Prompt (COMMAND LAST)
        instruction = f"""
        Generate a {aspect_ratio} aspect ratio image.
        
        --------------------------------------------------
        ⚠️ PROTOCOL: STYLE REPLACEMENT MODE
        --------------------------------------------------
        
        INPUTS:
        1. REFERENCE IMAGES = "CASTING PHOTOS" (Raw, Unstyled, Identity Source)
        2. TEXT PROMPT = "DIRECTOR'S SHOT LIST" (Lighting, Camera, Mood, Action)
        
        INSTRUCTION:
        You are a Cinematographer. Your job is to take the ACTOR from the "Casting Photo" and COSTUME from the "Outfit" reference, and place them on a NEW FILM SET described in the "Director's Shot List".
        
        RULES:
        1. **IDENTITY MAPPING**: Match `[VISUAL ID: Cast: NAME]` to the character in the text prompt.
        2. **WARDROBE MAPPING**: Match `[VISUAL ID: Outfit for NAME: ...]` *strictly* to that specific character.
           - DO NOT PUT Character A's outfit on Character B.
           - If a character has a specific outfit ID, ignore general text descriptions of their clothes. The IMAGE is the authority.
        3. **NO BLEEDING**: Keep visual assets segregated. Character A gets Image A. Character B gets Image B.
        4. **CINEMATIC STYLE**: Discard the "Selfie" or "Catalog" style of the reference images. Apply the lighting/camera from the prompt.
        
        EXAMPLE:
        - Input: `[VISUAL ID: Cast: Shay]`, `[VISUAL ID: Cast: Bob]`, `[VISUAL ID: Outfit for Shay: Yellow]`, `[VISUAL ID: Outfit for Bob: Black]`
        - Prompt: "Shay and Bob talking."
        - Output: Shay (Face A) wearing Yellow (Outfit A). Bob (Face B) wearing Black (Outfit B).
        
        ---------------------
        **DIRECTOR'S SHOT LIST (EXECUTE THIS):**
        {positive_prompt}
        ---------------------
        """
        parts.append({ "text": instruction })
        
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
                         logs.append(f"❌ RAW RESPONSE: {json.dumps(result, indent=2)}")
                         raise Exception("No Content Candidates Returned. See Logs for Raw Response.")
                         
                    finish_reason = candidates[0].get("finishReason", "UNKNOWN")
                    
                    # SAFETY CHECK
                    if finish_reason == "SAFETY":
                        if attempt < max_retries:
                            safety_ratings = candidates[0].get("safetyRatings", [])
                            logs.append(f"⚠️ Blocked by Safety Filters (Attempt {attempt+1}/{max_retries}). Ratings: {json.dumps(safety_ratings)}")
                            time.sleep(retry_delay)
                            retry_delay = min(retry_delay * 1.5, 10)
                            continue
                        else:
                            safety_ratings = candidates[0].get("safetyRatings", [])
                            logs.append(f"❌ FINAL BLOCK. Safety Ratings: {json.dumps(safety_ratings)}")
                            raise Exception(f"Blocked by Safety Filters. Ratings: {safety_ratings}")
                    
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

