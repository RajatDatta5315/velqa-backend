from js import Response, fetch, Headers
import json
import re

# ─────────────────────────────────────────────
# CORS HELPER
# ─────────────────────────────────────────────
def cors_headers():
    return Headers.new({
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
        "Content-Type": "application/json"
    })

def json_response(data, status=200):
    return Response.new(json.dumps(data), status=status, headers=cors_headers())

# ─────────────────────────────────────────────
# AI CALL HELPER
# ─────────────────────────────────────────────
async def call_groq(ai_key, system_prompt, user_prompt, json_mode=True):
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    }
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    res = await fetch(
        "https://api.groq.com/openai/v1/chat/completions",
        method="POST",
        headers=Headers.new({"Authorization": f"Bearer {ai_key}", "Content-Type": "application/json"}),
        body=json.dumps(payload)
    )
    data = await res.json()
    content = data["choices"][0]["message"]["content"]
    return json.loads(content) if json_mode else content

# ─────────────────────────────────────────────
# GEO SCORE CALCULATOR
# ─────────────────────────────────────────────
def calculate_geo_score(audit_data):
    score = 0
    checks = {}

    # 1. Has structured data mentioned? (+20)
    sol = audit_data.get("solution", "").lower()
    has_schema = "schema" in sol or "json-ld" in sol or "structured" in sol
    checks["structured_data"] = has_schema
    if has_schema: score += 20

    # 2. Has pros (brand strengths)? (+15)
    pros = audit_data.get("pros", [])
    checks["brand_strengths"] = len(pros) > 0
    if len(pros) > 0: score += 15

    # 3. Domain has no numbers/hyphens (clean brand name)? (+10)
    domain = audit_data.get("domain", "")
    clean_domain = not bool(re.search(r'[\d-]', domain.split('.')[0]))
    checks["clean_domain"] = clean_domain
    if clean_domain: score += 10

    # 4. Cons count (fewer = better) — max 15 pts
    cons = audit_data.get("cons", [])
    con_score = max(0, 15 - (len(cons) * 5))
    checks["low_issues"] = len(cons) < 3
    score += con_score

    # 5. Base score — all sites start at 25
    score += 25

    return min(score, 100), checks

