import os
import random
import requests
from atproto import Client, models

# AI Configuration (Uses Groq or OpenAI structure)
AI_API_URL = "https://api.groq.com/openai/v1/chat/completions" # Example for Groq
# Agar OpenAI use karna hai to: "https://api.openai.com/v1/chat/completions"

def generate_ai_comment(post_text):
    api_key = os.getenv("AI_API_KEY")
    if not api_key:
        return "Great insight! Thanks for sharing." # Fallback if no key

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Prompt for the AI
    payload = {
        "model": "llama3-8b-8192", # Or "gpt-4o-mini" for OpenAI
        "messages": [
            {
                "role": "system", 
                "content": "You are a tech-savvy user on Bluesky. Read the post and write a very short (under 20 words), casual, friendly, and non-salesy comment. Agree with them or add value. Do not use hashtags. Do not sound like a bot."
            },
            {
                "role": "user", 
                "content": f"Post content: {post_text}"
            }
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(AI_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"AI Error: {e}")
    
    return "Solid point. Following this closely." # Fallback

def run_smart_comments():
    try:
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        
        topics = ["AI Agents", "SEO Tips", "ReactJS", "IndieHacker"]
        query = random.choice(topics)
        
        # Search recent posts
        search_results = bsky.app.bsky.feed.search_posts(params=models.AppBskyFeedSearchPosts.Params(q=query, limit=3))

        for post in search_results.posts:
            # Generate AI Comment based on THEIR post content
            comment_text = generate_ai_comment(post.record.text)
            
            try:
                bsky.send_post(
                    text=comment_text,
                    reply_to=models.AppBskyFeedPost.ReplyRef(
                        parent=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri),
                        root=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri)
                    )
                )
                print(f"AI Commented on {post.author.handle}: {comment_text}")
            except Exception as e:
                print(f"Skipped post: {e}")
                
    except Exception as e:
        print(f"Bot Error: {e}")

if __name__ == "__main__":
    run_smart_comments()
