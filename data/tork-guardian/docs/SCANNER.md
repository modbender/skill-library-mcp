# Tork Security Scanner

The Tork Security Scanner analyzes OpenClaw skills **before installation** to detect vulnerabilities, malicious patterns, and unsafe code. It assigns a risk score, renders a verdict, and generates a Tork Verified badge for skills that pass.

## Detection Rules

The scanner ships with 14 built-in rules across two categories:

### Code Security (SEC)

| ID | Name | Severity | Detects |
|----|------|----------|---------|
| SEC-001 | eval() usage | High | `eval()` calls that enable arbitrary code execution |
| SEC-002 | Function constructor | High | `new Function()` that creates functions from strings |
| SEC-003 | child_process usage | Critical | `require('child_process')`, `exec()`, `spawn()` calls |
| SEC-004 | Write to sensitive paths | High | `writeFile` / `appendFile` targeting `.env`, `.ssh`, `/etc/` |
| SEC-005 | Hardcoded API keys/secrets | Critical | `api_key = "sk_live_..."`, `secret_key = "..."` patterns |
| SEC-006 | Prompt injection patterns | Critical | "Ignore previous instructions", "you are now a", etc. |
| SEC-007 | Data exfiltration via HTTP | High | `fetch()` / `axios` / `http.request` to external URLs |

### Network Security (NET)

| ID | Name | Severity | Detects |
|----|------|----------|---------|
| NET-001 | Server creation | Medium | `net.createServer`, `http.createServer`, `https.createServer` |
| NET-002 | Hardcoded IP addresses | High | Raw IPs in strings (bypasses domain allowlists) |
| NET-003 | UDP socket creation | High | `dgram.createSocket` (DNS tunneling, C2 channels) |
| NET-004 | DNS TXT record queries | Critical | `dns.resolveTxt`, TXT record lookups (data exfil channel) |
| NET-005 | Process spawn + network call | Critical | `exec("curl ...")`, `spawn("wget ...")`, `spawn("nc ...")` |
| NET-006 | WebSocket to non-standard domains | Medium | `new WebSocket("wss://external...")` |
| NET-007 | Sequential port scanning | Critical | `net.connect`, `net.createConnection` with port args |

## CLI Usage

### Basic scan

```bash
npx tork-scan ./my-skill
```

### With full finding details

```bash
npx tork-scan ./my-skill --verbose
```

### JSON output (for CI/CD pipelines)

```bash
npx tork-scan ./my-skill --json
```

### Strict mode (fail on any high+ finding)

```bash
npx tork-scan ./my-skill --strict
```

## CLI Flags

| Flag | Description |
|------|-------------|
| `--json` | Output results as JSON (report + badge) |
| `--verbose` | Show full details for every finding (snippet, description, remediation) |
| `--strict` | Exit code 1 if any high or critical finding is present |
| `-h`, `--help` | Show usage information |

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | Skill is verified or reviewed |
| 1 | Skill is flagged, or `--strict` and high+ findings exist |
| 2 | Scanner error (invalid path, etc.) |

## Risk Score Calculation

Each finding contributes to the risk score based on its severity:

| Severity | Weight |
|----------|--------|
| Critical | 25 |
| High | 15 |
| Medium | 8 |
| Low | 3 |

The total is capped at 100. Formula: `min(100, sum of weights)`.

**Examples:**
- 1 medium finding: score = 8
- 1 critical + 1 high: score = 40
- 4 critical findings: score = 100

## Verdict Tiers

| Verdict | Score Range | Meaning |
|---------|-------------|---------|
| **Verified** | 0 - 29 | Safe to install. No significant security concerns. |
| **Reviewed** | 30 - 49 | Review recommended. Some patterns need manual inspection. |
| **Flagged** | 50 - 100 | Do not install. Significant security risks detected. |

## Badge System

After scanning, generate a Tork Verified badge for your skill README:

```typescript
import { SkillScanner, generateBadge, generateBadgeMarkdown } from '@tork/guardian';

const scanner = new SkillScanner();
const report = await scanner.scanSkill('./my-skill');
const badge = generateBadge(report);
const markdown = generateBadgeMarkdown(badge);

console.log(markdown);
// [![Tork Verified](https://img.shields.io/badge/...)](https://tork.network/verify/my-skill)
```

### Badge tiers

| Badge | Color | Meaning |
|-------|-------|---------|
| Tork Verified | Green (`#22c55e`) | Score < 30. Safe to install. |
| Tork Reviewed | Yellow (`#eab308`) | Score 30-49. Manual review recommended. |
| Tork Flagged | Red (`#ef4444`) | Score >= 50. Security risks detected. |
| Tork Unverified | Gray (`#6b7280`) | Not yet scanned. |

## Example Scan Output

```
╔══════════════════════════════════════════╗
║          Tork Security Scanner           ║
╚══════════════════════════════════════════╝

  Skill:          my-agent-skill
  Files scanned:  12
  Scan duration:  45ms
  Findings:       3
  Risk score:     48/100
  Verdict:        REVIEWED
  Badge:          Tork Reviewed (reviewed)

── Findings ────────────────────────────────

  Critical (1):
  [CRIT] SEC-003: child_process usage
         src/tools/shell.ts:15:1
         const cp = require("child_process");
         → Direct use of child_process can execute arbitrary system commands.
         ✓ Use Tork Guardian governTool() to validate commands before execution.

  High (1):
  [HIGH] SEC-001: eval() usage
         src/parser.ts:42:12
         const result = eval(expression);
         → Use of eval() allows arbitrary code execution and is a common injection vector.
         ✓ Replace eval() with JSON.parse(), Function(), or a safe expression parser.

  Medium (1):
  [MED ] NET-001: Server creation
         src/server.ts:8:1
         const server = http.createServer(app);
         → Creating network servers may expose the host to inbound connections.
         ✓ Use Tork Guardian validatePortBind() to govern which ports may be opened.

  [![Tork Reviewed](https://img.shields.io/badge/Tork%20Reviewed-reviewed-eab308)](https://tork.network/verify/my-agent-skill)
```

## Programmatic Usage

```typescript
import { SkillScanner } from '@tork/guardian';

const scanner = new SkillScanner();

// Scan an entire skill directory
const report = await scanner.scanSkill('./my-skill');
console.log(`Risk: ${report.riskScore}, Verdict: ${report.verdict}`);

// Scan a single file
const findings = await scanner.scanFile('./my-skill/src/index.ts');
findings.forEach(f => console.log(`${f.ruleId}: ${f.ruleName} at line ${f.line}`));

// Calculate risk from custom findings
const score = scanner.calculateRiskScore(findings);
```

See [QUICK-START.md](QUICK-START.md) for a 2-minute setup guide.
