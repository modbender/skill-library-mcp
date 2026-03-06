# Skill Development Guidelines

All prerequisites and rules to follow when developing skills for OpenClaw.

---

## Core Principles

When developing skills, ALWAYS follow these rules:

| # | Principle | Description |
|---|-----------|-------------|
| 1 | 可用性 & 鲁棒性 | Ensure program works reliably, handle edge cases |
| 2 | 优化交互体验 | Optimize user experience, keep commands simple |
| 3 | 错误回退 | Provide fallback when user misconfigures |
| 4 | 一次搞定 | One-input solutions, never make user type twice |
| 5 | 记住这个 | When user says "记住这个", write it in markdown |

---

## Configuration Rules

- **Never change openclaw.json without explicit user permission**
- Always show planned changes to user for review BEFORE applying
- User preference: **NO emoji** in any output
- All formal documentation for projects must be in English only

---

## API Key Configuration

- Third-party API proxies need correct baseUrl paths
- Example: `https://letaicode.cn/claude/v1` (not just `/claude`)
- Always test API keys with curl before configuring
- Store sensitive info in environment variables, not in code

---

## Execution Attitude

- When user requests something, execute it unless it causes actual harm
- Don't question or second-guess user requests based on "meaningfulness"
- Trust the user's judgment over own assumptions

---

## Output Preferences

- **No emoji** in any output (user preference)
- Discord/WhatsApp: No markdown tables, use bullet lists
- Discord links: Wrap in `<>` to suppress embeds

---

## Project Structure

A proper skill should include:

```
skill-name/
├── SKILL.md         # Documentation for OpenClaw
├── README.md        # User-facing documentation
├── main            # Main executable (Node.js/Python/Bash)
├── config.json     # Configuration template
└── .gitignore     # Ignore config.json, tokens, secrets
```

---

## Best Practices

### One-Command Setup
- Users should configure with a single command
- Auto-save configuration to config.json
- Test connection during setup

### Smart Error Handling
- Show helpful error messages
- Suggest fixes when possible
- Provide fallback options for misconfiguration

### Natural Language Support
- Support multiple command patterns
- Fuzzy matching for entity names
- List available options when not found

---

## Reference

- OpenClaw docs: `/home/crix/.npm-global/lib/node_modules/openclaw/docs`
- Skill hub: https://clawhub.com
