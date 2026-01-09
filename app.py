import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import time

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# Database to store paid entities
injected_entities = []

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    # Analysis logic (Same as before)
    prompt = f"Analyze site for AI Visibility: {url}. Return ONLY JSON: {{'ai_recognition': '...', 'score': 0-10, 'verdict': '...'}}"
    chat = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192", response_format={"type": "json_object"})
    return chat.choices[0].message.content

# --- AUTOMATIC INJECTION ROUTE ---
@app.route('/paypal-webhook', methods=['POST'])
def paypal_webhook():
    data = request.json
    # PayPal sends payment status
    if data.get('event_type') == 'PAYMENT.SALE.COMPLETED':
        user_url = data['resource']['custom_id'] # Hum custom_id mein URL bhejenge
        
        # AUTOMATIC INJECTION LOGIC
        new_entry = {
            "url": user_url,
            "timestamp": time.time(),
            "status": "INJECTED",
            "layer": "Neural-L1"
        }
        injected_entities.append(new_entry)
        print(f"AUTO-INJECTED: {user_url}")
        
    return jsonify({"status": "received"}), 200

# Route to check if a URL is injected
@app.route('/check-status/<path:url>')
def check_status(url):
    is_verified = any(e['url'] == url for e in injected_entities)
    return jsonify({"verified": is_verified})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
