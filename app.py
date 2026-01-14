import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return "VELQA_ACTIVE", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        target_url = data.get('url')
        
        # Serper call with tighter timeout
        search_res = requests.post(
            "https://google.serper.dev/search",
            headers={'X-API-KEY': os.getenv("SERPER_API_KEY"), 'Content-Type': 'application/json'},
            json={"q": f"site:{target_url} SEO audit"},
            timeout=5
        )
        snippets = [item.get('snippet', '') for item in search_res.json().get('organic', [])[:2]]

        prompt = f"Analyze {target_url}. Context: {snippets}. Output ONLY JSON: {{'verdict': '...', 'roast': '...', 'vulnerabilities': [...]}}"
        
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192", # Using 8b instead of 70b for instant response
            response_format={"type": "json_object"}
        )
        
        return jsonify({"report": json.loads(chat.choices[0].message.content)})
    except Exception as e:
        return jsonify({"error": "KRYV_TIMEOUT"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv("PORT", 5000))
