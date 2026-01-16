import os, requests, random, time
from pymongo import MongoClient
from atproto import Client

def post_to_bluesky():
    # Loop to prevent immediate exit
    while True:
        try:
            bsky = Client()
            bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
            
            # AI logic for main posts
            topics = ["Future of AI SEO", "GEO Optimization", "Neural Web Trends"]
            prompt = f"Write a professional but mysterious 1-sentence hype post about {random.choice(topics)}."
            
            # Groq Call for Post content
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}]}
            )
            post_text = res.json()['choices'][0]['message']['content'].strip()

            bsky.send_post(text=f"🌌 VELQA NEURAL: {post_text}")
            print("Main post successful")
            
            time.sleep(14400) # Wait 4 hours for next post
        except Exception as e:
            print(f"Worker error: {e}")
            time.sleep(300)
