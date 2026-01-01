# Idea Analyzer

Extract, validate, and analyze ideas from any source using AI.

```
📱 Phone → Slack → 🖥️ Extractor → 🗄️ Database → 🤖 Claude → 📊 Report
```

## Features

- **Extract content from:**
  - 🎬 YouTube videos (with Whisper transcription)
  - 📄 Web articles and blog posts
  - 🔴 Reddit threads (posts + comments)
  - 🐙 GitHub repositories (README + structure)
  - 📎 Files (PDF, DOCX, audio, video)

- **Analyze with Claude:**
  - Idea extraction and validation
  - Market research
  - Competitor analysis
  - Risk assessment
  - Executive summary + full report
  - Preliminary design

---

## Quick Start (Windows)

### Prerequisites

1. **Docker Desktop** - [Download](https://docs.docker.com/get-docker/)
2. **Python 3.10+** - [Download](https://python.org)
3. **FFmpeg** - Install via `winget install ffmpeg`

### Installation

```powershell
# 1. Clone/download this folder to C:\idea-analyzer
cd C:\idea-analyzer

# 2. Run setup script
.\setup.bat

# 3. Edit .env file with your Slack tokens (see below)
notepad .env

# 4. Start services (in separate terminals)
.\start-extractor.bat    # Terminal 1
.\start-slack-bot.bat    # Terminal 2
```

---

## Setting Up Slack App

### Step 1: Create Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps)
2. Click **Create New App** → **From scratch**
3. Name it "Idea Analyzer" and select your workspace

### Step 2: Configure Bot

1. Go to **OAuth & Permissions**
2. Under **Bot Token Scopes**, add:
   - `chat:write`
   - `channels:history`
   - `files:read`
   - `app_mentions:read`

3. Click **Install to Workspace**
4. Copy the **Bot User OAuth Token** (starts with `xoxb-`)

### Step 3: Enable Socket Mode

1. Go to **Socket Mode**
2. Enable Socket Mode
3. Create an app-level token with `connections:write` scope
4. Copy the **App Token** (starts with `xapp-`)

### Step 4: Enable Events

1. Go to **Event Subscriptions**
2. Enable Events
3. Under **Subscribe to bot events**, add:
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `app_mention`

### Step 5: Get Signing Secret

1. Go to **Basic Information**
2. Copy the **Signing Secret**

### Step 6: Update .env File

```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
```

### Step 7: Invite Bot to Channel

In Slack, type: `/invite @Idea Analyzer`

---

## Usage

### From Slack

```
# Share any URL
https://youtube.com/watch?v=xxx

# Upload a file
[drag and drop file]

# List recent extractions
list

# Check extraction status
status abc123
```

### From Claude

After receiving extraction ID from Slack:

```
Analyze idea abc123
```

Claude will:
1. Fetch the transcript
2. Research the market
3. Analyze competitors
4. Generate executive summary
5. Offer full report and design

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Your Phone                             │
│   Share URL/file to Slack                                   │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                        Slack                                │
│   #idea-inbox channel                                       │
└─────────────────────────┬───────────────────────────────────┘
                          │ webhook
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Your PC (Docker)                         │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Slack Bot │→ │ Extractor │→ │ Postgres  │  │ PostgREST│  │
│  │ :3001     │  │ :8000     │  │ :5432     │  │ :3000    │  │
│  └───────────┘  └───────────┘  └───────────┘  └──────────┘  │
│                       ↓                                      │
│              ┌───────────────┐                               │
│              │    Whisper    │                               │
│              │ (transcription)│                               │
│              └───────────────┘                               │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼ (REST API)
┌─────────────────────────────────────────────────────────────┐
│                    Claude (Your Pro Sub)                    │
│   web_search + web_fetch for research                       │
│   Generate reports + designs                                │
└─────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /` | - | Health check |
| `POST /extract` | `{"url": "..."}` | Start extraction |
| `POST /extract/file` | multipart/form-data | Upload file |
| `GET /extraction/{id}` | - | Get extraction |
| `GET /extractions` | - | List all |

---

## Troubleshooting

### Docker not starting
```powershell
# Make sure Docker Desktop is running
# Check status
docker ps
```

### Whisper out of memory
Edit `.env` and use smaller model:
```env
WHISPER_MODEL=tiny  # or base, small
```

### Slack bot not responding
1. Check bot is invited to channel
2. Verify tokens in `.env`
3. Check Socket Mode is enabled

### Database connection error
```powershell
# Restart Docker services
docker-compose down
docker-compose up -d
```

---

## Customization

### Change Whisper Model

In `.env`:
```env
WHISPER_MODEL=small  # tiny, base, small, medium, large
```

| Model | RAM | Speed | Accuracy |
|-------|-----|-------|----------|
| tiny | 1GB | Fast | Basic |
| base | 1GB | Fast | OK |
| small | 2GB | Medium | Good |
| medium | 5GB | Slow | Better |
| large | 10GB | Slowest | Best |

### Add Custom Extractors

Create new file in `extractor/extractors/`:
```python
async def extract_custom(url: str) -> Dict[str, Any]:
    return {
        'title': 'Title',
        'content': 'Extracted content',
        'metadata': {}
    }
```

---

## Files Structure

```
idea-analyzer/
├── docker-compose.yml      # Docker services
├── .env                    # Configuration
├── setup.bat               # Setup script
├── start-extractor.bat     # Start extractor
├── start-slack-bot.bat     # Start Slack bot
│
├── extractor/              # Extraction service
│   ├── main.py             # FastAPI app
│   ├── requirements.txt
│   └── extractors/
│       ├── youtube.py
│       ├── article.py
│       ├── reddit.py
│       ├── github.py
│       └── file_extractor.py
│
├── slack-bot/              # Slack integration
│   ├── app.py
│   └── requirements.txt
│
├── supabase/               # Database
│   └── schema.sql
│
└── claude-skill/           # Claude instructions
    └── SKILL.md
```

---

## License

MIT - Use freely for personal projects.
