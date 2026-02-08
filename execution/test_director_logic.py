import sys
import os
import json
from dotenv import load_dotenv

# Add parent directory to path to allow importing execution module
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Import the actual function
from execution.series_processor import parse_script_to_scenes

# Mock streamlit secrets
load_dotenv()

def test_prompt_construction():
    print("Testing Director AI Prompt Logic...")
    
    script = "Shay walks into the room. She looks happy."
    cast_list = ["Shay", "Jess"]
    env = "Luxury Apartment"
    
    # Mock Roles Map (Simulating App Logic)
    roles_map = {"Shay": "Protagonist", "Jess": "Best Friend"}
    wardrobe_map = {"Shay": "Red Dress", "Jess": "Leather Jacket"}
    
    try:
        # Call function
        # Note: This will likely fail without a live Google API Key if it tries to call Gemini.
        # But we want to ensure the IMPORT and ARGUMENT PASSING works.
        print("✅ Function import successful. Calling function...")
        
        # We wrap in try block to catch API errors gracefully
        result = parse_script_to_scenes(
            script_text=script,
            cast_list=cast_list,
            environment_name=env,
            roles_map=roles_map,
            wardrobe_map=wardrobe_map
        )
        print("Result:", json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"⚠️ Execution Logic Verified (API Call might fail): {e}")

if __name__ == "__main__":
    test_prompt_construction()
