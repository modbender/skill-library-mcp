#!/usr/bin/env node

/**
 * Meegle MCP Proxy Server
 *
 * This script acts as a proxy between OpenClaw and the Meegle MCP server,
 * handling authentication and request forwarding.
 */

const https = require('https');
const http = require('http');

// Configuration from environment variables
const MEEGLE_USER_KEY = process.env.MEEGLE_USER_KEY;
const MEEGLE_MCP_URL = process.env.MEEGLE_MCP_URL || 'https://project.larksuite.com/mcp_server/v1';
const MEEGLE_MCP_KEY = process.env.MEEGLE_MCP_KEY;

if (!MEEGLE_USER_KEY) {
  console.error('Error: MEEGLE_USER_KEY environment variable is required');
  process.exit(1);
}

if (!MEEGLE_MCP_KEY) {
  console.error('Error: MEEGLE_MCP_KEY environment variable is required');
  process.exit(1);
}

// Build the full MCP endpoint URL with authentication
const mcpEndpoint = `${MEEGLE_MCP_URL}?mcpKey=${MEEGLE_MCP_KEY}&userKey=${MEEGLE_USER_KEY}`;

/**
 * Forward MCP request to Meegle server
 */
async function forwardMcpRequest(mcpRequest) {
  return new Promise((resolve, reject) => {
    const url = new URL(mcpEndpoint);
    const options = {
      hostname: url.hostname,
      port: url.port || 443,
      path: url.pathname + url.search,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'OpenClaw-Meegle-Skill/1.0'
      }
    };

    const req = https.request(options, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve(response);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });

    req.on('error', (error) => {
      reject(new Error(`Request failed: ${error.message}`));
    });

    req.write(JSON.stringify(mcpRequest));
    req.end();
  });
}

/**
 * Handle MCP protocol communication via stdio
 */
async function handleStdioProtocol() {
  process.stdin.setEncoding('utf8');

  let buffer = '';

  process.stdin.on('data', async (chunk) => {
    buffer += chunk;

    // Process complete JSON-RPC messages (separated by newlines)
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep incomplete line in buffer

    for (const line of lines) {
      if (!line.trim()) continue;

      try {
        const request = JSON.parse(line);
        const response = await forwardMcpRequest(request);

        // Send response back via stdout
        process.stdout.write(JSON.stringify(response) + '\n');
      } catch (error) {
        // Send error response
        const errorResponse = {
          jsonrpc: '2.0',
          error: {
            code: -32603,
            message: error.message
          },
          id: null
        };
        process.stdout.write(JSON.stringify(errorResponse) + '\n');
      }
    }
  });

  process.stdin.on('end', () => {
    process.exit(0);
  });
}

/**
 * Main entry point
 */
async function main() {
  console.error('Meegle MCP Proxy started');
  console.error(`Connecting to: ${MEEGLE_MCP_URL}`);
  console.error(`User Key: ${MEEGLE_USER_KEY.substring(0, 4)}...`);

  // Start stdio protocol handler
  await handleStdioProtocol();
}

// Handle graceful shutdown
process.on('SIGINT', () => {
  console.error('Shutting down Meegle MCP Proxy...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.error('Shutting down Meegle MCP Proxy...');
  process.exit(0);
});

// Start the proxy
main().catch((error) => {
  console.error('Fatal error:', error.message);
  process.exit(1);
});
