import os, time
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from instagrapi import Client

SESSION_FILE = Path(".tmp/ig_session.json")
cl = Client()
cl.load_settings(SESSION_FILE)
cl.login(os.getenv("IG_USERNAME"), os.getenv("IG_PASSWORD"))

posts = [
    (
        "output/users/Neo/Instagram/gen_nano2_1774299768_9accaff5.jpg",
        "Built different. Not louder — sharper.\n\n#AIInfluencer #CreativeDirector #VisualStorytelling #MediaProduction #VLM"
    ),
    (
        "output/users/Neo/Instagram/gen_nano2_1774299805_03702776.jpg",
        "Moved through the space like it was built for this moment. It was not. That is the point.\n\n#AIMedia #VisualStorytelling #CreativeLife #ArtDirection #VLM"
    ),
    (
        "output/users/Neo/Instagram/gen_nano2_1774303572_3f629ac4.jpg",
        "She sees the detail I miss. That is not luck — that is design.\n\nWith @shay.so.fine — always building. @tytheguyyttg made this possible.\n\n#AIMedia #CreativePartners #StudioLife #CreateFlow #VLM #ShaySoFine"
    ),
]

for i, (img, cap) in enumerate(posts):
    print(f"Posting {i+1}/3: {img}")
    media = cl.photo_upload(img, cap)
    print(f"✅ Live: https://www.instagram.com/p/{media.code}/")
    if i < len(posts) - 1:
        print("Waiting 10s...")
        time.sleep(10)
