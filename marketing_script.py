import os
import random
import requests
from atproto import Client
from mastodon import Mastodon

def get_ai_hype():
    topics = ["Neural SEO", "AI GEO-Optimization", "Search Gaps", "Digital Authority"]
    topic = random.choice(topics)
    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['AI_API_KEY']}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are VELQA. Write 1 savage, cryptic sentence about AI taking over search. No hashtags."},
                             {"role": "user", "content": f"Topic: {topic}"}]
            }
        )
        return res.json()['choices'][0]['message']['content'].strip()
    except: return "Neural networks expanding."

def run_marketing():
    text = f"VELQA_SIGNAL: {get_ai_hype()}"
    
    # Bluesky
    try:
        bsky = Client()
        bsky.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_PASSWORD"])
        bsky.send_post(text=text)
        print("✅ Bluesky Post Done")
    except Exception as e: print(f"Bsky Error: {e}")

    # Mastodon
    try:
        masto = Mastodon(access_token=os.environ["MASTODON_TOKEN"], api_base_url=os.environ["MASTODON_INSTANCE"])
        masto.toot(text)
        print("✅ Mastodon Post Done")
    except Exception as e: print(f"Masto Error: {e}")

if __name__ == "__main__":
    run_marketing()
