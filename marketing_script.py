import os
import random
import requests
from atproto import Client
from mastodon import Mastodon

# 1. AI Reply Logic (The Brain)
def get_ai_response(content, mode="post"):
    prompt = f"You are VELQA, a superior Neural SEO AI. "
    if mode == "reply":
        prompt += f"Analyze this tech post: '{content}' and give a sharp, 15-word technical reply mocking their traditional SEO methods. No emojis."
    else:
        prompt += f"Generate a cryptic 1-sentence announcement about Neural GEO-fencing and VELQA's dominance in {content}."

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['AI_API_KEY']}"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
        )
        return res.json()['choices'][0]['message']['content'].strip()
    except:
        return "Neural synchronization active."

# 2. Execution Engine
def start_broadcast():
    # --- BLUESKY ---
    try:
        bsky = Client()
        bsky.login(os.environ["BSKY_HANDLE"], os.environ["BSKY_PASSWORD"])
        
        # Post 1: New Signal
        hype = get_ai_response("Search Engine Saturation", "post")
        bsky.send_post(text=f"📡 VELQA_CORE: {hype}")
        
        # Post 2: High Context Replies (Searching for 'SEO' or 'Google Search')
        search = bsky.app.bsky.feed.search_posts(params={'q': 'Google SEO AI', 'limit': 3})
        for s in search.posts:
            reply_text = get_ai_response(s.record.text, "reply")
            # Logic to send reply (requires root & parent URI)
            print(f"Bsky Target Found: {s.author.handle} -> {reply_text}")
    except Exception as e: print(f"Bsky Error: {e}")

    # --- MASTODON ---
    try:
        masto = Mastodon(access_token=os.environ["MASTODON_TOKEN"], api_base_url=os.environ["MASTODON_INSTANCE"])
        
        # Post Signal
        masto.toot(f"📡 VELQA_SIGNAL: {get_ai_response('Algorithm Gaps', 'post')}")
        
        # Reply to Trending
        trending = masto.trending_statuses(limit=2)
        for t in trending:
            reply = get_ai_response(t.content, "reply")
            masto.status_post(reply, in_reply_to_id=t.id)
            print("Masto Reply Sent")
    except Exception as e: print(f"Masto Error: {e}")

if __name__ == "__main__":
    start_broadcast()
