# NEXUS + Claude Code: Deployment Workflow

> How to seamlessly work between Claude Desktop (NEXUS Development Project) and Claude Code for Idea Analyzer deployment

---

## The Two-Tool Strategy

### Claude Desktop (This Project)
**Purpose:** Planning, architecture, coordination, documentation
**Best For:**
- Making architectural decisions
- Reviewing overall progress
- Updating NEXUS documentation
- Planning next steps
- Understanding context across entire NEXUS ecosystem

### Claude Code
**Purpose:** Execution, file operations, code changes
**Best For:**
- Creating/modifying files
- Running commands
- Testing code
- Git operations
- Direct project work

---

## Which Folder for Claude Code?

### ✅ Work from: `C:\Projects\idea-analyzer\`

**Why:**
- This is the actual project that needs modification
- All files are in one place
- Git repository is here
- Can run local tests immediately
- Direct access to existing code

### ❌ NOT from: NEXUS project folder

**Why:**
- NEXUS project is for documentation/planning
- Idea Analyzer is a separate codebase
- Don't mix NEXUS architecture docs with Idea Analyzer code

---

## The Complete Workflow

### Phase 1: Planning & Context (Claude Desktop - This Project)

**What we just did:**
1. ✅ Discussed deployment strategy
2. ✅ Created all necessary files
3. ✅ Documented architecture decisions
4. ✅ Prepared deployment guides

**What you do:**
- Review the deployment files I created
- Download them to a temporary location
- Understand the overall deployment strategy
- Ask any clarifying questions here

---

### Phase 2: Execution (Claude Code)

**Location:** `C:\Projects\idea-analyzer\`

**Process:**
1. Open Claude Code
2. Set working directory: `C:\Projects\idea-analyzer\`
3. Use Prompts to execute specific tasks
4. Claude Code will create/modify files directly in your project

---

## Detailed Step-by-Step Process

### Step 1: Download Deployment Files (You)

From Claude Desktop, download the 9 files I created:
```
DEPLOYMENT-CHECKLIST.md
VPS-DEPLOYMENT-GUIDE.md
extractor.Dockerfile
slack-bot.Dockerfile
docker-compose.vps.yml
auth.py
main-py-updates.md
mcp-server-updates.md
.env.vps.example
```

Save them to: `C:\Downloads\nexus-deployment\` (or wherever convenient)

---

### Step 2: Open Claude Code

**Command:**
```powershell
cd C:\Projects\idea-analyzer
code .
```

This opens VS Code in the Idea Analyzer project directory.

**Then:** Open Claude Code panel (Ctrl+Shift+P → "Claude Code")

---

### Step 3: Give Claude Code Initial Context

**First message in Claude Code:**

```
I'm deploying the Idea Analyzer to NEXUS VPS. I have deployment files ready.

Project location: C:\Projects\idea-analyzer\
Deployment files location: C:\Downloads\nexus-deployment\

Please help me:
1. Copy the deployment files into the correct locations
2. Update extractor/main.py with authentication
3. Update mcp-server/index.js for VPS connection
4. Test the Docker builds locally

I'll provide the specific files and instructions as we go.
```

---

### Step 4: Execute Tasks in Claude Code

Use these **task-specific prompts** in Claude Code:

#### Task 1: Copy Deployment Files
```
Copy these deployment files to the correct locations:

FROM: C:\Downloads\nexus-deployment\
TO: Current project

Files to copy:
- extractor.Dockerfile → extractor/Dockerfile
- slack-bot.Dockerfile → slack-bot/Dockerfile  
- docker-compose.vps.yml → ./docker-compose.vps.yml
- auth.py → extractor/auth.py
- .env.vps.example → ./.env.vps.example

Also copy the guide files to a new /docs/deployment/ folder:
- DEPLOYMENT-CHECKLIST.md
- VPS-DEPLOYMENT-GUIDE.md
- main-py-updates.md
- mcp-server-updates.md

Confirm when done.
```

#### Task 2: Update extractor/main.py
```
Update extractor/main.py to add API authentication.

Reference: docs/deployment/main-py-updates.md

Changes needed:
1. Add imports: from auth import verify_api_key, is_auth_enabled
2. Add dependencies=[Depends(verify_api_key)] to these endpoints:
   - POST /extract
   - POST /extract/file
   - GET /extraction/{id}
   - GET /extractions
3. Keep GET / and GET /health public (no auth)
4. Update health check to show auth_enabled status

Show me the diff before applying.
```

#### Task 3: Update mcp-server/index.js
```
Update mcp-server/index.js for VPS connection.

Reference: docs/deployment/mcp-server-updates.md

Changes needed:
1. Add environment variable support at top
2. Create authenticatedFetch() helper function
3. Update all tool handlers to use authenticatedFetch()
4. Keep check_service_status using public health endpoint
5. Add error logging

