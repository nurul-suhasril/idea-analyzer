"""
Idea Analyzer - Slack Bot
Receives URLs and files from Slack and triggers extraction
"""

import os
import re
import asyncio
from dotenv import load_dotenv

from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
import httpx

load_dotenv()

# Initialize Slack app
app = AsyncApp(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

# Extractor service URL
EXTRACTOR_URL = os.getenv("EXTRACTOR_URL", "http://localhost:8000")

# URL patterns
URL_PATTERN = re.compile(
    r'https?://[^\s<>"\'\])]+'
)

def detect_url_type(url: str) -> str:
    """Detect URL type for display"""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "🎬 YouTube"
    elif "reddit.com" in url_lower:
        return "🔴 Reddit"
    elif "github.com" in url_lower:
        return "🐙 GitHub"
    else:
        return "📄 Article"

@app.event("message")
async def handle_message(event, say, client):
    """Handle incoming messages"""
    
    # Ignore bot messages
    if event.get("bot_id"):
        return
    
    text = event.get("text", "")
    channel = event.get("channel")
    thread_ts = event.get("thread_ts") or event.get("ts")
    user = event.get("user")
    
    # Check for URLs
    urls = URL_PATTERN.findall(text)
    
    # Check for files
    files = event.get("files", [])
    
    if not urls and not files:
        # Check for commands
        if text.lower().strip() == "list":
            await handle_list_command(say, channel, thread_ts)
        elif text.lower().strip().startswith("status "):
            extraction_id = text.strip().split(" ")[1]
            await handle_status_command(say, extraction_id, thread_ts)
        return
    
    # Process URLs
    for url in urls:
        # Clean URL (remove trailing punctuation)
        url = url.rstrip('.,;:!?')
        url_type = detect_url_type(url)
        
        # Send initial response
        await say(
            text=f"{url_type} detected. Processing...",
            thread_ts=thread_ts
        )
        
        # Call extractor service
        try:
            async with httpx.AsyncClient(timeout=30.0) as http_client:
                response = await http_client.post(
                    f"{EXTRACTOR_URL}/extract",
                    json={
                        "url": url,
                        "slack_channel_id": channel,
                        "slack_thread_ts": thread_ts
                    }
                )
                result = response.json()
                
                extraction_id = result.get("id", "unknown")
                
                await say(
                    text=f"✅ Extraction started!\n"
                         f"• ID: `{extraction_id}`\n"
                         f"• Status: Processing\n\n"
                         f"When ready, tell Claude: `Analyze idea {extraction_id}`",
                    thread_ts=thread_ts
                )
                
        except Exception as e:
            await say(
                text=f"❌ Error starting extraction: {str(e)}",
                thread_ts=thread_ts
            )
    
    # Process files
    for file_info in files:
        file_name = file_info.get("name", "unknown")
        file_url = file_info.get("url_private_download")
        
        if not file_url:
            continue
        
        await say(
            text=f"📎 File detected: `{file_name}`. Processing...",
            thread_ts=thread_ts
        )
        
        try:
            # Download file from Slack
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                # Get file from Slack
                file_response = await http_client.get(
                    file_url,
                    headers={"Authorization": f"Bearer {os.environ.get('SLACK_BOT_TOKEN')}"}
                )
                file_content = file_response.content
                
                # Send to extractor
                response = await http_client.post(
                    f"{EXTRACTOR_URL}/extract/file",
                    files={"file": (file_name, file_content)},
                    data={
                        "slack_channel_id": channel,
                        "slack_thread_ts": thread_ts
                    }
                )
                result = response.json()
                
                extraction_id = result.get("id", "unknown")
                
                await say(
                    text=f"✅ File extraction started!\n"
                         f"• ID: `{extraction_id}`\n"
                         f"• File: {file_name}\n\n"
                         f"When ready, tell Claude: `Analyze idea {extraction_id}`",
                    thread_ts=thread_ts
                )
                
        except Exception as e:
            await say(
                text=f"❌ Error processing file: {str(e)}",
                thread_ts=thread_ts
            )

async def handle_list_command(say, channel, thread_ts):
    """List recent extractions"""
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(
                f"{EXTRACTOR_URL}/extractions",
                params={"limit": 10}
            )
            extractions = response.json()
            
            if not extractions:
                await say(
                    text="📋 No extractions found.",
                    thread_ts=thread_ts
                )
                return
            
            lines = ["📋 **Recent Extractions:**\n"]
            
            for ext in extractions:
                status_emoji = {
                    "completed": "✅",
                    "processing": "🔄",
                    "pending": "⏳",
                    "failed": "❌"
                }.get(ext["status"], "❓")
                
                source_emoji = {
                    "youtube": "🎬",
                    "reddit": "🔴",
                    "github": "🐙",
                    "article": "📄",
                    "file": "📎"
                }.get(ext["source_type"], "📄")
                
                title = ext.get("title", "Untitled")
                if len(title) > 40:
                    title = title[:37] + "..."
                
                lines.append(
                    f"{status_emoji} `{ext['id']}` {source_emoji} {title}"
                )
            
            await say(
                text="\n".join(lines),
                thread_ts=thread_ts
            )
            
    except Exception as e:
        await say(
            text=f"❌ Error fetching list: {str(e)}",
            thread_ts=thread_ts
        )

async def handle_status_command(say, extraction_id, thread_ts):
    """Check status of an extraction"""
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.get(
                f"{EXTRACTOR_URL}/extraction/{extraction_id}"
            )
            
            if response.status_code == 404:
                await say(
                    text=f"❌ Extraction `{extraction_id}` not found.",
                    thread_ts=thread_ts
                )
                return
            
            ext = response.json()
            
            status_emoji = {
                "completed": "✅",
                "processing": "🔄",
                "pending": "⏳",
                "failed": "❌"
            }.get(ext["status"], "❓")
            
            message = f"{status_emoji} **Extraction {extraction_id}**\n"
            message += f"• Status: {ext['status']}\n"
            message += f"• Type: {ext['source_type']}\n"
            
            if ext.get("title"):
                message += f"• Title: {ext['title']}\n"
            
            if ext["status"] == "failed" and ext.get("error_message"):
                message += f"• Error: {ext['error_message']}\n"
            
            if ext["status"] == "completed":
                message += f"\nReady to analyze! Tell Claude: `Analyze idea {extraction_id}`"
            
            await say(
                text=message,
                thread_ts=thread_ts
            )
            
    except Exception as e:
        await say(
            text=f"❌ Error fetching status: {str(e)}",
            thread_ts=thread_ts
        )

@app.event("app_mention")
async def handle_mention(event, say):
    """Handle when bot is mentioned"""
    
    await say(
        text="👋 Hi! I'm the Idea Analyzer bot.\n\n"
             "**How to use:**\n"
             "• Share any URL (YouTube, Reddit, GitHub, articles)\n"
             "• Upload a file (PDF, audio, video, etc.)\n"
             "• Type `list` to see recent extractions\n"
             "• Type `status <id>` to check extraction status\n\n"
             "After extraction, analyze with Claude using: `Analyze idea <id>`",
        thread_ts=event.get("ts")
    )

async def main():
    """Start the Slack bot"""
    
    handler = AsyncSocketModeHandler(
        app, 
        os.environ.get("SLACK_APP_TOKEN")
    )
    
    print("⚡ Slack bot starting...")
    await handler.start_async()

if __name__ == "__main__":
    asyncio.run(main())
