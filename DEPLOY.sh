#!/bin/bash
set -e
echo "=== VELQA Backend Deploy ==="
source ~/.nvm/nvm.sh 2>/dev/null || true

# 1. Create D1
echo "[1/4] Creating velqa-db..."
DB_OUTPUT=$(npx wrangler d1 create velqa-db 2>&1 || true)
echo "$DB_OUTPUT"
DB_ID=$(echo "$DB_OUTPUT" | grep -oP '(?<=database_id = ")[^"]+' | head -1)
[ -z "$DB_ID" ] && { echo "Paste DB ID:"; read -r DB_ID; }
sed -i "s/REPLACE_WITH_VELQA_DB_ID/$DB_ID/" wrangler.toml
echo "✓ DB ID: $DB_ID"

# 2. Schema
echo "[2/4] Schema..."
npx wrangler d1 execute velqa-db --remote --command "CREATE TABLE IF NOT EXISTS velqa_kv (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at INTEGER DEFAULT (strftime('%s', 'now')));"
echo "✓ Schema done"

# 3. Secrets — set non-interactively, edit values below
echo "[3/4] Setting secrets..."
printf '%s' "YOUR_GITHUB_CLIENT_ID"     | npx wrangler secret put GITHUB_CLIENT_ID     --force
printf '%s' "YOUR_GITHUB_CLIENT_SECRET" | npx wrangler secret put GITHUB_CLIENT_SECRET --force
printf '%s' "YOUR_GROQ_API_KEY"         | npx wrangler secret put AI_API_KEY           --force
printf '%s' "YOUR_SERPER_API_KEY"       | npx wrangler secret put SERPER_API_KEY       --force
echo "✓ Secrets set"

# 4. Deploy
echo "[4/4] Deploying..."
npx wrangler deploy
echo "=== VELQA LIVE ==="
