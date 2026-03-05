---
name: guardskills
description: Security gate for skill installs. Scans skill content for malicious patterns (credential exfiltration, remote code execution, destructive ops, privilege escalation) before installation. Always run guardskills before installing any skill from ClawHub, GitHub, or local sources.
homepage: https://github.com/felixondesk/guardskills
metadata:
  {
    "openclaw":
      {
        "emoji": "🛡️",
        "requires": { "bins": ["guardskills"] },
        "install":
          [
            {
              "id": "node",
              "kind": "node",
              "package": "guardskills",
              "bins": ["guardskills"],
              "label": "Install guardskills (npm)",
            },
          ],
      },
  }
---

# GuardSkills — Security Scanner for Skills

Static analysis security gate. Scans skill files for malicious patterns and produces a risk decision before allowing installation.

## Rule — ALWAYS scan before installing

Before installing any skill (ClawHub, GitHub, local, or skills.sh), you MUST run a guardskills scan first. Never run `clawhub install`, `skills add`, or copy skill files without scanning.

## Scan by source

### 1. ClawHub skills

When the user asks to install a ClawHub skill, scan it first:

```bash
guardskills scan-clawhub <owner/skill-slug>
```

Also accepts full URLs:

```bash
guardskills scan-clawhub https://clawhub.ai/owner/skill-slug
```

### 2. Local skills

When loading or reviewing a skill folder on disk:

```bash
guardskills scan-local <path-to-skill-folder>
```

If the path contains multiple skills:

```bash
guardskills scan-local <path-to-skills-root> --skill <skill-folder-name>
```

### 3. GitHub skills

When installing from a GitHub repository:

```bash
guardskills add owner/repo --skill <skill-name> --dry-run
```

Also accepts full URLs:

```bash
guardskills add https://github.com/owner/repo --skill <skill-name> --dry-run
```

### 4. skills.sh skills

Use the same GitHub flow:

```bash
guardskills add owner/repo --skill <skill-name> --dry-run
```

If scan passes:

```bash
guardskills add owner/repo --skill <skill-name>
```

## How to interpret results

| Decision       | Action                                                       |
| -------------- | ------------------------------------------------------------ |
| `SAFE`         | Proceed with installation.                                   |
| `WARNING`      | Ask the user for confirmation before proceeding.             |
| `UNSAFE`       | Block. Tell the user the skill is unsafe and do not install.  |
| `CRITICAL`     | Block. Do not install under any circumstances.               |
| `UNVERIFIABLE` | Block. Inform the user the skill could not be verified.      |

## Useful flags

- `--json` — machine-readable JSON output
- `--dry-run` — scan only, do not install
- `--ci` — deterministic gate mode (no prompts, no install)
- `--strict` — use stricter risk thresholds
- `--yes` — auto-accept WARNING level (only if user explicitly requests)
- `--force` — override UNSAFE block (only if user explicitly requests)
- `--allow-unverifiable` — override UNVERIFIABLE block (only if user explicitly requests)

## Exit codes

- `0` — allowed / safe
- `10` — warning not confirmed
- `20` — blocked (UNSAFE, CRITICAL, or UNVERIFIABLE)
- `30` — runtime / internal error

## Recommended workflow

1. User asks to install a skill.
2. Determine the source (ClawHub, GitHub, local, skills.sh).
3. Run the appropriate `guardskills` scan command.
4. Read the decision from the output.
5. If `SAFE`, proceed with `clawhub install` or equivalent.
6. If `WARNING`, inform the user and ask for confirmation.
7. If `UNSAFE`, `CRITICAL`, or `UNVERIFIABLE`, block and explain why.
8. Never skip the scan step.

## Notes

- guardskills is an additional security layer, not a replacement for manual review.
- A `SAFE` result means no known high-risk patterns were detected, not a guarantee of safety.
- The scanner checks for: credential exfiltration, remote code execution chains, destructive filesystem operations, privilege escalation, obfuscated payloads, and suspicious network activity.
