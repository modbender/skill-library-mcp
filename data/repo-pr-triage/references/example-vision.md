# OpenClaw Vision & PR Evaluation Framework

**Author:** Rex (research agent) | **Date:** 2026-02-16 | **Version:** 1.0

This document provides a decision framework for evaluating PRs against OpenClaw's stated vision and Peter Steinberger's (steipete) priorities. Built from primary sources: GitHub repo, steipete's blog and X posts, Lex Fridman podcast (#491), Peter Yang interview, Pragmatic Engineer interview, and Alex Finn power-user content.

---

## 1. OpenClaw's Mission and Identity

**One-line:** A personal, self-hosted AI assistant you run on your own devices and talk to through the messaging apps you already use.

**Core identity:**
- Self-hosted, local-first gateway (NOT a cloud service)
- Single-user personal assistant (NOT a platform or multi-tenant SaaS)
- Multi-channel inbox (WhatsApp, Telegram, Discord, iMessage, Slack, Signal, Teams, etc.)
- Agent-native: built for AI coding agents with tool use, sessions, memory, multi-agent routing
- Open source (MIT license), moving to a foundation structure
- "The Gateway is just the control plane; the product is the assistant"

**Who it's for:** Developers and power users who want a personal AI assistant they control, without giving up data ownership or relying on hosted services.

---

## 2. Steipete's Priorities and Values (Ranked)

### Tier 1: Non-negotiable
1. **Security and safety.** Steipete cares deeply about prompt injection resistance, DM pairing policies, and treating inbound messages as untrusted. Recent betas focus on "security hardening." He recommends Opus 4.6 partly for "better prompt-injection resistance." The README has an entire security-defaults section.
2. **Local-first / self-hosted.** OpenClaw runs on YOUR hardware, YOUR rules. VPS is discouraged. The architecture is loopback-bound by default. Data stays with the user.
3. **Open source independence.** Even while joining OpenAI, steipete's priority was making OpenClaw a foundation: "open, independent, and just getting started." Model-agnostic by design, supporting any provider.
4. **Simplicity and fun.** "The way to learn AI is to play." He rejects over-engineering: no plan mode ("plan mode was a hack for older models"), no MCPs ("most MCPs should be CLIs"). Prefers the agent to figure things out naturally.

### Tier 2: Strong preferences
5. **Personal assistant UX.** The product is "like having a new weird friend that lives on your computer." Texting from your phone IS the interface. No dashboards required.
6. **Practical, real-world utility.** Flight check-ins, home automation, security cameras, morning briefs. Not theoretical/academic use cases.
7. **Quality over process.** "I ship code I don't read" (Pragmatic Engineer title). Steipete is a builder who moves fast. He values velocity and working code over bureaucratic contribution processes.
8. **Multi-channel as core strength.** Supporting more messaging surfaces is a competitive advantage. Channels are first-class citizens.

### Tier 3: Important but secondary
9. **Voice and multimodal.** Voice Wake, Talk Mode, Canvas/A2UI are highlighted features. The assistant should see, hear, and speak.
10. **Companion apps.** macOS menu bar, iOS/Android nodes extend the gateway to physical devices.
11. **Community and ecosystem.** Skills platform, wizard-driven onboarding, plugin channels. Making it easy for others to extend.

---

## 3. What Aligns With the Vision (GREEN signals)

- **Security hardening:** Prompt injection mitigations, DM policy improvements, input sanitization, auth improvements
- **New channel integrations:** Adding support for more messaging platforms (Matrix, Zalo, etc. already added)
- **Local-first improvements:** Better offline behavior, reduced external dependencies, faster startup
- **Agent reliability:** Session management, retry policies, streaming/chunking, model failover improvements
- **CLI/UX polish:** Better onboarding wizard, doctor diagnostics, error messages
- **Performance:** Faster gateway, lower memory usage, quicker response times
- **Voice/multimodal:** Improvements to Voice Wake, Talk Mode, Canvas, camera/screen integration
- **Skills platform:** Making it easier to write, share, and install skills
- **Bug fixes and stability:** Always welcome
- **Documentation:** Docs improvements, especially for onboarding new users
- **Model support:** Adding new model providers, improving OAuth flows, failover logic
- **PR de-duplication / triage tooling:** Steipete explicitly asked for this (Feb 15 tweet)

