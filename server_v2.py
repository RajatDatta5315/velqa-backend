from js import Response, fetch, Headers
import json

async def on_fetch(request, env):
    # CORS Headers initialization
    headers = Headers.new({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    })

    if request.method == "OPTIONS":
        return Response.new("", status=204, headers=headers)

    if request.method == "GET":
        return Response.new(json.dumps({"status": "VELQA_ONLINE"}), status=200, headers=headers)

    if request.method == "POST":
        try:
            body = await request.json()
            domain = body.get("domain", "unknown.com")
            
            # API Keys from Environment
            ai_key = env.get("AI_API_KEY")
            serper_key = env.get("SERPER_API_KEY")

            # 1. Serper Search
            serper_res = await fetch(
                "https://google.serper.dev/search",
                method="POST",
                headers=Headers.new({"X-API-KEY": serper_key, "Content-Type": "application/json"}),
                body=json.dumps({"q": f"{domain} technical history", "num": 3})
            )
            serper_data = await serper_res.text()

            # 2. Groq AI Analysis
            ai_payload = json.dumps({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "You are VELQA. Return JSON only."},
                    {"role": "user", "content": f"Audit {domain} using context: {serper_data}. Include history, roast, pros, cons, and solution."}
                ],
                "response_format": {"type": "json_object"}
            })

            ai_res = await fetch(
                "https://api.groq.com/openai/v1/chat/completions",
                method="POST",
                headers=Headers.new({"Authorization": f"Bearer {ai_key}", "Content-Type": "application/json"}),
                body=ai_payload
            )
            ai_json = await ai_res.json()
            
            # Extract content correctly
            audit_result = json.loads(ai_json.choices[0].message.content)

            response_data = {
                "status": "success",
                "data": {
                    "domain": domain,
                    "history": audit_result.get("history", "Data hidden in neural gaps."),
                    "roast": audit_result.get("roast", "Weak infrastructure detected."),
                    "vulnerabilities": audit_result.get("cons", []),
                    "strengths": audit_result.get("pros", []),
                    "solution": audit_result.get("solution", "Inject VELQA Stealth Script.")
                }
            }
            return Response.new(json.dumps(response_data), status=200, headers=headers)

        except Exception as e:
            return Response.new(json.dumps({"error": str(e)}), status=500, headers=headers)
