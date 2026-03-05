#!/usr/bin/env node
/*
 * project CLI (v1)
 *
 * Minimal, dependency-free implementation of the design doc.
 *
 * Usage:
 *   project detect
 *   project context
 *   project target list
 *   project target run <target>
 *   project init
 *   project apply <planId>
 *   project artifact add <path|url> [--tags a,b,c]
 *   project search keyword <term>
 */

const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function die(msg, code = 1) {
  process.stderr.write(String(msg).trimEnd() + '\n');
  process.exit(code);
}

function nowIso() {
  return new Date().toISOString();
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(obj, null, 2));
}

function exists(p) {
  try {
    fs.accessSync(p);
    return true;
  } catch {
    return false;
  }
}

function findProjectRoot(startDir) {
  let dir = path.resolve(startDir || process.cwd());
  while (true) {
    const projDir = path.join(dir, '.project');
    if (exists(projDir)) return dir;

    // if git repo root contains .project
    if (exists(path.join(dir, '.git')) && exists(path.join(dir, '.project'))) return dir;

    const parent = path.dirname(dir);
    if (parent === dir) return null;
    dir = parent;
  }
}

function ensureBundle(root) {
  const projDir = path.join(root, '.project');
  if (!exists(projDir)) die(`No .project bundle found (run: project init) at or above ${process.cwd()}`);
  return projDir;
}

function loadTargets(root) {
  const projDir = ensureBundle(root);
  const tp = path.join(projDir, 'targets.json');
  if (!exists(tp)) return { version: 1, targets: {} };
  return readJson(tp);
}

function defaultInitPlan(root) {
  const planId = `plan-${Date.now()}`;
  const projDir = path.join(root, '.project');
  const slug = path.basename(root);

  const files = [
    {
      path: '.project/project.json',
      kind: 'json',
      content: {
        version: 1,
        slug,
        name: slug,
        createdAt: nowIso(),
      },
    },
    {
      path: '.project/PROJECT.md',
      kind: 'text',
      content:
        `# ${slug}\n\n` +
        `## Brief\n\n- What is this project?\n- What are the current goals?\n\n` +
        `## Conventions\n\n- Language/runtime:\n- Build/test:\n- Lint/format:\n\n` +
        `## Key links\n\n- Docs: \n- Repo: \n\n`,
    },
    {
      path: '.project/targets.json',
      kind: 'json',
      content: {
        version: 1,
        targets: {
          context: {
            description: 'Print project context (PROJECT.md) and target list',
            commands: [],
          },
          build: { description: 'Build the project (fill in)', commands: [] },
          test: { description: 'Run tests (fill in)', commands: [] },
          lint: { description: 'Run lint checks (fill in)', commands: [] },
          format: { description: 'Auto-format (fill in)', commands: [] },
          run: { description: 'Run the app (fill in)', commands: [] },
          dev: { description: 'Dev mode/watchers (fill in)', commands: [] },
          deploy: { description: 'Deploy workflow (fill in)', commands: [] },
          doctor: { description: 'Project health checks (fill in)', commands: [] },
          artifacts: { description: 'List artifacts', commands: [] },
        },
      },
    },
    {
      path: '.project/index/artifacts.json',
      kind: 'json',
      content: { version: 1, artifacts: [] },
    },
  ];

  return {
    id: planId,
    kind: 'init',
    createdAt: nowIso(),
    root,
    writes: files,
  };
}

function savePlan(root, plan) {
  const projDir = path.join(root, '.project');
  const p = path.join(projDir, 'history', 'plans', `${plan.id}.json`);
  writeJson(p, plan);
  return p;
}

