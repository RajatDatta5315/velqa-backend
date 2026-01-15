import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
# Koyeb compatibility ke liye CORS ko loose rakha hai
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# API Keys from Koyeb Env Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "VELQA_CORE_ACTIVE", "network": "KRYV"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        target_url = data.get('url')
        
        if not target_url:
            return jsonify({"error": "No URL provided"}), 400

        # Serper Search
        search_res = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'},
            json={"q": f"site:{target_url} SEO"},
            timeout=8
        )
        snippets = [item.get('snippet', '') for item in search_res.json().get('organic', [])[:2]]

        prompt = f"Analyze {target_url} for GEO. Context: {snippets}. Output ONLY JSON: {{'verdict': '...', 'roast': '...', 'vulnerabilities': [...]}}"
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        return jsonify({"report": json.loads(chat.choices[0].message.content)})
    except Exception as e:
        return jsonify({"error": "KRYV_UPLINK_TIMEOUT"}), 500

if __name__ == '__main__':
    # Koyeb requires 8000 port by default
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
