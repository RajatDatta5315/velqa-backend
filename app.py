import os, requests, json, base64, sys, traceback
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# --- SPY LOGGING UTILITY ---
def spy_log(msg, data=None):
    status = f"DEBUG_SPY: {msg}"
    if data: status += f" | DATA: {data}"
    print(status, file=sys.stderr)

try:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    mongo_client = MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=5000)
    db = mongo_client.velqa_db
    configs_col = db.site_configs
    spy_log("DATABASE_READY")
except Exception as e:
    spy_log("SETUP_ERROR", str(e))

@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        url = data.get('url')
        biz_desc = data.get('business_description')
        spy_log(f"STARTING_OPTIMIZE_FOR: {url}")

        # Jina Reader
        res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
        content = res.text[:3000]
        spy_log("CONTENT_FETCHED", f"Length: {len(content)}")

        # AI Prompt with Strict Control
        prompt = f"""
        Role: SEO/GEO Expert. Task: Optimize {url}.
        Context: {biz_desc}. 
        Content: {content}.
        Return ONLY valid JSON:
        {{
            "ai_bait": "short paragraph for AI",
            "schema_json": {{"@context": "https://schema.org", "@type": "Organization", "name": "..."}},
            "geo_gaps": ["gap1", "gap2"],
            "platform_strategy": ["strat1", "strat2"]
        }}
        """

        chat = client.chat.completions.create(
            messages=[{"role":"user","content":prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type":"json_object"}
        )
        
        raw_res = chat.choices[0].message.content
        spy_log("AI_RAW_RESPONSE", raw_res)
        result = json.loads(raw_res)

        site_id = base64.b64encode(url.encode()).decode()[:8].replace('=', '')
        
        # Save to Mongo
        configs_col.update_one(
            {"site_id": site_id},
            {"$set": {
                "url": url, 
                "ai_bait": result.get('ai_bait'), 
                "schema": result.get('schema_json'),
                "geo_gaps": result.get('geo_gaps'),
                "platform_strategy": result.get('platform_strategy')
            }},
            upsert=True
        )
        spy_log("DB_SYNC_COMPLETE", f"ID: {site_id}")

        return jsonify({"plan": result, "site_id": site_id, "spy_msg": "Injected Successfully"})

    except Exception as e:
        error_msg = traceback.format_exc()
        spy_log("CRITICAL_OPTIMIZE_ERROR", error_msg)
        return jsonify({"error": str(e), "trace": error_msg}), 500

@app.route('/v3/inject.js')
def inject_js():
    site_id = request.args.get('id')
    config = configs_col.find_one({"site_id": site_id})
    if not config: return "console.log('VELQA: Not Found');", 404
    
    js = f"""
    (function(){{
        console.log("VELQA_DEPLOYED: {site_id}");
        const b=document.createElement('div'); b.style.display='none'; b.innerText=`{config['ai_bait']}`;
        document.body.prepend(b);
        const s=document.createElement('script'); s.type='application/ld+json';
        s.text=JSON.stringify({json.dumps(config['schema'])});
        document.head.appendChild(s);
    }})();
    """
    return js, 200, {'Content-Type': 'application/javascript'}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
