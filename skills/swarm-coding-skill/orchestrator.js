#!/usr/bin/env node
/**
 * Swarm Coding Orchestrator (Enhanced)
 *
 * Fully autonomous multi-agent code generator with specialized roles.
 * Uses qwen-coder exclusively via OpenRouter.
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

const WORKSPACE_ROOT = path.resolve(__dirname, '..'); // workspace root

function loadEnv() {
  const envPath = path.join(WORKSPACE_ROOT, '.env');
  if (!fs.existsSync(envPath)) throw new Error('.env not found in workspace root. Add OPENROUTER_API_KEY.');
  const content = fs.readFileSync(envPath, 'utf8');
  const env = {};
  content.split('\n').forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#')) return;
    const idx = line.indexOf('=');
    if (idx > 0) env[line.substring(0, idx).trim()] = line.substring(idx + 1).trim();
  });
  return env;
}
const env = loadEnv();
const OPENROUTER_KEY = env.OPENROUTER_API_KEY;
if (!OPENROUTER_KEY) throw new Error('OPENROUTER_API_KEY missing in .env');

// Model selection: precedence: process.env.OPENROUTER_MODEL > .env > default
// Default is qwen/qwen3-coder per skill spec. If your key lacks access, add it in OpenRouter dashboard.
const MODEL = process.env.OPENROUTER_MODEL || env.OPENROUTER_MODEL || 'qwen/qwen3-coder';
// Mock mode: set MOCK=1 in shell or .env to use canned responses (no API calls)
const MOCK = process.env.MOCK === '1' || env.MOCK === '1';

function queryOpenRouter(messages, temperature = 0.3) {
  if (MOCK) {
    if (messages[0].role === 'system' && messages[0].content.includes('senior software architect')) {
      return Promise.resolve(`{
  "project_name": "Privy Dashboard",
  "tech_stack": {
    "backend": "Express",
    "frontend": "React",
    "language": "JavaScript",
    "database": "None",
    "css_framework": "Plain CSS",
    "blockchain_network": "ethereum",
    "wallet_provider": "Privy"
  },
  "roles": [
    { "id": "backend-dev", "name": "BackendDev", "outputs": ["server.js","package.json"], "depends_on": [] },
    { "id": "frontend-dev", "name": "FrontendDev", "outputs": ["public/index.html","styles.css","app.js"], "depends_on": ["backend-dev"] },
    { "id": "blockchain-dev", "name": "BlockchainDev", "outputs": ["privy-config.js"], "depends_on": ["backend-dev"] },
    { "id": "qa", "name": "QAEngineer", "outputs": ["test/api.test.js"], "depends_on": ["backend-dev","frontend-dev"] },
    { "id": "devops", "name": "DevOps", "outputs": ["Dockerfile","docker-compose.yml"], "depends_on": ["qa"] }
  ],
  "shared_files": ["README.md"],
  "constraints": []
}`);
    }
    return Promise.resolve(`=== FILE: server.js ===
const express = require('express');
const app = express();
app.use(express.static('public'));
app.get('/api/balance', (req, res) => res.json({ balance: 100 }));
app.listen(3001, () => console.log('Listening on 3001'));
=== END FILE ===

=== FILE: package.json ===
{
  "name": "privy-dashboard",
  "version": "1.0.0",
  "main": "server.js",
  "scripts": { "start": "node server.js" },
  "dependencies": { "express": "^4.18.2" }
}
=== END FILE ===

=== FILE: public/index.html ===
<!DOCTYPE html><html><head><title>Privy Dashboard</title></head><body><h1>Token Balance: <span id="bal">...</span></h1><script>fetch('/api/balance').then(r=>r.json()).then(d=>document.getElementById('bal').textContent=d.balance);</script></body></html>
=== END FILE ===

=== FILE: styles.css ===
body { font-family: sans-serif; padding: 20px; background: #111; color: #eee; }
h1 { color: #ff0055; }
=== END FILE ===

=== FILE: app.js ===
console.log('Frontend loaded');
=== END FILE ===

=== FILE: privy-config.js ===
console.log('Privy integration would go here');
=== END FILE ===

=== FILE: test/api.test.js ===
const request = require('supertest');
const app = require('../server');
describe('GET /api/balance', () => { it('returns 200', async () => { await request(app).get('/api/balance').expect(200); }); });
=== END FILE ===

=== FILE: Dockerfile ===
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "server.js"]
=== END FILE ===

=== FILE: docker-compose.yml ===
version: '3.8'
services:
  app:
    build: .
    ports: ["3001:3001"]
=== END FILE ===`);
  }

  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      model: MODEL,
      messages: messages,
      temperature,
      max_tokens: 4096
    });
    const req = https.request({
      hostname: 'openrouter.ai',
      port: 443,
      path: '/api/v1/chat/completions',
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${OPENROUTER_KEY}`,
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    }, (res) => {
      let chunks = '';
      res.on('data', c => chunks += c);
      res.on('end', () => {
        try {
          const json = JSON.parse(chunks);
          if (json.error) reject(new Error(JSON.stringify(json.error)));
          else resolve(json.choices[0].message.content);
        } catch (e) { reject(e); }
      });
    });
    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

function log(msg) {
  console.log(`[${new Date().toISOString()}] ${msg}`);
}

// Learning capture functions (inspired by self-improving-agent)
function logError(workspace, agentId, error, context = '') {
  const timestamp = new Date().toISOString();
  const entry = `## ${timestamp} — ${agentId}\n\n**Error:** ${error}\n**Context:** ${context || 'N/A'}\n\n---\n\n`;
  fs.appendFileSync(path.join(workspace.learningsDir, 'ERRORS.md'), entry);
}

function logLearning(workspace, agentId, title, content, category = 'correction') {
  const timestamp = new Date().toISOString();
  const entry = `## ${timestamp} — ${agentId} (${category})\n\n**${title}**\n\n${content}\n\n---\n\n`;
  fs.appendFileSync(path.join(workspace.learningsDir, 'LEARNINGS.md'), entry);
}

function logFeatureRequest(workspace, agentId, feature, rationale) {
  const timestamp = new Date().toISOString();
  const entry = `## ${timestamp} — ${agentId}\n\n**Feature:** ${feature}\n**Rationale:** ${rationale}\n\n---\n\n`;
  fs.appendFileSync(path.join(workspace.learningsDir, 'FEATURE_REQUESTS.md'), entry);
}

// Record a decision to DECISIONS.md
function recordDecision(workspace, agentId, decision, rationale) {
  const timestamp = new Date().toISOString();
  const entry = `## ${timestamp} — ${agentId}\n\n**Decision:** ${decision}\n\n**Rationale:** ${rationale}\n\n---\n\n`;
  fs.appendFileSync(workspace.decisionsPath, entry);
}

function createProjectWorkspace(prompt) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
  const projectId = `swarm-${timestamp}`;
  const projectDir = path.join(WORKSPACE_ROOT, 'swarm-projects', projectId);
  fs.mkdirSync(projectDir, { recursive: true });
  const workspace = {
    projectId,
    projectDir,
    prompt,
    manifestPath: path.join(projectDir, 'swarm.yaml'),
    filesDir: path.join(projectDir, 'files'),
    tasksPath: path.join(projectDir, 'tasks.json'),
    decisionsPath: path.join(projectDir, 'DECISIONS.md'),
    learningsDir: path.join(projectDir, '.learnings')
  };
  fs.mkdirSync(workspace.filesDir, { recursive: true });
  fs.mkdirSync(workspace.learningsDir, { recursive: true });
  fs.writeFileSync(workspace.tasksPath, JSON.stringify({ tasks: [], completed: [] }, null, 2));
  
  // Track start time for duration calculation
  workspace.startTime = Date.now();
  
  // Initialize DECISIONS.md with project start
  const decisionsHeader = `# Project Decisions\n\nCreated: ${new Date().toISOString()}\nPrompt: ${prompt}\n\nThis file documents key architectural and technical decisions made during development. It serves as project memory for future reference and continuity.\n\n---\n\n`;
  fs.writeFileSync(workspace.decisionsPath, decisionsHeader);
  
  // Initialize learning logs
  const learningHeader = `# Swarm Learning Log\n\nGenerated: ${new Date().toISOString()}\nProject: ${prompt}\n\n---\n\n`;
  fs.writeFileSync(path.join(workspace.learningsDir, 'ERRORS.md'), learningHeader);
  fs.writeFileSync(path.join(workspace.learningsDir, 'LEARNINGS.md'), learningHeader);
  fs.writeFileSync(path.join(workspace.learningsDir, 'FEATURE_REQUESTS.md'), learningHeader);
  
  log(`Workspace: ${projectDir}`);
  return workspace;
}

// Planner: decides roles and dependencies
async function runPlanner(workspace) {
  log('Running Planner...');
  const systemMsg = `You are a senior software architect designing a swarm-coding manifest.

Given a user prompt, output ONLY valid JSON (no markdown) with this schema:
{
  "project_name": "short name",
  "tech_stack": {
    "backend": "Express" | "FastAPI" | "Go" | "Rust" | "Node" | "Python",
    "frontend": "React" | "Vue" | "Svelte" | "VanillaJS",
    "language": "JavaScript" | "TypeScript" | "Python" | "Go" | "Rust",
    "database": "Postgres" | "MongoDB" | "SQLite" | "None",
    "css_framework": "Tailwind" | "Bootstrap" | "Plain CSS",
    "blockchain_network": "ethereum" | "solana" | "polygon" | "none",
    "wallet_provider": "Privy" | "Wagmi" | "RainbowKit" | "None"
  },
  "roles": [
    { "id": "backend-dev", "name": "BackendDev", "outputs": ["server.js","package.json"], "depends_on": [] }
  ],
  "shared_files": ["README.md"],
  "constraints": [],
  "decisions": [
    { "what": "Tech stack choice", "why": "Based on prompt analysis and team capabilities" }
  ]
}

Decisions:
- Always include BackendDev, FrontendDev, QA, DevOps.
- Include Designer if frontend exists.
- Include BlockchainDev if prompt mentions blockchain, web3, tokens, NFTs, smart contracts, or Privy.
- Include SecurityAuditor if blockchain or finance/payments.
- Include TechnicalWriter for production-ready projects.
- Set depends_on to ensure logical order.
- Outputs should be likely file paths under the project root.
- Include a "decisions" array explaining key architectural choices you're making (tech stack, auth method, etc.). This will be recorded in the project's DECISIONS.md for future reference.
`;

  const userMsg = `Build an app with this description: "${workspace.prompt}"`;

  const response = await queryOpenRouter([
    { role: 'system', content: systemMsg },
    { role: 'user', content: userMsg }
  ], 0.4);

  let jsonStr = response;
  const match = response.match(/```json\n([\s\S]*?)\n```/);
  if (match) jsonStr = match[1];
  const manifest = JSON.parse(jsonStr);
  fs.writeFileSync(workspace.manifestPath, JSON.stringify(manifest, null, 2));
  
  // Record tech stack decisions from planner
  if (manifest.decisions && Array.isArray(manifest.decisions)) {
    manifest.decisions.forEach(dec => {
      recordDecision(workspace, 'Planner', dec.what, dec.why || 'Architectural choice');
    });
  } else {
    // Fallback: record the tech stack as a decision
    const tech = manifest.tech_stack;
    const techSummary = Object.entries(tech).map(([k,v]) => `${k}: ${v}`).join(', ');
    recordDecision(workspace, 'Planner', 'Tech stack selected', techSummary);
  }
  
  // Record overall architectural decision about role assignment
  const roleCount = manifest.roles.length;
  const roleNames = manifest.roles.map(r => r.id).join(', ');
  recordDecision(workspace, 'Planner', `Assigned ${roleCount} roles`, `Team composition: ${roleNames}`);
  
  log(`Manifest: ${manifest.roles.map(r => r.id).join(' -> ')}`);
  return manifest;
}

// Parse file blocks from LLM output
function parseWorkerOutput(output, roleDir) {
  const fileRegex = /=== FILE: (.+?)\s*===\n([\s\S]*?)\n=== END FILE ===/g;
  let match;
  const files = [];
  while ((match = fileRegex.exec(output)) !== null) {
    const filePath = match[1].replace(/^\.?\//, '');
    const content = match[2];
    const fullPath = path.join(roleDir, filePath);
    fs.mkdirSync(path.dirname(fullPath), { recursive: true });
    fs.writeFileSync(fullPath, content);
    files.push(filePath);
  }
  if (files.length === 0) throw new Error('No file blocks found');
  return files;
}

function getRoleConfig(role, manifest) {
  const tech = manifest.tech_stack;
  const base = `You are an autonomous coding agent in a swarm. You will be given a specific task. Write clean, well-commented code. Follow these rules strictly:

1. Output each file as: === FILE: relative/path ===\n<content>\n=== END FILE ===
2. Write full file contents; no partial snippets.
3. Create any needed directories.
4. Include error handling and sensible defaults.
5. Prefer standard libraries; minimize deps.

**Project Memory - DECISIONS MADE Section:**
At the END of your output (after all files), include a section that documents any significant technical decisions you made. This creates a permanent record in DECISIONS.md.

Format exactly as:
DECISIONS MADE:
- [Decision]: Used JWT instead of session cookies
- [Reason]: Stateless auth scales better for APIs

- [Decision]: Chose SQLite for local storage
- [Reason]: Simpler deployment, no external DB needed

Include 2-4 decisions per role. Think about: architecture choices, library selections, security tradeoffs, performance considerations, why you structured files a certain way.
`;

  const specifics = {
    'backend-dev': `Create the backend API.
Tech: ${tech.backend} (${tech.language})
Files to create: ${role.outputs.join(', ')}.

If Privy is the wallet provider (${tech.wallet_provider}), include routes for authentication callbacks and token verification.
Provide a simple health endpoint GET /health.
Use CORS appropriately.
Include a sample .env.example if needed.`,

    'frontend-dev': `Create the frontend UI.
Tech: ${tech.frontend} with ${tech.css_framework}.
Files: ${role.outputs.join(', ')}.

Use fetch to call backend API. If Privy is used, integrate @privy-io/react-auth (for React) or plain JS SDK.
Implement a clean, responsive layout.
Add a health indicator showing backend reachability.`,

    'designer': `Design assets and styles.
Files: ${role.outputs.join(', ')}.

Define a design system: colors, spacing, typography.
Create reusable CSS classes or a Tailwind config if Tailwind is used (${
 tech.css_framework}).
Design components: Button, Card, Header, Footer.
Write HTML mockups or React components as appropriate.
Focus on accessibility and mobile-first.`,

    'blockchain-dev': `Blockchain integration.
Files: ${role.outputs.join(', ')}.

Network: ${tech.blockchain_network}.
Wallet: ${tech.wallet_provider}.

If Privy, add auth flow (login button, session handling). Include a script to verify embedded wallet signatures on backend.
Write a sample smart contract (Solidity) if tokens/NFTs are relevant. Deploy script using Hardhat or ethers.js.
Document environment variables needed (Privy keys, RPC URLs).`,

    'security-auditor': `Review the codebase for security issues.
Files: ${role.outputs.join(', ')}.

Scan for common vulnerabilities (injection, XSS, reentrancy, insecure dependencies).
Add security headers (helmet), rate limiting, input validation if missing.
Check Privy integration for proper secret handling.
Write SECURITY.md with findings and recommendations.
Add a basic audit script (npm run audit).`,

    'qa': `Write automated tests.
Files: ${role.outputs.join(', ')}.

Use Jest or Mocha/Chai. Test at least 2 API endpoints and 1 blockchain interaction if present.
Include setup/teardown and mocking.
Add an integration test that starts the server and runs curl checks.
Provide a test README snippet.`,

    'technical-writer': `Documentation.
Files: ${role.outputs.join(', ')}.

Write comprehensive README.md with setup, run, test, deploy.
Generate API.md with endpoint docs (OpenAPI style if possible).
Add inline code comments where needed.
Include a troubleshooting section.
Keep tone friendly and concise.`,

    'devops': `Deployment and CI/CD.
Files: ${role.outputs.join(', ')}.

Create Dockerfile (multi-stage build), docker-compose.yml with services (app, db if any).
Add GitHub Actions workflow that runs tests on PR, builds and pushes Docker image.
Include environment variable management (dotenv).
Add a deploy script (e.g., to Fly.io, Vercel, or Azure).
Ensure health checks and logs.`
  };

  return { base: base + '\n\n' + (specifics[role.id] || 'Implement your assigned files according to the manifest.'), role };
}

// Spawn a worker
async function spawnWorker(workspace, role, manifest) {
  const roleDir = path.join(workspace.filesDir, role.id);
  fs.mkdirSync(roleDir, { recursive: true });

  const { base } = getRoleConfig(role, manifest);
  const deps = role.depends_on || [];
  const depNote = deps.length ? `\nNote: wait for dependencies: ${deps.join(', ')}.` : '';
  const task = `Project: "${workspace.prompt}"\n\nRole: ${role.name} (${role.id})\n${depNote}\n\nWrite all required files to the shared workspace. Use the FILE block format.`;

  log(`Starting ${role.name}...`);
  try {
    const result = await queryOpenRouter([
      { role: 'system', content: base },
      { role: 'user', content: task }
    ], 0.25);
    const files = parseWorkerOutput(result, roleDir);
    fs.writeFileSync(path.join(roleDir, 'raw.txt'), result);
    log(`${role.name} wrote ${files.length} files.`);
    
    // Extract and record decisions from this agent's output
    extractAndRecordDecisions(workspace, role.id, result);
    
    return { roleId: role.id, status: 'done', files };
  } catch (err) {
    log(`${role.name} failed: ${err.message}`);
    // Log error to learning repository
    logError(workspace, role.id, err.message, `Task: ${role.outputs.join(', ')}`);
    
    // Check if this is a known error pattern and suggest retry with adjusted prompt
    if (err.message.includes('timeout') || err.message.includes('502')) {
      logLearning(workspace, 'Orchestrator', 'Retry strategy for transient failures', 
        `When encountering timeouts or 502 errors from the model API, retry once with a simplified task prompt. This happened with ${role.id}.`, 'best_practice');
      // Could implement retry here with adjusted temperature or simplified instructions
    }
    
    throw err;
  }
}

// Parse decisions from agent output and append to DECISIONS.md
function extractAndRecordDecisions(workspace, agentId, output) {
  // Find the "DECISIONS MADE" section
  const sectionMatch = output.match(/DECISIONS MADE:?[\s\S]*?$/m);
  if (!sectionMatch) return;
  
  const section = sectionMatch[0];
  const lines = section.split('\n');
  let currentDecision = null;
  let currentReason = null;
  
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith('- [Decision]:') || trimmed.startsWith('[Decision]:') || trimmed.startsWith('Decision:')) {
      // Save previous if complete
      if (currentDecision && currentReason) {
        recordDecision(workspace, agentId, currentDecision, currentReason);
      }
      currentDecision = trimmed.replace(/^[-*\[\]]*\s*Decision:?\s*/i, '').trim();
      currentReason = null;
    } else if ((trimmed.startsWith('- [Reason]:') || trimmed.startsWith('[Reason]:') || trimmed.startsWith('Reason:')) && currentDecision) {
      currentReason = trimmed.replace(/^[-*\[\]]*\s*Reason:?\s*/i, '').trim();
      // Save complete pair
      if (currentDecision && currentReason) {
        recordDecision(workspace, agentId, currentDecision, currentReason);
        currentDecision = null;
        currentReason = null;
      }
    }
  }
  // Save any dangling pair (in case order was Reason then Decision, but unlikely)
  if (currentDecision && currentReason) {
    recordDecision(workspace, agentId, currentDecision, currentReason);
  }
}

