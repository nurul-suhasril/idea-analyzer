# Idea Analyzer Skill

## Overview
This skill enables Claude to analyze ideas extracted from various sources (YouTube videos, articles, Reddit posts, GitHub repos, etc.) that have been processed by the Idea Analyzer extraction service.

## Configuration

**Extraction Service URL:** `http://YOUR_SERVER_IP:8000`

Replace `YOUR_SERVER_IP` with your actual server IP or domain.

## Available Commands

### 1. Analyze Idea
Trigger: User says "Analyze idea [ID]" or "Analyze [ID]"

**Process:**
1. Fetch the extracted content from the API
2. Clean and structure the transcript
3. Extract the core idea/concept
4. Conduct web research for validation
5. Analyze competitors and alternatives
6. Generate executive summary and full report

### 2. List Extractions
Trigger: User says "List extractions" or "Show my ideas"

**Process:**
1. Fetch recent extractions from the API
2. Display in a formatted list

### 3. Design Idea
Trigger: User says "Design [ID]" or "Create design for [ID]"

**Process:**
1. Fetch the extraction and any existing analysis
2. Generate preliminary technical design

---

## Workflow: Analyze Idea

When the user asks to analyze an idea, follow this workflow:

### Step 1: Fetch Content
```bash
curl -s "http://YOUR_SERVER_IP:8000/extraction/[ID]"
```

### Step 2: Clean Transcript
Remove filler words, timestamps, and format the content for analysis.

### Step 3: Extract Core Idea
Identify:
- Main concept/proposition
- Key claims made
- Target audience
- Proposed benefits
- Required resources/skills

### Step 4: Generate Research Questions
Create 5-7 specific questions to validate this idea:
- Market size and demand
- Existing solutions/competitors
- Technical feasibility
- Potential challenges
- Success stories/failures

### Step 5: Conduct Web Research
Use `web_search` to research each question. Prioritize:
- Recent news and trends
- Competitor analysis
- Market data
- Expert opinions
- Case studies

### Step 6: Validate Idea
Assess:
- Is this idea solving a real problem?
- What's the market size?
- Who are the competitors?
- What are the barriers to entry?
- What are the risks?

### Step 7: Generate Reports

**Executive Summary (1 page max):**
```markdown
# Executive Summary: [Idea Title]

## The Idea
[2-3 sentence description]

## Viability Score: [X/10]

## Top 3 Opportunities
1. [Opportunity 1]
2. [Opportunity 2]
3. [Opportunity 3]

## Top 3 Risks
1. [Risk 1]
2. [Risk 2]
3. [Risk 3]

## Recommendation
[✅ Pursue / 🔍 Research More / ❌ Pass]

[Brief justification]
```

**Full Report:**
```markdown
# Full Analysis: [Idea Title]

## 1. Idea Overview
[Detailed breakdown of the concept]

## 2. Market Analysis
[Market size, trends, demand]

## 3. Competitor Landscape
[Existing solutions, their strengths/weaknesses]

## 4. Technical Feasibility
[What's needed to build this]

## 5. Resource Requirements
[Time, money, skills needed]

## 6. Risk Analysis
[Detailed risks and mitigations]

## 7. Validation Summary
[Key findings from research]

## 8. Sources
[List of sources used]
```

---

## Workflow: Preliminary Design

When user wants to proceed with an idea:

```markdown
# Preliminary Design: [Idea Title]

## 1. System Architecture
[High-level architecture diagram description]

## 2. Recommended Tech Stack
- Frontend: [recommendation]
- Backend: [recommendation]
- Database: [recommendation]
- Infrastructure: [recommendation]

## 3. MVP Features
[Prioritized list of must-have features]

## 4. Implementation Phases
- Phase 1 (Week 1-2): [scope]
- Phase 2 (Week 3-4): [scope]
- Phase 3 (Week 5-6): [scope]

## 5. Estimated Effort
[Time and resource estimates]

## 6. Next Steps
[Actionable next steps to start]
```

---

## Example Usage

**User:** Analyze idea abc123

**Claude:** 
1. Fetches content from extraction service
2. Analyzes and researches
3. Presents executive summary
4. Offers full report
5. Asks if user wants preliminary design

---

## API Reference

**Base URL:** `http://YOUR_SERVER_IP:8000`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/extraction/{id}` | GET | Get extraction by ID |
| `/extractions` | GET | List recent extractions |
| `/extractions?status=completed` | GET | Filter by status |

**Response Format:**
```json
{
  "id": "abc123",
  "url": "https://...",
  "source_type": "youtube",
  "title": "Video Title",
  "raw_transcript": "...",
  "metadata": {...},
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z"
}
```
