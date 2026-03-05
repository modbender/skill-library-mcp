# django-claw

Run Django management commands and ORM queries directly from OpenClaw — on any Django project.

## Requirements

- [OpenClaw](https://openclaw.ai) installed
- `bash` and `python3` available
- macOS or Linux

## Installation

```bash
clawhub install django-claw
```

Then run the setup wizard on first use:

```
django-claw setup
```

The wizard will ask for your Django project path, virtual env path, and settings module. Config is saved to `~/.openclaw/skills/django-claw/config.json$

## Commands

| Command | Description |
|---|---|
| `django-claw setup` | Run the setup wizard |
| `django-claw models` | List all models and record counts |
| `django-claw apps` | List installed Django apps |
| `django-claw urls` | List all URL patterns |
| `django-claw users` | List all users |
| `django-claw db` | Show database stats (all models with counts) |
| `django-claw pending` | Show unapplied migrations |
| `django-claw showmigrations` | Show full migration history |
| `django-claw makemigrations` | Create new migrations |
| `django-claw migrate` | Apply pending migrations |
| `django-claw check` | Run Django system checks |
| `django-claw version` | Show Django version |
| `django-claw python` | Show Python version |
| `django-claw logs` | Tail the Django log file |
| `django-claw shell: <code>` | Run a Django ORM query |
| `django-claw readonly` | Check read-only mode status |
| `django-claw readonly on` | Enable read-only mode |
| `django-claw readonly off` | Disable read-only mode |

## Read-Only Mode

When read-only mode is enabled, destructive commands (`migrate`, `makemigrations`, `shell`) are blocked. Useful for Production environments.

```
django-claw readonly on
```

## Reconfigure

To change your project path or settings at any time:

```
django-claw setup
```

## Source

[github.com/manojrammurthy/django-claw-skill](https://github.com/manojrammurthy/django-claw-skill)
