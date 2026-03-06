#!/usr/bin/env node
/**
 * Merge Open Wearables MCP server into clawdbot.json5.
 * Usage: node merge-mcp.js <deploy-json-path> [clawdbot-config-path]
 * deploy-json: path to .clawhealth-deploy.json (api_url, api_key, mcp_path, clawdbot_config)
 * clawdbot-config-path: optional; defaults to value in deploy-json or ~/.clawdbot/clawdbot.json5
 */

const fs = require('fs');
const path = require('path');
const JSON5 = require('json5');

const deployPath = process.argv[2];
if (!deployPath) {
  console.error('Usage: node merge-mcp.js <deploy-json-path> [clawdbot-config-path]');
  process.exit(1);
}

const deploy = JSON.parse(fs.readFileSync(deployPath, 'utf8'));
const configPath = process.argv[3] || deploy.clawdbot_config || path.join(process.env.HOME || '', '.clawdbot', 'clawdbot.json5');

let config = {};
if (fs.existsSync(configPath)) {
  const raw = fs.readFileSync(configPath, 'utf8');
  config = JSON5.parse(raw);
} else {
  const dir = path.dirname(configPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

if (!config.mcp) config.mcp = {};
if (!config.mcp.servers) config.mcp.servers = {};

config.mcp.servers['open-wearables'] = {
  command: 'uv',
  args: ['run', '--frozen', '--directory', deploy.mcp_path, 'start'],
  env: {
    OPEN_WEARABLES_API_URL: deploy.api_url,
    OPEN_WEARABLES_API_KEY: deploy.api_key,
  },
};

fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf8');
console.log('Merged open-wearables MCP into', configPath);
