"""
Instagram Client for Neo, Shay, and Ty
Uses instagrapi for direct Instagram API access.

Auth priority:
  1. Local session file (.tmp/ig_session_{account}.json) — fastest, reused across runs
  2. 1Password sessionid — fetched via `op` CLI when session file is missing/expired
  3. Username/password login — last resort, prone to IG rate limits

1Password item titles:
  Neo  → "Instagram Neo (neoismyname1)"
  Shay → "Instagram Shay (shay.so.fine)"
  Ty   → "Instagram Ty (tytheguyyttg)"
  Each item has a "sessionid" field containing the IG sessionid cookie value.

Usage:
    from execution.instagram_client import get_client, post_carousel
    cl = get_client(account="shay")  # or "neo", "ty"
    post_carousel(image_paths, caption, account="shay")
"""

import os
import json
import subprocess
from pathlib import Path
from instagrapi import Client

TMP_DIR = Path(__file__).parent.parent / ".tmp"

# 1Password item titles per account
OP_ITEM_TITLES = {
    "neo":  "Instagram Neo (neoismyname1)",
    "shay": "Instagram Shay (shay.so.fine)",
    "ty":   "Instagram Ty (tytheguyyttg)",
}


def get_session_file(account="neo"):
    return TMP_DIR / f"ig_session_{account}.json"


def _fetch_sessionid_from_1password(account):
    """Fetch IG sessionid from 1Password via op CLI. Returns None if unavailable."""
    from urllib.parse import unquote
    title = OP_ITEM_TITLES.get(account)
    if not title:
        return None
    try:
        result = subprocess.run(
            ["op", "item", "get", title, "--fields", "sessionid", "--reveal"],
            capture_output=True, text=True, timeout=10
        )
        sid = result.stdout.strip()
        if not sid:
            return None
        # 1Password stores the raw cookie value which may be URL-encoded (%3A → :)
        return unquote(sid)
    except Exception:
        return None


def _patch_instagrapi_extractors():
    """Patch instagrapi extractors to handle missing fields in newer IG API responses."""
    try:
        import instagrapi.extractors as ext
        _orig = ext.extract_broadcast_channel
        def _safe(data):
            try:
                return _orig(data)
            except (KeyError, TypeError):
                return []
        ext.extract_broadcast_channel = _safe
    except Exception:
        pass


def get_client(account="neo"):
    """Get an authenticated Instagram client. Reuses session if available."""
    _patch_instagrapi_extractors()
    cl = Client()
    session_file = get_session_file(account)

    # 1. Try existing session file
    if session_file.exists():
        try:
            cl.load_settings(str(session_file))
            cl.login_by_sessionid(cl.settings.get("authorization_data", {}).get("sessionid", ""))
            cl.get_timeline_feed()
            return cl
        except Exception:
            session_file.unlink(missing_ok=True)
            cl = Client()

    # 2. Try sessionid from .env (IG_SESSIONID_NEO / IG_SESSIONID_SHAY / IG_SESSIONID_TY)
    env_key = f"IG_SESSIONID_{account.upper()}"
    sessionid = os.environ.get(env_key) or _fetch_sessionid_from_1password(account)
    if sessionid:
        try:
            source = ".env" if os.environ.get(env_key) else "1Password"
            print(f"[{source}] Fetched sessionid for {account}, logging in...")
            user_id = sessionid.split(":")[0]
            username = os.environ.get(
                f"IG_USERNAME_{account.upper()}" if account != "neo" else "IG_USERNAME", account
            )
            # Set session directly — avoids user_info_v1/graphql validation calls
            # that fail due to instagrapi/Instagram API version mismatch
            settings = cl.get_settings()
            settings["authorization_data"]["sessionid"] = sessionid
            settings["authorization_data"]["ds_user_id"] = user_id
            cl.set_settings(settings)
            cl.private.cookies.update({"sessionid": sessionid, "ds_user_id": user_id})
            cl.username = username
            cl.get_timeline_feed()  # verify session actually works
            session_file.parent.mkdir(parents=True, exist_ok=True)
            cl.dump_settings(str(session_file))
            print(f"[{source}] Session restored and saved for {account}")
            return cl
        except Exception as e:
            print(f"[{source}] sessionid login failed for {account}: {e}")
            cl = Client()

    # 3. Fall back to username/password login
    username_key = f"IG_USERNAME_{account.upper()}" if account != "neo" else "IG_USERNAME"
    password_key = f"IG_PASSWORD_{account.upper()}" if account != "neo" else "IG_PASSWORD"

    username = os.environ.get(username_key)
    password = os.environ.get(password_key)

    if not username or not password:
        raise ValueError(
            f"Set {username_key} and {password_key} environment variables. "
            "Never hardcode credentials."
        )

    def challenge_code_handler(username, choice):
        print(f"\nInstagram verification required for @{username}.")
        print("Check your email/SMS — a 6-digit code was sent.")
        return input("Enter the code: ").strip()

    cl.challenge_code_handler = challenge_code_handler
    cl.login(username, password)

    session_file.parent.mkdir(parents=True, exist_ok=True)
    cl.dump_settings(str(session_file))

    return cl


def post_photo(image_path: str, caption: str, account="neo"):
    """Post a single photo with caption."""
    cl = get_client(account=account)
    media = cl.photo_upload(image_path, caption)
    print(f"Posted to {account}: https://www.instagram.com/p/{media.code}/")
    return media


def post_carousel(image_paths: list, caption: str, account="neo"):
    """Post multiple images as a carousel."""
    cl = get_client(account=account)
    media = cl.album_upload(image_paths, caption)
    print(f"Posted carousel to {account}: https://www.instagram.com/p/{media.code}/")
    return media


def post_reel(
    video_path: str,
    caption: str,
    account: str = "ty",
    thumbnail_path: str = None,
) -> object:
    """
    Post a video as an Instagram Reel via instagrapi clip_upload.

    Args:
        video_path:      Path to .mp4 (1080x1920, H.264, ≤60s)
        caption:         Caption text (include hashtags here)
        account:         Account key from ACCOUNTS dict
        thumbnail_path:  Optional custom thumbnail image (.jpg)

    Returns:
        instagrapi Media object
    """
    cl = get_client(account=account)

    kwargs = {}
    if thumbnail_path and os.path.exists(thumbnail_path):
        kwargs["thumbnail"] = thumbnail_path

    media = cl.clip_upload(
        path=video_path,
        caption=caption,
        **kwargs
    )
    print(f"🎬 Reel posted to @{account}: https://www.instagram.com/p/{media.code}/")
    return media


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python instagram_client.py <image_path> <caption> [account]")
        sys.exit(1)
    account = sys.argv[3] if len(sys.argv) > 3 else "neo"
    post_photo(sys.argv[1], sys.argv[2], account=account)
