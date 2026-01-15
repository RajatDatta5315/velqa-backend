from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, json, base64
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Setup
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
mongo_client = MongoClient(os.getenv("MONGO_URI"))
db = mongo_client.velqa_db
stats_col = db.site_configs

# --- MODULAR FUNCTIONS ---

def get_site_content(url):
    try:
        res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
        return res.text[:4000]
    except: return "Content unavailable"

# --- ROUTES ---

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    content = get_site_content(data.get('url'))
    prompt = f"Audit this: {content}. Return ONLY JSON: {{'verdict': '...', 'roast': '...', 'vulnerabilities': []}}"
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant", response_format={"type":"json_object"})
    return jsonify({"report": json.loads(chat.choices[0].message.content)})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    url = data.get('url')
    biz_desc = data.get('business_description')
    content = get_site_content(url)
    
    prompt = f"GEO Optimize: {url}. Context: {biz_desc}. Content: {content}. Return JSON: {{'ai_bait': '...', 'schema_json': {{...}}}}"
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant", response_format={"type":"json_object"})
    
    result = json.loads(chat.choices[0].message.content)
    
    # SAVE TO MONGODB (The Secret Key for Injection)
    site_id = base64.b64encode(url.encode()).decode()[:8]
    stats_col.update_one(
        {"site_id": site_id},
        {"$set": {"url": url, "ai_bait": result['ai_bait'], "schema": result['schema_json']}},
        upsert=True
    )
    
    return jsonify({"plan": result, "site_id": site_id})

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    config = stats_col.find_one({"site_id": site_id})
    
    if not config:
        return "console.error('VELQA: Invalid ID');", 200, {'Content-Type': 'application/javascript'}

    # DOM Manipulation Logic
    js_code = f"""
    (function() {{
        console.log("VELQA_SHIELD_ACTIVE for {config['url']}");
        
        // Inject AI Bait (Hidden)
        const bait = document.createElement('div');
        bait.style.display = 'none';
        bait.id = 'velqa-gen-bait';
        bait.innerText = `{config['ai_bait']}`;
        document.body.prepend(bait);

        // Inject Schema
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.text = JSON.stringify({json.dumps(config['schema'])});
        document.head.appendChild(script);
    }})();
    """
    return js_code, 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
