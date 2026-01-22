import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from stealth_injector import generate_stealth_script
from core_engine import generate_neural_audit
from bot_nexus import start_bot_engine

app = Flask(__name__)
CORS(app)

# Background Scheduler Start (Bluesky, Mastodon, Self-Ping)
if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
    start_bot_engine()

# Shared store (Simulating DB for Phase 2)
temp_store = {}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        domain = data.get('domain', '').strip().replace('https://', '').replace('http://', '')
        
        if not domain:
            return jsonify({"error": "Domain required"}), 400

        # Generate Audit Data
        result = generate_neural_audit(domain)
        site_id = result['site_id']
        temp_store[site_id] = result
        
        # SPACE_APP_URL should be like: https://velqa-velqa.hf.space
        base_url = os.getenv("SPACE_APP_URL", "http://localhost:7860")
        
        return jsonify({
            "status": "Success",
            "script": f"{base_url}/v3/stealth.js?id={site_id}",
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/stealth.js', methods=['GET'])
def get_stealth_js():
    site_id = request.args.get('id')
    data = temp_store.get(site_id)
    
    # Fallback for testing
    if not data:
        js = generate_stealth_script("demo.com", {"vulnerabilities": ["ID_NOT_FOUND"]})
    else:
        js = generate_stealth_script(data['domain'], data)
        
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/')
def home():
    return "VELQA NEURAL CORE: PHASE 2 ACTIVE (HUGGING FACE)"

if __name__ == "__main__":
    # Hugging Face mandatory port
    app.run(host="0.0.0.0", port=7860)
