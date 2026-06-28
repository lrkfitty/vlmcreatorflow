#!/usr/bin/env python3.11
"""
generate_vo.py — Voiceover Generator with Word-Level Timestamps
---------------------------------------------------------------
Generates VO audio + word timestamps for Remotion caption sync.

Step 1: Generate VO script from image + context via Gemini
Step 2: Synthesize speech via ElevenLabs with word-level timestamps
Step 3: Save .mp3 + .json (word timestamps) to output dir

Usage:
    from execution.generate_vo import generate_vo
    result = generate_vo(
        context="Ty at rooftop Bangkok, late night",
        account="ty",
        output_dir="output/users/Tyrie/Reels/",
        reel_id="reel_001",
        style="hook"   # hook | builder | lifestyle | day_in_life
    )
    # Returns: {"audio_path": "...", "transcript_path": "...", "script": "..."}
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Voice IDs ──────────────────────────────────────────────────────────────────
VOICES = {
    "ty":    "YrNC95Mxua3x0bsFLL2s",  # Tyrie 2205
    "shay":  "t57i1laWzBvWcMySqAmS",  # Shay voice
    "neo":   "YrNC95Mxua3x0bsFLL2s",  # fallback to Ty for now
}

# ── Script styles (Ty-specific narrative templates) ────────────────────────────
TY_SCRIPT_PROMPTS = {
    "hook": """
Write a 10-15 second Instagram Reel VO script for Ty (Tyrie), an entrepreneur building an AI content company
from Bangkok, Thailand.

STYLE: First-person, direct, confessional. Sounds like a smart friend talking, not an ad.
HOOK (first 2 seconds): Bold claim or curiosity gap. Examples:
- "I quit my job to build this from Bangkok."
- "This single thing is compounding my brand while I sleep."
- "Nobody told me content could work like this."
BODY (3-10 seconds): Quick, specific value or story beat. Real numbers if possible.
CTA (last 2 seconds): Soft — "follow for more" or nothing. Never salesy.

CONTEXT: {context}

RULES:
- Max 60 words total (reads in ~12 seconds at natural pace)
- No filler words ("um", "like", "you know")
- No corporate speak
- Sentence fragments are fine — natural spoken cadence
- Do NOT include stage directions, just the words to speak

Return ONLY the script text, nothing else.
""",
    "builder": """
Write a 10-15 second Instagram Reel VO script for Ty (Tyrie), entrepreneur and AI creator in Bangkok.

NARRATIVE: Builder energy. Behind the scenes of creating something real.
STYLE: Thoughtful, confident, slightly vulnerable. Not a guru — a guy figuring it out in real time.

CONTEXT: {context}

RULES:
- Max 60 words
- First person, conversational
- Specific detail beats generic claim
- Ends with something that makes them want to follow the story

Return ONLY the script text.
""",
    "lifestyle": """
Write a 10-15 second Instagram Reel VO script for Ty (Tyrie), living and building in Bangkok, Thailand.

NARRATIVE: Aspirational but real. Bangkok luxury lifestyle meets builder hustle.
STYLE: Cool, relaxed confidence. Not showing off — sharing a moment.

CONTEXT: {context}

RULES:
- Max 60 words
- Vivid, sensory language — make them feel the scene
- Drops a subtle flex naturally, not forcefully
- Authentic, not performative

Return ONLY the script text.
""",
    "day_in_life": """
Write a 10-15 second Instagram Reel VO script for Ty (Tyrie), day-in-the-life format.

NARRATIVE: Real moment from building/living in Bangkok. Honest, present tense.
STYLE: Like a voice memo he's sending to a close friend.

CONTEXT: {context}

RULES:
- Max 60 words
- Present tense preferred
- Specific time/place details ground it ("3am Bangkok", "poolside with my laptop")
- Ends on a beat that makes you want to see what happens next

