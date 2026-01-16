import os
import random
import time
import requests
from atproto import Client, models

# Groq Config
AI_API_URL = "https://api.groq.com/openai/v1/chat/completions"
AI_MODEL = "llama-3.3-70b-versatile" 

def get_smart_ai_reply(post_text, author_handle):
    api_key = os.getenv("AI_API_KEY")
    if not api_key: return "Interesting perspective on this!"

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    # Context-aware Prompting
    prompt = f"""
    You are a smart, slightly edgy tech enthusiast on Bluesky. 
    User @{author_handle} posted: "{post_text}"
    
    Task: Write a contextual, 1-sentence reply.
    - If it's about AI, add a smart thought.
    - If it's about SEO, mention the future of search.
    - If it's general tech, be supportive.
    - Tone: Casual, NO hashtags, NO corporate speak, NO "Great post!". 
    - Max 15 words.
    """

    payload = {
        "model": AI_MODEL,
        "messages": [{"role": "system", "content": "You are a human-like tech expert."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.8
    }

    try:
        res = requests.post(AI_API_URL, json=payload, headers=headers)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content'].strip().replace('"', '')
    except:
        return "Spot on. The ecosystem is changing fast."
    return "Solid point."

def run_smart_comments():
    try:
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        
        # Tech keywords for context
        topics = ["SEO news", "AI agents", "OpenAI", "Web3 development"]
        query = random.choice(topics)
        
        search = bsky.app.bsky.feed.search_posts(params=models.AppBskyFeedSearchPosts.Params(q=query, limit=5))

        for post in search.posts:
            # Skip if it's already a reply to avoid loops
            if post.record.reply: continue

            # Generate Smart Reply
            reply_text = get_smart_ai_reply(post.record.text, post.author.handle)
            
            try:
                bsky.send_post(
                    text=reply_text,
                    reply_to=models.AppBskyFeedPost.ReplyRef(
                        parent=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri),
                        root=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri)
                    )
                )
                print(f"✅ Replied to @{post.author.handle}: {reply_text}")
                time.sleep(15) # Safety delay
            except Exception as e:
                print(f"Error: {e}")
                
    except Exception as e:
        print(f"Bot Fail: {e}")

if __name__ == "__main__":
    run_smart_comments()
