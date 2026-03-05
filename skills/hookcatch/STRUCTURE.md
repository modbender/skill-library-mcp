# OpenClaw Skill Structure Explanation

## Directory Structure

```
skills/hookcatch/
├── bin/
│   └── hookcatch-skill          # AI-optimized wrapper (optional)
├── SKILL.md                     # OpenClaw skill definition (REQUIRED)
├── README.md                    # Installation & usage guide (REQUIRED)
├── package.json                 # NPM package config (for wrapper)
├── test.sh                      # Test script
└── .gitignore                   # Git ignore file
```

## Two Ways to Use the Skill

### 1. Direct CLI Usage (Simple)
OpenClaw agents call the `hookcatch` CLI directly:
```bash
hookcatch bin create --name "Test"
hookcatch bin list --format json
hookcatch tunnel 3000
```

**Pros:**
- No additional wrapper needed
- Direct access to all CLI features
- Simpler installation

**Cons:**
- Output might not be optimally formatted for AI parsing
- Environment variable mismatch (`HOOKCATCH_API_KEY` vs `HOOKCATCH_TOKEN`)
- Less structured error messages

### 2. Skill Wrapper (Enhanced)
OpenClaw agents use `hookcatch-skill` wrapper:
```bash
hookcatch-skill bin create --name "Test"
hookcatch-skill bin list
hookcatch-skill tunnel 3000
```

**Pros:**
- Automatically formats output as JSON
- Maps `HOOKCATCH_API_KEY` → `HOOKCATCH_TOKEN`
- Structured error messages for AI
- Better authentication validation
- Provides help text in JSON format

**Cons:**
- Requires additional NPM package
- Extra layer of indirection

## What Each File Does

### `SKILL.md` (REQUIRED)
The official skill definition that OpenClaw reads. Contains:
- Frontmatter with metadata (name, description, requirements)
- AgentSkills-compatible format
- Installation instructions
- Command documentation
- Usage examples

**AgentSkills Metadata:**
```yaml
metadata: {
  "openclaw": {
    "emoji": "🪝",
    "requires": {
      "bins": ["hookcatch"],
      "env": ["HOOKCATCH_API_KEY"]
    },
    "primaryEnv": "HOOKCATCH_API_KEY",
    "homepage": "https://hookcatch.dev",
    "install": [{
      "id": "npm",
      "kind": "node",
      "packages": ["hookcatch"],
      "bins": ["hookcatch"],
      "label": "Install HookCatch CLI (npm)"
    }]
  }
}
```

### `README.md` (REQUIRED)
Human-readable documentation:
- Installation instructions
- Setup steps
- Usage examples
- Troubleshooting
- Links to main docs

### `bin/hookcatch-skill` (OPTIONAL)
Node.js wrapper script that:
1. Checks for `HOOKCATCH_API_KEY` environment variable
2. Maps it to `HOOKCATCH_TOKEN` for the CLI
3. Forces `--format json` for bin commands
4. Provides structured error messages
5. Shows help as JSON when no args provided

### `package.json` (OPTIONAL)
NPM package definition for the wrapper:
- Defines `@hookcatch/openclaw-skill` package
- Declares `hookcatch-skill` bin
- Sets peer dependency on `hookcatch` CLI
- Enables separate installation

### `test.sh` (OPTIONAL)
Bash script to test the skill:
- Checks CLI installation
- Checks wrapper installation
- Validates authentication
- Tests basic commands
- Provides helpful error messages

## Installation Flow

### Via ClawHub (Recommended)
```bash
clawhub install hookcatch
```
This installs:
1. The skill definition (SKILL.md)
2. The hookcatch CLI (via npm)
3. Sets up environment variables

### Manual Installation
```bash
# Install CLI
npm install -g hookcatch

# Optional: Install wrapper
npm install -g @hookcatch/openclaw-skill

# Copy skill to OpenClaw
cp -r skills/hookcatch ~/.openclaw/skills/

# Authenticate
hookcatch token generate
export HOOKCATCH_API_KEY="hc_live_..."
```

## Why the Wrapper is Optional

The wrapper (`bin/hookcatch-skill`) is **optional** because:

1. **The CLI is already AI-friendly**: It supports `--format json` and provides structured output
2. **OpenClaw can call binaries directly**: No wrapper needed for basic usage
3. **Flexibility**: Users can choose direct CLI or enhanced wrapper
4. **Separation of concerns**: CLI can be used independently of OpenClaw

## Best Practice

**For OpenClaw Submission:**
- Include `bin/hookcatch-skill` wrapper ✅
- It provides better AI agent experience
- Helps with authentication mapping
- Provides consistent JSON output

**For Users:**
- Let them choose: direct CLI or wrapper
- Document both approaches
- Wrapper is recommended for automation

## Comparison with Other Skills

### Minimal Skill (Direct CLI)
```
skills/mytool/
├── SKILL.md
└── README.md
```
Relies entirely on existing CLI

### Enhanced Skill (With Wrapper)
```
skills/mytool/
├── bin/
│   └── mytool-skill
├── SKILL.md
├── README.md
└── package.json
```
Adds AI-optimized wrapper for better experience

### Full Skill (With Code)
```
skills/mytool/
├── src/
│   └── index.js
├── bin/
│   └── mytool-skill
├── SKILL.md
├── README.md
└── package.json
```
Implements full logic in skill (rare)

## Recommendation

**Current Structure (Enhanced Skill) ✅**

Your HookCatch skill follows the **enhanced skill** pattern:
- Core functionality in separate CLI (`hookcatch`)
- Optional wrapper for better AI experience (`hookcatch-skill`)
- Well documented (SKILL.md + README.md)
- Testable (test.sh)

This is the **best practice** for skills that wrap existing tools!

## Summary

**Do you need bin/hookcatch-skill?**
- **No, not required** - OpenClaw can use `hookcatch` CLI directly
- **Yes, recommended** - Provides better AI agent experience
- **Your choice** - Document both approaches

**Current status:** ✅ Complete with optional wrapper for enhanced experience
