---
name: fis-architecture
description: Multi-agent workflow framework using JSON tickets and file-based coordination. Use when managing multi-agent workflows through JSON tickets, tracking tasks with file-based coordination, generating agent badges, or implementing FIS (Federal Intelligence System) workflow patterns.
---

# FIS Architecture

Multi-agent workflow framework using JSON tickets and file-based coordination.

## Overview

FIS (Federal Intelligence System) manages multi-agent workflows through:
- **JSON tickets** for task tracking
- **File-based** coordination (no database)
- **Markdown** for knowledge storage
- **Optional** Python helpers for badge generation

## Quick Start

### 1. Create Ticket

```bash
python3 lib/fis_lifecycle.py create \
  --agent "worker" \
  --task "Your task description" \
  --role "worker"
```

Or via Python:
```python
from lib.fis_lifecycle import FISLifecycle

fis = FISLifecycle()
fis.create_ticket(
    agent="worker",
    task="Your task description",
    role="worker"
)
```

### 2. Complete Task

```bash
python3 lib/fis_lifecycle.py complete \
  --ticket-id "TASK_XXX"
```

### 3. List Active Tickets

```bash
python3 lib/fis_lifecycle.py list
```

### 4. Generate Badge (Optional)

**Quick generation:**
```bash
cd lib
python3 badge_generator.py
```

**Single badge:**
```python
from lib.badge_generator import generate_badge_with_task

path = generate_badge_with_task(
    agent_name="Worker-001",
    role="WORKER",
    task_desc="Your task description",
    task_requirements=["Step 1", "Step 2", "Step 3"]
)
```

**Multiple badges:**
```python
from lib.badge_generator import generate_multi_badge

cards = [
    {
        'agent_name': 'Worker-001',
        'role': 'worker',
        'task_desc': 'Implement feature A',
        'task_requirements': ['Design', 'Code', 'Test']
    },
    {
        'agent_name': 'Reviewer-001',
        'role': 'reviewer',
        'task_desc': 'Review implementation',
        'task_requirements': ['Check code', 'Verify tests']
    }
]
path = generate_multi_badge(cards, "team_badges.png")
```

**Custom badge with full control:**
```python
from lib.badge_generator import BadgeGenerator
from datetime import datetime

generator = BadgeGenerator()

agent_data = {
    'name': 'Custom-Agent',
    'id': f'AGENT-{datetime.now().year}-001',
    'role': 'WORKER',
    'task_id': '#TASK-001',
    'soul': '"Execute with precision"',
    'responsibilities': [
        "Complete assigned tasks",
        "Report progress promptly"
    ],
    'output_formats': 'MARKDOWN | JSON',
    'task_requirements': [
        "1. Analyze requirements",
        "2. Implement solution"
    ],
    'status': 'ACTIVE',
    # 'qr_url': 'https://your-link.com'  # Optional: adds QR code
}

path = generator.create_badge(agent_data)
```

## File Structure

Skill files:
```
lib/
├── fis_lifecycle.py      # Ticket lifecycle management
├── badge_generator.py    # Badge image generation
└── fis_config.py         # Configuration

examples/
└── demo.py               # Runnable examples showing badge generation
```

Workflow hub (created at runtime):
```
~/.openclaw/fis-hub/           # Your workflow hub
├── tickets/
│   ├── active/               # Active tasks
│   └── completed/            # Archived tasks
└── knowledge/                # Shared knowledge
```

## Ticket Format

```json
{
  "ticket_id": "TASK_001",
  "agent_id": "worker-001",
  "role": "worker",
  "task": "Task description",
  "status": "active",
  "created_at": "2026-02-25T10:00:00",
  "updated_at": "2026-02-25T10:00:00"
}
```

## Workflow

1. **Create** ticket with task description
2. **Execute** task by worker agent
3. **Review** (optional) by reviewer agent
4. **Complete** and archive ticket

## Badge Output

Badges are saved to: `~/.openclaw/output/badges/`

Badge features:
- Security level and workspace ID display
- Optional QR code (when `qr_url` provided)
- Chinese font support

## Dependencies

Optional (for badges):
- `Pillow>=9.0.0`
- `qrcode>=7.0`

## License

MIT
