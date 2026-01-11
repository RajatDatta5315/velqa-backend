from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from supabase import create_client, Client
from engine import scrape_site, get_ai_analysis
# ... other imports

app = Flask(__name__)
CORS(app)

# Supabase Setup
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "rajatdatta90000@gmail.com")

@app.route('/auth/signup', methods=['POST'])
def signup():
    data = request.json
    try:
        # Supabase Auth Signup
        res = supabase.auth.sign_up({"email": data['email'], "password": data['password']})
        return jsonify({"status": "success", "user": res.user.email}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.json
    try:
        # Supabase Auth Login
        res = supabase.auth.sign_in_with_password({"email": data['email'], "password": data['password']})
        return jsonify({"status": "success", "user": res.user.email}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    url = data.get('url')
    email = data.get('email')
    
    content = scrape_site(url)
    analysis = get_ai_analysis(content, url) # Ab ye Llama-3-70b use karega
    
    # Bypass Logic for Admin
    is_admin = (email == ADMIN_EMAIL)
    return jsonify({**analysis, "is_premium": is_admin})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
