import uuid
from datetime import datetime
import random

def generate_neural_audit(domain):
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"
    
    # Roasts for different types of domains
    roasts = [
        f"Your SEO on {domain} is so weak, even Google's 404 page has more authority.",
        f"{domain}? Looks like a 1995 template had a baby with a broken database.",
        f"Neural scan complete. {domain} has the security of a screen door on a submarine.",
        f"I've seen faster loading times on a dial-up connection in a rainstorm."
    ]
    
    vulnerabilities_pool = [
        "EXPOSED_METADATA_LEAK",
        "NEURAL_LATENCY_CRITICAL",
        "SCHEMA_INJECTION_VULNERABLE",
        "AI_CRAWLER_BLOCK_MISSING",
        "HEADER_SECURITY_FAIL",
        "DOMAIN_INTEGRITY_LOW"
    ]

    return {
        "domain": domain,
        "site_id": site_id,
        "verdict": "VULNERABLE_CORE_DETECTED", # Match with AuditCore.tsx
        "roast": random.choice(roasts),        # Match with AuditCore.tsx
        "vulnerabilities": random.sample(vulnerabilities_pool, 3), # Match with AuditCore.tsx
        "plan": {
            "ai_bait": f"Neural pattern for {domain} active.",
            "seo_strategy": {"title": f"VELQA | {domain} Optimized"},
            "neural_schema": {"@type": "WebSite", "name": domain}
        },
        "timestamp": datetime.utcnow().isoformat()
    }
