# Claude Code Prompts for Idea Analyzer Deployment

Copy and paste these prompts directly into Claude Code. Work through them sequentially.

---

## Setup: Open Claude Code

```powershell
cd C:\Projects\idea-analyzer
code .
```

Then open Claude Code panel in VS Code.

---

## Prompt 1: Initial Setup & Copy Files

```
I'm deploying the Idea Analyzer to NEXUS VPS. I have deployment files ready in C:\Downloads\nexus-deployment\

Project location: C:\Projects\idea-analyzer\
Deployment files: C:\Downloads\nexus-deployment\

Tasks:
1. Create a docs/deployment/ folder
2. Copy these files to correct locations:
   - extractor.Dockerfile → extractor/Dockerfile
   - slack-bot.Dockerfile → slack-bot/Dockerfile
   - docker-compose.vps.yml → ./docker-compose.vps.yml
   - auth.py → extractor/auth.py
   - .env.vps.example → ./.env.vps.example

3. Copy guide files to docs/deployment/:
   - DEPLOYMENT-CHECKLIST.md
   - VPS-DEPLOYMENT-GUIDE.md
   - main-py-updates.md
   - mcp-server-updates.md

4. Show me the new project structure after copying.

Confirm completion before I proceed to next task.
```

---

## Prompt 2: Update extractor/main.py

```
Update extractor/main.py to add API authentication.

Reference: docs/deployment/main-py-updates.md

Changes needed:
1. Add these imports at the top (after other imports):
   from auth import verify_api_key, is_auth_enabled
   from fastapi import Depends

2. Add dependencies=[Depends(verify_api_key)] to these endpoints:
   - @app.post("/extract")
   - @app.post("/extract/file")
   - @app.get("/extraction/{id}")
   - @app.get("/extractions")

3. Keep these endpoints PUBLIC (no auth needed):
   - @app.get("/")
   - @app.get("/health")

4. Update the health check endpoint to return auth status:
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "service": "idea-analyzer-extractor",
           "auth_enabled": is_auth_enabled()
       }

Before applying changes:
- Show me the current health check function
- Show me one of the protected endpoints (e.g., /extract)
- Show me the diff for the changes

After I approve, apply the changes.
```

---

## Prompt 3: Update mcp-server/index.js

```
Update mcp-server/index.js for VPS connection with authentication.

Reference: docs/deployment/mcp-server-updates.md

Changes needed:

1. At the top of the file, add environment variable support:
   const EXTRACTOR_URL = process.env.EXTRACTOR_URL || 'http://localhost:8000';
   const API_KEY = process.env.NEXUS_API_KEY || '';
   
   console.error(`[MCP] Extractor URL: ${EXTRACTOR_URL}`);
   console.error(`[MCP] API Key configured: ${API_KEY ? 'Yes' : 'No'}`);

2. Create this helper function (add after the constants):
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

3. Update the tool handlers to use authenticatedFetch():
   - get_extraction: Change fetch() to authenticatedFetch()
   - list_extractions: Change fetch() to authenticatedFetch()
   - extract_url: Change fetch() to authenticatedFetch()
   - check_service_status: Keep using regular fetch() for health endpoint

Before applying:
- Show me the current structure of one tool handler (e.g., get_extraction)
- Show me the diff for the changes

After I approve, apply the changes.
```

---

## Prompt 4: Update .gitignore

```
Update .gitignore to ensure sensitive files are not committed.

Add these entries if not already present:
.env
.env.vps
*.log
venv/
__pycache__/
*.pyc
.DS_Store

Show me:
1. Current .gitignore contents
2. Which entries will be added (if any)
3. Updated .gitignore after changes
```

---

## Prompt 5: Test Docker Builds

```
Test the Docker builds locally to ensure they work.

Tasks:
1. Build extractor image:
   docker build -t idea-analyzer-extractor:test -f extractor/Dockerfile extractor/

2. Build slack-bot image:
   docker build -t idea-analyzer-slack:test -f slack-bot/Dockerfile slack-bot/

3. Test extractor container with minimal config:
   docker run --rm -d --name test-extractor -p 8000:8000 \
     -e WHISPER_MODEL=tiny \
     -e DATABASE_URL=postgresql://test:test@localhost:5432/test \
     idea-analyzer-extractor:test

4. Wait 10 seconds, then test health endpoint:
   curl http://localhost:8000/health

5. Stop test container:
   docker stop test-extractor

Report:
- Build success/failures for each image
- Build times
- Any warnings or errors
- Health check response
- Final status: PASS or FAIL
```

