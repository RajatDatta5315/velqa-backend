import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq

app = Flask(__name__)
CORS(app)

# CONFIGURATION
# Bhai, in dono ki API Keys apne environment variables mein ya yaha string mein daal dena
GROQ_API_KEY = "TERI_GROQ_API_KEY"
SERPER_API_KEY = "TERI_SERPER_API_KEY"

client = Groq(api_key=GROQ_API_KEY)

def get_ai_search_visibility(url):
    """Checks how AI search engines like Perplexity or Gemini see the site."""
    search_url = "https://google.serper.dev/search"
    # Hum search kar rahe hain ki AI sources mein is URL ka kitna zikr hai
    payload = {"q": f"site:{url} source:perplexity OR source:searchgpt OR source:gemini"}
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(search_url, headers=headers, json=payload)
        return response.json().get('organic', [])
    except Exception as e:
        return []

@app.route('/analyze', methods=['POST'])
def analyze_geo():
    data = request.json
    target_url = data.get('url')

    if not target_url:
        return jsonify({"error": "URL is required"}), 400

    # 1. Asli Data Fetch karna (Serper API)
    visibility_data = get_ai_search_visibility(target_url)
    
    # Snippets nikaalna taaki AI ko context mile
    snippets = [item.get('snippet', '') for item in visibility_data[:3]]

    # 2. Brutal GEO Audit Prompt (Jo tune nikala tha)
    prompt = f"""
    Perform a Brutal GEO (Generative Engine Optimization) Audit for the website: {target_url}
    Context from AI Search Engines: {snippets}

    Your personality: A high-end Mercedes-Benz Engineer who hates low-quality web architecture.

    Strict Tasks:
    1. Identify 'Content Gaps' why AI models like Perplexity aren't citing this site enough.
    2. Suggest 3 'Neural Injections': Specific FAQ schema, bulleted stats, or semantic structures.
    3. Give a 'Brutal Verdict' on the site's future in an AI-first world.

    Return the response in STRICT JSON format with these exact keys:
    'verdict', 'roast', 'vulnerabilities', 'action_plan'.
    """

    try:
        # 3. Llama-3 (Groq) se Analysis karwana
        completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are VELQA's Core Neural Engine. You speak in high-tech, brutal, and precise terms."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-70b-8192",
            response_format={"type": "json_object"}
        )

        analysis_result = completion.choices[0].message.content
        # JSON string ko parse karke bhej rahe hain
        import json
        return jsonify({"report": json.loads(analysis_result)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Production mein host '0.0.0.0' hona chahiye
    app.run(host='0.0.0.0', port=5000)
