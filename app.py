import os
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# Security: Environment Variables se keys uthayega
# Render ke Dashboard pe jaakar Settings -> Env Vars mein ye keys daal dena
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def get_ai_search_visibility(url):
    """Real-time scan using Serper.dev"""
    search_url = "https://google.serper.dev/search"
    payload = json.dumps({
      "q": f"site:{url} or AI reviews of {url}"
    })
    headers = {
      'X-API-KEY': SERPER_API_KEY,
      'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", search_url, headers=headers, data=payload)
        return response.json().get('organic', [])
    except:
        return []

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({"error": "No URL provided"}), 400

    # Step 1: Get Real Search Data
    raw_data = get_ai_search_visibility(target_url)
    snippets = [item.get('snippet', '') for item in raw_data[:2]]

    # Step 2: AI Process with Llama-3
    prompt = f"""
    Analyze this target for GEO (Generative Engine Optimization): {target_url}
    Context found: {snippets}
    
    You are VELQA, a brutal AI engine. 
    Return a STRICT JSON object with:
    'verdict': (One word)
    'roast': (Short brutal critique)
    'vulnerabilities': (List of 3 specific GEO gaps)
    """

    try:
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a specialized GEO audit tool. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )
        
        # Parse output
        ai_response = json.loads(completion.choices[0].message.content)
        return jsonify({"report": ai_response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
