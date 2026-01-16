import os
from atproto import Client, models

def run_smart_comments():
    bsky = Client()
    bsky.login(os.getenv("BSKY_HANDLE"), os.getenv("BSKY_PASSWORD"))
    
    # 1. Search for trending tech posts
    params = models.AppBskyFeedSearchPosts.Params(q="AI SEO Web3", limit=5)
    search_results = bsky.app.bsky.feed.search_posts(params)
    
    comments = [
        "This is a great insight on AI trends!",
        "Love how the ecosystem is evolving. Great post.",
        "Totally agree with your take on SEO gaps.",
        "Interesting perspective, thanks for sharing!",
        "Spot on! The future of neural networks is exciting."
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
            print(f"Commented on {post.author.handle}")
        except:
            continue

if __name__ == "__main__":
    run_smart_comments()
