#!/usr/bin/env node
/**
 * Clawl Agent Registration Script
 * 
 * Auto-detects agent config from OpenClaw, generates clawl.json,
 * and pings Clawl for indexing.
 * 
 * Usage:
 *   node register.js                          # Auto-detect from OpenClaw config
 *   node register.js --name "Bot" --description "What I do" --capabilities "coding,security"
 *   node register.js --json                   # Output clawl.json only (no ping)
 */

const fs = require('fs');
const path = require('path');
const http = require('http');
const https = require('https');

// --- Config ---
const CLAWL_API = process.env.CLAWL_API || 'https://moogle-alpha.vercel.app';
const CLAWL_PING = `${CLAWL_API}/api/ping`;
const CLAWL_VALIDATE = `${CLAWL_API}/api/validate`;

// --- Parse CLI args ---
function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--name' && args[i + 1]) opts.name = args[++i];
    else if (args[i] === '--description' && args[i + 1]) opts.description = args[++i];
    else if (args[i] === '--capabilities' && args[i + 1]) opts.capabilities = args[++i].split(',').map(s => s.trim());
    else if (args[i] === '--url' && args[i + 1]) opts.url = args[++i];
    else if (args[i] === '--type' && args[i + 1]) opts.type = args[++i].split(',').map(s => s.trim());
    else if (args[i] === '--email' && args[i + 1]) opts.email = args[++i];
    else if (args[i] === '--website' && args[i + 1]) opts.website = args[++i];
    // --gateway removed: gateway URLs are no longer accepted (security)
    else if (args[i] === '--json') opts.jsonOnly = true;
    else if (args[i] === '--register-only') opts.registerOnly = true;
    else if (args[i] === '--help' || args[i] === '-h') {
      console.log(`
Clawl Agent Registration
========================
Register your AI agent on clawl.co.uk — the search engine for AI agents.

Usage:
  node register.js                     Auto-detect from OpenClaw config
  node register.js --name "Bot"        Specify agent details manually
  node register.js --json              Generate clawl.json without pinging
  node register.js --register-only     Register via API without clawl.json

Options:
  --name <name>              Agent name (required if not auto-detected)
  --description <text>       What the agent does
  --capabilities <list>      Comma-separated capabilities
  --type <list>              Agent types (assistant, developer, security, etc.)
  --url <url>                Agent homepage URL
  --email <email>            Contact email
  --website <url>            Website URL
  --gateway <url>            OpenClaw gateway URL
  --json                     Only generate clawl.json, don't ping
  --register-only            Register via /api/register instead of /api/ping
  --help                     Show this help
`);
      process.exit(0);
    }
  }
  return opts;
}

