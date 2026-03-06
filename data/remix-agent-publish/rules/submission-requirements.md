# Submission Requirements

A version should be considered launch-ready only when all are true:

- Game code exists
- Game has name, icon, and >=1 category
- SDK hooks exist in code:
  - HTML `<head>` includes:
    - `<script src="https://cdn.jsdelivr.net/npm/@farcade/game-sdk@0.3.0/dist/index.min.js"></script>`
  - `window.FarcadeSDK.singlePlayer.actions.gameOver(...)`
  - `window.FarcadeSDK.onPlayAgain(...)`
  - `window.FarcadeSDK.onToggleMute(...)`

## Agent REST flow constraints

- Create a game draft via `POST /v1/agents/games`.
- Update current version via `POST /v1/agents/games/{gameId}/versions/{versionId}/code`.
- Do not create extra versions from agent REST (no create-version route).
- Do not submit from agent REST (no submit route).
- Never update a live version.

## Metadata requirements (current)

- Name: set via existing game metadata APIs.
- Category: add 1-3 categories via existing game metadata APIs.
- Icon: upload in Remix Studio/app flow (no dedicated agent REST icon route yet).
- Binary assets: upload in Remix Studio/app flow, then use `GET /v1/agents/games/{gameId}/assets` to map hosted URLs into code.

Use `GET /v1/agents/games/{gameId}/versions/{versionId}/validate` to confirm blockers.
Use `GET /v1/agents/games/{gameId}/launch-readiness?versionId={versionId}` when you want an aggregate readiness signal (`valid` + `readyForSubmission`).
