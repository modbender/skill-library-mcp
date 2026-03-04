# Farcade Game SDK Reference (`@farcade/game-sdk`)

Use this file when generating or repairing game code for Remix.

## Runtime model

- In Remix-hosted uploads, the SDK is available as `window.FarcadeSDK`.
- Include SDK script in the HTML `<head>`:
  - `<script src="https://cdn.jsdelivr.net/npm/@farcade/game-sdk@0.3.0/dist/index.min.js"></script>`
- Do not rely on package imports in uploaded single-file game code.
- Always call `await window.FarcadeSDK.ready()` before reading player/game data.

## Required hooks for v1 agent validation

These checks are required by `GET /v1/agents/games/{gameId}/versions/{versionId}/validate`:

- `window.FarcadeSDK.singlePlayer.actions.gameOver({ score })`
- `window.FarcadeSDK.onPlayAgain(() => { ... })`
- `window.FarcadeSDK.onToggleMute(({ isMuted }) => { ... })`

## Commonly used SDK surface

Properties/getters:

- `window.FarcadeSDK.player`
- `window.FarcadeSDK.players`
- `window.FarcadeSDK.gameState`
- `window.FarcadeSDK.gameInfo`
- `window.FarcadeSDK.purchasedItems`
- `window.FarcadeSDK.isReady`
- `window.FarcadeSDK.hasItem(itemId)`

Single-player actions:

- `window.FarcadeSDK.singlePlayer.actions.gameOver({ score })`
- `window.FarcadeSDK.singlePlayer.actions.saveGameState({ gameState })`
- `window.FarcadeSDK.singlePlayer.actions.purchase({ item })`
- `window.FarcadeSDK.singlePlayer.actions.reportError({ message, ... })`
- `window.FarcadeSDK.hapticFeedback()`

Multiplayer actions/events also exist (`multiplayer.actions.*`, `onGameStateUpdated`), but are optional for basic single-player games.

## Minimal integration template

```javascript
async function initGame() {
  const sdk = window.FarcadeSDK
  await sdk.ready()

  let muted = true
  sdk.onToggleMute(({ isMuted }) => {
    muted = isMuted
  })

  sdk.onPlayAgain(() => {
    restart()
  })

  function finish(score) {
    sdk.singlePlayer.actions.gameOver({ score })
  }

  function save(state) {
    sdk.singlePlayer.actions.saveGameState({ gameState: state })
  }

  function restart() {
    // reset local game state and render
  }

  // start gameplay loop...
}

initGame()
```

## Mistakes to avoid

- Calling SDK getters before `ready()` resolves.
- Omitting one of the required validation hooks (`gameOver`, `onPlayAgain`, `onToggleMute`).
- Using non-existent SDK methods such as `vibrate`, `checkpoint`, or `save`.
- Using `localStorage`/`sessionStorage` as primary persistence instead of `saveGameState`.
