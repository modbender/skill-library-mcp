# clawhub-scanner

OpenClaw skill + npm package that scans installed ClawHub skills for known malicious patterns, IoCs, and security risks.

## Context
ClawHub (the OpenClaw skill marketplace) has a massive malware problem:
- 534 critical vulnerabilities found by Snyk (Feb 2026)
- 341 skills distributing Atomic Stealer (AMOS) malware ("ClawHavoc")
- 76 confirmed malicious payloads for credential theft
- Known C2 server: 91.92.242.30

## What to Build

### Package: `@elvatis_com/clawhub-scanner`
TypeScript, published to npm.

### Core Features
1. **Scan installed skills** - Read all skills from `~/.openclaw/skills/` and ClawHub cache
2. **Pattern matching** - Check for known malicious patterns:
   - Credential harvesting (API keys, tokens, SSH keys, browser data)
   - Data exfiltration (outbound HTTP to suspicious domains/IPs)
   - Prompt injection attempts in skill descriptions/instructions
   - Obfuscated code (base64 encoded commands, eval(), dynamic imports)
   - Known malicious C2 IPs/domains (hardcoded + updatable list)
   - Suspicious file access patterns (~/.ssh, ~/.aws, browser profiles, keychain)
3. **Integrity check** - Hash verification against known-good versions
4. **Report generation** - Clean, human-readable report with severity levels

### Detection Rules (patterns to flag)
```
HIGH: eval(), Function(), child_process.exec with dynamic input
HIGH: fetch/axios/http to IP addresses or non-standard ports
HIGH: Access to ~/.ssh, ~/.aws, ~/.gnupg, browser profile dirs
HIGH: Base64 decode + exec patterns
HIGH: Known C2 IPs (91.92.242.30, etc.)
MEDIUM: Broad file system reads outside skill directory
MEDIUM: Environment variable harvesting (process.env iteration)
MEDIUM: Clipboard access
LOW: Network calls to unrecognized domains
LOW: Large encoded strings (>500 chars base64)
```

### CLI Interface
```bash
# Scan all installed skills
clawhub-scanner scan

# Scan specific skill
clawhub-scanner scan --skill my-skill

# Update threat intelligence
clawhub-scanner update

# Output JSON for automation
clawhub-scanner scan --json

# Verbose mode
clawhub-scanner scan -v
```

### Project Structure
```
src/
  index.ts          # Main entry point + CLI
  scanner.ts        # Core scanning logic
  patterns.ts       # Detection rules/patterns
  indicators.ts     # Known IoCs (IPs, domains, hashes)
  reporter.ts       # Output formatting
  types.ts          # TypeScript types
tests/
  scanner.test.ts
  patterns.test.ts
package.json
tsconfig.json
README.md
LICENSE               # MIT
```

### Tech Stack
- TypeScript, Node.js 18+
- No heavy dependencies - keep it lean
- vitest for tests
- Commander.js for CLI
- chalk for colored output

### npm publish
- Scope: @elvatis_com
- `npm publish --access public`

### Quality
- All functions typed
- Tests for every detection pattern
- README with usage examples and screenshots of output