// Execute manifest respecting dependencies (topological sort)
async function executeManifest(workspace, manifest) {
  const tasksPath = workspace.tasksPath;
  const tasksDB = JSON.parse(fs.readFileSync(tasksPath, 'utf8'));
  const roleMap = new Map(manifest.roles.map(r => [r.id, r]));

  // Build dependency graph
  const inDegree = new Map();
  manifest.roles.forEach(r => inDegree.set(r.id, r.depends_on?.length || 0));
  let queue = manifest.roles.filter(r => inDegree.get(r.id) === 0).map(r => r.id);
  const completed = new Set(tasksDB.completed);
  
  const roleStats = new Map(); // Track success/failure per role

  while (queue.length > 0) {
    const roleId = queue.shift();
    const role = roleMap.get(roleId);
    const deps = role.depends_on || [];
    if (!deps.every(d => completed.has(d))) continue;

    try {
      const res = await spawnWorker(workspace, role, manifest);
      tasksDB.completed.push(roleId);
      tasksDB.tasks.push(res);
      completed.add(roleId);
      roleStats.set(roleId, { status: 'success', files: res.files.length });
      fs.writeFileSync(tasksPath, JSON.stringify(tasksDB, null, 2));
    } catch (err) {
      log(`Task ${roleId} failed; aborting.`);
      roleStats.set(roleId, { status: 'failed', error: err.message });
      // Log learning: this role consistently fails, maybe needs better prompt?
      logLearning(workspace, 'Orchestrator', `Role ${roleId} failed`, 
        `Error: ${err.message}. Consider: (1) Simplify the task for this role, (2) Adjust system prompt, (3) Split into smaller subtasks.`, 'error_pattern');
      throw err;
    }

    // Decrement in-degree of dependents
    manifest.roles.forEach(r => {
      if (r.depends_on.includes(roleId)) {
        inDegree.set(r.id, inDegree.get(r.id) - 1);
        if (inDegree.get(r.id) === 0) queue.push(r.id);
      }
    });
  }

  // Generate summary statistics
  generateRunSummary(workspace, manifest, roleStats, tasksDB.tasks);
  
  log('All tasks completed.');
  return tasksDB.tasks;
}