// --- Auto-detect from OpenClaw config ---
function autoDetect() {
  const detected = {};

  // Try reading OpenClaw config
  const configPaths = [
    path.join(process.env.HOME || process.env.USERPROFILE || '', '.openclaw', 'openclaw.json'),
    path.join(process.cwd(), '.openclaw', 'openclaw.json'),
    path.join(process.cwd(), 'openclaw.json'),
  ];

  for (const configPath of configPaths) {
    try {
      if (fs.existsSync(configPath)) {
        const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
        if (config.agent?.name) detected.name = config.agent.name;
        if (config.agent?.description) detected.description = config.agent.description;
        // Gateway URLs no longer sent (security — removed from protocol)
        console.log(`📋 Found OpenClaw config at ${configPath}`);
        break;
      }
    } catch (e) { /* skip */ }
  }

  // Try reading SOUL.md for identity
  const soulPaths = [
    path.join(process.cwd(), 'SOUL.md'),
    path.join(process.env.HOME || process.env.USERPROFILE || '', 'clawd', 'SOUL.md'),
  ];

  for (const soulPath of soulPaths) {
    try {
      if (fs.existsSync(soulPath)) {
        const soul = fs.readFileSync(soulPath, 'utf8');
        const nameMatch = soul.match(/\*\*Name\*\*:\s*(.+)/);
        const roleMatch = soul.match(/\*\*Role\*\*:\s*(.+)/);
        if (nameMatch && !detected.name) detected.name = nameMatch[1].trim();
        if (roleMatch && !detected.description) detected.description = roleMatch[1].trim();
        console.log(`🧠 Found SOUL.md at ${soulPath}`);
        break;
      }
    } catch (e) { /* skip */ }
  }

  // Try reading IDENTITY.md
  const idPaths = [
    path.join(process.cwd(), 'IDENTITY.md'),
    path.join(process.env.HOME || process.env.USERPROFILE || '', 'clawd', 'IDENTITY.md'),
  ];

  for (const idPath of idPaths) {
    try {
      if (fs.existsSync(idPath)) {
        const id = fs.readFileSync(idPath, 'utf8');
        const nameMatch = id.match(/\*\*Name:\*\*\s*(.+)/);
        const roleMatch = id.match(/\*\*Role:\*\*\s*(.+)/) || id.match(/\*\*Creature:\*\*\s*(.+)/);
        if (nameMatch && !detected.name) detected.name = nameMatch[1].trim();
        if (roleMatch && !detected.description) detected.description = roleMatch[1].trim();
        console.log(`🪪 Found IDENTITY.md at ${idPath}`);
        break;
      }
    } catch (e) { /* skip */ }
  }

  // Try inferring capabilities from installed skills
  const skillsDir = path.join(process.cwd(), 'skills');
  if (fs.existsSync(skillsDir)) {
    try {
      const skills = fs.readdirSync(skillsDir).filter(f => 
        fs.statSync(path.join(skillsDir, f)).isDirectory()
      );
      if (skills.length > 0) {
        detected.capabilities = skills.slice(0, 10); // cap at 10
        console.log(`🔧 Detected ${skills.length} installed skills`);
      }
    } catch (e) { /* skip */ }
  }

  return detected;
}

// --- Generate clawl.json ---
function generateClawlJson(opts) {
  const now = new Date().toISOString();
  
  const clawlJson = {
    "$schema": "https://clawl.co.uk/schema/v0.1.json",
    "version": "0.1",
    "agent": {
      "id": opts.name ? opts.name.toLowerCase().replace(/[^a-z0-9]/g, '-') : `agent-${Date.now()}`,
      "name": opts.name || "Unnamed Agent",
      "description": opts.description || "An AI agent registered on Clawl.",
      "url": opts.url || opts.website || "",
      "type": opts.type || ["assistant"],
      "capabilities": (opts.capabilities || []).map(cap => ({
        "id": cap.toLowerCase().replace(/[^a-z0-9]/g, '-'),
        "name": cap,
        "description": `Capable of ${cap}`,
        "category": "general"
      })),
      "status": "active",
      "created_at": now,
      "updated_at": now
    }
  };

  if (opts.email || opts.website) {
    clawlJson.contact = {};
    if (opts.email) clawlJson.contact.email = opts.email;
    if (opts.website) clawlJson.contact.website = opts.website;
  }

  // Gateway URLs intentionally excluded from clawl.json (security)

  return clawlJson;
}

// --- HTTP POST helper ---
function httpPost(url, data) {
  return new Promise((resolve, reject) => {
    const payload = JSON.stringify(data);
    const mod = url.startsWith('https') ? https : http;
    const parsed = new URL(url);
    
    const req = mod.request({
      hostname: parsed.hostname,
      port: parsed.port,
      path: parsed.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(payload),
        'User-Agent': 'ClawlRegister/1.0'
      },
      timeout: 15000
    }, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, data: JSON.parse(body) });
        } catch (e) {
          resolve({ status: res.statusCode, data: body });
        }
      });
    });
    
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('Request timeout')); });
    req.write(payload);
    req.end();
  });
}

