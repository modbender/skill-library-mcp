---
name: /security-scan - AIclude Security Vulnerability Scanner
description: Scan MCP Servers and AI Agent Skills for security vulnerabilities.
  Returns existing scan results instantly if available, or registers the target
  and triggers a new scan automatically.
---

# /security-scan - AIclude Security Vulnerability Scanner

Scan MCP Servers and AI Agent Skills for security vulnerabilities. Returns existing scan results instantly if available, or registers the target and triggers a new scan automatically.

## Usage

```
# Search by name (recommended - leverages existing scan results)
/security-scan --name <package-name> [options]

# Scan a local directory directly
/security-scan <target-path> [options]
```

## Parameters

- `--name`: Name of the MCP server or Skill to search (npm package name, GitHub repo, etc.)
- `target-path`: Local path to scan (use instead of --name)
- `--type`: Target type (`mcp-server` | `skill`) - auto-detected if omitted
- `--profile`: Sandbox isolation profile (`strict` | `standard` | `permissive`)
- `--format`: Report output format (`markdown` | `json`)
- `--engines`: Scan engines to use (comma-separated)

## Examples

```
# Search security scan results for an MCP server
/security-scan --name @anthropic/mcp-server-fetch

# Search scan results for a Skill
/security-scan --name my-awesome-skill --type skill

# Scan local source code
/security-scan ./my-mcp-server
```

## What It Checks

- **Prompt Injection**: Hidden prompt injection patterns targeting LLMs
- **Tool Poisoning**: Malicious instructions embedded in tool descriptions
- **Command Injection**: Unvalidated input passed to exec/spawn calls
- **Supply Chain**: Known CVEs in dependencies and malicious packages (typosquatting)
- **Malware**: Backdoors, cryptominers, ransomware, data stealers, and obfuscated code
- **Permission Abuse**: Excessive filesystem, network, or process permissions

## Scan Engines

7 engines run in parallel for comprehensive coverage:

| Engine | Description |
|--------|-------------|
| SAST | Static code pattern matching against YAML rule sets |
| SCA | Dependency CVE lookup via OSV.dev, SBOM generation |
| Tool Analyzer | MCP tool definition analysis (poisoning, shadowing, rug-pull) |
| DAST | Parameter fuzzing (SQL/Command/XSS injection) |
| Permission Checker | Filesystem, network, and process permission analysis |
| Behavior Monitor | Runtime behavior pattern detection |
| Malware Detector | Signature scanning, entropy analysis, backdoor detection |

## Output

The report includes:
1. **Risk Level Summary** (CRITICAL / HIGH / MEDIUM / LOW / INFO)
2. **Vulnerability List** (code location, description, severity)
3. **Risk Assessment** (what risks are present and their impact)
4. **Remediation Recommendations** (how to fix each vulnerability)

## Web Dashboard

View all scan results at https://vs.aiclude.com
