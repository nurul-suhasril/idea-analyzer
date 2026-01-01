# Idea Analyzer VPS Deployment Guide

This guide walks through deploying the Idea Analyzer from local Windows to NEXUS VPS.

---

## Prerequisites

### On VPS
- ✅ Contabo VPS running Ubuntu 24.04
- ✅ Coolify installed and configured
- ✅ Domain DNS configured (A record pointing to VPS)
- ✅ SSH access configured

### On Local Machine
- ✅ Idea Analyzer working locally at `C:\Projects\idea-analyzer\`
- ✅ Git configured
- ✅ GitHub repository created (optional but recommended)

---

## Phase 1: Prepare Local Repository

### 1. Add New Files to Project

Copy the created files into your local project:

```powershell
# Navigate to project
cd C:\Projects\idea-analyzer

# Create Dockerfile in extractor/
copy path\to\extractor.Dockerfile extractor\Dockerfile

# Create Dockerfile in slack-bot/
copy path\to\slack-bot.Dockerfile slack-bot\Dockerfile

# Copy docker-compose for VPS
copy path\to\docker-compose.vps.yml docker-compose.vps.yml

# Create auth module in extractor/
copy path\to\auth.py extractor\auth.py

# Create environment template
copy path\to\.env.vps.example .env.vps.example
```

### 2. Update extractor/main.py

Add authentication to the extractor service following `main-py-updates.md`:

**At the top of main.py, add:**
```python
from auth import verify_api_key, is_auth_enabled
from fastapi import Depends
```

**Update endpoints:**
```python
# Add dependencies=[Depends(verify_api_key)] to:
@app.post("/extract", dependencies=[Depends(verify_api_key)])
@app.post("/extract/file", dependencies=[Depends(verify_api_key)])
@app.get("/extraction/{id}", dependencies=[Depends(verify_api_key)])
@app.get("/extractions", dependencies=[Depends(verify_api_key)])

# Keep these public (no auth):
@app.get("/")
@app.get("/health")
```

**Optional: Update health check to show auth status:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "idea-analyzer-extractor",
        "auth_enabled": is_auth_enabled()
    }
```

### 3. Update mcp-server/index.js

Follow `mcp-server-updates.md` to add VPS connection support:

**At the top, add:**
```javascript
const EXTRACTOR_URL = process.env.EXTRACTOR_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXUS_API_KEY || '';

console.error(`[MCP] Extractor URL: ${EXTRACTOR_URL}`);
console.error(`[MCP] API Key configured: ${API_KEY ? 'Yes' : 'No'}`);
```

**Add helper function:**
```javascript
async function authenticatedFetch(path, options = {}) {
  const url = `${EXTRACTOR_URL}${path}`;
  const headers = {
    ...options.headers,
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
  };
  
  try {
    const response = await fetch(url, { ...options, headers });
    if (response.status === 401) {
      console.error('[MCP] Authentication failed - check NEXUS_API_KEY');
    }
    return response;
  } catch (error) {
    console.error(`[MCP] Request failed to ${url}:`, error.message);
    throw error;
  }
}
```

**Update all fetch calls to use `authenticatedFetch()`** (see full examples in mcp-server-updates.md)

### 4. Update .gitignore

Ensure sensitive files are ignored:

```
# Add if not already present
.env
.env.vps
*.log
venv/
__pycache__/
*.pyc
.DS_Store
```

### 5. Test Locally with Docker

Build and test the containers locally before deploying:

```powershell
# Build images
docker build -t idea-analyzer-extractor:local -f extractor/Dockerfile extractor/
docker build -t idea-analyzer-slack:local -f slack-bot/Dockerfile slack-bot/

# Test extractor container
docker run --rm -p 8000:8000 `
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/idea_analyzer `
  -e REDIS_URL=redis://host.docker.internal:6379 `
  -e WHISPER_MODEL=tiny `
  idea-analyzer-extractor:local

# In another terminal, test health endpoint
curl http://localhost:8000/health
```

### 6. Commit and Push to GitHub

```powershell
git add .
git commit -m "Add VPS deployment configuration with authentication"
git push origin main
```

---

## Phase 2: Deploy to VPS

### 1. Connect to VPS

```powershell
ssh nurul@your-vps-ip
```

### 2. Create Project in Coolify

1. Open Coolify dashboard: `https://coolify.nexus.yourdomain.com`
2. Click "New Resource" → "GitHub Repository"
3. Connect your GitHub account (if not already)
4. Select repository: `your-username/idea-analyzer`
5. Set deployment type: **Docker Compose**
6. Point to: `docker-compose.vps.yml`

