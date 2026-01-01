"""
File Extractor
Extracts content from uploaded files (PDF, DOCX, TXT, audio, video, etc.)
"""

import os
import asyncio
import mimetypes
from typing import Dict, Any

import whisper

# Lazy load Whisper model
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        print(f"Loading Whisper model: {model_name}")
        _whisper_model = whisper.load_model(model_name)
    return _whisper_model

async def extract_file(filepath: str, filename: str) -> Dict[str, Any]:
    """
    Extract content from a file based on its type
    """
    
    # Detect file type
    mime_type, _ = mimetypes.guess_type(filename)
    extension = os.path.splitext(filename)[1].lower()
    
    # Route to appropriate extractor
    if extension in ['.txt', '.md', '.markdown']:
        return await extract_text(filepath, filename)
    
    elif extension == '.pdf':
        return await extract_pdf(filepath, filename)
    
    elif extension in ['.docx', '.doc']:
        return await extract_docx(filepath, filename)
    
    elif extension in ['.mp3', '.wav', '.m4a', '.flac', '.ogg']:
        return await extract_audio(filepath, filename)
    
    elif extension in ['.mp4', '.webm', '.mkv', '.avi', '.mov']:
        return await extract_video(filepath, filename)
    
    elif extension == '.json':
        return await extract_json(filepath, filename)
    
    elif extension in ['.csv', '.tsv']:
        return await extract_csv(filepath, filename)
    
    else:
        # Try as plain text
        try:
            return await extract_text(filepath, filename)
        except:
            raise ValueError(f"Unsupported file type: {extension}")

async def extract_text(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract plain text files"""
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    return {
        'title': filename,
        'content': content,
        'metadata': {
            'file_type': 'text',
            'file_size': os.path.getsize(filepath),
            'word_count': len(content.split())
        }
    }

async def extract_pdf(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract text from PDF"""
    
    try:
        import fitz  # PyMuPDF
        
        doc = fitz.open(filepath)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        content = '\n\n'.join(text_parts)
        
        return {
            'title': filename,
            'content': content,
            'metadata': {
                'file_type': 'pdf',
                'pages': len(doc),
                'file_size': os.path.getsize(filepath)
            }
        }
    except ImportError:
        raise ValueError("PDF extraction requires PyMuPDF. Install with: pip install pymupdf")

async def extract_docx(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract text from DOCX"""
    
    try:
        from docx import Document
        
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        content = '\n\n'.join(paragraphs)
        
        return {
            'title': filename,
            'content': content,
            'metadata': {
                'file_type': 'docx',
                'paragraphs': len(paragraphs),
                'file_size': os.path.getsize(filepath)
            }
        }
    except ImportError:
        raise ValueError("DOCX extraction requires python-docx. Install with: pip install python-docx")

async def extract_audio(filepath: str, filename: str) -> Dict[str, Any]:
    """Transcribe audio file with Whisper"""
    
    loop = asyncio.get_event_loop()
    model = get_whisper_model()
    
    print(f"Transcribing audio: {filename}")
    result = await loop.run_in_executor(
        None,
        lambda: model.transcribe(filepath)
    )
    
    return {
        'title': filename,
        'content': result['text'],
        'metadata': {
            'file_type': 'audio',
            'file_size': os.path.getsize(filepath),
            'language': result.get('language', 'unknown')
        }
    }

async def extract_video(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract audio from video and transcribe"""
    
    import subprocess
    import tempfile
    
    # Extract audio to temp file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp:
        audio_path = tmp.name
    
    try:
        # Use ffmpeg to extract audio
        subprocess.run([
            'ffmpeg', '-i', filepath,
            '-vn', '-acodec', 'libmp3lame', '-q:a', '4',
            '-y', audio_path
        ], check=True, capture_output=True)
        
        # Transcribe the audio
        result = await extract_audio(audio_path, filename)
        result['metadata']['file_type'] = 'video'
        
        return result
    
    finally:
        # Cleanup
        if os.path.exists(audio_path):
            os.remove(audio_path)

async def extract_json(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract JSON file content"""
    
    import json
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Pretty print JSON
    content = json.dumps(data, indent=2, ensure_ascii=False)
    
    return {
        'title': filename,
        'content': content,
        'metadata': {
            'file_type': 'json',
            'file_size': os.path.getsize(filepath)
        }
    }

async def extract_csv(filepath: str, filename: str) -> Dict[str, Any]:
    """Extract CSV file content"""
    
    import csv
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    # Convert to markdown table
    if rows:
        headers = rows[0]
        content_parts = []
        content_parts.append('| ' + ' | '.join(headers) + ' |')
        content_parts.append('| ' + ' | '.join(['---'] * len(headers)) + ' |')
        
        for row in rows[1:100]:  # Limit to 100 rows
            content_parts.append('| ' + ' | '.join(row) + ' |')
        
        if len(rows) > 101:
            content_parts.append(f"\n... and {len(rows) - 101} more rows")
        
        content = '\n'.join(content_parts)
    else:
        content = "(empty file)"
    
    return {
        'title': filename,
        'content': content,
        'metadata': {
            'file_type': 'csv',
            'rows': len(rows),
            'columns': len(rows[0]) if rows else 0,
            'file_size': os.path.getsize(filepath)
        }
    }
