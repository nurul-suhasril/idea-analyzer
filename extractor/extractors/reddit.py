"""
Reddit Extractor
Extracts posts and comments from Reddit threads
"""

import os
import re
import asyncio
from typing import Dict, Any

import httpx

async def extract_reddit(url: str) -> Dict[str, Any]:
    """
    Extract Reddit post and comments
    
    Uses Reddit's JSON API (no auth required for public posts)
    """
    
    # Convert URL to JSON endpoint
    # Handle various Reddit URL formats
    json_url = url.rstrip('/')
    if not json_url.endswith('.json'):
        json_url = json_url + '.json'
    
    # Replace old.reddit or www.reddit with regular reddit
    json_url = re.sub(r'(old\.|www\.)?reddit\.com', 'reddit.com', json_url)
    
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={
            'User-Agent': 'IdeaAnalyzer/1.0 (Educational Research Bot)'
        }
    ) as client:
        response = await client.get(json_url)
        data = response.json()
    
    # Parse the response
    # Reddit returns a list: [post, comments]
    if isinstance(data, list) and len(data) >= 2:
        post_data = data[0]['data']['children'][0]['data']
        comments_data = data[1]['data']['children']
    else:
        raise ValueError("Unexpected Reddit API response format")
    
    # Extract post info
    title = post_data.get('title', 'Unknown Title')
    author = post_data.get('author', '[deleted]')
    subreddit = post_data.get('subreddit', '')
    selftext = post_data.get('selftext', '')
    score = post_data.get('score', 0)
    num_comments = post_data.get('num_comments', 0)
    created_utc = post_data.get('created_utc', 0)
    
    # Build content
    content_parts = []
    
    # Add post content
    content_parts.append(f"# {title}")
    content_parts.append(f"Posted by u/{author} in r/{subreddit}")
    content_parts.append(f"Score: {score} | Comments: {num_comments}")
    content_parts.append("")
    
    if selftext:
        content_parts.append("## Post Content")
        content_parts.append(selftext)
        content_parts.append("")
    
    # Add comments
    content_parts.append("## Top Comments")
    content_parts.append("")
    
    def extract_comments(comments, depth=0, max_depth=3, max_comments=20):
        """Recursively extract comments"""
        extracted = []
        count = 0
        
        for comment in comments:
            if count >= max_comments:
                break
            if comment.get('kind') != 't1':  # t1 = comment
                continue
            
            comment_data = comment.get('data', {})
            body = comment_data.get('body', '')
            c_author = comment_data.get('author', '[deleted]')
            c_score = comment_data.get('score', 0)
            
            if body and body != '[deleted]' and body != '[removed]':
                indent = "  " * depth
                extracted.append(f"{indent}**u/{c_author}** ({c_score} points):")
                extracted.append(f"{indent}{body}")
                extracted.append("")
                count += 1
                
                # Get replies
                if depth < max_depth:
                    replies = comment_data.get('replies', '')
                    if isinstance(replies, dict):
                        reply_children = replies.get('data', {}).get('children', [])
                        extracted.extend(extract_comments(
                            reply_children, 
                            depth + 1, 
                            max_depth,
                            max_comments - count
                        ))
        
        return extracted
    
    comments_text = extract_comments(comments_data)
    content_parts.extend(comments_text)
    
    content = '\n'.join(content_parts)
    
    metadata = {
        'subreddit': subreddit,
        'author': author,
        'score': score,
        'num_comments': num_comments,
        'created_utc': created_utc,
        'source_url': url,
    }
    
    return {
        'title': f"[r/{subreddit}] {title}",
        'content': content,
        'metadata': metadata
    }
