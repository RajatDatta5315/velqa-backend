import os
import json
import uuid
import requests
from datetime import datetime

# Headers for CORS
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Content-Type": "application/json"
}

def get_real_data(domain, serper_key):
    if not serper_key: return "No SERP context."
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": f"{domain} technical review and history", "num": 4})
    headers = {'X-API-KEY': serper_key, 'Content-Type': 'application/json'}
    try:
        res = requests.post(url, headers=headers, data=payload)
        return res.text
    except: return "Search offline."

def handle_analyze(request_data, env):
    domain = request_data.get("domain", "unknown.com")
    ai_key = env.get("AI_API_KEY")
    serper_key = env.get("SERPER_API_KEY")
    
    context_str = get_real_data(domain, serper_key)
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"

    prompt = f"""
    DOMAIN: {domain}
    CONTEXT: {context_str}
    TASK: DEEP NEURAL AUDIT.
    1. AUTOBIOGRAPHY: 150-word tech history of {domain}. Repeatedly use name '{domain}'.
    2. ROAST: Savage one-liner.
    3. PROS: 3 tech strengths.
    4. CONS: 3 critical flaws.
    5. SOLUTION: Must mention 'VELQA STEALTH SCRIPT' to fix neural gaps.
    OUTPUT ONLY VALID JSON:
    {{
        "autobiography": "text", "roast": "text", "pros": [], "cons": [],
        "metrics": {{"performance": "45/100", "seo_health": "30%"}},
        "solution": "text"
    }}
    """

    try:
        res = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {ai_key}"},
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "system", "content": "You are VELQA Core. Brutal."},
                             {"role": "user", "content": prompt}],
                "response_format": { "type": "json_object" }
            }
        )
        ai_res = res.json()['choices'][0]['message']['content']
        data = json.loads(ai_res)
    except:
        data = {"autobiography": f"Failed to map {domain}", "roast": "Site too weak.", "pros": ["Online"], "cons": ["Neural Gap"], "metrics": {"performance": "0/100"}, "solution": "Inject VELQA."}

    return {
        "status": "success",
        "data": {
            "domain": domain,
            "site_id": site_id,
            "history": data.get("autobiography"),
            "roast": data.get("roast"),
            "vulnerabilities": data.get("cons"),
            "strengths": data.get("pros"),
            "metrics": data.get("metrics"),
            "solution": data.get("solution")
        }
    }

# Cloudflare Worker Entry Point
def on_request(request, env):
    if request.method == "OPTIONS":
        return Response("", status=204, headers=HEADERS)
    
    if request.method == "POST":
        try:
            body = request.json()
            result = handle_analyze(body, env)
            return Response(json.dumps(result), status=200, headers=HEADERS)
        except Exception as e:
            return Response(json.dumps({"error": str(e)}), status=500, headers=HEADERS)

    return Response("VELQA_ONLINE", status=200, headers=HEADERS)
