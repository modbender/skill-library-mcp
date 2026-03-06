#!/usr/bin/env node
// wip-universal-installer/install.mjs
// Reference installer for agent-native software.
// Reads a repo, detects available interfaces, installs them all.

import { execSync } from 'node:child_process';
import { existsSync, readFileSync, writeFileSync, cpSync, mkdirSync } from 'node:fs';
import { join, basename, resolve } from 'node:path';
import { detectInterfaces, describeInterfaces, detectInterfacesJSON } from './detect.mjs';

const OPENCLAW_DIR = join(process.env.HOME, '.openclaw');
const EXTENSIONS_DIR = join(OPENCLAW_DIR, 'extensions');

// Flags
const args = process.argv.slice(2);
const DRY_RUN = args.includes('--dry-run');
const JSON_OUTPUT = args.includes('--json');
const target = args.find(a => !a.startsWith('--'));

function log(msg) { if (!JSON_OUTPUT) console.log(`  ${msg}`); }
function ok(msg) { if (!JSON_OUTPUT) console.log(`  ✓ ${msg}`); }
function skip(msg) { if (!JSON_OUTPUT) console.log(`  - ${msg}`); }
function fail(msg) { if (!JSON_OUTPUT) console.error(`  ✗ ${msg}`); }

function readJSON(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function installCLI(repoPath, door) {
  if (DRY_RUN) {
    ok(`CLI: would install globally (dry run)`);
    return true;
  }
  try {
    execSync('npm install -g .', { cwd: repoPath, stdio: 'pipe' });
    const binNames = typeof door.bin === 'string' ? [basename(repoPath)] : Object.keys(door.bin);
    ok(`CLI: ${binNames.join(', ')} installed globally`);
    return true;
  } catch (e) {
    try {
      execSync('npm link', { cwd: repoPath, stdio: 'pipe' });
      ok(`CLI: linked globally via npm link`);
      return true;
    } catch {
      fail(`CLI: install failed. Run manually: cd "${repoPath}" && npm install -g .`);
      return false;
    }
  }
}

function installOpenClaw(repoPath, door) {
  const name = door.config?.name || basename(repoPath);
  const dest = join(EXTENSIONS_DIR, name);

  if (DRY_RUN) {
    ok(`OpenClaw: would copy to ${dest} (dry run)`);
    return true;
  }

  if (existsSync(dest)) {
    skip(`OpenClaw: ${name} already installed at ${dest}`);
    return true;
  }

  try {
    mkdirSync(dest, { recursive: true });
    cpSync(repoPath, dest, { recursive: true, filter: (src) => !src.includes('.git') });
    ok(`OpenClaw: copied to ${dest}`);

    if (existsSync(join(dest, 'package.json'))) {
      try {
        execSync('npm install --omit=dev', { cwd: dest, stdio: 'pipe' });
        ok(`OpenClaw: dependencies installed`);
      } catch {
        skip(`OpenClaw: no deps needed`);
      }
    }
    return true;
  } catch (e) {
    fail(`OpenClaw: copy failed. ${e.message}`);
    return false;
  }
}

function installClaudeCodeHook(repoPath, door) {
  const settingsPath = join(process.env.HOME, '.claude', 'settings.json');
  let settings = readJSON(settingsPath);

  if (!settings) {
    skip(`Claude Code: no settings.json found at ${settingsPath}`);
    return false;
  }

  if (DRY_RUN) {
    ok(`Claude Code: would add ${door.event || 'PreToolUse'} hook (dry run)`);
    return true;
  }

  if (!settings.hooks) settings.hooks = {};
  const event = door.event || 'PreToolUse';

  if (!settings.hooks[event]) settings.hooks[event] = [];

  const hookCommand = door.command || `node "${join(repoPath, 'guard.mjs')}"`;
  const existing = settings.hooks[event].some(entry =>
    entry.hooks?.some(h => h.command === hookCommand)
  );

  if (existing) {
    skip(`Claude Code: ${event} hook already configured`);
    return true;
  }

  settings.hooks[event].push({
    matcher: door.matcher || undefined,
    hooks: [{
      type: 'command',
      command: hookCommand,
      timeout: door.timeout || 10
    }]
  });

  try {
    writeFileSync(settingsPath, JSON.stringify(settings, null, 2) + '\n');
    ok(`Claude Code: ${event} hook added to settings.json`);
    return true;
  } catch (e) {
    fail(`Claude Code: failed to update settings.json. ${e.message}`);
    return false;
  }
}

async function main() {
  if (!target || target === '--help' || target === '-h') {
    console.log('');
    console.log('  wip-install ... the reference installer for agent-native software');
    console.log('');
    console.log('  Usage:');
    console.log('    wip-install /path/to/repo');
    console.log('    wip-install https://github.com/org/repo');
    console.log('    wip-install org/repo');
    console.log('');
    console.log('  Flags:');
    console.log('    --dry-run   Detect interfaces without installing anything');
    console.log('    --json      Output detection results as JSON');
    console.log('');
    console.log('  Interfaces it detects:');
    console.log('    CLI        ... package.json bin entry -> npm install -g');
    console.log('    Module     ... ESM main/exports -> importable');
    console.log('    MCP Server ... mcp-server.mjs -> config for .mcp.json');
    console.log('    OpenClaw   ... openclaw.plugin.json -> copies to extensions/');
    console.log('    Skill      ... SKILL.md -> agent instructions');
    console.log('    CC Hook    ... guard.mjs or claudeCode.hook -> settings.json');
    console.log('');
    process.exit(0);
  }

  // Resolve target: GitHub URL, org/repo shorthand, or local path
  let repoPath;

  if (target.startsWith('http') || target.startsWith('git@') || target.match(/^[\w-]+\/[\w.-]+$/)) {
    const url = target.match(/^[\w-]+\/[\w.-]+$/)
      ? `https://github.com/${target}.git`
      : target;
    const repoName = basename(url).replace('.git', '');
    repoPath = join('/tmp', `wip-install-${repoName}`);

    log('');
    log(`Cloning ${url}...`);
    try {
      if (existsSync(repoPath)) {
        execSync(`rm -rf "${repoPath}"`);
      }
      execSync(`git clone "${url}" "${repoPath}"`, { stdio: 'pipe' });
      ok(`Cloned to ${repoPath}`);
    } catch (e) {
      fail(`Clone failed: ${e.message}`);
      process.exit(1);
    }
  } else {
    repoPath = resolve(target);
    if (!existsSync(repoPath)) {
      fail(`Path not found: ${repoPath}`);
      process.exit(1);
    }
  }

  // JSON mode: detect and output
  if (JSON_OUTPUT) {
    const result = detectInterfacesJSON(repoPath);
    console.log(JSON.stringify(result, null, 2));
    if (DRY_RUN) process.exit(0);
    // If not dry run, continue with install but suppress output
  }

  // Detect interfaces
  const { interfaces, pkg } = detectInterfaces(repoPath);
  const ifaceNames = Object.keys(interfaces);

  if (ifaceNames.length === 0) {
    skip('No installable interfaces detected.');
    process.exit(0);
  }

  if (!JSON_OUTPUT) {
    console.log('');
    const repoName = basename(repoPath);
    console.log(`  Installing: ${repoName}${DRY_RUN ? ' (dry run)' : ''}`);
    console.log(`  ${'─'.repeat(40)}`);
    log(`Detected ${ifaceNames.length} interface(s): ${ifaceNames.join(', ')}`);
    console.log('');
  }

  if (DRY_RUN && !JSON_OUTPUT) {
    // In dry run, show what would happen
    console.log(describeInterfaces(interfaces));
    console.log('');
    console.log('  Dry run complete. No changes made.');
    console.log('');
    process.exit(0);
  }

  // Install each interface
  let installed = 0;

  if (interfaces.cli) {
    installCLI(repoPath, interfaces.cli);
    installed++;
  }

  if (interfaces.openclaw) {
    installOpenClaw(repoPath, interfaces.openclaw);
    installed++;
  }

  if (interfaces.claudeCodeHook) {
    installClaudeCodeHook(repoPath, interfaces.claudeCodeHook);
    installed++;
  }

  if (interfaces.mcp) {
    if (!JSON_OUTPUT) {
      console.log('');
      log(`MCP Server detected: ${interfaces.mcp.file}`);
      log(`Add to .mcp.json:`);
      console.log(JSON.stringify({
        [interfaces.mcp.name]: {
          command: 'node',
          args: [join(repoPath, interfaces.mcp.file)]
        }
      }, null, 2));
    }
    installed++;
  }

  if (interfaces.skill) {
    ok(`Skill: SKILL.md available at ${interfaces.skill.path}`);
    installed++;
  }

  if (interfaces.module) {
    ok(`Module: import from "${interfaces.module.main}"`);
    installed++;
  }

  if (!JSON_OUTPUT) {
    console.log('');
    console.log(`  Done. ${installed} interface(s) processed.`);
    console.log('');
  }
}

main().catch(e => {
  fail(e.message);
  process.exit(1);
});
