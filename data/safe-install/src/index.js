import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { scanSkill } from '@mike007jd/openclaw-clawshield';

export const TOOL = 'safe-install';
export const VERSION = '0.1.0';

const DEFAULT_POLICY = {
  defaultAction: 'prompt',
  blockedPatterns: [],
  allowedSources: [],
  forceRequiredForAvoid: true
};

// Safety limits
const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024; // 100MB
const MAX_FILES_PER_SKILL = 10000;
const MAX_TOTAL_SIZE_BYTES = 500 * 1024 * 1024; // 500MB

function nowIso() {
  return new Date().toISOString();
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      args._.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

function makeEnvelope(status, data = {}, errors = []) {
  return {
    tool: TOOL,
    version: VERSION,
    timestamp: nowIso(),
    status,
    data,
    errors
  };
}

function ensureDir(targetPath) {
  fs.mkdirSync(targetPath, { recursive: true });
}

function defaultPolicyPath(cwd = process.cwd()) {
  return path.join(cwd, '.openclaw-tools', `${TOOL}.json`);
}

function defaultStoreRoot(cwd = process.cwd()) {
  return path.join(cwd, '.openclaw-tools', TOOL);
}

function loadJsonIfExists(filePath, fallback) {
  if (!fs.existsSync(filePath)) return fallback;
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function saveJson(filePath, value) {
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, `${JSON.stringify(value, null, 2)}\n`, 'utf8');
}

export function validatePolicy(policy) {
  const errors = [];
  if (!['allow', 'prompt', 'block'].includes(policy.defaultAction)) {
    errors.push('defaultAction must be allow|prompt|block');
  }
  if (!Array.isArray(policy.blockedPatterns)) {
    errors.push('blockedPatterns must be an array');
  }
  if (!Array.isArray(policy.allowedSources)) {
    errors.push('allowedSources must be an array');
  }
  if (typeof policy.forceRequiredForAvoid !== 'boolean') {
    errors.push('forceRequiredForAvoid must be boolean');
  }
  return { valid: errors.length === 0, errors };
}

function loadPolicy(configPath) {
  const merged = {
    ...DEFAULT_POLICY,
    ...loadJsonIfExists(configPath, {})
  };
  return merged;
}

function readHistory(storeRoot) {
  const historyPath = path.join(storeRoot, 'history.json');
  return loadJsonIfExists(historyPath, []);
}

function appendHistory(storeRoot, record) {
  const historyPath = path.join(storeRoot, 'history.json');
  const history = readHistory(storeRoot);
  history.push(record);
  saveJson(historyPath, history);
}

function readState(storeRoot) {
  return loadJsonIfExists(path.join(storeRoot, 'state.json'), { active: {} });
}

function writeState(storeRoot, state) {
  saveJson(path.join(storeRoot, 'state.json'), state);
}

function validateSafeName(name) {
  // Only allow safe characters: lowercase letters, numbers, dot, hyphen, underscore
  const SAFE_NAME_PATTERN = /^[a-z0-9._-]+$/;
  return SAFE_NAME_PATTERN.test(name) && !name.includes('..');
}

function assertSafePath(targetPath, storeRoot) {
  // Normalize paths for comparison (without requiring existence)
  const resolvedTarget = path.normalize(path.resolve(targetPath));
  const resolvedRoot = path.normalize(path.resolve(storeRoot));
  // Ensure target is within storeRoot
  if (!resolvedTarget.startsWith(resolvedRoot)) {
    throw new Error(`Path traversal detected: ${targetPath} escapes ${storeRoot}`);
  }
  // Additional check: no '..' components in the relative path
  const relative = path.relative(resolvedRoot, resolvedTarget);
  if (relative.startsWith('..') || relative.includes('../')) {
    throw new Error(`Path traversal detected: ${targetPath} contains forbidden traversal`);
  }
  return resolvedTarget;
}

function listFilesRecursive(root, out = [], stats = { count: 0, totalSize: 0 }) {
  if (stats.count > MAX_FILES_PER_SKILL) {
    throw new Error(`Too many files in skill: exceeds ${MAX_FILES_PER_SKILL}`);
  }
  if (stats.totalSize > MAX_TOTAL_SIZE_BYTES) {
    throw new Error(`Skill too large: exceeds ${MAX_TOTAL_SIZE_BYTES} bytes`);
  }
  const entries = fs.readdirSync(root, { withFileTypes: true });
  for (const entry of entries) {
    if (entry.name === 'node_modules' || entry.name === '.git' || entry.name === 'dist') continue;
    const full = path.join(root, entry.name);
    if (entry.isDirectory()) {
      listFilesRecursive(full, out, stats);
      continue;
    }
    const fileStat = fs.statSync(full);
    if (fileStat.size > MAX_FILE_SIZE_BYTES) {
      throw new Error(`File too large: ${entry.name} (${fileStat.size} bytes)`);
    }
    stats.count += 1;
    stats.totalSize += fileStat.size;
    if (stats.count > MAX_FILES_PER_SKILL) {
      throw new Error(`Too many files in skill: exceeds ${MAX_FILES_PER_SKILL}`);
    }
    out.push(full);
  }
  return out;
}

function hashDirectory(rootPath) {
  const stats = { count: 0, totalSize: 0 };
  const files = listFilesRecursive(rootPath, [], stats).sort();
  const hash = crypto.createHash('sha256');
  for (const filePath of files) {
    hash.update(path.relative(rootPath, filePath));
    hash.update(fs.readFileSync(filePath));
  }
  return hash.digest('hex');
}

function parseSkillSpec(spec) {
  const atIndex = spec.lastIndexOf('@');
  if (atIndex <= 0) {
    return { name: spec, version: 'latest' };
  }
  return {
    name: spec.slice(0, atIndex),
    version: spec.slice(atIndex + 1) || 'latest'
  };
}

function detectSkillMeta(sourcePath, spec) {
  const parsedSpec = parseSkillSpec(spec);
  const packagePath = path.join(sourcePath, 'package.json');
  let skillName, version;
  if (fs.existsSync(packagePath)) {
    const pkg = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
    skillName = pkg.name || parsedSpec.name || path.basename(sourcePath);
    version = pkg.version || parsedSpec.version || '0.0.0';
  } else {
    skillName = parsedSpec.name || path.basename(sourcePath);
    version = parsedSpec.version || '0.0.0';
  }
  
  // Validate skill name and version for path safety
  if (!validateSafeName(skillName)) {
    throw new Error(`Invalid skill name: "${skillName}". Only [a-z0-9._-] allowed, no ".."`);
  }
  if (!validateSafeName(version)) {
    throw new Error(`Invalid version: "${version}". Only [a-z0-9._-] allowed, no ".."`);
  }
  
  return { skill: skillName, version };
}

function resolveSourcePath(spec, policy) {
  const candidate = path.resolve(spec);
  if (fs.existsSync(candidate) && fs.statSync(candidate).isDirectory()) {
    return candidate;
  }

  const registry = policy.registry && typeof policy.registry === 'object' ? policy.registry : {};
  const mapped = registry[spec];
  if (mapped) {
    const resolved = path.resolve(mapped);
    if (fs.existsSync(resolved) && fs.statSync(resolved).isDirectory()) {
      return resolved;
    }
  }

  throw new Error(`Cannot resolve skill source for: ${spec}`);
}

function sourceAllowed(policy, sourcePath, skillName) {
  if (!policy.allowedSources.length) return true;
  return policy.allowedSources.some((allowed) => sourcePath.includes(allowed) || skillName.includes(allowed));
}

async function promptConfirm(message) {
  const rl = readline.createInterface({ input, output });
  try {
    const answer = await rl.question(`${message} [y/N]: `);
    return /^y(es)?$/i.test(answer.trim());
  } finally {
    rl.close();
  }
}

function copyDir(sourcePath, targetPath, storeRoot) {
  // Security: validate target path is within storeRoot
  if (storeRoot) {
    assertSafePath(targetPath, storeRoot);
  }
  ensureDir(path.dirname(targetPath));
  fs.rmSync(targetPath, { recursive: true, force: true });
  fs.cpSync(sourcePath, targetPath, { recursive: true });
}

function renderHistoryTable(history) {
  const lines = ['safe-install history', ''];
  if (history.length === 0) {
    lines.push('No install attempts recorded.');
    return lines.join('\n');
  }
  for (const entry of history.slice().reverse()) {
    lines.push(
      `- ${entry.installedAt} | ${entry.skill}@${entry.version} | ${entry.status} | decision=${entry.decision}`
    );
  }
  return lines.join('\n');
}

function printHelp() {
  console.log(`safe-install usage:
  safe-install <skill[@version]|local-path> [--force] [--yes] [--format <table|json>] [--config <path>] [--store <path>]
  safe-install history [--format <table|json>] [--store <path>]
  safe-install rollback <skill> [--format <table|json>] [--store <path>]
  safe-install policy validate --file <path> [--format <table|json>]`);
}

export async function installSkill(spec, options = {}) {
  const cwd = options.cwd || process.cwd();
  const policyPath = path.resolve(options.config || defaultPolicyPath(cwd));
  const storeRoot = path.resolve(options.store || defaultStoreRoot(cwd));
  const policy = loadPolicy(policyPath);

  const validation = validatePolicy(policy);
  if (!validation.valid) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: validation.errors
    };
  }

  const sourcePath = resolveSourcePath(spec, policy);
  const meta = detectSkillMeta(sourcePath, spec);

  const scanResult = scanSkill(sourcePath, { suppressionsPath: policy.suppressionsPath });
  const blockedPattern = (policy.blockedPatterns || []).find((pattern) => {
    try {
      return new RegExp(pattern, 'i').test(sourcePath);
    } catch {
      return false;
    }
  });

  if (!sourceAllowed(policy, sourcePath, meta.skill)) {
    const record = {
      skill: meta.skill,
      version: meta.version,
      hash: null,
      decision: 'Avoid',
      policy: path.basename(policyPath),
      installedAt: nowIso(),
      status: 'blocked',
      reason: 'source-not-allowed'
    };
    appendHistory(storeRoot, record);
    return {
      code: 2,
      status: 'blocked',
      data: { record, scan: scanResult },
      errors: ['Source is not in policy allowedSources.']
    };
  }

  if (blockedPattern) {
    const record = {
      skill: meta.skill,
      version: meta.version,
      hash: null,
      decision: 'Avoid',
      policy: path.basename(policyPath),
      installedAt: nowIso(),
      status: 'blocked',
      reason: `blocked-pattern:${blockedPattern}`
    };
    appendHistory(storeRoot, record);
    return {
      code: 2,
      status: 'blocked',
      data: { record, scan: scanResult },
      errors: [`Source path matches blocked pattern: ${blockedPattern}`]
    };
  }

  let decision = scanResult.riskLevel;
  let approved = false;

  if (decision === 'Safe') {
    approved = policy.defaultAction !== 'block';
  } else if (decision === 'Caution') {
    if (options.yes) {
      approved = true;
    } else if (process.stdin.isTTY) {
      approved = await promptConfirm(`Skill ${meta.skill} is CAUTION. Continue installation?`);
    }
  } else {
    // Avoid
    approved = !!options.force || !policy.forceRequiredForAvoid;
  }

  if (!approved) {
    const record = {
      skill: meta.skill,
      version: meta.version,
      hash: null,
      decision,
      policy: path.basename(policyPath),
      installedAt: nowIso(),
      status: 'blocked',
      reason: 'policy-decision'
    };
    appendHistory(storeRoot, record);
    return {
      code: 2,
      status: 'blocked',
      data: { record, scan: scanResult },
      errors: ['Installation blocked by policy decision.']
    };
  }

  const hash = hashDirectory(sourcePath);
  const snapshotPath = path.join(storeRoot, 'snapshots', meta.skill, meta.version, hash);
  const activePath = path.join(storeRoot, 'active', meta.skill);
  
  // Security: verify paths are within storeRoot before any operations
  assertSafePath(snapshotPath, storeRoot);
  assertSafePath(activePath, storeRoot);
  
  copyDir(sourcePath, snapshotPath, storeRoot);
  copyDir(snapshotPath, activePath, storeRoot);

  const state = readState(storeRoot);
  state.active[meta.skill] = {
    version: meta.version,
    hash,
    snapshotPath,
    updatedAt: nowIso()
  };
  writeState(storeRoot, state);

  const record = {
    skill: meta.skill,
    version: meta.version,
    hash,
    decision,
    policy: path.basename(policyPath),
    installedAt: nowIso(),
    status: 'installed',
    sourcePath
  };
  appendHistory(storeRoot, record);

  return {
    code: 0,
    status: decision === 'Safe' ? 'ok' : 'warning',
    data: {
      install: record,
      scan: scanResult,
      activePath
    },
    errors: []
  };
}

