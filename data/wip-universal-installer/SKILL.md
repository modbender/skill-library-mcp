---
name: wip-universal-installer
version: 2.1.5
description: The Universal Interface specification for agent-native software. Teaches your AI how to build repos with every interface.
homepage: https://github.com/wipcomputer/wip-universal-installer
metadata:
  category: dev-tools
  capabilities:
    - detect-interfaces
    - install-cli
    - install-mcp
    - install-openclaw-plugin
    - install-claude-code-hook
  dependencies: []
  interface: CLI
openclaw:
  emoji: "🔌"
  install:
    env: []
author:
  name: Parker Todd Brooks
---

# wip-universal-installer

Reference installer for agent-native software. Scans a repo, detects which interfaces it exposes, and installs them all.

## When to Use This Skill

**Use wip-install for:**
- Installing any repo that follows the Universal Interface pattern
- Detecting what interfaces a repo provides
- Setting up CLI tools, MCP servers, OpenClaw plugins, and Claude Code hooks in one command

**Use detect.mjs for:**
- Programmatically detecting interfaces in a repo
- Building custom installers or CI pipelines
- Validating that a repo follows the spec

### Do NOT Use For

- Installing standard npm packages (use npm directly)
- Repos that don't follow the Universal Interface conventions
- Building or compiling code (this only installs)

## API Reference

### CLI

```bash
wip-install /path/to/repo           # install all interfaces
wip-install org/repo                 # clone from GitHub + install
wip-install --dry-run /path/to/repo  # detect only, no changes
wip-install --json /path/to/repo     # JSON output
```

### Module (detect.mjs)

```javascript
import { detectInterfaces, describeInterfaces, detectInterfacesJSON } from './detect.mjs';

const { interfaces, pkg } = detectInterfaces('/path/to/repo');
console.log(describeInterfaces(interfaces));

const json = detectInterfacesJSON('/path/to/repo');
console.log(JSON.stringify(json, null, 2));
```

## Universal Interface

See [SPEC.md](https://github.com/wipcomputer/wip-universal-installer/blob/main/SPEC.md) for the full specification.

1. **CLI** ... `package.json` bin field
2. **Module** ... `package.json` main/exports
3. **MCP Server** ... `mcp-server.mjs`
4. **OpenClaw Plugin** ... `openclaw.plugin.json`
5. **Skill** ... `SKILL.md`
6. **Claude Code Hook** ... `guard.mjs` or `claudeCode.hook`
