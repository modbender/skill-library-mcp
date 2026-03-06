#!/usr/bin/env node
/**
 * SealVera skill setup — zero-config installer
 *
 * What this does:
 *   1. Prompts for API key (or reads from env/args)
 *   2. Verifies connectivity + org info
 *   3. Copies sealvera-log.js into the workspace
 *   4. Patches AGENTS.md with the mandatory logging convention
 *   5. Writes .sealvera.json config
 *   6. Prints the NODE_OPTIONS line for auto-intercept
 *
 * Usage:
 *   node setup.js                          # interactive
 *   node setup.js --key sv_xxx             # non-interactive
 *   SEALVERA_API_KEY=sv_xxx node setup.js  # via env
 */
'use strict';

const { spawnSync } = require('child_process');
const https  = require('https');
const http   = require('http');
const path   = require('path');
const fs     = require('fs');
const readline = require('readline');

const G  = s => `\x1b[32m${s}\x1b[0m`;
const R  = s => `\x1b[31m${s}\x1b[0m`;
const Y  = s => `\x1b[33m${s}\x1b[0m`;
const D  = s => `\x1b[2m${s}\x1b[0m`;
const B  = s => `\x1b[1m${s}\x1b[0m`;
const CY = s => `\x1b[36m${s}\x1b[0m`;

const SKILL_DIR   = path.resolve(__dirname, '..');
const ENDPOINT    = (process.env.SEALVERA_ENDPOINT || 'https://app.sealvera.com').replace(/\/$/, '');

// ── Detect workspace ──────────────────────────────────────────────────────────
// Priority: --workspace arg > OPENCLAW_WORKSPACE env > cwd
function detectWorkspace() {
  const wsArg = process.argv.find((a, i) => process.argv[i - 1] === '--workspace');
  if (wsArg) return path.resolve(wsArg);
  if (process.env.OPENCLAW_WORKSPACE) return path.resolve(process.env.OPENCLAW_WORKSPACE);
  // Walk up from cwd to find AGENTS.md
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    if (fs.existsSync(path.join(dir, 'AGENTS.md'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

// ── CLI helpers ───────────────────────────────────────────────────────────────
function prompt(question) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(resolve => rl.question(question, ans => { rl.close(); resolve(ans.trim()); }));
}

function request(urlStr, headers = {}, method = 'GET', body = null) {
  return new Promise((resolve, reject) => {
    const url = new URL(urlStr);
    const mod = url.protocol === 'https:' ? https : http;
    const opts = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname + (url.search || ''),
      method,
      headers: { 'Content-Type': 'application/json', ...headers },
    };
    const req = mod.request(opts, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
        catch(_) { resolve({ status: res.statusCode, body: {} }); }
      });
    });
    req.on('error', reject);
    if (body) req.write(JSON.stringify(body));
    req.end();
  });
}

// ── Workspace patchers ────────────────────────────────────────────────────────
const AGENTS_MARKER = '## SealVera — Sub-agent Audit (auto-installed)';

function patchAgentsMd(workspaceDir, logPath) {
  const agentsPath = path.join(workspaceDir, 'AGENTS.md');
  const block = `
${AGENTS_MARKER}

### If you ARE a sub-agent (spawned via sessions_spawn)

**MANDATORY: Log your result to SealVera before finishing.** No exceptions, no matter how trivial the task:

\`\`\`javascript
const log = require('${logPath}');
await log({
  action: '<one-line: what you did>',
  decision: 'COMPLETED',   // COMPLETED/FAILED | PASSED/FAILED | APPROVED/REJECTED
  input:  { task: '<what you were asked>' },
  output: { result: '<what happened>' },
  reasoning: [{ factor: 'outcome', value: '<result>', signal: 'safe', explanation: '<why>' }]
});
\`\`\`

### If you ARE spawning a sub-agent (calling sessions_spawn)

Append this **MANDATORY** footer to every task prompt:

\`\`\`
---
MANDATORY: Before you finish, log your result to SealVera:
  const log = require('${logPath}');
  await log({ action: '<what you did>', decision: 'COMPLETED', input: { task: '<summary>' }, output: { result: '<summary>' }, reasoning: [{ factor: 'outcome', value: '<result>', signal: 'safe', explanation: '<why>' }] });
Vocabulary: task=COMPLETED/FAILED | test=PASSED/FAILED | gate=APPROVED/REJECTED | handoff=ESCALATED
\`\`\`
`;

  if (!fs.existsSync(agentsPath)) {
    fs.writeFileSync(agentsPath, `# AGENTS.md\n${block}`);
    return 'created';
  }

  const content = fs.readFileSync(agentsPath, 'utf8');
  if (content.includes(AGENTS_MARKER)) {
    // Already patched — update it
    const before = content.slice(0, content.indexOf(AGENTS_MARKER));
    fs.writeFileSync(agentsPath, before + block);
    return 'updated';
  }

  fs.appendFileSync(agentsPath, '\n' + block);
  return 'patched';
}

