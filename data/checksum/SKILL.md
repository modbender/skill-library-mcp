---
name: checksum
description: A CLI utility for generating and verifying cryptographic file checksums (MD5, SHA1, SHA256). Supports recursive directory hashing and verification from file.
---

# Checksum Utility

A dedicated CLI tool for ensuring file integrity. Use this skill to verify downloads, check for changes in files, or generate checksums for release artifacts.

## Features

- **Multi-Algorithm:** Supports `md5` (default), `sha1`, `sha256`, `sha512`.
- **Recursive Hashing:** Generates checksums for entire directories.
- **Verification:** (Planned) Validate files against a checksum list.
- **JSON Output:** Machine-readable output for integration scripts.

## Usage

### Calculate File Checksum

```bash
node skills/checksum/index.js --file <path> [--algo <md5|sha1|sha256>]
```

Example:
```bash
node skills/checksum/index.js --file package.json --algo sha256
# Output: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  package.json
```

### Recursive Directory Checksum

```bash
node skills/checksum/index.js --dir <path> [--algo <md5|sha1|sha256>] [--json]
```

Example:
```bash
node skills/checksum/index.js --dir src/ --algo sha1 --json > checksums.json
```

## Why use this instead of `md5sum`?

- **Cross-Platform:** Works on any OS with Node.js (Linux, macOS, Windows).
- **No System Deps:** Doesn't rely on `coreutils` being installed.
- **JSON Support:** Easy to parse in other scripts.
