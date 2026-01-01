# Updates Required for extractor/main.py

## 1. Add Import at the Top

```python
from auth import verify_api_key
from fastapi import Depends
```

## 2. Update Protected Endpoints

Add `dependencies=[Depends(verify_api_key)]` to all API endpoints except health checks.

### Example Changes:

#### Before:
```python
@app.post("/extract")
async def extract_url(request: ExtractRequest):
    # ... existing code
```

#### After:
```python
@app.post("/extract", dependencies=[Depends(verify_api_key)])
async def extract_url(request: ExtractRequest):
    # ... existing code
```

## 3. List of Endpoints to Protect

Apply `dependencies=[Depends(verify_api_key)]` to:

- `POST /extract` - Start URL extraction
- `POST /extract/file` - Upload file extraction
- `GET /extraction/{id}` - Get specific extraction
- `GET /extractions` - List extractions

## 4. Keep Health Endpoints Public

DO NOT add authentication to:

- `GET /` - Root health check
- `GET /health` - Health check endpoint

These should remain public for monitoring tools (Netdata, UptimeRobot).

## 5. Full Example of Updated Endpoint

```python
@app.post("/extract", dependencies=[Depends(verify_api_key)])
async def extract_url(request: ExtractRequest):
    """
    Start content extraction from a URL.
    Requires X-API-Key header for authentication.
    """
    try:
        # Generate unique ID
        extraction_id = generate_id()
        
        # ... rest of existing code ...
        
        return {
            "id": extraction_id,
            "status": "pending",
            "message": "Extraction started"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 6. Optional: Add Auth Status to Health Check

Update the health check to indicate if auth is enabled:

```python
from auth import is_auth_enabled

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "idea-analyzer-extractor",
        "auth_enabled": is_auth_enabled()
    }
```

## Complete List of Changes

1. ✅ Add `from auth import verify_api_key` to imports
2. ✅ Add `from fastapi import Depends` if not already present
3. ✅ Add `dependencies=[Depends(verify_api_key)]` to `/extract`
4. ✅ Add `dependencies=[Depends(verify_api_key)]` to `/extract/file`
5. ✅ Add `dependencies=[Depends(verify_api_key)]` to `/extraction/{id}`
6. ✅ Add `dependencies=[Depends(verify_api_key)]` to `/extractions`
7. ✅ Keep `/` and `/health` endpoints public
8. ✅ (Optional) Update health check to show auth status

## Testing After Implementation

### Test with valid API key:
```bash
curl -H "X-API-Key: your-secret-key" https://api.nexus.yourdomain.com/extractions
```

### Test without API key (should fail):
```bash
curl https://api.nexus.yourdomain.com/extractions
# Expected: 401 Unauthorized
```

### Test health check (should work without auth):
```bash
curl https://api.nexus.yourdomain.com/health
# Expected: 200 OK
```
