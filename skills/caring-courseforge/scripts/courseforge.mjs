#!/usr/bin/env node
// CourseForge MCP wrapper for OpenClaw
// Usage: node courseforge.mjs <tool_name> [json_args]
//
// Requires:
//   - npm install -g courseforge-mcp-client
//   - COURSEFORGE_API_KEY environment variable set
//
// Examples:
//   node courseforge.mjs list_courses '{}'
//   node courseforge.mjs create_course '{"title":"My Course","description":"Intro","difficulty":"beginner"}'

import { spawn } from 'child_process';
import { resolve } from 'path';
import { existsSync } from 'fs';

const tool = process.argv[2];
const args = process.argv[3] || '{}';

if (!tool) {
  console.error('Usage: courseforge.mjs <tool_name> [json_args]');
  process.exit(1);
}

if (!process.env.COURSEFORGE_API_KEY) {
  console.error('Error: COURSEFORGE_API_KEY environment variable is required.');
  console.error('Get your key at: https://caringcourseforge.com → Settings → API Keys');
  process.exit(1);
}

// Find the courseforge-mcp binary, fall back to npx
const home = process.env.HOME || '';
const candidates = [
  resolve(home, '.npm-global/bin/courseforge-mcp'),
  resolve(home, '.local/bin/courseforge-mcp'),
  '/usr/local/bin/courseforge-mcp',
];

let mcpBin = null;
let mcpArgs = [];
for (const c of candidates) {
  if (existsSync(c)) { mcpBin = c; break; }
}
if (!mcpBin) {
  // Fall back to npx with pinned version
  mcpBin = 'npx';
  mcpArgs = ['-y', 'courseforge-mcp-client@1.3.0'];
}

// Only pass required env vars to the child process — avoid leaking unrelated secrets
const child = spawn(mcpBin, mcpArgs, {
  env: {
    COURSEFORGE_API_KEY: process.env.COURSEFORGE_API_KEY,
    COURSEFORGE_API_URL: process.env.COURSEFORGE_API_URL || '',
    HOME: process.env.HOME || '',
    PATH: process.env.PATH || '',
    NODE_PATH: process.env.NODE_PATH || '',
    npm_config_prefix: process.env.npm_config_prefix || '',
  },
  stdio: ['pipe', 'pipe', 'pipe']
});

let output = '';
child.stdout.on('data', d => { output += d.toString(); });
child.stderr.on('data', () => {});

let parsedArgs;
try {
  parsedArgs = JSON.parse(args);
} catch (e) {
  console.error('Error: Invalid JSON arguments:', args);
  process.exit(1);
}

const init = JSON.stringify({
  jsonrpc: '2.0', id: 1, method: 'initialize',
  params: {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'openclaw-courseforge', version: '1.0.0' }
  }
});

const call = JSON.stringify({
  jsonrpc: '2.0', id: 2, method: 'tools/call',
  params: { name: tool, arguments: parsedArgs }
});

child.stdin.write(init + '\n');
setTimeout(() => {
  child.stdin.write(call + '\n');
  setTimeout(() => { child.stdin.end(); }, 500);
}, 300);

child.on('close', () => {
  const lines = output.trim().split('\n');
  for (const line of lines) {
    try {
      const d = JSON.parse(line);
      if (d.id === 2) {
        // Extract the text content for cleaner output
        if (d.result?.content?.[0]?.text) {
          try {
            const parsed = JSON.parse(d.result.content[0].text);
            console.log(JSON.stringify(parsed, null, 2));
          } catch {
            console.log(d.result.content[0].text);
          }
        } else if (d.error) {
          console.error('MCP Error:', JSON.stringify(d.error, null, 2));
          process.exit(1);
        } else {
          console.log(JSON.stringify(d, null, 2));
        }
        return;
      }
    } catch {}
  }
  console.error('No response received from MCP server');
  process.exit(1);
});

child.on('error', (err) => {
  console.error('Failed to start courseforge-mcp. Is it installed?');
  console.error('Run: npm install -g courseforge-mcp-client');
  process.exit(1);
});
