# 1Claw Skill for ClawHub

**Version:** 1.0.8 · [View on ClawHub](https://clawhub.ai/kmjones1979/1claw)

An [OpenClaw](https://docs.openclaw.ai) skill that gives AI agents secure, HSM-backed secret management via [1Claw](https://1claw.xyz).

## What it does

Teaches agents to store, retrieve, rotate, and share secrets using the 1Claw vault. Secrets are encrypted with hardware security modules and fetched just-in-time — they never persist in conversation context.

## Files

| File          | Purpose                                                     |
| ------------- | ----------------------------------------------------------- |
| `SKILL.md`    | Primary skill description, setup, tools, and best practices |
| `EXAMPLES.md` | Example agent conversations demonstrating each tool         |
| `CONFIG.md`   | Environment variables, credential setup, and secret types   |

## Install via ClawHub CLI

```bash
clawhub install 1claw
```

## Testing / validation

To confirm the skill is valid for OpenClaw bots and ClawHub (required files, frontmatter, tool names):

```bash
./scripts/validate.sh
```

Run from the `skill` directory or from the repo root.

## Links

- [1Claw Dashboard](https://1claw.xyz)
- [Documentation](https://docs.1claw.xyz)
- [SDK](https://github.com/1clawAI/1claw-sdk)
- [MCP Server](https://www.npmjs.com/package/@1claw/mcp)
