from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, json, base64
from groq import Groq
from pymongo import MongoClient
import sys

app = Flask(__name__)
CORS(app) # Sabhi origins allow kar diye hain

# --- SPY LOGGING ---
def spy_log(msg):
    print(f"DEBUG_SPY: {msg}", file=sys.stderr)

# Clients
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# MongoDB Spy Connection
try:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        spy_log("ERROR: MONGO_URI missing in Environment Variables!")
    mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    db = mongo_client.velqa_db
    configs_col = db.site_configs
    mongo_client.admin.command('ping')
    spy_log("DB_CONNECTED_SUCCESSFULLY")
except Exception as e:
    spy_log(f"DB_CONNECTION_FAILED: {str(e)}")

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        url = data.get('url')
        biz_desc = data.get('business_description')
        spy_log(f"OPTIMIZE_REQUEST_FOR: {url}")

        # Jina Reader Spy
        spy_log("FETCHING_FROM_JINA...")
        res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
        content = res.text[:4000]
        spy_log("JINA_FETCH_COMPLETE")
        
        # Groq AI Spy
        spy_log("CALLING_GROQ_AI...")
        prompt = f"GEO Optimize: {url}. Context: {biz_desc}. Content: {content}. Return ONLY JSON: {{'ai_bait': '...', 'schema_json': {{...}}}}"
        chat = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.1-8b-instant", 
            response_format={"type":"json_object"}
        )
        result = json.loads(chat.choices[0].message.content)
        spy_log("AI_GENERATION_SUCCESS")
        
        site_id = base64.b64encode(url.encode()).decode()[:8]
        
        # DB Push Spy
        spy_log(f"SAVING_TO_MONGO: SITE_ID_{site_id}")
        configs_col.update_one(
            {"site_id": site_id},
            {"$set": {"url": url, "ai_bait": result['ai_bait'], "schema": result['schema_json']}},
            upsert=True
        )
        spy_log("MONGO_SAVE_COMPLETE")

        return jsonify({"plan": result, "site_id": site_id})
    except Exception as e:
        spy_log(f"CRITICAL_OPTIMIZE_ERROR: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Health check for Koyeb
@app.route('/', methods=['GET'])
def health(): return "SPY_NODE_ACTIVE", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
