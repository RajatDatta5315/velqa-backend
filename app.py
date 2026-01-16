import os
import threading
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from automation_worker import post_to_bluesky  # Background worker import

app = Flask(__name__)
CORS(app)

# Database Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['velqa_db']
optimizations = db['optimizations']

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    domain = data.get('domain')
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"
    
    # Placeholder for AI Logic
    result = {
        "domain": domain,
        "site_id": site_id,
        "plan": {
            "ai_bait": f"Neural intelligence update for {domain}. Optimized for high-intent search patterns.",
            "seo_strategy": {"title": f"VELQA | {domain} Optimized"}
        },
        "timestamp": datetime.utcnow()
    }
    
    optimizations.insert_one(result)
    
    # Return Script Link for Trial
    script_url = f"https://{request.host}/v3/inject.js?id={site_id}"
    return jsonify({"status": "Success", "script": script_url, "data": result})

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    # Fetch data from DB
    data = optimizations.find_one({"site_id": site_id})
    
    if data:
        title = data['plan']['seo_strategy']['title']
        bait = data['plan']['ai_bait']
        
        # JS code that runs on user's browser
        js_content = f"""
        console.log("VELQA: Page Autonomously Optimized");
        document.title = "{title}";
        let meta = document.createElement('meta');
        meta.name = "description";
        meta.content = "{bait}";
        document.getElementsByTagName('head')[0].appendChild(meta);
        """
        return js_content, 200, {'Content-Type': 'application/javascript'}
    
    return "console.log('VELQA: Invalid ID');", 404

@app.route('/')
def home():
    return jsonify({"status": "VELQA NEURAL ONLINE", "worker": "ACTIVE"})

if __name__ == "__main__":
    # Start worker in a separate thread (Koyeb Free Tier Hack)
    threading.Thread(target=post_to_bluesky, daemon=True).start()
    
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
