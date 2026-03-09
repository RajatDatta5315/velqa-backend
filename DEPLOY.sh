#!/bin/bash
# VELQA Backend Deploy
set -e
source ~/.nvm/nvm.sh 2>/dev/null || true
echo "=== VELQA Deploy ==="

echo "[1/4] Creating velqa-db..."
npx wrangler d1 create velqa-db 2>&1 || true
echo ""
echo "Paste the database_id shown above, then Enter:"
read -r DB_ID
[ -z "$DB_ID" ] && { echo "Check: npx wrangler d1 list"; read -r DB_ID; }
sed -i "s/REPLACE_WITH_VELQA_DB_ID/$DB_ID/" wrangler.toml
echo "✓ DB ID: $DB_ID"

echo "[2/4] Schema..."
npx wrangler d1 execute velqa-db --remote --command "CREATE TABLE IF NOT EXISTS velqa_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at INTEGER DEFAULT (strftime('%s', 'now')));"
echo "✓ Schema done"

echo "[3/4] Secrets (paste when prompted)..."
npx wrangler secret put GITHUB_CLIENT_ID
npx wrangler secret put GITHUB_CLIENT_SECRET
npx wrangler secret put AI_API_KEY
npx wrangler secret put SERPER_API_KEY
echo "✓ Secrets set"

echo "[4/4] Deploying..."
npx wrangler deploy
echo "=== VELQA LIVE ==="
