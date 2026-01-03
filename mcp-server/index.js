import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";
import path from "path";
import FormData from "form-data";

// Use environment variable for VPS connection, fallback to localhost for dev
const EXTRACTOR_URL = process.env.EXTRACTOR_URL || 'http://localhost:8000';
const API_KEY = process.env.NEXUS_API_KEY || '';

// Log configuration on startup (useful for debugging)
console.error(`[MCP] Extractor URL: ${EXTRACTOR_URL}`);
console.error(`[MCP] API Key configured: ${API_KEY ? 'Yes' : 'No'}`);

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

// Create MCP server
const server = new Server(
  {
    name: "idea-analyzer",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_extraction",
        description: "Get an extraction by ID. Returns the transcript, title, metadata, and status of a previously extracted video, article, or file.",
        inputSchema: {
          type: "object",
          properties: {
            id: {
              type: "string",
              description: "The extraction ID (e.g., 'fgnb0h2x')",
            },
          },
          required: ["id"],
        },
      },
      {
        name: "list_extractions",
        description: "List recent extractions. Shows all extracted content with their IDs, titles, types, and status.",
        inputSchema: {
          type: "object",
          properties: {
            limit: {
              type: "number",
              description: "Maximum number of extractions to return (default: 20)",
            },
            status: {
              type: "string",
              description: "Filter by status: 'pending', 'processing', 'completed', or 'failed'",
            },
          },
        },
      },
      {
        name: "extract_url",
        description: "Start a new extraction from a URL. Supports YouTube videos, articles, Reddit threads, and GitHub repositories.",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "The URL to extract content from",
            },
          },
          required: ["url"],
        },
      },
      {
        name: "check_service_status",
        description: "Check if the Idea Analyzer extraction service is running.",
        inputSchema: {
          type: "object",
          properties: {},
        },
      },
      {
        name: "upload_file",
        description: "Upload and transcribe a local video or audio file. Supports common formats like MP4, MP3, WAV, M4A, etc.",
        inputSchema: {
          type: "object",
          properties: {
            file_path: {
              type: "string",
              description: "Absolute path to the file (e.g., C:\\Downloads\\video.mp4)",
            },
          },
          required: ["file_path"],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "get_extraction": {
        const response = await authenticatedFetch(`/extraction/${args.id}`);
        if (!response.ok) {
          if (response.status === 404) {
            return {
              content: [
                {
                  type: "text",
                  text: `Extraction '${args.id}' not found. Use list_extractions to see available IDs.`,
                },
              ],
            };
          }
          throw new Error(`HTTP ${response.status}`);
        }
        const data = await response.json();
        
        // Format the response nicely
        const result = {
          id: data.id,
          title: data.title,
          source_type: data.source_type,
          status: data.status,
          url: data.url,
          created_at: data.created_at,
          metadata: data.metadata,
          transcript: data.raw_transcript,
        };
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "list_extractions": {
        const params = new URLSearchParams();
        if (args.limit) params.append("limit", args.limit.toString());
        if (args.status) params.append("status", args.status);

        const response = await authenticatedFetch(`/extractions?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        // Format as a simple list
        const extractions = data.map((e) => ({
          id: e.id,
          title: e.title || "(processing...)",
          type: e.source_type,
          status: e.status,
          created: e.created_at,
        }));
        
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(extractions, null, 2),
            },
          ],
        };
      }

      case "extract_url": {
        const response = await authenticatedFetch(`/extract`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: args.url }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        return {
          content: [
            {
              type: "text",
              text: `Extraction started!\n\nID: ${data.id}\nStatus: ${data.status}\nMessage: ${data.message}\n\nUse get_extraction with ID '${data.id}' to check progress and retrieve the transcript once completed.`,
            },
          ],
        };
      }

      case "check_service_status": {
        try {
          const response = await fetch(`${EXTRACTOR_URL}/health`);
          if (response.ok) {
            const data = await response.json();
            return {
              content: [
                {
                  type: "text",
                  text: `✅ Idea Analyzer service is running and healthy.\nAuth enabled: ${data.auth_enabled || 'unknown'}`,
                },
              ],
            };
          }
          throw new Error("Service unhealthy");
        } catch (e) {
          return {
            content: [
              {
                type: "text",
                text: "❌ Idea Analyzer service is not running. Please start it with: .\\start-extractor.bat",
              },
            ],
          };
        }
      }

      case "upload_file": {
        const filePath = args.file_path;

        // Check if file exists
        if (!fs.existsSync(filePath)) {
          return {
            content: [
              {
                type: "text",
                text: `Error: File not found at path: ${filePath}`,
              },
            ],
          };
        }

        // Get file stats to check size
        const stats = fs.statSync(filePath);
        const fileSizeMB = (stats.size / (1024 * 1024)).toFixed(2);
        const fileName = path.basename(filePath);

        console.error(`[MCP] Uploading file: ${fileName} (${fileSizeMB} MB)`);

        try {
          // Create form data
          const formData = new FormData();
          formData.append("file", fs.createReadStream(filePath));

          // Upload the file
          const response = await fetch(`${EXTRACTOR_URL}/extract/file`, {
            method: "POST",
            headers: {
              ...(API_KEY ? { 'X-API-Key': API_KEY } : {}),
              ...formData.getHeaders(),
            },
            body: formData,
          });

          if (!response.ok) {
            if (response.status === 401) {
              console.error('[MCP] Authentication failed - check NEXUS_API_KEY');
              throw new Error("Authentication failed. Check your API key.");
            }
            if (response.status === 413) {
              throw new Error("File too large. Maximum size is typically 500MB.");
            }
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const data = await response.json();

          return {
            content: [
              {
                type: "text",
                text: `File upload started!\n\nFile: ${fileName}\nSize: ${fileSizeMB} MB\nExtraction ID: ${data.id}\nStatus: ${data.status}\nMessage: ${data.message}\n\nUse get_extraction with ID '${data.id}' to check progress and retrieve the transcript once completed.`,
              },
            ],
          };
        } catch (error) {
          console.error(`[MCP] File upload failed:`, error.message);
          return {
            content: [
              {
                type: "text",
                text: `Error uploading file: ${error.message}`,
              },
            ],
          };
        }
      }

      default:
        return {
          content: [
            {
              type: "text",
              text: `Unknown tool: ${name}`,
            },
          ],
        };
    }
  } catch (error) {
    return {
      content: [
        {
          type: "text",
          text: `Error: ${error.message}. Make sure the Idea Analyzer service is running on ${EXTRACTOR_URL}`,
        },
      ],
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Idea Analyzer MCP server running");
}

main().catch(console.error);
