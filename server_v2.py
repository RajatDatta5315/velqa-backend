import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from stealth_injector import generate_stealth_script
from core_engine import generate_neural_audit

app = Flask(__name__)
CORS(app)

# Global store for active audits
temp_store = {}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        domain = data.get('domain', '').strip().replace('https://', '').replace('http://', '')
        
        if not domain:
            return jsonify({"error": "Domain required"}), 400

        # Create Neural Audit
        result = generate_neural_audit(domain)
        site_id = result['site_id']
        temp_store[site_id] = result
        
        # Hamesha apne custom domain ka link bhejna
        return jsonify({
            "status": "Success",
            "script": f"https://velqa.kryv.network/api/v3/stealth.js?id={site_id}",
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/stealth.js', methods=['GET'])
def get_stealth_js():
    site_id = request.args.get('id')
    data = temp_store.get(site_id)
    
    # Agar data nahi hai, toh default demo data
    if not data:
        data = {"domain": "guest_node", "vulnerabilities": ["SCAN_PENDING"]}
        
    js = generate_stealth_script(data['domain'], data)
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/')
def home():
    return "VELQA NEURAL CORE ACTIVE: 3D ENGINE READY"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
