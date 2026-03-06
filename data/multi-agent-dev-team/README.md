# Multi-Agent Dev Team

**Build software with AI agents that collaborate like a real dev team**

[![ClawHub](https://img.shields.io/badge/ClawHub-Install-blue)](https://clawhub.com/skills/multi-agent-dev-team)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-2026.2%2B-purple)](https://openclaw.ai)

## Overview

Multi-Agent Dev Team is an OpenClaw skill that provides two collaborative AI agents:
- **PM Agent**: Orchestrates projects, breaks down requirements, coordinates the Dev agent
- **Dev Agent**: Implements code, tests functionality, commits to Git

Together, they can build complete software projects from simple descriptions.

## Quick Start

### Installation

```bash
npx clawhub install multi-agent-dev-team
```

### Configuration

Add to `~/.openclaw/config.yaml`:

```yaml
agents:
  multi-agent-pm:
    soul: ~/.openclaw/skills/multi-agent-dev-team/agents/pm-agent/SOUL.md
    model: anthropic/claude-sonnet-4-5-20250929
    
  multi-agent-dev:
    soul: ~/.openclaw/skills/multi-agent-dev-team/agents/dev-agent/SOUL.md
    model: google/gemini-2.5-flash
```

### Usage

```bash
openclaw chat --agent multi-agent-pm
```

Then simply describe what you want to build!

## Features

### ✨ Free Version (This Skill)
- 🤝 **2 collaborative agents** (PM + Dev)
- 🏗️ **Project orchestration** by PM agent
- 💻 **Code implementation** by Dev agent
- 📝 **Git integration** with clean commits
- 🎯 **Iterative refinement** (up to 3 rounds)
- 📚 **Templates & examples** included

### 🚀 Pro Version ($49)
- 👥 **6 specialized agents**: PM, Architect, Dev, QA, DevOps, BizDev
- 🔄 **Lobster pipelines**: Automated workflows with approval gates
- 🏛️ **Architecture design**: Dedicated system design agent
- ✅ **Automated QA**: Code review & testing agent
- 🚀 **DevOps automation**: CI/CD & deployment
- 💼 **Business strategy**: Market research & planning
- 📖 **Comprehensive guides**: English + Korean docs

[**Upgrade to Pro →**](https://ubik-collective.lemonsqueezy.com)

## What Can You Build?

### Perfect For:
- ✅ Landing pages and marketing sites
- ✅ React/Next.js applications
- ✅ Component libraries
- ✅ Prototypes and MVPs
- ✅ Developer tools
- ✅ Documentation sites

### Example Projects:
- **SaaS Landing Page**: Hero, features, pricing, contact ([See example](examples/landing-page-example.md))
- **GitHub Profile Viewer**: API integration, search, responsive cards
- **Button Component Library**: TypeScript, variants, Storybook docs
- **Task Management App**: CRUD operations, state management
- **Portfolio Website**: Multi-page, dynamic content

## How It Works

```
You (Director)
    ↓
    ↓ Describe project
    ↓
PM Agent
    ↓ Create task spec
    ↓ Spawn Dev agent
    ↓
Dev Agent
    ↓ Implement code
    ↓ Test & commit
    ↓
PM Agent
    ↓ Review deliverables
    ↓ Report completion
    ↓
You receive working code! ✨
```

## Real Example

**Input:**
```
Build a Next.js landing page with hero, features, and contact sections.
Use TypeScript and Tailwind CSS.
```

**Output (25 minutes later):**
- ✅ Complete Next.js 14 project
- ✅ TypeScript + Tailwind CSS
- ✅ Responsive design
- ✅ Git repository initialized
- ✅ Production-ready code

**Live Demo:** https://my-landing-page-blush-rho.vercel.app

## Documentation

- 📖 [SKILL.md](SKILL.md) - Complete usage guide
- 📋 [Project Spec Template](templates/project-spec-template.md) - How to write good requests
- 💡 [Landing Page Example](examples/landing-page-example.md) - Real project walkthrough
- 🧠 [PM Agent SOUL](agents/pm-agent/SOUL.md) - PM agent capabilities
- 💻 [Dev Agent SOUL](agents/dev-agent/SOUL.md) - Dev agent capabilities

## Requirements

- OpenClaw 2026.2.0 or later
- At least one LLM provider configured (Anthropic/Google/OpenAI)
- Git installed (for Dev agent)
- Node.js 18+ (for web projects)

## Recommended Models

**PM Agent:**
- `anthropic/claude-sonnet-4-5-20250929` (best reasoning)
- `google/gemini-2.5-flash` (fast & efficient)

**Dev Agent:**
- `google/gemini-2.5-flash` (recommended - fast code generation)
- `anthropic/claude-sonnet-4-5` (higher quality)
- `openai/gpt-4o-mini` (budget-friendly)

## Support

- 📖 **Docs**: https://docs.openclaw.ai
- 💬 **Discord**: https://discord.com/invite/clawd
- 🐛 **Issues**: https://github.com/openclaw/openclaw
- 📧 **Email**: support@ubik.systems

## Pro Upgrade

Want the full development team experience?

### Multi-Agent Dev Team Pro includes:

**Additional Agents:**
- 🏛️ **Architect**: System design & technical planning
- ✅ **QA**: Automated testing & code review
- 🚀 **DevOps**: CI/CD & deployment automation
- 💼 **BizDev**: Market research & business strategy

**Advanced Features:**
- 🔄 **Lobster Pipelines**: Automated workflows with human approval gates
- 📊 **Quality Gates**: Automated checks before deployment
- 🌍 **Multi-language Guides**: English + Korean documentation
- 🎓 **Training Materials**: Video tutorials & best practices

**Priority Support:**
- 💬 Direct Discord channel
- 📧 Email support
- 🎯 Custom workflow consultation

[**Get Pro for $49 →**](https://ubik-collective.lemonsqueezy.com)

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Credits

**Built by:** [UBIK Collective](https://ubik.systems)

**Powered by:** [OpenClaw](https://openclaw.ai)

**Contributors:**
- PM 팀장 (Project orchestration)
- Dev agents (Code implementation)
- QA agents (Testing & review)

---

**Ready to build with AI agents?**

```bash
npx clawhub install multi-agent-dev-team
openclaw chat --agent multi-agent-pm
```

Then describe your project and watch the magic happen! ✨
