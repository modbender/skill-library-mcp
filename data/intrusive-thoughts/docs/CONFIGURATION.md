# Configuration Reference

All configuration lives in `config.json`. Use `config.example.json` as a template.

## Sections

### `human` — Your Human

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | "Your Human" | Name for greetings |
| `timezone` | string | "UTC" | IANA timezone |
| `telegram_target` | string | "" | Telegram chat ID for messages |
| `preferred_language` | string | "en" | Language code |

### `agent` — Your Agent

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `name` | string | "Agent" | Agent's display name |
| `emoji` | string | "🦞" | Signature emoji |
| `git_email` | string | "agent@openclaw.local" | Git commit email |
| `git_name` | string | "Agent" | Git commit name |

### `integrations` — External Services

#### `integrations.moltbook`
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | false | Enable Moltbook posting |
| `api_key_file` | string | "" | Path to API key file |
| `username` | string | "" | Moltbook username |

#### `integrations.telegram`
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `enabled` | bool | true | Enable Telegram messages |
| `channel` | string | "telegram" | OpenClaw channel name |

#### `integrations.weather`
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `location` | string | "London, UK" | Weather location |
| `api_key` | string | "" | Weather API key (optional) |

### `system` — System Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `data_dir` | string | project dir | Data directory path |
| `dashboard_port` | int | 3117 | Dashboard HTTP port |
| `log_level` | string | "INFO" | Logging level |

### `scheduling` — Timing

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `morning_mood_time` | string | "07:00" | Morning ritual time (HH:MM) |
| `night_sessions` | array | [...] | Night workshop times |
| `day_sessions` | array | [...] | Default daytime pop-in times |
| `timezone` | string | "UTC" | Scheduling timezone |

### `customization` — Behavior Tuning

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `mood_influence_strength` | float | 1.0 | How much weather/news affects mood (0-2) |
| `streak_sensitivity` | float | 0.7 | How quickly streaks trigger variety (0-1) |
| `achievement_notifications` | bool | true | Announce achievements |
| `journal_auto_generate` | bool | true | Auto-generate night journals |
| `soundtrack_display` | bool | true | Show mood soundtracks |

## Environment Variables

Config values can be overridden with environment variables:

```bash
INTRUSIVE_DATA_DIR=/custom/path
INTRUSIVE_DASHBOARD_PORT=8080
INTRUSIVE_LOG_LEVEL=DEBUG
```

## Security Notes

- **Never commit `config.json`** — it may contain API keys
- Use `config.example.json` as a template for new installations
- The `.gitignore` excludes `config.json` and all runtime data
- API keys should reference files, not be stored directly in config
