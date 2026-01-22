import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from core_engine import generate_neural_audit # Purana logic use kar rahe hain
from stealth_injector import generate_stealth_script # Naya Logic
from bot_nexus import start_bot_engine # Naya Bot

app = Flask(__name__)
CORS(app)

# Start Background Bots (No more YAML!)
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    start_bot_engine()

# Fake DB (Replace with Mongo logic from app.py if needed, or keep simple)
temp_store = {}

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    domain = data.get('domain')
    
    # Generate Data
    result = generate_neural_audit(domain) # Core Engine se data
    
    # Store for script generation
    temp_store[result['site_id']] = result
    
    return jsonify({
        "status": "Success",
        "script": f"https://api.velqa.kryv.network/v3/stealth.js?id={result['site_id']}", # New URL
        "data": result
    })

@app.route('/v3/stealth.js', methods=['GET'])
def get_stealth_js():
    site_id = request.args.get('id')
    data = temp_store.get(site_id)
    
    # Fallback for Demo ID
    if site_id == "ID_DEMO" or not data:
        return generate_stealth_script("demo.com", {}), 200, {'Content-Type': 'application/javascript'}
        
    js = generate_stealth_script(data['domain'], data)
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/')
def home():
    return jsonify({"status": "VELQA PHASE 2: STEALTH & NEXUS ONLINE"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
