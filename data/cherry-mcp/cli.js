#!/usr/bin/env node
/**
 * Cherry MCP CLI 🍒
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG_PATH = path.join(__dirname, 'config.json');

function load() {
  try {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  } catch {
    return { port: 3456, host: '127.0.0.1', servers: {}, security: {} };
  }
}

function save(config) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2) + '\n');
  console.log('✓ Saved');
}

const commands = {
  'add-server': (args) => {
    const [name, command, ...cmdArgs] = args;
    if (!name || !command) {
      console.log('Usage: add-server <name> <command> [args...]');
      console.log('Example: add-server github npx @anthropic/mcp-github');
      return;
    }
    const config = load();
    config.servers[name] = { command, args: cmdArgs, env: {} };
    save(config);
    console.log(`✓ Added '${name}'`);
  },

  'remove-server': (args) => {
    const [name] = args;
    if (!name) return console.log('Usage: remove-server <name>');
    const config = load();
    if (!config.servers[name]) return console.log(`✗ '${name}' not found`);
    delete config.servers[name];
    save(config);
    console.log(`✓ Removed '${name}'`);
  },

  'list-servers': () => {
    const config = load();
    const servers = Object.entries(config.servers);
    if (!servers.length) return console.log('No servers configured');
    console.log('\nServers:');
    for (const [name, srv] of servers) {
      console.log(`  ${name}: ${srv.command} ${(srv.args || []).join(' ')}`);
      const envKeys = Object.keys(srv.env || {});
      if (envKeys.length) console.log(`    env: ${envKeys.join(', ')}`);
    }
    console.log('');
  },

  'set-env': (args) => {
    const [server, key, value] = args;
    if (!server || !key || !value) {
      console.log('Usage: set-env <server> <KEY> <value>');
      return;
    }
    const config = load();
    if (!config.servers[server]) return console.log(`✗ Server '${server}' not found`);
    config.servers[server].env = config.servers[server].env || {};
    config.servers[server].env[key] = value;
    save(config);
    console.log(`✓ Set ${key} for '${server}'`);
  },

  'remove-env': (args) => {
    const [server, key] = args;
    if (!server || !key) return console.log('Usage: remove-env <server> <KEY>');
    const config = load();
    if (!config.servers[server]) return console.log(`✗ Server '${server}' not found`);
    delete config.servers[server].env?.[key];
    save(config);
    console.log(`✓ Removed ${key} from '${server}'`);
  },

  'set-rate-limit': (args) => {
    const [rpm] = args;
    if (!rpm) return console.log('Usage: set-rate-limit <requests-per-minute>');
    const config = load();
    config.security = config.security || {};
    config.security.rateLimit = parseInt(rpm, 10);
    save(config);
    console.log(`✓ Rate limit: ${rpm} req/min`);
  },

  'set-allowed-ips': (args) => {
    if (!args.length) return console.log('Usage: set-allowed-ips <ip1> [ip2] ...');
    const config = load();
    config.security = config.security || {};
    config.security.allowedIps = args;
    save(config);
    console.log(`✓ Allowed IPs: ${args.join(', ')}`);
  },

  'enable-audit-log': () => {
    const config = load();
    config.security = config.security || {};
    config.security.auditLog = true;
    save(config);
    console.log('✓ Audit logging enabled');
  },

  'show-config': () => {
    console.log(JSON.stringify(load(), null, 2));
  },

  'restart': () => {
    try {
      execSync('pm2 restart cherry-mcp', { stdio: 'inherit' });
    } catch {
      console.log('Not running. Start with: pm2 start bridge.js --name cherry-mcp');
    }
  },

  'help': () => {
    console.log(`
Cherry MCP CLI 🍒

SERVERS:
  add-server <name> <cmd> [args]   Add MCP server
  remove-server <name>             Remove MCP server
  list-servers                     List servers

ENVIRONMENT:
  set-env <server> <KEY> <value>   Set env var for server
  remove-env <server> <KEY>        Remove env var

SECURITY:
  set-rate-limit <rpm>             Requests per minute limit
  set-allowed-ips <ip> [ip...]     IP allowlist
  enable-audit-log                 Log all requests

OTHER:
  show-config                      Show config
  restart                          Restart via pm2
  help                             This help
`);
  }
};

const [,, cmd, ...args] = process.argv;
(commands[cmd] || commands.help)(args);
