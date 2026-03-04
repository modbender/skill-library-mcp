# mindmap-generator skill

An OpenClaw skill that generates visual mindmaps from conversations, goals, decisions, and daily priorities — delivered as PNG images directly in Telegram.

## Features

- **Mermaid-based rendering** — uses `@mermaid-js/mermaid-cli` (mmdc) to render mindmaps to PNG
- **Telegram delivery** — sends mindmap images inline via Bot API `sendPhoto`
- **6 templates** — daily priorities, decision tree, weekly review, goal decomposition, project kickoff, meeting action map
- **Graceful fallback** — text-based Unicode tree when rendering fails
- **Meeting notes optional** — works with or without meeting transcripts

## Structure

```
mindmap-generator/
├── SKILL.md                    # Skill definition (required)
├── scripts/
│   ├── render_mindmap.sh       # Mermaid → PNG renderer
│   ├── send_telegram_photo.sh  # Telegram Bot API sender
│   └── generate_and_send.sh    # Full pipeline (stdin → render → send)
├── references/
│   ├── mermaid_mindmap_syntax.md
│   └── mindmap_best_practices.md
└── assets/templates/
    ├── daily_priorities.txt
    ├── decision_tree.txt
    ├── weekly_review.txt
    ├── goal_decomposition.txt
    ├── project_kickoff.txt
    └── meeting_action_map.txt
```

## Prerequisites

- Node.js v18+
- `@mermaid-js/mermaid-cli` (`npm install @mermaid-js/mermaid-cli`)
- `curl` (for Telegram API)
- Telegram Bot Token (set as `TELEGRAM_BOT_TOKEN`)

## Publishing to ClawHub

```bash
clawhub auth login
clawhub publish . --slug mindmap-generator --name "Mindmap Generator" --version 1.0.0 --tags latest
```

## License

MIT
