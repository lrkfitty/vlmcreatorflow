import os, json
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from instagrapi import Client

SESSION_FILE = Path(".tmp/ig_session_shay.json")
cl = Client()
cl.load_settings(SESSION_FILE)
cl.login(os.getenv("IG_SHAY_USERNAME"), os.getenv("IG_SHAY_PASSWORD"))

user = cl.user_info_by_username("shay.so.fine")
medias = cl.user_medias(user.pk, amount=32)

print(f"=== SHAY.SO.FINE CONTENT AUDIT ===")
print(f"Total posts: {len(medias)}\n")

likes_total = 0
comments_total = 0

for i, m in enumerate(medias):
    likes_total += m.like_count
    comments_total += m.comment_count
    caption = (m.caption_text or "")[:80].replace("\n", " ")
    print(f"{i+1:2d}. [{m.media_type}] 👍{m.like_count} 💬{m.comment_count} | {m.taken_at.strftime('%b %d')} | {caption}")

avg_likes = likes_total / len(medias)
avg_comments = comments_total / len(medias)
engagement = ((likes_total + comments_total) / len(medias)) / 150 * 100

print(f"\n=== STATS ===")
print(f"Avg likes:    {avg_likes:.1f}")
print(f"Avg comments: {avg_comments:.1f}")
print(f"Eng. rate:    {engagement:.1f}%")

# Top performers
top = sorted(medias, key=lambda x: x.like_count + x.comment_count, reverse=True)[:5]
print(f"\n=== TOP 5 POSTS ===")
for m in top:
    caption = (m.caption_text or "")[:60].replace("\n", " ")
    print(f"  👍{m.like_count} 💬{m.comment_count} | {m.taken_at.strftime('%b %d')} | {caption}")
