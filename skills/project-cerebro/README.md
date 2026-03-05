# Project Cerebro

**Autonomous AI Brain Control Center** — A multi-agent task orchestration system built on OpenClaw.

---

## Overview

Cerebro manages multiple specialized AI **brains** (agents). Tasks are assigned to brains, which execute them autonomously using OpenClaw. A web dashboard provides visibility and control.

### The core flow (this is the “power + simplicity”)
- **Execution Stream = source of truth** for everything that will execute / has executed
- **One-time tasks** sit in the Execution Stream until either:
  - you manually hit **Run**, or
  - the task’s brain is in **Auto Mode**
- **Recurring tasks** spawn exactly **one** task instance into the Execution Stream when due
  - recurring instances execute when due **regardless of Auto Mode**
  - you can **disable** a recurring task with the power toggle
  - you can also manually **spawn/run** an instance via the recurring task’s play button
- **Each task is assigned to a brain**, and the brain’s scope/tools/context determine how it executes

**Key Features:**
- Multi-brain orchestration with specialized agents
- Recurring tasks & scheduled automation
- Channel-agnostic notifications via OpenClaw (`config/brain_targets.json`)
- Optional Job Applications module (Kanban + Job Brain)
- Responsive web UI with dark mode
- Reports (markdown artifacts)
- Safe: personal config lives in local env/config files (not committed)

---

## Quick Start

See **[SETUP.md](./SETUP.md)** for detailed installation and configuration.

**TL;DR:**
```bash
git clone https://github.com/YOUR_USERNAME/project-cerebro.git
cd project-cerebro
npm install
cp .env.example .env
# Edit .env with your OpenClaw token, etc.
cp config/brains.template.json config/brains.json
cp config/brain_targets.template.json config/brain_targets.json
# Edit config/brain_targets.json with your channel + target per brain
npm run build
npm start
# Dashboard: http://localhost:3000 (default)
```

---

## Architecture

See **[ARCHITECTURE.md](./ARCHITECTURE.md)** for detailed design.

**High-level:**
- **Backend:** TypeScript + Fastify + SQLite
- **Frontend:** React + Vite + Tailwind
- **Integration:** OpenClaw Gateway (WebSocket/HTTP API)
- **Channels:** Any OpenClaw-supported channel (notifications + brain routing via `config/brain_targets.json`)

---

## Brains

Each brain is a specialized OpenClaw agent with its own scope, tools, and context.

**Important:** the open-source templates intentionally include only a minimal default set of brains. Zach’s custom brains (e.g. research/money) are not included.

Default examples:
- **Nexus (default brain):** the general-purpose brain for orchestration and “everything else”
- **Personal Life Brain**
- **Schoolwork Brain**

Optional module:
- **Job Application Brain** (+ Job Applications tracker + Job Profile page)
Routing:
- Per-brain notification destination is defined in `config/brain_targets.json` as `{ channel, target }`.

Configure in `config/brains.json` (copy from template).

---

## Security & Privacy

- **No secrets in repo:** All tokens, personal IDs, and config are `.gitignore`d.
- **No personal tasks shipped:** Your SQLite DB + local tasks/recurring tasks are never committed. See `config/seeds/*.template.json` for starter examples.
- **Templates provided:** `.env.example`, `config/*.template.json`.
- **Local-only by default:** Dashboard binds to `127.0.0.1`.
- **OpenClaw hardening:** Run `openclaw security audit --deep` on the host.

---

## Modularity (agent-friendly)

This repo is meant to be easy for agents to customize.

Common edits an agent can do safely:
- **Add a new brain**: add an entry to `config/brains.json` + `config/brain_targets.json`, then create/configure the corresponding OpenClaw agent.
- **Remove the Job Applications module**: remove the Job Brain entry from `config/brains.json` and delete the Job Applications page/routes (frontend) + job profile routes (backend).
- **Change execution behavior**: use Auto-mode per brain, manual “Run” actions, and recurring tasks that spawn instances into the Execution Stream.

## Development

```bash
npm run dev        # Backend dev server (hot reload)
cd frontend && npm run dev  # Frontend dev server
npm run build      # Build both backend + frontend
npm test           # (not yet implemented)
```

---

## Deployment

### Systemd Service (Linux)

```bash
sudo cp project-cerebro.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable project-cerebro
sudo systemctl start project-cerebro
```

### Docker (future)

Not yet packaged. PRs welcome.

---

## Contributing

1. Fork the repo
2. Create a feature branch
3. Make changes (no personal info!)
4. Submit a PR

---

## License

MIT (or your preferred license)

---

## Credits

Built with [OpenClaw](https://openclaw.ai) — the AI assistant framework.
