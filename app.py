from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import scrape_site, get_ai_analysis
from database import add_to_index, is_verified, load_data

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def health_check():
    return "VELQA CORE ACTIVE"

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    content = scrape_site(url)
    if not content:
        return jsonify({"score": 0, "verdict": "Website unreachable. Check the URL."}), 400
    
    analysis = get_ai_analysis(content)
    return analysis

@app.route('/check-status/<path:url>')
def status(url):
    verified = is_verified(url)
    return jsonify({"verified": verified})

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    # PayPal subscription logic
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        # PayPal custom_id field contains the URL
        url = data['resource'].get('custom_id')
        if url:
            add_to_index(url)
            print(f"AUTO-INJECTED: {url}")
    return "OK", 200

@app.route('/ai-feed.json')
def ai_feed():
    return jsonify({"verified_entities": load_data()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
