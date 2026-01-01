# Idea Analyzer - Comprehensive Project Summary

**Version:** 1.0.0
**Created:** 2026-01-01
**Platform:** Windows-based development with Docker

---

## 1. Project Structure

```
idea-analyzer/
├── .env                          # Environment configuration (not in repo)
├── .env.example                  # Template for environment variables
├── README.md                     # User documentation
├── docker-compose.yml            # Docker orchestration config
├── setup.bat                     # Windows setup script
├── start-extractor.bat           # Start extraction service
├── start-slack-bot.bat           # Start Slack bot
│
├── mcp-server/                   # Model Context Protocol server
│   ├── package.json              # Node.js dependencies
│   └── index.js                  # MCP server implementation
│
├── extractor/                    # Content extraction service
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt          # Python dependencies
│   └── extractors/               # Source-specific extractors
│       ├── __init__.py
│       ├── article.py            # Web article extractor (Trafilatura)
│       ├── file_extractor.py     # File upload handler
│       ├── github.py             # GitHub repository extractor
│       ├── reddit.py             # Reddit thread extractor
│       └── youtube.py            # YouTube video/transcript extractor
│
├── slack-bot/                    # Slack integration
│   ├── app.py                    # Slack Bolt async app
│   └── requirements.txt          # Python dependencies
│
├── supabase/                     # Database
│   └── schema.sql                # PostgreSQL schema definition
│
├── claude-skill/                 # Claude integration guide
│   └── SKILL.md                  # Analysis workflow documentation
│
└── venv/                         # Python virtual environment (local)
```

---

## 2. Tech Stack

### Backend Services
- **Python 3.10+** - Main application language
- **FastAPI** - Extraction service web framework
- **Slack Bolt (Async)** - Slack integration framework
- **Node.js** - MCP server runtime

### Content Extraction
- **yt-dlp** - YouTube video/audio downloading
- **OpenAI Whisper** - Audio transcription (configurable models: tiny/base/small/medium/large)
- **Trafilatura** - Web article text extraction
- **PRAW** - Reddit API wrapper
- **PyGithub** - GitHub API client
- **PyMuPDF** - PDF text extraction
- **python-docx** - Word document parsing

### Infrastructure & Storage
- **PostgreSQL 15** - Primary database
- **Redis 7** - Job queue (currently unused, planned for Celery)
- **PostgREST** - Auto-generated REST API for Postgres
- **Docker & Docker Compose** - Service orchestration

### API & Communication
- **httpx** - Async HTTP client
- **MCP SDK** (@modelcontextprotocol/sdk) - Model Context Protocol implementation

---

## 3. Services

The application runs 5 containerized/local services:

| Service | Type | Port | Description |
|---------|------|------|-------------|
| **postgres** | Docker | 5432 | PostgreSQL database storing extractions & analyses |
| **redis** | Docker | 6379 | Redis for job queue (planned for background tasks) |
| **postgrest** | Docker | 3000 | REST API auto-generated from Postgres schema |
| **extractor** | Python (local) | 8000 | FastAPI service for content extraction |
| **slack-bot** | Python (local) | N/A | Slack event listener via Socket Mode |

### Service Dependencies
```
postgres (healthy) ← postgrest
redis (standalone)
extractor → postgres (direct connection)
slack-bot → extractor (HTTP API)
```

---

## 4. Database Schema

### Tables

#### **extractions**
Primary table storing all extracted content.

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(12) PRIMARY KEY | Random 8-char ID (e.g., "fgnb0h2x") |
| `url` | TEXT | Source URL or filename |
| `source_type` | VARCHAR(20) | Type: youtube, article, reddit, github, file |
| `title` | TEXT | Extracted title |
| `raw_transcript` | TEXT | Full extracted content/transcript |
| `cleaned_transcript` | TEXT | Cleaned version (not currently used) |
| `metadata` | JSONB | Source-specific metadata (duration, author, etc.) |
| `status` | VARCHAR(20) | pending, processing, completed, failed |
| `error_message` | TEXT | Error details if status=failed |
| `slack_channel_id` | VARCHAR(50) | Originating Slack channel |
| `slack_thread_ts` | VARCHAR(50) | Slack thread timestamp |
| `created_at` | TIMESTAMP WITH TIME ZONE | Auto-set on creation |
| `updated_at` | TIMESTAMP WITH TIME ZONE | Auto-updated via trigger |

**Indexes:**
- `idx_extractions_status` on `status`
- `idx_extractions_source_type` on `source_type`
- `idx_extractions_created_at` on `created_at DESC`

#### **analyses**
Stores Claude's analysis results (table exists but not currently populated by code).

