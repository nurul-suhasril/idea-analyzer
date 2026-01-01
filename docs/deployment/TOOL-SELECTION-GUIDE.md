# Quick Guide: Claude Desktop vs Claude Code

When working on NEXUS, use this guide to decide which tool to use.

---

## Decision Tree

### I want to...

#### 📝 Make architectural decisions
→ **Claude Desktop (This Project)**
- Review overall NEXUS architecture
- Decide on deployment strategies
- Plan integration between services
- Update roadmap and decisions log

#### ✏️ Modify code files
→ **Claude Code (idea-analyzer folder)**
- Add authentication to API
- Update MCP server
- Fix bugs
- Refactor code

#### 📦 Create new files
→ **Claude Code (idea-analyzer folder)**
- Dockerfiles
- Configuration files
- New Python modules
- Documentation

#### 🔧 Run commands
→ **Claude Code (idea-analyzer folder)**
- Docker builds
- Git operations
- Local testing
- npm/pip installs

#### 🤔 Understand how something works
→ **Claude Desktop (This Project)**
- Explain architecture
- Clarify design decisions
- Review documentation
- Understand integrations

#### 🐛 Debug an issue
→ **Start in Claude Code, escalate to Claude Desktop**
- Claude Code: Check logs, test fixes
- Claude Desktop: If it's architectural/design issue

#### 📊 Review overall progress
→ **Claude Desktop (This Project)**
- Update roadmap
- Mark milestones complete
- Plan next phase
- Document learnings

#### 🧪 Test locally
→ **Claude Code (idea-analyzer folder)**
- Run Docker containers
- Test API endpoints
- Verify changes work
- Run integration tests

#### 🚀 Deploy to VPS
→ **Both (sequence)**
1. Claude Desktop: Plan deployment strategy
2. Claude Code: Prepare files, test builds
3. Claude Desktop: Guide VPS configuration
4. Claude Code: Help with SSH commands (optional)
5. Claude Desktop: Document completion

#### 📚 Update documentation
→ **Depends on what you're documenting**
- NEXUS architecture docs → Claude Desktop (This Project)
- Idea Analyzer README → Claude Code (idea-analyzer folder)
- API documentation → Claude Code (idea-analyzer folder)
- Decisions log → Claude Desktop (This Project)

#### 🔐 Generate secrets
→ **Either tool works**
- Claude Code: If you want to run commands directly
- Claude Desktop: If you want guidance only

#### 🔍 Search past conversations
→ **Claude Desktop (This Project)**
- Has access to conversation search MCP tool
- Can reference past architectural discussions
- Maintains context across entire NEXUS project

#### 🎯 Plan next steps
→ **Claude Desktop (This Project)**
- Strategic planning
- Roadmap updates
- Prioritization decisions
- Resource allocation

---

## Tool Comparison

| Task Type | Claude Desktop | Claude Code | Best Choice |
|-----------|----------------|-------------|-------------|
| **Planning** | ✅ Excellent | ❌ Not ideal | Desktop |
| **Coding** | ❌ Read-only | ✅ Full editing | Code |
| **Commands** | ❌ Can't execute | ✅ Can run | Code |
| **Architecture** | ✅ Full context | ⚠️ Limited context | Desktop |
| **File operations** | ❌ Can't modify | ✅ Create/edit/delete | Code |
| **Documentation** | ✅ NEXUS docs | ✅ Code docs | Both |
| **Testing** | ❌ Can't run | ✅ Can execute | Code |
| **Integration** | ✅ Sees big picture | ⚠️ Project-specific | Desktop |
| **Debugging** | ✅ Strategic help | ✅ Tactical help | Both |
| **Git operations** | ❌ Can't execute | ✅ Can commit/push | Code |

---

## Common Workflows

### Workflow 1: Adding a New Feature

1. **Claude Desktop**: Plan the feature
   - "I want to add rate limiting to the API"
   - Discuss approach, implications
   - Decide on implementation strategy

2. **Claude Code**: Implement the feature
   - Use prompts to modify code
   - Add necessary dependencies
   - Test locally

3. **Claude Desktop**: Document the feature
   - Update architecture.md
   - Add to decisions-log.md
   - Update roadmap.md

---

### Workflow 2: Fixing a Bug

