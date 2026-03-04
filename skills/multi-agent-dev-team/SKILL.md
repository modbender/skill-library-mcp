---
name: Multi-Agent Dev Team
description: 2-agent collaborative software development workflow for OpenClaw
homepage: https://ubik.systems
metadata: {"clawdbot":{"emoji":"🤝","requires":{"agents":["multi-agent-pm","multi-agent-dev"]}}}
---

# Multi-Agent Dev Team

**2-agent collaborative software development workflow for OpenClaw**

Build complete software projects using AI agents that work together like a real development team.

## What is this?

The Multi-Agent Dev Team skill provides a **PM (Project Manager)** and **Dev (Developer)** agent that collaborate to build software projects. You describe what you want, the PM breaks it down into tasks, and the Dev agent implements them.

**Perfect for:**
- Landing pages and websites
- Small web applications
- Prototypes and MVPs
- Code generation projects
- Learning multi-agent workflows

## Quick Start

### 1. Install the skill

```bash
npx clawhub install multi-agent-dev-team
```

### 2. Set up agents

The skill includes two pre-configured agents:

**PM Agent** (`multi-agent-pm`)
- Handles project planning
- Coordinates the Dev agent
- Reports progress to you

**Dev Agent** (`multi-agent-dev`)
- Implements code
- Tests functionality
- Commits to Git

### 3. Configure in `~/.openclaw/config.yaml`

```yaml
agents:
  multi-agent-pm:
    soul: ~/.openclaw/skills/multi-agent-dev-team/agents/pm-agent/SOUL.md
    model: anthropic/claude-sonnet-4-5-20250929  # or your preferred model
    
  multi-agent-dev:
    soul: ~/.openclaw/skills/multi-agent-dev-team/agents/dev-agent/SOUL.md
    model: google/gemini-2.5-flash  # faster for code generation
```

### 4. Start your PM agent

```bash
openclaw chat --agent multi-agent-pm
```

## Usage Example

### Building a Landing Page

**You (Director):**
> Build me a Next.js landing page with hero section, features, and contact form. Use Tailwind CSS and TypeScript.

**PM Agent:**
> I'll break this down into a clear task for the Dev agent. Starting now...
> 
> *[Spawns Dev agent with detailed spec]*
> 
> Dev agent is working on the project. I'll monitor progress and report back when complete.

**PM Agent (later):**
> ✅ Landing page completed!
> 
> **Deliverables:**
> - Next.js 14+ App Router project
> - Hero, Features, Contact sections
> - Fully responsive design
> - TypeScript + Tailwind CSS
> - Git repository initialized
> 
> **Location:** `~/projects/my-landing-page/`
> 
> Ready for deployment. Would you like me to deploy to Vercel?

## How It Works

### Architecture

```
You (Director)
    ↓
PM Agent (Orchestrator)
    ↓
Dev Agent (Implementer)
    ↓
Working Code
```

### Workflow

1. **You** describe your project to the **PM agent**
2. **PM** creates a structured task specification
3. **PM** spawns **Dev agent** with the spec
4. **Dev** implements the code
5. **PM** reviews the deliverables
6. **PM** reports completion (or requests revisions)
7. Repeat steps 4-6 if needed (max 3 iterations)

### Task Specification Format

The PM agent uses this template to communicate with Dev:

```markdown
## Project: [NAME]
## Task: [ACTION]

## Requirements:
1. [Requirement 1]
2. [Requirement 2]

## Technical Constraints:
- [Constraint 1]
- [Constraint 2]

## Acceptance Criteria:
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Deliverables:
- [Deliverable 1]
- [Deliverable 2]
```

## Supported Project Types

### ✅ Works Great
- **Next.js** landing pages & apps
- **React** components & SPAs
- **Node.js** scripts & APIs
- **TypeScript** projects
- **Static sites** (HTML/CSS/JS)
- **Documentation** sites

### ⚠️ Limited Support
- Complex backend systems (use Pro version)
- Real-time applications
- Multi-service architectures
- Mobile apps

### ❌ Not Recommended
- Large enterprise systems
- Mission-critical production code without human review
- Projects requiring specialized agents (use Pro version)

## Configuration Options

### Agent Models

**PM Agent** (orchestration):
- `anthropic/claude-sonnet-4-5` - Best reasoning
- `google/gemini-2.5-flash` - Fast & efficient
- `openai/gpt-4o` - Balanced

