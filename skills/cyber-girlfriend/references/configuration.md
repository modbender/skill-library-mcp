# Configuration

Use a single config file. JSON is the simplest default.

## Required Sections

### `persona`

- `name`: in-character name
- `owner_nickname`: how the companion addresses the owner
- `tone`: short guidance string
- `relationship_style`: short guidance string
- `emoji`: optional

### `delivery`

- `channel`: e.g. `telegram`
- `owner_target`: destination identifier
- `owner_session_key`: recent-message source key
- `generator_target`: isolated generation target/session if the runtime needs one

### `schedule`

- `quiet_hours_start`
- `quiet_hours_end`
- `daily_limit`
- `cooldown_sec`
- `mode_windows.afternoon`
- `mode_windows.evening`
- `mode_windows.night`

### `behavior`

- `style_variants`
- `content_types`
- `emotion_thresholds`
- `message_length.min_chars`
- `message_length.max_chars`

### `runtime`

Externalize all runtime hooks here.

Suggested fields:
- `workspace_root`
- `state_dir`
- `recent_messages_path`
- `sessions_store_path`
- `healthcheck_command`
- `jobs_list_command`
- `generate_command_template`
- `send_command_template`
- `generate_retry_attempts`
- `generate_retry_delay_sec`

Do not hardcode a provider or model here unless the user explicitly wants that.
If the runtime depends on a remote model endpoint, expose retry behavior here rather than hardcoding it in prompts.

### `sources`

Optional source blocks.

Suggested X block:
- `enabled`
- `chrome_path`
- `trending_url`
- `cache_path`
- `refresh_ttl_sec`
- `max_items`

## State Files

Recommended:
- `companion-state.json`
- `share-cache.json`

Track only behaviorally useful state:
- pacing
- last style/content type
- preference counters
- last owner reply metadata
- source cache timestamp