1. **Claude Code**: Investigate
   - Check logs
   - Review error messages
   - Test reproduction

2. **Claude Desktop**: If it's complex
   - "Here's the error I'm seeing..."
   - Get architectural guidance
   - Understand root cause

3. **Claude Code**: Apply fix
   - Modify code
   - Test fix
   - Commit changes

4. **Claude Desktop**: Document
   - Add to troubleshooting.md if relevant
   - Update decisions if architecture changes

---

### Workflow 3: Deploying to VPS

1. **Claude Desktop**: Prepare
   - Review deployment strategy
   - Download deployment files
   - Understand the process

2. **Claude Code**: File preparation
   - Copy deployment files
   - Update code
   - Test Docker builds
   - Commit to Git

3. **Claude Desktop**: VPS configuration
   - Guide through Coolify setup
   - Help with environment variables
   - Troubleshoot issues

4. **Claude Code**: Verification (optional)
   - SSH commands
   - Test API endpoints
   - Check logs

5. **Claude Desktop**: Documentation
   - Update services.md
   - Mark roadmap milestones
   - Document lessons learned

---

## Current Project Locations

### NEXUS Development Project
**Where:** Claude Desktop
**Path:** Project knowledge files (this conversation)
**Contains:**
- architecture.md
- decisions-log.md
- roadmap.md
- services.md
- troubleshooting.md
- idea-analyzer context files

### Idea Analyzer Project
**Where:** Claude Code (when working on it)
**Path:** `C:\Projects\idea-analyzer\`
**Contains:**
- Actual source code
- Dockerfiles
- Configuration files
- Local tests

---

## Pro Tips

### 💡 Tip 1: Keep Both Open
Have Claude Desktop (this Project) open while working in Claude Code.

**Why:** Quick context reference, strategic guidance, documentation.

### 💡 Tip 2: Copy-Paste Context
When switching tools, paste relevant context from the other tool.

**Example:**
- Claude Code makes changes → Copy summary to Claude Desktop
- Claude Desktop gives guidance → Copy to Claude Code as prompt

### 💡 Tip 3: Use MCP in Desktop
MCP tools work best in Claude Desktop for:
- Idea Analyzer operations (extract_url, list_extractions)
- Conversation search (finding past discussions)
- Service status checks

### 💡 Tip 4: Use Prompts in Code
Save common tasks as Prompts in Claude Code:
- "Deploy preparation"
- "Run all tests"
- "Git commit workflow"

### 💡 Tip 5: Strategic vs Tactical
- Strategic (what/why) → Claude Desktop
- Tactical (how/execute) → Claude Code

---

## Quick Reference Card

```
┌──────────────────────────────────────────┐
│      CLAUDE DESKTOP (This Project)      │
├──────────────────────────────────────────┤
│ Planning      │ Architecture            │
│ Strategy      │ Documentation           │
│ Decisions     │ Context                 │
│ Roadmap       │ Integration             │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────┐
│    CLAUDE CODE (Idea Analyzer Dir)       │
├──────────────────────────────────────────┤
│ Coding        │ Commands                │
│ Testing       │ Git                     │
│ Files         │ Building                │
│ Debugging     │ Execution               │
└──────────────────────────────────────────┘
```

---

## Right Now: What Should I Use?

### If you want to...

**Review the deployment files I created**
→ Claude Desktop (you're already here!)

**Start implementing the deployment**
→ Claude Code (use CLAUDE-CODE-PROMPTS.md)

**Understand the deployment strategy**
→ Claude Desktop (ask questions here)

**Actually modify the files**
→ Claude Code (execute the prompts)

**Update NEXUS documentation after deployment**
→ Claude Desktop (update roadmap, services, etc.)

---

## Still Unsure?

Ask yourself:
1. **Am I making decisions or executing decisions?**
   - Decisions → Desktop
   - Executing → Code

2. **Do I need to run commands?**
   - Yes → Code
   - No → Desktop

3. **Which project am I working on?**
   - Overall NEXUS → Desktop
   - Specific component → Code

4. **Am I planning or doing?**
   - Planning → Desktop
   - Doing → Code

---

**Default rule:** When in doubt, start in Claude Desktop (This Project) to plan, then move to Claude Code to execute.
