# Shelter Agent Skill

**[shelter.money](https://shelter.money)** — Your AI financial advisor, connected to your real bank data.

Shelter connects your bank accounts via Plaid and gives you (and your AI agents) real-time financial health: safe-to-spend, cash forecasts, zombie subscriptions, affordability checks, and AI coaching. This skill lets Claude Code, OpenClaw, and other AI agents talk directly to your Shelter data.

## Get started

1. **Create your free account** at **[shelter.money](https://shelter.money)**
2. **Connect your bank** — takes ~60 seconds via Plaid
3. **Generate an API key** in the app under Settings > API Keys
4. **Install the skill** (pick one):

```bash
# Claude Code marketplace
/plugin marketplace add nextauralabs/shelter-skill

# npm
npm install -g @shelter/agent-skill

# ClawHub
clawhub install shelter

# Manual
# Copy SKILL.md and references/ into ~/.claude/skills/shelter/
```

5. **Set your key**:
```bash
export SHELTER_API_KEY="wv_your_key_here"
```

6. **Ask your agent anything about your money** — it handles the rest.

## What your agent can do

| Ask your agent... | What happens |
|---|---|
| "How am I doing?" | Checks safe-to-spend, stress level, upcoming income |
| "When do I run out of money?" | Calculates runway and predicts the next cash crunch |
| "What does next week look like?" | 14-day day-by-day balance forecast |
| "Any problems I should know about?" | Surfaces zombie subscriptions, spending spikes, upcoming bills |
| "Where am I wasting money?" | Finds savings opportunities with estimated annual savings |
| "Can I afford $200 headphones?" | Simulates the purchase against your real cash flow |
| "Give me today's coaching" | Personalized financial coaching with specific action items |
| Complex financial questions | Routes to Guardian AI for nuanced, contextual advice |

## Security

- **Read-only** — Shelter can see your data but can never move money
- **Scoped API keys** — you choose exactly what each key can access
- **No raw bank data** — the API returns computed insights, not raw transactions
- **Keys are hashed** — your secret is never stored in plain text
- **Audit logging** — every API call is logged
- **Instant revocation** — disable any key from Settings > API Keys

## Links

- **Sign up**: [shelter.money](https://shelter.money)
- **API docs**: [SKILL.md](./SKILL.md) | [Data Model Reference](./references/DATA_MODEL.md)
- **Support**: support@shelter.money
- **Privacy**: [shelter.money/privacy](https://shelter.money/privacy)

## License

MIT