export function rollbackSkill(skill, options = {}) {
  // Validate skill name for path safety
  if (!validateSafeName(skill)) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: [`Invalid skill name: "${skill}". Only [a-z0-9._-] allowed.`]
    };
  }
  
  const cwd = options.cwd || process.cwd();
  const storeRoot = path.resolve(options.store || defaultStoreRoot(cwd));
  const history = readHistory(storeRoot).filter((entry) => entry.skill === skill && entry.status === 'installed');

  if (history.length < 2) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: [`Not enough install history to rollback ${skill}.`]
    };
  }

  const state = readState(storeRoot);
  const current = state.active[skill];
  const sorted = history.slice().sort((a, b) => new Date(a.installedAt) - new Date(b.installedAt));

  let target = sorted[sorted.length - 2];
  if (current) {
    const previous = [...sorted].reverse().find((entry) => entry.hash !== current.hash);
    if (previous) {
      target = previous;
    }
  }

  const snapshotPath = path.join(storeRoot, 'snapshots', target.skill, target.version, target.hash);
  if (!fs.existsSync(snapshotPath)) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: [`Snapshot not found for rollback target: ${snapshotPath}`]
    };
  }
  
  // Security: verify paths are within storeRoot
  try {
    assertSafePath(snapshotPath, storeRoot);
  } catch (e) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: [`Security violation in snapshot path: ${e.message}`]
    };
  }

  const activePath = path.join(storeRoot, 'active', target.skill);
  
  try {
    assertSafePath(activePath, storeRoot);
  } catch (e) {
    return {
      code: 1,
      status: 'error',
      data: {},
      errors: [`Security violation in active path: ${e.message}`]
    };
  }
  
  copyDir(snapshotPath, activePath, storeRoot);
  state.active[skill] = {
    version: target.version,
    hash: target.hash,
    snapshotPath,
    updatedAt: nowIso()
  };
  writeState(storeRoot, state);

  const record = {
    skill,
    version: target.version,
    hash: target.hash,
    decision: 'Safe',
    policy: 'rollback',
    installedAt: nowIso(),
    status: 'rolled_back',
    sourcePath: snapshotPath
  };
  appendHistory(storeRoot, record);

  return {
    code: 0,
    status: 'ok',
    data: { rollbackTo: record, activePath },
    errors: []
  };
}