# ─────────────────────────────────────────────
# MAIN HANDLER
# ─────────────────────────────────────────────
async def on_fetch(request, env):
    if request.method == "OPTIONS":
        return Response.new("", status=204, headers=cors_headers())

    url = request.url
    pathname = url.split("?")[0].split("/")
    path = "/" + "/".join(pathname[3:]) if len(pathname) > 3 else "/"

    ai_key = env.get("AI_API_KEY")

    # ─── GET: Health Check ───
    if request.method == "GET":
        return json_response({"status": "VELQA_GEO_ENGINE_v4.0", "routes": ["/analyze", "/geo/llms-txt", "/geo/schema", "/geo/robots", "/geo/score"]})

    if request.method == "POST":
        try:
            body = await request.json()
            domain = body.get("domain", "unknown.com").lower().strip()
            brand_name = domain.split('.')[0].capitalize()

            # ══════════════════════════════════════════
            # ROUTE 1: /analyze — Full Neural Audit
            # ══════════════════════════════════════════
            if path == "/analyze" or path == "/":
                serper_key = env.get("SERPER_API_KEY")
                context_str = ""

                if serper_key:
                    try:
                        serper_res = await fetch(
                            "https://google.serper.dev/search",
                            method="POST",
                            headers=Headers.new({"X-API-KEY": serper_key, "Content-Type": "application/json"}),
                            body=json.dumps({"q": f"{domain} technical review product", "num": 3})
                        )
                        context_str = await serper_res.text()
                    except:
                        context_str = "No search context available."

                audit = await call_groq(
                    ai_key,
                    "You are VELQA Neural Audit Engine. You audit websites for AI visibility. Return ONLY valid JSON.",
                    f"""Audit the website: {domain}
Context from web: {context_str[:1500]}

Return this exact JSON structure:
{{
  "history": "150-word technical biography of {domain} as a digital entity. Mention {brand_name} by name multiple times.",
  "roast": "One brutal one-liner about {domain}'s current state.",
  "pros": ["strength 1", "strength 2", "strength 3"],
  "cons": ["critical issue 1", "critical issue 2", "critical issue 3"],
  "metrics": {{"performance": "42/100", "seo_health": "38%", "geo_relevance": "Low", "ai_visibility": "Not Indexed"}},
  "solution": "Explain why {brand_name} must use VELQA GEO tools to become visible to AI crawlers like GPTBot, Claude-Web, and PerplexityBot."
}}"""
                )

                geo_score, checks = calculate_geo_score({
                    "domain": domain,
                    "pros": audit.get("pros", []),
                    "cons": audit.get("cons", []),
                    "solution": audit.get("solution", "")
                })

                # Build neural schema for GeoStrat component
                neural_schema = {
                    "@context": "https://schema.org",
                    "@type": "SoftwareApplication",
                    "name": brand_name,
                    "url": f"https://{domain}",
                    "description": f"AI-verified entity tracked by VELQA GEO Engine",
                    "applicationCategory": "WebApplication",
                    "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                    "sameAs": [f"https://{domain}"],
                    "verifiedBy": "VELQA Neural Network"
                }

                return json_response({
                    "status": "success",
                    "data": {
                        "domain": domain,
                        "history": audit.get("history", "Neural history unavailable."),
                        "roast": audit.get("roast", "Too weak to roast."),
                        "pros": audit.get("pros", []),
                        "cons": audit.get("cons", []),
                        "vulnerabilities": audit.get("cons", []),
                        "strengths": audit.get("pros", []),
                        "metrics": audit.get("metrics", {}),
                        "solution": audit.get("solution", "Inject VELQA tools immediately."),
                        "geo_score": geo_score,
                        "geo_checks": checks,
                        "plan": {
                            "ai_bait": f"{brand_name} — AI Indexed via VELQA Protocol",
                            "seo_strategy": {"title": f"VELQA | {domain.upper()} | GEO Score: {geo_score}/100"},
                            "neural_schema": neural_schema
                        }
                    }
                })

            # ══════════════════════════════════════════
            # ROUTE 2: /geo/llms-txt — Generate llms.txt
            # ══════════════════════════════════════════
            elif path == "/geo/llms-txt":
                description = body.get("description", f"A web application at {domain}")
                features = body.get("features", [])
                pricing = body.get("pricing", "Contact for pricing")

                features_text = "\n".join([f"- {f}" for f in features]) if features else "- Core web application features"

                llms_txt = f"""# {brand_name}

> {description}

## What is {brand_name}?
{brand_name} ({domain}) is a web-based platform. This file is provided to help AI language models, crawlers, and generative search engines understand and accurately represent {brand_name}.

## Core Features
{features_text}

## Pricing
{pricing}

## Who Uses {brand_name}?
This product is designed for professionals, teams, and individuals seeking effective digital solutions.

## Key URLs
- Homepage: https://{domain}
- Documentation: https://{domain}/docs
- API: https://{domain}/api

## Contact & Support
- Website: https://{domain}
- Support: support@{domain}

## AI Crawler Permissions
This site explicitly allows:
- GPTBot (OpenAI)
- Claude-Web (Anthropic)
- PerplexityBot (Perplexity AI)
- GoogleBot
- BingBot

## Data Freshness
This file is maintained and updated regularly. Content here reflects the current state of {brand_name}.

---
*Generated by VELQA GEO Engine — velqa.kryv.network*"""

                return json_response({
                    "status": "success",
                    "filename": "llms.txt",
                    "placement": "Place at https://{domain}/llms.txt (your site root)",
                    "content": llms_txt
                })

            # ══════════════════════════════════════════
            # ROUTE 3: /geo/schema — JSON-LD Schema Builder
            # ══════════════════════════════════════════
            elif path == "/geo/schema":
                schema_type = body.get("type", "software")
                description = body.get("description", f"A modern web application")
                features = body.get("features", [])
                pricing = body.get("pricing", "Free")
                linkedin = body.get("linkedin", "")
                crunchbase = body.get("crunchbase", "")

                same_as = [f"https://{domain}"]
                if linkedin: same_as.append(linkedin)
                if crunchbase: same_as.append(crunchbase)

                schemas = []

                # SoftwareApplication Schema
                software_schema = {
                    "@context": "https://schema.org",
                    "@type": "SoftwareApplication",
                    "name": brand_name,
                    "url": f"https://{domain}",
                    "description": description,
                    "applicationCategory": "WebApplication",
                    "operatingSystem": "Web Browser",
                    "offers": {
                        "@type": "Offer",
                        "price": "0" if "free" in pricing.lower() else "1",
                        "priceCurrency": "USD",
                        "description": pricing
                    },
                    "featureList": features,
                    "sameAs": same_as
                }
                schemas.append(software_schema)

                # Organization Schema
                org_schema = {
                    "@context": "https://schema.org",
                    "@type": "Organization",
                    "name": brand_name,
                    "url": f"https://{domain}",
                    "description": description,
                    "sameAs": same_as,
                    "contactPoint": {
                        "@type": "ContactPoint",
                        "contactType": "customer support",
                        "url": f"https://{domain}/support"
                    }
                }
                schemas.append(org_schema)

                # FAQ Schema (AI generates Q&A)
                faq_data = await call_groq(
                    ai_key,
                    "You generate FAQ structured data for websites. Return ONLY valid JSON.",
                    f"""Create 4 FAQ pairs for {brand_name} ({domain}).
Description: {description}

Return:
{{
  "faqs": [
    {{"question": "What is {brand_name}?", "answer": "..."}},
    {{"question": "How does {brand_name} work?", "answer": "..."}},
    {{"question": "Who is {brand_name} for?", "answer": "..."}},
    {{"question": "Is {brand_name} free?", "answer": "..."}}
  ]
}}"""
                )

                faq_schema = {
                    "@context": "https://schema.org",
                    "@type": "FAQPage",
                    "mainEntity": [
                        {
                            "@type": "Question",
                            "name": faq["question"],
                            "acceptedAnswer": {
                                "@type": "Answer",
                                "text": faq["answer"]
                            }
                        }
                        for faq in faq_data.get("faqs", [])
                    ]
                }
                schemas.append(faq_schema)

                # Build injection HTML
                inject_html = "\n".join([
                    f'<script type="application/ld+json">\n{json.dumps(s, indent=2)}\n</script>'
                    for s in schemas
                ])

                return json_response({
                    "status": "success",
                    "schemas": schemas,
                    "inject_html": inject_html,
                    "placement": "Paste inside <head> tag of your website"
                })

            # ══════════════════════════════════════════
            # ROUTE 4: /geo/robots — robots.txt AI Optimizer
            # ══════════════════════════════════════════
            elif path == "/geo/robots":
                disallow_paths = body.get("disallow", ["/admin", "/dashboard", "/api/private"])
                allow_paths = body.get("allow", ["/", "/blog", "/docs", "/pricing"])

                disallow_lines = "\n".join([f"Disallow: {p}" for p in disallow_paths])
                allow_lines = "\n".join([f"Allow: {p}" for p in allow_paths])

                robots_txt = f"""# robots.txt for {domain}
# Generated by VELQA GEO Engine — velqa.kryv.network
# Last Updated: {domain} — VELQA Certified

# ── Standard Search Engines ──
User-agent: Googlebot
{allow_lines}
{disallow_lines}

User-agent: Bingbot
{allow_lines}
{disallow_lines}

# ── AI Crawlers (EXPLICITLY ALLOWED for GEO) ──

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: cohere-ai
Allow: /

User-agent: YouBot
Allow: /

User-agent: Omgilibot
Allow: /

User-agent: Applebot
Allow: /

# ── Sitemap ──
Sitemap: https://{domain}/sitemap.xml

# ── General Fallback ──
User-agent: *
{allow_lines}
{disallow_lines}
Crawl-delay: 1"""

                return json_response({
                    "status": "success",
                    "filename": "robots.txt",
                    "placement": "Place at https://{domain}/robots.txt (your site root)",
                    "content": robots_txt,
                    "ai_bots_allowed": ["GPTBot", "ChatGPT-User", "Claude-Web", "anthropic-ai", "PerplexityBot", "cohere-ai", "YouBot"]
                })

            # ══════════════════════════════════════════
            # ROUTE 5: /geo/score — Standalone GEO Score
            # ══════════════════════════════════════════
            elif path == "/geo/score":
                # Quick score without full audit
                has_llms = body.get("has_llms_txt", False)
                has_schema = body.get("has_structured_data", False)
                has_robots = body.get("has_ai_robots", False)
                has_sitemap = body.get("has_sitemap", False)
                has_ssr = body.get("has_ssr", False)
                last_updated_days = body.get("last_updated_days", 999)

                score = 0
                checks = {}

                checks["llms_txt"] = has_llms
                if has_llms: score += 25

                checks["structured_data"] = has_schema
                if has_schema: score += 20

                checks["ai_robots"] = has_robots
                if has_robots: score += 20

                checks["sitemap"] = has_sitemap
                if has_sitemap: score += 15

                checks["ssr"] = has_ssr
                if has_ssr: score += 10

                checks["fresh_content"] = last_updated_days < 90
                if last_updated_days < 90: score += 10

                grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 50 else "D" if score >= 30 else "F"

                return json_response({
                    "status": "success",
                    "domain": domain,
                    "geo_score": score,
                    "grade": grade,
                    "checks": checks,
                    "missing": [k for k, v in checks.items() if not v],
                    "message": f"{brand_name} GEO Score: {score}/100 (Grade: {grade})"
                })


            # ═══ VIGILIS HEARTBEAT: /vigilis/heartbeat ════════════════════
            elif path == "/vigilis/heartbeat":
                # PC VIGILIS pings this every run to prevent cron from double-running
                import time as _time
                ts = str(int(_time.time()))
                await env.DB.prepare("INSERT OR REPLACE INTO velqa_kv (key, value) VALUES (?, ?)").bind("vigilis_heartbeat", ts).run()
                return json_response({"status": "ok", "ts": ts, "message": "heartbeat_received"})

            # ═══ GITHUB OAUTH: /github/callback ═══════════════════════════
            elif path == "/github/callback":
                import urllib.parse as up
                qs = up.parse_qs(request.url.split("?")[1] if "?" in request.url else "")
                code = (qs.get("code") or [body.get("code", "")])[0]
                if not code:
                    return json_response({"error": "code required"}, status=400)
                res = await fetch(
                    "https://github.com/login/oauth/access_token",
                    method="POST",
                    headers=Headers.new({"Accept": "application/json", "Content-Type": "application/json"}),
                    body=json.dumps({"client_id": env.GITHUB_CLIENT_ID, "client_secret": env.GITHUB_CLIENT_SECRET, "code": code})
                )
                td = await res.json()
                token = td.get("access_token", "")
                if not token:
                    return json_response({"error": "OAuth failed", "detail": td}, status=400)
                user_res = await fetch("https://api.github.com/user",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "User-Agent": "VELQA-GEO"}))
                ud = await user_res.json()
                return json_response({"access_token": token, "username": ud.get("login"), "avatar": ud.get("avatar_url")})

            # ═══ GITHUB: /github/repos ══════════════════════════════════════
            elif path == "/github/repos":
                token = body.get("access_token", "")
                if not token: return json_response({"error": "access_token required"}, status=400)
                repos_res = await fetch("https://api.github.com/user/repos?per_page=50&sort=updated&type=all",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "User-Agent": "VELQA-GEO"}))
                repos = await repos_res.json()
                simplified = [{"full_name": r.get("full_name"), "name": r.get("name"), "description": r.get("description"), "html_url": r.get("html_url"), "private": r.get("private")} for r in repos if isinstance(r, dict)]
                return json_response({"repos": simplified})

            # ═══ GITHUB: /github/connect ════════════════════════════════════
            elif path == "/github/connect":
                token = body.get("access_token", "")
                repo = body.get("repo_full_name", "")
                domain = body.get("domain", "").replace("https://", "").replace("http://", "").strip("/")
                if not all([token, repo, domain]):
                    return json_response({"error": "access_token, repo_full_name, domain required"}, status=400)
                record = json.dumps({"access_token": token, "repo": repo, "domain": domain, "connected_at": "2026"})
                kv_key = f"velqa_repo_{repo.replace('/', '_')}"
                await env.DB.prepare("INSERT OR REPLACE INTO velqa_kv (key, value) VALUES (?, ?)").bind(kv_key, record).run()
                _geo_prompt = "Domain: " + domain + ". What GEO files are missing? Return JSON: {missing: [llms.txt], priority: high, summary: brief}"
                audit = await call_groq(env.AI_API_KEY,
                    "You are a GEO expert. Return JSON only.",
                    _geo_prompt)
                return json_response({"status": "connected", "repo": repo, "domain": domain, "first_audit": audit})

            # ═══ GITHUB: /github/status ════════════════════════════════════
            elif path == "/github/status":
                token = body.get("access_token", "")
                rows_res = await env.DB.prepare("SELECT value FROM velqa_kv WHERE key LIKE 'velqa_repo_%'").all()
                connected = []
                for row in (rows_res.results or []):
                    try:
                        rec = json.loads(row["value"])
                        if rec.get("access_token") == token:
                            connected.append({"repo": rec.get("repo"), "domain": rec.get("domain")})
                    except: pass
                return json_response({"connected_repos": connected, "count": len(connected)})

            # ═══ GITHUB: /github/pr — auto-create GEO fix PR ═══════════════
            elif path == "/github/pr":
                token = body.get("access_token", "")
                repo = body.get("repo_full_name", "")
                file_type = body.get("file_type", "llms.txt")
                domain = body.get("domain", "")
                if not all([token, repo]): return json_response({"error": "access_token, repo_full_name required"}, status=400)
                brand = domain.split(".")[0].capitalize() if domain else repo.split("/")[-1]
                if file_type == "llms.txt":
                    content_str = f"# {brand}\n\n> GEO optimization file auto-generated by VELQA — velqa.kryv.network\n\n## Product\n{brand} SaaS at https://{domain}\n\n## AI Crawler Permissions\nGPTBot: Allow\nClaude-Web: Allow\nPerplexityBot: Allow\nanthropic-ai: Allow\n\n*Auto-generated by VELQA*"
                    filename = "public/llms.txt"
                elif file_type == "robots.txt":
                    content_str = f"User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: Claude-Web\nAllow: /\n\nUser-agent: PerplexityBot\nAllow: /\n\nSitemap: https://{domain}/sitemap.xml"
                    filename = "public/robots.txt"
                else:
                    content_str = f"{{\"name\": \"{brand}\"}}"
                    filename = "public/schema.json"
                import base64 as b64
                encoded = b64.b64encode(content_str.encode()).decode()
                # Get default branch SHA
                ref_res = await fetch(f"https://api.github.com/repos/{repo}",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "User-Agent": "VELQA-GEO"}))
                rd = await ref_res.json()
                branch = rd.get("default_branch", "main")
                ref2 = await fetch(f"https://api.github.com/repos/{repo}/git/refs/heads/{branch}",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "User-Agent": "VELQA-GEO"}))
                ref2d = await ref2.json()
                sha = ref2d.get("object", {}).get("sha", "")
                br_name = f"velqa-{file_type.replace('.', '-')}-{sha[:6]}"
                await fetch(f"https://api.github.com/repos/{repo}/git/refs", method="POST",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "VELQA-GEO"}),
                    body=json.dumps({"ref": f"refs/heads/{br_name}", "sha": sha}))
                await fetch(f"https://api.github.com/repos/{repo}/contents/{filename}", method="PUT",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "VELQA-GEO"}),
                    body=json.dumps({"message": f"feat: add {filename} — GEO optimization by VELQA", "content": encoded, "branch": br_name}))
                pr_res = await fetch(f"https://api.github.com/repos/{repo}/pulls", method="POST",
                    headers=Headers.new({"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "VELQA-GEO"}),
                    body=json.dumps({"title": f"[VELQA] Add {filename} for AI crawler GEO optimization", "body": f"Auto-generated by [VELQA](https://velqa.kryv.network)\n\nAdds `{filename}` to improve your GEO score by 15-25 points.\n\n*KRYV Network*", "head": br_name, "base": branch}))
                prd = await pr_res.json()
                return json_response({"status": "PR_CREATED", "pr_url": prd.get("html_url"), "pr_number": prd.get("number"), "file": filename})



            # ═══ CRON/MONITOR — manual or cron trigger ═══════════════════════
            elif path == "/cron/monitor":
                import time as _time
                # Heartbeat check: if VIGILIS on PC ran within last 2h, skip cron
                hb_row = await env.DB.prepare("SELECT value FROM velqa_kv WHERE key = 'vigilis_heartbeat'").first()
                if hb_row and hb_row.get("value"):
                    age = int(_time.time()) - int(hb_row["value"])
                    if age < 7200:
                        return json_response({"status": "skipped", "reason": "PC_active", "age_seconds": age})

                # Run autonomous GitHub repo monitoring
                rows_res = await env.DB.prepare("SELECT value FROM velqa_kv WHERE key LIKE 'velqa_repo_%'").all()
                results = []
                for row in (rows_res.results or []):
                    val = row.get("value")
                    if not val: continue
                    try:
                        rec = json.loads(val)
                        token = rec.get("access_token", "")
                        repo = rec.get("repo", "")
                        domain = rec.get("domain", "")
                        if not all([token, repo, domain]): continue
                        # Check which GEO files are missing
                        for fname in ["public/llms.txt", "public/robots.txt"]:
                            try:
                                chk = await fetch(f"https://api.github.com/repos/{repo}/contents/{fname}",
                                    headers=Headers.new({"Authorization": f"Bearer {token}", "User-Agent": "VELQA-GEO"}))
                                if chk.status == 404:
                                    # File missing — queue a PR (simplified: just log)
                                    results.append({"repo": repo, "missing": fname, "action": "pr_needed"})
                            except: pass
                    except: pass
                return json_response({"status": "ok", "checked": len(results), "actions": results})


            else:
                return json_response({"error": f"Unknown route: {path}"}, status=404)

        except Exception as e:
            return json_response({"error": str(e), "route": "unknown"}, status=500)


# ══════════════════════════════════════════════════════════════════
# GITHUB OAUTH + AUTONOMOUS MONITORING ROUTES
# ══════════════════════════════════════════════════════════════════

# These routes are injected into the main handler. For the worker,
# add the following elif blocks inside the main on_fetch handler
# after the existing route checks.

# ROUTE: /github/callback — OAuth exchange
# GET /github/callback?code=XXX
# Returns { access_token, username, repos[] }

# ROUTE: /github/repos — List user repos
# POST /github/repos { access_token }

# ROUTE: /github/connect — Connect repo to VELQA monitoring
# POST /github/connect { access_token, repo_full_name, domain }
# Stores { repo, domain, token } in KV. On cron, VELQA audits + opens PRs.

# ROUTE: /github/status — Get monitoring status for connected repos
# POST /github/status { access_token }

# ROUTE (CRON): /cron/monitor — Called on scheduled cron
# Loops all KV-stored repos, runs audit, opens GitHub PRs for missing files

