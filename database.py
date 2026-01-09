import json
import os

DB_FILE = "data.json"

def load_data():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f)

def add_to_index(url):
    data = load_data()
    # Check if already exists
    if not any(e['url'] == url for e in data):
        entry = {"url": url, "status": "INJECTED", "verified": True}
        data.append(entry)
        save_data(data)
        return entry
    return None

def is_verified(url):
    data = load_data()
    return any(e['url'] == url for e in data)
