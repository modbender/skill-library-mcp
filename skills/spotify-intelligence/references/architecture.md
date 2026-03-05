# Architecture (v1)

## Modules
1. `core/config` - Load and validate config/environment
2. `core/logging` - Unified structured logs and errors
3. `spotify/auth` - OAuth + token refresh
4. `spotify/playback` - Playback and device control
5. `journal/db` - SQLite schema + migrations
6. `journal/commands` - rating/tagging/context actions
7. `intelligence/patterns` - feature extraction + scoring
8. `intelligence/recommend` - recommendation modes

## Data Flow
User command -> Spotify API + Local Journal -> Pattern Engine -> Explainable recommendation

## Non-goals (v1)
- Full ML pipeline
- Multi-user tenancy
- Cloud-hosted backend
