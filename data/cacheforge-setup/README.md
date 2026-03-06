# CacheForge Setup

Guided onboarding for CacheForge:

1. Register/authenticate (`POST /api/provision`)
2. Configure upstream (`openrouter`, `anthropic`, or `custom`)
3. Apply OpenClaw provider config (with backup)
4. Validate connectivity
5. Top up credits (Stripe or crypto)

Use `SKILL.md` for agent workflow and `setup.py` for CLI commands.

## What It Does

This skill gets new users from install to first successful CacheForge request quickly, with safe defaults and connectivity checks.

## More from CacheForge

This skill is part of the **CacheForge** open skill suite.

| Skill | What it does |
|-------|--------------|
| **[cacheforge](https://clawhub.com/cacheforge/cacheforge)** | Primary entrypoint with companion bootstrap. |
| **[cacheforge-setup](https://clawhub.com/cacheforge/cacheforge-setup)** | This skill: guided onboarding and first-run configuration. |
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
