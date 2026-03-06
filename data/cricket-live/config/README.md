# Configuration

## `cricket.yaml`

Main skill configuration.

| Key | Description | Default |
|-----|-------------|---------|
| `api_key` | CricketData.org API key. **Recommended:** use `CRICKET_API_KEY` env var instead. | `""` |
| `base_url` | API base URL | `https://api.cricapi.com/v1` |
| `favorite_teams` | Teams to prioritize in alerts | `[India, Mumbai Indians, Chennai Super Kings]` |
| `alert_events` | Events that trigger notifications | `[wicket, century, match_end, half_century]` |
| `cache_dir` | Directory for cached API responses | `/tmp/cricket-cache` |
| `cache_ttl` | TTL (seconds) per endpoint type | See file for defaults |
| `timezone` | Display timezone | `Asia/Kolkata` |

### API Key Priority
1. `CRICKET_API_KEY` environment variable (highest priority)
2. `api_key` field in `cricket.yaml`

## `teams.yaml`

Team name aliases for fuzzy matching. Maps common shorthand names to canonical names used by the CricketData.org API.

**Structure:**
```yaml
international:
  India:          # Canonical name
    - India       # Aliases
    - IND
    - Team India

ipl:
  Mumbai Indians:
    - MI
    - Mumbai
```

**Adding a team:** Add a new entry under `international` or `ipl` with the canonical name as the key and aliases as a list.
