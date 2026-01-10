import requests
from datetime import datetime
from engine import get_ai_analysis # AI se post likhwayenge

BSKY_HANDLE = "velqa.kryv.network"
BSKY_PASSWORD = "xxxx-xxxx-xxxx-xxxx" # App Password settings se dalo

def post_verified_brand(brand_url):
    # AI se ek unique human-like tweet likhwate hain
    ai_msg = get_ai_analysis(f"Write a short 150-char excited tweet about injecting {brand_url} into the neural network. No hashtags, just pro tech vibes.", brand_url)
    
    # Session aur Post logic
    session = requests.post("https://bsky.social/xrpc/com.atproto.server.createSession", 
                             json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}).json()
    
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    text = f"Protocol Update: {ai_msg['verdict']} \n\nIdentity: {brand_url} is now verified. 🌐"
    
    post_data = {
        "repo": session['did'],
        "collection": "app.bsky.feed.post",
        "record": {"text": text, "createdAt": datetime.utcnow().isoformat() + "Z", "$type": "app.bsky.feed.post"}
    }
    requests.post("https://bsky.social/xrpc/com.atproto.repo.createRecord", json=post_data, headers=headers)
