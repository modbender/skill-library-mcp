# Claw Mentor — Mentee Skill

**Bring your mentor's updates into your OpenClaw agent.**

Subscribe to an expert mentor at [app.clawmentor.ai](https://app.clawmentor.ai). When they update their OpenClaw configuration, your agent notifies you with a plain-English compatibility report and guides you through applying or skipping the changes — safely.

## Quick Start

1. Subscribe at [app.clawmentor.ai](https://app.clawmentor.ai)
2. Get your API key: Settings → Mentee Skill → Generate API Key
3. Install this skill in your OpenClaw `skills/` directory
4. Configure: set `CLAW_MENTOR_API_KEY` in your environment

Full instructions in [SKILL.md](./SKILL.md).

## Privacy

Your config files never leave your machine. The server only receives:
- Your onboarding survey answers (voluntary, self-reported)
- Your apply/skip/rollback decisions (no config content)

Audit exactly what this skill does: it's all in SKILL.md and the API endpoints are documented there.

## License

MIT
