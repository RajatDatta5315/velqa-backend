from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from engine import scrape_site, get_ai_analysis
from database import add_to_index, is_verified, load_data, save_data

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    content = scrape_site(url)
    analysis = get_ai_analysis(content, url)
    return analysis

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Logic for PayPal payment success
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id')
        if url:
            add_to_index(url)
            print(f"Neural Injection started for: {url}")
    return "OK", 200

@app.route('/ai-feed.json')
def ai_feed():
    return jsonify({"entities": load_data()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
