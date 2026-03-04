# Natural Language Planner

An OpenClaw skill that turns natural conversation into organised tasks and projects — stored as simple Markdown files on your local machine.

## What It Does

- **Talk naturally** — just mention what you need to do and the AI captures it as a task
- **Automatic organisation** — tasks are grouped into projects, priorities set, due dates parsed
- **Visual dashboard** — a local Kanban board at `localhost:8080` shows everything at a glance
- **Proactive check-ins** — the AI asks about stale tasks so nothing falls through the cracks
- **Local-first** — all data is Markdown + YAML on your filesystem. No accounts, no cloud, no lock-in

## Quick Start

### 1. Install the dependency

```bash
pip install pyyaml
```

### 2. Add the skill to your AI assistant

Copy or clone this directory into your skills folder. The AI will detect the
`SKILL.md` and activate the planner automatically.

### 3. Start using it

Just talk to your AI assistant:

> "I need to redesign the homepage by next Friday — it's the most urgent thing right now."

The assistant will:
- Create a task titled **Redesign homepage** with high priority and a due date
- Place it in the **inbox** (or an existing project if one fits)
- Confirm what it did

### 4. Open the dashboard (optional)

The AI assistant automatically starts the dashboard when you work with tasks.
You can also start it manually:

```bash
python -m scripts dashboard ~/nlplanner
```

## Workspace Structure

All your data lives in one directory (default `~/nlplanner`):

```
~/nlplanner/
├── .nlplanner/          # Config and dashboard files
│   └── config.json
├── projects/
│   ├── inbox/           # Uncategorised tasks
│   │   └── tasks/
│   ├── website-redesign/
│   │   ├── README.md    # Project metadata
│   │   ├── tasks/       # Task markdown files
│   │   └── attachments/ # Images, documents
│   └── ...
└── archive/             # Archived projects and tasks
```

Every task and project is a Markdown file with YAML frontmatter — readable
and editable in any text editor.

## Configuration

Settings live in `.nlplanner/config.json`:

| Setting | Default | Description |
|---|---|---|
| `checkin_frequency_hours` | 24 | How often to ask about stale tasks |
| `auto_archive_completed_days` | 30 | Days before done tasks auto-archive |
| `default_priority` | `"medium"` | Default priority for new tasks |
| `dashboard_port` | 8080 | Port for the local dashboard |
| `dashboard_auto_start` | `true` | Agent auto-starts the dashboard on first task operation |
| `dashboard_allow_network` | `false` | Bind to all interfaces (0.0.0.0) instead of localhost |

## Dashboard Features

The browser-based dashboard includes:

- **This Week view** — focus cards for what you're working on this week
- **Kanban board** — drag-free columns for To Do, In Progress, Done
- **Project overview** — cards showing each project with task counts
- **Timeline** — upcoming deadlines sorted by date
- **Search** — find any task instantly
- **Task detail modal** — click to see full task info, attachments, and AI tips
- **Image gallery** — attachments displayed as thumbnails with lightbox
- **Dark mode** — toggle via the header icon (persists across sessions)
- **Auto-refresh** — updates every 5 seconds

## Remote Access (Tunnels)

Want to check your dashboard from your phone or share a link with someone?
The planner can create a secure tunnel to expose your local dashboard.

```bash
# Auto-detects cloudflared, ngrok, or localtunnel
python -m scripts tunnel ~/nlplanner
```

Or ask the AI: *"Make my dashboard accessible from my phone."*

**Supported tools** (install one):

| Tool | Install | Notes |
|---|---|---|
| Cloudflare Tunnel | `winget install cloudflare.cloudflared` / `brew install cloudflared` | Free, no account needed for quick tunnels |
| ngrok | [ngrok.com/download](https://ngrok.com/download) | Free tier, requires account |
| localtunnel | `npm install -g localtunnel` | Free, no account |

> **Security note:** The dashboard has no authentication. Anyone with the
> tunnel URL can view your tasks. Share the link carefully.

## Persistent Service (Raspberry Pi / Servers)

On a headless device (Raspberry Pi, home server, NAS), you can run the
dashboard as a systemd service so it starts on boot and stays running:

1. Create the service file:

```bash
sudo tee /etc/systemd/system/nlplanner-dashboard.service << 'EOF'
[Unit]
Description=Natural Language Planner Dashboard
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/path/to/natural-language-planner
ExecStart=/usr/bin/python3 -m scripts dashboard --network /path/to/workspace
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

2. Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nlplanner-dashboard.service
sudo systemctl start nlplanner-dashboard.service
```

3. Check status and logs:

```bash
systemctl status nlplanner-dashboard.service
journalctl -u nlplanner-dashboard.service -f
```

> **Tip:** Before starting, make sure nothing else is using port 8080
> (`sudo ss -tlnp | grep 8080`). Stale services from earlier setups are
> a common cause of port conflicts. Check with
> `systemctl list-units --type=service | grep dashboard`.

Omit `--network` if the dashboard should only be accessible on localhost.

## Static Export

Export a self-contained HTML snapshot of your dashboard for hosting on any
static platform (GitHub Pages, Netlify, Vercel).

```bash
# Default: exports to <workspace>/.nlplanner/export/
python -m scripts export ~/nlplanner

# Export to a specific directory (e.g. for GitHub Pages)
python -m scripts export ~/nlplanner --output ./docs
```

The export inlines all CSS, JS, and data into a single `index.html` that
works without a server. Note that exports are snapshots — re-export after
changes for an updated version.

## Requirements

- **Python 3.9+**
- **PyYAML** (`pip install pyyaml`)
- No other external dependencies for core functionality
- For remote access: `cloudflared`, `ngrok`, or `localtunnel` (optional)

## Project Structure

```
natural-language-planner/
├── SKILL.md              # AI skill instructions
├── scripts/
│   ├── __init__.py       # Package init
│   ├── __main__.py       # CLI entry point
│   ├── file_manager.py   # CRUD for projects and tasks
│   ├── config_manager.py # Settings management
│   ├── index_manager.py  # Search and lookup
│   ├── dashboard_server.py # Local web server + auto-start
│   ├── tunnel.py         # Remote access via tunnels
│   ├── export.py         # Static HTML snapshot export
│   └── utils.py          # Shared utilities
├── templates/
│   ├── dashboard/        # HTML/CSS/JS for the dashboard
│   ├── project_template.md
│   └── task_template.md
├── tests/                # Unit tests
└── examples/             # Sample data and conversations
```

## Contributing

Contributions are welcome! Here's how:

1. **Fork** this repository
2. Create a **feature branch** (`git checkout -b feature/my-idea`)
3. Make your changes and add tests
4. Submit a **pull request** with a clear description

### Development

```bash
# Run tests
python -m pytest tests/ -v

# Start dashboard in development
python -m scripts dashboard ~/nlplanner

# Start a tunnel for remote access
python -m scripts tunnel ~/nlplanner

# Export a static snapshot
python -m scripts export ~/nlplanner --output ./docs
```

### Areas for contribution

- Better natural date parsing
- Drag-and-drop in the Kanban board
- Import from Todoist / Notion / other tools
- Authentication for tunneled dashboards
- Time tracking

## Design Principles

1. **Local-first** — your data never leaves your machine
2. **Human-readable** — everything is Markdown you can edit by hand
3. **Non-destructive** — archive, never delete
4. **Minimal dependencies** — stdlib where possible
5. **Cross-platform** — works on Windows, macOS, and Linux

## License

MIT — see [LICENSE.txt](LICENSE.txt)
