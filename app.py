from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from engine import scrape_site, get_ai_analysis
from image_gen import generate_brand_card
from bluesky_post import post_to_bluesky
from database import add_to_index, load_data

app = Flask(__name__)
CORS(app)

# Security: Fetching from Render Environment Variables (Not hardcoded)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") 

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        url = data.get('url')
        email = data.get('email')

        content = scrape_site(url)
        analysis = get_ai_analysis(content, url)
        
        # Free access logic for you
        if email and email == ADMIN_EMAIL:
            analysis['is_premium'] = True
            
        return jsonify(analysis)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id')
        if url:
            add_to_index(url)
            # 8b model use kar rahe hain for higher rate limits (As you suggested)
            analysis = get_ai_analysis("verified_user", url)
            card = generate_brand_card(url, analysis['score'], analysis['intelligence'])
            post_to_bluesky(f"Protocol Activated for {url}. Neural nodes sync complete.", card)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
