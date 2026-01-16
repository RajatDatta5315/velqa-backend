import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from core_engine import generate_neural_audit
from automation_worker import post_to_bluesky

app = Flask(__name__)
CORS(app)

client = MongoClient(os.getenv("MONGO_URI"))
db = client['velqa_db']
optimizations = db['optimizations']

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        domain = request.json.get('domain')
        # Core Engine se asli data generate karo
        result = generate_neural_audit(domain)
        
        # Database mein save
        optimizations.insert_one(result.copy())
        
        # RESPONSE: Is format ko mat chhedna, frontend isi ko read karta hai
        return jsonify({
            "status": "Success",
            "script": f"https://api.velqa.kryv.network/v3/inject.js?id={result['site_id']}",
            "data": result # <--- Ye portal ko audit/strat dikhayega
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    data = optimizations.find_one({"site_id": site_id})
    if data:
        return f"document.title = '{data['plan']['seo_strategy']['title']}';", 200, {'Content-Type': 'application/javascript'}
    return "console.log('Error');", 404

@app.route('/')
def home():
    return jsonify({"status": "VELQA NEURAL ONLINE"})

if __name__ == "__main__":
    threading.Thread(target=post_to_bluesky, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
