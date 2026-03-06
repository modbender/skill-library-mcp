#!/usr/bin/env node
// Team Builder - OpenClaw Multi-Agent Team Deployer v1.1
// Usage: node deploy.js [--team <prefix>]

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = q => new Promise(r => rl.question(q, r));
const w = (fp, c) => { fs.mkdirSync(path.dirname(fp), { recursive: true }); fs.writeFileSync(fp, c, 'utf8'); };
const home = process.env.HOME || process.env.USERPROFILE;

// --- Multi-team support ---
const args = process.argv.slice(2);
const teamFlagIdx = args.indexOf('--team');
const teamPrefix = (teamFlagIdx !== -1 && args[teamFlagIdx + 1]) ? args[teamFlagIdx + 1] + '-' : '';

// --- Model auto-detection (FIX: read correct config path) ---
function detectModels() {
  try {
    const confPath = path.join(home, '.openclaw', 'openclaw.json');
    const raw = fs.readFileSync(confPath, 'utf8');
    // Strip JS-style comments for JSON5 compat
    const cleaned = raw.replace(/\/\/[^\n]*/g, '').replace(/\/\*[\s\S]*?\*\//g, '');
    const conf = JSON.parse(cleaned);
    // Support both current (models.providers) and legacy (modelProviders) config paths
    const provs = Object.keys((conf.models && conf.models.providers) || conf.modelProviders || {});
    return provs;
  } catch { return []; }
}
function suggestModel(type, provs) {
  const patterns = { think: /glm.?5|opus|o1|deepthink/i, exec: /glm.?4(?!.*flash)|sonnet|gpt-4/i, fast: /flash|haiku|mini/i };
  const p = patterns[type]; if (!p) return null;
  for (const k of provs) { if (p.test(k)) return k; }
  return null;
}

const ROLES = [
  { id: 'chief-of-staff', dname: 'Chief of Staff', pos: 'dispatch+strategy+efficiency', think: true },
  { id: 'data-analyst', dname: 'Data Analyst', pos: 'data+user research', think: false },
  { id: 'growth-lead', dname: 'Growth Lead', pos: 'GEO+SEO+community+social', think: true },
  { id: 'content-chief', dname: 'Content Chief', pos: 'strategy+writing+copy+i18n', think: true },
  { id: 'intel-analyst', dname: 'Intel Analyst', pos: 'competitors+market trends', think: false },
  { id: 'product-lead', dname: 'Product Lead', pos: 'product mgmt+tech architecture', think: true },
  { id: 'fullstack-dev', dname: 'Fullstack Dev', pos: 'fullstack dev+ops+ACP Claude Code', think: false },
];

// --- SOUL generators ---
function chiefSoul(name, team) {
  return `# SOUL.md - ${name} (chief-of-staff)\n\n## Identity\n- Role ID: chief-of-staff\n- Position: Global dispatch + product matrix strategy + internal efficiency\n- Reports to: CEO\n- Bridge between CEO and ${team}\n\n## Core Responsibilities\n\n### Dispatch & Coordination\n1. Daily morning/evening brief writing and distribution\n2. Scan all agent inboxes, detect blockers and anomalies\n3. Cross-team task coordination and priority sorting\n4. Maintain task board (shared/kanban/)\n\n### Matrix Strategy\n5. Product matrix health assessment\n6. Cross-product traffic strategy suggestions\n7. Resource allocation optimization\n8. Pricing strategy analysis\n\n### Internal Efficiency\n9. Workflow optimization: find bottlenecks, reduce repetition\n10. Agent output quality monitoring\n11. Inbox protocol compliance\n12. Knowledge base governance\n13. Automation suggestions\n14. CEO efficiency recommendations\n15. Knowledge base governance: ensure each file has clear ownership, no conflicting edits\n\n## Daily Flow\n### Morning (cron)\n1. Read shared/decisions/active.md\n2. Scan all shared/inbox/to-*.md\n3. Read shared/kanban/blocked.md\n4. Check agent output quality\n5. Write shared/briefings/morning-YYYY-MM-DD.md\n\n### Evening (cron)\n1. Summarize day output\n2. Check task completion\n3. Evaluate team efficiency\n4. Write shared/briefings/evening-YYYY-MM-DD.md\n5. Generate next day plan\n\n### Weekly review (Friday evening appendix)\n- Agent workload distribution\n- Inbox response times\n- Efficiency bottlenecks\n- Knowledge base health\n\n## Permissions\n### Autonomous: coordinate tasks, adjust non-critical priorities, optimize processes\n### Ask CEO: new product launch/shutdown, strategy changes, external publishing, spending\n`;
}

function dataSoul(name) {
  return `# SOUL.md - ${name} (data-analyst)\n\n## Identity\n- Role ID: data-analyst\n- Position: Data hub + user research\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Cross-product core metrics summary (traffic, signups, active users, revenue)\n2. Data anomaly detection (>20% deviation from 7-day avg = alert)\n3. Funnel analysis, conversion tracking\n4. User feedback collection and analysis\n5. User persona maintenance -> shared/knowledge/user-personas.md\n\n## Daily Flow\n1. Read brief and inbox\n2. Pull product core data\n3. Scan user feedback channels\n4. Anomalies -> write to chief-of-staff and product-lead\n5. Write structured data to shared/data/ for other agents to consume\n\n## Standards\n- Note time range and data source\n- YoY and MoM comparisons\n- Never fabricate data\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/user-personas.md — UPDATE with new user insights\n- shared/data/ — Write daily metrics, analysis results here (other agents read-only)\n- When updating: add date + data source at the top\n`;
}

function growthSoul(name) {
  return `# SOUL.md - ${name} (growth-lead)\n\n## Identity\n- Role ID: growth-lead\n- Position: Full-channel growth (GEO + SEO + community + social)\n- Reports to: Chief of Staff -> CEO\n\n## Core Responsibilities\n### GEO - AI Search Optimization (Highest Priority)\n1. Monitor AI search engines (ChatGPT, Perplexity, Gemini, Google AI Overview)\n2. Track product mention rate, ranking, accuracy\n3. Knowledge graph maintenance (Wikipedia, Crunchbase, G2, Capterra)\n4. Update shared/knowledge/geo-playbook.md\n\n### SEO\n5. Keyword research and ranking tracking\n6. Technical SEO audit\n7. Update shared/knowledge/seo-playbook.md\n\n### Community + Social\n8. Reddit/Product Hunt/Indie Hackers/HN engagement\n9. Twitter/X, LinkedIn publishing\n\n## Channel Priority: GEO > SEO > Community > Content > Paid ads (CEO decides)\n## Principle: Provide value first, no spam\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/geo-playbook.md — UPDATE after discovering effective GEO strategies\n- shared/knowledge/seo-playbook.md — UPDATE after SEO experiments\n- When updating: add date + reason + data evidence at the top\n- Other agents READ these files but do not modify them\n`;
}

function contentSoul(name) {
  return `# SOUL.md - ${name} (content-chief)\n\n## Identity\n- Role ID: content-chief\n- Position: One-person content factory (strategy + writing + copy + i18n)\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Content calendar and topic planning\n2. Long-form: tutorials, comparisons, industry analysis (2-3/week)\n3. Short copy: landing pages, CTAs, social posts\n4. Multi-language localization\n\n## Standards\n- Blog: 2000-3000 words, keyword in title, FAQ section\n- Copy: concise, 3-second value delivery, 2-3 A/B versions\n- Translation: native level, culturally adapted\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/content-guidelines.md — UPDATE with proven writing patterns\n- When updating: add date + reason + data evidence at the top\n- Other agents READ this file but do not modify it\n`;
}

function intelSoul(name) {
  return `# SOUL.md - ${name} (intel-analyst)\n\n## Identity\n- Role ID: intel-analyst\n- Position: Competitor intel + market trends\n- Reports to: Chief of Staff\n\n## Core Responsibilities\n1. Competitor product monitoring (features, pricing, funding)\n2. Competitor marketing strategy analysis\n3. Market trends and new player discovery\n4. Competitor AI search presence\n\n## Rhythm: Mon/Wed/Fri scans (cron). Major changes = immediate alert.\n\n## Each Scan\n1. Read shared/knowledge/competitor-map.md\n2. Search competitor news\n3. Update competitor-map.md\n4. Alert chief-of-staff, growth-lead, product-lead on findings\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/competitor-map.md — UPDATE after each scan with new findings\n- When updating: add date + source + what changed at the top\n- Other agents READ this file but do not modify it\n`;
}

function productSoul(name) {
  return `# SOUL.md - ${name} (product-lead)\n\n## Identity\n- Role ID: product-lead\n- Position: Product management + tech architecture\n- Reports to: Chief of Staff -> CEO\n- Direct report: fullstack-dev\n\n## Core Responsibilities\n1. Requirements pool and prioritization\n2. Product roadmap\n3. Tech architecture design and standards\n4. Code quality oversight\n5. Technical debt management\n\n## Principles: User value first | Reuse over reinvent | MVP then iterate\n\n## Knowledge Ownership (you maintain these files)\n- shared/knowledge/tech-standards.md — UPDATE after architecture decisions\n- When updating: add date + reason + decision context at the top\n- Other agents READ this file but do not modify it\n`;
}

function devSoul(name) {
  return `# SOUL.md - ${name} (fullstack-dev)\n\n## Identity\n- Role ID: fullstack-dev\n- Position: Fullstack engineering manager + basic ops\n- Reports to: product-lead\n\n## Core Responsibilities\n1. Receive tasks from product-lead\n2. Simple tasks (<60 lines): do directly\n3. Medium/complex: spawn Claude Code via ACP\n4. Ops: monitoring, deployment, SSL, security scans\n\n## Coding Behavior\n\n> **Skip this entire section if the coding-lead skill is loaded.** coding-lead takes priority.\n\n### Task Classification\n- Simple (<60 lines, single file): do directly\n- Medium (2-5 files): spawn Claude Code\n- Complex (architecture): plan first, then spawn\n\n### Coding Roles (Complex Tasks Only)\n- Architect, Frontend, Backend, Reviewer, QA\n- Spawn role-specific Claude Code sessions for complex multi-layer tasks\n- Skip roles that don\'t apply. Simple/medium: no roles.\n\n### Context: gather project docs, tech-standards.md, memory before spawning\n### Prompt: include path, stack, standards, history, criteria. Append linter/test + auto-notify\n### Spawn: cwd=project dir, never ~/.openclaw/, parallel 2-3 max\n### QA Isolation: QA tests must be spawned in a SEPARATE session from implementation. QA prompt gets requirements + interfaces only, NOT implementation code. This prevents "testing your own homework."
### Review: simple=skip, medium=quick check, complex=full checklist (logic/security/perf/style/tests)\n### Smart Retry: fail -> analyze -> rewrite prompt -> retry, max 3 then report\n### Patterns: record successful prompts in memory, search before spawning\n### Updates: notify on start/completion/error, kill runaway sessions\n\n## Proactive Patrol\n- Scan git logs and error logs when triggered by cron\n- Fix simple issues, report complex ones to chief-of-staff\n\n## Principles\n- Follow shared/knowledge/tech-standards.md strictly\n- Reuse over reinvention\n- When in doubt, ask product-lead\n\n## Task Tracking (if coding-lead skill is NOT loaded)\nTrack active coding tasks in `<project>/.openclaw/active-tasks.json`:\n- Register each spawned CC session with: id, task, branch, status, startedAt\n- Update on completion: status=done, filesChanged, checks (lint/tests)\n- Check before spawning to avoid duplicate work\n\n## Definition of Done (if coding-lead skill is NOT loaded)\nMedium: CC success + lint + tests + no unrelated changes + memory logged\nComplex: all above + review + QA + UI screenshots if applicable\n`;
}

const SOUL_FN = {
  'chief-of-staff': chiefSoul,
  'data-analyst': dataSoul,
  'growth-lead': growthSoul,
  'content-chief': contentSoul,
  'intel-analyst': intelSoul,
  'product-lead': productSoul,
  'fullstack-dev': devSoul,
};

// --- Main ---
async function main() {
  console.log('\n========================================');
  console.log('  OpenClaw Team Builder v1.1');
  console.log('========================================\n');

  const teamName = await ask('Team name [Alpha Team]: ') || 'Alpha Team';

  // --- Flexible role selection (2-10) ---
  console.log('\nAvailable roles:');
  ROLES.forEach((r, i) => console.log('  ' + (i+1) + '. ' + r.dname + ' (' + r.id + ') - ' + r.pos));
  const roleInput = await ask('\nSelect roles (comma-separated numbers, or Enter for all): ');
  let selectedRoles;
  if (!roleInput.trim()) {
    selectedRoles = ROLES;
  } else {
    const indices = roleInput.split(',').map(s => parseInt(s.trim()) - 1).filter(i => i >= 0 && i < ROLES.length);
    selectedRoles = indices.map(i => ROLES[i]);
    if (selectedRoles.length < 2) { console.log('Minimum 2 roles. Using all.'); selectedRoles = ROLES; }
  }
  console.log('Selected ' + selectedRoles.length + ' roles: ' + selectedRoles.map(r => r.dname).join(', '));
  const defDir = path.join(home, '.openclaw', 'workspace-team');
  const workDir = await ask(`Workspace dir [${defDir}]: `) || defDir;
  const tz = await ask('Timezone [Asia/Shanghai]: ') || 'Asia/Shanghai';
  const mh = parseInt(await ask('Morning brief hour [8]: ') || '8');
  const eh = parseInt(await ask('Evening brief hour [18]: ') || '18');
  const provs = detectModels();
  const sugT = suggestModel('think', provs) || 'zai/glm-5';
  const sugE = suggestModel('exec', provs) || 'zai/glm-4.7';
  if (provs.length) console.log('\nDetected providers: ' + provs.join(', '));
  console.log('Suggested: thinking=' + sugT + ', execution=' + sugE);
  const tm = await ask('Thinking model [' + sugT + ']: ') || sugT;
  const em = await ask('Execution model [' + sugE + ']: ') || sugE;
  const ceoTitle = await ask('CEO title [Boss]: ') || 'Boss';

  console.log('\n--- Role names (Enter for default) ---');
  const names = {};
  for (const r of selectedRoles) {
    names[r.id] = await ask(`  ${r.id} [${r.dname}]: `) || r.dname;
  }

  const doTg = (await ask('\nSetup Telegram? (y/n) [n]: ')).toLowerCase() === 'y';
  let tgId, tgProxy, tgTokens;
  if (doTg) {
    tgId = await ask('  Telegram user ID: ');
    tgProxy = await ask('  Proxy (Enter to skip): ') || null;
    console.log('  Bot tokens (Enter to skip):');
    tgTokens = {};
    for (const r of selectedRoles) {
      const t = await ask(`    ${names[r.id]} (${r.id}): `);
      if (t) tgTokens[r.id] = t;
    }
    if (!Object.keys(tgTokens).length) tgTokens = null;
  }

  console.log('\n--- Generating ---\n');

  // FIX: Apply team prefix to agent IDs
  const prefixedRoles = selectedRoles.map(r => ({ ...r, pid: teamPrefix + r.id }));

  // Directories
  const dirs = ['shared/briefings','shared/inbox','shared/decisions','shared/kanban','shared/knowledge','shared/products','shared/data'];
  prefixedRoles.forEach(r => dirs.push(`agents/${r.pid}/memory`));
  dirs.forEach(d => fs.mkdirSync(path.join(workDir, d), { recursive: true }));
  console.log('  [OK] Directories');

  // AGENTS.md
  const rows = prefixedRoles.map(r => `| ${names[r.id]} | ${r.pid} | ${r.pos} |`).join('\n');
  w(path.join(workDir, 'AGENTS.md'), `# AGENTS.md - ${teamName}\n\n## First Instruction\n\nYou are a member of ${teamName}. Your identity.name is set in OpenClaw config.\n\nExecute immediately:\n1. Confirm your role\n2. Read agents/[your-id]/SOUL.md\n3. Read shared/decisions/active.md\n4. Read shared/inbox/to-[your-id].md\n5. Read agents/[your-id]/MEMORY.md\n\n### Role Lookup\n| Name | ID | Position |\n|------|-----|----------|\n${rows}\n\n## Inbox Protocol\n\nWrite: [YYYY-MM-DD HH:MM] from:[id] priority:[high/normal/low] | To: [id] | Subject | Expected output | Deadline\nRead inbox at session start. Processed items -> bottom. Urgent -> also notify ${teamPrefix}chief-of-staff.\n\n## Output: memory->agents/[id]/ | inbox->shared/inbox/ | products->shared/products/ | knowledge->shared/knowledge/ | tasks->shared/kanban/\n\n## Prohibited: no reading other agents' private dirs, no modifying decisions/, no deleting shared/, no external publishing without CEO, no fabricating data\n`);
  console.log('  [OK] AGENTS.md');

  // SOUL.md + USER.md
  w(path.join(workDir, 'SOUL.md'), `# ${teamName} Values\n\nBe genuinely helpful. Have opinions. Be resourceful. Earn trust. Keep private info private. No fabricating data.\n`);
  w(path.join(workDir, 'USER.md'), `# CEO Info\n\n- Title: ${ceoTitle}\n- Timezone: ${tz}\n- Role: SaaS product matrix entrepreneur\n`);
  console.log('  [OK] SOUL.md + USER.md');

  // Agent SOUL + MEMORY
  for (const r of prefixedRoles) {
    const fn = SOUL_FN[r.id];
    const soul = r.id === 'chief-of-staff' ? fn(names[r.id], teamName) : fn(names[r.id]);
    w(path.join(workDir, `agents/${r.pid}/SOUL.md`), soul);
    w(path.join(workDir, `agents/${r.pid}/MEMORY.md`), `# Memory - ${names[r.id]}\n\n(New agent, no memory yet)\n`);
  }
  console.log(`  [OK] ${prefixedRoles.length} Agent SOUL.md + MEMORY.md`);

  // Inboxes
  for (const r of prefixedRoles) {
    w(path.join(workDir, `shared/inbox/to-${r.pid}.md`), `# Inbox - ${names[r.id]}\n\n(No messages)\n\n## Processed\n`);
  }
  console.log(`  [OK] ${prefixedRoles.length} Inboxes`);

  // Shared files
  w(path.join(workDir, 'shared/decisions/active.md'), `# Active Decisions\n\n> All agents read every session.\n\n## Strategy\n- Team: ${teamName}\n- Stage: Cold start\n- Focus: GEO\n\n## Channel Priority\n1. GEO > 2. SEO > 3. Community > 4. Content > 5. Paid (not yet)\n\n## CEO Decision Queue\n(None)\n\n---\n*Fill in: products, goals, resource allocation*\n`);
  w(path.join(workDir, 'shared/products/_index.md'), `# Product Matrix\n\n## Template\n- Name:\n- URL:\n- Code dir:\n- Description:\n- Target users:\n- Features:\n- Tech stack:\n- Status:\n- Keywords (GEO/SEO):\n- Competitors:\n- Differentiator:\n`);
  w(path.join(workDir, 'shared/knowledge/geo-playbook.md'), '# GEO Playbook\n\nAI search optimization strategies.\n');
  w(path.join(workDir, 'shared/knowledge/seo-playbook.md'), '# SEO Playbook\n\nTraditional SEO strategies.\n');
  w(path.join(workDir, 'shared/knowledge/competitor-map.md'), '# Competitor Map\n\n(Fill in competitors)\n');
  w(path.join(workDir, 'shared/knowledge/content-guidelines.md'), '# Content Guidelines\n\nBrand voice, standards.\n');
  w(path.join(workDir, 'shared/knowledge/user-personas.md'), '# User Personas\n\nTarget user profiles.\n');
  w(path.join(workDir, 'shared/knowledge/tech-standards.md'), `# Tech Standards\n\n## Core: KISS + SOLID + DRY. Research before modifying.\n## Red lines: no copy-paste, no breaking existing features, no blind execution.\n## Quality: methods <200 lines, files <500 lines, follow existing style.\n## Security: no hardcoded secrets, DB changes via SQL scripts.\n\n## Tech Stack Preferences (New Projects)\nNew project tech stack must be confirmed with CEO before starting.\n- Backend: PHP (Laravel/ThinkPHP preferred), Python as fallback\n- Frontend: Vue.js or React\n- Mobile: Flutter or UniApp-X\n- CSS: Tailwind CSS\n- DB: MySQL or PostgreSQL\n- Existing projects: keep current stack\n- Always propose first, get approval, then code\n\n---\n*Customize with your tech stack*\n`);
  w(path.join(workDir, 'shared/kanban/backlog.md'), '# Backlog\n\n(Product Lead maintains)\n');
  w(path.join(workDir, 'shared/kanban/in-progress.md'), '# In Progress\n\n(Agents update)\n');
  w(path.join(workDir, 'shared/kanban/blocked.md'), '# Blocked\n\n(Chief of Staff monitors)\n');
  console.log('  [OK] Shared files');

  // apply-config.js
  const wsPath = workDir.replace(/\\/g, '/').replace(home.replace(/\\/g, '/'), '~');
  const agentList = prefixedRoles.map(r => `    { id: "${r.pid}", name: "${names[r.id]}", workspace: "${wsPath}", model: { primary: "${r.think ? tm : em}" }, identity: { name: "${names[r.id]}" } }`).join(',\n');
  const allIds = ['main', ...prefixedRoles.map(r => `"${r.pid}"`)].join(', ');

  let tgBlock = '';
  if (tgTokens && tgId) {
    // FIX: Add groups config with requireMention for proper group @mention handling
    const tgEntries = Object.entries(tgTokens).map(([id, tk]) => {
      const pid = teamPrefix + id;
      return `  config.channels.telegram.accounts["${pid}"] = { botToken: "${tk}", dmPolicy: "allowlist", allowFrom: ["${tgId}"], groupPolicy: "open", groups: { "*": { requireMention: true, groupPolicy: "open" } }, streaming: "partial" };\n  if (!binSet.has("${pid}:${pid}")) config.bindings.push({ agentId: "${pid}", match: { channel: "telegram", accountId: "${pid}" } });`;
    }).join('\n');
    tgBlock = `
  // Telegram
  if (!config.channels) config.channels = {};
  if (!config.channels.telegram) config.channels.telegram = { enabled: true };
  if (!config.channels.telegram.accounts) config.channels.telegram.accounts = {};
  ${tgProxy ? `if (!config.channels.telegram.proxy) config.channels.telegram.proxy = "${tgProxy}";` : ''}
  const binSet = new Set(config.bindings.map(b => b.agentId + ':' + (b.match && b.match.accountId || '')));
${tgEntries}`;
  }

  // FIX: Added defensive checks for missing config structure
  w(path.join(workDir, 'apply-config.js'), `#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const cfgPath = path.join(process.env.HOME || process.env.USERPROFILE, '.openclaw', 'openclaw.json');

let config;
try {
  config = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
} catch (e) {
  console.error('Failed to read config:', e.message);
  process.exit(1);
}

// Backup (with .json extension for clarity)
const bak = cfgPath + '.backup-' + Date.now() + '.json';
fs.writeFileSync(bak, JSON.stringify(config, null, 2));
console.log('Backup: ' + bak);

// Ensure required structure exists
if (!config.agents) config.agents = {};
if (!Array.isArray(config.agents.list)) config.agents.list = [];
if (!config.bindings) config.bindings = [];

// Add agents
const newAgents = [
${agentList}
];
const existing = new Set(config.agents.list.map(a => a.id));
for (const a of newAgents) {
  if (!existing.has(a.id)) { config.agents.list.push(a); console.log('Added: ' + a.id); }
  else console.log('Exists: ' + a.id);
}

// agentToAgent
if (!config.tools) config.tools = {};
config.tools.agentToAgent = { enabled: true, allow: [${allIds}] };
${tgBlock}

fs.writeFileSync(cfgPath, JSON.stringify(config, null, 2));
console.log('\\nDone! Run: openclaw gateway restart');
`);
  console.log('  [OK] apply-config.js');

  // Cron scripts — FIX: apply teamPrefix to cron names and agent IDs
  const crons = [
    { name: `${teamPrefix}chief-morning-brief`, cron: `0 ${mh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Morning workflow: 1. Read decisions. 2. Scan inboxes. 3. Read kanban. 4. Write shared/briefings/morning-today.md. Under 500 words.' },
    { name: `${teamPrefix}chief-evening-brief`, cron: `0 ${eh} * * *`, agent: `${teamPrefix}chief-of-staff`, deliver: '--announce', msg: 'Evening workflow: 1. Scan inboxes. 2. Check task completion. 3. Write shared/briefings/evening-today.md. Under 500 words.' },
    { name: `${teamPrefix}growth-daily-work`, cron: `0 ${mh+1} * * *`, agent: `${teamPrefix}growth-lead`, deliver: '--no-deliver', msg: 'Daily growth (incl GEO): 1. Read brief+inbox. 2. GEO monitoring. 3. SEO check. 4. Community scan. 5. Write to shared/.' },
    { name: `${teamPrefix}data-daily-pull`, cron: `0 ${mh-1} * * *`, agent: `${teamPrefix}data-analyst`, deliver: '--no-deliver', msg: 'Daily data+research: 1. Check product data. 2. Scan user feedback. 3. Alert chief-of-staff on anomalies.' },
    { name: `${teamPrefix}intel-scan`, cron: `5 ${mh-1} * * 1,3,5`, agent: `${teamPrefix}intel-analyst`, deliver: '--no-deliver', msg: 'Competitor scan: 1. Read competitor-map. 2. Search news. 3. Update map. 4. Alert on findings.' },
    { name: `${teamPrefix}content-weekly-plan`, cron: `5 ${mh+1} * * 1`, agent: `${teamPrefix}content-chief`, deliver: '--no-deliver', msg: 'Weekly content plan: 1. Read decisions+inbox. 2. Plan this week content. 3. Start first piece.' },
  ];

  // FIX: PowerShell — call openclaw directly, no cmd /c wrapper; timeout 300s
  let ps = `# ${teamName} Cron Jobs\n\n`;
  for (const c of crons) {
    ps += `openclaw cron add --name "${c.name}" --cron "${c.cron}" --tz "${tz}" --session isolated --agent ${c.agent} ${c.deliver} --exact --timeout-seconds 600 --message "${c.msg}"\n\n`;
  }
  w(path.join(workDir, 'create-crons.ps1'), ps);

  // Bash
  let sh = `#!/bin/bash\n# ${teamName} Cron Jobs\n\n`;
  for (const c of crons) {
    sh += `openclaw cron add --name "${c.name}" --cron "${c.cron}" --tz "${tz}" --session isolated --agent ${c.agent} ${c.deliver} --exact --timeout-seconds 600 --message "${c.msg}"\n\n`;
  }
  w(path.join(workDir, 'create-crons.sh'), sh);
  console.log('  [OK] create-crons.ps1 + .sh');

  // README
  w(path.join(workDir, 'README.md'), `# ${teamName}\n\n## Quick Start\n1. \`node apply-config.js\` -- add agents to openclaw.json\n2. Run \`create-crons.ps1\` (Windows) or \`create-crons.sh\` (Linux/Mac)\n3. \`openclaw gateway restart\`\n4. Fill in shared/decisions/active.md and shared/products/_index.md\n\n## Agents\n${prefixedRoles.map(r => `- **${names[r.id]}** (${r.pid}) -- ${r.pos} -- model: ${r.think ? tm : em}`).join('\n')}\n\n## Cron Schedule\n| Time | Agent | Task |\n|------|-------|------|\n${crons.map(c => `| ${c.cron} | ${c.agent} | ${c.name} |`).join('\n')}\n`);
  console.log('  [OK] README.md');

  console.log(`\n========================================`);
  console.log(`  ${teamName} deployed to ${workDir}`);
  console.log(`  Next: node apply-config.js`);
  console.log(`========================================\n`);

  rl.close();
}

main().catch(e => { console.error(e); rl.close(); process.exit(1); });
