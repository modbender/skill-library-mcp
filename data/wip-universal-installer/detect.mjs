/**
 * wip-universal-installer/detect.mjs
 * Interface detection logic. Scans a repo and reports which interfaces it exposes.
 * Importable by other tools. Zero dependencies.
 */

import { existsSync, readFileSync } from 'node:fs';
import { join, basename } from 'node:path';

function readJSON(path) {
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

/**
 * Detect all interfaces in a repo.
 * Returns { interfaces, pkg } where interfaces is an object keyed by interface type.
 */
export function detectInterfaces(repoPath) {
  const interfaces = {};
  const pkg = readJSON(join(repoPath, 'package.json'));

  // 1. CLI: package.json has bin entry
  if (pkg?.bin) {
    interfaces.cli = { bin: pkg.bin, name: pkg.name };
  }

  // 2. Module: package.json has main or exports
  if (pkg?.main || pkg?.exports) {
    interfaces.module = { main: pkg.main || pkg.exports };
  }

  // 3. MCP Server: mcp-server.mjs/js/ts or dist/mcp-server.js
  const mcpFiles = ['mcp-server.mjs', 'mcp-server.js', 'mcp-server.ts', 'dist/mcp-server.js'];
  for (const f of mcpFiles) {
    if (existsSync(join(repoPath, f))) {
      interfaces.mcp = { file: f, name: pkg?.name || basename(repoPath) };
      break;
    }
  }

  // 4. OpenClaw Plugin: openclaw.plugin.json exists
  const ocPlugin = join(repoPath, 'openclaw.plugin.json');
  if (existsSync(ocPlugin)) {
    interfaces.openclaw = { config: readJSON(ocPlugin), path: ocPlugin };
  }

  // 5. Skill: SKILL.md exists
  if (existsSync(join(repoPath, 'SKILL.md'))) {
    interfaces.skill = { path: join(repoPath, 'SKILL.md') };
  }

  // 6. Claude Code Hook: guard.mjs or claudeCode.hook in package.json
  if (pkg?.claudeCode?.hook) {
    interfaces.claudeCodeHook = pkg.claudeCode.hook;
  } else if (existsSync(join(repoPath, 'guard.mjs'))) {
    interfaces.claudeCodeHook = {
      event: 'PreToolUse',
      matcher: 'Edit|Write',
      command: `node "${join(repoPath, 'guard.mjs')}"`,
      timeout: 5
    };
  }

  return { interfaces, pkg };
}

/**
 * Describe detected interfaces as a human-readable summary.
 */
export function describeInterfaces(interfaces) {
  const lines = [];
  const names = Object.keys(interfaces);

  if (names.length === 0) {
    return 'No interfaces detected.';
  }

  if (interfaces.cli) {
    const bins = typeof interfaces.cli.bin === 'string' ? [interfaces.cli.name] : Object.keys(interfaces.cli.bin);
    lines.push(`CLI: ${bins.join(', ')}`);
  }
  if (interfaces.module) lines.push(`Module: ${JSON.stringify(interfaces.module.main)}`);
  if (interfaces.mcp) lines.push(`MCP Server: ${interfaces.mcp.file}`);
  if (interfaces.openclaw) lines.push(`OpenClaw Plugin: ${interfaces.openclaw.config?.name || 'detected'}`);
  if (interfaces.skill) lines.push(`Skill: SKILL.md`);
  if (interfaces.claudeCodeHook) lines.push(`Claude Code Hook: ${interfaces.claudeCodeHook.event || 'PreToolUse'}`);

  return `${names.length} interface(s): ${names.join(', ')}\n${lines.map(l => `  ${l}`).join('\n')}`;
}

/**
 * Detect interfaces and return a structured JSON-serializable result.
 */
export function detectInterfacesJSON(repoPath) {
  const { interfaces, pkg } = detectInterfaces(repoPath);
  return {
    repo: basename(repoPath),
    package: pkg?.name || null,
    version: pkg?.version || null,
    interfaces: Object.fromEntries(
      Object.entries(interfaces).map(([type, info]) => [type, {
        detected: true,
        ...info,
      }])
    ),
    interfaceCount: Object.keys(interfaces).length,
  };
}