| Column | Type | Description |
|--------|------|-------------|
| `id` | VARCHAR(12) PRIMARY KEY | Random ID |
| `extraction_id` | VARCHAR(12) | Foreign key → extractions(id) |
| `executive_summary` | TEXT | Brief summary of analysis |
| `full_report` | TEXT | Detailed analysis |
| `preliminary_design` | TEXT | Technical design if applicable |
| `viability_score` | INTEGER | Score out of 10 |
| `recommendation` | VARCHAR(20) | pursue, research_more, pass |
| `created_at` | TIMESTAMP WITH TIME ZONE | Analysis timestamp |

**Indexes:**
- `idx_analyses_extraction_id` on `extraction_id`

### Triggers
- `update_extractions_updated_at` - Auto-updates `updated_at` on row modification

---

## 5. API Endpoints

### Extractor Service (Port 8000)

| Endpoint | Method | Description | Request Body | Response |
|----------|--------|-------------|--------------|----------|
| `GET /` | GET | Health check | N/A | `{"status": "running", "service": "..."}` |
| `GET /health` | GET | Health check | N/A | `{"status": "healthy"}` |
| `POST /extract` | POST | Start URL extraction | `{"url": "...", "slack_channel_id": "...", "slack_thread_ts": "..."}` | `{"id": "...", "status": "pending", "message": "..."}` |
| `POST /extract/file` | POST | Upload file for extraction | multipart/form-data: `file`, `slack_channel_id`, `slack_thread_ts` | `{"id": "...", "status": "pending", "message": "..."}` |
| `GET /extraction/{id}` | GET | Get extraction by ID | N/A | Full extraction object with transcript |
| `GET /extractions` | GET | List recent extractions | Query: `limit` (default 20), `status` | Array of extraction objects |

### PostgREST (Port 3000)
Auto-generated REST API providing direct database access:
- `GET /extractions` - Query extractions table
- `GET /analyses` - Query analyses table
- Supports filtering, ordering, pagination via query params

---

## 6. MCP Tools

The MCP server exposes 4 tools for Claude to interact with the system:

### **get_extraction**
Retrieves a specific extraction by ID.

**Input:**
```json
{
  "id": "abc123"
}
```

**Returns:** Full extraction object including transcript, metadata, status.

### **list_extractions**
Lists recent extractions with optional filtering.

**Input:**
```json
{
  "limit": 20,          // Optional, default 20
  "status": "completed" // Optional: pending, processing, completed, failed
}
```

**Returns:** Array of extraction summaries (id, title, type, status, created).

### **extract_url**
Starts a new extraction from a URL.

**Input:**
```json
{
  "url": "https://youtube.com/watch?v=..."
}
```

**Returns:** Extraction ID and status message.

**Supported URLs:**
- YouTube videos (youtube.com, youtu.be)
- Reddit threads (reddit.com)
- GitHub repositories (github.com)
- Web articles (any other URL)

### **check_service_status**
Verifies the extractor service is running.

**Input:** None

**Returns:** Service health status message.

---

## 7. Environment Variables

Required configuration in `.env` file:

### Database
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/idea_analyzer
POSTGREST_URL=http://localhost:3000
```

### Redis
```env
REDIS_URL=redis://localhost:6379
```

### Slack Bot
**Required** - Get from [api.slack.com/apps](https://api.slack.com/apps)
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
```

**Required Scopes:**
- `chat:write`
- `channels:history`
- `files:read`
- `app_mentions:read`

**Socket Mode:** Must be enabled with `connections:write` scope.