Return ONLY the script text.
"""
}


def generate_script(context: str, account: str = "ty", style: str = "hook") -> str:
    """Generate VO script via Gemini based on context + account style."""
    import google.generativeai as genai
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not set")

    prompt_template = TY_SCRIPT_PROMPTS.get(style, TY_SCRIPT_PROMPTS["hook"])
    prompt = prompt_template.replace("{context}", context)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.5-flash")
    response = model.generate_content(prompt)
    script = response.text.strip().strip('"').strip("'")
    return script


def synthesize_vo(script: str, account: str = "ty", output_path: str = None) -> dict:
    """
    Synthesize speech via ElevenLabs with word-level timestamps.
    Returns {"audio_path": str, "words": [{"word": str, "start": float, "end": float}]}
    """
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        raise ValueError("ELEVENLABS_API_KEY not set")

    voice_id = VOICES.get(account, VOICES["ty"])

    # ElevenLabs v1 TTS with timestamps
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.45,
            "similarity_boost": 0.82,
            "style": 0.35,
            "use_speaker_boost": True
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()

    # Save audio
    import base64
    audio_b64 = data.get("audio_base64", "")
    audio_bytes = base64.b64decode(audio_b64)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

    # Parse word-level alignment
    alignment = data.get("alignment", {})
    chars = alignment.get("characters", [])
    char_starts = alignment.get("character_start_times_seconds", [])
    char_ends = alignment.get("character_end_times_seconds", [])

    # Group chars into words
    words = []
    current_word = ""
    word_start = None
    word_end = None

    for i, char in enumerate(chars):
        start = char_starts[i] if i < len(char_starts) else 0
        end = char_ends[i] if i < len(char_ends) else 0

        if char == " " or i == len(chars) - 1:
            if char != " ":
                current_word += char
                word_end = end
            if current_word.strip():
                words.append({
                    "word": current_word.strip(),
                    "start": round(word_start or start, 3),
                    "end": round(word_end or end, 3)
                })
            current_word = ""
            word_start = None
            word_end = None
        else:
            if not current_word:
                word_start = start
            current_word += char
            word_end = end

    # Fix zero-duration words: each word's end = next word's start (or start + 0.1s floor)
    for i, w in enumerate(words):
        if w["end"] <= w["start"]:
            if i + 1 < len(words):
                w["end"] = words[i + 1]["start"]
            else:
                w["end"] = round(w["start"] + 0.1, 3)

    return {"audio_path": output_path, "words": words, "duration": char_ends[-1] if char_ends else 0}


def generate_vo(
    context: str,
    account: str = "ty",
    output_dir: str = None,
    reel_id: str = None,
    style: str = "hook"
) -> dict:
    """
    Full pipeline: generate script → synthesize VO → save audio + timestamps.

    Returns:
    {
        "script": str,
        "audio_path": str,
        "transcript_path": str,
        "words": [...],
        "duration": float
    }
    """
    output_dir = output_dir or "output/users/Tyrie/Reels"
    reel_id = reel_id or f"reel_{int(__import__('time').time())}"
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 1. Generate script
    script = generate_script(context, account=account, style=style)
    print(f"📝 Script: {script[:100]}...")

    # 2. Synthesize
    audio_path = os.path.join(output_dir, f"{reel_id}_vo.mp3")
    result = synthesize_vo(script, account=account, output_path=audio_path)

    # 3. Save transcript + word timestamps
    transcript_path = os.path.join(output_dir, f"{reel_id}_transcript.json")
    transcript_data = {
        "reel_id": reel_id,
        "account": account,
        "style": style,
        "context": context,
        "script": script,
        "words": result["words"],
        "duration": result["duration"]
    }
    with open(transcript_path, "w") as f:
        json.dump(transcript_data, f, indent=2)

    print(f"✅ VO generated: {audio_path} ({result['duration']:.1f}s, {len(result['words'])} words)")

    return {
        "script": script,
        "audio_path": audio_path,
        "transcript_path": transcript_path,
        "words": result["words"],
        "duration": result["duration"]
    }


if __name__ == "__main__":
    import sys
    context = sys.argv[1] if len(sys.argv) > 1 else "Ty working late at a Bangkok rooftop, building his AI content company"
    style = sys.argv[2] if len(sys.argv) > 2 else "hook"
    result = generate_vo(context=context, account="ty", style=style)
    print(f"\nScript: {result['script']}")
    print(f"Duration: {result['duration']:.1f}s")
    print(f"Audio: {result['audio_path']}")
