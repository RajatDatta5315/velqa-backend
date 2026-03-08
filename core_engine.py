# DEPRECATED: This file was the old Flask engine.
# Active backend is server_v2.py (Cloudflare Python Worker).
# Kept for reference only.

import os
import uuid
import json
import requests
from datetime import datetime

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
SERPER_API_URL = "https://google.serper.dev/search"

def get_real_data(domain):
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key: return "No SERP context."
    payload = json.dumps({"q": f"{domain} technical review and history", "num": 4})
    headers = {'X-API-KEY': api_key, 'Content-Type': 'application/json'}
    try:
        response = requests.post(SERPER_API_URL, headers=headers, data=payload)
        return response.text
    except: return "Search offline."

def generate_neural_audit(domain):
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"
    context_str = get_real_data(domain)
    brand_name = domain.split('.')[0].capitalize()

    prompt = f"""
    DOMAIN: {domain}
    CONTEXT: {context_str}

    TASK: Generate a DEEP NEURAL AUDIT.
    Return ONLY valid JSON:
    {{
        "history": "150-word technical biography of {domain}. Mention {brand_name} by name multiple times.",
        "roast": "One brutal one-liner about {domain}.",
        "pros": ["strength 1", "strength 2", "strength 3"],
        "cons": ["critical issue 1", "critical issue 2", "critical issue 3"],
        "metrics": {{"performance": "42/100", "seo_health": "38%", "geo_relevance": "Low", "ai_visibility": "Not Indexed"}},
        "solution": "Explain why {brand_name} must use VELQA GEO tools."
    }}
    """

    try:
        res = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are VELQA Core. Brutal, technical, JSON-only."},
                    {"role": "user", "content": prompt}
                ],
                "response_format": {"type": "json_object"}
            }
        )
        data = json.loads(res.json()['choices'][0]['message']['content'])
    except:
        data = {
            "history": f"System failed to map the full history of {domain}",
            "roast": "Site too weak to audit.",
            "pros": ["Exists on the internet"],
            "cons": ["No GEO optimization", "No AI visibility", "No structured data"],
            "metrics": {"performance": "0/100"},
            "solution": "Inject VELQA Script immediately."
        }

    geo_score = 25  # base
    if data.get("pros"): geo_score += 15
    if len(data.get("cons", [])) < 3: geo_score += 15

    return {
        "domain": domain,
        "site_id": site_id,
        "history": data.get("history"),
        "roast": data.get("roast"),
        "pros": data.get("pros"),
        "cons": data.get("cons"),
        "vulnerabilities": data.get("cons"),
        "strengths": data.get("pros"),
        "metrics": data.get("metrics"),
        "solution": data.get("solution"),
        "geo_score": geo_score,
        "plan": {
            "ai_bait": f"{brand_name} — AI Indexed via VELQA Protocol",
            "seo_strategy": {"title": f"VELQA | {domain.upper()}"}
        },
        "timestamp": datetime.utcnow().isoformat()
    }
