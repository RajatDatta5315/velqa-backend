import os
import threading
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from core_engine import generate_neural_audit
from automation_worker import post_to_bluesky

app = Flask(__name__)
CORS(app)

# DB Setup
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['velqa_db']
optimizations = db['optimizations']

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        domain = data.get('domain')
        
        # Core Engine se data lo
        result = generate_neural_audit(domain)
        
        # DB mein save karo
        optimizations.insert_one(result.copy())
        
        # Script URL generate karo
        # IMPORTANT: Hum api.velqa... use kar rahe hain agar available hai
        host = "api.velqa.kryv.network" if "api.velqa" in request.host else request.host
        script_url = f"https://{host}/v3/inject.js?id={result['site_id']}"
        
        # RESPONSE FORMAT FIXED (Ye wahi format hai jo frontend chahta hai)
        return jsonify({
            "status": "Success",
            "script": script_url, 
            "data": result  # <-- Frontend is field ko dhoond raha tha
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/inject.js', methods=['GET'])
def inject_js():
    site_id = request.args.get('id')
    data = optimizations.find_one({"site_id": site_id})
    
    if data:
        title = data['plan']['seo_strategy']['title']
        js_content = f"""
        console.log("VELQA: Neural Uplink Active");
        document.title = "{title}";
        """
        return js_content, 200, {'Content-Type': 'application/javascript'}
    
    return "console.log('VELQA: Invalid ID');", 404

@app.route('/')
def home():
    return jsonify({"status": "VELQA NEURAL ONLINE"})

if __name__ == "__main__":
    threading.Thread(target=post_to_bluesky, daemon=True).start()
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
