#!/bin/bash
# VELQA Local GEO Monitor Daemon
# Primary runner on your Linux PC (every 5min)
# Cloudflare cron (every 6h) is the fallback when PC is off
#
# Setup: 
#   echo "ghp_YOUR_GITHUB_TOKEN" > ~/.velqa_token
#   chmod 600 ~/.velqa_token

VELQA_API="https://velqa-backend.kryv.workers.dev"
LOG="$HOME/velqa-monitor.log"
TOKEN_FILE="$HOME/.velqa_token"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG"; }

# ── Preflight checks ─────────────────────────────────────────────
if [ ! -f "$TOKEN_FILE" ]; then
  log "SETUP NEEDED: run → echo 'ghp_yourtoken' > ~/.velqa_token && chmod 600 ~/.velqa_token"
  exit 0
fi

TOKEN=$(cat "$TOKEN_FILE" | tr -d '[:space:]')

if ! curl -sf --max-time 10 "$VELQA_API" > /dev/null 2>&1; then
  log "VELQA API offline or no internet — Cloudflare cron will cover this cycle"
  exit 0
fi

log "Checking connected repos..."

# ── Get connected repos ─────────────────────────────────────────
RESPONSE=$(curl -sf --max-time 15 -X POST "$VELQA_API/github/status" \
  -H "Content-Type: application/json" \
  -d "{\"access_token\": \"$TOKEN\"}" 2>/dev/null)

COUNT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null || echo "0")
log "Found $COUNT connected repos"

if [ "$COUNT" = "0" ]; then
  log "No repos connected — go to https://velqa.kryv.network → Auto-Monitor tab to connect one"
  exit 0
fi

# ── For each repo: check GEO files, open PRs if missing ─────────
REPOS=$(echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for r in data.get('connected_repos', []):
    print(r['repo'], r['domain'])
" 2>/dev/null)

while IFS=' ' read -r REPO DOMAIN; do
  [ -z "$REPO" ] && continue
  log "Auditing: $REPO ($DOMAIN)"

  # Check if llms.txt exists in repo
  LLMS_STATUS=$(curl -sf --max-time 10 \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: VELQA-local-monitor" \
    "https://api.github.com/repos/$REPO/contents/public/llms.txt" \
    -o /dev/null -w "%{http_code}")

  if [ "$LLMS_STATUS" != "200" ]; then
    log "  → llms.txt missing in $REPO — opening PR"
    PR=$(curl -sf --max-time 20 -X POST "$VELQA_API/github/pr" \
      -H "Content-Type: application/json" \
      -d "{\"access_token\": \"$TOKEN\", \"repo_full_name\": \"$REPO\", \"domain\": \"$DOMAIN\", \"file_type\": \"llms.txt\"}" 2>/dev/null)
    PR_URL=$(echo "$PR" | python3 -c "import sys,json; print(json.load(sys.stdin).get('pr_url','failed'))" 2>/dev/null || echo "failed")
    log "  → PR created: $PR_URL"
  else
    log "  → llms.txt already exists ✓"
  fi

  # Check robots.txt
  ROBOTS_STATUS=$(curl -sf --max-time 10 \
    -H "Authorization: Bearer $TOKEN" \
    -H "User-Agent: VELQA-local-monitor" \
    "https://api.github.com/repos/$REPO/contents/public/robots.txt" \
    -o /dev/null -w "%{http_code}")

  if [ "$ROBOTS_STATUS" != "200" ]; then
    log "  → robots.txt missing — opening PR"
    curl -sf --max-time 20 -X POST "$VELQA_API/github/pr" \
      -H "Content-Type: application/json" \
      -d "{\"access_token\": \"$TOKEN\", \"repo_full_name\": \"$REPO\", \"domain\": \"$DOMAIN\", \"file_type\": \"robots.txt\"}" > /dev/null 2>&1
    log "  → robots.txt PR queued"
  fi

  # Small delay between repos to respect GitHub rate limits
  sleep 2

done <<< "$REPOS"

log "Monitor cycle complete. Next run in 5min."
