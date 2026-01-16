import os
import time
import random
from pymongo import MongoClient
from atproto import Client, models

# Configuration
MONGO_URI = os.getenv("MONGO_URI")
BSKY_HANDLE = os.getenv("BSKY_HANDLE")
BSKY_PASSWORD = os.getenv("BSKY_PASSWORD")

client = MongoClient(MONGO_URI)
db = client['velqa_db']
optimizations = db['optimizations']

def post_to_bluesky():
    try:
        bsky = Client()
        bsky.login(BSKY_HANDLE, BSKY_PASSWORD)
        print("--- VELQA BLUESKY UPLINK ACTIVE ---")

        while True:
            # 1. Post New Optimizations (Social Proof)
            new_job = optimizations.find_one({"posted_to_social": {"$ne": True}})
            if new_job:
                bait = new_job.get('plan', {}).get('ai_bait', 'Neural Intelligence Update')
                short_bait = (bait[:120] + '...') if len(bait) > 120 else bait
                post_text = f"🎯 Neural Sync: \n\nNew domain optimized for AI search gaps. \n\nPattern: \"{short_bait}\"\n\n#GEO #VELQA #BuildInPublic"
                
                try:
                    bsky.send_post(text=post_text)
                    optimizations.update_one({"_id": new_job["_id"]}, {"$set": {"posted_to_social": True}})
                    print(f"Social Proof Posted for {new_job.get('domain')}")
                except Exception as e:
                    print(f"Post Error: {e}")

            # 2. Daily Routine (Placeholder for 3 posts & 30 comments)
            # Yahan hum logic add karenge jab server stable ho jayega
            
            time.sleep(60) # Har minute check karo
    except Exception as e:
        print(f"Worker Master Error: {e}")
        time.sleep(300)

if __name__ == "__main__":
    post_to_bluesky()
