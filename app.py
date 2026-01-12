import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client # Install: pip install supabase

app = Flask(__name__)
CORS(app) # Taaki Frontend aur Backend baat kar sakein

# Supabase Config (Get these from your Supabase Dashboard)
SUPABASE_URL = "your_project_url"
SUPABASE_KEY = "your_service_role_key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/analyze', methods=['POST'])
def analyze():
    # User status check (Locked behind payment)
    user_id = request.json.get('user_id')
    user = supabase.table('profiles').select('is_pro').eq('id', user_id).single().execute()
    
    if not user.data['is_pro']:
        return jsonify({"status": "LOCKED", "message": "Neural Core requires PRO access."}), 403

    target_url = request.json.get('url')
    # Actual Llama-3-70b logic here
    report = {
        "verdict": "VULNERABLE",
        "score": 4.2,
        "tactics": "Aggressive SEO expansion needed."
    }
    return jsonify({"status": "SUCCESS", "report": report})

# Webhook for Supabase (Payment Integration)
@app.route('/webhook/payment-success', methods=['POST'])
def payment_success():
    data = request.json
    # Payment done? Unlock user dashboard automatically
    email = data['email']
    supabase.table('profiles').update({'is_pro': True}).eq('email', email).execute()
    return jsonify({"status": "DASHBOARD_UNLOCKED"}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
