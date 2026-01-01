"""
YouTube Extractor
Downloads video/audio and transcribes using Whisper
"""

import os
import tempfile
import asyncio
from typing import Dict, Any

import yt_dlp
import whisper

# Load Whisper model (lazy load)
_whisper_model = None

def get_whisper_model():
    global _whisper_model
    if _whisper_model is None:
        model_name = os.getenv("WHISPER_MODEL", "base")
        print(f"Loading Whisper model: {model_name}")
        _whisper_model = whisper.load_model(model_name)
    return _whisper_model

async def extract_youtube(url: str) -> Dict[str, Any]:
    """
    Extract transcript from YouTube video
    
    1. Try to get existing subtitles
    2. If no subtitles, download audio and transcribe with Whisper
    """
    
    # First, try to get video info and subtitles
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        title = info.get('title', 'Unknown Title')
        duration = info.get('duration', 0)
        channel = info.get('channel', 'Unknown Channel')
        description = info.get('description', '')
        
        metadata = {
            'duration': duration,
            'channel': channel,
            'description': description[:500],  # Truncate description
            'view_count': info.get('view_count'),
            'upload_date': info.get('upload_date'),
            'video_id': info.get('id'),
        }
        
        # Check for existing subtitles
        subtitles = info.get('subtitles', {})
        auto_captions = info.get('automatic_captions', {})
        
        # Try to get English subtitles
        if 'en' in subtitles:
            print(f"Found manual English subtitles for: {title}")
            transcript = await download_subtitles(url, 'en', False)
            if transcript:
                return {
                    'title': title,
                    'content': transcript,
                    'metadata': metadata
                }
        
        if 'en' in auto_captions:
            print(f"Found auto-generated English captions for: {title}")
            transcript = await download_subtitles(url, 'en', True)
            if transcript:
                return {
                    'title': title,
                    'content': transcript,
                    'metadata': metadata
                }
    
    # No subtitles available, transcribe with Whisper
    print(f"No subtitles found, transcribing with Whisper: {title}")
    transcript = await transcribe_with_whisper(url)
    
    return {
        'title': title,
        'content': transcript,
        'metadata': metadata
    }

async def download_subtitles(url: str, lang: str = 'en', auto: bool = False) -> str:
    """Download and parse subtitles"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': not auto,
            'writeautomaticsub': auto,
            'subtitleslangs': [lang],
            'subtitlesformat': 'vtt',
            'skip_download': True,
            'outtmpl': os.path.join(tmpdir, '%(id)s.%(ext)s'),
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info['id']
            
            # Look for subtitle file
            for ext in ['vtt', 'srt']:
                sub_file = os.path.join(tmpdir, f"{video_id}.{lang}.{ext}")
                if os.path.exists(sub_file):
                    return parse_subtitle_file(sub_file)
    
    return ""

def parse_subtitle_file(filepath: str) -> str:
    """Parse VTT/SRT subtitle file to plain text"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    text_lines = []
    
    for line in lines:
        line = line.strip()
        # Skip timestamps and headers
        if '-->' in line or line.startswith('WEBVTT') or line.isdigit():
            continue
        # Skip empty lines
        if not line:
            continue
        # Skip position/alignment tags
        if line.startswith('<') or '::' in line:
            continue
        # Remove HTML-like tags
        import re
        line = re.sub(r'<[^>]+>', '', line)
        if line:
            text_lines.append(line)
    
    # Remove duplicate consecutive lines (common in auto-captions)
    deduped = []
    prev = ""
    for line in text_lines:
        if line != prev:
            deduped.append(line)
            prev = line
    
    return ' '.join(deduped)

async def transcribe_with_whisper(url: str) -> str:
    """Download audio and transcribe with Whisper"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        audio_path = os.path.join(tmpdir, 'audio.mp3')
        
        # Download audio only
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'outtmpl': os.path.join(tmpdir, 'audio.%(ext)s'),
        }
        
        print("Downloading audio...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # Find the audio file
        for f in os.listdir(tmpdir):
            if f.startswith('audio.'):
                audio_path = os.path.join(tmpdir, f)
                break
        
        # Transcribe with Whisper
        print("Transcribing with Whisper...")
        model = get_whisper_model()
        
        # Run in thread to not block async
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: model.transcribe(audio_path)
        )
        
        return result['text']
