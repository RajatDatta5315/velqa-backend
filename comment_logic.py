import os
import random
import time
import requests
from atproto import Client, models

# --- CONFIGURATION ---
# Groq API URL
AI_API_URL = "https://api.groq.com/openai/v1/chat/completions"
# Model ID: Using Llama 3 70B for high intelligence & speed
AI_MODEL = "llama3-70b-8192" 

def get_ai_comment(post_text):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        print("⚠️ AI_API_KEY missing. Using fallback.")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # Prompt engineering for "Human-like" non-salesy interaction
    system_prompt = (
        "You are a casual, tech-savvy user on a social network. "
        "Read the provided post and write a SINGLE short sentence (under 15 words) as a reply. "
        "Tone: Friendly, appreciative, or slightly witty. "
        "Rules: NO hashtags. NO sales pitches. NO robotic phrases like 'Great post'. "
        "Just talk like a real human developer or enthusiast."
    )

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Post content: {post_text}"}
        ],
        "temperature": 0.8, # Thoda creative banaya hai
        "max_tokens": 50
    }

    try:
        response = requests.post(AI_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            comment = response.json()['choices'][0]['message']['content'].strip()
            # Clean up quotes if AI adds them
            return comment.replace('"', '').replace("'", "")
    except Exception as e:
        print(f"❌ Groq API Error: {e}")
    
    return None

def run_smart_comments():
    try:
        print("--- STARTING NEURAL COMMENT ROUTINE ---")
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        
        # In topics par baat karega
        topics = ["AI Agents", "SEO", "Web3 Dev", "Startup Life", "Coding"]
        query = random.choice(topics)
        print(f"🔍 Searching topic: {query}")
        
        # Search recent posts
        search_results = bsky.app.bsky.feed.search_posts(params=models.AppBskyFeedSearchPosts.Params(q=query, limit=5))

        count = 0
        for post in search_results.posts:
            if count >= 2: break # Ek baar mein max 2 comments (Spam se bachne ke liye)

            # Skip replies, only comment on root posts
            if post.record.reply: continue

            # Generate AI Comment
            ai_reply = get_ai_comment(post.record.text)
            
            if ai_reply:
                try:
                    bsky.send_post(
                        text=ai_reply,
                        reply_to=models.AppBskyFeedPost.ReplyRef(
                            parent=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri),
                            root=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri)
                        )
                    )
                    print(f"✅ Commented on @{post.author.handle}: {ai_reply}")
                    count += 1
                    time.sleep(10) # Thoda wait karo taaki bot na lage
                except Exception as e:
                    print(f"⚠️ Post Failed: {e}")
            else:
                print("⏩ AI returned nothing, skipping.")
                
    except Exception as e:
        print(f"❌ Automation Error: {e}")

if __name__ == "__main__":
    run_smart_comments()
