from js import Response, fetch, Headers
import json
import uuid

async def handle_analyze(request_data, env):
    domain = request_data.get("domain", "unknown.com")
    ai_key = env.get("AI_API_KEY")
    serper_key = env.get("SERPER_API_KEY")
    
    # Live Search via Serper (Using Fetch instead of Requests)
    serper_headers = Headers.new({"X-API-KEY": serper_key, "Content-Type": "application/json"})
    serper_body = json.dumps({"q": f"{domain} technical review and history", "num": 4})
    
    serper_res = await fetch("https://google.serper.dev/search", method="POST", headers=serper_headers, body=serper_body)
    context_str = await serper_res.text()
    
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"

    # Neural Audit Prompt
    prompt = f"DOMAIN: {domain}\nCONTEXT: {context_str}\nGenerate a DEEP NEURAL AUDIT JSON with history, roast, pros, cons, metrics, and solution promoting VELQA STEALTH SCRIPT."

    ai_headers = Headers.new({"Authorization": f"Bearer {ai_key}", "Content-Type": "application/json"})
    ai_payload = json.dumps({
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "You are VELQA Core. Output ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"}
    })

    ai_res = await fetch("https://api.groq.com/openai/v1/chat/completions", method="POST", headers=ai_headers, body=ai_payload)
    ai_data = await ai_res.json()
    
    audit_data = json.loads(ai_data.choices[0].message.content)

    return {
        "status": "success",
        "data": {
            "domain": domain,
            "site_id": site_id,
            "history": audit_data.get("autobiography", audit_data.get("history")),
            "roast": audit_data.get("roast"),
            "vulnerabilities": audit_data.get("cons"),
            "strengths": audit_data.get("pros"),
            "metrics": audit_data.get("metrics"),
            "solution": audit_data.get("solution")
        }
    }

async def on_fetch(request, env):
    # CORS Headers
    res_headers = Headers.new({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    })

    if request.method == "OPTIONS":
        return Response.new("", status=204, headers=res_headers)
    
    if request.method == "POST":
        try:
            body = await request.json()
            result = await handle_analyze(body, env)
            return Response.new(json.dumps(result), status=200, headers=res_headers)
        except Exception as e:
            return Response.new(json.dumps({"error": str(e)}), status=500, headers=res_headers)

    return Response.new("VELQA_ONLINE", status=200, headers=res_headers)
