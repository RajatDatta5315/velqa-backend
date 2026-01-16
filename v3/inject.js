(async function() {
    const params = new URLSearchParams(window.location.search);
    const siteId = new URL(document.currentScript.src).searchParams.get('id');

    if (!siteId) return;

    try {
        const response = await fetch(`https://exciting-ferne-kryv-d4a2caf9.koyeb.app/api/v3/config?id=${siteId}`);
        const config = await response.json();

        if (config.success) {
            // 1. Inject Schema
            const script = document.createElement('script');
            script.type = 'application/ld+json';
            script.text = JSON.stringify(config.schema);
            document.head.appendChild(script);

            // 2. DOM HIJACKING (Autonomous Mode)
            if (config.optimizations) {
                // Update Title
                if (config.optimizations.title) {
                    document.title = config.optimizations.title;
                }
                // Update Meta Description
                let metaDesc = document.querySelector('meta[name="description"]');
                if (metaDesc) {
                    metaDesc.setAttribute('content', config.optimizations.description);
                } else {
                    metaDesc = document.createElement('meta');
                    metaDesc.name = "description";
                    metaDesc.content = config.optimizations.description;
                    document.head.appendChild(metaDesc);
                }
                console.log("VELQA: Page Autonomously Optimized.");
            }
        }
    } catch (e) {
        console.error("VELQA Uplink Failed.");
    }
})();
