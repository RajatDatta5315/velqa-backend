import os
import random
from atproto import Client
from mastodon import Mastodon
from apscheduler.schedulers.background import BackgroundScheduler
import requests

# --- AI CONFIG ---
def get_ai_hype(topic):
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Write a cryptic, 1-sentence tech prediction about {topic}. No hashtags. Pure cyberpunk vibe."}]
            }
        )
        return res.json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"Neural link active on {topic}."

# --- POSTING LOGIC ---
def broadcast_signal():
    print("⚡️ INITIATING BROADCAST...")
    topic = random.choice(["SEO Singularity", "AI Agents", "Decentralized Web", "Neural Search"])
    content = get_ai_hype(topic)
    final_text = f"UNDEFINED_ENTITY: {content}"

    # 1. Bluesky
    try:
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        bsky.send_post(text=final_text)
        print("✅ Bluesky Sent")
    except Exception as e:
        print(f"❌ Bluesky Failed: {e}")

    # 2. Mastodon (New Integration)
    try:
        # Mastodon ke liye tujhe access token chahiye hoga (niche bataunga kaise milega)
        if os.getenv("MASTODON_TOKEN"):
            masto = Mastodon(
                access_token=os.getenv("MASTODON_TOKEN"),
                api_base_url=os.getenv("MASTODON_INSTANCE") # e.g., https://mastodon.social
            )
            masto.toot(final_text)
            print("✅ Mastodon Sent")
    except Exception as e:
        print(f"❌ Mastodon Failed: {e}")

# --- SCHEDULER ---
def start_bot_engine():
    scheduler = BackgroundScheduler()
    # Har 4 ghante mein post karega
    scheduler.add_job(broadcast_signal, 'interval', hours=4)
    scheduler.start()
    print("🤖 BOT NEXUS ONLINE: Scheduler Running inside Koyeb")
