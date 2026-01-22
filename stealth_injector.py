import json

def generate_stealth_script(domain, data):
    """
    Creates a script that injects INVISIBLE Authority signals.
    No watermark. No title hijacking.
    """
    
    # 1. Neural Schema (Google Knowledge Graph ke liye)
    schema = {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": domain,
        "url": f"https://{domain}",
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"https://{domain}/search?q={{search_term_string}}",
            "query-input": "required name=search_term_string"
        },
        "publisher": {
            "@type": "Organization",
            "name": f"{domain} Authority",
            "logo": {
                "@type": "ImageObject",
                "url": "https://img.icons8.com/color/48/verified-badge.png" 
            }
        }
    }
    
    # 2. Competitor Keywords (Hidden Meta Tags)
    keywords = ["AI Optimization", "Next-Gen SEO", "Neural Search", "High Authority"]
    if data and 'vulnerabilities' in data:
        # Hum vulnerabilities ko keywords mein badal denge (Smart Move)
        keywords += [v.split(':')[0] for v in data['vulnerabilities']]

    keywords_str = ",".join(keywords[:10])

    # 3. The Injection Code (Pure JS, No Visual Changes)
    js_code = f"""
    (function() {{
        console.log('VELQA_NEURAL: Stealth Mode Active');
        
        // A. Inject JSON-LD Schema (Invisible to Humans, Gold for Bots)
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.text = JSON.stringify({json.dumps(schema)});
        document.head.appendChild(script);
        
        // B. Inject Meta Keywords (Competitor Gaps)
        const meta = document.createElement('meta');
        meta.name = 'keywords';
        meta.content = '{keywords_str}';
        document.head.appendChild(meta);
        
        // C. Console Badge (Only Devs see this)
        console.log('%c OPTIMIZED BY VELQA ', 'background: #000; color: #00f; font-weight: bold; padding: 4px;');
    }})();
    """
    
    return js_code
