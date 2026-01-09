from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import scrape_site, get_ai_analysis
from database import add_to_index, is_verified, injected_entities

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    url = request.json.get('url')
    content = scrape_site(url)
    if not content: return jsonify({"error": "Unreachable"}), 400
    return get_ai_analysis(content)

@app.route('/check-status/<path:url>')
def status(url):
    return jsonify({"verified": is_verified(url)})

# Global AI Feed for Search Engines/AI Crawlers
@app.route('/ai-feed.json')
def ai_feed():
    return jsonify({"verified_entities": injected_entities})

# Webhook for PayPal
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    # Logic: Subscription approve hote hi inject
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        # Yahan hum subscription metadata se URL nikalenge
        pass 
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