---

## Prompt 6: Review Changes

```
Show me a summary of all changes made:

1. Git status - what files were added/modified?
2. Show diff for extractor/main.py (just the auth-related changes)
3. Show diff for mcp-server/index.js (just the auth-related changes)
4. List all new files created
5. Verify that .env files are in .gitignore

Provide a summary I can review before committing.
```

---

## Prompt 7: Git Commit & Push

```
Commit and push all changes to GitHub.

Steps:
1. Show git status
2. Stage all deployment files:
   git add .

3. Create commit with this message:
   "Add VPS deployment configuration with authentication
   
   - Add Dockerfiles for extractor and slack-bot services
   - Add docker-compose.vps.yml for VPS orchestration
   - Implement API key authentication in extractor
   - Update MCP server for VPS connection with auth
   - Add comprehensive deployment documentation
   - Configure 3-network isolation (public/app/data)
   
   Deployment includes:
   - PostgreSQL, Redis, PostgREST, Extractor, Slack Bot
   - Traefik labels for automatic HTTPS
   - Health checks and restart policies
   - Environment variable configuration"

4. Show commit details before pushing

5. After I confirm, push to origin main:
   git push origin main

6. Confirm push success and show remote URL
```

---

## Post-Execution Checklist

After completing all 7 prompts in Claude Code, verify:

- ✅ All deployment files in correct locations
- ✅ extractor/main.py has authentication
- ✅ mcp-server/index.js uses environment variables
- ✅ .gitignore protects sensitive files
- ✅ Docker builds successful
- ✅ Changes committed to Git
- ✅ Changes pushed to GitHub

---

## Return to Claude Desktop

Once complete, go back to Claude Desktop (NEXUS Development Project) and report:

```
Claude Code completed file updates. Summary:

✅ Files copied: [list]
✅ Code updated: extractor/main.py, mcp-server/index.js
✅ Docker builds: [success/failure]
✅ Git status: [committed and pushed / ready to commit]

Ready for VPS deployment guidance.
Any questions about the deployment process?
```

---

## Troubleshooting Common Issues

### If Docker Build Fails

**Prompt:**
```
Docker build failed. Here's the error:
[paste error]

Please:
1. Analyze the error
2. Check the Dockerfile for issues
3. Suggest fixes
4. Help me rebuild
```

### If Git Push Fails

**Prompt:**
```
Git push failed. Error:
[paste error]

Please help me:
1. Check remote configuration
2. Verify authentication
3. Resolve conflicts if any
4. Successfully push
```

### If File Paths Wrong

**Prompt:**
```
Files were copied to wrong locations. Current structure:
[paste tree output]

Expected structure:
[paste from deployment guide]

Please:
1. Move files to correct locations
2. Verify with tree command
3. Update git staging
```

---

## Advanced: Optional Prompts

### Generate Secrets

```
Help me generate secure secrets for VPS deployment:

1. Generate DB_PASSWORD (32 bytes, base64)
2. Generate REDIS_PASSWORD (32 bytes, base64)
3. Generate NEXUS_API_KEY (32 bytes, hex)

For each, run the generation command and show me the result.
Store these securely - I'll need them for Coolify configuration.
```

### Test MCP Connection (After VPS Deploy)

```
Test MCP connection to VPS:

1. Show current claude_desktop_config.json
2. Update it with:
   {
     "mcpServers": {
       "idea-analyzer": {
         "command": "node",
         "args": ["C:\\Projects\\idea-analyzer\\mcp-server\\index.js"],
         "env": {
           "EXTRACTOR_URL": "https://api.nexus.yourdomain.com",
           "NEXUS_API_KEY": "paste-your-actual-key-here"
         }
       }
     }
   }

3. Validate JSON syntax
4. Explain next steps (restart Claude Desktop)
```

### SSH to VPS

```
Help me verify VPS deployment:

Using this SSH command:
ssh nurul@YOUR_VPS_IP

Once connected, run these commands:
1. docker ps - show running containers
2. docker logs nexus-extractor --tail 50
3. docker logs nexus-slack-bot --tail 50
4. curl http://localhost:8000/health

Show me what to look for in each output.
```

---

## Ready to Start?

1. **Copy Prompt 1** into Claude Code
2. **Wait for completion** 
3. **Move to Prompt 2**
4. **Continue sequentially** through Prompt 7
5. **Return to Claude Desktop** when done

The prompts are designed to be self-contained. Claude Code will execute them step-by-step.

**Estimated total time:** 15-30 minutes for all prompts