---

## 4. What Does NOT Align (RED signals)

- **Cloud/hosted/SaaS direction:** Anything that moves away from local-first. No managed hosting, no cloud dependencies as requirements.
- **Multi-tenant features:** OpenClaw is single-user. PRs adding user management, team features, or org-level abstractions are off-mission.
- **Heavy abstraction layers / frameworks:** Steipete dislikes over-engineering. MCPs, complex planning systems, enterprise middleware patterns are anti-patterns.
- **Vendor lock-in:** Anything that hard-codes a single model provider or requires a specific cloud service.
- **UI-heavy features that bypass messaging:** The core UX is texting. PRs that build elaborate web dashboards as the primary interface miss the point. (Canvas and Control UI exist but serve the assistant, not replace it.)
- **Autonomous agent features without safety rails:** Given the security focus, PRs that let agents take unconstrained external actions would be rejected.
- **Scope creep into unrelated domains:** OpenClaw is a personal assistant gateway. It is not a general-purpose automation platform, CI/CD tool, or social media management suite.
- **Breaking changes without migration path:** The doctor tool exists for migrations. Breaking changes need graceful handling.
- **"AI slop" generators:** Steipete has spoken against AI slop (Lex Fridman 3:02:13). Low-quality auto-generated content features would not align.

---

## 5. Scoring Rubric (0-100)

Use this rubric to score a PR against OpenClaw's vision. Sum the applicable modifiers from a base score of 50.

### Base: 50 points (neutral, well-implemented PR)

### Positive Modifiers (add points)

| Signal | Points | Notes |
|--------|--------|-------|
| Fixes a security vulnerability | +20 | Top priority |
| Improves prompt injection resistance | +15 | Core concern |
| Adds/improves a messaging channel | +12 | Core competitive advantage |
| Bug fix with test coverage | +10 | Always valuable |
| Improves local-first behavior | +10 | Reduces cloud dependency |
| Improves CLI/onboarding UX | +8 | Lowers barrier to entry |
| Performance improvement (measured) | +8 | Speed matters for personal assistant |
| Voice/multimodal improvement | +7 | Active area of investment |
| Documentation improvement | +5 | Helps community growth |
| Skills platform enhancement | +5 | Ecosystem growth |
| Model provider support | +5 | Model-agnostic is a value |
| Has tests | +5 | Quality signal |
| Small, focused diff | +5 | Easier to review, less risk |
| Addresses an open issue | +3 | Community-responsive |

### Negative Modifiers (subtract points)

