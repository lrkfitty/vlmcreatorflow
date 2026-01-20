import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def generate_storyboard_prompts(scenario_name, context, model="gemini"):
    """
    Generates 4 sequential prompts for a storyboard.
    Returns: List of 4 strings.
    """
    
    system_instruction = f"""
    You are an award-winning Film & Creative Director.
    Create a 4-step storyboard (4 sequential image prompts) based on the following scenario.
    
    SCENARIO: {scenario_name}
    CONTEXT/DETAILS: {context}
    
    CRITICAL DIRECTION:
    - If there are "Friends" or "Cast" mentioned (e.g., Jess, best friend), they are CO-STARS, not extras.
    - They must be interacting meaningfully with the protagonist (e.g., sharing a laugh, toasting drinks, intense conversation, hugging).
    - NEVER put friends in the background. They are part of the core narrative.
    - Treat this like a TV Show scene where the chemistry between characters is the main focus.
    
    REQUIREMENTS:
    - Return ONLY a JSON list of 4 strings. Example: ["Prompt 1", "Prompt 2", "Prompt 3", "Prompt 4"]
    - Style: High-end, cinematic, vivid descriptions.
    - Include specific camera angles (e.g., "Over-the-shoulder shot", "Low angle") and lighting.
    - Ensure outfit details are visible in the action.
    """
    
    if model == "gemini":
        return _generate_gemini(system_instruction)
    else:
        # Fallback or future expansion
        return _generate_gemini(system_instruction)

def _generate_gemini(prompt):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return ["Error: Missing GOOGLE_API_KEY", "", "", ""]
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    headers = { "Content-Type": "application/json" }
    
    payload = {
        "contents": [{
            "parts": [{ "text": prompt }]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        res_json = response.json()
        
        # Extract text
        if 'candidates' not in res_json:
            print(f"❌ Storyboard Gen Error: {res_json.get('promptFeedback', res_json)}")
            return []
            
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        
        # Clean markdown
        text = text.replace('```json', '').replace('```', '').strip()
        
        # Parse JSON
        try:
            params = json.loads(text)
        except json.JSONDecodeError:
             return ["Error parsing JSON", text, "", ""]

        # Handle Dict wrapper case (e.g. {"prompts": [...]})
        if isinstance(params, dict):
            for key, val in params.items():
                if isinstance(val, list):
                    params = val
                    break
        if isinstance(params, list) and len(params) >= 4:
            return params[:4]
        else:
            return ["Error parsing response", str(text), "", ""]
            
    except Exception as e:
        return [f"API Error: {e}", "", "", ""]
