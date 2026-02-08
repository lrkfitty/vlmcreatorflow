import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

def parse_script_to_scenes(script_text, cast_list, environment_name, genre="General", tone="Neutral", roles_map=None, wardrobe_map=None, ref_images=None, secondary_environment="None", camera="Auto", lens="Auto", lighting="Auto", film_stock="Auto", filter_look="Auto", movie_style="Auto", transition_style="Auto"):
    """
    Uses Gemini to break down a raw script into structured Scenes.
    Enforces 12-Scene Structure (8 Narrative + 4 B-Roll).
    V3 Update: Added Cinematic Parameters (Camera, Lens, Lighting).
    V3.5 Update: Multimodal Support (Deep Vision).
    V3.6 Update: Added Film Stock and Filter/Look.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return {"error": "Missing GOOGLE_API_KEY"}

    # Format roles for context
    roles_context = ""
    if roles_map or wardrobe_map:
        roles_context = "\n    - Character Profiles:\n"
        all_names = set(list(roles_map.keys()) if roles_map else []) | set(list(wardrobe_map.keys()) if wardrobe_map else [])
        for name in all_names:
            role = roles_map.get(name, "Actor") if roles_map else "Actor"
            outfit = wardrobe_map.get(name, "Standard Outfit") if wardrobe_map else "Standard Outfit"
            roles_context += f"      * {name}: Role={role}, Wardrobe={outfit}\n"

    # CINEMATOGRAPHY CONTEXT
    cam_context = f"""
    CINEMATOGRAPHY SETTINGS (STRICTLY ENFORCE):
    - CAMERA BODY: {camera}
    - LENS PACKAGE: {lens}
    - LIGHTING STYLE: {lighting}
    - FILM STOCK: {film_stock}
    - FILTER/LOOK: {filter_look}
    - MOVIE STYLE REFERENCE: {movie_style}
    - PREFERRED TRANSITION STYLE: {transition_style}
    """

    system_instruction = f"""
    You are a World-Class HOLLYWOOD DIRECTOR and CINEMATOGRAPHER (Netflix/HBO/A24 Standard).
    Your job is to visualize a script into a precise, high-end storyboard for an AI Video Generation pipeline.
    You MUST prioritize VISUAL AESTHETICS above all else. No flat lighting. No generic angles.
    Refer to the 'CINEMATOGRAPHY SETTINGS' below for the specific camera and lens package.
    
    SERIES BIBLE:
    - GENRE: {genre}
    - TONE: {tone}
    - PRIMARY LOCATION: {environment_name}
    - SECONDARY LOCATION (B-ROLL): {secondary_environment}
    
    DYNAMIC ENVIRONMENT SCALING:
    - The PRIMARY LOCATION is the starting point or anchor.
    - HOWEVER, if the SCRIPT explicitly describes a scene moving to a new place (e.g. 'INT. CAR', 'EXT. PARK'), you MUST update the `location` field and the prompt description to match the NEW location.
    - Do NOT force the Primary Location if the story leaves it. Follow the narrative journey.
    
    CAST & ROLES:
    {roles_context}
    
    CRITICAL INSTRUCTION - CHARACTER NAMES:
    - ALWAYS refer to characters by their defined NAME (e.g. "Shay", "Chels").
    - NEVER refer to them by their Role (e.g. "The Love Interest", "The Main Character").
    - The Asset System only recognizes NAMES.
    
    {cam_context}
    
    INSTRUCTIONS:
    1. VISUAL STYLE: You must write prompts that look like high-budget film stills.
       - Use keywords: "Cinematic, Color Graded, Volumetric Lighting, Depth of Field, 8k, Ultra-Detailed".
       - Apply the specific Camera/Lens/Lighting settings provided above to EVERY description.
       - Example: "Wide shot on Arri Alexa with Anamorphic Lens, cinematic moody lighting..."
    
    2. SCENE BREAKDOWN: transform the script into **EXACTLY 12 VISUAL SHOTS**.
       - **Suggested Structure (Adapt if Narrative Requires):**
         * Shots 1-2: Narrative (Establish Character/Action)
         * Shot 3: Organic Transition / Atmosphere (B-Roll OR Reaction Shot)
         * Shots 4-5: Narrative (Deepen Story)
         * Shot 6: Mid-Point Bridge (Detail/Environment or Character Moment)
         * Shots 7-11: Narrative Peak / Resolution
         * Shot 12: B-Roll (Closing Shot / Tone - NO CHARACTERS) OR Final Hero Shot

       - **CRITICAL RULE ON B-ROLL:**
         * Do NOT force B-Roll every 4th shot if it breaks the flow.
         * Only use B-Roll (Environment/Details) if it enhances the pacing or atmosphere.
         * If the scene is dialogue-heavy or emotional, **PRIORITIZE CHARACTER FOCUS**.

    3. VISUAL FIDELITY (CRITICAL - DO NOT FAIL THIS):
       - You have been provided with VISUAL REFERENCE images labeled "Wardrobe".
       - You MUST Use these images as the ABSOLUTE SOURCE OF TRUTH.

       A. **WARDROBE (STRICT - DO NOT HALLUCINATE)**:
       - You DO NOT know what the outfit looks like. Use the LABEL only.
       - **CORRECT**: "Shay wearing the Red Dress"
       - **WRONG**: "Shay wearing a red silk gown with lace trim" (This will conflict with the image).
       - **REASON**: The image generator uses the REFERENCE IMAGE. Your text description of the outfit creates GHOSTING and ARTIFACTS.
       - **EXCEPTION**: You CAN describe how the outfit is being worn (e.g. "dirty", "wet", "torn", "flowing in wind").

       B. **FACES & IDENTITY (STRICT - DO NOT HALLUCINATE)**:
       - You DO NOT know what the character looks like.
       - **CORRECT**: "Shay smiles..."
       - **WRONG**: "Shay, a beautiful blonde woman with blue eyes, smiles..."
       - **REASON**: Describing the face creates a "Generic AI Face" that overrides the specific LoRA/Reference Identity.
       - **VERIFICATION**: Scan your prompt. Did you write "blonde", "brunette", "blue eyes", "pale skin"? DELETE IT immediately. Only describe EMOTIONS and LIGHTING on the face.

    4. B-ROLL RULES:
       - B-Roll shots must NOT focus on main characters. Focus on details, environment, lighting, or objects that set the mood (Tone).
       - Use the 'Secondary/B-Roll Environment'.
    
    5. SHOT LIST: For each Shot, you must define these SPECIFIC, GRANULAR parameters:
       - 'shot_size': E.g. "Extreme Close Up", "Medium Shot", "Wide Shot".
       - 'camera_angle': E.g. "Low Angle", "High Angle", "Dutch Angle", "Eye Level".
       - 'composition': E.g. "Center Framed", "Rule of Thirds", "Symmetrical".
       - 'depth_of_field': E.g. "Shallow depth of field", "Deep focus", "Bokeh".
       - 'lighting_type': E.g. "Rembrandt", "Soft Box", "Neon", "Golden Hour Hard Light".
       - 'time_of_day': E.g. "Morning", "Day", "Golden Hour", "Blue Hour", "Night".
       - 'subject_position': E.g. "Seated at bar", "Walking towards camera".
       - 'action_description': What is happening.
       - 'characters': List of characters present.
       - 'visual_prompt': THE FINAL MASTER PROMPT (Must be 1000+ characters).
         * This is where you earn your Oscar. Do NOT just copy the script action.
         * **SCENE EXPANSION**: If the script says "Shay sits", you write "Shay sits, slumped forward, exhaustion etched into her posture, the harsh neon light casting deep shadows under her eyes."
         * **ENVIRONMENTAL TEXTURE**: Describe the dust motes, the condensation on glass, the crack in the wall, the specific way light hits the fabric.
         * **MICRO-EXPRESSIONS**: Describe the subtle twitch of a lip, the glaze in the eyes, the tension in the jaw.
         * **LIGHTING SPECIFICITY**: Use terms like "Chiaroscuro", "Rim Light", "Volumetric God Rays", "Practical Source", "Specular Highlights".
         * Structure: "[Shot Size], [Camera Angle]. [Subject Position], [Action Description + Micro-Expression]. [Time of Day], [Lighting Type + Specular Details], [Depth of Field]. [Camera/Lens Specs for Texture]. Ultra-detailed, 8k film still, raw photography. [Detailed Background Texture]. [Detailed Outfit interaction with environment]. [Atmosphere/Vibe]."
    
    OUTPUT FORMAT:
    Return ONLY valid JSON.
    {{
      "title": "Episode Title",
      "scenes": [
        {{
          "id": 1,
          "location": "...",
          "shots": [
            {{
               "shot_size": "...",
               "camera_angle": "...",
               "composition": "...",
               "depth_of_field": "...",
               "lighting_type": "...",
               "time_of_day": "...",
               "subject_position": "...",
               "action_description": "...",
               "characters": ["Name1"],
               "visual_prompt": "..."
            }}
          ]
        }}
      ]
    }}
    """

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = { "Content-Type": "application/json" }
    
    # BUILD MULTIMODAL PAYLOAD
    parts = []
    
    # 1. System Instruction
    parts.append({ "text": system_instruction })
    
    # 2. Reference Images (PARALLELIZED)
    if ref_images:
        import base64
        import concurrent.futures
        import time

        def load_single_ref(img_data):
            path = img_data.get('path')
            label = img_data.get('label', 'Image')
            t_start = time.time()
            
            result_parts = []
            
            try:
                # Case A: URL
                if path and path.startswith("http"):
                    resp = requests.get(path, timeout=10)
                    if resp.status_code == 200:
                        b64 = base64.b64encode(resp.content).decode('utf-8')
                        result_parts.append({ "text": f"VISUAL REFERENCE - {label}:" })
                        result_parts.append({ "inline_data": { "mime_type": "image/jpeg", "data": b64 } })
                        print(f"   ⚡ Downloaded {label} in {time.time() - t_start:.2f}s")
                    else:
                        print(f"   ⚠️ Failed to download {label}: Status {resp.status_code}")

                # Case B: Local File
                elif path and os.path.exists(path):
                    with open(path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode('utf-8')
                        result_parts.append({ "text": f"VISUAL REFERENCE - {label}:" })
                        result_parts.append({ "inline_data": { "mime_type": "image/jpeg", "data": b64 } })
                        print(f"   ⚡ Loaded {label} (Local) in {time.time() - t_start:.2f}s")
            except Exception as e:
                print(f"   ❌ Error loading {label}: {e}")
                
            return result_parts

        print(f"⚡ Director AI: fetching {len(ref_images)} assets in parallel...")
        t_batch_start = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # maintain order? Order matters less here as distinct prompt parts, but nice to keep.
            results = list(executor.map(load_single_ref, ref_images))
            
        for res in results:
            parts.extend(res)
            
        print(f"⚡ Director AI assets ready in {time.time() - t_batch_start:.2f}s")

    # 3. Script
    parts.append({ "text": "\n\nSCRIPT:\n" + script_text })

    payload = {
        "contents": [{
            "parts": parts
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        # Timeout increased to 120s for Director AI Stability
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        res_json = response.json()
        
        # Extract text
        if 'candidates' not in res_json:
            error_msg = f"Gemini Refusal: {res_json.get('promptFeedback', res_json)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
            
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        
        # Clean markdown
        text = text.replace('```json', '').replace('```', '').strip()
        
        # Parse
        data = json.loads(text)
        return data

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    # Local Test
    sample_script = "Tylarkin walks into the Neon Bar. He sees Shay sitting at a booth. He waves."
    cast = ["Tylarkin", "Shay"]
    env = "Neon Bar"
    print(json.dumps(parse_script_to_scenes(sample_script, cast, env), indent=2))
