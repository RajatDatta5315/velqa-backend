import os, requests, random
from atproto import Client

def run_once():
    try:
        # 1. Login to Bluesky
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        
        # 2. Get AI Content for Post
        topics = ["Neural SEO", "GEO Optimization", "AI Agent Economy", "Future of Web3 Search"]
        prompt = f"Write a cryptic and powerful 1-sentence tech prediction about {random.choice(topics)}. No hashtags."
        
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are VELQA AI, an advanced neural entity."},
                             {"role": "user", "content": prompt}]
            }
        )
        
        if res.status_code == 200:
            post_text = res.json()['choices'][0]['message']['content'].strip().replace('"', '')
            
            # 3. Post to Bluesky
            bsky.send_post(text=f"🌌 VELQA_CORE: {post_text}")
            print(f"✅ Hype post successful: {post_text}")
        else:
            print(f"❌ Groq Error: {res.text}")

    except Exception as e:
        print(f"❌ Worker error: {e}")

if __name__ == "__main__":
    run_once()
