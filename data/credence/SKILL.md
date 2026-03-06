---
name: credence
description: Check any MCP server or AI tool against the Credence trust registry before installing it. Scores security, provenance, and behavioral risk on a 0-100 scale.
user-invocable: true
metadata: {"openclaw": {"emoji": "🛡️", "requires": {"bins": ["curl"]}, "os": ["darwin", "linux", "win32"], "tags": ["security", "trust", "mcp"]}}
---

# Credence

Check MCP servers and AI tools against the Credence trust registry before you install them.

## When to use this skill

- Before installing any MCP server
- When a user asks you to add an MCP server or AI tool
- When you want to verify whether a tool is safe
- When the user asks `/credence`

## How it works

Credence scans MCP servers and AI tools for security issues, verifies their provenance, and checks behavioral risk. Every scanned tool gets a trust score from 0 to 100 and a verdict:

| Score | Verdict | Meaning |
|-------|---------|---------|
| 90-100 | APPROVED | Safe to install |
| 70-89 | CONDITIONAL | Review the flagged items before installing |
| 40-69 | FLAGGED | Significant concerns — install only if you understand the risks |
| 0-39 | REJECTED | Do not install |

## Instructions

### Check a server by name or URL

Fetch the Credence registry and look up the server:

```bash
curl -s "https://raw.githubusercontent.com/pestafford/credence-registry/main/registry/index.json"
```

Search the `servers` array for a match on `server_id`, `server_name`, `canonical_name`, or `repo_url`. The match does not need to be exact — partial matches on the repo URL or server name are fine.

**If found**, report:

```
Credence: <server_name>
  Score: <trust_score>/100
  Verdict: <thinktank_verdict>
  Scanned: <attested_at>
  Registry: https://credence.securingthesingularity.com/registry.html
```

Then give your recommendation:
- **APPROVED (90+):** Safe to install. Proceed.
- **CONDITIONAL (70-89):** Mention the score and suggest the user review the registry page for details before installing.
- **FLAGGED (40-69):** Warn the user. Do not install without explicit confirmation.
- **REJECTED (0-39):** Do not install. Explain that Credence found serious issues.

**If not found**, say:

```
This tool has not been scanned by Credence yet.
Submit it for scanning at: https://credence.securingthesingularity.com/#submit
```

Then let the user decide whether to proceed.

### Check before installing

Whenever you are about to install or connect to an MCP server (via `claude mcp add`, editing `claude_desktop_config.json`, or any other method), check it against Credence first. If the server is not in the registry, tell the user it hasn't been scanned and ask if they want to proceed anyway.

### Get full details

For more detail on a specific server, fetch its attestation file. The `attestation_file` path from the index entry is relative to:

```
https://raw.githubusercontent.com/pestafford/credence-registry/main/registry/
```

The attestation includes the full score breakdown (security, provenance, behavioral), scan metadata, and the deliberation verdict.

## Examples

**User says:** "Add the filesystem MCP server"

1. Fetch the registry index
2. Find `modelcontextprotocol/servers/filesystem` — score 88, APPROVED
3. Report: "Credence score: 88/100 (APPROVED). Safe to install."
4. Proceed with the install

**User says:** "Install some-unknown-server"

1. Fetch the registry index
2. Not found
3. Report: "This server hasn't been scanned by Credence yet. You can submit it at https://credence.securingthesingularity.com/#submit — want to install anyway?"

**User says:** `/credence modelcontextprotocol/servers/memory`

1. Fetch the registry index
2. Find it — score 98, APPROVED
3. Report the full status

## Notes

- The registry is public and requires no authentication
- Scores are based on automated scanning plus adversarial AI deliberation
- A missing entry does not mean a tool is dangerous — it just hasn't been scanned yet
- For the full methodology, see https://credence.securingthesingularity.com/faq.html
