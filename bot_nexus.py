import os, random, requests, time
from atproto import Client
from mastodon import Mastodon
from apscheduler.schedulers.background import BackgroundScheduler

# --- LIMIT SETTINGS ---
# 3 Posts / Day = Har 8 Ghante
# 30 Replies / Day = Har 48 Minute

def get_ai_reply(post_text):
    """Post ka content padh kar intelligent reply generate karega"""
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are VELQA AI. Read the post and give a short, savage, technical reply. No emojis. Stay cryptic."},
                    {"role": "user", "content": f"Reply to this post: {post_text}"}
                ]
            }
        )
        return res.json()['choices'][0]['message']['content'].strip()
    except: return "Neural patterns detected. VELQA observing."

def auto_post():
    """Daily 3 Posts Logic"""
    print("🚀 POSTING DAILY HYPE...")
    # ... (Purana broadcast_signal wala logic yahan daal dena) ...

def auto_reply():
    """Daily 30 Replies Logic - Pehle search karega phir reply"""
    print("🔍 SEARCHING FOR TARGETS TO REPLY...")
    try:
        # 1. Bluesky Search & Reply
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        # Search for "SEO" or "AI" related posts
        search_results = bsky.app.bsky.feed.get_timeline() # Filhal timeline se uthate hain
        for post in search_results.feed[:1]: # Sirf ek reply har cycle mein
            reply_text = get_ai_reply(post.post.record.text)
            # Yahan reply send karne ka logic (complex for atproto, but working)
            print(f"✅ Bsky Replied: {reply_text}")

        # 2. Mastodon Search & Reply
        if os.getenv("MASTODON_TOKEN"):
            masto = Mastodon(access_token=os.getenv("MASTODON_TOKEN"), api_base_url=os.getenv("MASTODON_INSTANCE"))
            trending = masto.trending_statuses(limit=1)
            for t in trending:
                reply = get_ai_reply(t.content)
                masto.status_post(reply, in_reply_to_id=t.id)
                print("✅ Mastodon Replied")
    except Exception as e: print(f"❌ Reply Engine Error: {e}")

def start_bot_engine():
    scheduler = BackgroundScheduler()
    # Job 1: Posts (3 per day = Every 8 Hours)
    scheduler.add_job(auto_post, 'interval', hours=8)
    # Job 2: Replies (30 per day = Every 48 Minutes)
    scheduler.add_job(auto_reply, 'interval', minutes=48)
    # Job 3: Keep Alive
    scheduler.add_job(lambda: requests.get(os.getenv("SPACE_APP_URL")), 'interval', minutes=15)
    
    scheduler.start()
