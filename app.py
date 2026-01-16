import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from core_engine import generate_neural_audit

app = Flask(__name__)
CORS(app)

# MongoDB Setup
try:
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client['velqa_db']
    optimizations = db['optimizations']
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        domain = data.get('domain')
        
        if not domain:
            return jsonify({"error": "Domain is required"}), 400

        # Generate Detailed Audit
        result = generate_neural_audit(domain)
        
        # Save to Database
        optimizations.update_one(
            {"domain": domain}, 
            {"$set": result}, 
            upsert=True
        )
        
        # Response for Portal.tsx
        return jsonify({
            "status": "Success",
            "script": f"https://api.velqa.kryv.network/v3/inject.js?id={result['site_id']}",
            "data": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    data = optimizations.find_one({"site_id": site_id})
    
    if data:
        # Injection logic: Updates Title and Logs Meta
        strategy_title = data['plan']['seo_strategy']['title']
        js_content = f"""
        console.log('VELQA_NEURAL_ACTIVE: {site_id}');
        document.title = '{strategy_title}';
        """
        return js_content, 200, {'Content-Type': 'application/javascript'}
    
    return "console.log('VELQA_ERROR: INVALID_ID');", 404

@app.route('/')
def home():
    return jsonify({"status": "VELQA NEURAL ONLINE", "version": "3.2.0"})

if __name__ == "__main__":
    # Flask port management
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
