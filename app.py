from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from groq import Groq

app = Flask(__name__)

# Strict CORS for production
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return "VELQA_CORE_V3_ONLINE", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        target_url = data.get('url')
        
        if not target_url:
            return jsonify({"error": "TARGET_URL_MISSING"}), 400

        # Serper SEO Context
        search_res = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': os.getenv("SERPER_API_KEY"), 'Content-Type': 'application/json'},
            json={"q": f"site:{target_url} SEO weaknesses"},
            timeout=10
        )
        
        snippets = [item.get('snippet', '') for item in search_res.json().get('organic', [])[:2]]
        
        # MODEL UPDATED TO llama-3.1-8b-instant
        prompt = f"Analyze {target_url}. Context: {snippets}. Output ONLY JSON: {{'verdict': '...', 'roast': '...', 'vulnerabilities': [...]}}"
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}
        )
        
        return jsonify({"report": json.loads(chat.choices[0].message.content)})

    except Exception as e:
        print(f"CRITICAL_EXCEPTION: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
