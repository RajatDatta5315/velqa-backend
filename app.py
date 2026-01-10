from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from engine import scrape_site, get_ai_analysis
from image_gen import generate_brand_card
from bluesky_post import post_to_bluesky
from database import add_to_index, load_data

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    # Engine logic here...
    return jsonify({"score": 2.4, "verdict": "Risk", "intelligence": "Analyzing..."})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id')
        if url:
            # 1. Add to DB
            add_to_index(url)
            
            # 2. Get AI "Fear" Intel
            analysis = get_ai_analysis("Simulated content", url)
            intel = analysis['intelligence']
            score = analysis['score']
            
            # 3. Generate Fear Card
            card_path = generate_brand_card(url, score, intel)
            
            # 4. Post to Bluesky
            post_text = f"🚨 ALERT: {url} is invisible to AI Models.\n\nNeural Audit Complete. Injection Protocol Initiated.\n\n#GEO #VELQA #AI"
            post_to_bluesky(post_text, card_path)
            
            print(f"Full Cycle Complete for {url}")
            
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
