import os
import random
from atproto import Client, models

def run_smart_comments():
    try:
        bsky = Client()
        bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
        
        # Keywords to look for
        topics = ["AI SEO", "Digital Marketing", "Neural Networks", "SEO strategy"]
        query = random.choice(topics)
        
        # Search for recent posts
        search_results = bsky.app.bsky.feed.search_posts(params=models.AppBskyFeedSearchPosts.Params(q=query, limit=5))
        
        comments = [
            "This is a solid take on the current shift in search algorithms.",
            "Really insightful perspective. The gap between AI and human content is shrinking.",
            "Great points! Neural optimization is becoming the next big frontier.",
            "Interesting. Thanks for sharing this value!",
            "Spot on. Optimization today is more about intent than keywords."
        ]

        for post in search_results.posts:
            try:
                bsky.send_post(
                    text=random.choice(comments),
                    reply_to=models.AppBskyFeedPost.ReplyRef(
                        parent=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri),
                        root=models.ComAtprotoRepoStrongRef.Main(cid=post.cid, uri=post.uri)
                    )
                )
                print(f"Successfully commented on {post.author.handle}'s post.")
            except Exception as e:
                print(f"Failed to reply: {e}")
                continue
                
    except Exception as e:
        print(f"Automation Master Error: {e}")

if __name__ == "__main__":
    run_smart_comments()
