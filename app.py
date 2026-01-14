import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)

# CORS FIX: Sab origins ko allow kar rahe hain taaki Vercel se connection na toote
CORS(app, resources={r"/*": {"origins": "*"}})

# Security: Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def get_ai_search_visibility(url):
    """Real-time scan using Serper.dev"""
    search_url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": f"site:{url} or AI visibility analysis for {url}"
    })
    headers = {
      'X-API-KEY': SERPER_API_KEY,
      'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", search_url, headers=headers, data=payload, timeout=10)
        return response.json().get('organic', [])
    except:
        return []

# Health Check Route (Render ko jagane ke liye)
@app.route('/', methods=['GET'])
def health():
    return jsonify({"status": "VELQA Neural Engine Online", "network": "KRYV"}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        target_url = data.get('url')

        if not target_url:
            return jsonify({"error": "Target URL required"}), 400

        # Step 1: Search Data
        raw_data = get_ai_search_visibility(target_url)
        snippets = [item.get('snippet', '') for item in raw_data[:2]]

        # Step 2: VELQA Brutal Logic
        prompt = f"""
        Analyze this target for GEO (Generative Engine Optimization): {target_url}
        Context found: {snippets}
        
        Identity: You are the VELQA Neural Engine, the core of the KRYV Network. 
        Tone: High-end, Brutal, Tech-Obsessed.
        
        Return a STRICT JSON object with these keys:
        'verdict': (One word: ELITE, VULNERABLE, or OBSOLETE)
        'roast': (Brutal 1-sentence critique)
        'vulnerabilities': (List of 3 specific GEO injections)
        """

        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are VELQA. You only output valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        
        ai_response = json.loads(completion.choices[0].message.content)
        return jsonify({"report": ai_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
