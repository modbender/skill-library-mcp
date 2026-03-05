# JustPayAI — Skill Directory Submissions

Track where JustPayAI's skill file has been submitted for AI agent discoverability.

## Submitted

| Directory | Status | Date | Link |
|-----------|--------|------|------|
| ClawHub (OpenClaw) | Pending login | 2026-02-10 | https://clawhub.ai |

## To Submit

### 1. ClawHub (OpenClaw Registry)
- **URL:** https://clawhub.ai
- **Format:** SKILL.md with YAML frontmatter (name, description, metadata)
- **CLI:** `clawdhub publish ./OpenClawFolder --slug justpayai --name "JustPayAI" --version 1.0.0 --changelog "Initial release" --tags "latest,payments,marketplace,solana,ai-agents"`
- **Requirements:** GitHub account (1+ week old), `npm install -g clawdhub`, `clawdhub login`
- **Status:** SKILL.md ready, need to login and publish

### 2. skills.sh (Agent Skills Directory)
- **URL:** https://skills.sh
- **Format:** Submit a URL to your hosted skill.md file
- **Submit URL:** https://justpayai.dev/skill.md
- **Notes:** Community-curated directory. Submit via their web form or GitHub PR.

### 3. Awesome OpenClaw Skills (GitHub)
- **URL:** https://github.com/nichochar/awesome-openclaw-skills
- **Format:** GitHub PR adding your skill to the README list
- **PR content:** Add JustPayAI entry under "Payments" or "Marketplace" category
- **Entry:** `- [JustPayAI](https://clawhub.ai/skills/justpayai) — AI agent marketplace & payments on Solana`

### 4. Toolhouse AI Agent Directory
- **URL:** https://app.toolhouse.ai
- **Format:** Register as a tool provider, submit API schema
- **Notes:** Focuses on tool integrations for LLM agents

### 5. AgentOps Registry
- **URL:** https://agentops.ai
- **Format:** SDK integration + directory listing
- **Notes:** Agent observability platform with a growing registry

### 6. LangChain Hub / LangSmith
- **URL:** https://smith.langchain.com
- **Format:** Publish as a LangChain tool/toolkit
- **Notes:** Huge LLM developer community. Would require a LangChain wrapper package.

### 7. CrewAI Tools Registry
- **URL:** https://docs.crewai.com
- **Format:** CrewAI tool class wrapping JustPayAI API
- **Notes:** Popular multi-agent framework. Publish a `crewai-tools-justpayai` package.

### 8. Direct Hosting (Already Live)
- **Skill file:** https://justpayai.dev/skill.md
- **API docs:** https://justpayai.dev/docs
- **Website:** https://justpayai.dev
- **API health:** https://api.justpayai.dev/health

---

## Publishing Workflow

1. **Login:** `clawdhub login` (opens browser for GitHub OAuth)
2. **Publish:** `clawdhub publish ./OpenClawFolder --slug justpayai --name "JustPayAI" --version 1.0.0 --changelog "Initial release — AI agent marketplace with jobs, campaigns, escrow, and USDC payments on Solana" --tags "latest,payments,marketplace,solana,ai-agents"`
3. **Verify:** `clawdhub search justpayai`
4. **Update later:** Bump version and re-publish: `clawdhub publish ./OpenClawFolder --slug justpayai --version 1.1.0 --changelog "Added campaigns system"`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-10 | Initial release — auth, services, jobs, campaigns, wallet, reports, proposals |
