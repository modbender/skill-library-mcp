# Installing Agent Guardrails for Claude Code

## Quick Install

```bash
# Clone the skill
git clone https://github.com/jzOcb/agent-guardrails

# Install in your project
cd your-project/
bash /path/to/agent-guardrails/scripts/install.sh .
```

## What Gets Installed

✅ **Git Hooks** - Automatic enforcement on every commit
✅ **Validation Scripts** - Pre/post creation checks
✅ **Secret Detection** - Prevent credential leaks
✅ **Deployment Verification** - Ensure production integration

## Usage with Claude Code

### 1. Prevent Reimplementation

Before creating new code:
```bash
bash scripts/pre-create-check.sh .
```

Claude will see existing modules and import them instead of rewriting.

### 2. Validate Changes

After editing code:
```bash
bash scripts/post-create-validate.sh path/to/file.py
```

Catches duplicates, missing imports, bypass patterns.

### 3. Check Secrets

Before committing:
```bash
bash scripts/check-secrets.sh
```

Blocks hardcoded API keys, tokens, passwords.

### 4. Verify Deployment

When feature is "done":
```bash
bash .deployment-check.sh
```

Ensures code is actually wired to production (not just written).

## Automatic Mode

After installation, git hooks run automatically:
- Every commit → checks secrets, bypass patterns
- Can't commit without passing checks

## Customization

Edit `.git/hooks/pre-commit` to adjust patterns:
```bash
# Add your own bypass patterns
# Add your own secret patterns
# Customize for your project
```

## For Claude Code Agents

When using Claude Code CLI with this skill:

**Prompt enhancement:**
```
Before creating new code, run pre-create-check to see existing modules.
After editing, run post-create-validate to ensure quality.
Before marking "done", run .deployment-check to verify integration.
```

This ensures Claude Code agents respect your enforcement rules.

## Troubleshooting

**Hook not running?**
```bash
chmod +x .git/hooks/pre-commit
```

**Want to skip once?**
```bash
git commit --no-verify -m "message"
```

**Need to update patterns?**
Edit `scripts/post-create-validate.sh` and `.git/hooks/pre-commit`

## Learn More

- [Full Documentation](./README.md)
- [Deployment Guide](./references/deployment-verification-guide.md)
- [Skill Update Loop](./references/skill-update-feedback.md)
