# Updates Required for mcp-server/index.js

## 1. Update Configuration at the Top

### Before:
```javascript
const EXTRACTOR_URL = 'http://localhost:8000';
```

### After:
```javascript
// Use environment variable for VPS connection, fallback to localhost for dev
const EXTRACTOR_URL = process.env.EXTRACTOR_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXUS_API_KEY || '';

// Log configuration on startup (useful for debugging)
console.error(`[MCP] Extractor URL: ${EXTRACTOR_URL}`);
console.error(`[MCP] API Key configured: ${API_KEY ? 'Yes' : 'No'}`);
```

## 2. Add API Key to Request Headers

Find all `fetch()` calls and add the X-API-Key header.

### Example - get_extraction tool:

#### Before:
```javascript
const response = await fetch(`${EXTRACTOR_URL}/extraction/${id}`);
```

#### After:
```javascript
const headers = API_KEY ? { 'X-API-Key': API_KEY } : {};
const response = await fetch(`${EXTRACTOR_URL}/extraction/${id}`, { headers });
```

## 3. Create Helper Function for Authenticated Requests

Add this helper function near the top of your file:

```javascript
/**
 * Make an authenticated request to the extractor service
 * @param {string} path - API path (e.g., '/extractions')
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<Response>} Fetch response
 */
async function authenticatedFetch(path, options = {}) {
  const url = `${EXTRACTOR_URL}${path}`;
  const headers = {
    ...options.headers,
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
  };
  
  return fetch(url, { ...options, headers });
}
```

## 4. Update All Tool Implementations

Replace direct `fetch()` calls with `authenticatedFetch()`:

### get_extraction tool:
```javascript
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "get_extraction",
      description: "Get a specific extraction by ID",
      inputSchema: {
        type: "object",
        properties: {
          id: { type: "string", description: "Extraction ID" }
        },
        required: ["id"]
      }
    },
    // ... other tools
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "get_extraction") {
    const { id } = args;
    
    try {
      const response = await authenticatedFetch(`/extraction/${id}`);
      
      if (!response.ok) {
        return {
          content: [{
            type: "text",
            text: `Error: ${response.status} - ${await response.text()}`
          }]
        };
      }
      
      const data = await response.json();
      return {
        content: [{
          type: "text",
          text: JSON.stringify(data, null, 2)
        }]
      };
    } catch (error) {
      return {
        content: [{
          type: "text",
          text: `Error fetching extraction: ${error.message}`
        }]
      };
    }
  }
  
  // ... other tool handlers
});
```

### list_extractions tool:
```javascript
if (name === "list_extractions") {
  const { limit = 20, status } = args;
  
  try {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    if (status) params.append('status', status);
    
    const response = await authenticatedFetch(`/extractions?${params}`);
    
    if (!response.ok) {
      return {
        content: [{
          type: "text",
          text: `Error: ${response.status} - ${await response.text()}`
        }]
      };
    }
    
    const data = await response.json();
    return {
      content: [{
        type: "text",
        text: JSON.stringify(data, null, 2)
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error listing extractions: ${error.message}`
        }]
      };
    }
  }
```

### extract_url tool:
```javascript
if (name === "extract_url") {
  const { url } = args;
  
  try {
    const response = await authenticatedFetch('/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    if (!response.ok) {
      return {
        content: [{
          type: "text",
          text: `Error: ${response.status} - ${await response.text()}`
        }]
      };
    }
    
    const data = await response.json();
    return {
      content: [{
        type: "text",
        text: `Extraction started: ${data.id}\nStatus: ${data.status}\n${data.message || ''}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error starting extraction: ${error.message}`
      }]
    };
  }
}
```

### check_service_status tool:
```javascript
if (name === "check_service_status") {
  try {
    // Health check doesn't require authentication
    const response = await fetch(`${EXTRACTOR_URL}/health`);
    
    if (!response.ok) {
      return {
        content: [{
          type: "text",
          text: `Service unreachable: HTTP ${response.status}`
        }]
      };
    }
    
    const data = await response.json();
    return {
      content: [{
        type: "text",
        text: `Service Status: ${data.status}\nAuth Enabled: ${data.auth_enabled || 'Unknown'}`
      }]
    };
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Service unreachable: ${error.message}`
      }]
    };
  }
}
```

## 5. Error Handling Improvements

Add better error handling for authentication errors:

```javascript
async function authenticatedFetch(path, options = {}) {
  const url = `${EXTRACTOR_URL}${path}`;
  const headers = {
    ...options.headers,
    ...(API_KEY ? { 'X-API-Key': API_KEY } : {})
  };
  
  try {
    const response = await fetch(url, { ...options, headers });
    
    // Log authentication errors for debugging
    if (response.status === 401) {
      console.error('[MCP] Authentication failed - check NEXUS_API_KEY');
    }
    
    return response;
  } catch (error) {
    console.error(`[MCP] Request failed to ${url}:`, error.message);
    throw error;
  }
}
```

## Summary of Changes

1. ✅ Add `EXTRACTOR_URL` and `API_KEY` from environment variables
2. ✅ Add startup logging for configuration
3. ✅ Create `authenticatedFetch()` helper function
4. ✅ Update `get_extraction` to use authenticated requests
5. ✅ Update `list_extractions` to use authenticated requests
6. ✅ Update `extract_url` to use authenticated requests
7. ✅ Keep `check_service_status` using public health endpoint
8. ✅ Add better error handling and logging

## Testing

After making these changes, test locally first:

### Local Testing (before deployment):
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "idea-analyzer": {
      "command": "node",
      "args": ["C:\\Projects\\idea-analyzer\\mcp-server\\index.js"],
      "env": {
        "EXTRACTOR_URL": "http://localhost:8000",
        "NEXUS_API_KEY": ""
      }
    }
  }
}
```

### VPS Testing (after deployment):
```json
// claude_desktop_config.json
{
  "mcpServers": {
    "idea-analyzer": {
      "command": "node",
      "args": ["C:\\Projects\\idea-analyzer\\mcp-server\\index.js"],
      "env": {
        "EXTRACTOR_URL": "https://api.nexus.yourdomain.com",
        "NEXUS_API_KEY": "your-actual-secret-api-key"
      }
    }
  }
}
```

Remember to restart Claude Desktop after config changes!
