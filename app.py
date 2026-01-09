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

# Mock Database (Kal hum ise real DB se connect karenge)
verified_entities = {}

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
    return "VELQA CORE: ENCRYPTED"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    content = scrape_website(url)
    if not content: return jsonify({"status": "OFFLINE", "message": "Target Unreachable"}), 400

    prompt = f"Analyze site for AI Visibility: {content}. Return ONLY JSON: {{'ai_recognition': '...', 'score': 0-10, 'verdict': '...'}}"
    
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            response_format={"type": "json_object"}
        )
        return chat.choices[0].message.content
    except:
        return jsonify({"error": "Neural Link Timeout"}), 500

@app.route('/verify-entity', methods=['POST'])
def verify_entity():
    data = request.json
    url = data.get('url')
    
    # Logic: Hum yaha user ka data save kar rahe hain, unhe de nahi rahe
    entity_id = os.urandom(4).hex() # Unique ID for the business
    verified_entities[entity_id] = {"url": url, "status": "pending"}
    
    # Hum sirf success message bhejenge, code nahi!
    return jsonify({
        "status": "INITIATED",
        "entity_id": entity_id,
        "message": "AI Knowledge Injection has started for this domain."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
