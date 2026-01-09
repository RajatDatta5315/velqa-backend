import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from groq import Groq

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

def scrape_website(url):
    try:
        if not url.startswith('http'): url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=7)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)[:3000]
    except: return None

@app.route('/', methods=['GET'])
def home():
    return "VELQA CORE ACTIVE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    content = scrape_website(url)
    if not content: return jsonify({"error": "Unreachable"}), 400

    prompt = f"Analyze this site for AI Visibility: {content}. Return ONLY JSON with keys: 'ai_recognition' (Recognized/Unknown), 'score' (0-10), 'verdict' (1 sentence)."
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return chat.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate-fix', methods=['POST'])
def generate_fix():
    data = request.json
    url = data.get('url')
    # Simple logic to create a brand name from URL
    brand = url.split("//")[-1].split(".")[0].upper()
    
    # Premium Neural Graph Structure
    schema = {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": brand,
        "url": url,
        "description": "AI-Optimized Entity verified by VELQA Protocol.",
        "knowsAbout": ["Artificial Intelligence", "GEO", "Digital Transformation"],
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{url}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        }
    }
    return jsonify({"schema": schema})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