function copyLogHelper(workspaceDir) {
  const src  = path.join(SKILL_DIR, '..', '..', 'sealvera-log.js'); // workspace root
  const dest = path.join(workspaceDir, 'sealvera-log.js');

  // If local workspace copy exists, use it (most up-to-date)
  if (fs.existsSync(src) && path.resolve(src) !== path.resolve(dest)) {
    fs.copyFileSync(src, dest);
    return { path: dest, copied: true };
  }

  // Otherwise generate a minimal standalone version
  if (!fs.existsSync(dest)) {
    const apiKey = process.env.SEALVERA_API_KEY || '';
    const content = generateLogHelper(apiKey, ENDPOINT);
    fs.writeFileSync(dest, content);
    return { path: dest, generated: true };
  }

  return { path: dest, existed: true };
}

function generateLogHelper(apiKey, endpoint) {
  return `#!/usr/bin/env node
/**
 * sealvera-log.js — SealVera logging helper (auto-generated by setup.js)
 * Drop this file in your workspace and require() it from any agent or sub-agent.
 *
 * Decision vocabulary:
 *   Task:  COMPLETED, RESPONDED, FAILED, ERROR, ESCALATED, SKIPPED, PARTIAL
 *   Tests: PASSED, FAILED, SKIPPED, ERROR
 *   Gate:  APPROVED, REJECTED, FLAGGED
 */
'use strict';

const https = require('https');
const http  = require('http');
const { v4: uuidv4 } = require('uuid');

const SV_KEY      = process.env.SEALVERA_API_KEY || '${apiKey}';
const SV_ENDPOINT = (process.env.SEALVERA_ENDPOINT || '${endpoint}').replace(/\\/$/, '');
const SV_AGENT    = process.env.SEALVERA_AGENT || 'openclaw-agent';

const VALID = new Set([
  'COMPLETED','RESPONDED','FAILED','ERROR','ESCALATED','SKIPPED','PARTIAL',
  'PASSED','SUCCESS','BLOCKED',
  'APPROVED','REJECTED','FLAGGED',
]);

async function log({ action, decision = 'COMPLETED', input = {}, output = {}, reasoning = [] }) {
  if (!VALID.has(decision)) {
    console.warn('[sealvera] Unknown decision "' + decision + '". Valid: ' + [...VALID].join(', '));
  }
  const payload = {
    agent: SV_AGENT,
    action,
    decision,
    input:  typeof input  === 'string' ? { value: input  } : input,
    output: typeof output === 'string' ? { value: output } : output,
    reasoning_steps: Array.isArray(reasoning) ? reasoning : [],
    id: uuidv4(),
    timestamp: new Date().toISOString(),
  };
  try {
    const body = JSON.stringify(payload);
    const url  = new URL(SV_ENDPOINT + '/api/ingest');
    const mod  = url.protocol === 'https:' ? https : http;
    return await new Promise((resolve, reject) => {
      const req = mod.request({
        hostname: url.hostname,
        port: url.port || (url.protocol === 'https:' ? 443 : 80),
        path: url.pathname,
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'x-sealvera-key': SV_KEY, 'Content-Length': Buffer.byteLength(body) },
      }, res => {
        let data = '';
        res.on('data', c => data += c);
        res.on('end', () => {
          try { resolve(JSON.parse(data)); } catch(_) { resolve({ ok: true }); }
        });
      });
      req.on('error', reject);
      req.write(body);
      req.end();
    });
  } catch(e) {
    console.error('[sealvera] log error (non-fatal):', e.message);
    return null;
  }
}

module.exports = log;
`;
}

function writeEnvHint(workspaceDir, apiKey, agentName) {
  const envPath = path.join(workspaceDir, '.env');
  const lines = [
    `SEALVERA_API_KEY=${apiKey}`,
    `SEALVERA_AGENT=${agentName}`,
    `SEALVERA_ENDPOINT=${ENDPOINT}`,
  ];
  if (fs.existsSync(envPath)) {
    let content = fs.readFileSync(envPath, 'utf8');
    let changed = false;
    for (const line of lines) {
      const key = line.split('=')[0];
      if (!content.includes(key + '=')) {
        content += '\n' + line;
        changed = true;
      }
    }
    if (changed) { fs.writeFileSync(envPath, content.trimEnd() + '\n'); return 'updated'; }
    return 'exists';
  }
  // Don't create .env if it doesn't exist — just hint
  return 'skip';
}

