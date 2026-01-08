import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from groq import Groq

app = Flask(__name__)
CORS(app)

# Key Environment Variable se uthayega (Secure)
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY not found!")

client = Groq(api_key=GROQ_API_KEY)

def scrape_website(url):
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        return text[:4000] 
    except Exception as e:
        return None

@app.route('/', methods=['GET'])
def home():
    return "Velqa Brain is Active."

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "URL is required"}), 400

    site_content = scrape_website(url)
    
    if not site_content:
        return jsonify({"status": "ERROR", "message": "Could not scrape site. Ensure it's public."})

    prompt = f"""
    Analyze this website content:
    {site_content}

    Act as a strict AI Search Judge (Perplexity/Gemini). Answer these 3 questions:
    1. Does this brand appear in your pre-training data? (Yes/No)
    2. Is their value proposition clear to a machine? (Score 1-10)
    3. VERDICT: If a user asked "Best services for [Industry]", would you recommend this URL? (YES/NO)

    Return ONLY a JSON object (no markdown):
    {{
        "ai_recognition": "Recognized" or "Unknown",
        "score": "X/10",
        "verdict": "Your verdict here"
    }}
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            model="llama3-8b-8192",
            response_format={"type": "json_object"} 
        )
        result = chat_completion.choices[0].message.content
        return result # Ye directly JSON return karega
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
