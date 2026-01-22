import os
import random
import requests
import time
from atproto import Client
from mastodon import Mastodon
from apscheduler.schedulers.background import BackgroundScheduler

def get_ai_hype(topic):
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": f"Write a cryptic 1-sentence tech prediction about {topic}. No hashtags."}]
            }
        )
        return res.json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return f"Neural link active on {topic}."

def broadcast_signal():
    print("🚀 BROADCAST STARTING...")
    topic = random.choice(["SEO", "AI Agents", "Web3", "Neural Networks"])
    content = get_ai_hype(topic)
    
    # Bluesky
    try:
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        bsky.send_post(text=f"VELQA_CORE: {content}")
        print("✅ Bluesky Success")
    except Exception as e: print(f"❌ Bsky Error: {e}")

    # Mastodon
    try:
        if os.getenv("MASTODON_TOKEN"):
            masto = Mastodon(access_token=os.getenv("MASTODON_TOKEN"), api_base_url=os.getenv("MASTODON_INSTANCE"))
            masto.toot(f"VELQA_CORE: {content}")
            print("✅ Mastodon Success")
    except Exception as e: print(f"❌ Mastodon Error: {e}")

# ANTI-SLEEP PING
def ping_self():
    url = os.getenv("SPACE_APP_URL") # Hugging Face ka app url (e.g. https://user-space.hf.space)
    if url:
        try:
            requests.get(url)
            print("⚡️ SELF-PING: Keeping Space Awake")
        except: pass

def start_bot_engine():
    scheduler = BackgroundScheduler()
    scheduler.add_job(broadcast_signal, 'interval', hours=4)
    scheduler.add_job(ping_self, 'interval', minutes=20) # Har 20 min mein jagayega
    scheduler.start()
