---
name: aavegotchi-renderer-bypass
description: Render Aavegotchi assets by deriving renderer hashes from Goldsky Base core data and calling POST /api/renderer/batch on www.aavegotchi.com. Use when the user gives a tokenId or inventory URL, or when deterministic hash plus image artifacts are required.
---

# Aavegotchi Renderer Bypass

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
`<Collateral>-<EyeShape>-<EyeColor>-<Body>-<Face>-<Eyes>-<Head>-<LeftHand>-<RightHand>-<Pet>`
4. Call `POST https://www.aavegotchi.com/api/renderer/batch` with:
- `verify: true`
- `renderTypes: ["PNG_Full", "PNG_Headshot", "GLB_3DModel"]`
5. Download `proxyUrls.PNG_Full` and `proxyUrls.PNG_Headshot`.
6. Return the hash, response, and saved artifact paths.

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

## Return format

Always return:

1. `tokenId`
2. `hash`
3. `/api/renderer/batch` status and raw JSON
4. `PNG_Full` and `PNG_Headshot` output paths (or missing reason)
5. `GLB_3DModel` URL or `availability.exists=false`

## Troubleshooting

- If Goldsky returns no gotchi, verify `tokenId` and Base context.
- If batch returns hash-format `400`, verify eye mappings and left/right wearable order.
- If `availability.exists` is `false`, rerun batch to trigger render and poll again.
- If endpoint returns `404`, verify production deployment state.
