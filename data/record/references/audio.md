# record audio - Full Reference

## Options

| Option | Description | Default |
|---|---|---|
| `--duration <seconds>` | Stop after N seconds. Without it, press stop key. | - |
| `--output <path>` | File or directory for output. | temp dir |
| `--name <pattern>` | Filename pattern (strftime tokens, `{uuid}`, `{chunk}`). | `micrec-%Y%m%d-%H%M%S` |
| `--overwrite` | Overwrite existing output file. | false |
| `--json` | Print JSON to stdout. | false |
| `--source <mic\|system\|both>` | Capture source selection. | `mic` |
| `--list-devices` | List input devices and exit. | - |
| `--list-displays` | List displays for system audio capture and exit. | - |
| `--list-formats` | List audio formats and exit. | - |
| `--list-qualities` | List encoder qualities and exit. | - |
| `--display <id\|primary>` | Display to use for system audio capture. | primary |
| `--device <uid\|name>` | Input device UID or name (mic source only). | system default |
| `--stop-key <char>` | Stop key (single ASCII char). | `s` |
| `--pause-key <char>` | Pause key. | `p` |
| `--resume-key <char>` | Resume key. | `r` |
| `--silence-db <dBFS>` | Silence threshold (e.g. `-50`) for mic source. Requires `--silence-duration`. | - |
| `--silence-duration <s>` | Stop after N seconds of silence (mic source). Requires `--silence-db`. | - |
| `--max-size <MB>` | Stop when file reaches this size in MB. | - |
| `--split <seconds>` | Split into chunks. Output must be a directory. | - |
| `--sample-rate <Hz>` | Sample rate. | 44100 (mic), 48000 (system/both) |
| `--channels <count>` | Channel count. | 1 (mic), 2 (system/both) |
| `--system-gain <multiplier>` | Gain multiplier for system audio (`system`/`both`). | 1.0 |
| `--bit-rate <bps>` | Encoder bit rate. Ignored for linearPCM. | 128000 |
| `--format <format>` | Audio format. | aac |
| `--quality <quality>` | Encoder quality. | high |

## Supported Formats

| Format | Extension |
|---|---|
| `aac` | `.m4a` |
| `alac` | `.m4a` |
| `linearPCM` | `.caf` |
| `appleIMA4` | `.caf` |
| `ulaw` | `.caf` |
| `alaw` | `.caf` |

Source compatibility:
- `--source mic`: all formats above.
- `--source system|both`: `aac`, `alac`.

## Examples

```bash
# Basic timed recording
record audio --duration 5

# Record system audio only
record audio --source system --duration 5

# Record system + mic audio mixed into one track
record audio --source both --display primary --duration 10

# Boost system audio in mixed capture
record audio --source both --system-gain 2.0 --duration 10

# Record with specific device
record audio --device "MacBook Pro Microphone" --duration 10

# List displays for system capture selection
record audio --list-displays

# High-quality AAC recording
record audio --format aac --sample-rate 48000 --channels 2 --quality high --duration 30

# Auto-stop on silence
record audio --silence-db -50 --silence-duration 3

# Split into 30-second chunks
record audio --split 30 --output /tmp

# Custom filename pattern
record audio --output /tmp --name "meeting-%Y%m%d-%H%M%S-{uuid}"

# Save to specific file, overwrite if exists
record audio --output /tmp/meeting.m4a --overwrite --duration 60

# JSON output
record audio --duration 5 --json
```

## Notes

- Pause/resume keys work only with a real TTY.
- If `--pause-key` and `--resume-key` are the same, the key toggles pause/resume.
- With `--split --json`, output is NDJSON (one JSON object per chunk).
- `--source system` and `--source both` require Screen Recording permission.
- `--system-gain` boosts system audio before mixing/encoding. Large values can clip; start near `1.2` to `2.0`.
