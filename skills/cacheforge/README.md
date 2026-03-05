# CacheForge

Primary entrypoint for CacheForge on OpenClaw.

Install `cacheforge` first. It bootstraps companion skills when needed, then routes workflow tasks to:

1. `cacheforge-setup` (onboarding)
2. `cacheforge-ops` (billing/upstream/keys)
3. `cacheforge-stats` (usage/savings telemetry)

## Install

```bash
clawhub install cacheforge
```

## What It Does

CacheForge is an OpenAI-compatible gateway for agent workflows. It can reduce wasted LLM spend and improve repeat-turn performance (results vary by provider/workload).

Vault Mode (Pro) targets tool-heavy agents.

## More from CacheForge

This skill is part of the **CacheForge** open skill suite.

| Skill | What it does |
|-------|--------------|
| **[cacheforge](https://clawhub.com/cacheforge/cacheforge)** | This skill: primary entrypoint with companion bootstrap. |
| **[cacheforge-setup](https://clawhub.com/cacheforge/cacheforge-setup)** | Guided onboarding: register, configure upstream, apply OpenClaw config, validate. |
| **[cacheforge-ops](https://clawhub.com/cacheforge/cacheforge-ops)** | Day-2 operations: balance, top-up, upstream management, API keys. |
| **[cacheforge-stats](https://clawhub.com/cacheforge/cacheforge-stats)** | Terminal dashboard for usage, savings, and performance telemetry. |

Start with:

```bash
clawhub install cacheforge
```

## Links

- **Console**: [app.anvil-ai.io](https://app.anvil-ai.io)
- **GitHub**: [cacheforge-ai/cacheforge-skills](https://github.com/cacheforge-ai/cacheforge-skills)

## License

MIT

---

Built by **[CacheForge](https://app.anvil-ai.io/)**.

CacheForge helps reduce wasted LLM spend on agent workflows (results vary by provider/workload).
