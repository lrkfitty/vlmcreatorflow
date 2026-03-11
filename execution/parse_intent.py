"""
parse_intent.py
---------------
NL Art Director — maps a free-text creative brief to structured CreateFlow assets.

Layer 3 (Execution) script. Called by the Art Director tab in app.py.

Input:  brief (str) — natural language description of the desired shot
Output: dict with keys: character, outfit, vibe, scenario, aspect_ratio, additional_notes
"""

import os
import json
import re
from dotenv import load_dotenv

load_dotenv()


def _load_asset_catalog(world_db_path: str = "world_db.json") -> dict:
    """Load and flatten the world_db.json into a simplified catalog for LLM context."""
    if not os.path.exists(world_db_path):
        return {}

    with open(world_db_path, "r") as f:
        db = json.load(f)

    catalog = {}

    # Characters
    catalog["characters"] = [
        {"key": k, "name": v.get("name", k), "description": v.get("description", "")}
        for k, v in db.get("characters", {}).items()
    ]

    # Scenarios (vibes/locations)
    catalog["scenarios"] = [
        {"key": k, "name": v.get("name", k), "description": v.get("template_prompt", "")[:120]}
        for k, v in db.get("scenarios", {}).items()
    ]

    # Locations
    catalog["locations"] = [
        {"key": k, "name": v.get("name", k), "description": v.get("description", "")}
        for k, v in db.get("locations", {}).items()
    ]

    return catalog


def parse_intent(
    brief: str,
    world_db_path: str = "world_db.json",
    model_engine: str = "gemini-2.0-flash",
) -> dict:
    """
    Map a free-text creative brief to structured CreateFlow asset keys.

    Args:
        brief:          Natural language creative brief from the user.
        world_db_path:  Path to world_db.json (relative to project root).
        model_engine:   Gemini model to use.

    Returns:
        dict with:
            character       (str)  — matched character name or None
            outfit          (str)  — matched outfit description or raw mention
            vibe            (str)  — matched scenario/vibe name or raw mention
            scenario_key    (str)  — world_db scenario key or None
            aspect_ratio    (str)  — e.g. "9:16", "1:1", "16:9"
            additional_notes (str) — anything that didn't map to an asset
            raw_brief       (str)  — original brief, passed through
            confidence      (str)  — "high" | "medium" | "low"
    """
    import google.generativeai as genai

    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key:
        return _fallback_parse(brief, "GOOGLE_API_KEY not found in .env")

    catalog = _load_asset_catalog(world_db_path)

    # Build a compact, readable catalog string for the LLM
    characters_str = "\n".join(
        f"  - {c['name']} (key: {c['key']})" for c in catalog.get("characters", [])
    )
    scenarios_str = "\n".join(
        f"  - {s['name']} (key: {s['key']})" for s in catalog.get("scenarios", [])[:40]  # cap for token budget
    )
    locations_str = "\n".join(
        f"  - {l['name']} (key: {l['key']})" for l in catalog.get("locations", [])
    )

    system_prompt = f"""You are an AI Art Director for a social media content creator platform called CreateFlow.

Your job is to read a creative brief and map it to the available assets in the system.

AVAILABLE CHARACTERS:
{characters_str}

AVAILABLE SCENARIOS (vibes/settings):
{scenarios_str}

AVAILABLE LOCATIONS:
{locations_str}

RULES:
1. Match the best CHARACTER from the list above. Use the exact character name. If no match, use "Shay" as default.
2. Match the best SCENARIO from the list that fits the vibe. Use the exact scenario name.
3. Extract the OUTFIT description from the brief (can be free text — no need to match a list).
4. Determine the best ASPECT RATIO: "9:16" for portrait/social posts, "1:1" for square, "16:9" for landscape/cinematic.
5. Capture anything that doesn't fit into character/outfit/vibe as ADDITIONAL_NOTES.
6. Rate your CONFIDENCE: "high" if the brief was clear and specific matches exist, "medium" if some guesswork involved, "low" if the brief was vague.

OUTPUT: Return ONLY valid JSON in this exact format:
{{
    "character": "<matched character name>",
    "outfit": "<outfit description from brief or inferred>",
    "vibe": "<matched scenario name>",
    "scenario_key": "<matched scenario key>",
    "aspect_ratio": "<ratio>",
    "additional_notes": "<any extra creative direction, mood notes, or unmatched elements>",
    "confidence": "<high|medium|low>"
}}
"""

    user_message = f'Map this brief to CreateFlow assets:\n\n"{brief}"'

    try:
        genai.configure(api_key=google_key)
        model = genai.GenerativeModel(model_engine)
        response = model.generate_content([system_prompt, user_message])
        raw = response.text.strip()

        # Strip markdown fences if present
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        # Find JSON object
        start = raw.find("{")
        end = raw.rfind("}") + 1
        if start >= 0 and end > start:
            raw = raw[start:end]

        result = json.loads(raw)
        result["raw_brief"] = brief
        return result

    except Exception as e:
        print(f"[parse_intent] Error calling Gemini: {e}")
        return _fallback_parse(brief, str(e))


def _fallback_parse(brief: str, error: str = "") -> dict:
    """Graceful fallback — pass the brief through as additional_notes."""
    return {
        "character": "Shay",
        "outfit": "",
        "vibe": "",
        "scenario_key": None,
        "aspect_ratio": "9:16",
        "additional_notes": brief,
        "confidence": "low",
        "raw_brief": brief,
        "_error": error,
    }


# ─── Quick Test (run directly) ────────────────────────────────────────────────
if __name__ == "__main__":
    test_brief = "moody rooftop bar at night, Shay in a sleek black dress, editorial and cinematic"
    print("\n📋 Brief:", test_brief)
    result = parse_intent(test_brief)
    print("\n✅ Parsed Intent:")
    print(json.dumps(result, indent=2))
