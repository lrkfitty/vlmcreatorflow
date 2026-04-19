#!/usr/bin/env /opt/homebrew/bin/python3.11
"""
setup_ig_session.py — One-time browser login to save Instagram cookies.

Run this when an account's session expires. Opens a real Chrome window,
you log in manually (handles 2FA, challenges, etc.), then it saves the
browser cookies for post_via_browser.py to reuse.

Usage:
    python3.11 execution/setup_ig_session.py --account ty
    python3.11 execution/setup_ig_session.py --account neo
    python3.11 execution/setup_ig_session.py --account shay
    python3.11 execution/setup_ig_session.py --account vlm
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

BASE = Path(__file__).resolve().parent.parent
load_dotenv(BASE / ".env")
TMP = BASE / ".tmp"
TMP.mkdir(exist_ok=True)

ACCOUNT_USERNAMES = {
    "neo":  os.environ.get("IG_USERNAME",        "neoismyname1"),
    "shay": os.environ.get("IG_USERNAME_SHAY",   "shay.so.fine"),
    "ty":   os.environ.get("IG_USERNAME_TY",     "tytheguyyttg"),
    "vlm":  os.environ.get("IG_USERNAME_VLM",    "Virallensemediavlm"),
}

ACCOUNT_PASSWORDS = {
    "neo":  os.environ.get("IG_PASSWORD",        ""),
    "shay": os.environ.get("IG_PASSWORD_SHAY",   ""),
    "ty":   os.environ.get("IG_PASSWORD_TY",     ""),
    "vlm":  os.environ.get("IG_PASSWORD_VLM",    ""),
}


def cookies_file(account: str) -> Path:
    return TMP / f"ig_browser_cookies_{account}.json"


def save_session(account: str):
    from playwright.sync_api import sync_playwright

    username = ACCOUNT_USERNAMES.get(account, account)
    password = ACCOUNT_PASSWORDS.get(account, "")
    out_path = cookies_file(account)

    print(f"\n=== Instagram Session Setup — @{username} ===")
    print("A Chrome window will open. Log in normally.")
    print("If there's a verification code, enter it in the browser.")
    print("Once you can see your Instagram feed, come back here.\n")

    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,
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
        page = ctx.new_page()
        page.goto("https://www.instagram.com/accounts/login/", wait_until="domcontentloaded")
        time.sleep(2)

        # Pre-fill credentials if available
        if username and password:
            try:
                page.locator("input[name='username']").fill(username)
                page.locator("input[name='password']").fill(password)
                print(f"Credentials pre-filled for @{username}. Click Log In in the browser.")
            except Exception:
                print("Could not pre-fill credentials — fill them in manually.")

        print("\nWaiting for you to log in... (watching for Instagram feed)")
        print("Press Ctrl+C to cancel.\n")

        # Wait until the user is logged in (feed visible) — up to 3 minutes
        try:
            # Feed is loaded when we're NOT on the login page anymore
            # and we can see the home/create button
            page.wait_for_url(
                lambda url: "instagram.com" in url and "/accounts/login" not in url and "/challenge" not in url,
                timeout=180_000,
            )
            # Extra wait for the page to fully settle
            time.sleep(3)
        except Exception:
            print("Timed out waiting for login. Try again.")
            browser.close()
            sys.exit(1)

        # Check we're actually on the feed, not stuck somewhere
        current_url = page.url
        print(f"Logged in! Current page: {current_url}")

        # Save all instagram.com cookies
        all_cookies = ctx.cookies(["https://www.instagram.com"])
        cookie_map = {c["name"]: c["value"] for c in all_cookies}

        if "sessionid" not in cookie_map:
            print("ERROR: No sessionid cookie found after login. Try again.")
            browser.close()
            sys.exit(1)

        out_path.write_text(json.dumps(all_cookies, indent=2))
        print(f"\n✓ Session saved: {out_path}")
        print(f"  sessionid: {cookie_map['sessionid'][:30]}...")
        print(f"  ds_user_id: {cookie_map.get('ds_user_id', 'N/A')}")
        print(f"\nYou can now close the browser window.")
        print(f"post_via_browser.py will use this session for @{username}.")

        time.sleep(3)
        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Save Instagram browser session for automated posting.")
    parser.add_argument("--account", required=True, choices=["neo", "shay", "ty", "vlm"],
                        help="Which account to set up")
    args = parser.parse_args()
    save_session(args.account)


if __name__ == "__main__":
    main()
