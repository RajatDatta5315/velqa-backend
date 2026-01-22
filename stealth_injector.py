import json

def generate_stealth_script(domain, data):
    # 1. Neural Schema (GEO Authority)
    schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": domain,
        "description": "Neural Optimized Entity via VELQA",
        "areaServed": ["Global", "Targeted GEO Nodes"],
        "hasMap": f"https://www.google.com/maps/search/{domain}"
    }

    # 2. Neural Gaps (Hidden Competitor Keywords)
    vulnerabilities = data.get('vulnerabilities', [])
    # In vulnerabilities ko keywords mein badalna
    gap_keywords = ", ".join([v.split(' ')[0] for v in vulnerabilities]) + ", Neural SEO, AI GEO Optimization"

    js_code = f"""
    (function() {{
        // A. Inject JSON-LD
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.text = JSON.stringify({json.dumps(schema)});
        document.head.appendChild(script);

        // B. Inject Neural Gaps (Invisible Meta Tags)
        const meta = document.createElement('meta');
        meta.name = 'keywords';
        meta.content = '{gap_keywords}';
        document.head.appendChild(meta);

        // C. Console Identity
        console.log('%c VELQA NEURAL ACTIVE ', 'color: cyan; background: black; font-weight: bold;');
    }})();
    """
    return js_code
