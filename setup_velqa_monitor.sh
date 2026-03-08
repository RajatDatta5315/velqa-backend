#!/bin/bash
# VELQA Local Monitor Setup Script
# Run once on your Linux PC: bash setup_velqa_monitor.sh

echo "=== VELQA Local GEO Monitor Setup ==="

# 1. Copy monitor script
cp velqa_monitor.sh ~/velqa-monitor.sh
chmod +x ~/velqa-monitor.sh
echo "✅ Monitor script copied to ~/velqa-monitor.sh"

# 2. Install systemd service + timer
sudo cp velqa_monitor.service /etc/systemd/system/velqa-monitor.service
sudo cp velqa_monitor.timer /etc/systemd/system/velqa-monitor.timer
echo "✅ Systemd service + timer installed"

# 3. Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable velqa-monitor.timer
sudo systemctl start velqa-monitor.timer
echo "✅ Timer enabled — runs every 5 minutes when PC is on"

# 4. Prompt for GitHub token
echo ""
echo "══════════════════════════════════════════════════════"
echo "  LAST STEP: Store your GitHub token"
echo "  1. Go to: github.com/settings/tokens → Classic → New"
echo "  2. Select scopes: repo, read:user"
echo "  3. Paste it below:"
echo "══════════════════════════════════════════════════════"
read -s -p "GitHub token (hidden): " GH_TOKEN
echo ""
echo "$GH_TOKEN" > ~/.velqa_token
chmod 600 ~/.velqa_token
echo "✅ Token stored securely in ~/.velqa_token"

echo ""
echo "══════════════════════════════════════════════════════"
echo "✅ VELQA local monitor is running!"
echo ""
echo "  Check status:  systemctl status velqa-monitor.timer"
echo "  View logs:     tail -f ~/velqa-monitor.log"
echo "  Manual run:    bash ~/velqa-monitor.sh"
echo ""
echo "  The Cloudflare cron (every 6h) remains as fallback"
echo "  when your PC is off."
echo "══════════════════════════════════════════════════════"
