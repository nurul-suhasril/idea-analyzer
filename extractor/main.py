"""
Idea Analyzer - Extraction Service
FastAPI app that extracts content from various sources
"""

import os
import string
import random
import asyncio
from datetime import datetime
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Import authentication
from auth import verify_api_key, is_auth_enabled

# Import extractors
from extractors.youtube import extract_youtube
from extractors.article import extract_article
from extractors.reddit import extract_reddit
from extractors.github import extract_github
from extractors.file_extractor import extract_file

load_dotenv()

# Database connection
def get_db():
    return psycopg2.connect(
        os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/idea_analyzer"),
        cursor_factory=RealDictCursor
    )

# Redis connection
redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Extractor service starting...")
    yield
    # Shutdown
    print("👋 Extractor service shutting down...")

app = FastAPI(
    title="Idea Analyzer - Extractor",
    description="Extract content from YouTube, articles, Reddit, GitHub, and files",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ExtractionRequest(BaseModel):
    url: str
    slack_channel_id: Optional[str] = None
    slack_thread_ts: Optional[str] = None

class ExtractionResponse(BaseModel):
    id: str
    status: str
    message: str

def generate_id(length=8):
    """Generate a random ID"""
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def detect_source_type(url: str) -> str:
    """Detect the type of source from URL"""
    url_lower = url.lower()
    
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "reddit.com" in url_lower:
        return "reddit"
    elif "github.com" in url_lower:
        return "github"
    else:
        return "article"

async def process_extraction(extraction_id: str, url: str, source_type: str):
    """Background task to process extraction"""
    conn = get_db()
    cur = conn.cursor()
    
    try:
        # Update status to processing
        cur.execute(
            "UPDATE extractions SET status = 'processing' WHERE id = %s",
            (extraction_id,)
        )
        conn.commit()
        
        # Extract based on source type
        if source_type == "youtube":
            result = await extract_youtube(url)
        elif source_type == "reddit":
            result = await extract_reddit(url)
        elif source_type == "github":
            result = await extract_github(url)
        else:
            result = await extract_article(url)
        
        # Update with results
        cur.execute(
            """
            UPDATE extractions 
            SET status = 'completed',
                title = %s,
                raw_transcript = %s,
                metadata = %s
            WHERE id = %s
            """,
            (result["title"], result["content"], 
             psycopg2.extras.Json(result.get("metadata", {})), extraction_id)
        )
        conn.commit()
        
        print(f"✅ Extraction {extraction_id} completed: {result['title']}")
        
    except Exception as e:
        cur.execute(
            "UPDATE extractions SET status = 'failed', error_message = %s WHERE id = %s",
            (str(e), extraction_id)
        )
        conn.commit()
        print(f"❌ Extraction {extraction_id} failed: {e}")
    
    finally:
        cur.close()
        conn.close()

@app.get("/")
async def root():
    return {"status": "running", "service": "Idea Analyzer Extractor"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "idea-analyzer-extractor",
        "auth_enabled": is_auth_enabled()
    }

@app.post("/extract", response_model=ExtractionResponse, dependencies=[Depends(verify_api_key)])
async def create_extraction(request: ExtractionRequest, background_tasks: BackgroundTasks):
    """Create a new extraction job"""
    
    extraction_id = generate_id()
    source_type = detect_source_type(request.url)
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO extractions (id, url, source_type, status, slack_channel_id, slack_thread_ts)
            VALUES (%s, %s, %s, 'pending', %s, %s)
            """,
            (extraction_id, request.url, source_type, 
             request.slack_channel_id, request.slack_thread_ts)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
    
    # Start background extraction
    background_tasks.add_task(process_extraction, extraction_id, request.url, source_type)
    
    return ExtractionResponse(
        id=extraction_id,
        status="pending",
        message=f"Extraction started for {source_type} content"
    )

@app.post("/extract/file", response_model=ExtractionResponse, dependencies=[Depends(verify_api_key)])
async def extract_from_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    slack_channel_id: Optional[str] = None,
    slack_thread_ts: Optional[str] = None
):
    """Extract content from uploaded file"""
    
    extraction_id = generate_id()
    
    # Save file temporarily
    temp_path = f"/tmp/{extraction_id}_{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute(
            """
            INSERT INTO extractions (id, url, source_type, status, slack_channel_id, slack_thread_ts)
            VALUES (%s, %s, 'file', 'pending', %s, %s)
            """,
            (extraction_id, file.filename, slack_channel_id, slack_thread_ts)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()
    
    # Start background extraction
    async def process_file():
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE extractions SET status = 'processing' WHERE id = %s",
                (extraction_id,)
            )
            conn.commit()
            
            result = await extract_file(temp_path, file.filename)
            
            cur.execute(
                """
                UPDATE extractions 
                SET status = 'completed', title = %s, raw_transcript = %s, metadata = %s
                WHERE id = %s
                """,
                (result["title"], result["content"],
                 psycopg2.extras.Json(result.get("metadata", {})), extraction_id)
            )
            conn.commit()
            
            # Cleanup temp file
            os.remove(temp_path)
            
        except Exception as e:
            cur.execute(
                "UPDATE extractions SET status = 'failed', error_message = %s WHERE id = %s",
                (str(e), extraction_id)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()
    
    background_tasks.add_task(process_file)
    
    return ExtractionResponse(
        id=extraction_id,
        status="pending",
        message=f"File extraction started for {file.filename}"
    )

@app.get("/extraction/{extraction_id}", dependencies=[Depends(verify_api_key)])
async def get_extraction(extraction_id: str):
    """Get extraction by ID"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT * FROM extractions WHERE id = %s", (extraction_id,))
        result = cur.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        return dict(result)
    finally:
        cur.close()
        conn.close()

@app.get("/extractions", dependencies=[Depends(verify_api_key)])
async def list_extractions(limit: int = 20, status: Optional[str] = None):
    """List recent extractions"""
    
    conn = get_db()
    cur = conn.cursor()
    
    try:
        if status:
            cur.execute(
                "SELECT * FROM extractions WHERE status = %s ORDER BY created_at DESC LIMIT %s",
                (status, limit)
            )
        else:
            cur.execute(
                "SELECT * FROM extractions ORDER BY created_at DESC LIMIT %s",
                (limit,)
            )
        
        results = cur.fetchall()
        return [dict(r) for r in results]
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("EXTRACTOR_HOST", "0.0.0.0"),
        port=int(os.getenv("EXTRACTOR_PORT", 8000)),
        reload=True
    )
