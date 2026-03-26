#!/usr/bin/env python3.11
"""
render_reel.py — Remotion Reel Renderer for Ty
------------------------------------------------
Drives the full reel render pipeline:

  1. Stage audio (VO .mp3) → vlm-ty-reels/public/audio/{reel_id}/vo.mp3
  2. Stage images          → vlm-ty-reels/public/images/{reel_id}/img_N.jpg
  3. Pick a music track    → vlm-ty-reels/public/music/{track}
  4. Call Remotion CLI     → renders 1080x1920 H.264 mp4
  5. Return output path

Usage:
    from execution.render_reel import render_reel
    mp4_path = render_reel(
        reel_id="reel_001",
        vo_path="output/reel_001_vo.mp3",
        transcript_path="output/reel_001_transcript.json",
        image_paths=["img1.jpg", "img2.jpg", "img3.jpg"],
    )
"""

import os
import json
import shutil
import random
import subprocess
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
_HERE = Path(__file__).parent
_REMOTION_ROOT = Path("/Users/tylarkin/Desktop/Claude Videos/vlm-ty-reels")
_MUSIC_MASTER  = Path("/Users/tylarkin/Desktop/Angeil Eyes Music Master")

# Music mood → subfolder mapping (prefer Chill for Ty's lifestyle content)
_MUSIC_FOLDERS = {
    "chill":    _MUSIC_MASTER / "Chill Rn:B:Hip Hop",
    "catch":    _MUSIC_MASTER / "Music Catch",
    "club":     _MUSIC_MASTER / "Club BKK",
    "house":    _MUSIC_MASTER / "House Party",
}

_SUPPORTED_AUDIO = (".mp3", ".wav", ".m4a", ".aac")
_SUPPORTED_IMG   = (".jpg", ".jpeg", ".png", ".webp")


def _pick_music(mood: str = "chill") -> tuple[str, float]:
    """
    Pick a random track from the given mood folder.
    Returns (absolute_path, random_start_offset_seconds).
    """
    folder = _MUSIC_FOLDERS.get(mood, _MUSIC_FOLDERS["chill"])
    if not folder.exists():
        # Fallback: scan all subfolders
        tracks = list(_MUSIC_MASTER.rglob("*.mp3"))
    else:
        tracks = [f for f in folder.iterdir() if f.suffix.lower() in _SUPPORTED_AUDIO]

    if not tracks:
        raise FileNotFoundError(f"No music tracks found in {folder}")

    track = random.choice(tracks)
    # Start somewhere in the first 2 minutes so we get the good part
    start_offset = random.uniform(10, 90)
    return str(track), start_offset


def _stage_files(
    reel_id: str,
    vo_path: str,
    image_paths: list,
) -> dict:
    """
    Copy VO + images into Remotion public/ folder.
    Returns staging info dict.
    """
    audio_dir = _REMOTION_ROOT / "public" / "audio" / reel_id
    image_dir = _REMOTION_ROOT / "public" / "images" / reel_id
    music_dir = _REMOTION_ROOT / "public" / "music"

    audio_dir.mkdir(parents=True, exist_ok=True)
    image_dir.mkdir(parents=True, exist_ok=True)
    music_dir.mkdir(parents=True, exist_ok=True)

    # Stage VO
    dest_vo = audio_dir / "vo.mp3"
    shutil.copy2(vo_path, dest_vo)
    print(f"📁 VO staged: {dest_vo}")

    # Stage images
    staged_images = []
    for i, img_path in enumerate(image_paths):
        src = Path(img_path)
        if not src.exists():
            print(f"⚠️  Image not found: {img_path} — skipping")
            continue
        ext = src.suffix.lower()
        if ext not in _SUPPORTED_IMG:
            print(f"⚠️  Unsupported image type: {ext} — skipping")
            continue
        dest_img = image_dir / f"img_{i}.jpg"
        # Convert to jpg if needed via copy (PIL would handle real conversion)
        shutil.copy2(src, dest_img)
        staged_images.append(str(dest_img))
        print(f"📁 Image {i} staged: {dest_img}")

    return {
        "audio_dir": str(audio_dir),
        "image_dir": str(image_dir),
        "music_dir": str(music_dir),
        "image_count": len(staged_images),
    }