export function validatePolicyFile(filePath) {
  const resolved = path.resolve(filePath);
  if (!fs.existsSync(resolved)) {
    return { code: 1, status: 'error', data: {}, errors: [`Policy file not found: ${resolved}`] };
  }
  const parsed = JSON.parse(fs.readFileSync(resolved, 'utf8'));
  const validation = validatePolicy(parsed);
  return {
    code: validation.valid ? 0 : 1,
    status: validation.valid ? 'ok' : 'error',
    data: {
      file: resolved,
      valid: validation.valid
    },
    errors: validation.errors
  };
}

export async function runCli(argv) {
  const args = parseArgs(argv);
  const command = args._[0];
  const format = args.format || 'table';

  if (!command || args.help) {
    printHelp();
    return command ? 0 : 1;
  }

  try {
    if (command === 'history') {
      const storeRoot = path.resolve(args.store || defaultStoreRoot(process.cwd()));
      const history = readHistory(storeRoot);
      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope('ok', { history }), null, 2));
      } else {
        console.log(renderHistoryTable(history));
      }
      return 0;
    }

    if (command === 'rollback') {
      const skill = args._[1];
      if (!skill) {
        console.error(JSON.stringify(makeEnvelope('error', {}, ['Missing skill name for rollback']), null, 2));
        return 1;
      }
      const result = rollbackSkill(skill, { store: args.store });
      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope(result.status, result.data, result.errors), null, 2));
      } else if (result.code === 0) {
        console.log(`Rolled back ${skill} to ${result.data.rollbackTo.version}`);
      } else {
        console.error(result.errors.join('\n'));
      }
      return result.code;
    }

    if (command === 'policy' && args._[1] === 'validate') {
      const file = args.file;
      if (!file) {
        console.error(JSON.stringify(makeEnvelope('error', {}, ['Missing --file']), null, 2));
        return 1;
      }
      const result = validatePolicyFile(file);
      if (format === 'json') {
        console.log(JSON.stringify(makeEnvelope(result.status, result.data, result.errors), null, 2));
      } else if (result.code === 0) {
        console.log(`Policy is valid: ${result.data.file}`);
      } else {
        console.error(result.errors.join('\n'));
      }
      return result.code;
    }

    const installResult = await installSkill(command, {
      config: args.config,
      store: args.store,
      force: !!args.force,
      yes: !!args.yes
    });

    if (format === 'json') {
      console.log(JSON.stringify(makeEnvelope(installResult.status, installResult.data, installResult.errors), null, 2));
    } else if (installResult.code === 0) {
      const rec = installResult.data.install;
      console.log(`Installed ${rec.skill}@${rec.version} (${rec.hash.slice(0, 12)})`);
    } else {
      console.error(installResult.errors.join('\n'));
    }

    return installResult.code;
  } catch (error) {
    console.error(
      JSON.stringify(
        makeEnvelope('error', {}, [error instanceof Error ? error.message : String(error)]),
        null,
        2
      )
    );
    return 1;
  }
}
