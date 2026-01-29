from js import Response, fetch, Headers
import json
import uuid

async def handle_analyze(request_data, env):
    domain = request_data.get("domain", "unknown.com")
    ai_key = env.get("AI_API_KEY")
    serper_key = env.get("SERPER_API_KEY")
    
    # 1. Serper Search
    serper_url = "https://google.serper.dev/search"
    serper_headers = {"X-API-KEY": serper_key, "Content-Type": "application/json"}
    serper_body = json.dumps({"q": f"{domain} technical review and history", "num": 4})
    
    serper_res = await fetch(serper_url, method="POST", headers=Headers.new(serper_headers), body=serper_body)
    serper_json = await serper_res.json()
    context_str = json.dumps(serper_json)
    
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"

    # 2. Neural Audit Prompt
    prompt = f"DOMAIN: {domain}\nCONTEXT: {context_str}\nGenerate a DEEP NEURAL AUDIT JSON with history, roast, pros, cons, metrics, and solution promoting VELQA STEALTH SCRIPT."

    ai_url = "https://api.groq.com/openai/v1/chat/completions"
    ai_headers = {"Authorization": f"Bearer {ai_key}", "Content-Type": "application/json"}
    ai_payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are VELQA Core. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    })

    ai_res = await fetch(ai_url, method="POST", headers=Headers.new(ai_headers), body=ai_payload)
    ai_data = await ai_res.json()
    
    # AI response extraction
    raw_content = ai_data.choices[0].message.content
    audit_data = json.loads(raw_content)

    return {
        "status": "success",
        "data": {
            "domain": domain,
            "site_id": site_id,
            "history": audit_data.get("autobiography") or audit_data.get("history") or "History unavailable.",
            "roast": audit_data.get("roast", "Scan complete."),
            "vulnerabilities": audit_data.get("cons") or audit_data.get("vulnerabilities") or [],
            "strengths": audit_data.get("pros") or audit_data.get("strengths") or [],
            "metrics": audit_data.get("metrics", {"performance": "50/100"}),
            "solution": audit_data.get("solution", "Inject VELQA Script.")
        }
    }

async def on_fetch(request, env):
    # Standard CORS Headers
    res_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    }

    if request.method == "OPTIONS":
        return Response.new("", status=204, headers=Headers.new(res_headers))
    
    if request.method == "POST":
        try:
            body = await request.json()
            result = await handle_analyze(body, env)
            return Response.new(json.dumps(result), status=200, headers=Headers.new(res_headers))
        except Exception as e:
            err_data = {"error": str(e)}
            return Response.new(json.dumps(err_data), status=500, headers=Headers.new(res_headers))

    # GET Request (Health Check)
    return Response.new(json.dumps({"status": "VELQA_ONLINE"}), status=200, headers=Headers.new(res_headers))