// ── Main ──────────────────────────────────────────────────────────────────────
async function main() {
  console.log(`\n${B('SealVera')} — Zero-Config Setup\n`);

  const workspace = detectWorkspace();
  console.log(D(`  Workspace: ${workspace}\n`));

  // 1. Get API key
  let apiKey = process.env.SEALVERA_API_KEY || '';
  const keyArg = process.argv.find((a, i) => process.argv[i - 1] === '--key');
  if (keyArg) apiKey = keyArg;

  if (!apiKey) {
    console.log(`Get your API key at: ${CY(ENDPOINT + '/dashboard')}\n`);
    apiKey = await prompt('Paste your API key (sv_...): ');
  }

  if (!apiKey.startsWith('sv_')) {
    console.error(R('✗ Invalid key — should start with sv_'));
    process.exit(1);
  }
  console.log(G('✓') + ` API key: ${D(apiKey.slice(0, 14) + '...')}`);

  // 2. Verify connectivity
  process.stdout.write('  Connecting to SealVera...');
  let org;
  try {
    const { status, body } = await request(`${ENDPOINT}/api/org`, { 'x-sealvera-key': apiKey });
    if (status === 401) {
      console.log('');
      console.error(R('\n✗ API key rejected — check your key at ' + ENDPOINT + '/dashboard'));
      process.exit(1);
    }
    org = body.org || body;
    console.log(` ${G('✓')}`);
    console.log(G('✓') + ` Org: ${B(org.name || org.id || 'default')}  plan: ${CY(org.tier || 'free')}`);
  } catch(e) {
    console.log('');
    console.error(R('✗ Connection failed: ' + e.message));
    process.exit(1);
  }

  // 3. Agent name
  let agentName = process.env.SEALVERA_AGENT || '';
  const nameArg = process.argv.find((a, i) => process.argv[i - 1] === '--agent');
  if (nameArg) agentName = nameArg;
  if (!agentName) {
    const defaultName = path.basename(workspace).replace(/[^a-z0-9-]/gi, '-').toLowerCase() || 'openclaw-agent';
    agentName = await prompt(`Agent name [${defaultName}]: `) || defaultName;
  }
  console.log(G('✓') + ` Agent name: ${B(agentName)}`);

  // 4. Copy sealvera-log.js into workspace
  process.env.SEALVERA_API_KEY = apiKey;
  const { path: logPath, copied, generated } = copyLogHelper(workspace);
  const logLabel = copied ? 'copied' : generated ? 'generated' : 'already present';
  console.log(G('✓') + ` sealvera-log.js ${logLabel} → ${D(logPath)}`);

  // 5. Patch AGENTS.md
  const agentsResult = patchAgentsMd(workspace, logPath);
  console.log(G('✓') + ` AGENTS.md ${agentsResult} — sub-agent audit rule installed`);

  // 6. Update .env if it exists
  const envResult = writeEnvHint(workspace, apiKey, agentName);
  if (envResult === 'updated') console.log(G('✓') + ' .env updated with SealVera keys');
  else if (envResult === 'exists') console.log(D('  .env already has SealVera keys'));
  else console.log(Y('!') + ` Add to your .env or shell:\n   ${D('SEALVERA_API_KEY=' + apiKey)}\n   ${D('SEALVERA_AGENT=' + agentName)}`);

  // 7. Write config
  const config = { endpoint: ENDPOINT, agent: agentName, apiKey, installedAt: new Date().toISOString() };
  fs.writeFileSync(path.join(workspace, '.sealvera.json'), JSON.stringify(config, null, 2));
  console.log(G('✓') + ' .sealvera.json written');

  // 8. Send a test log to confirm end-to-end
  process.stdout.write('  Sending test log...');
  try {
    const testResult = await request(
      `${ENDPOINT}/api/ingest`,
      { 'x-sealvera-key': apiKey, 'Content-Type': 'application/json' },
      'POST',
      {
        agent: agentName,
        action: 'sealvera_setup',
        decision: 'COMPLETED',
        input:  { task: 'Install and configure SealVera skill' },
        output: { result: 'Setup completed successfully', workspace },
        reasoning_steps: [{ factor: 'setup', value: 'ok', signal: 'safe', explanation: 'All steps passed' }],
      }
    );
    if (testResult.body?.ok || testResult.status === 200) {
      console.log(` ${G('✓')}  ${D('id: ' + (testResult.body?.id || 'ok'))}`);
    } else {
      console.log(` ${Y('!')} status ${testResult.status}`);
    }
  } catch(e) {
    console.log(` ${Y('!')} ${e.message}`);
  }

  // Done
  console.log(`
${B('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')}
${G('✓')} ${B('SealVera is ready.')}
${B('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')}

Every sub-agent you spawn will now log to SealVera automatically.

${B('Dashboard:')}   ${CY(ENDPOINT + '/dashboard')}
${B('Workspace:')}   ${D(workspace)}
${B('Agent:')}       ${B(agentName)}

${D('Optional — auto-intercept all LLM calls (no code changes):')}
  ${D('export NODE_OPTIONS="--require ' + path.resolve(SKILL_DIR, 'scripts', 'autoload.js') + '"')}

${D('Check status anytime:')}
  ${D('node ' + path.resolve(SKILL_DIR, 'scripts', 'status.js'))}
`);
}

main().catch(err => {
  console.error(R('\n✗ Setup failed: ' + err.message));
  process.exit(1);
});
