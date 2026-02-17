# AXIMO Runbook — Cloudflare Tunnel + Next Proxy + Backend Guard

## Architecture (current)
- Cloudflare Tunnel (cloudflared tunnel run aximo) exposes:
  - https://meeting.aximo.works -> localhost:3000 (Next.js production)
- Next.js (launchd com.aximo.frontend) serves:
  - /kanban, /meeting pages
  - /api/proxy/* : server-side proxy to backend
- FastAPI backend (launchd com.aximo.backend) listens:
  - http://127.0.0.1:8000
  - Enforced: X-AXIMO-TOKEN (AXIMO_API_TOKEN)
  - IP allowlist disabled: AXIMO_IP_ALLOWLIST=

## Key files
- Backend env: /Users/albertkim/02_PROJECTS/03_aximo/backend/.env
- Frontend prod env: /Users/albertkim/02_PROJECTS/03_aximo/frontend/aximo-web/.env.prod (gitignored)
- Backend launchd: ~/Library/LaunchAgents/com.aximo.backend.plist (sources backend/.env)
- Frontend launchd: ~/Library/LaunchAgents/com.aximo.frontend.plist (sources .env.prod)
- Cloudflared: ~/Library/LaunchAgents/com.aximo.cloudflared.plist (if managed by launchd)

## Restart procedures
### Backend restart
uid=$(id -u)
pl=~/Library/LaunchAgents/com.aximo.backend.plist
launchctl bootout gui/${uid}/com.aximo.backend 2>/dev/null || true
launchctl unload "$pl" 2>/dev/null || true
launchctl load "$pl"
launchctl kickstart -k gui/${uid}/com.aximo.backend

### Frontend restart
uid=$(id -u)
pl=~/Library/LaunchAgents/com.aximo.frontend.plist
launchctl bootout gui/${uid}/com.aximo.frontend 2>/dev/null || true
launchctl unload "$pl" 2>/dev/null || true
launchctl load "$pl"
launchctl kickstart -k gui/${uid}/com.aximo.frontend

## Health checks
- Backend health:
  curl -s http://127.0.0.1:8000/health
- Local proxy sanity:
  curl -i http://127.0.0.1:3000/api/proxy/tasks | head
- External (Service Token) sanity:
  curl -i -H "CF-Access-Client-Id: <ID>" -H "CF-Access-Client-Secret: <SECRET>" https://meeting.aximo.works/api/proxy/tasks | head
