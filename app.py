from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from engine import scrape_site, get_ai_analysis
from image_gen import generate_brand_card
from bluesky_post import post_to_bluesky
from database import add_to_index, load_data, supabase # database.py se supabase import kiya
from geo_logic import generate_seo_article

app = Flask(__name__)
CORS(app)

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    email = data.get('email')
    content = scrape_site(url)
    analysis = get_ai_analysis(content, url)
    if email and email == ADMIN_EMAIL:
        analysis['is_premium'] = True
    return jsonify(analysis)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id')
        if url:
            # 1. Generate SEO Article
            article = generate_seo_article(url)
            
            # 2. Save to Supabase with Article
            supabase.table("velqa_index").insert({
                "url": url, 
                "article": article,
                "status": "injected"
            }).execute()
            
            # 3. Social & Card
            analysis = get_ai_analysis("verified", url)
            card = generate_brand_card(url, analysis['score'], analysis['intelligence'])
            post_to_bluesky(f"Neural SEO Optimized: {url} has been boosted. View audit below.", card)
            
    return "OK", 200

@app.route('/ai-feed.json')
def ai_feed():
    # Supabase se latest 10 injections uthao
    res = supabase.table("velqa_index").select("*").order("id", desc=True).limit(10).execute()
    return jsonify({"entities": res.data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