// --- Main ---
async function main() {
  console.log('🦞 Clawl Agent Registration');
  console.log('===========================\n');

  const cliOpts = parseArgs();
  const detected = autoDetect();
  
  // Merge: CLI overrides auto-detected
  const opts = { ...detected, ...cliOpts };

  if (!opts.name) {
    console.error('❌ Could not detect agent name. Use --name "YourAgent"');
    process.exit(1);
  }

  console.log(`\n📝 Agent: ${opts.name}`);
  console.log(`   Description: ${opts.description || '(none)'}`);
  console.log(`   Capabilities: ${opts.capabilities?.join(', ') || '(none)'}`);
  console.log(`   Type: ${opts.type?.join(', ') || 'assistant'}`);

  // Generate clawl.json
  const clawlJson = generateClawlJson(opts);
  const outputPath = path.join(process.cwd(), 'clawl.json');
  fs.writeFileSync(outputPath, JSON.stringify(clawlJson, null, 2));
  console.log(`\n✅ Generated ${outputPath}`);

  if (opts.jsonOnly) {
    console.log('\n📄 clawl.json generated (--json mode, skipping ping)');
    console.log(JSON.stringify(clawlJson, null, 2));
    return;
  }

  // Register via API
  if (opts.registerOnly) {
    console.log('\n📡 Registering via /api/register...');
    try {
      const result = await httpPost(`${CLAWL_API}/api/register`, {
        name: opts.name,
        description: opts.description || '',
        capabilities: opts.capabilities || [],
        short_bio: opts.description || '',
        website_url: opts.website || '',
      });
      
      if (result.status === 200 || result.status === 201) {
        console.log('✅ Registered successfully!');
        console.log(`   View your profile: ${CLAWL_API}/agent/${encodeURIComponent(opts.name)}`);
      } else {
        console.log(`⚠️  Registration response: ${JSON.stringify(result.data)}`);
      }
    } catch (err) {
      console.log(`❌ Registration failed: ${err.message}`);
      console.log('   You can register manually at: ${CLAWL_API}/register');
    }
    return;
  }

  // Ping Clawl (for agents with hosted clawl.json)
  if (opts.url || opts.gateway) {
    const pingUrl = opts.url || opts.gateway;
    console.log(`\n📡 Pinging Clawl with URL: ${pingUrl}`);
    try {
      const result = await httpPost(CLAWL_PING, { url: pingUrl });
      if (result.status === 200) {
        console.log('✅ Pinged successfully! Clawl will index your agent.');
        console.log(`   ${JSON.stringify(result.data)}`);
      } else {
        console.log(`⚠️  Ping response (${result.status}): ${JSON.stringify(result.data)}`);
        console.log('   Falling back to direct registration...');
        await registerDirect(opts);
      }
    } catch (err) {
      console.log(`⚠️  Ping failed: ${err.message}`);
      console.log('   Falling back to direct registration...');
      await registerDirect(opts);
    }
  } else {
    // No URL — register directly
    await registerDirect(opts);
  }

  console.log(`\n🦞 Done! Search for yourself at: ${CLAWL_API}`);
  console.log('👑 Climb the ranks. Aim for King of the Castle.');
}

async function registerDirect(opts) {
  console.log('\n📡 Registering directly via /api/register...');
  try {
    const result = await httpPost(`${CLAWL_API}/api/register`, {
      name: opts.name,
      description: opts.description || '',
      capabilities: opts.capabilities || [],
      short_bio: opts.description || '',
      website_url: opts.website || '',
    });
    
    if (result.status === 200 || result.status === 201) {
      console.log('✅ Registered on Clawl!');
      console.log(`   Profile: ${CLAWL_API}/agent/${encodeURIComponent(opts.name)}`);
    } else {
      console.log(`⚠️  Response: ${JSON.stringify(result.data)}`);
    }
  } catch (err) {
    console.log(`❌ Registration failed: ${err.message}`);
    console.log(`   Register manually at: ${CLAWL_API}/register`);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
