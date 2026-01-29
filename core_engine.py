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

    # Brutal Autobiography Prompt
    prompt = f"""
    DOMAIN: {domain}
    CONTEXT: {context_str}
    
    TASK: Generate a DEEP NEURAL AUDIT.
    1. AUTOBIOGRAPHY: Write a 150-word technical history of {domain}. Describe it like a failing digital organism. Use its name '{domain}' repeatedly. 
    2. ROAST: A savage one-liner.
    3. PROS: 3 legitimate strengths.
    4. CONS: 3 critical technical failures.
    5. SOLUTION: Explicitly mention that the owner must inject the 'VELQA STEALTH SCRIPT' to fix neural gaps and stop competitor crawling.
    
    OUTPUT ONLY VALID JSON:
    {{
        "autobiography": "detailed text",
        "roast": "text",
        "pros": [],
        "cons": [],
        "metrics": {{"performance": "0/100", "seo_health": "0%", "geo_relevance": "Low"}},
        "solution": "text promoting VELQA script"
    }}
    """
    
    try:
        res = requests.post(
            GROQ_API_URL,
            headers={"Authorization": f"Bearer {os.getenv('AI_API_KEY')}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are VELQA Core. Brutal, technical, and JSON-only."},
                             {"role": "user", "content": prompt}],
                "response_format": { "type": "json_object" }
            }
        )
        data = json.loads(res.json()['choices'][0]['message']['content'])
    except:
        data = { "autobiography": "System failed to map the full history of " + domain, "roast": "Site too weak to audit.", "pros": ["None"], "cons": ["Existence"], "metrics": { "performance": "0/100" }, "solution": "Inject VELQA Script immediately." }

    return {
        "domain": domain,
        "site_id": site_id,
        "history": data.get("autobiography"),
        "roast": data.get("roast"),
        "vulnerabilities": data.get("cons"),
        "strengths": data.get("pros"),
        "metrics": data.get("metrics"),
        "solution": data.get("solution"),
        "plan": {{ "ai_bait": "Neural Path Active", "seo_strategy": {{ "title": f"VELQA | {domain.upper()}" }} }},
        "timestamp": datetime.utcnow().isoformat()
    }
