# @aiclude/security-skill

Security vulnerability scanner for MCP Servers and AI Agent Skills. Provides the `/security-scan` slash command for Claude Code.

Queries the [AICLUDE scan database](https://vs.aiclude.com) for existing vulnerability reports. If no report exists, the target is automatically registered and scanned server-side.

## Installation

```bash
npm install @aiclude/security-skill
```

## Usage

### As a Claude Code Skill

```
/security-scan --name @anthropic/mcp-server-fetch
/security-scan --name my-awesome-skill --type skill
```

### Programmatic API

```typescript
import { SkillHandler } from "@aiclude/security-skill";

const handler = new SkillHandler();

const report = await handler.lookup({
  name: "@some/mcp-server",
  type: "mcp-server",
});
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--name` | Package name to search (npm, GitHub, etc.) |
| `--type` | `mcp-server` or `skill` (auto-detected) |

## How It Works

1. Sends the package name to the AICLUDE scan API
2. If a scan report exists, returns it immediately
3. If not, registers the target for server-side scanning
4. Waits for the scan to complete and returns the results

Only the package name and type are sent. No source code, files, or credentials are transmitted.

## Server-Side Scan Engines

The AICLUDE server runs 7 engines on registered targets:

| Engine | What It Detects |
|--------|----------------|
| SAST | Code vulnerabilities via pattern matching |
| SCA | Known CVEs in dependencies (OSV.dev) |
| Tool Analyzer | MCP tool poisoning, shadowing, rug-pull |
| DAST | SQL/Command/XSS injection via fuzzing |
| Permission Checker | Excessive filesystem/network/process access |
| Behavior Monitor | Suspicious runtime behavior patterns |
| Malware Detector | Backdoors, cryptominers, ransomware, data stealers |

## Output

Reports include:

1. **Risk Level** — CRITICAL / HIGH / MEDIUM / LOW / INFO
2. **Vulnerability List** — code location, description, severity
3. **Risk Assessment** — impact and likelihood analysis
4. **Remediation** — how to fix each finding

## Related Packages

- [`@aiclude/security-mcp`](https://www.npmjs.com/package/@aiclude/security-mcp) — MCP Server interface
- [vs.aiclude.com](https://vs.aiclude.com) — Web dashboard with full scan results

## License

Apache 2.0 — [AICLUDE Inc.](https://aiclude.com)
