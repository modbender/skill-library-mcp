# OpenClaw Full CLI Reference

Reference normalized against `https://docs.openclaw.ai/llms.txt`.
Last verified: 2026-02-22.

Safety note:
- Commands listed here reflect upstream CLI surface.
- Local wrapper policy may block high-risk groups unless `OPENCLAW_WRAPPER_ALLOW_RISKY=1`.
- See `references/security-policy.md`.

## Top-level CLI command surface (official docs index)

- `openclaw acp` — https://docs.openclaw.ai/cli/acp.md
- `openclaw agent` — https://docs.openclaw.ai/cli/agent.md
- `openclaw agents` — https://docs.openclaw.ai/cli/agents.md
- `openclaw approvals` — https://docs.openclaw.ai/cli/approvals.md
- `openclaw browser` — https://docs.openclaw.ai/cli/browser.md
- `openclaw channels` — https://docs.openclaw.ai/cli/channels.md
- `openclaw clawbot` — https://docs.openclaw.ai/cli/clawbot.md
- `openclaw completion` — https://docs.openclaw.ai/cli/completion.md
- `openclaw config` — https://docs.openclaw.ai/cli/config.md
- `openclaw configure` — https://docs.openclaw.ai/cli/configure.md
- `openclaw cron` — https://docs.openclaw.ai/cli/cron.md
- `openclaw daemon` — https://docs.openclaw.ai/cli/daemon.md
- `openclaw dashboard` — https://docs.openclaw.ai/cli/dashboard.md
- `openclaw devices` — https://docs.openclaw.ai/cli/devices.md
- `openclaw directory` — https://docs.openclaw.ai/cli/directory.md
- `openclaw dns` — https://docs.openclaw.ai/cli/dns.md
- `openclaw docs` — https://docs.openclaw.ai/cli/docs.md
- `openclaw doctor` — https://docs.openclaw.ai/cli/doctor.md
- `openclaw gateway` — https://docs.openclaw.ai/cli/gateway.md
- `openclaw health` — https://docs.openclaw.ai/cli/health.md
- `openclaw hooks` — https://docs.openclaw.ai/cli/hooks.md
- `openclaw logs` — https://docs.openclaw.ai/cli/logs.md
- `openclaw memory` — https://docs.openclaw.ai/cli/memory.md
- `openclaw message` — https://docs.openclaw.ai/cli/message.md
- `openclaw models` — https://docs.openclaw.ai/cli/models.md
- `openclaw node` — https://docs.openclaw.ai/cli/node.md
- `openclaw nodes` — https://docs.openclaw.ai/cli/nodes.md
- `openclaw onboard` — https://docs.openclaw.ai/cli/onboard.md
- `openclaw pairing` — https://docs.openclaw.ai/cli/pairing.md
- `openclaw plugins` — https://docs.openclaw.ai/cli/plugins.md
- `openclaw qr` — https://docs.openclaw.ai/cli/qr.md
- `openclaw reset` — https://docs.openclaw.ai/cli/reset.md
- `openclaw sandbox` — https://docs.openclaw.ai/cli/sandbox.md
- `openclaw security` — https://docs.openclaw.ai/cli/security.md
- `openclaw sessions` — https://docs.openclaw.ai/cli/sessions.md
- `openclaw setup` — https://docs.openclaw.ai/cli/setup.md
- `openclaw skills` — https://docs.openclaw.ai/cli/skills.md
- `openclaw status` — https://docs.openclaw.ai/cli/status.md
- `openclaw system` — https://docs.openclaw.ai/cli/system.md
- `openclaw tui` — https://docs.openclaw.ai/cli/tui.md
- `openclaw uninstall` — https://docs.openclaw.ai/cli/uninstall.md
- `openclaw update` — https://docs.openclaw.ai/cli/update.md
- `openclaw voicecall` — https://docs.openclaw.ai/cli/voicecall.md
- `openclaw webhooks` — https://docs.openclaw.ai/cli/webhooks.md

## Quick usage rule
- For full subcommand syntax, use `openclaw <command> --help`.
- For API-oriented flows, prefer local docs: `/home/openclaw/.openclaw/workspace/docs`.
