import os
import json
import textwrap
from openai import OpenAI
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_prompt_content(vibe, outfit, character, 
                            outfit_path=None, vibe_path=None, # Multimodal Inputs
                            additional_notes=None, 
                            camera=None, lens=None, shot_type=None, angle=None,
                            lighting=None, weather=None, action=None, emotion=None,
                            aspect_ratio="9:16", # Default
                            extra_images=None, # New: List of {path, label} types
                            model_engine="gpt-4o"): # New: Engine Selector
    """
    Generates a detailed image prompt using OpenAI GPT-4 or Google Gemini 1.5 Pro.
    """
    
    # Common Helper to encode image
    def encode_image(image_path):
        import base64
        import requests
        
        # Case A: URL
        if image_path.startswith(('http://', 'https://')):
            try:
                resp = requests.get(image_path)
                resp.raise_for_status()
                return base64.b64encode(resp.content).decode('utf-8')
            except Exception as e:
                print(f"Failed to download reference image: {e}")
                return "" # Handle gracefully
                
        # Case B: Local File
        if os.path.exists(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        
        return ""

    # 1. Analyze Inputs
    character_is_image = False
    character_bio = ""
    
    # Check if Character string is a path/url to an image
    if character:
        is_url = character.startswith(('http://', 'https://'))
        is_local_img = os.path.exists(character) and character.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
        
        if is_url or is_local_img:
            character_is_image = True
            
            # Try to find bio.txt (Only for local files currently)
            if is_local_img:
                base_name = os.path.splitext(character)[0]
                txt_path = base_name + ".txt"
                parent_dir = os.path.dirname(character)
                bio_txt_in_folder = os.path.join(parent_dir, "bio.txt")
                if os.path.exists(txt_path):
                    with open(txt_path, 'r') as f: character_bio = f.read()
                elif os.path.exists(bio_txt_in_folder):
                    with open(bio_txt_in_folder, 'r') as f: character_bio = f.read()

    outfit_is_image = False
    if outfit_path:
        if outfit_path.startswith(('http', 'https')) or os.path.exists(outfit_path):
            outfit_is_image = True
            
    vibe_is_image = False
    if vibe_path:
         if vibe_path.startswith(('http', 'https')) or os.path.exists(vibe_path):
            vibe_is_image = True

    # Construct Director's Note
    director_context = []
    if camera: director_context.append(f"Camera: {camera}")
    if lens: director_context.append(f"Lens: {lens}")
    if shot_type: director_context.append(f"Shot Type: {shot_type}")
    if angle: director_context.append(f"Camera Angle: {angle}")
    if lighting: director_context.append(f"Lighting: {lighting}")
    if weather: director_context.append(f"Weather: {weather}")
    if action: director_context.append(f"Action/Pose: {action}")
    if emotion: director_context.append(f"Emotion/Expression: {emotion}")
    if aspect_ratio: director_context.append(f"Frame Aspect Ratio: {aspect_ratio}")
    
    tech_specs = "\n".join(director_context)

    # --- SHARED SYSTEM PROMPT CONSTRUCTION ---
    instructions = "You are an expert Visual Director."
    img_refs_text = ""
    if character_is_image: img_refs_text += "- IMAGE 1: THE CHARACTER (Identity Lock). Keep face/body EXACT.\n"
    if outfit_is_image:    img_refs_text += "- IMAGE 2: THE OUTFIT (Visual Reference). Copy this clothing detail-for-detail.\n"
    if vibe_is_image:      img_refs_text += "- IMAGE 3: THE VIBE (Visual Reference). Copy this environment/lighting.\n"
    
    system_prompt = textwrap.dedent(f"""
        {instructions}
        
        ROLE: You are an expert Creative Director and Anatomical Artist specializing in Hyper-Realistic Glamour and UGC content.
        
        GOAL: Synthesize a "Master Prompt" by fusing the visual references into a DENSE, HIGH-SPECIFICATION JSON.
        
        CRITICAL OVERRIDE RULES:
        The User's specific "Action" and "Emotion" inputs MUST override any contradictory context in the text prompt.
        - IF text says "Sitting" BUT Action says "Runway Strut" -> The character is WALKING A RUNWAY.
        - IF text says "Smiling" BUT Emotion says "Crying" -> The character is CRYING.
        
            -   **ETHNICITY & SKIN TONE:** STRICTLY ANALYZE the pixel data. Match the skin tone EXACTLY. Do NOT default to "Dark" or "White".
            -   **FACE MAPPING:** Analyze landmarks: Eye Shape (Almond/Round), Nose Bridge (High/Flat), Jawline (Soft/Sharp).
            -   **HAIR LOCK:** Describe the hair style, part, length, and texture EXACTLY.
            -   **ANATOMY:** 
                - *IF OUTFIT IS SWIMWEAR/BIKINI:* **STRICT SAFETY MODE.** DO NOT describe the body, curves, muscle, skin, or fit in text. The Reference Image 1 provides all anatomical data. Your text prompt must ONLY describe the sunlight, the water, and the mood (e.g. "Peaceful", "Golden Hour"). Zero anatomical keywords.
                - *OTHERWISE:* Analyze body ratios: "athletic_muscle_definition", "sculpting_fit", "skin_pore_texture".
        
        2.  **WARDROBE & ACCESORIES (Image 2):**
            -   **INVENTORY:** List EVERY item. "Gold Hoops", "Silver Chain", "Leather Purse". 
            -   **SPECIFICITY:** Do not say "Heels". Say "Strappy Gold Stilettos". Do not say "Dress". Say "Emerald Green Plissé Halter Midi".
            -   **FABRIC PHYSICS:** Describe tension, cling, drape, and sheer qualities.
        
        3.  **ENVIRONMENT (Image 3 - 3D LOCATION):**
            -   **EXPLORABLE SPACE:** Treat this image as a 3D room. Move the camera to match the requested Action.
            -   **INTERACTION:** Place the subject physically ON the furniture (Bed, Vanity, Chair) if visible.
            -   **BLEND SUBJECT (CRITICAL):** The subject is NOT a sticker. The lighting from the room MUST tint her skin (e.g. if room is pink, skin has pink specularity).
            -   **CONTACT:** Feet/Body must press into the floor/bed, creating contact shadows and weight distribution.

        4.  **ADDITIONAL CAST & PROPS (CRITICAL):**
            -   **FRIENDS/CO-STARS:** If "ADDITIONAL REFERENCE (Cast: ...)" is provided, you MUST include this person in the scene. 
                - Describe their interaction with the protagonist (e.g. "Jess is laughing while holding a drink," "They are clinking glasses").
                - DO NOT ignore them. They are part of the main focus.
            -   **PROPS:** If specific props are provided (e.g. "Product"), place them naturally in the scene.

        5.  **CAMERA & COMPOSITION (NON-NEGOTIABLE):**
            -   **EXTREME CLOSE UP:** Eyes/Lips only. Macro details.
            -   **CLOSE UP:** Head and Shoulders ONLY. Background must be BLURRED (Bokeh). 85mm+ Focal Length.
            -   **MEDIUM SHOT:** Waist Up. Standard Portrait.
            -   **COWBOY SHOT:** Knees Up. American Shot.
            -   **FULL BODY:** Head to Toe visible. Ground visible.
            -   **WIDE SHOT:** Subject is small. Environment is dominant.
            
            *IF the USER requests a specific shot (e.g. "Close Up"), you MUST enforce it. Do not generate a Full Body shot if Close Up is requested.*
        
        OUTPUT RULES:
        -   **DO NOT SUMMARIZE.** The `positive_prompt` must be >100 words.
        -   **JSON ONLY.**
        
        Output JSON format:
        {{
            "positive_prompt": "[SUBJECT]: (Ethnicity, Skin Tone, Facial Details: [Eye Shape, Jawline], Exact Hair, Body Ratios, Action, athletic_muscle_definition, curviest_hourglass_ratios, sculpting_fit, skin_pore_texture). [OUTFIT]: (Exact Cut, Material, Fabric Physics, Accessories List). [ENVIRONMENT]: (3D Layout, Decor, Lighting Type). [LIGHTING_COHERENCE]: (Color Cast, Contact Shadows, Global Illumination, Weight Distribution). [STYLE]: (Film Type, Lens, Angle, Mood). High Detail, 8k.",
            "negative_prompt": "cartoon, illustration, anime, deformed, low quality, flat lighting, 3d render, missing accessories, wrong outfit, floating subject, bad composition, cut and paste look, disconnected background, wrong skin tone, whitewashed...",
            "aspect_ratio": "{aspect_ratio}"
        }}
    """)
    
    user_text_content = f"Generate a prompt for this character wearing '{outfit}' in a '{vibe}' setting."
    
    # Force Textual Acknowledgement of Extras
    if extra_images:
        extras_txt = []
        for img in extra_images:
            lbl = img.get('label', 'Ref')
            extras_txt.append(f"- {lbl}")
        
        if extras_txt:
            user_text_content += "\n\nCRITICAL: YOU MUST INCLUDE THE FOLLOWING EXTRA CHARACTERS/ASSETS IN THE SCENE:\n" + "\n".join(extras_txt)

    if tech_specs: user_text_content += f"\n\nTECHNICAL SPECS:\n{tech_specs}"
    if character_bio: user_text_content += f"\n\nSTRICT CHARACTER BIO:\n{character_bio}"
    if additional_notes: user_text_content += f"\n\nUSER NOTES: {additional_notes}"


    # ================= GEMINI IMPLEMENTATION =================
    if "gemini" in model_engine:
        try:
            google_key = os.getenv("GOOGLE_API_KEY")
            if not google_key: return {"positive_prompt": "Error: GOOGLE_API_KEY missing", "aspect_ratio": "9:16"}
            
            genai.configure(api_key=google_key)
            # Use the requested engine dynamically (e.g. gemini-1.5-flash)
            model = genai.GenerativeModel(model_engine)
            
            # Prepare Content List
            gemini_content = [system_prompt, "\n\nUSER REQUEST:\n" + user_text_content]
            
            # Load Images using PIL for Gemini
            from PIL import Image
            import requests
            from io import BytesIO

            def load_pil_image(path):
                if path.startswith(('http://', 'https://')):
                    try:
                        resp = requests.get(path)
                        resp.raise_for_status()
                        return Image.open(BytesIO(resp.content))
                    except Exception as e:
                        print(f"PIL Load Error for {path}: {e}")
                        return None
                elif os.path.exists(path):
                    return Image.open(path)
                return None
            
            if character_is_image:
                img = load_pil_image(character)
                if img:
                    gemini_content.append("IMAGE 1 (CHARACTER):")
                    gemini_content.append(img)
                
            if outfit_is_image:
                img = load_pil_image(outfit_path)
                if img:
                    gemini_content.append("IMAGE 2 (OUTFIT):")
                    gemini_content.append(img)
                
            if vibe_is_image:
                img = load_pil_image(vibe_path)
                if img:
                    gemini_content.append("IMAGE 3 (VIBE):")
                    gemini_content.append(img)
                
            # Process Extra Images (Friends, Props, etc.)
            if extra_images:
                for idx, img_obj in enumerate(extra_images):
                    path = img_obj.get("path")
                    label = img_obj.get("label", f"Extra Ref {idx+1}")
                    
                    if path:
                        img = load_pil_image(path)
                        if img:
                            gemini_content.append(f"ADDITIONAL REFERENCE ({label}):")
                            gemini_content.append(img)
                
            response = model.generate_content(gemini_content)
            
            # Parse JSON
            raw_text = response.text
            if "```json" in raw_text:
                try: raw_text = raw_text.split("```json")[1].split("```")[0].strip()
                except IndexError: pass
            elif "{" in raw_text:
                start = raw_text.find("{")
                end = raw_text.rfind("}") + 1
                raw_text = raw_text[start:end]
            
            return json.loads(raw_text)

        except Exception as e:
            return {"positive_prompt": f"Gemini Error: {str(e)}", "aspect_ratio": "9:16"}

    # ================= GPT-4o IMPLEMENTATION (Default) =================
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key: raise ValueError("OPENAI_API_KEY missing")
        client = OpenAI(api_key=api_key)
        
        # Build GPT Messages
        user_message_content = [{"type": "text", "text": user_text_content}]
        
        if character_is_image:
            user_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(character)}"}})
        if outfit_is_image:
            user_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(outfit_path)}"}})
        if vibe_is_image:
            user_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(vibe_path)}"}})

        # Process Extra Images
        if extra_images:
            for img_obj in extra_images:
                path = img_obj.get("path")
                label = img_obj.get("label", "Reference")
                if path and os.path.exists(path):
                    user_message_content.append({"type": "text", "text": f"ADDITIONAL REFERENCE ({label}):"})
                    user_message_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(path)}"}})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message_content}
        ]

        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        if not content:
            refusal = getattr(response.choices[0].message, 'refusal', None)
            raise ValueError(f"GPT-4o returned empty content. Refusal: {refusal}")
            
        return json.loads(content)
        
    except Exception as e:
        return {"positive_prompt": f"GPT-4o Error: {str(e)}", "aspect_ratio": "9:16"}