Show me the diff before applying.
```

#### Task 4: Update .gitignore
```
Update .gitignore to ensure these files are ignored:
- .env
- .env.vps
- *.log
- venv/
- __pycache__/
- *.pyc

Show current .gitignore and proposed changes.
```

#### Task 5: Test Docker Builds
```
Test the Docker builds locally:

1. Build extractor image:
   docker build -t idea-analyzer-extractor:test -f extractor/Dockerfile extractor/

2. Build slack-bot image:
   docker build -t idea-analyzer-slack:test -f slack-bot/Dockerfile slack-bot/

3. Run quick health check test:
   docker run --rm -p 8000:8000 -e WHISPER_MODEL=tiny idea-analyzer-extractor:test
   (In another terminal: curl http://localhost:8000/health)

Report any errors.
```

#### Task 6: Git Commit
```
Prepare for Git commit:

1. Show git status
2. Review changes with git diff
3. Stage all deployment files
4. Create commit with message:
   "Add VPS deployment configuration with authentication
   
   - Add Dockerfiles for extractor and slack-bot
   - Add docker-compose.vps.yml for VPS deployment
   - Implement API key authentication
   - Update MCP server for VPS connection
   - Add deployment documentation"

5. Push to GitHub

Confirm before executing each step.
```

---

### Step 5: Return to Claude Desktop (This Project)

**When to come back here:**
- After Claude Code completes the file modifications
- To review what was done
- To plan next steps (actual VPS deployment)
- To update NEXUS documentation

**What to tell me:**
```
Claude Code has completed the file updates. Here's what was done:
[paste summary from Claude Code]

I'm ready to proceed with VPS deployment. What's next?
```

---

### Step 6: VPS Deployment Planning (Claude Desktop)

**Back in this Project:**
- Review deployment checklist
- Discuss VPS configuration
- Plan environment variables
- Generate secrets
- Plan Coolify setup

---

### Step 7: VPS Deployment Execution (Could be either tool)

**Option A: Claude Code**
- If you want help with SSH commands
- If you want help generating secrets
- If you want to test API calls

**Option B: Manually + Claude Desktop for guidance**
- Follow VPS-DEPLOYMENT-GUIDE.md
- Come back here with questions
- Use this Project for troubleshooting

---

## When to Use Which Tool

### Use Claude Desktop (This Project) for:

✅ **Strategic Planning**
- "Should we deploy PostgreSQL separately or with the app?"
- "What's the best way to handle secrets?"
- "How should we structure the networks?"

✅ **Architecture Review**
- "Does this deployment approach make sense?"
- "What are the security implications?"
- "How does this fit into the overall NEXUS architecture?"

✅ **Documentation Updates**
- "Update roadmap.md with deployment completion"
- "Add new service URLs to services.md"
- "Document lessons learned in decisions-log.md"

✅ **Context & Understanding**
- "Explain the 3-network isolation model"
- "Why did we choose this authentication approach?"
- "What are the trade-offs of running MCP locally?"

✅ **Multi-Project Coordination**
- "How does Idea Analyzer integrate with the rest of NEXUS?"
- "What should we deploy next?"
- "Update the overall NEXUS roadmap"

---

### Use Claude Code for:

✅ **File Operations**
- Creating files
- Modifying code
- Moving/renaming files
- Copying files

✅ **Code Changes**
- Adding authentication
- Updating endpoints
- Refactoring code
- Fixing bugs

✅ **Running Commands**
- Docker builds
- Git operations
- Testing scripts
- Local server testing

✅ **Project-Specific Work**
- Working in C:\Projects\idea-analyzer\
- Testing locally
- Building containers
- Running tests

✅ **Following Instructions**
- "Do exactly what's in main-py-updates.md"
- "Run these 5 commands in sequence"
- "Update these specific files"

---

## Practical Example: Complete Deployment Flow

### 1️⃣ Claude Desktop (This Project)
**You:** "I'm ready to deploy Idea Analyzer to VPS. What do I need to do?"

**Me:** [Creates all deployment files, explains strategy]

**You:** Downloads files, reviews approach

---

### 2️⃣ Claude Code (Idea Analyzer Project)
**You:** Opens C:\Projects\idea-analyzer in Claude Code

**Prompt 1:** "Copy deployment files from C:\Downloads\nexus-deployment\"

**Claude Code:** Executes, confirms completion

**Prompt 2:** "Update extractor/main.py per main-py-updates.md"

**Claude Code:** Shows diff, applies changes

**Prompt 3:** "Update mcp-server/index.js per mcp-server-updates.md"

**Claude Code:** Shows diff, applies changes

**Prompt 4:** "Test Docker builds"

**Claude Code:** Runs builds, reports success

**Prompt 5:** "Git commit and push"

**Claude Code:** Commits with proper message, pushes

---

### 3️⃣ Claude Desktop (This Project)
**You:** "Files are updated and pushed to GitHub. Ready for VPS."

**Me:** 
- Guides you through VPS deployment steps
- Helps generate secrets
- Troubleshoots any issues
- Updates NEXUS documentation

---

### 4️⃣ Claude Code (For VPS Commands)
**Optional:** Use Claude Code to help with:
- SSH commands
- Docker commands on VPS
- Testing API endpoints
- Generating secrets

---

### 5️⃣ Claude Desktop (This Project) - Final
**You:** "Deployment complete! Here's what happened..."

**Me:** 
- Updates roadmap.md (mark Phase 2 complete)
- Updates services.md with live URLs
- Updates decisions-log.md with any new decisions
- Plans next phase

---

## Quick Reference Commands

### In Claude Code:
```
# Set working directory
cd C:\Projects\idea-analyzer

# Useful prompts:
"Show current project structure"
"Run git status"
"Build Docker image for extractor"
"Show diff for extractor/main.py"
"Test the health endpoint"
"Commit and push to GitHub"
```

### In Claude Desktop (This Project):
```
# Useful questions:
"What's the current status of NEXUS deployment?"
"Review the changes Claude Code made"
"What should we deploy next?"
"Update the roadmap with today's progress"
"What are the security considerations for X?"
"How does this integrate with the rest of NEXUS?"
```

---

## Pro Tips

### Tip 1: Use Prompts Feature in Claude Code
Save common tasks as Prompts:
- "Deploy preparation checklist"
- "Run local tests"
- "Git commit and push"
- "Docker build all services"

### Tip 2: Copy-Paste Between Tools
Claude Desktop → Claude Code:
- Copy file contents I create
- Copy specific instructions
- Copy command sequences

Claude Code → Claude Desktop:
- Copy execution results
- Copy error messages
- Copy git commit messages

### Tip 3: Keep This Project Open
Always have Claude Desktop with NEXUS Development Project open for:
- Quick context checks
- Documentation updates
- Strategic decisions

### Tip 4: MCP in Both Places
Both Claude Desktop and Claude Code can use MCP:
- Same tools available
- Same data access
- Use whichever is convenient

### Tip 5: Session Continuity
If you switch tools mid-task:
- Summarize what was done in the first tool
- Paste that summary when starting in the second tool
- Maintain context across both conversations

---

## Example Session Template

### Claude Desktop Session Start:
```
Starting work on: [Task name]
Current status: [Brief status]
Goal today: [What you want to accomplish]
Questions: [Any questions before diving in]
```

### Claude Code Session Start:
```
Working directory: C:\Projects\idea-analyzer
Task: [Specific task from Claude Desktop discussion]
Reference files: [List any guide files]
Expected outcome: [What success looks like]
```

### End of Session (Either Tool):
```
✅ Completed: [What was done]
📝 Notes: [Important observations]
⏭️ Next: [What's next]
❓ Blockers: [Any issues encountered]
```

---

## Your Specific Next Steps

### Right Now (After reading this):

1. **Download** the 9 deployment files from Claude Desktop
2. **Review** VPS-DEPLOYMENT-GUIDE.md to understand the flow
3. **Decide**: Do the file updates now, or later?

### When Ready to Execute:

**Option A: Use Claude Code (Recommended)**
1. Open C:\Projects\idea-analyzer in VS Code
2. Open Claude Code panel
3. Start with Task 1 (copy files)
4. Work through Tasks 2-6 sequentially
5. Return here to report completion

**Option B: Do Manually**
1. Follow the update guides yourself
2. Test as you go
3. Return here when ready for VPS deployment

### After File Updates Complete:

Come back to **Claude Desktop (This Project)** and say:
```
File updates complete. Ready for VPS deployment.
Current state: [Brief summary]
Next step: [What you think is next]
Questions: [Any questions about VPS deployment]
```

Then I'll guide you through the VPS deployment process.

---

## FAQ

**Q: Can I use Claude Code for the actual VPS deployment?**
A: Yes, for the commands. But Coolify configuration is done in the web UI. Claude Code can help with:
- SSH commands
- Generating secrets
- Testing API endpoints
- Verifying deployment

**Q: Should I keep both conversations running?**
A: Yes! Keep this Project open in Claude Desktop for context, and use Claude Code in VS Code for execution.

**Q: What if I get stuck in Claude Code?**
A: Come back here with the error message. This Project has full NEXUS context to help troubleshoot.

**Q: Can Claude Code access the MCP tools?**
A: Yes, if configured. But typically you'd use MCP from Claude Desktop for analysis, and Claude Code for file operations.

**Q: Do I need to copy files to NEXUS project folder?**
A: No. Keep Idea Analyzer in C:\Projects\idea-analyzer\. Only update NEXUS documentation files (in this Project) after deployment completes.

---

**Ready to start?** 

Tell me which approach you prefer:
1. **"Use Claude Code"** - I'll give you the first prompt to use
2. **"Manual"** - I'll clarify any questions you have about the guides
3. **"Hybrid"** - Some tasks in Claude Code, some manual

What works best for you?
