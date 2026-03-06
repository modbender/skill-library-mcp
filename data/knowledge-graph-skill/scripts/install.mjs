#!/usr/bin/env node
// install.mjs — Auto-setup KG skill for autonomous agent use
// Run once after installing the skill. Idempotent (safe to re-run).
//
// Supports: OpenClaw (AGENTS.md), Claude Code (CLAUDE.md), Gemini CLI (GEMINI.md)
// Auto-detects platform or use --platform flag to force.
//
// What it does:
// 1. Creates data/ dir + empty kg-store.json if not exists (inside skill dir, co-located with scripts)
// 2. Generates kg-summary.md
// 3. Patches agent instructions file with KG instructions + graph summary
// 4. Ensures .gitignore for vault files
//
// Usage: node scripts/install.mjs [--workspace /path/to/workspace] [--platform openclaw|claude|gemini]

import { readFileSync, writeFileSync, existsSync, mkdirSync, realpathSync } from 'fs';
import { join, dirname, resolve, relative } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
// SKILL_DIR = the knowledge-graph skill folder (where this script lives / source)
const SKILL_DIR = realpathSync(resolve(join(__dirname, '..')));
// DATA_DIR is resolved later after we know the target workspace
// (may point to target workspace's skill copy, not source)

const args = process.argv.slice(2);
function flag(name) {
  const i = args.indexOf('--' + name);
  return i !== -1 ? args[i + 1] : null;
}

// ── Platform detection ──
const PLATFORM_FILES = {
  openclaw: ['AGENTS.md'],
  claude:   ['CLAUDE.md'],
  gemini:   ['GEMINI.md'],
};
const DETECTION_ORDER = [
  { platform: 'openclaw', files: ['AGENTS.md', 'SOUL.md'] },
  { platform: 'claude',   files: ['CLAUDE.md'] },
  { platform: 'gemini',   files: ['GEMINI.md'] },
];

function detectPlatform(workspace) {
  const forced = flag('platform');
  if (forced && PLATFORM_FILES[forced]) return forced;
  for (const { platform, files } of DETECTION_ORDER) {
    for (const f of files) {
      if (existsSync(join(workspace, f))) return platform;
    }
  }
  return 'openclaw';
}

function getAgentFile(platform) {
  return PLATFORM_FILES[platform]?.[0] || 'AGENTS.md';
}

// ── Workspace detection ──
// --workspace flag takes priority; otherwise walk up from skill dir
function findWorkspace() {
  const explicit = flag('workspace');
  if (explicit) {
    try { return realpathSync(resolve(explicit)); }
    catch { return resolve(explicit); }
  }
  // Skill is typically inside <workspace>/skills/knowledge-graph/
  try {
    const candidate = realpathSync(resolve(join(SKILL_DIR, '..', '..')));
    const allFiles = ['AGENTS.md', 'SOUL.md', 'CLAUDE.md', 'GEMINI.md'];
    if (allFiles.some(f => existsSync(join(candidate, f)))) return candidate;
  } catch {}
  // Fallback to default OpenClaw workspace
  const home = process.env.HOME || process.env.USERPROFILE || '/root';
  try { return realpathSync(join(home, '.openclaw', 'workspace')); }
  catch { return join(home, '.openclaw', 'workspace'); }
}

const WORKSPACE       = findWorkspace();
const PLATFORM        = detectPlatform(WORKSPACE);
const AGENT_FILENAME  = getAgentFile(PLATFORM);
const AGENT_FILE_PATH = join(WORKSPACE, AGENT_FILENAME);

// skillRelPath = path to skill dir as seen from WORKSPACE (for script commands in injected block)
// Priority: 1) skill inside target workspace → relative, 2) skill copy in target workspace → relative, 3) absolute fallback
let skillRelPath;
if (SKILL_DIR.startsWith(WORKSPACE + '/')) {
  // Skill IS inside the target workspace (e.g. Annie installing for herself)
  skillRelPath = relative(WORKSPACE, SKILL_DIR);
} else {
  // Cross-workspace install — check if target workspace has its own copy of the skill
  const skillDirName = SKILL_DIR.split('/').slice(-2).join('/'); // "skills/knowledge-graph"
  const localSkillDir = join(WORKSPACE, skillDirName);
  if (existsSync(join(localSkillDir, 'scripts'))) {
    // Target workspace has its own skill copy — use relative path to THAT copy
    skillRelPath = relative(WORKSPACE, localSkillDir);
  } else {
    // No local copy — fallback to absolute path of source skill
    skillRelPath = SKILL_DIR;
  }
}

