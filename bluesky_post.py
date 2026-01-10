import requests
from datetime import datetime

# Bluesky API Details
BSKY_HANDLE = "velqa.kryv.network" # Tera verified handle
BSKY_PASSWORD = "xxxx-xxxx-xxxx-xxxx" # Settings -> App Passwords mein jaake banao
API_URL = "https://bsky.social/xrpc"

def get_session():
    resp = requests.post(
        f"{API_URL}/com.atproto.server.createSession",
        json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}
    )
    return resp.json()

def post_to_bluesky(text):
    session = get_session()
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    
    post_data = {
        "repo": session['did'],
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "$type": "app.bsky.feed.post"
        }
    }
    
    resp = requests.post(f"{API_URL}/com.atproto.repo.createRecord", json=post_data, headers=headers)
    return resp.json()

# Example: post_to_bluesky("Neural Injection active for tesla.com 🚀 #VELQA #GEO")
