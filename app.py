from flask import Flask, request, jsonify
from flask_cors import CORS
from engine import scrape_site, get_ai_analysis
from database import add_to_index, is_verified, load_data, save_data
from injection import generate_neural_metadata

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url')
    content = scrape_site(url)
    if not content:
        return jsonify({"score": 0, "verdict": "Website unreachable."}), 400
    return get_ai_analysis(content)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    # Logic for PayPal Subscription
    if data.get('event_type') == 'BILLING.SUBSCRIPTION.CREATED':
        url = data['resource'].get('custom_id') # Humne index.html mein set kiya tha
        if url:
            full_data = load_data()
            # Neural Injection happens here
            metadata = generate_neural_metadata(url)
            entry = {"url": url, "verified": True, "metadata": metadata}
            full_data.append(entry)
            save_data(full_data)
    return "OK", 200

@app.route('/ai-feed.json')
def ai_feed():
    return jsonify({"entities": load_data()})

@app.route('/check-status/<path:url>')
def check_status(url):
    return jsonify({"verified": is_verified(url)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
