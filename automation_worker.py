import os
import time
from pymongo import MongoClient
from atproto import Client, models

# Configuration
MONGO_URI = os.getenv("MONGO_URI")
BSKY_HANDLE = os.getenv("BSKY_HANDLE") # e.g. velqa.bsky.social
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

client = MongoClient(MONGO_URI)
db = client['velqa_db']
optimizations = db['optimizations']

def post_to_bluesky():
    try:
        bsky = Client()
        bsky.login(BSKY_HANDLE, BSKY_PASSWORD)
        print("Bluesky Uplink Established.")

        while True:
            # Look for new records that haven't been posted
            new_job = optimizations.find_one({"posted_to_social": {"$exists": False}})
            
            if new_job:
                # Craft a value-driven post (No URL leak)
                bait = new_job.get('plan', {}).get('ai_bait', 'Advanced Intelligence')
                # Sirf pehle 100 characters taaki post clean rahe
                short_bait = (bait[:100] + '...') if len(bait) > 100 else bait
                
                post_text = f"🎯 Neural Optimization Sync: \n\nTarget niche analyzed. Gaps identified. \n\nGenerated Bait Pattern: \"{short_bait}\"\n\n#GEO #VELQA #SearchAI"
                
                bsky.send_post(text=post_text)
                
                # Mark as posted so we don't spam
                optimizations.update_one({"_id": new_job["_id"]}, {"$set": {"posted_to_social": True}})
                print(f"Posted: {new_job['_id']}")
            
            time.sleep(60) # Har 1 minute mein check karega
    except Exception as e:
        print(f"Worker Error: {e}")
        time.sleep(300) # Error pe 5 min wait

if __name__ == "__main__":
    post_to_bluesky()
