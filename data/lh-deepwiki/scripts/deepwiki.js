#!/usr/bin/env node
const https = require('https');

/**
 * lh-deepwiki - DeepWiki MCP client (Streamable HTTP edition)
 * Author: 龙虾哥 (liuhedev)
 * Repository: github.com/liuhedev/lh-openclaw-kit
 */

const args = process.argv.slice(2);
const command = args[0];
const repo = args[1];
const extra = args.slice(2).join(' ');

if (!command || !repo) {
  console.log('Usage: node scripts/deepwiki.js <command> <owner/repo> [args]');
  console.log('Commands: ask, structure, contents');
  process.exit(0);
}

const MCP_URL = 'https://mcp.deepwiki.com/mcp';

/**
 * Perform an MCP JSON-RPC call over Streamable HTTP
 * @param {string} method - MCP method name
 * @param {object} params - MCP method parameters
 */
function mcpCall(method, params) {
  return new Promise((resolve, reject) => {
    const payload = { jsonrpc: '2.0', id: Date.now(), method, params };
    const body = JSON.stringify(payload);
    const url = new URL(MCP_URL);
    
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Content-Length': Buffer.byteLength(body),
        'User-Agent': 'lh-deepwiki-client/1.0'
      },
      timeout: 120000 // 120s timeout
    };

    const req = https.request(options, (res) => {
      let responseBody = '';
      
      res.on('data', chunk => {
        responseBody += chunk;
      });

      res.on('end', () => {
        // DeepWiki MCP returns text/event-stream lines for results
        // Even if requested with application/json, it may use data: lines
        const lines = responseBody.split('\n');
        
        // Strategy 1: Look for SSE formatted lines
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const parsed = JSON.parse(line.slice(6));
              if (parsed.result) return resolve(parsed.result);
              if (parsed.error) return reject(new Error(`MCP Error: ${parsed.error.message} (code: ${parsed.error.code})`));
            } catch (e) {
              // Ignore parse errors for partial/malformed SSE lines
            }
          }
        }

        // Strategy 2: Try parsing the whole body as a single JSON response
        try {
          const parsed = JSON.parse(responseBody);
          if (parsed.result) return resolve(parsed.result);
          if (parsed.error) return reject(new Error(`MCP Error: ${parsed.error.message} (code: ${parsed.error.code})`));
        } catch (e) {
          // Fall through to generic error
        }

        // Error handling for empty or unrecognized responses
        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}: ${responseBody.slice(0, 500) || 'Unknown Error'}`));
        } else {
          reject(new Error(`Protocol Error: No valid MCP result found in response. Body sample: ${responseBody.slice(0, 500)}`));
        }
      });
    });

    req.on('error', (err) => {
      reject(new Error(`Request Error: ${err.message}`));
    });

    req.on('timeout', () => {
      req.destroy();
      reject(new Error('Request Timeout: DeepWiki server took too long to respond (>120s).'));
    });

    req.write(body);
    req.end();
  });
}

async function run() {
  try {
    // 1. Initialize MCP connection
    await mcpCall('initialize', {
      protocolVersion: '2024-11-05', // Standard MCP version
      capabilities: {},
      clientInfo: { name: 'lh-deepwiki', version: '1.0.0' }
    });

    let toolName, toolArgs;
    switch (command) {
      case 'ask':
        toolName = 'ask_question';
        toolArgs = { repoName: repo, question: extra };
        break;
      case 'structure':
        toolName = 'read_wiki_structure';
        toolArgs = { repoName: repo };
        break;
      case 'contents':
        toolName = 'read_wiki_contents';
        toolArgs = { repoName: repo, path: extra };
        break;
      default:
        console.error(`Error: Unknown command "${command}". Use ask, structure, or contents.`);
        process.exit(1);
    }

    // 2. Call the tool
    const result = await mcpCall('tools/call', { 
      name: toolName, 
      arguments: toolArgs 
    });

    // 3. Format and output results
    if (result && result.content) {
      for (const item of result.content) {
        if (item.type === 'text') {
          console.log(item.text);
        } else if (item.type === 'resource') {
          console.log(`[Resource: ${item.resource?.uri}]`);
          console.log(item.resource?.text);
        }
      }
    } else {
      console.log('Result (raw):');
      console.log(JSON.stringify(result, null, 2));
    }
  } catch (err) {
    console.error(`Execution Failed: ${err.message}`);
    process.exit(1);
  }
}

run();
