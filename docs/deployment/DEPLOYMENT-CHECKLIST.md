# Idea Analyzer VPS Deployment - Quick Checklist

Use this checklist to track your deployment progress.

---

## Pre-Deployment: File Preparation

### New Files to Create

- [ ] `extractor/Dockerfile` - Container config for extraction service
- [ ] `slack-bot/Dockerfile` - Container config for Slack bot
- [ ] `docker-compose.vps.yml` - VPS orchestration config
- [ ] `extractor/auth.py` - API authentication module
- [ ] `.env.vps.example` - Environment variables template
- [ ] `.gitignore` updates - Ensure .env files are ignored

### Files to Modify

- [ ] `extractor/main.py` - Add authentication to endpoints
  - Add imports: `from auth import verify_api_key, is_auth_enabled`
  - Add `dependencies=[Depends(verify_api_key)]` to protected routes
  - Update health check to show auth status (optional)

- [ ] `mcp-server/index.js` - Add VPS connection support
  - Add environment variable support for URL and API key
  - Create `authenticatedFetch()` helper function
  - Update all tool handlers to use authenticated requests
  - Add error logging

### Files to Review (No Changes Needed)

- [ ] `supabase/schema.sql` - Database schema (already correct)
- [ ] `extractor/extractors/*.py` - Extractor modules (no changes)
- [ ] `slack-bot/app.py` - Slack bot (no changes)
- [ ] `extractor/requirements.txt` - Dependencies (verify current)
- [ ] `slack-bot/requirements.txt` - Dependencies (verify current)

---

## Local Testing

- [ ] Build extractor Docker image locally
- [ ] Build slack-bot Docker image locally  
- [ ] Test extractor container with local database
- [ ] Verify health endpoint responds
- [ ] Test API authentication (with/without key)
- [ ] Commit changes to Git
- [ ] Push to GitHub

---

## VPS Deployment

### Infrastructure

- [ ] VPS running and accessible
- [ ] Coolify installed
- [ ] Domain DNS configured (A record)
- [ ] SSH access working

### Coolify Configuration

- [ ] Create new resource in Coolify
- [ ] Connect GitHub repository
- [ ] Select docker-compose.vps.yml
- [ ] Configure environment variables (all from .env.vps.example)
- [ ] Set domain routing for api.nexus.yourdomain.com
- [ ] Enable HTTPS/SSL
- [ ] Deploy

### Environment Variables Set

- [ ] `NEXUS_DOMAIN`
- [ ] `DB_PASSWORD`
- [ ] `REDIS_PASSWORD`
- [ ] `NEXUS_API_KEY`
- [ ] `SLACK_BOT_TOKEN`
- [ ] `SLACK_SIGNING_SECRET`
- [ ] `SLACK_APP_TOKEN`
- [ ] `WHISPER_MODEL` (optional, defaults to "base")
- [ ] `REDDIT_CLIENT_ID` (optional)
- [ ] `REDDIT_CLIENT_SECRET` (optional)
- [ ] `GITHUB_TOKEN` (optional)

---

## Verification

### Service Health

- [ ] All containers running (green in Coolify)
- [ ] No errors in container logs
- [ ] Health endpoint: `curl https://api.nexus.yourdomain.com/health`
- [ ] SSL certificate active (HTTPS working)

### Authentication

- [ ] Request without API key returns 401
- [ ] Request with valid API key succeeds
- [ ] Health endpoint accessible without auth

### Database

- [ ] PostgreSQL container running
- [ ] Database initialized with schema
- [ ] Can connect: `docker exec -it nexus-postgres psql -U nexus -d idea_analyzer`

---

## MCP Configuration

### Local MCP Updates

- [ ] Update `claude_desktop_config.json` with VPS URL
- [ ] Add `NEXUS_API_KEY` to MCP config
- [ ] Restart Claude Desktop (fully quit and reopen)

### MCP Testing

