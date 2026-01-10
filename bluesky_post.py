import requests
from datetime import datetime
import os

BSKY_HANDLE = "velqa.kryv.network"
BSKY_PASSWORD = os.environ.get("BSKY_PASS")
API_URL = "https://bsky.social/xrpc"

def upload_image(session, image_path):
    with open(image_path, 'rb') as f:
        img_data = f.read()
    
    headers = {
        "Authorization": f"Bearer {session['accessJwt']}",
        "Content-Type": "image/png"
    }
    resp = requests.post(f"{API_URL}/com.atproto.repo.uploadBlob", data=img_data, headers=headers)
    return resp.json().get('blob')

def post_to_bluesky(text, image_path=None):
    # 1. Session Create
    session = requests.post(
        f"{API_URL}/com.atproto.server.createSession",
        json={"identifier": BSKY_HANDLE, "password": BSKY_PASSWORD}
    ).json()
    
    # 2. Upload Image (if exists)
    embed = None
    if image_path:
        blob = upload_image(session, image_path)
        embed = {
            "$type": "app.bsky.embed.images",
            "images": [{"alt": "VELQA Audit Card", "image": blob}]
        }

    # 3. Create Post
    headers = {"Authorization": f"Bearer {session['accessJwt']}"}
    post_data = {
        "repo": session['did'],
        "collection": "app.bsky.feed.post",
        "record": {
            "text": text,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "$type": "app.bsky.feed.post",
            "embed": embed
        }
    }
    
    resp = requests.post(f"{API_URL}/com.atproto.repo.createRecord", json=post_data, headers=headers)
    return resp.json()
