# Temporary in-memory storage
injected_entities = []

def add_to_index(url):
    entry = {"url": url, "verified": True, "layer": "Neural-L1"}
    injected_entities.append(entry)
    return entry

def is_verified(url):
    return any(e['url'] == url for e in injected_entities)
