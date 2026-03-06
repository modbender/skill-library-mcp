# BoltzPay OpenClaw Skill

This directory contains the OpenClaw skill definition for BoltzPay. The `SKILL.md` file defines the skill metadata, commands, and usage instructions for the [ClawHub](https://clawhub.ai) skill marketplace.

## What is OpenClaw?

[OpenClaw](https://github.com/openclaw/openclaw) is an open-source framework for AI agent skills. Skills are defined as Markdown files with YAML frontmatter and published to ClawHub for discovery by AI agents.

## Files

- `SKILL.md` — The skill definition file. Contains YAML frontmatter with metadata and Markdown body with commands, setup, and examples.

## Publishing to ClawHub

Publishing is deferred to **Phase 7** (Launch). When ready:

1. **Install the OpenClaw CLI:**

   ```bash
   npm install -g openclaw
   ```

2. **Authenticate with ClawHub:**

   ```bash
   clawhub login
   ```

3. **Publish the skill** from this directory:

   ```bash
   cd integrations/openclaw
   clawhub publish
   ```

4. **Verify** the skill appears on ClawHub:

   ```bash
   clawhub search boltzpay
   ```

## Testing Locally

Verify the SKILL.md frontmatter is valid YAML:

```bash
# Check frontmatter can be parsed
python3 -c "
import yaml
with open('SKILL.md') as f:
    content = f.read()
    # Extract frontmatter between --- markers
    parts = content.split('---', 2)
    meta = yaml.safe_load(parts[1])
    print(f'Name: {meta[\"name\"]}')
    print(f'Description: {meta[\"description\"]}')
    print(f'Metadata: {meta[\"metadata\"]}')
"
```

Expected output:

```
Name: boltzpay
Description: Pay for API data automatically — multi-protocol (x402 + L402), multi-chain
Metadata: {"openclaw": {"emoji": "...", ...}}
```

## Notes

- The `metadata` field in SKILL.md MUST be a single-line JSON string (OpenClaw parser limitation)
- The skill requires `npx` as a binary dependency (declared in metadata)
- Publishing deferred to Phase 7. This file is ready for publish.