// Generate end-of-run summary
function generateRunSummary(workspace, manifest, roleStats, tasks) {
  const summaryPath = path.join(workspace.projectDir, 'SWARM_SUMMARY.md');
  const endTime = new Date().toISOString();
  const duration = (new Date() - new Date(workspace.startTime || endTime)) / 1000;
  
  let summary = `# Swarm Execution Summary\n\n`;
  summary += `**Project:** ${manifest.project_name}\n`;
  summary += `**Prompt:** ${workspace.prompt}\n`;
  summary += `**Completed:** ${endTime}\n`;
  summary += `**Duration:** ${Math.round(duration)}s\n`;
  summary += `**Manifest:** ${workspace.manifestPath}\n\n`;
  
  summary += `## Role Performance\n\n`;
  summary += `| Role | Status | Files | Notes |\n`;
  summary += `|------|--------|-------|-------|\n`;
  manifest.roles.forEach(role => {
    const stats = roleStats.get(role.id) || { status: 'not_run' };
    const statusIcon = stats.status === 'success' ? '✓' : stats.status === 'failed' ? '✗' : '○';
    const files = stats.files || '-';
    const notes = stats.error ? `Error: ${stats.error.substring(0, 50)}...` : '-';
    summary += `| ${role.name} (${role.id}) | ${statusIcon} ${stats.status || 'skipped'} | ${files} | ${notes} |\n`;
  });
  
  summary += `\n## Tech Stack\n\n`;
  const tech = manifest.tech_stack;
  Object.entries(tech).forEach(([key, val]) => {
    summary += `- **${key}:** ${val}\n`;
  });
  
  // Count total files generated
  const totalFiles = tasks.reduce((sum, task) => sum + (task.files?.length || 0), 0);
  summary += `\n**Total files generated:** ${totalFiles}\n`;
  
  // Include learning log references
  summary += `\n## Learnings Captured\n\n`;
  summary += `- Errors: \`.learnings/ERRORS.md\` (${countLines(path.join(workspace.learningsDir, 'ERRORS.md'))} entries)\n`;
  summary += `- Insights: \`.learnings/LEARNINGS.md\` (${countLines(path.join(workspace.learningsDir, 'LEARNINGS.md'))} entries)\n`;
  summary += `- Feature requests: \`.learnings/FEATURE_REQUESTS.md\` (${countLines(path.join(workspace.learningsDir, 'FEATURE_REQUESTS.md'))} entries)\n`;
  
  summary += `\n## Next Steps\n\n`;
  summary += `1. Review \`.learnings/\` for patterns and improvements\n`;
  summary += `2. Check \`DECISIONS.md\` for architectural rationale\n`;
  summary += `3. Test the generated project at \`${workspace.projectDir}\`\n`;
  summary += `4. Promote broadly applicable learnings to skill documentation\n`;
  
  fs.writeFileSync(summaryPath, summary);
  log(`Summary written: ${summaryPath}`);
}

