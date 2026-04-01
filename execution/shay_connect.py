import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from instagrapi import Client

SESSION_FILE = Path(".tmp/ig_session_shay.json")
SESSION_FILE.parent.mkdir(parents=True, exist_ok=True)

cl = Client()
cl.delay_range = [2, 5]

username = os.getenv("IG_SHAY_USERNAME")
password = os.getenv("IG_SHAY_PASSWORD")
print(f"Connecting: @{username}")

cl.login(username, password)
cl.dump_settings(SESSION_FILE)

user = cl.user_info_by_username(username)
print(f"✅ Connected: @{user.username}")
print(f"Followers:   {user.follower_count:,}")
print(f"Following:   {user.following_count:,}")
print(f"Posts:       {user.media_count}")
print(f"Bio:         {user.biography}")