| Signal | Points | Notes |
|--------|--------|-------|
| Introduces cloud dependency as requirement | -25 | Violates local-first |
| Multi-tenant / team features | -20 | Wrong product direction |
| Vendor lock-in to single provider | -15 | Against model-agnostic principle |
| Large diff with no tests | -15 | Risk signal |
| Adds heavy abstraction layer | -12 | Over-engineering |
| Breaks existing API without migration | -12 | Doctor tool exists for a reason |
| Duplicate of existing PR | -10 | Wastes maintainer time |
| UI-first feature bypassing messaging UX | -8 | Misses core UX |
| Unrelated scope (feature creep) | -10 | Not the product |
| AI slop / low-quality auto-generated code | -15 | Against stated values |
| Spam / promotional content | -30 | Auto-reject, not a real contribution |
| Misleading description (doesn't match code) | -8 | Trust signal |
| PR template unfilled / skipped | -5 | Low-effort signal |
| No description or context | -5 | Hard to evaluate intent |

### Score Interpretation

| Score | Action |
|-------|--------|
| 80-100 | Strong align. Prioritize review. |
| 65-79 | Good align. Standard review queue. |
| 50-64 | Neutral. Review if bandwidth allows. |
| 35-49 | Weak align. Likely close or request major changes. |
| 0-34 | Misaligned. Close with explanation. |

---

## 6. Key Quotes and Signals

### From steipete's blog (Feb 14, 2026):
- "My next mission is to build an agent that even my mum can use."
- "What I want is to change the world, not build a large company."
- "It will stay a place for thinkers, hackers and people that want a way to own their data."
- "The goal of supporting even more models and companies."

### From X/Twitter (Feb 15, 2026):
- "PRs on OpenClaw are growing at an *impossible* rate... I need AI that scans every PR and Issue and de-dupes. It should also detect which PR is the best based on various signals (so really also a deep review is needed). Ideally it should also have a vision document to mark/reject PRs that stray too far."
- "I'm joining OpenAI to bring agents to everyone. OpenClaw is becoming a foundation: open, independent, and just getting started."
- "The Claw gotta orchestrate itself." (on building self-orchestrating tooling)

### From Peter Yang interview:
- "Plan mode was a hack for older models. I just write 'let's discuss' and have a conversation."
- "No MCPs. Most MCPs should be CLIs. The agent will try the CLI, get the help menu, and from now on we're good."
- Use cases: flight check-ins, home control, security camera monitoring

### From Lex Fridman Podcast #491:
- "AI agents will replace 80% of apps" (timestamp 3:02)
- Discussed acquisition offers from OpenAI and Meta (chose OpenAI for alignment)
- "Self-modifying AI agent" as a core concept
- Security concerns discussed at length (1:02:26)

### From README:
- "The Gateway is just the control plane; the product is the assistant."
- "If you want a personal, single-user assistant that feels local, fast, and always-on, this is it."
- Recommends Anthropic Pro/Max + Opus 4.6 for "long-context strength and better prompt-injection resistance"

### From Alex Finn (power user, content reflects ecosystem values):
- "Local > VPS, always" -- aligns with steipete's local-first stance
- Brain + Muscles architecture (expensive model for decisions, cheap models for grunt work)
- Security mindset: bot has admin access, don't expose it to the world
- Interface simplicity: texting from your phone IS the interface

---

## 7. Context for PR Triage Automation

When evaluating a PR automatically, the agent should:

1. **Read the PR title, description, and diff summary** to classify the area (security, channel, CLI, docs, etc.)
2. **Check for duplicates** against open PRs with similar titles or modified files
3. **Apply the scoring rubric** using the positive/negative modifiers
4. **Flag for human review** if score is 50-64 (ambiguous) or touches security-sensitive code
5. **Auto-label** with area tags (security, channel, voice, docs, etc.)
6. **Reject with explanation** if score falls below 35 and reasons are clear

### File-path heuristics for classification:
- `src/channels/*` or `plugins/channel-*` = Channel work (+5 base)
- `src/security/*` or changes to auth/pairing = Security (+10 base)
- `src/agent/*` or `src/session/*` = Core agent runtime (neutral, review carefully)
- `docs/*` = Documentation (+3 base)
- `src/voice/*` or `src/canvas/*` = Multimodal (+3 base)
- `src/cli/*` or `src/wizard/*` = CLI/UX (+3 base)
- `skills/*` = Skills platform (+3 base)

---

## 8. Foundation Transition Considerations

As of Feb 15, 2026, steipete announced OpenClaw is becoming a foundation. This means:
- Governance will formalize; expect contribution guidelines to tighten
- Model-agnostic stance will strengthen (foundation cannot favor one provider)
- Community maintainers will gain more authority
- PRs should be evaluated with long-term maintainability in mind
- Corporate-sponsored PRs that serve a single vendor's interests should be scrutinized

---

*This document should be updated as steipete's public communications evolve. Key sources to monitor: @steipete on X, steipete.me blog, OpenClaw GitHub releases, and the OpenClaw Discord.*
