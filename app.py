from flask import Flask, request, jsonify
from flask_cors import CORS
import os, requests, json
from groq import Groq

app = Flask(__name__)
CORS(app)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Helper: Website ka poora text nikalne ke liye
def get_site_content(url):
    try:
        # Jina Reader API: Simple and powerful for LLMs
        res = requests.get(f"https://r.jina.ai/{url}", timeout=10)
        return res.text[:4000] # Pehle 4000 characters kaafi hain
    except:
        return "Could not fetch content directly."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    target_url = data.get('url')
    content = get_site_content(target_url) # AB YE REAL DATA LAYEGA
    
    prompt = f"""
    Perform a DEEP SEO & AI AUDIT on this content:
    URL: {target_url}
    CONTENT: {content}
    
    Return ONLY JSON:
    {{
      "verdict": "Detailed 1-sentence verdict",
      "roast": "Brutal roast about their technical failures",
      "vulnerabilities": ["Critical issue 1", "Critical issue 2", "..."],
      "seo_score": 0-100
    }}
    """
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant", response_format={"type":"json_object"})
    return jsonify({"report": json.loads(chat.choices[0].message.content)})

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    target_url = data.get('url')
    biz_desc = data.get('business_description', 'Digital Entity')
    content = get_site_content(target_url)

    prompt = f"""
    Act as a GEO (Generative Engine Optimization) Expert.
    Optimize {target_url} for Perplexity/Gemini citing.
    Business: {biz_desc}
    Current Content: {content}

    Return ONLY JSON with:
    1. 'ai_bait': A 60-word 'Information Gain' paragraph. (Fact-heavy, direct answer style).
    2. 'schema_json': Professional JSON-LD for AI crawlers.
    3. 'geo_gaps': 3 things AI search engines want to see but are missing.
    4. 'platform_strategy': Specific titles for Dev.to/Hashnode to hijack niche authority.
    """
    chat = client.chat.completions.create(messages=[{"role":"user","content":prompt}], model="llama-3.1-8b-instant", response_format={"type":"json_object"})
    return jsonify({"plan": json.loads(chat.choices[0].message.content)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
