"""
API Authentication for NEXUS Idea Analyzer
Validates X-API-Key header for protected endpoints
"""

import os
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional

# Get API key from environment
API_KEY = os.environ.get("NEXUS_API_KEY")

# Define the header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Security(api_key_header)) -> bool:
    """
    Verify the API key from the X-API-Key header.
    
    Args:
        api_key: The API key from the request header
        
    Returns:
        bool: True if valid or no auth configured
        
    Raises:
        HTTPException: 401 if API key is invalid
    """
    # If no API key is configured, allow all requests (for local dev)
    if not API_KEY:
        return True
    
    # If API key is configured but not provided in request
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Include X-API-Key header."
        )
    
    # Verify the API key matches
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    return True


# Convenience function for checking if auth is enabled
def is_auth_enabled() -> bool:
    """Check if API authentication is enabled (API key is set)."""
    return bool(API_KEY)