### Reddit API (Optional)
Get from [reddit.com/prefs/apps](https://www.reddit.com/prefs/apps)
```env
REDDIT_CLIENT_ID=your-client-id
REDDIT_CLIENT_SECRET=your-client-secret
REDDIT_USER_AGENT=IdeaAnalyzer/1.0
```

### GitHub (Optional)
For private repository access:
```env
GITHUB_TOKEN=your-github-token
```

### Extractor Service
```env
EXTRACTOR_HOST=0.0.0.0
EXTRACTOR_PORT=8000
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
```

**Whisper Model Selection:**

| Model | RAM | Speed | Accuracy |
|-------|-----|-------|----------|
| tiny | 1GB | Fast | Basic |
| base | 1GB | Fast | OK |
| small | 2GB | Medium | Good |
| medium | 5GB | Slow | Better |
| large | 10GB | Slowest | Best |

---

## 8. How to Run

### Prerequisites
1. **Docker Desktop** - [Download](https://docs.docker.com/get-docker/)
2. **Python 3.10+** - [Download](https://python.org)
3. **FFmpeg** - Install via `winget install ffmpeg`

### Initial Setup

```powershell
# 1. Clone/navigate to project
cd C:\Projects\idea-analyzer

# 2. Run setup (installs dependencies, starts Docker)
.\setup.bat

# 3. Configure Slack tokens
notepad .env
```

### Starting Services

**Terminal 1 - Extractor Service:**
```powershell
.\start-extractor.bat
```
This runs: `python extractor/main.py` (FastAPI on port 8000)

**Terminal 2 - Slack Bot:**
```powershell
.\start-slack-bot.bat
```
This runs: `python slack-bot/app.py` (Slack Socket Mode listener)

### Using from Slack

1. Invite bot to channel: `/invite @Idea Analyzer`
2. Share a URL: `https://youtube.com/watch?v=...`
3. Or upload a file (PDF, audio, video)
4. Bot responds with extraction ID: `abc123`

### Using from Claude (via MCP)

```
# List recent extractions
list_extractions

# Get specific extraction
get_extraction {"id": "abc123"}

# Start new extraction
extract_url {"url": "https://..."}

# Check if service is running
check_service_status
```

### Using the Claude Skill

In Claude conversation (after extraction completes):
```
Analyze idea abc123
```

Claude will:
1. Fetch the transcript via MCP
2. Extract core idea
3. Conduct web research
4. Generate executive summary
5. Offer full report and preliminary design

---

## 9. Docker Configuration

### docker-compose.yml

**Version:** 3.8

**Services:**

#### postgres
- **Image:** postgres:15
- **Container:** idea-postgres
- **Ports:** 5432:5432
- **Volumes:**
  - Named volume: `postgres_data`
  - Init script: `./supabase/schema.sql`
- **Health Check:** `pg_isready -U postgres` every 10s

#### redis
- **Image:** redis:7-alpine
- **Container:** idea-redis
- **Ports:** 6379:6379
- **Volumes:** Named volume: `redis_data`

#### postgrest
- **Image:** postgrest/postgrest
- **Container:** idea-postgrest
- **Ports:** 3000:3000
- **Depends On:** postgres (healthy)
- **Config:**
  - DB URI: `postgres://postgres:postgres@postgres:5432/idea_analyzer`
  - Schema: `public`
  - Role: `postgres`

**Volumes:**
- `postgres_data` - Persists database
- `redis_data` - Persists Redis data

### Running Docker Services

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart specific service
docker-compose restart postgres
```

---

## 10. Current Status

### ✅ What Works

**Extraction:**
- ✅ YouTube video transcription (via subtitles or Whisper)
- ✅ Web article extraction (Trafilatura)
- ✅ File upload handling (PDF, DOCX, audio, video)
- ✅ GitHub repository extraction (implemented)
- ✅ Reddit thread extraction (implemented)

**Slack Integration:**
- ✅ URL detection and auto-extraction
- ✅ File upload handling
- ✅ Socket Mode event handling
- ✅ Commands: `list`, `status <id>`
- ✅ Threaded responses

**MCP Server:**
- ✅ All 4 tools functional
- ✅ Connects to extractor service
- ✅ Returns formatted data to Claude

**Database:**
- ✅ PostgreSQL schema with auto-migrations
- ✅ Extraction status tracking
- ✅ Metadata storage (JSONB)
- ✅ PostgREST API layer

**Infrastructure:**
- ✅ Docker Compose orchestration
- ✅ Windows batch scripts for setup/startup
- ✅ Health checks and auto-restart

### 🚧 What's Incomplete

**Background Processing:**
- ⚠️ Redis is running but not utilized
- ⚠️ Celery is in requirements but not configured
- ⚠️ Long extractions block FastAPI worker (should be async queue)

**Analysis Storage:**
- ⚠️ `analyses` table exists but never written to
- ⚠️ Claude's analyses are not persisted
- ⚠️ No way to retrieve past analysis results

**Error Handling:**
- ⚠️ Limited retry logic for failed extractions
- ⚠️ No cleanup of failed temp files
- ⚠️ Slack error messages could be more descriptive

**Testing:**
- ❌ No unit tests
- ❌ No integration tests
- ❌ No CI/CD pipeline

**Documentation:**
- ⚠️ MCP server installation not documented for end users
- ⚠️ No API documentation (Swagger/OpenAPI)
- ⚠️ Missing contribution guidelines

**Features:**
- ❌ No web UI (CLI/Slack only)
- ❌ No user authentication
- ❌ No extraction history cleanup (old extractions persist forever)
- ❌ No rate limiting on API endpoints

### 🔮 Planned Enhancements

**High Priority:**
1. Implement Celery worker for async extraction jobs
2. Store Claude's analysis results in `analyses` table
3. Add retry mechanism for failed extractions
4. Create web dashboard for viewing extractions/analyses

**Medium Priority:**
1. Add Swagger/OpenAPI documentation
2. Implement extraction TTL/cleanup job
3. Add rate limiting and authentication
4. Improve error messages and logging

**Low Priority:**
1. Unit test coverage
2. CI/CD with GitHub Actions
3. Support for additional file types (audio formats, epub, markdown)
4. Export analysis reports as PDF/DOCX

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                         │
├──────────────────┬──────────────────────┬──────────────────────┤
│  Slack Mobile    │   Claude Desktop     │   MCP Client         │
│  (Share URLs)    │   (Analysis)         │   (API Access)       │
└────────┬─────────┴──────────┬───────────┴────────┬─────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌────────────────┐  ┌────────────────────┐
│   Slack Bot     │  │   MCP Server   │  │   PostgREST API   │
│   (Socket Mode) │  │   (Node.js)    │  │   (Auto-gen)      │
│   Port: N/A     │  │   Port: stdio  │  │   Port: 3000      │
└────────┬────────┘  └────────┬───────┘  └─────────┬──────────┘
         │                    │                     │
         │                    │                     │
         ▼                    ▼                     │
┌──────────────────────────────────────────────────┘
│            Extractor Service (FastAPI)            │
│                  Port: 8000                       │
│                                                   │
│  ┌──────────────────────────────────────┐        │
│  │  Extractors:                         │        │
│  │  • YouTube (yt-dlp + Whisper)        │        │
│  │  • Article (Trafilatura)             │        │
│  │  • Reddit (PRAW)                     │        │
│  │  • GitHub (PyGithub)                 │        │
│  │  • File (PyMuPDF, python-docx)       │        │
│  └──────────────────────────────────────┘        │
└───────────────────┬──────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│             Docker Services (Compose)            │
├──────────────────┬───────────────────────────────┤
│  PostgreSQL 15   │  Redis 7       │  PostgREST  │
│  Port: 5432      │  Port: 6379    │  Port: 3000 │
│                  │                │             │
│  Tables:         │  (Planned for  │  REST API   │
│  • extractions   │   Celery)      │  over DB    │
│  • analyses      │                │             │
└──────────────────┴────────────────┴─────────────┘
```

---

## Key Workflows

### 1. URL Extraction via Slack
```
User shares URL → Slack Bot detects URL → POST /extract
→ Create extraction record (status=pending)
→ Background task: Download & extract content
→ Update record (status=completed, raw_transcript=content)
→ Slack receives extraction ID
```

### 2. Analysis via Claude (MCP)
```
User: "Analyze idea abc123" → Claude calls get_extraction tool
→ MCP server: GET /extraction/abc123
→ Returns transcript to Claude
→ Claude performs web research
→ Claude generates analysis (not saved to DB)
→ Returns report to user
```

### 3. File Upload via Slack
```
User uploads file → Slack Bot downloads file
→ POST /extract/file (multipart form)
→ Save to /tmp
→ Background: Extract text/transcribe
→ Update database
→ Clean up temp file
```

---

## Dependencies Summary

### Python (Extractor)
```
fastapi==0.109.0
uvicorn==0.27.0
python-multipart==0.0.6
httpx==0.26.0
redis==5.0.1
psycopg2-binary==2.9.9
yt-dlp==2024.1.4
openai-whisper==20231117
trafilatura==1.6.3
praw==7.7.1
PyGithub==2.1.1
python-dotenv==1.0.0
celery==5.3.6
```

### Python (Slack Bot)
```
slack-bolt==1.18.1
slack-sdk==3.26.1
python-dotenv==1.0.0
httpx==0.26.0
aiofiles==23.2.1
```

### Node.js (MCP Server)
```json
{
  "@modelcontextprotocol/sdk": "^1.0.0"
}
```

---

## Security Considerations

⚠️ **Current Security Issues:**

1. **No Authentication:** PostgREST and Extractor API are open
2. **Credentials in .env:** Slack tokens stored in plaintext
3. **No Input Validation:** URLs and files not sanitized
4. **SQL Injection Risk:** Some direct SQL queries (though using parameterization)
5. **No Rate Limiting:** APIs vulnerable to abuse
6. **CORS Wide Open:** `allow_origins=["*"]`

🔒 **Recommended Mitigations:**

1. Add JWT-based authentication to PostgREST
2. Use environment-specific secrets management (Azure Key Vault, AWS Secrets Manager)
3. Implement input validation and file type restrictions
4. Add rate limiting middleware (slowapi)
5. Restrict CORS to known origins
6. Enable HTTPS with SSL certificates in production

---

## Performance Notes

**Bottlenecks:**
- Whisper transcription can take 1-5 minutes for long videos
- Large file uploads block the FastAPI worker
- No caching for repeated URL extractions

**Optimizations Needed:**
1. Move extraction to Celery background workers
2. Add Redis caching for transcripts
3. Implement streaming responses for large files
4. Use connection pooling for Postgres

---

## Contact & Support

This is a personal/prototype project. For questions or issues:

1. Check the [README.md](README.md) for setup help
2. Review [SKILL.md](claude-skill/SKILL.md) for Claude integration
3. File issues or questions as appropriate

---

**End of Project Summary**
*Last Updated: 2026-01-01*
