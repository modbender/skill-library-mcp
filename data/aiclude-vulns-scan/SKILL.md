---
name: aiclude-vulns-scan
description: Search security vulnerability scan results for MCP Servers and AI Agent Skills from the AICLUDE scan database.
tags: [security, vulnerability, scanner, mcp, ai-agent]
homepage: https://vs.aiclude.com
repository: https://github.com/aiclude/asvs
---

# /security-scan - AICLUDE Vulnerability Scanner

Search the AICLUDE security scan database for vulnerability reports on MCP Servers and AI Agent Skills. If no report exists, the target is registered and scanned automatically.

## Usage

```
/security-scan --name <package-name> [--type mcp-server|skill]
```

## Parameters

- `--name`: Package name to search (npm package, GitHub repo, etc.)
- `--type`: Target type (`mcp-server` | `skill`) - auto-detected if omitted

## Examples

```
/security-scan --name @anthropic/mcp-server-fetch
/security-scan --name my-awesome-skill --type skill
```

## How It Works

1. Sends the package name to the AICLUDE scan API
2. If a scan report exists, returns it immediately
3. If not, registers the target for scanning
4. Waits for the scan to complete and returns the results
5. Results are also viewable at https://vs.aiclude.com

Only the package name and type are sent. No source code or credentials are transmitted.

## Output

- **Risk Level** (CRITICAL / HIGH / MEDIUM / LOW / INFO)
- **Vulnerability List** with locations and descriptions
- **Risk Assessment** and remediation recommendations

## Links

- **Web Dashboard**: https://vs.aiclude.com
- **npm**: [`@aiclude/security-skill`](https://www.npmjs.com/package/@aiclude/security-skill)
- **MCP Server**: [`@aiclude/security-mcp`](https://www.npmjs.com/package/@aiclude/security-mcp)

## License

Apache 2.0 - AICLUDE Inc.
