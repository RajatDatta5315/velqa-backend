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

# Global in-memory list synced with file
injected_entities = load_data()

def add_to_index(url):
    global injected_entities
    entry = {"url": url, "verified": True, "layer": "Neural-L1"}
    injected_entities.append(entry)
    save_data(injected_entities)
    return entry

def is_verified(url):
    data = load_data()
    return any(e['url'] == url for e in data)
