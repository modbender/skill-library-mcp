# Derived Feature Layer (Fallback when Spotify feature endpoint is unavailable)

When Spotify native feature flags (e.g. `audio-features`) are blocked (403), we build proxy features from:
- Skip/completion/playtime signals
- Recency counters
- User tags/context (`gym`, `focus`, etc.)

## Table
- `track_derived_features`
  - `speed_proxy`
  - `energy_proxy`
  - `focus_proxy`
  - `mood_stability_proxy`
  - `novelty_proxy`
  - `confidence`

## Rebuild
```powershell
python .\scripts\decision\rebuild-derived-features.py
```

## Queries
Fast-like proxy:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\query-derived-fast.ps1 -MinSpeedProxy 0.6 -Top 50
```

Focus-like proxy:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\decision\query-derived-focus.ps1 -MinFocusProxy 0.6 -Top 50
```

## Goal
Combine Spotify data + own behavioral/context data for stronger correlations even without native Spotify feature flags.
