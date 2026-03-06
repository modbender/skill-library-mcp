#!/usr/bin/env node

/**
 * Coding Team Setup v2.0 — Interactive Configuration Wizard
 * 
 * Supports:
 * - Flexible team size: 2–10 agents
 * - Custom team name / multiple teams
 * - Customisable collaboration workflow
 * - Role templates + fully custom roles
 * 
 * Usage: node setup.js [--team <name>] [--non-interactive]
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

// ── Colours ──────────────────────────────────────────────
const C = {
  reset: '\x1b[0m', bright: '\x1b[1m', dim: '\x1b[2m',
  green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m',
  magenta: '\x1b[35m', cyan: '\x1b[36m', red: '\x1b[31m',
};
const log   = (m, c = 'reset') => console.log(`${C[c]}${m}${C.reset}`);
const step  = (n, m) => console.log(`${C.cyan}[Step ${n}]${C.reset} ${m}`);
const ok    = m => console.log(`${C.green}✅ ${m}${C.reset}`);
const warn  = m => console.log(`${C.yellow}⚠️  ${m}${C.reset}`);
const fail  = m => console.log(`${C.red}❌ ${m}${C.reset}`);

// ── Prompt helpers ───────────────────────────────────────
function ask(q) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  return new Promise(r => rl.question(q, a => { rl.close(); r(a.trim()); }));
}

async function askDefault(q, def) {
  const a = await ask(`${q} [${def}]: `);
  return a || def;
}

async function confirm(q, def = true) {
  const tag = def ? 'Y/n' : 'y/N';
  const a = await ask(`${q} [${tag}]: `);
  return a === '' ? def : a.toLowerCase().startsWith('y');
}

async function choose(q, choices) {
  console.log(`\n${C.cyan}${q}${C.reset}`);
  choices.forEach((c, i) => console.log(`  ${C.magenta}${i + 1}.${C.reset} ${c}`));
  const a = await ask(`Select [1-${choices.length}]: `);
  const idx = parseInt(a, 10) - 1;
  return (idx >= 0 && idx < choices.length) ? idx : 0;
}

async function multiSelect(q, items, defaults = []) {
  console.log(`\n${C.cyan}${q}${C.reset}`);
  console.log(`  ${C.dim}(space-separated numbers, or "all")${C.reset}`);
  items.forEach((it, i) => {
    const mark = defaults.includes(i) ? `${C.green}✓${C.reset}` : ' ';
    console.log(`  ${mark} ${C.magenta}${i + 1}.${C.reset} ${it}`);
  });
  const a = await ask('Your selection: ');
  if (a.toLowerCase() === 'all') return items.map((_, i) => i);
  const nums = a.split(/[\s,]+/).map(Number).filter(n => n >= 1 && n <= items.length);
  return nums.length > 0 ? nums.map(n => n - 1) : defaults;
}

// ── Load data ────────────────────────────────────────────
const SKILL_DIR   = path.resolve(__dirname, '..');
const CONFIG_DIR  = path.join(SKILL_DIR, 'config');
const TMPL_DIR    = path.join(SKILL_DIR, 'templates');

function loadRolesConfig() {
  return JSON.parse(fs.readFileSync(path.join(CONFIG_DIR, 'roles.json'), 'utf-8'));
}

// ── CLI args ─────────────────────────────────────────────
const args = process.argv.slice(2);
const argTeam = (() => {
  const i = args.indexOf('--team');
  return i !== -1 && args[i + 1] ? args[i + 1] : null;
})();

// ── Generators ───────────────────────────────────────────

function genSOUL(roleId, role) {
  return `# SOUL.md — ${role.name} ${role.emoji}

## Identity
- **Name:** ${role.name}
- **Emoji:** ${role.emoji}
- **Vibe:** ${role.vibe || 'Professional, collaborative'}

## Core Identity

${role.description}

## Responsibilities
${(role.responsibilities || []).map(r => `- ${r}`).join('\n')}

## Collaboration
- Follow the team workflow defined by the coordinator
- Share state through the file system
- Use sessions_spawn / sessions_send for inter-agent communication
`;
}

function genAGENTS(roleId, teamName, workflow) {
  const wfText = workflow.steps
    .map((s, i) => {
      const who = s.roles ? s.roles.join(' + ') : (s.role || '?');
      const par = s.parallel ? ' [parallel]' : '';
      return `${i + 1}. **${who}** — ${s.action}${par}`;
    })
    .join('\n');

  return `# AGENTS.md — ${roleId} (Team: ${teamName})

## Team Workflow

${wfText}

## Task Output

Write deliverables to:
\`\`\`
teamtask/tasks/{task-id}/${roleId}/
\`\`\`

## Model Fallback

When the current model fails (429 / timeout), the framework auto-falls back.

## Timeout Governance (Mandatory)

- Do not run production fan-out checks with bare \`sessions_spawn\`.
- Use timeout-governed dispatch (graded timeout + retry + circuit breaker).
- Baseline: simple 60s/2 retries, normal 120s/3 retries, complex 180s/3 retries.
- Always report: spawn status + fallback trace + final failure type.
`;
}

function genTOOLS() {
  return `# TOOLS.md

## Standard Tools
- read / write / edit — file ops
- exec — shell commands
- browser — web automation
- sessions_spawn — dispatch sub-agents
`;
}

function genUSER() {
  return `# USER.md

## Context
Member of an OpenClaw multi-agent development team.

## Preferences
- Efficiency > verbosity
- Actions > words
`;
}

// ── Main ─────────────────────────────────────────────────

async function main() {
  console.log(`
${C.bright}${C.cyan}╔══════════════════════════════════════════════════════════════╗
║     Coding Team Setup v2.0 — Flexible Multi-Agent Wizard    ║
║          Supports 2–10 agents · Custom teams · Workflows     ║
╚══════════════════════════════════════════════════════════════╝${C.reset}
`);

  const rolesData = loadRolesConfig();
  const templates = rolesData.roleTemplates;
  const workflows = rolesData.workflowTemplates;
  const templateIds = Object.keys(templates);

  // ── Step 1: OpenClaw directory ──
  step(1, 'Locating OpenClaw directory…');
  const openclawPath = process.env.OPENCLAW_DIR || path.join(process.env.HOME, '.openclaw');
  const configPath = path.join(openclawPath, 'openclaw.json');

  if (!fs.existsSync(configPath)) {
    fail(`openclaw.json not found at ${configPath}`);
    process.exit(1);
  }
  ok(`Found: ${openclawPath}`);

  // ── Step 2: Team name ──
  step(2, 'Team configuration');
  const teamName = argTeam || await askDefault('Team name (用于区分多个团队)', 'default');
  const teamPrefix = teamName === 'default' ? '' : `${teamName}-`;
  ok(`Team: ${teamName}`);

  // ── Step 3: Select roles ──
  step(3, `Select roles (2–10 agents)`);

  const roleLabels = templateIds.map(id => {
    const r = templates[id];
    return `${r.emoji} ${r.name} — ${r.description}`;
  });

  const selectedIdxs = await multiSelect(
    'Which roles do you want in this team?',
    roleLabels,
    [0, 1, 2, 3, 4, 5, 6]   // default: first 7
  );

  if (selectedIdxs.length < 2) {
    fail('Minimum 2 agents required.');
    process.exit(1);
  }
  if (selectedIdxs.length > 10) {
    fail('Maximum 10 agents allowed.');
    process.exit(1);
  }

  const selectedRoles = {};
  selectedIdxs.forEach(i => {
    const id = templateIds[i];
    selectedRoles[id] = { ...templates[id] };
  });
  ok(`Selected ${Object.keys(selectedRoles).length} roles`);

  // ── Step 3b: Add custom roles? ──
  const remaining = 10 - Object.keys(selectedRoles).length;
  if (remaining > 0) {
    const addCustom = await confirm(`Add custom roles? (${remaining} slots remaining)`, false);
    if (addCustom) {
      let adding = true;
      while (adding && Object.keys(selectedRoles).length < 10) {
        const cId   = await ask('  Role ID (lowercase, e.g. "ml-engineer"): ');
        if (!cId) { adding = false; break; }
        const cName = await askDefault('  Display name', cId);
        const cEmoji= await askDefault('  Emoji', '🔧');
        const cDesc = await askDefault('  Description', `${cName} — custom role`);
        const cVibe = await askDefault('  Vibe', 'Professional');
        const cResp = await ask('  Responsibilities (comma-separated): ');
        const modelTypeIdx = await choose('  Default model type', [
          'Strongest Reasoning', 'Code Specialized', 'Balanced', 'Fast', 'Long Context'
        ]);
        const modelTypes = ['strongest', 'code', 'balanced', 'fast', 'longContext'];

        selectedRoles[cId] = {
          id: cId,
          name: cName,
          emoji: cEmoji,
          category: 'custom',
          description: cDesc,
          defaultModel: modelTypes[modelTypeIdx],
          vibe: cVibe,
          responsibilities: cResp ? cResp.split(',').map(s => s.trim()) : []
        };
        ok(`Added custom role: ${cEmoji} ${cName}`);

        if (Object.keys(selectedRoles).length < 10) {
          adding = await confirm('Add another custom role?', false);
        }
      }
    }
  }

  // ── Step 4: Model assignment ──
  step(4, 'Model assignment');

  // Detect registered models from openclaw.json
  let config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
  const registeredModels = Object.keys(config.agents?.defaults?.models || {});

  console.log(`\n${C.dim}Registered models (${registeredModels.length}):${C.reset}`);
  if (registeredModels.length > 0) {
    registeredModels.forEach((m, i) => console.log(`  ${C.dim}${i + 1}. ${m}${C.reset}`));
  } else {
    warn('No models registered yet. You can enter model IDs manually.');
  }

  // Default model presets (users can override)
  const MODEL_PRESETS = {
    strongest: registeredModels.find(m => /opus/i.test(m)) || 'custom-llmapi-lovbrowser-com/anthropic/claude-opus-4.6',
    code:      registeredModels.find(m => /codex/i.test(m)) || 'openai-codex/gpt-5.3-codex',
    balanced:  registeredModels.find(m => /sonnet/i.test(m)) || 'custom-llmapi-lovbrowser-com/anthropic/claude-sonnet-4.6',
    fast:      registeredModels.find(m => /haiku/i.test(m))  || 'custom-llmapi-lovbrowser-com/anthropic/claude-haiku-4.5',
    longContext: registeredModels.find(m => /gemini.*pro/i.test(m)) || 'google/gemini-2.5-pro',
  };

  const FALLBACK_MAP = {
    strongest: ['code', 'balanced', 'fast'],
    code:      ['balanced', 'strongest', 'fast'],
    balanced:  ['fast', 'strongest', 'code'],
    fast:      ['balanced', 'code', 'strongest'],
    longContext: ['strongest', 'code', 'balanced'],
  };

  const useDefaults = await confirm('Use auto-detected model presets? (or manually assign each)', true);

  const agentModels = {};  // { roleId: { primary, fallbacks } }

  for (const [roleId, role] of Object.entries(selectedRoles)) {
    const mType = role.defaultModel || 'balanced';
    if (useDefaults) {
      agentModels[roleId] = {
        primary: MODEL_PRESETS[mType],
        fallbacks: FALLBACK_MAP[mType].map(t => MODEL_PRESETS[t])
      };
    } else {
      console.log(`\n  ${role.emoji} ${role.name} (suggested type: ${mType})`);
      const primary = await askDefault(`    Primary model`, MODEL_PRESETS[mType]);
      const fb1 = await askDefault(`    Fallback 1`, MODEL_PRESETS[FALLBACK_MAP[mType][0]]);
      const fb2 = await askDefault(`    Fallback 2`, MODEL_PRESETS[FALLBACK_MAP[mType][1]]);
      const fb3 = await askDefault(`    Fallback 3`, MODEL_PRESETS[FALLBACK_MAP[mType][2]]);
      agentModels[roleId] = { primary, fallbacks: [fb1, fb2, fb3] };
    }
  }
  ok('Model assignment complete');

  // ── Step 5: Collaboration workflow ──
  step(5, 'Collaboration workflow');

  const wfNames = Object.keys(workflows);
  const wfLabels = wfNames.map(k => {
    const w = workflows[k];
    return `${w.name} — ${w.description}`;
  });

  const wfIdx = await choose('Select a workflow template (or "custom" to define your own):', wfLabels);
  let chosenWF = JSON.parse(JSON.stringify(workflows[wfNames[wfIdx]]));  // deep copy
  const selectedRoleIds = Object.keys(selectedRoles);

  if (wfNames[wfIdx] === 'custom') {
    // Custom workflow builder
    console.log(`\n${C.cyan}Define your workflow steps:${C.reset}`);
    console.log(`${C.dim}  Available roles: ${selectedRoleIds.join(', ')}${C.reset}`);
    console.log(`${C.dim}  Enter empty role to stop adding steps.${C.reset}`);

    chosenWF.steps = [];
    let stepNum = 1;
    let adding = true;

    while (adding) {
      console.log(`\n  ${C.bright}Step ${stepNum}:${C.reset}`);
      const rolesStr = await ask(`    Role(s) (comma-separated, or "_user" for user step): `);
      if (!rolesStr) { adding = false; break; }

      const roles = rolesStr.split(',').map(s => s.trim()).filter(Boolean);
      const action = await askDefault(`    Action description`, 'Execute task');
      const output = await askDefault(`    Expected output`, 'output.md');
      const parallel = roles.length > 1 ? await confirm(`    Execute in parallel?`, true) : false;
      const optional = await confirm(`    Optional step?`, false);
      const fbRole = await ask(`    Feedback loop to (role id, or empty): `);

      const stepObj = { step: stepNum };
      if (roles.length === 1) {
        stepObj.role = roles[0];
      } else {
        stepObj.roles = roles;
      }
      stepObj.action = action;
      stepObj.output = output;
      if (parallel) stepObj.parallel = true;
      if (optional) stepObj.optional = true;
      if (fbRole) stepObj.feedback_loop = fbRole;

      chosenWF.steps.push(stepObj);
      stepNum++;
    }

    chosenWF.name = await askDefault('Workflow name', `${teamName}-custom-workflow`);
  } else {
    // Auto-filter steps: remove steps for roles not in this team
    chosenWF.steps = chosenWF.steps.filter(s => {
      const allRoles = s.roles ? s.roles : (s.role ? [s.role] : []);
      // Keep _user steps and steps where at least one role is selected
      return allRoles.some(r => r === '_user' || selectedRoleIds.includes(r));
    });
    // Mark missing optional roles
    chosenWF.steps.forEach(s => {
      if (s.roles) {
        s.roles = s.roles.filter(r => r === '_user' || selectedRoleIds.includes(r));
      }
    });
    // Re-number
    chosenWF.steps.forEach((s, i) => s.step = i + 1);
  }

  ok(`Workflow: ${chosenWF.name} (${chosenWF.steps.length} steps)`);
  chosenWF.steps.forEach(s => {
    const who = s.roles ? s.roles.join(' + ') : (s.role || '?');
    const par = s.parallel ? ' [parallel]' : '';
    console.log(`  ${C.dim}${s.step}. ${who} — ${s.action}${par}${C.reset}`);
  });

  // ── Step 6: Workspace path ──
  step(6, 'Workspace path');
  const defaultWS = path.join(openclawPath, 'workspace');
  const workspace = await askDefault('Shared workspace', defaultWS);

  // ── Step 7: Confirm & backup ──
  step(7, 'Confirm configuration');

  console.log(`
${C.bright}Summary:${C.reset}
  Team:     ${teamName}
  Agents:   ${Object.values(selectedRoles).map(r => `${r.emoji} ${r.name}`).join(', ')}
  Workflow: ${chosenWF.name} (${chosenWF.steps.length} steps)
  Workspace: ${workspace}
`);

  const proceed = await confirm('Proceed with setup?', true);
  if (!proceed) {
    log('Aborted.', 'yellow');
    process.exit(0);
  }

  // Backup
  const backupPath = configPath + `.backup-${Date.now()}`;
  fs.copyFileSync(configPath, backupPath);
  ok(`Backup: ${backupPath}`);

  // ── Step 8: Write openclaw.json ──
  step(8, 'Writing configuration…');

  config = JSON.parse(fs.readFileSync(configPath, 'utf-8'));

  if (!config.agents) config.agents = { defaults: {}, list: [] };
  if (!config.agents.defaults) config.agents.defaults = {};
  if (!config.agents.list) config.agents.list = [];

  // Collect all models to register
  const allModels = new Set();
  for (const m of Object.values(agentModels)) {
    allModels.add(m.primary);
    m.fallbacks.forEach(f => allModels.add(f));
  }
  if (!config.agents.defaults.models) config.agents.defaults.models = {};
  allModels.forEach(m => { config.agents.defaults.models[m] = {}; });

  // Remove old team agents (matching prefix) but keep main + other teams
  const prefixPattern = teamPrefix ? new RegExp(`^${teamPrefix}`) : null;
  config.agents.list = config.agents.list.filter(a => {
    if (a.default === true) return true;
    // If we have a prefix, only remove agents with that prefix
    if (prefixPattern) return !prefixPattern.test(a.id);
    // If default team, remove agents whose id matches any selected role OR old non-prefixed agents
    return false; // remove all non-main for default team
  });

  // Build new agent entries
  const newAgentIds = [];
  for (const [roleId, role] of Object.entries(selectedRoles)) {
    const agentId = `${teamPrefix}${roleId}`;
    const isCodeArtisan = roleId === 'code-artisan';
    const agentWS = isCodeArtisan
      ? path.join(openclawPath, 'agents', agentId, 'workspace')
      : workspace;

    newAgentIds.push(agentId);
    config.agents.list.push({
      id: agentId,
      name: `${role.name}  ${role.emoji}`,
      workspace: agentWS,
      model: {
        primary: agentModels[roleId].primary,
        fallbacks: agentModels[roleId].fallbacks,
      },
      skills: ['teamtask'],
    });
  }

  // Update main agent allowAgents
  const mainIdx = config.agents.list.findIndex(a => a.default === true);
  if (mainIdx === -1) {
    config.agents.list.unshift({
      id: 'main', default: true, name: 'Main Agent',
      workspace,
      subagents: { allowAgents: newAgentIds },
    });
  } else {
    if (!config.agents.list[mainIdx].subagents) {
      config.agents.list[mainIdx].subagents = {};
    }
    // Merge with existing allowAgents (other teams' agents)
    const existing = config.agents.list[mainIdx].subagents.allowAgents || [];
    const merged = [...new Set([...existing.filter(id => {
      // Keep agents from other teams
      if (prefixPattern) return !prefixPattern.test(id);
      return false;
    }), ...newAgentIds])];
    config.agents.list[mainIdx].subagents.allowAgents = merged;
  }

  fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
  ok(`Updated: ${configPath}`);

  // ── Step 9: Create workspaces ──
  step(9, 'Creating agent workspaces…');

  for (const [roleId, role] of Object.entries(selectedRoles)) {
    const agentId = `${teamPrefix}${roleId}`;
    const wsPath = path.join(openclawPath, 'agents', agentId, 'workspace');

    if (!fs.existsSync(wsPath)) {
      fs.mkdirSync(wsPath, { recursive: true });
    }

    // Write workspace files
    fs.writeFileSync(path.join(wsPath, 'SOUL.md'), genSOUL(roleId, role));
    fs.writeFileSync(path.join(wsPath, 'AGENTS.md'), genAGENTS(roleId, teamName, chosenWF));
    fs.writeFileSync(path.join(wsPath, 'TOOLS.md'), genTOOLS());
    fs.writeFileSync(path.join(wsPath, 'USER.md'), genUSER());
    ok(`${role.emoji} ${role.name} → ${wsPath}`);
  }

  // ── Step 10: Save team config for future reference ──
  step(10, 'Saving team manifest…');

  const manifest = {
    team: teamName,
    created: new Date().toISOString(),
    agents: Object.entries(selectedRoles).map(([id, role]) => ({
      id: `${teamPrefix}${id}`,
      roleId: id,
      name: role.name,
      emoji: role.emoji,
      model: agentModels[id],
    })),
    workflow: chosenWF,
    workspace,
  };

  const manifestDir = path.join(openclawPath, 'workspace', 'teamtask', 'teams');
  fs.mkdirSync(manifestDir, { recursive: true });
  const manifestPath = path.join(manifestDir, `${teamName}.json`);
  fs.writeFileSync(manifestPath, JSON.stringify(manifest, null, 2));
  ok(`Team manifest: ${manifestPath}`);

  // Create team task directory
  const taskDir = path.join(openclawPath, 'workspace', 'teamtask', 'tasks');
  fs.mkdirSync(taskDir, { recursive: true });

  // ── Done ──
  console.log(`
${C.bright}${C.green}╔══════════════════════════════════════════════════════════════╗
║                      Setup Complete!                         ║
╚══════════════════════════════════════════════════════════════╝${C.reset}

${C.bright}Team "${teamName}" — ${Object.keys(selectedRoles).length} agents:${C.reset}
${Object.values(selectedRoles).map(r => `  ${r.emoji} ${r.name}`).join('\n')}

${C.bright}Workflow: ${chosenWF.name}${C.reset}
${chosenWF.steps.map(s => {
  const who = s.roles ? s.roles.join(' + ') : (s.role || '?');
  return `  ${s.step}. ${who} — ${s.action}`;
}).join('\n')}

${C.yellow}Next steps:${C.reset}
  1. Restart Gateway:  ${C.cyan}openclaw gateway restart${C.reset}
  2. Verify agents:    ${C.cyan}openclaw agents list${C.reset}
  3. Test spawn:       ${C.cyan}sessions_spawn({ task: "hello", agentId: "${newAgentIds[0]}" })${C.reset}

${C.yellow}Manage teams:${C.reset}
  • Team manifest:     ${manifestPath}
  • Add another team:  ${C.cyan}node setup.js --team <name>${C.reset}

${C.dim}Tip: each team has its own workflow. Run the wizard again with --team to create parallel teams.${C.reset}
`);
}

main().catch(err => {
  fail(`Error: ${err.message}`);
  console.error(err);
  process.exit(1);
});
