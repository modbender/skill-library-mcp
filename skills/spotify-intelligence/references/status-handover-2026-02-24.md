# Spotify-Intelligence — Status Handover (2026-02-24)

## Gesamtstatus
- **v1 Core: abgeschlossen**
- Paket: `dist/spotify-intelligence.skill` (clean, ohne lokale Tokens/DB)

## Fertig (Done)
- OAuth/Auth + Refresh
- Read-Layer (single/paginated), dedupe, normalized SQLite model
- Skip/Playtime + Heuristiken + Confidence
- Cleanup/Reorg Engine (proposed -> staged -> confirmed)
- Audit/Undo-Logs + owner-aware foreign-playlist handling
- Governance/Cost Guardrails + Preflight Gates
- Playback Control (play/pause/next/prev/seek/volume/device)
- Song-Search Play + Queue Controls
- Recommendation Layer v1 (`passend`, `mood-shift`, `explore`)
- Feedback Loop (`like/dislike/skip/keep/dont-ask-again`)
- Volume-Signal Ingest + device-specific stats
- Device-Context Profiles + device-aware recommendations
- External Context Resolver scaffold (BT > location > motion)
- Agent Shortcuts (token-sparend)

## Node-Livefeed Status (wichtig)
- **Deferred / On Hold bis App stabil ist**
- Integration ist vorbereitet über:
  - `external_context_events`
  - `context_feature_flags.node_context_enabled`
  - `scripts/context/external-context-commands.ps1`
- Sobald App stabil:
  1. Handy-Node Livefeeds (GPS/BT/motion) aktiv anbinden
  2. Ingest-Pipeline auf echte Node-Events umstellen
  3. Resolver-TTL/Confidence feinjustieren
  4. Empfehlung/Steuerung mit Live-Context final scharf schalten

## Betriebsprinzip (final)
- Gateway: kontinuierliche Low-Cost-Routinen
- Agent: punktuelle Entscheidungs-/Interaktionsaktionen
- Mensch: finale Bestätigung bei kritischen Writes

## Nächster Wiedereinstieg
1. App-Fix bestätigen
2. `external-context-commands.ps1 -Action enable-node-context`
3. erste echte Node-Events ingesten
4. Reco/Decision mit Livefeed validieren
