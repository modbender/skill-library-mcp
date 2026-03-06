# OAuth/Auth-Core Usage

## Important
- Credentials are **never** hardcoded in scripts.
- Credentials come from either:
  1) environment variables (`SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`), or
  2) local vault via `scripts/run-with-vault-env.ps1`.
- This allows every user to use their own Spotify app credentials.

## One-time login (Authorization Code Flow)
From `skills/spotify-intelligence`:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\auth\spotify-auth.ps1"
```

The script opens browser login, receives callback on configured redirect URI, and writes token data to `data/tokens.json`.

## Read currently playing track
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-with-vault-env.ps1 -Command "powershell -ExecutionPolicy Bypass -File .\scripts\auth\get-current-track.ps1"
```

Returns JSON with track name, artist, album, and playback state.

## If another user runs this skill
- Set own env vars before running, **or**
- Store own values in their own local vault instance under the same names.