// Resolve DATA_DIR: use the target skill dir (not source) so each workspace has its own data
const TARGET_SKILL_DIR = skillRelPath === SKILL_DIR
  ? SKILL_DIR                                    // absolute fallback (no local copy)
  : resolve(join(WORKSPACE, skillRelPath));       // local skill copy in target workspace
const DATA_DIR = join(TARGET_SKILL_DIR, 'data');

console.log(`🔧 Installing Knowledge Graph skill...`);
console.log(`   Skill dir:  ${SKILL_DIR}`);
console.log(`   Target dir: ${TARGET_SKILL_DIR}`);
console.log(`   Workspace:  ${WORKSPACE}`);
console.log(`   Skill path: ${skillRelPath}  ${skillRelPath === SKILL_DIR ? '(absolute — cross-workspace install)' : '(relative)'}`);
console.log(`   Data dir:   ${DATA_DIR}`);
console.log(`   Platform:   ${PLATFORM} (${AGENT_FILENAME})`);

// ── Step 1: Ensure data dir + store ──
if (!existsSync(DATA_DIR)) {
  mkdirSync(DATA_DIR, { recursive: true });
  console.log(`✅ Created data/`);
}

const STORE_PATH = join(DATA_DIR, 'kg-store.json');
if (!existsSync(STORE_PATH)) {
  const emptyStore = {
    version: 2,
    meta: { created: today(), lastConsolidated: null, entityCount: 0, edgeCount: 0, maxDepth: 0 },
    nodes: {},
    edges: [],
    categories: {}
  };
  writeFileSync(STORE_PATH, JSON.stringify(emptyStore, null, 2) + '\n');
  console.log(`✅ Created empty kg-store.json`);
} else {
  console.log(`⏭️  kg-store.json already exists`);
}

// ── Step 1b: Ensure default config ──
const CONFIG_PATH = join(DATA_DIR, 'kg-config.json');
if (!existsSync(CONFIG_PATH)) {
  writeFileSync(CONFIG_PATH, '{}\n');
  console.log(`✅ Created kg-config.json (empty — all defaults)`);
} else {
  console.log(`⏭️  kg-config.json already exists`);
}

// ── Step 2: Generate summary ──
try {
  const { toKGMLAsync } = await import('../lib/serialize.mjs');
  const kgml = await toKGMLAsync();
  writeFileSync(join(DATA_DIR, 'kg-summary.md'), kgml);
  console.log(`✅ Generated kg-summary.md`);
} catch (e) {
  console.log(`⚠️  Could not generate summary: ${e.message}`);
}

// ── Step 3: Patch agent instructions file ──
const KG_MARKER     = '<!-- KG-AUTONOMOUS-START -->';
const KG_MARKER_END = '<!-- KG-AUTONOMOUS-END -->';

if (existsSync(AGENT_FILE_PATH)) {
  let content = readFileSync(AGENT_FILE_PATH, 'utf8');
  if (content.includes(KG_MARKER)) {
    const startIdx = content.indexOf(KG_MARKER);
    const endIdx   = content.indexOf(KG_MARKER_END);
    if (endIdx !== -1) {
      content = content.slice(0, startIdx) + generateAgentsBlock() + content.slice(endIdx + KG_MARKER_END.length);
      writeFileSync(AGENT_FILE_PATH, content);
      console.log(`✅ Updated KG section in ${AGENT_FILENAME}`);
    }
  } else {
    content = content.trimEnd() + '\n\n' + generateAgentsBlock();
    writeFileSync(AGENT_FILE_PATH, content);
    console.log(`✅ Added KG section to ${AGENT_FILENAME}`);
  }
} else {
  writeFileSync(AGENT_FILE_PATH, generateAgentsBlock());
  console.log(`✅ Created ${AGENT_FILENAME} with KG section`);
}

