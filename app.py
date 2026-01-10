from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from engine import scrape_site, get_ai_analysis
from image_gen import generate_brand_card
from bluesky_post import post_to_bluesky
from database import add_to_index, load_data

app = Flask(__name__)
CORS(app)

# Secrets from Environment Variables
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "rajatdatta90000@gmail.com")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    email = data.get('email') # Coming from KRYV Login

    # 1. Scraping & Real Intelligence
    content = scrape_site(url)
    analysis = get_ai_analysis(content, url)
    
    # 2. Admin Logic: Free for you
    if email == ADMIN_EMAIL:
        analysis['is_premium'] = True
    
    return jsonify(analysis)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # PayPal Webhook: Fixing the 'back to main page' loop
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id')
        if url:
            # REAL INJECTION: Create Neural Manifest
            add_to_index(url)
            
            # TRIGGER GEO ARTICLE GENERATION (The Secret Sauce)
            # This would call a function to write/post an article automatically
            print(f"Neural Manifest Created & SEO Articles Queued for: {url}")
            
            # Social Update
            analysis = get_ai_analysis("verified", url)
            card = generate_brand_card(url, analysis['score'], analysis['intelligence'])
            post_to_bluesky(f"VERIFIED: {url} is now part of the KRYV Neural Network.", card)
            
    return "OK", 200

# KRYV SSO Integration Placeholder
@app.route('/auth/kryv', methods=['POST'])
def kryv_auth():
    # Integrate with your Supabase KRYV DB here
    token = request.json.get('token')
    return jsonify({"status": "authenticated", "user": "validated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
