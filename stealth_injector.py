import json

def generate_stealth_script(domain, data):
    schema = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": f"Neural Optimization of {domain}",
        "author": {"@type": "Organization", "name": "VELQA"}
    }
    
    js_code = f"""
    (function() {{
        // 1. Load Pixi.js for Neural Graphics
        const pixiScript = document.createElement('script');
        pixiScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.2.4/pixi.min.js';
        document.head.appendChild(pixiScript);

        // 2. Inject Neural Schema
        const schemaScript = document.createElement('script');
        schemaScript.type = 'application/ld+json';
        schemaScript.text = JSON.stringify({json.dumps(schema)});
        document.head.appendChild(schemaScript);

        // 3. Neural Rain Animation (Pixi.js)
        pixiScript.onload = () => {{
            console.log("VELQA: Neural Graphics Engine Engaged");
            // Yahan hum background mein invisible canvas daal rahe hain
            const app = new PIXI.Application({{ 
                width: window.innerWidth, 
                height: window.innerHeight, 
                transparent: true, 
                resolution: 1 
            }});
            app.view.style.position = 'fixed';
            app.view.style.top = '0';
            app.view.style.left = '0';
            app.view.style.pointerEvents = 'none';
            app.view.style.zIndex = '-1';
            app.view.style.opacity = '0.1'; // Ekdum halka Matrix effect
            document.body.appendChild(app.view);
            
            // Neural Rain Logic (Simplified)
            const particles = [];
            for(let i=0; i<50; i++) {{
                const p = new PIXI.Graphics();
                p.beginFill(0x00ffff); p.drawRect(0,0,2,10); p.endFill();
                p.x = Math.random() * window.innerWidth;
                p.y = Math.random() * window.innerHeight;
                app.stage.addChild(p);
                particles.push(p);
            }}
            app.ticker.add(() => {{
                particles.forEach(p => {{
                    p.y += 2;
                    if(p.y > window.innerHeight) p.y = -10;
                }});
            }});
        }};
    }})();
    """
    return js_code
