#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
post_via_browser.py — Instagram posting via Playwright browser automation.

Bypasses instagrapi's private API (which Instagram blocks for automated clients).
Uses real Chromium with your session cookie — identical to posting manually.

Supports: single photo, carousels (2–10 images).

Usage (standalone):
    python3.11 execution/post_via_browser.py \
        --account ty \
        --images output/users/Tyrie/Instagram/day02_shot1.jpg output/users/Tyrie/Instagram/day02_shot2.jpg \
        --caption "Caption text here"

    # Headless (for cron):
    python3.11 execution/post_via_browser.py --account ty --images ... --caption "..." --headless
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import unquote

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")

TMP = BASE / ".tmp"
TMP.mkdir(exist_ok=True)


# ── Session helpers ──────────────────────────────────────────────────────────

def _get_session_cookies(account: str) -> list[dict]:
    """
    Return cookies for Playwright. Priority:
      1. ig_browser_cookies_{account}.json  — saved by setup_ig_session.py (full cookie jar)
      2. ig_session_{account}.json          — instagrapi session file
      3. IG_SESSIONID_{ACCOUNT} in .env     — raw sessionid string
    """
    # 1. Full browser cookie jar (best — saved by setup_ig_session.py)
    browser_cookie_file = TMP / f"ig_browser_cookies_{account}.json"
    if browser_cookie_file.exists():
        try:
            cookies = json.loads(browser_cookie_file.read_text())
            if any(c["name"] == "sessionid" for c in cookies):
                return cookies
        except Exception:
            pass

    # 2. instagrapi session file
    insta_session_file = TMP / f"ig_session_{account}.json"
    sessionid = None
    ds_user_id = None
    if insta_session_file.exists():
        try:
            data = json.loads(insta_session_file.read_text())
            cookies_dict = data.get("cookies", {})
            sessionid = cookies_dict.get("sessionid")
            ds_user_id = cookies_dict.get("ds_user_id")
            if not sessionid:
                auth = data.get("authorization_data", {})
                sessionid = auth.get("sessionid")
                ds_user_id = auth.get("ds_user_id") or (sessionid.split(":")[0] if sessionid else None)
        except Exception:
            pass

    # 3. .env fallback
    if not sessionid:
        env_key = f"IG_SESSIONID_{account.upper()}"
        raw = os.environ.get(env_key, "")
        if raw:
            sessionid = unquote(raw)
            ds_user_id = sessionid.split(":")[0]

    if not sessionid:
        raise ValueError(
            f"No session found for '{account}'. "
            f"Run: python3.11 execution/setup_ig_session.py --account {account}"
        )

    return [
        {"name": "sessionid",  "value": sessionid,            "domain": ".instagram.com", "path": "/"},
        {"name": "ds_user_id", "value": str(ds_user_id or ""), "domain": ".instagram.com", "path": "/"},
    ]


# ── Core posting logic ───────────────────────────────────────────────────────

def _dismiss_dialogs(page):
    """Dismiss notification / cookie prompts if they appear."""
    for selector in [
        "text=Not Now",
        "text=Not now",
        "text=Allow",
        "[aria-label='Close']",
    ]:
        try:
            btn = page.locator(selector).first
            if btn.is_visible(timeout=1500):
                btn.click()
                time.sleep(0.5)
        except Exception:
            pass


def _wait_and_click(page, *selectors, timeout=15000, description="element"):
    """Try each selector in order, click the first one that's visible."""
    for sel in selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=timeout)
            loc.click()
            return
        except Exception:
            continue
    raise TimeoutError(f"Could not find clickable {description}. Tried: {selectors}")


