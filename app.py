import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# SABSE IMPORTANT: Isse block nahi hoga
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

@app.route('/', methods=['GET'])
def health():
    return "VELQA_CORE_ONLINE", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Pre-flight requests ke liye (CORS fix)
        if request.method == 'OPTIONS':
            return '', 204
            
        data = request.get_json()
        target_url = data.get('url')

        # Logic remain same as previous version...
        search_url = "https://google.serper.dev/search"
        headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
        res = requests.post(search_url, headers=headers, json={"q": f"site:{target_url}"}, timeout=10)
        snippets = [item.get('snippet', '') for item in res.json().get('organic', [])[:2]]

        prompt = f"Analyze {target_url} for GEO. Context: {snippets}. Return JSON with 'verdict', 'roast', 'vulnerabilities'."
        
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        
        return jsonify({"report": json.loads(completion.choices[0].message.content)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
