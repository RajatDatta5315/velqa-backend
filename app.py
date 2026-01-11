from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.auth_manager import signup_user, login_user # Import from new file

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)

@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    data = request.json
    result = signup_user(data['email'], data['password'])
    return jsonify(result)

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.json
    result = login_user(data['email'], data['password'])
    return jsonify(result)

# ... analyze routes ...