function applyPlan(root, planId) {
  const projDir = path.join(root, '.project');
  const planPath = path.join(projDir, 'history', 'plans', `${planId}.json`);
  if (!exists(planPath)) die(`Plan not found: ${planId}`);
  const plan = readJson(planPath);

  const applied = [];
  for (const w of plan.writes || []) {
    const dst = path.join(root, w.path);
    if (w.kind === 'json') {
      writeJson(dst, w.content);
    } else {
      fs.mkdirSync(path.dirname(dst), { recursive: true });
      fs.writeFileSync(dst, String(w.content));
    }
    applied.push({ path: w.path, kind: w.kind });
  }

  const receipt = {
    id: `apply-${Date.now()}`,
    planId,
    appliedAt: nowIso(),
    root,
    writes: applied,
  };

  const receiptPath = path.join(projDir, 'history', 'applies', `${receipt.id}.json`);
  writeJson(receiptPath, receipt);

  return { receipt, receiptPath };
}

function addArtifactPlan(root, spec, tags) {
  const planId = `plan-${Date.now()}`;
  const projDir = ensureBundle(root);

  const artifactsPath = path.join(projDir, 'index', 'artifacts.json');
  const idx = exists(artifactsPath) ? readJson(artifactsPath) : { version: 1, artifacts: [] };

  const artifact = {
    id: `artifact-${Date.now()}`,
    createdAt: nowIso(),
    type: /^https?:\/\//.test(spec) ? 'url' : 'file',
    spec,
    tags: tags || [],
  };

  // plan writes the updated index
  const next = { ...idx, artifacts: [...(idx.artifacts || []), artifact] };

  return {
    id: planId,
    kind: 'artifact.add',
    createdAt: nowIso(),
    root,
    writes: [
      {
        path: '.project/index/artifacts.json',
        kind: 'json',
        content: next,
      },
    ],
  };
}

function printContext(root) {
  const projDir = ensureBundle(root);
  const md = path.join(projDir, 'PROJECT.md');
  const pj = path.join(projDir, 'project.json');
  const targets = loadTargets(root);

  const meta = exists(pj) ? readJson(pj) : null;
  const brief = exists(md) ? fs.readFileSync(md, 'utf8') : '';

  process.stdout.write(`# Project: ${meta?.name || path.basename(root)}\n`);
  process.stdout.write(`Root: ${root}\n\n`);
  if (brief) process.stdout.write(brief.trimEnd() + '\n\n');

  const names = Object.keys(targets.targets || {}).sort();
  process.stdout.write('## Targets\n');
  for (const n of names) {
    const d = targets.targets[n]?.description || '';
    process.stdout.write(`- ${n}${d ? ` — ${d}` : ''}\n`);
  }
}

function runTarget(root, targetName) {
  const targets = loadTargets(root);
  const t = (targets.targets || {})[targetName];
  if (!t) die(`Unknown target: ${targetName}`);

  // built-in targets
  if (targetName === 'context') {
    printContext(root);
    return { code: 0 };
  }
  if (targetName === 'artifacts') {
    const p = path.join(ensureBundle(root), 'index', 'artifacts.json');
    const idx = exists(p) ? readJson(p) : { version: 1, artifacts: [] };
    process.stdout.write(JSON.stringify(idx, null, 2) + '\n');
    return { code: 0 };
  }

  const commands = t.commands || [];
  if (!Array.isArray(commands) || commands.length === 0) {
    die(`Target '${targetName}' has no commands. Define it in .project/targets.json`);
  }

  const results = [];
  for (const cmd of commands) {
    const r = spawnSync(cmd, {
      cwd: root,
      shell: true,
      stdio: 'inherit',
      env: process.env,
    });
    results.push({ cmd, status: r.status });
    if (r.status !== 0) return { code: r.status ?? 1, results };
  }
  return { code: 0, results };
}