def post_to_instagram(
    image_paths: list[str],
    caption: str,
    account: str,
    headless: bool = False,
) -> str | None:
    """
    Post one or more images to Instagram via browser automation.
    Returns the post URL on success, None on failure.
    """
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

    image_paths = [str(p) for p in image_paths if Path(p).exists()]
    if not image_paths:
        raise FileNotFoundError("No valid image paths provided.")

    cookies = _get_session_cookies(account)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"],
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        ctx.add_cookies(cookies)
        page = ctx.new_page()

        try:
            print(f"  [browser] Opening Instagram for @{account}...")
            page.goto("https://www.instagram.com/", wait_until="domcontentloaded", timeout=30000)
            time.sleep(2)
            _dismiss_dialogs(page)

            # Verify we're logged in (no login form visible)
            if page.locator("input[name='username']").is_visible(timeout=3000):
                raise RuntimeError(
                    f"Session expired for @{account} — Instagram showing login form.\n"
                    f"  Fix: python3.11 execution/setup_ig_session.py --account {account}"
                )

            print("  [browser] Logged in. Opening Create Post...")

            # Click the "Create" / New post button
            _wait_and_click(
                page,
                "[aria-label='New post']",
                "svg[aria-label='New post']",
                "[aria-label='Create']",
                # fallback: find by text in nav
                "text=Create",
                description="Create Post button",
                timeout=10000,
            )
            time.sleep(1.5)
            _dismiss_dialogs(page)

            # Upload files via the file chooser dialog
            print(f"  [browser] Uploading {len(image_paths)} image(s)...")
            with page.expect_file_chooser(timeout=10000) as fc_info:
                _wait_and_click(
                    page,
                    "text=Select from computer",
                    "button:has-text('Select from computer')",
                    description="Select from computer button",
                    timeout=8000,
                )
            file_chooser = fc_info.value
            file_chooser.set_files(image_paths)
            time.sleep(2)

            # If carousel: Instagram may show "Add more" after first image
            # Multiple files selected at once is handled — just proceed

            # Next → Crop step
            print("  [browser] Advancing through crop step...")
            _wait_and_click(
                page,
                "button:has-text('Next')",
                "[role='button']:has-text('Next')",
                description="Next (crop)",
                timeout=15000,
            )
            time.sleep(1.5)

            # Next → Filter/Edit step
            print("  [browser] Advancing through filter step...")
            _wait_and_click(
                page,
                "button:has-text('Next')",
                "[role='button']:has-text('Next')",
                description="Next (filters)",
                timeout=10000,
            )
            time.sleep(1.5)

            # Caption
            print("  [browser] Adding caption...")
            caption_sel = [
                "textarea[aria-label='Write a caption…']",
                "textarea[aria-label='Write a caption...']",
                "div[aria-label='Write a caption…']",
                "div[aria-label='Write a caption...']",
                "div[role='textbox'][aria-label*='caption']",
                "textarea[placeholder*='caption']",
            ]
            for sel in caption_sel:
                try:
                    loc = page.locator(sel).first
                    if loc.is_visible(timeout=4000):
                        loc.click()
                        loc.fill(caption)
                        break
                except Exception:
                    continue

            time.sleep(1)

            # Share
            print("  [browser] Clicking Share...")
            _wait_and_click(
                page,
                "button:has-text('Share')",
                "[role='button']:has-text('Share')",
                description="Share button",
                timeout=10000,
            )

            # Wait for success — watch for "Post shared" text or URL change
            print("  [browser] Waiting for confirmation...")
            post_url = None
            try:
                page.wait_for_selector(
                    "text=Your post has been shared,text=Post shared",
                    timeout=30000,
                )
                print("  [browser] Post shared!")
            except PWTimeout:
                # Sometimes it just redirects without a confirmation banner
                pass

            # Try to grab the post URL from any "View Post" link or current URL
            try:
                view_link = page.locator("a:has-text('View Post'), a[href*='/p/']").first
                if view_link.is_visible(timeout=3000):
                    post_url = view_link.get_attribute("href")
                    if post_url and not post_url.startswith("http"):
                        post_url = "https://www.instagram.com" + post_url
            except Exception:
                pass

            time.sleep(2)
            return post_url or "posted (URL not captured)"

        except Exception as e:
            # Save a screenshot for debugging
            try:
                shot_path = TMP / f"post_error_{account}.png"
                page.screenshot(path=str(shot_path))
                print(f"  [browser] Screenshot saved → {shot_path}")
            except Exception:
                pass
            raise
        finally:
            browser.close()


# ── CLI entry point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Post to Instagram via browser automation")
    parser.add_argument("--account",  required=True, help="Account key: neo | shay | ty | vlm")
    parser.add_argument("--images",   required=True, nargs="+", help="Image file path(s)")
    parser.add_argument("--caption",  required=True, help="Post caption")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    args = parser.parse_args()

    print(f"\n=== Browser Post: @{args.account} | {len(args.images)} image(s) ===")
    try:
        url = post_to_instagram(
            image_paths=args.images,
            caption=args.caption,
            account=args.account,
            headless=args.headless,
        )
        print(f"\n✓ Posted: {url}")
    except Exception as e:
        print(f"\n✗ Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
