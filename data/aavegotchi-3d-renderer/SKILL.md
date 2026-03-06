---
name: aavegotchi-3d-renderer
description: Render Aavegotchi assets by deriving renderer hashes from Goldsky Base core data and calling POST /api/renderer/batch on www.aavegotchi.com. Use when the user gives a tokenId or inventory URL, or when deterministic hash plus image artifacts are required.
---

# Aavegotchi 3D Renderer

Render gotchi assets from token data and renderer batch APIs.

## Inputs

- Accept either `tokenId` or inventory URL with `id=<tokenId>`.
- Target Base by default (`chainId=8453`).

## Outputs

- Return derived renderer hash.
- Return `/api/renderer/batch` HTTP status.
- Save raw batch JSON to disk.
- Save `PNG_Full` and `PNG_Headshot` to disk when available.
- Return `GLB_3DModel` availability and URL when present.

## Execute

1. Extract `tokenId` from direct input or inventory URL.
2. Query Goldsky Base core subgraph:
`https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`
3. Derive hash in renderer format:
`<Collateral>-<EyeShape>-<EyeColor>-<Body>-<Face>-<Eyes>-<Head>-<RightHand>-<LeftHand>-<Pet>`
4. Kick off render with `POST https://www.aavegotchi.com/api/renderer/batch` using:
- `force: true`
- `verify: false`
- `renderTypes: ["PNG_Full", "PNG_Headshot", "GLB_3DModel"]`
5. Poll `POST /api/renderer/batch` with `verify: true` until `availability.exists=true` for all requested render types or timeout.
6. Download `proxyUrls.PNG_Full` and `proxyUrls.PNG_Headshot` only when corresponding `availability.exists=true`.
7. Return the hash, kickoff + verify responses, poll summary, and saved artifact paths.

## Command

Run the bundled script:

```bash
node scripts/render-gotchi-bypass.mjs --token-id 6741
```

Or pass an inventory URL:

```bash
node scripts/render-gotchi-bypass.mjs \
  --inventory-url "https://www.aavegotchi.com/u/0x.../inventory?itemType=aavegotchis&chainId=8453&id=6741"
```

Use `--out-dir /tmp` to control artifact location (default: `/tmp`).

Optional polling controls:

```bash
--poll-attempts 18 --poll-interval-ms 10000
```

## Return format

Always return:

1. `tokenId`
2. `hash`
3. Kickoff status, verify status, and raw JSON paths
4. Poll summary (`pollAttempts`, `pollIntervalMs`, `renderReady`)
5. `PNG_Full` and `PNG_Headshot` output paths (or missing reason)
6. `GLB_3DModel` availability and URL when present

## Troubleshooting

- If Goldsky returns no gotchi, verify `tokenId` and Base context.
- If batch returns hash-format `400`, verify eye mappings and right/left wearable order (`index4` then `index5`).
- If `availability.exists` is `false`, ensure kickoff used `force:true`, then keep polling `verify:true` until timeout.
- If endpoint returns `404`, verify production deployment state.