def _stage_music(music_path: str, music_dir: str) -> str:
    """
    Copy chosen music track into public/music/ if not already there.
    Returns the filename (not full path).
    """
    src = Path(music_path)
    dest = Path(music_dir) / src.name
    if not dest.exists():
        shutil.copy2(src, dest)
    return src.name


def render_reel(
    reel_id: str,
    vo_path: str,
    transcript_path: str,
    image_paths: list,
    output_dir: str = None,
    music_mood: str = "chill",
    music_path: str = None,
    crf: int = 18,
) -> str:
    """
    Full Reel render pipeline.

    Args:
        reel_id:         Unique ID (used for folder naming)
        vo_path:         Path to VO .mp3
        transcript_path: Path to transcript .json (word timestamps)
        image_paths:     List of image file paths (3-4 recommended)
        output_dir:      Where to save the final .mp4 (default: output/reels/)
        music_mood:      "chill" | "catch" | "club" | "house"
        music_path:      Explicit music path (overrides mood picker)
        crf:             H.264 quality (18 = high quality, lower = bigger file)

    Returns:
        Absolute path to rendered .mp4
    """
    output_dir = output_dir or str(_HERE.parent / "output" / "reels")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    output_path = os.path.join(output_dir, f"{reel_id}.mp4")

    # 1. Load transcript
    with open(transcript_path, "r") as f:
        transcript = json.load(f)

    words    = transcript["words"]      # [{word, start, end}]
    duration = transcript["duration"]   # seconds

    print(f"🎬 Rendering reel: {reel_id}")
    print(f"   VO duration: {duration:.1f}s | Words: {len(words)} | Images: {len(image_paths)}")

    # 2. Stage files
    staging = _stage_files(reel_id, vo_path, image_paths)

    # 3. Music
    if music_path:
        chosen_music, music_start = music_path, 30.0
    else:
        chosen_music, music_start = _pick_music(music_mood)

    music_filename = _stage_music(chosen_music, staging["music_dir"])
    print(f"🎵 Music: {music_filename} (start: {music_start:.0f}s)")

    # 4. Build props JSON for Remotion
    props = {
        "reelId":      reel_id,
        "words":       words,
        "duration":    duration,
        "imageCount":  staging["image_count"],
        "musicFile":   music_filename,
        "musicStart":  music_start,
    }
    props_json = json.dumps(props)

    # 5. Total frames = VO duration + 1.5s tail
    total_frames = int((duration + 1.5) * 30) + 1

    # 6. Call Remotion CLI
    cmd = [
        "npx", "remotion", "render",
        "src/index.tsx",
        "TyReel",
        output_path,
        f"--props={props_json}",
        f"--frames=0-{total_frames}",
        f"--codec=h264",
        f"--crf={crf}",
        "--width=1080",
        "--height=1920",
        "--fps=30",
        "--concurrency=4",
    ]

    print(f"🔧 Running Remotion render...")
    result = subprocess.run(
        cmd,
        cwd=str(_REMOTION_ROOT),
        capture_output=False,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Remotion render failed (exit {result.returncode})")

    print(f"✅ Reel rendered: {output_path}")
    return output_path


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    import glob

    if len(sys.argv) < 4:
        print("Usage: python3 execution/render_reel.py <reel_id> <vo.mp3> <transcript.json> [img1 img2 ...]")
        sys.exit(1)

    reel_id_arg     = sys.argv[1]
    vo_arg          = sys.argv[2]
    transcript_arg  = sys.argv[3]
    images_arg      = sys.argv[4:] or []

    mp4 = render_reel(
        reel_id=reel_id_arg,
        vo_path=vo_arg,
        transcript_path=transcript_arg,
        image_paths=images_arg,
    )
    print(f"\n🎬 Output: {mp4}")