- [ ] Ask Claude to check service status
- [ ] Test extraction via Claude: `extract_url`
- [ ] Test retrieval via Claude: `list_extractions`
- [ ] Verify data appears in VPS database

---

## Slack Integration

### Slack Configuration

- [ ] Bot invited to test channel
- [ ] Socket Mode enabled with correct scopes

### Slack Testing

- [ ] Share URL - bot responds with extraction ID
- [ ] Check status - bot shows processing/completed
- [ ] Verify extraction in database
- [ ] Test file upload (optional)

---

## Monitoring

### Netdata (if deployed)

- [ ] Netdata accessible
- [ ] CPU/RAM metrics showing
- [ ] Container metrics visible
- [ ] Alerts configured (>80% RAM, >80% disk)

### UptimeRobot

- [ ] Monitor created for api.nexus.yourdomain.com/health
- [ ] Check interval: 5 minutes
- [ ] Slack webhook configured for alerts
- [ ] Test alert sent successfully

---

## Documentation

- [ ] Update NEXUS project files with deployment date
- [ ] Document actual domain used
- [ ] Store secrets in password manager
- [ ] Create backup of .env file (encrypted/secure location)
- [ ] Update services.md with live URLs
- [ ] Mark Phase 2 as complete in roadmap.md

---

## Post-Deployment

### Immediate

- [ ] Run one full extraction end-to-end (YouTube video)
- [ ] Verify transcription works (Whisper running on VPS)
- [ ] Check RAM usage during extraction
- [ ] Test from multiple interfaces (Claude, Slack)

### Within 24 Hours

- [ ] Monitor resource usage trends
- [ ] Check for any error patterns in logs
- [ ] Verify automatic restarts work (if container crashes)
- [ ] Test after VPS reboot

### Within 1 Week

- [ ] Establish backup routine
- [ ] Document any issues encountered
- [ ] Plan next features (Celery, analysis storage)

---

## Rollback Procedure (If Needed)

If deployment fails:

- [ ] Switch MCP back to localhost in Claude config
- [ ] Restart Claude Desktop
- [ ] Continue using local instance
- [ ] Debug VPS issues without pressure
- [ ] Re-attempt deployment when ready

---

## Success Criteria

Deployment is successful when:

✅ **Extractor API**
- Responding to health checks
- Accepting authenticated requests
- Processing extractions successfully

✅ **Slack Bot**
- Listening for URLs
- Creating extractions
- Responding with status

✅ **MCP Integration**
- Tools working from Claude Desktop
- Data syncing with VPS
- No authentication errors

✅ **Monitoring**
- Alerts configured
- Metrics collecting
- Notifications working

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Container won't start | Check env vars, review logs |
| 401 errors from MCP | Verify API key matches in both places |
| Slack bot silent | Check tokens, verify Socket Mode enabled |
| Out of memory | Reduce Whisper model size or upgrade VPS |
| SSL not generating | Check DNS, wait for propagation, verify ports open |

---

## Reference Files

These files contain detailed instructions:

- `VPS-DEPLOYMENT-GUIDE.md` - Complete step-by-step guide
- `main-py-updates.md` - How to update extractor/main.py
- `mcp-server-updates.md` - How to update mcp-server/index.js
- `.env.vps.example` - All environment variables explained

---

## Estimated Time

- **File preparation:** 30-45 minutes
- **Local testing:** 15-30 minutes
- **VPS deployment:** 30-60 minutes (including Coolify setup)
- **MCP configuration:** 10-15 minutes
- **Testing & verification:** 30-45 minutes

**Total:** 2-3 hours for first deployment

---

## Next Steps After Success

1. Deploy to production with real domain
2. Add Celery for background processing
3. Store analysis results in database
4. Create web dashboard
5. Add rate limiting
6. Implement backup automation

---

**Status Tracking**

Deployment Date: _______________
VPS IP: _______________
Domain: _______________
API Key: _______________ (store in password manager!)

Notes:
_______________________________________
_______________________________________
_______________________________________