// ── Step 4: Ensure .gitignore ──
const gitignorePath = join(DATA_DIR, '.gitignore');
const gitignoreContent = 'vault.enc.json\n.vault-key\nkg-store.json\nkg-summary.md\nkg-access.json\nkg-viz.html\nkg-config.json\n';
if (!existsSync(gitignorePath)) {
  writeFileSync(gitignorePath, gitignoreContent);
  console.log(`✅ Created data/.gitignore`);
} else {
  // Ensure kg-config.json is in gitignore
  const existing = readFileSync(gitignorePath, 'utf8');
  if (!existing.includes('kg-config.json')) {
    writeFileSync(gitignorePath, existing.trimEnd() + '\nkg-config.json\n');
    console.log(`✅ Updated data/.gitignore (added kg-config.json)`);
  }
}

console.log(`\n🎉 Knowledge Graph skill installed successfully!`);
console.log(`   → ${AGENT_FILENAME} patched with KG instructions (stable, cache-friendly)`);
console.log(`   → Agent will autonomously add/query knowledge`);
console.log(`   → Run "node ${skillRelPath}/scripts/summarize.mjs" after any KG changes`);

// ── Helpers ──

function today() { return new Date().toISOString().slice(0, 10); }

function generateAgentsBlock() {
  const s = skillRelPath; // shorthand — relative or absolute depending on install context

  return `${KG_MARKER}
## Knowledge Graph (Autonomous)

Structured knowledge store — **always available, use proactively without being asked.**

### Every Session
Read \`${s}/data/kg-summary.md\` to see what's in the graph.

### When to ADD (do this automatically):
- New **person, project, device, org, service, concept** mentioned
- **Decision** made or **credential/API key** shared (use vault for secrets)
- **Preferences/opinions** → entity + \`likes\`/\`dislikes\` relation
- **People relationships** → \`human\` + \`knows\` relation
- **Places, events, habits, milestones** → matching entity type
- **Knowledge** (articles, papers) → \`knowledge\` entity — **run depth-check first, follow its output**
- **Know-how/procedures** → \`knowledge\` + tags \`#howto\`/\`#procedure\`
- **After any change: ALWAYS run** \`node ${s}/scripts/summarize.mjs\`

### 📊 Extracting Knowledge from Articles (Script-Driven)

When saving an article/paper/report, follow this exact workflow:

**Step 1: Save article text** to \`/tmp/article.txt\` (fetch → save)

**Step 2: Run depth-check** to get score + extraction template:
\`\`\`bash
node ${s}/scripts/depth-check.mjs --file /tmp/article.txt
\`\`\`

**Step 3: Write a bash script** following the template from depth-check output.
The script MUST include all 5 phases. Structure:

\`\`\`bash
#!/bin/bash
set -e
S=${s}/scripts  # shorthand for scripts path

# ── PHASE 1: Root + Domain nodes ──
node $S/add.mjs entity --id "ROOT_ID" --type "knowledge" --label "Title" --attrs '{"url":"...","date":"..."}'
node $S/add.mjs entity --id "domain_X" --type "concept" --label "Domain" --parent "ROOT_ID"

# ── PHASE 2: Mechanism/concept nodes UNDER domains ──
node $S/add.mjs entity --id "mech_X" --type "concept" --label "Mechanism" --parent "domain_X" --attrs '{"description":"..."}'

# ── PHASE 3: Orgs, People, Events UNDER mechanisms (depth ≥3!) ──
# ⚠️ Orgs/events go under MECHANISMS, not directly under domains!
#    root → domain → mechanism → org/event (this gives depth 3+)
# ⚠️ EVERY org MUST have --attrs with role/stats. No empty shells!
# ⚠️ EVERY event MUST have --attrs with date. No dateless events!
# ⚠️ EVERY named org/person = SEPARATE entity. Do NOT merge!
node $S/add.mjs entity --id "org_X" --type "org" --label "Org" --parent "mech_X" --attrs '{"role":"...","stats":"..."}'
node $S/add.mjs entity --id "event_X" --type "event" --label "Event" --parent "mech_X" --attrs '{"date":"Q1 2027","details":"..."}'
node $S/add.mjs entity --id "human_X" --type "human" --label "Person" --attrs '{"role":"..."}'

# ── PHASE 4: Relations (≥1 per 2 entities) ──
# Types: owns, depends_on, related_to, part_of, created, manages, uses, has
node $S/add.mjs rel --from "org_X" --to "org_Y" --rel "owns"
node $S/add.mjs rel --from "event_X" --to "org_X" --rel "related_to"

# ── PHASE 5: Validate (MANDATORY — do NOT skip!) ──
node $S/summarize.mjs
echo ""
echo "=== VALIDATION ==="
node $S/validate-kg.mjs --file /tmp/article.txt --root "ROOT_ID" --fix
\`\`\`

**Step 4: Run the script.** Check the validation output at the end.

**Step 5: If validation says ❌ FAIL** — read the missing items, write ANOTHER script to fix gaps, run it. Repeat until ✅ PASS.

### Key Rules
- **Every named org** in the article = separate \`org\` entity with attrs (role, stats). No empty shells.
- **Every dated event** = separate \`event\` entity with date in attrs.
- **Stats** (%, $) go in the SPECIFIC entity's attrs, not the root node.
- **Hierarchy**: root → domains → mechanisms → orgs/events (depth ≥ 3). Not flat.
- **Relations**: ≥1 per 2 entities. Cross-link between branches.
- **Anti-pattern "Attr stuffing"**: NEVER put a named org only inside another entity's attrs JSON. It MUST be its own node.

### API Reference
\`\`\`bash
# Add entity:
node ${s}/scripts/add.mjs entity --id <id> --type <type> --label "Name" [--parent <pid>] [--category <cat>] [--tags "t1,t2"] [--attrs '{"k":"v"}']
# Add relation:
node ${s}/scripts/add.mjs rel --from <id> --to <id> --rel <reltype>
# Quick add (auto id/tags):
node ${s}/scripts/add.mjs quick "Label:type" [--parent <id>] [--category <cat>]
# Remove:
node ${s}/scripts/remove.mjs entity --id <id>
node ${s}/scripts/remove.mjs rel --from <id> --to <id> --rel <reltype>
# Validate extraction:
node ${s}/scripts/validate-kg.mjs --file /tmp/article.txt --root <id> --fix
# Search:
node ${s}/scripts/query.mjs find <text>
node ${s}/scripts/query.mjs traverse <id> --depth 3
# Other: vault.mjs, visualize.mjs, consolidate.mjs, summarize.mjs
\`\`\`

**Entity types:** \`human\` \`ai\` \`device\` \`platform\` \`project\` \`decision\` \`concept\` \`skill\` \`network\` \`credential\` \`org\` \`service\` \`place\` \`event\` \`media\` \`product\` \`account\` \`routine\` \`knowledge\`
**Relations:** \`owns\` \`uses\` \`runs_on\` \`runs\` \`created\` \`related_to\` \`part_of\` \`instance_of\` \`decided\` \`depends_on\` \`connected\` \`manages\` \`likes\` \`dislikes\` \`located_in\` \`knows\` \`member_of\` \`has\`

### Configuration
\`\`\`bash
node ${s}/scripts/config.mjs                  # list all settings
node ${s}/scripts/config.mjs get <key>         # get value (e.g. summary.tokenBudget)
node ${s}/scripts/config.mjs set <key> <value> # set value
node ${s}/scripts/config.mjs reset <key>       # reset to default
\`\`\`

### Rules
- **Always add tags** — synonyms, translations, abbreviations for cross-language search
- Ephemeral notes → \`memory/\` daily files, not KG
- Rapidly changing data (weather, prices) → not KG
- Confidence: \`1.0\` = confirmed, \`0.5\` = inferred
${KG_MARKER_END}
`;
}