### 3. Configure Environment Variables

In Coolify, go to project settings → Environment Variables and add:

**Copy from `.env.vps.example` and fill in actual values:**

#### Required Variables
```
NEXUS_DOMAIN=nexus.yourdomain.com
DB_PASSWORD=<generate-secure-password>
REDIS_PASSWORD=<generate-secure-password>
NEXUS_API_KEY=<generate-api-key>
SLACK_BOT_TOKEN=xoxb-<your-token>
SLACK_SIGNING_SECRET=<your-secret>
SLACK_APP_TOKEN=xapp-<your-token>
```

#### Optional Variables
```
WHISPER_MODEL=base
REDDIT_CLIENT_ID=<if-using-reddit>
REDDIT_CLIENT_SECRET=<if-using-reddit>
GITHUB_TOKEN=<if-using-github-private-repos>
```

**Generate secure passwords:**
```bash
# On VPS or local terminal
openssl rand -base64 32  # For DB_PASSWORD
openssl rand -base64 32  # For REDIS_PASSWORD
openssl rand -hex 32     # For NEXUS_API_KEY
```

### 4. Configure Domain Routing

In Coolify, set up domain routing:

1. **Extractor Service:**
   - Domain: `api.nexus.yourdomain.com`
   - Port: 8000
   - Enable HTTPS (Let's Encrypt)

2. **PostgREST (optional):**
   - Domain: `postgrest.nexus.yourdomain.com`
   - Port: 3000
   - Enable HTTPS

### 5. Deploy

Click **Deploy** in Coolify dashboard.

Monitor the deployment logs:
- Building Docker images
- Starting containers
- Database initialization
- SSL certificate generation

Expected deployment time: **5-10 minutes**

### 6. Verify Deployment

**Check service health:**
```bash
# From your local machine
curl https://api.nexus.yourdomain.com/health

# Expected response:
# {"status":"healthy","service":"idea-analyzer-extractor","auth_enabled":true}
```

**Test authentication:**
```bash
# Without API key (should fail with 401)
curl https://api.nexus.yourdomain.com/extractions

# With API key (should succeed)
curl -H "X-API-Key: your-actual-api-key" https://api.nexus.yourdomain.com/extractions
```

**Check Coolify logs:**
- All services should show as "running" (green)
- No error messages in container logs
- SSL certificates should be active

---

## Phase 3: Configure Local MCP for VPS

### 1. Update Claude Desktop Config

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**Update the config:**
```json
{
  "mcpServers": {
    "idea-analyzer": {
      "command": "node",
      "args": [
        "C:\\Projects\\idea-analyzer\\mcp-server\\index.js"
      ],
      "env": {
        "EXTRACTOR_URL": "https://api.nexus.yourdomain.com",
        "NEXUS_API_KEY": "your-actual-api-key-from-env-vars"
      }
    }
  }
}
```

### 2. Restart Claude Desktop

**Important:** Fully quit and restart Claude Desktop (not just close window).

1. Right-click Claude Desktop in system tray
2. Click "Quit"
3. Restart Claude Desktop

### 3. Verify MCP Connection

In Claude Desktop, ask:
```
Check the idea analyzer service status
```

Expected response:
```
Service Status: healthy
Auth Enabled: true
```

### 4. Test Extraction

```
Extract this article: https://example.com/some-article
```

Claude should:
1. Call the MCP tool
2. Send authenticated request to VPS
3. Return extraction ID
4. Extraction appears in VPS database

---

## Phase 4: Test Slack Integration

### 1. Invite Bot to Channel

In Slack workspace:
```
/invite @Idea Analyzer
```

### 2. Test URL Sharing

Share a URL in the channel:
```
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Bot should respond with:
```
✅ Extraction started: abc12345
Use /status abc12345 to check progress
```

### 3. Check Extraction Status

```
/status abc12345
```

### 4. Verify in Database

SSH to VPS and check database:
```bash
ssh nurul@vps-ip

# Connect to database
docker exec -it nexus-postgres psql -U nexus -d idea_analyzer

# Check extractions
SELECT id, url, status, title FROM extractions ORDER BY created_at DESC LIMIT 5;
```

---

## Phase 5: Monitoring Setup

### 1. Configure Netdata Alerts

In Netdata (if deployed), set alerts for:
- RAM usage > 80%
- Disk usage > 80%
- Container down

### 2. Configure UptimeRobot

Create monitors for:
- `https://api.nexus.yourdomain.com/health` (HTTP GET, every 5 min)
- `https://postgrest.nexus.yourdomain.com/` (HTTP GET, every 5 min)

### 3. Test Alerts

Trigger a test alert to verify Slack notifications work.

---

## Troubleshooting

### Container Won't Start

**Check logs in Coolify:**
```
Services → idea-analyzer → Logs
```

**Common issues:**
- Missing environment variables
- Database connection failed (check credentials)
- Port already in use
- Insufficient RAM

### Authentication Failing

**Check API key:**
```bash
# From local machine
curl -v -H "X-API-Key: your-key" https://api.nexus.yourdomain.com/health
```

Look for:
- 401 = Invalid/missing API key
- 200 = Auth working

**Verify MCP is using correct key:**
Check Claude Desktop logs (stderr output when it starts)

### Slack Bot Not Responding

**Check container logs:**
```bash
ssh nurul@vps-ip
docker logs nexus-slack-bot
```

**Common issues:**
- Invalid Slack tokens
- Socket Mode not enabled
- Bot not invited to channel
- Extractor service unreachable

### Whisper Transcription Failing

**Check RAM usage:**
```bash
docker stats nexus-extractor
```

If RAM > 90%, try smaller Whisper model:
- Change `WHISPER_MODEL=tiny` in Coolify env vars
- Redeploy

Or add OpenAI Whisper API as fallback (costs money but uses their API instead).

### SSL Certificate Not Generating

**Check DNS:**
```bash
nslookup api.nexus.yourdomain.com
```

Should point to VPS IP.

**Check Coolify logs** for Let's Encrypt errors.

**Common fixes:**
- Wait 5-10 minutes for DNS propagation
- Verify port 80/443 open in firewall
- Ensure domain is not behind Cloudflare proxy (use DNS only)

---

## Rollback Plan

If deployment fails and you need to roll back:

### 1. Keep Local Running

Your local instance is still working - use that while fixing VPS.

### 2. Update MCP to Point Back to Local

```json
{
  "mcpServers": {
    "idea-analyzer": {
      "command": "node",
      "args": ["C:\\Projects\\idea-analyzer\\mcp-server\\index.js"],
      "env": {
        "EXTRACTOR_URL": "http://localhost:8000",
        "NEXUS_API_KEY": ""
      }
    }
  }
}
```

### 3. Restart Claude Desktop

### 4. Debug VPS Issues

Take your time fixing VPS deployment - local system is still operational.

---

## Post-Deployment Checklist

- [ ] All containers running in Coolify
- [ ] Health check returns 200 OK
- [ ] API authentication working (401 without key, 200 with key)
- [ ] MCP tools working from Claude Desktop
- [ ] Slack bot responding to URLs
- [ ] Extraction completes successfully
- [ ] Database populated with test extraction
- [ ] SSL certificates active (HTTPS working)
- [ ] Monitoring configured (Netdata + UptimeRobot)
- [ ] Alerts configured (Slack notifications)
- [ ] Backup process documented

---

## Next Steps

After successful deployment:

1. **Add Celery Worker** - Move long-running extractions to background queue
2. **Store Analysis Results** - Save Claude's analyses to `analyses` table
3. **Create Web Dashboard** - View extractions and analyses in browser
4. **Add Rate Limiting** - Protect API from abuse
5. **Implement Cleanup Job** - Delete old extractions after 90 days

---

## Quick Reference

### Important URLs
```
Extractor API:  https://api.nexus.yourdomain.com
Health Check:   https://api.nexus.yourdomain.com/health
PostgREST:      https://postgrest.nexus.yourdomain.com (optional)
Coolify:        https://coolify.nexus.yourdomain.com
```

### Important Directories
```
Local:  C:\Projects\idea-analyzer\
VPS:    /data/coolify/services/<service-id>/
```

### Useful Commands
```bash
# View logs
docker logs nexus-extractor
docker logs nexus-slack-bot

# Restart service
docker restart nexus-extractor

# Check database
docker exec -it nexus-postgres psql -U nexus -d idea_analyzer

# View all containers
docker ps
```

---

**Deployment Complete!**

Your Idea Analyzer is now running on NEXUS VPS, accessible 24/7 from Claude and Slack. The MCP server runs locally and connects securely to your VPS via HTTPS with API key authentication.
