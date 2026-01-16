import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from core_engine import generate_neural_audit # Logic imported
from automation_worker import post_to_bluesky

app = Flask(__name__)
CORS(app)

# DB Setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client['velqa_db']
optimizations = db['optimizations']

@app.route('/analyze', methods=['POST'])
def analyze():
    domain = request.json.get('domain')
    if not domain:
        return jsonify({"error": "No domain"}), 400
    
    # Logic from core_engine
    result = generate_neural_audit(domain)
    optimizations.insert_one(result.copy())
    
    # Return exactly what frontend needs
    return jsonify(result)

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    data = optimizations.find_one({"site_id": site_id})
    if data:
        js = f"document.title = '{data['plan']['seo_strategy']['title']}'; console.log('VELQA Active');"
        return js, 200, {'Content-Type': 'application/javascript'}
    return "console.log('VELQA Error');", 404

if __name__ == "__main__":
    threading.Thread(target=post_to_bluesky, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