function keywordSearch(root, term) {
  // v1: grep within .project + a few common docs if present
  const projDir = ensureBundle(root);
  const candidates = [
    projDir,
    path.join(root, 'README.md'),
    path.join(root, 'docs'),
  ].filter((p) => exists(p));

  const hits = [];
  const esc = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const re = new RegExp(esc, 'i');

  function walk(p) {
    const st = fs.statSync(p);
    if (st.isDirectory()) {
      for (const ent of fs.readdirSync(p)) {
        if (ent === 'node_modules' || ent === '.git') continue;
        walk(path.join(p, ent));
      }
      return;
    }
    if (st.size > 2_000_000) return; // skip huge
    let txt;
    try {
      txt = fs.readFileSync(p, 'utf8');
    } catch {
      return;
    }
    const lines = txt.split(/\r?\n/);
    for (let i = 0; i < lines.length; i++) {
      if (re.test(lines[i])) hits.push({ file: path.relative(root, p), line: i + 1, text: lines[i].slice(0, 300) });
    }
  }

  for (const c of candidates) walk(c);
  process.stdout.write(JSON.stringify({ term, hits }, null, 2) + '\n');
}

// --- arg parsing ---
const argv = process.argv.slice(2);
if (argv.length === 0) die('usage: project <verb> ...');

const verb = argv[0];

if (verb === 'detect') {
  const root = findProjectRoot(process.cwd());
  if (!root) die('No .project bundle found in parent directories', 2);
  process.stdout.write(JSON.stringify({ root, projectDir: path.join(root, '.project') }, null, 2) + '\n');
  process.exit(0);
}

if (verb === 'context') {
  const root = findProjectRoot(process.cwd());
  if (!root) die('No .project bundle found in parent directories', 2);
  printContext(root);
  process.exit(0);
}

if (verb === 'target') {
  const sub = argv[1];
  const root = findProjectRoot(process.cwd());
  if (!root) die('No .project bundle found in parent directories', 2);

  if (sub === 'list') {
    const targets = loadTargets(root);
    process.stdout.write(JSON.stringify({ root, targets: targets.targets || {} }, null, 2) + '\n');
    process.exit(0);
  }

  if (sub === 'run') {
    const t = argv[2];
    if (!t) die('usage: project target run <target>');
    const r = runTarget(root, t);
    process.exit(r.code);
  }

  die('usage: project target <list|run> ...');
}

if (verb === 'init') {
  const root = process.cwd();
  const plan = defaultInitPlan(root);
  const planPath = savePlan(root, plan);
  process.stdout.write(JSON.stringify({ plan, planPath }, null, 2) + '\n');
  process.exit(0);
}

if (verb === 'apply') {
  const root = findProjectRoot(process.cwd()) || process.cwd();
  const planId = argv[1];
  if (!planId) die('usage: project apply <planId>');
  // if no bundle yet, apply assumes CWD is the root
  const r = applyPlan(root, planId);
  process.stdout.write(JSON.stringify(r, null, 2) + '\n');
  process.exit(0);
}

if (verb === 'artifact') {
  const sub = argv[1];
  if (sub !== 'add') die('usage: project artifact add <path|url> [--tags a,b,c]');

  const spec = argv[2];
  if (!spec) die('usage: project artifact add <path|url> [--tags a,b,c]');

  let tags = [];
  const ti = argv.indexOf('--tags');
  if (ti !== -1) tags = String(argv[ti + 1] || '').split(',').map((s) => s.trim()).filter(Boolean);

  const root = findProjectRoot(process.cwd());
  if (!root) die('No .project bundle found in parent directories (run: project init)', 2);

  const plan = addArtifactPlan(root, spec, tags);
  const planPath = savePlan(root, plan);
  process.stdout.write(JSON.stringify({ plan, planPath }, null, 2) + '\n');
  process.exit(0);
}

if (verb === 'search') {
  const sub = argv[1];
  if (sub !== 'keyword') die('usage: project search keyword <term>');
  const term = argv.slice(2).join(' ').trim();
  if (!term) die('usage: project search keyword <term>');
  const root = findProjectRoot(process.cwd());
  if (!root) die('No .project bundle found in parent directories', 2);
  keywordSearch(root, term);
  process.exit(0);
}

die(`Unknown verb: ${verb}`);
