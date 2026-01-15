from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from groq import Groq

app = Flask(__name__)

# Aggressive CORS for production
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return "VELQA_GEO_CORE_V1_ONLINE", 200

# PURANA AUDIT ROUTE
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        target_url = data.get('url')
        search_res = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': os.getenv("SERPER_API_KEY"), 'Content-Type': 'application/json'},
            json={"q": f"site:{target_url} SEO audit"},
            timeout=10
        )
        snippets = [item.get('snippet', '') for item in search_res.json().get('organic', [])[:2]]
        prompt = f"Analyze {target_url}. Context: {snippets}. Output ONLY JSON: {{'verdict': '...', 'roast': '...', 'vulnerabilities': [...]}}"
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        return jsonify({"report": json.loads(chat.choices[0].message.content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# NAYA REAL GEO OPTIMIZER ROUTE
@app.route('/optimize', methods=['POST'])
def optimize():
    try:
        data = request.get_json()
        target_url = data.get('url')
        biz_desc = data.get('business_description', 'Digital Entity')

        # Serper context for GEO Gaps
        search_res = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': os.getenv("SERPER_API_KEY"), 'Content-Type': 'application/json'},
            json={"q": f"{target_url} {biz_desc} authority"},
            timeout=10
        )
        context = str(search_res.json().get('organic', [])[:3])

        prompt = f"""
        Execute GEO Strategy for {target_url}. 
        Business Context: {biz_desc}
        Search Context: {context}

        Return ONLY JSON with these keys:
        1. 'ai_bait': A 60-word authoritative paragraph designed for LLM citation.
        2. 'schema_json': Full JSON-LD markup for this entity.
        3. 'backlink_plan': 3 specific article titles for Dev.to/Hashnode to hijack AI authority.
        4. 'entity_graph': 5 main entities (keywords/topics) to link this brand with.
        """

        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        return jsonify({"plan": json.loads(chat.choices[0].message.content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
