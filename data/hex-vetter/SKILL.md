---
name: hex-vetter
version: 1.0.0
description: Physical-layer hex auditing for skills. Detects hidden binary data, control characters, and encoding-based attacks.
author: Matrix-Meta
tags:
  - security
  - hex
  - audit
  - binary-analysis
---

# hex-vetter 🔬

Physical-layer hex auditing skill forects hidden binary data AI agents. Det, control characters, and encoding-based attacks.

## Overview

hex-vetter performs deep hex-level analysis of files to detect what text-based reviewers miss. It's designed for security audits of skill packages, detecting hidden payloads, obfuscated code, and suspicious binary data.

## Installation

```bash
git clone https://github.com/Matrix-Meta/hex-vetter.git
cd hex-vetter
npm install
```

## Usage

### Command Line

```bash
# Scan a single file
node vet.js <file_path>

# Scan a directory recursively
node scan_all.js <directory_path>

# Verify file integrity
node verify.js <file_path>
```

### As a Module

```javascript
const { scanFile } = require('./vet.js');
const result = await scanFile('/path/to/file.bin');

console.log(result.riskLevel);    // 'LOW', 'MEDIUM', 'HIGH'
console.log(result.flags);       // Array of detected issues
console.log(result.hexDump);      // Formatted hex output
```

## What It Detects

| Flag | Description |
|------|-------------|
| `NULL_BYTES` | Null bytes (0x00) - signs of binary injection or file padding |
| `CONTROL_CHARS` | Control characters (0x01-0x1F) - hidden terminal sequences |
| `UNICODE_OVERRIDE` | Unicode directional overrides (LRO, RLO, etc.) |
| `HIGH_NON_ASCII` | High ratio of non-ASCII bytes - Base64 or encoded payloads |
| `MAGIC_BYTES` | Known magic bytes/signatures |
| `SUSPICIOUS_PATTERN` | Pattern matching for common attack signatures |

## API Reference

### scanFile(filePath)

Scans a single file and returns analysis results.

```javascript
const { scanFile } = require('./vet.js');

const result = await scanFile('./some file.js');
// Returns: { riskLevel, flags, hexDump, details }
```

### scanDirectory(dirPath)

Recursively scans all files in a directory.

```javascript
const { scanDirectory } = require('./scan_all.js');

const results = await scanDirectory('./skills/');
// Returns: Array of scan results for each file
```

### verifyIntegrity(filePath)

Verifies file integrity using stored checksums.

```javascript
const { verifyIntegrity } = require('./verify.js');

const result = await verifyIntegrity('./starfragment.js');
// Returns: { valid, expected, actual }
```

## Risk Levels

- **🟢 LOW**: Normal file, no suspicious content detected
- **🟡 MEDIUM**: Some flags detected, manual review recommended
- **🔴 HIGH**: Significant suspicious content, MUST be manually reviewed

## Security Policy

1. **Mandatory Review**: Any file flagged as 🔴 **HIGH RISK** MUST be manually inspected by a human or a trusted agent before the skill is used.

2. **False Positives**: Risk ratings are heuristic. Common false positives include:
   - `.env` mentions in `.npmignore`
   - Documentation with encoded examples
   - Compressed assets

3. **Agent Action**: If an agent performs an audit and finds HIGH RISK, it MUST:
   - Notify the user immediately
   - Provide the specific reason (e.g., signature match vs. binary data)
   - Suggest next steps for manual review

## Architecture

```
hex-vetter/
├── starfragment.js       # Core module (self-modifying storage)
├── scan_all.js          # Recursive directory scanner
├── verify.js            # Integrity verification
├── vet.js               # Main entry point
├── README.md
└── SKILL.md            # This file
```

## Self-Modifying Storage

The `starfragment.js` module uses self-modifying storage - it reads and writes data from/to its own file at runtime. Constants are encoded and stored as valid JavaScript comments at the end of the source file.

## Contributing

Issues and pull requests are welcome on GitHub:
https://github.com/Matrix-Meta/hex-vetter
