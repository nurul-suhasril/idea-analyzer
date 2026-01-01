"""
Article Extractor
Extracts clean text from web articles using Trafilatura
"""

import asyncio
from typing import Dict, Any

import httpx
import trafilatura
from trafilatura.settings import use_config

# Configure trafilatura
config = use_config()
config.set("DEFAULT", "EXTRACTION_TIMEOUT", "30")

async def extract_article(url: str) -> Dict[str, Any]:
    """
    Extract article content from URL
    
    Uses Trafilatura for robust article extraction
    """
    
    # Fetch the page
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    ) as client:
        response = await client.get(url)
        html = response.text
    
    # Extract with trafilatura
    loop = asyncio.get_event_loop()
    
    # Get main content
    content = await loop.run_in_executor(
        None,
        lambda: trafilatura.extract(
            html,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=False,
            favor_recall=True,
            config=config
        )
    )
    
    # Get metadata
    metadata_result = await loop.run_in_executor(
        None,
        lambda: trafilatura.extract(
            html,
            output_format='json',
            include_comments=False,
            config=config
        )
    )
    
    # Parse metadata
    import json
    try:
        meta = json.loads(metadata_result) if metadata_result else {}
    except:
        meta = {}
    
    title = meta.get('title', '')
    
    # Try to get title from HTML if not in metadata
    if not title:
        from trafilatura import bare_extraction
        extracted = await loop.run_in_executor(
            None,
            lambda: bare_extraction(html)
        )
        if extracted:
            title = extracted.get('title', url)
    
    if not title:
        title = url
    
    if not content:
        raise ValueError(f"Could not extract content from {url}")
    
    metadata = {
        'author': meta.get('author', ''),
        'date': meta.get('date', ''),
        'sitename': meta.get('sitename', ''),
        'source_url': url,
        'word_count': len(content.split()) if content else 0,
    }
    
    return {
        'title': title,
        'content': content,
        'metadata': metadata
    }
