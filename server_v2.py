import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from stealth_injector import generate_stealth_script
from core_engine import generate_neural_audit

app = Flask(__name__)
# Sabse zaruri: CORS allow karna taaki Frontend (Vercel) se request block na ho
CORS(app, resources={r"/*": {"origins": "*"}})

temp_store = {}

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        if not data or 'domain' not in data:
            return jsonify({"error": "No domain provided"}), 400
            
        domain = data.get('domain', '').strip().replace('https://', '').replace('http://', '')
        
        # Engine run karo
        result = generate_neural_audit(domain)
        site_id = result['site_id']
        temp_store[site_id] = result
        
        # Ye link user ko dashboard pe dikhega
        script_url = f"https://velqa.kryv.network/api/v3/stealth.js?id={site_id}"
        
        return jsonify({
            "status": "Success",
            "script": script_url,
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/stealth.js', methods=['GET'])
def get_stealth_js():
    site_id = request.args.get('id')
    data = temp_store.get(site_id)
    
    if not data:
        data = {"domain": "unknown", "vulnerabilities": ["INITIALIZING"]}
        
    js = generate_stealth_script(data['domain'], data)
    return js, 200, {'Content-Type': 'application/javascript'}

@app.route('/health')
def health(): return "VELQA_ONLINE"

if __name__ == "__main__":
    # Back4app/Render automatically port allocate karte hain
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
