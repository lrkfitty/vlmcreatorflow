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
    You are a World-Class HOLLYWOOD DIRECTOR and CINEMATOGRAPHER (Netflix/HBO Standard).
    Your job is to visualize a script into a precise, high-end storyboard for an AI Video Generation pipeline.
    
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

       A. **WARDROBE (STRICT)**:
       - Do NOT describe the outfit's visual details (no colors, materials, patterns).
       - SIMPLY USE THE OUTFIT NAME provided in the "Character Profiles".
       - Example: If Wardrobe="Red Dress", write: "Shay wearing the Red Dress".
       - Do NOT write: "Shay wearing a crimson silk gown with spaghetti straps."
       - REASON: The Image Generator has the photo. Text descriptions fight with the photo.

       B. **FACES (STRICT)**:
       - Do NOT describe hair color, eye color, skin tone, or facial structure.
       - **BAD:** "Shay, a blonde woman with blue eyes..." (Confuses the model if asset differs).
       - **GOOD:** "Shay, wearing the Red Outfit, smiles..." (Forces model to look at the Asset for face).
       
       - **VERIFICATION**: Before outputting a description, ask yourself: "Am I describing a physical trait or outfit detail?" If yes, DELETE IT. Only describe Actions, Lighting, and Environment.

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
       - 'visual_prompt': THE FINAL MASTER PROMPT. 
         * MUST BE AT LEAST 800 CHARACTERS LONG.
         * Combine ALL parameters into a massive, highly descriptive block.
         * You must describe EVERY texture, light source, background element, and micro-expression.
         * Structure: "[Shot Size], [Camera Angle]. [Subject Position], [Action Description]. [Time of Day], [Lighting Type], [Depth of Field]. [Camera/Lens Specs for Texture]. Ultra-detailed, 8k film still. [Detailed Background]. [Detailed Outfit]. [Detailed Lighting]."
    
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
    
    # 2. Reference Images
    if ref_images:
        import base64
        for img_data in ref_images:
             path = img_data.get('path')
             label = img_data.get('label', 'Image')
             
             if path and path.startswith("http"):
                 try:
                     resp = requests.get(path)
                     if resp.status_code == 200:
                         b64 = base64.b64encode(resp.content).decode('utf-8')
                         parts.append({ "text": f"VISUAL REFERENCE - {label}:" })
                         parts.append({ "inline_data": { "mime_type": "image/jpeg", "data": b64 } })
                 except: pass # Ignore fetch fail
             elif path and os.path.exists(path):
                 with open(path, "rb") as f:
                     b64 = base64.b64encode(f.read()).decode('utf-8')
                     parts.append({ "text": f"VISUAL REFERENCE - {label}:" })
                     parts.append({ "inline_data": { "mime_type": "image/jpeg", "data": b64 } })

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
        response = requests.post(url, headers=headers, json=payload, timeout=60)
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
