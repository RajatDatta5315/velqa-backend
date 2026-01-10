import os
from supabase import create_client, Client

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def add_to_index(brand_url):
    # VELQA table mein data save karega
    data = {"url": brand_url, "status": "injected"}
    supabase.table("velqa_index").insert(data).execute()

def get_kryv_user(email):
    # KRYV users table se check karega
    response = supabase.table("profiles").select("*").eq("email", email).execute()
    return response.data
