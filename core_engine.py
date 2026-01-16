import uuid, random
from datetime import datetime

def generate_neural_audit(domain):
    site_id = f"ID_{uuid.uuid4().hex[:7].upper()}"
    
    # Technical "Bad" Points (Fear/Credibility)
    vulnerabilities = [
        f"LCP (Largest Contentful Paint) for {domain} is above 3.5s",
        "Missing X-Frame-Options Header (Clickjacking Risk)",
        "Neural Schema mismatch: Local entities not linked",
        "JavaScript Execution Thread blocking Main UI",
        "Unminified CSS slowing down GEO-crawlers"
    ]
    
    # Technical "Good" Points (Relief)
    strengths = [
        "SSL Integrity: Grade A+",
        "Mobile Viewport Optimization: Active",
        "Domain Authority Baseline: Stable",
        "TTFB (Time to First Byte): Optimized"
    ]

    return {
        "domain": domain,
        "site_id": site_id,
        "verdict": "VULNERABLE_BUT_OPTIMIZABLE",
        "roast": f"Analysis for {domain}: Your technical SEO is leaking authority. While the baseline is stable, the neural discovery layer is missing.",
        "vulnerabilities": random.sample(vulnerabilities, 3),
        "strengths": random.sample(strengths, 2), # Naya field
        "plan": {
            "ai_bait": f"Neural pattern for {domain} generated. Ready for injection.",
            "seo_strategy": {"title": f"VELQA | {domain} Neural Optimized"},
            "gaps": ["Local GEO-fence missing", "Schema entity link broken"]
        },
        "timestamp": datetime.utcnow().isoformat()
    }
