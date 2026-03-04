# OpenScan

A lightweight malware detection library for OpenClaw, targeting macOS and Linux binaries and scripts. Ported from the [Harkonnen](https://github.com/dev-null321/Harkonnen) antimalware engine.

## Why This Exists

OpenClaw skills can declare binary dependencies via `requires.bins`. Users install these binaries from various sources (Homebrew, npm, apt, random GitHub releases). There's currently no verification that these binaries are safe.

This scanner provides:
- **Pre-trust scanning** of binaries before execution
- **Skill folder auditing** to catch malicious scripts
- **Programmatic API** for integration into OpenClaw's skill loading

## Features

### Binary Analysis

| Platform | Format | Detection |
|----------|--------|-----------|
| macOS | Mach-O (32/64-bit, Universal/FAT) | Suspicious dylibs, code signature, encryption, security flags |
| Linux | ELF (32/64-bit) | Suspicious shared objects, security features (PIE, NX, RELRO) |

**What it checks:**
- **Suspicious libraries**: Frida, Cynject, MobileSubstrate, injection frameworks
- **Code signatures**: Missing or invalid signatures (macOS)
- **Security features**: ASLR/PIE disabled, executable stack/heap, missing NX
- **Packing/encryption**: High entropy detection, encrypted segments
- **Segment anomalies**: Suspicious names like `__INJECT`, `UPX`, `__MALWARE`

### Pattern Detection

Scans binary content for:
- **Shellcode patterns**: x86/x64 prologue sequences, NOP sleds, infinite loops
- **Suspicious APIs**: Process injection (CreateRemoteThread, VirtualAllocEx), keylogging (GetAsyncKeyState), anti-debugging (IsDebuggerPresent)
- **Network indicators**: Embedded URLs, IP addresses
- **Encoded payloads**: Large base64 blobs

### Script Analysis

For shell scripts, Python, JavaScript, etc.:
- **Dangerous patterns**: `curl | bash`, `eval()`, base64 decode + exec
- **Persistence mechanisms**: crontab, launchctl, LaunchAgents
- **Injection vectors**: `LD_PRELOAD`, `DYLD_INSERT_LIBRARIES`
- **Obfuscation**: Heavy hex escaping, very long lines

## Installation

```bash
# Clone the repo
git clone https://github.com/marqbritt/openscan.git
cd openscan

# No dependencies - pure Node.js
node bin/scan.js --help
```

Or install globally:
```bash
npm install -g .
openclaw-scan --help
```

## Usage

### Command Line

```bash
# Scan a single binary
node bin/scan.js /usr/local/bin/some-tool

# Scan a skill folder
node bin/scan.js ~/.openclaw/skills/some-skill

# JSON output (for automation)
node bin/scan.js /path/to/binary --json

# Only show threats (score > 20)
node bin/scan.js /path/to/folder --quiet

# Disable colors (for logging)
node bin/scan.js /path --no-color
```

### Programmatic API

```javascript
const { scanFile, scanDirectory, formatResult } = require('openscan');

// Scan a single file
async function checkBinary(path) {
  const result = await scanFile(path);
  
  console.log(`${result.name}: ${result.threatLevel} (${result.threatScore}/100)`);
  
  if (result.threatScore > 40) {
    console.log('Findings:', result.findings);
    return false; // Don't trust
  }
  return true;
}

// Scan an entire skill folder
async function auditSkill(skillPath) {
  const results = await scanDirectory(skillPath);
  
  const threats = results.filter(r => r.threatScore > 20);
  if (threats.length > 0) {
    console.log(`Found ${threats.length} suspicious files:`);
    threats.forEach(r => console.log(formatResult(r)));
  }
  
  return threats.length === 0;
}
```

### Integration Examples

**Pre-install hook (conceptual):**
```javascript
// In OpenClaw's skill loader
async function loadSkill(skillPath) {
  const meta = parseSkillMeta(skillPath);
  
  if (meta.requires?.bins) {
    for (const bin of meta.requires.bins) {
      const binPath = which(bin);
      if (binPath) {
        const result = await scanFile(binPath);
        if (result.threatScore > 60) {
          throw new Error(`Binary ${bin} failed security scan: ${result.findings.join(', ')}`);
        }
      }
    }
  }
  
  // Continue loading...
}
```

**Agent self-check:**
```javascript
// Before recommending a tool to the user
const { scanFile } = require('openscan');

async function recommendTool(toolPath) {
  const result = await scanFile(toolPath);
  
  if (result.threatScore > 40) {
    return `⚠️ Warning: ${toolPath} has suspicious characteristics:\n${result.findings.join('\n')}`;
  }
  
  return `✓ ${toolPath} appears safe (score: ${result.threatScore}/100)`;
}
```

## Threat Scoring

Each file receives a score from 0-100 based on weighted findings:

| Score | Level | Color | Meaning |
|-------|-------|-------|---------|
| 0-20 | CLEAN | Green | No significant findings |
| 21-40 | LOW | Yellow | Minor concerns, probably safe |
| 41-60 | MEDIUM | Orange | Suspicious patterns, review manually |
| 61-80 | HIGH | Red | Likely malicious or dangerous |
| 81-100 | CRITICAL | Purple | Known malicious patterns |

**Scoring weights:**
- Suspicious dylib/library: +15 per finding
- Missing code signature: +10 (macOS)
- High entropy (>7.5): +25
- Shellcode pattern: +20 per pattern
- Suspicious API reference: +5 per API (max 30)
- Dangerous script pattern: +10 per pattern
- Security features disabled: +5-15 depending on feature

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean (max score ≤ 20) |
| 1 | Suspicious (max score 21-60) |
| 2 | High threat (max score > 60) |

## Output Format

### Human-readable (default)

```
[CLEAN] ls
  Path: /bin/ls
  Type: macho | Size: 151.0KB
  Score: 12/100
  SHA256: 03a229a30505d148f4a66f3eaa1d046d7f6e7e4c2b7abd8f4cf0e3ac2b124651
  Findings:
    - Suspicious API: exec
    - Found 4 URL(s)
```

### JSON (--json)

```json
{
  "path": "/bin/ls",
  "name": "ls",
  "exists": true,
  "size": 154624,
  "type": "macho",
  "hashes": {
    "md5": "...",
    "sha256": "..."
  },
  "threatScore": 12,
  "threatLevel": "CLEAN",
  "findings": [
    "Suspicious API: exec",
    "Found 4 URL(s)"
  ],
  "details": {
    "binary": { ... },
    "patterns": { ... },
    "packing": { ... }
  }
}
```

## Architecture

```
lib/
├── entropy.js    # Shannon entropy calculation
│                 # - calculateEntropy(buffer) → 0-8
│                 # - detectPacking(buffer) → {isPacked, entropy, regions}
│
├── macho.js      # Mach-O parser (macOS)
│                 # - parseMachO(buffer) → {segments, dylibs, flags, ...}
│                 # - Handles FAT/Universal binaries
│                 # - Code signature detection
│
├── elf.js        # ELF parser (Linux)
│                 # - parseELF(buffer) → {sections, libs, flags, ...}
│                 # - Security feature detection (PIE, NX, RELRO)
│
├── patterns.js   # Pattern detection
│                 # - scanPatterns(buffer) → {shellcode, apis, urls, ...}
│                 # - Shellcode byte sequences
│                 # - API string references
│
└── scanner.js    # Main orchestrator
                  # - scanFile(path) → result
                  # - scanDirectory(path) → results[]
                  # - Threat scoring and formatting
```

## Limitations

1. **Not a replacement for antivirus/EDR** - This is lightweight static analysis, not a full security product.

2. **No signature database** - Does not check file hashes against known malware databases. Could integrate VirusTotal API in the future.

3. **Static analysis only** - Cannot detect runtime-only malicious behavior. No sandboxing or dynamic analysis.

4. **False positives** - Security tools, debuggers, and legitimate system utilities may trigger findings.

5. **Obfuscation** - Sophisticated obfuscation or custom packers may evade detection.

## Future Enhancements

- [ ] VirusTotal API integration for hash lookups
- [ ] Local blocklist of known-bad hashes
- [ ] npm package audit integration
- [ ] Homebrew formula verification
- [ ] OpenClaw core integration (pre-load hooks)
- [ ] ClawHub server-side scanning

## Credits

Detection logic ported from [Harkonnen](https://github.com/dev-null321/Harkonnen) antimalware engine by dev-null321.

## License

MIT