**Dev Agent** (code generation):
- `google/gemini-2.5-flash` - Fast iteration (recommended)
- `anthropic/claude-sonnet-4-5` - Higher quality
- `openai/gpt-4o-mini` - Budget-friendly

### Workspace Configuration

Set a dedicated workspace for projects:

```yaml
agents:
  multi-agent-pm:
    soul: ~/.openclaw/skills/multi-agent-dev-team/agents/pm-agent/SOUL.md
    model: anthropic/claude-sonnet-4-5-20250929
    cwd: ~/dev-projects  # All projects created here
```

## Best Practices

### 1. Start Small
Don't ask for everything at once. Start with an MVP:

❌ Bad:
> Build a full e-commerce site with user auth, payments, admin dashboard, and inventory management.

✅ Good:
> Build a simple product landing page with hero, features, and signup form.

### 2. Be Specific
The more specific your requirements, the better the result:

❌ Vague:
> Make a nice website.

✅ Specific:
> Create a Next.js landing page with:
> - Hero section with CTA button
> - 3-column feature grid
> - Contact form with email validation
> - Tailwind CSS styling
> - Dark mode support

### 3. Iterate Incrementally
Build in phases:

**Phase 1:** Basic structure
**Phase 2:** Add features
**Phase 3:** Polish & deploy

### 4. Review Output
Always review the generated code before deploying. The agents are good, but human oversight is important.

### 5. Provide Examples
If you have a specific style or pattern in mind, share examples:

> Build a landing page similar to https://example.com, but for [your product].

## Troubleshooting

### "Dev agent didn't complete the task"

**Check:**
1. Was the task specification clear?
2. Are required tools available (Node.js, Git)?
3. Did the agent hit resource limits?

**Solution:**
- Simplify the task
- Check PM agent logs via `sessions_history`
- Try again with clearer requirements

### "Code doesn't work"

**Check:**
1. Dependencies installed? (`npm install`)
2. Environment variables set?
3. Correct Node.js version?

**Solution:**
- Ask PM agent: "The code has errors. Please review and fix."
- The PM will spawn Dev again for corrections

### "Task took too long"

**Solutions:**
- Break into smaller tasks
- Use faster model for Dev agent (`gemini-2.5-flash`)
- Simplify requirements

## Examples

### Example 1: Simple Landing Page

```
You: Build a landing page for a SaaS product called "TaskFlow". 
Include hero, features (3 cards), and pricing table. Use Next.js 
and Tailwind CSS.

PM: Working on it... 
[2 minutes later]
PM: ✅ TaskFlow landing page complete! Ready for deployment.
```

### Example 2: React Component Library

```
You: Create a reusable Button component library with variants 
(primary, secondary, outline) and sizes (sm, md, lg). Use 
TypeScript and class-variance-authority.

PM: Task received. Spawning Dev agent...
[3 minutes later]
PM: ✅ Button component library complete with Storybook examples.
```

### Example 3: API Integration

```
You: Build a Next.js app that fetches and displays GitHub user 
profiles. Include search functionality and responsive cards.

PM: Starting development...
[4 minutes later]
PM: ✅ GitHub profile viewer complete with search and error handling.
```

## Upgrading to Pro

Want more power? Upgrade to **Multi-Agent Dev Team Pro** ($49):

### Pro Features
- 🎯 **6 specialized agents**: PM, Architect, Dev, QA, DevOps, BizDev
- 🔄 **Lobster pipelines**: Automated workflows with approval gates
- 🏗️ **Architecture design**: Dedicated agent for system design
- ✅ **Automated QA**: Code review & testing agent
- 🚀 **DevOps automation**: Deployment & CI/CD setup
- 💼 **Business planning**: Market research & strategy agent
- 📚 **Comprehensive guides**: English + Korean setup docs

[**Get Pro →**](https://ubik-collective.lemonsqueezy.com)

## Support

- 📖 **Documentation**: [docs.openclaw.ai](https://docs.openclaw.ai)
- 💬 **Discord**: [discord.com/invite/clawd](https://discord.com/invite/clawd)
- 🐛 **Issues**: [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
- 📧 **Email**: support@ubik.systems

## License

MIT License - See LICENSE file for details

## Credits

Built by [UBIK Collective](https://ubik.systems)

Powered by [OpenClaw](https://openclaw.ai)

---

**Ready to build with AI agents? Install now:**

```bash
npx clawhub install multi-agent-dev-team
```
