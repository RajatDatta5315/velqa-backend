import os
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def signup_user(email, password):
    try:
        response = supabase.auth.sign_up({"email": email, "password": password})
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def login_user(email, password):
    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        return {"status": "success", "data": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}
