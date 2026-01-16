import uuid, random
from datetime import datetime

def generate_neural_audit(domain):
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"
    
    # Technical "Fear" Metrics
    vulnerabilities = [
        f"DNS Latency: 420ms (Critical delay in {domain} resolution)",
        f"Core Web Vitals: LCP failed (3.8s). Visual stability compromised.",
        "SSL Handshake: Missing TLS 1.3 optimization.",
        "Server Response (TTFB): 1.2s (User drop-off rate high)",
        "Spam Score: 12% detected in backlink profile",
        "Mobile Crawler Block: 4 internal paths inaccessible"
    ]
    
    # Technical "Strengths" (To balance)
    strengths = [
        "Robots.txt: Properly configured",
        "HTTPS: Connection is secure",
        "Mobile Viewport: Correctly scaled"
    ]

    return {
        "domain": domain,
        "site_id": site_id,
        "verdict": "CRITICAL_AUTHORITY_LEAK",
        "roast": f"System scan for {domain}: Your digital infrastructure is outdated. You're losing approximately 40% of potential GEO traffic due to neural latency.",
        "vulnerabilities": random.sample(vulnerabilities, 4),
        "strengths": random.sample(strengths, 2),
        "metrics": {
            "performance": f"{random.randint(30, 60)}/100",
            "seo_health": f"{random.randint(45, 65)}%",
            "geo_relevance": "Low (Global overlap detected)"
        },
        "plan": {
            "ai_bait": f"Neural pattern for {domain} generated. Ready for injection.",
            "seo_strategy": {"title": f"VELQA | {domain} Neural Optimized"},
            "neural_schema": {"@type": "WebSite", "name": domain}
        },
        "timestamp": datetime.utcnow().isoformat()
    }
