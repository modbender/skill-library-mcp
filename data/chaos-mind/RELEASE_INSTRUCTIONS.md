# CHAOS Memory - Release Instructions

## GitHub Release Checklist

### 1. Create Release on GitHub
1. Go to https://github.com/hargabyte/Chaos-mind
2. Click "Releases" → "Create a new release"
3. Tag: `v1.0.0`
4. Title: `CHAOS Memory v1.0.0 - Initial Release`
5. Description:
```markdown
# CHAOS Memory v1.0.0

Hybrid search memory system for AI agents with auto-capture.

## Features
- 🔍 Hybrid search (BM25 + Vector + Graph + Heat)
- 🤖 Auto-capture from session transcripts
- 📊 Progressive disclosure (index/summary/full modes)
- ⚡ 43x faster extraction with Qwen3-1.7B

## Installation
```bash
curl -fsSL https://raw.githubusercontent.com/hargabyte/Chaos-mind/main/install.sh | bash
```

## What's Included
- Pre-built binaries for Linux, macOS (Intel + ARM)
- Systemd service support
- Configuration templates
- Auto-capture with flexible categories

## Requirements
- Dolt 0.50.0+
- Ollama (for auto-capture)
- 16GB RAM recommended

## Fixed in This Release
- ✅ Database port defaults to 3307 (avoids conflicts)
- ✅ Flexible category schema (VARCHAR, not enum)
- ✅ Systemd service with auto-restart
- ✅ Comprehensive documentation

## Documentation
- [Installation Guide](https://github.com/hargabyte/Chaos-mind/blob/main/INSTALL_NOTES.md)
- [Deployment Checklist](https://github.com/hargabyte/Chaos-mind/blob/main/DEPLOYMENT_CHECKLIST.md)
- [README](https://github.com/hargabyte/Chaos-mind/blob/main/README.md)
```

### 2. Upload Binaries

**From Z:\chaos-memory\skill\binaries\**, upload:

#### Required Files:
- `chaos-memory-linux-amd64.tar.gz` (Linux x86_64)
- `chaos-memory-darwin-amd64.tar.gz` (macOS Intel)
- `chaos-memory-darwin-arm64.tar.gz` (macOS M1/M2)

Each tar.gz should contain:
```
bin/
├── chaos-mcp
└── chaos-consolidator
```

#### Binary Naming Convention:
```bash
# Linux
chaos-memory-linux-amd64.tar.gz

# macOS Intel
chaos-memory-darwin-amd64.tar.gz

# macOS ARM
chaos-memory-darwin-arm64.tar.gz
```

### 3. Verify Install Script Compatibility

The install.sh detects platform and downloads the correct binary:
```bash
# Linux → chaos-memory-linux-amd64.tar.gz
# macOS Intel → chaos-memory-darwin-amd64.tar.gz
# macOS ARM → chaos-memory-darwin-arm64.tar.gz
```

Make sure binary names match this pattern.

### 4. Test Installation

After creating the release:

```bash
# Test fresh install
rm -rf ~/.chaos
curl -fsSL https://raw.githubusercontent.com/hargabyte/Chaos-mind/main/install.sh | bash

# Expected output:
# ✓ Dolt installed
# ✓ Binaries downloaded
# ✓ CLI tools installed
# ✓ Database initialized
# ✓ Config created
```

### 5. Update ClawHub

If publishing to ClawHub:
1. Update `clawdhub.yaml` with release URL
2. Submit to ClawHub registry
3. Test `clawdhub install chaos-memory`

---

## Binary Packaging

### From Windows (Z:\chaos-memory\skill\binaries\)

```powershell
# Create Linux package
tar -czf chaos-memory-linux-amd64.tar.gz -C linux .

# Create macOS Intel package
tar -czf chaos-memory-darwin-amd64.tar.gz -C macos .

# Create macOS ARM package
tar -czf chaos-memory-darwin-arm64.tar.gz -C macos-arm64 .
```

### Expected Structure in Each Archive:
```
bin/
├── chaos-mcp
└── chaos-consolidator
```

---

## Platform Detection Logic

Install script maps platforms like this:

| OS | Arch | Download Filename |
|----|------|-------------------|
| Linux | x86_64 | chaos-memory-linux-amd64.tar.gz |
| macOS | x86_64 | chaos-memory-darwin-amd64.tar.gz |
| macOS | arm64 | chaos-memory-darwin-arm64.tar.gz |

The `detect_platform()` function in install.sh handles this automatically.

---

## Post-Release

### Verify
- [ ] All binaries uploaded
- [ ] Release is public
- [ ] install.sh downloads correctly
- [ ] Database initializes on port 3307
- [ ] No enum errors in logs
- [ ] Systemd service installs

### Announce
- [ ] Update README with release notes
- [ ] Post to ClawHub (if applicable)
- [ ] Update CHANGELOG.md

---

## Troubleshooting

**Binary download fails:**
- Check release tag is exactly `v1.0.0`
- Verify binary names match expected pattern
- Ensure release is public

**Wrong binary downloaded:**
- Check platform detection with `uname -s` and `uname -m`
- Verify detect_platform() function logic

**Permission denied:**
- Binaries need execute permission in tar.gz
- Script does `chmod +x` after extraction
