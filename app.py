from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
from groq import Groq

app = Flask(__name__)

# Pehle se zyada khula CORS setup
CORS(app, resources={r"/*": {
    "origins": "*",
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/', methods=['GET'])
def health():
    return "VELQA_ONLINE", 200

@app.route('/analyze', methods=['POST'])
def analyze():
    # Pre-flight OPTIONS request handle karne ke liye
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        target_url = data.get('url')
        
        # Search call
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
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        
        # Response headers manually set kar rahe hain for safety
        response = jsonify({"report": json.loads(chat.choices[0].message.content)})
        response.headers.add("Access-Control-Allow-Origin", "*")
        return response

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)