// Count non-empty lines in a file
function countLines(filepath) {
  if (!fs.existsSync(filepath)) return 0;
  const content = fs.readFileSync(filepath, 'utf8');
  return content.split('\n').filter(line => line.trim() && !line.startsWith('#')).length;
}
function assembleProject(workspace, manifest) {
  log('Assembling project...');
  const projDir = workspace.projectDir;
  const rootFilesDir = workspace.filesDir;

  manifest.roles.forEach(role => {
    const roleDir = path.join(rootFilesDir, role.id);
    if (!fs.existsSync(roleDir)) return;
    role.outputs.forEach(out => {
      const src = path.join(roleDir, out);
      if (fs.existsSync(src)) {
        const dest = path.join(projDir, out);
        fs.mkdirSync(path.dirname(dest), { recursive: true });
        fs.copyFileSync(src, dest);
        log(`Copied ${out} from ${role.id}`);
      }
    });
  });

  const tech = manifest.tech_stack;
  const readme = `# ${manifest.project_name}\n\n${workspace.prompt}\n\n## Tech Stack\n- Backend: ${tech.backend}\n- Frontend: ${tech.frontend}\n- Language: ${tech.language}\n- Database: ${tech.database}\n- CSS: ${tech.css_framework}\n- Blockchain: ${tech.blockchain_network || 'none'}\n- Wallet: ${tech.wallet_provider || 'none'}\n\n## Run\n\`\`\`bash\nnpm install\nnpm start\n\`\`\`\n\n## Testing\n\`\`\`bash\nnpm test\n\`\`\`\n\n## Deployment\nSee docker-compose.yml.\n\n_Generated by Swarm Coding Skill_\n`;
  fs.writeFileSync(path.join(projDir, 'README.md'), readme);

  log(`Project assembled at ${projDir}`);
}

// Main
(async () => {
  if (process.argv.length < 3) {
    console.error('Usage: orchestrator.js "<prompt>"');
    process.exit(1);
  }
  const prompt = process.argv[2];

  try {
    const workspace = createProjectWorkspace(prompt);
    const manifest = await runPlanner(workspace);
    await executeManifest(workspace, manifest);
    assembleProject(workspace, manifest);
    log(`✅ Done! Project at: ${workspace.projectDir}`);
  } catch (err) {
    log(`❌ Fatal: ${err.message}`);
    console.error(err);
    process.exit(1);
  }
})();
