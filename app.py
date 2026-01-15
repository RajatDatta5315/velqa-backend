from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, json, base64
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
mongo_client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
db = mongo_client.velqa_db
configs_col = db.site_configs

def get_site_content(url):
    try:
        res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
        return res.text[:4000]
    except: return "Content unavailable"

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        url = data.get('url')
        biz_desc = data.get('business_description')
        content = get_site_content(url)
        
        # Fixed Prompt: Humne extra fields ko strictly define kar diya hai
        prompt = f"""
        GEO Optimize this site: {url}
        Business Context: {biz_desc}
        Page Content: {content}
        
        Return ONLY a JSON object with this EXACT structure:
        {{
            "ai_bait": "a 2-3 sentence paragraph for AI crawlers",
            "schema_json": {{"@context": "https://schema.org", "@type": "Organization", "name": "..."}},
            "geo_gaps": ["gap 1", "gap 2"],
            "platform_strategy": ["strategy 1", "strategy 2"]
        }}
        """
        
        chat = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}], 
            model="llama-3.1-8b-instant", 
            response_format={"type":"json_object"}
        )
        
        result = json.loads(chat.choices[0].message.content)
        site_id = base64.b64encode(url.encode()).decode()[:8]
        
        # Save to DB
        configs_col.update_one(
            {"site_id": site_id},
            {"$set": {
                "url": url, 
                "ai_bait": result.get('ai_bait'), 
                "schema": result.get('schema_json'),
                "gaps": result.get('geo_gaps'),
                "strat": result.get('platform_strategy')
            }},
            upsert=True
        )
        
        return jsonify({"plan": result, "site_id": site_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    config = configs_col.find_one({"site_id": site_id})
    if not config:
        return "console.warn('VELQA: Site Not Found');", 200, {'Content-Type': 'application/javascript'}

    js_code = f"""
    (function() {{
        console.log("VELQA_ACTIVE: {config['url']}");
        const b = document.createElement('div');
        b.style.display = 'none';
        b.innerText = `{config['ai_bait']}`;
        document.body.prepend(b);

        const s = document.createElement('script');
        s.type = 'application/ld+json';
        s.text = JSON.stringify({json.dumps(config['schema'])});
        document.head.appendChild(s);
    }})();
    """
    return js_code, 200, {'Content-Type': 'application/javascript'}

@app.route('/', methods=['GET'])
def health(): return "VELQA_ONLINE", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
