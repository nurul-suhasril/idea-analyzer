"""
GitHub Extractor
Extracts README, description, and structure from GitHub repos
"""

import os
import re
import base64
import asyncio
from typing import Dict, Any

import httpx

async def extract_github(url: str) -> Dict[str, Any]:
    """
    Extract GitHub repository content
    
    - README.md
    - Repository description
    - File structure
    - Key files (package.json, requirements.txt, etc.)
    """
    
    # Parse GitHub URL
    # Formats: 
    #   https://github.com/owner/repo
    #   https://github.com/owner/repo/tree/branch
    #   https://github.com/owner/repo/blob/branch/file
    
    match = re.match(r'https?://github\.com/([^/]+)/([^/]+)', url)
    if not match:
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    owner = match.group(1)
    repo = match.group(2).replace('.git', '')
    
    # GitHub API headers
    headers = {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'IdeaAnalyzer/1.0'
    }
    
    # Add token if available
    token = os.getenv('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'token {token}'
    
    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=headers
    ) as client:
        
        # Get repo info
        repo_response = await client.get(f'https://api.github.com/repos/{owner}/{repo}')
        repo_data = repo_response.json()
        
        if 'message' in repo_data and 'Not Found' in repo_data['message']:
            raise ValueError(f"Repository not found: {owner}/{repo}")
        
        # Get README
        readme_content = ""
        try:
            readme_response = await client.get(
                f'https://api.github.com/repos/{owner}/{repo}/readme'
            )
            readme_data = readme_response.json()
            if 'content' in readme_data:
                readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
        except:
            pass
        
        # Get file tree (root level)
        tree_content = []
        try:
            contents_response = await client.get(
                f'https://api.github.com/repos/{owner}/{repo}/contents'
            )
            contents_data = contents_response.json()
            if isinstance(contents_data, list):
                for item in contents_data:
                    icon = "📁" if item['type'] == 'dir' else "📄"
                    tree_content.append(f"{icon} {item['name']}")
        except:
            pass
        
        # Try to get package info
        package_info = ""
        key_files = ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'pyproject.toml']
        
        for filename in key_files:
            try:
                file_response = await client.get(
                    f'https://api.github.com/repos/{owner}/{repo}/contents/{filename}'
                )
                file_data = file_response.json()
                if 'content' in file_data:
                    package_info = base64.b64decode(file_data['content']).decode('utf-8')
                    package_info = f"### {filename}\n```\n{package_info[:2000]}\n```"
                    break
            except:
                continue
    
    # Build content
    content_parts = []
    
    content_parts.append(f"# {repo_data.get('full_name', f'{owner}/{repo}')}")
    content_parts.append("")
    
    if repo_data.get('description'):
        content_parts.append(f"**Description:** {repo_data['description']}")
        content_parts.append("")
    
    # Stats
    content_parts.append("## Repository Stats")
    content_parts.append(f"- ⭐ Stars: {repo_data.get('stargazers_count', 0)}")
    content_parts.append(f"- 🍴 Forks: {repo_data.get('forks_count', 0)}")
    content_parts.append(f"- 👀 Watchers: {repo_data.get('watchers_count', 0)}")
    content_parts.append(f"- 📝 Language: {repo_data.get('language', 'Unknown')}")
    content_parts.append(f"- 📜 License: {repo_data.get('license', {}).get('name', 'Not specified')}")
    content_parts.append("")
    
    # Topics/Tags
    topics = repo_data.get('topics', [])
    if topics:
        content_parts.append(f"**Topics:** {', '.join(topics)}")
        content_parts.append("")
    
    # File structure
    if tree_content:
        content_parts.append("## File Structure (Root)")
        content_parts.extend(tree_content)
        content_parts.append("")
    
    # Package info
    if package_info:
        content_parts.append("## Dependencies")
        content_parts.append(package_info)
        content_parts.append("")
    
    # README
    if readme_content:
        content_parts.append("## README")
        content_parts.append(readme_content)
    
    content = '\n'.join(content_parts)
    
    metadata = {
        'owner': owner,
        'repo': repo,
        'stars': repo_data.get('stargazers_count', 0),
        'forks': repo_data.get('forks_count', 0),
        'language': repo_data.get('language'),
        'topics': topics,
        'created_at': repo_data.get('created_at'),
        'updated_at': repo_data.get('updated_at'),
        'source_url': url,
    }
    
    return {
        'title': f"GitHub: {owner}/{repo}",
        'content': content,
        'metadata': metadata
    }
