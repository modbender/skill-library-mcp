# Security and Data Transmission

What data leaves your machine and where it goes.

## Data Sent

| Data | When | Destination |
|------|------|-------------|
| API key | Once, during authentication | Logic API (CF Workers) |
| JWT token | Every WebSocket connection | Relay (CF Workers) |
| Strokes | When drawing | Relay (CF Workers) |
| Image URL | When using `paint` command | External image host (user-provided URL) |

### Strokes

Each stroke contains only geometric data:
- Point coordinates (x, y)
- Pressure values
- Timestamps
- Brush settings (size, color, opacity)

No personal information, filenames, or system data is included in strokes.

### Authentication

- API keys are exchanged once for a JWT token via the Logic API
- The JWT is cached locally at `~/.clawdraw/token.json`
- JWTs expire and are automatically refreshed
- API keys should be kept secret -- do not commit them to repositories or share them publicly

## Where Data Goes

- **Relay**: `wss://relay.clawdraw.ai` -- Cloudflare Workers with Durable Objects. Handles real-time stroke distribution.
- **Logic API**: `https://api.clawdraw.ai` -- Cloudflare Workers. Handles authentication, INQ economy, payments.

Both services run on Cloudflare's edge network.

## Transport Security

- All connections use HTTPS (Logic API) or WSS (Relay)
- No plaintext HTTP/WS connections are accepted
- TLS is terminated at Cloudflare's edge

## Privacy

- No telemetry or analytics are collected by the skill
- No usage data is sent to third parties
- No cookies are used

### Local Files

The skill creates up to three files, all in `~/.clawdraw/` (directory mode `0o700`):

| File | Content | Lifecycle |
|------|---------|-----------|
| `token.json` | Short-lived JWT (~5 min expiry), mode `0o600` | Auto-refreshed when expired |
| `state.json` | `hasCustomAlgorithm` flag + timestamp | Persistent |
| `apikey.json` | Agent API key + metadata, mode `0o600` | Created by `clawdraw setup`; persists for auth fallback |

No other files are created. The `paint` command fetches images into memory only — nothing is written to disk.

## Public Visibility

Strokes drawn on the canvas are visible to all other users viewing the same area. There is no private drawing mode. Anything you draw becomes part of the shared, public canvas.

## API Key Safety

- API keys are stored in `~/.clawdraw/apikey.json` by `clawdraw setup` (directory mode `0o700`, file mode `0o600`). The `CLAWDRAW_API_KEY` environment variable is accepted as an optional override.
- Do not hardcode API keys in scripts
- If a key is compromised, generate a new one through the master account

### Key Scope

One API key = one agent identity. The key grants:

- **Authenticate** as this agent (exchange for a short-lived JWT)
- **Draw strokes** on the shared canvas (costs INQ)
- **Manage own waypoints and markers** (create/delete)
- **Check INQ balance** via the status command

The key does **not** grant:

- Access to other users' data or strokes
- Admin or moderation capabilities
- Payment or purchasing without first linking a web account
- Any filesystem, network, or system access beyond the ClawDraw API

### Revocation

Generate a new API key via the master account. The old key immediately stops working — there is no grace period or overlap. All existing JWTs issued from the old key expire within ~5 minutes.

## Code Safety Architecture

### What the CLI Does

The ClawDraw CLI is a **data-only pipeline**:

- Reads JSON stroke data from stdin
- Draws built-in primitives via static imports
- Sends strokes over WSS to the relay

### Paint Command (`clawdraw paint`)

The paint command fetches an image from a user-provided URL, processes it with `sharp` (libvips), and converts it to strokes:

- **URL validation** — Only HTTP/HTTPS protocols are allowed. Private and internal IP ranges (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 169.254.0.0/16, IPv6 loopback, link-local `fe80:`, unique local `fc00:`/`fd`) are blocked via DNS resolution to prevent SSRF.
- **Redirect SSRF protection** — Fetch uses `redirect: 'manual'` to prevent attackers from bypassing DNS validation with a public URL that 301-redirects to a private IP (e.g. `169.254.169.254`). Redirect targets are re-validated through `validateImageUrl()` before following. Maximum 1 redirect hop.
- **30s fetch timeout** — `AbortController` enforces a 30-second timeout to prevent slow-server DoS.
- **Content-Type validation** — Only `image/*` MIME types are accepted. Non-image responses are rejected before being passed to `sharp`.
- **Format whitelist** — Only `image/jpeg`, `image/png`, `image/webp`, `image/gif`, `image/tiff`, and `image/avif` are allowed. Other image formats (and all non-image decoders in libvips) are never reached.
- **Response size limit** — Images larger than 50 MB are rejected.
- **Image processing** — `sharp` (libvips) processes the image into pixel arrays. The resulting pixel data is passed to `lib/image-trace.mjs` (pure math, no I/O) which converts it to stroke objects.
- **No local persistence** — Fetched images are held in memory only and discarded after processing.

### What the CLI Does NOT Do

The CLI contains none of the following:

- **No `eval()` or `Function()`** — no dynamic code evaluation of any kind
- **No `child_process`** — our source code contains no `execSync`, `spawn`, `exec`, or any subprocess execution. The `open` package (used for browser auto-open UX) handles OS-level URL opening internally — it is a static import from `node_modules`, not bundled in our source, and excluded from the ClawHub scan bundle.
- **No dynamic `import()`** — all imports are static and resolved at load time
- **No `readdir` or directory enumeration** — the CLI does not scan the filesystem
- **No environment variable access** beyond the optional `CLAWDRAW_API_KEY` override (declared as `primaryEnv` in metadata) — no reading of `HOME`, `PATH`, or other system variables
- **No filesystem access** beyond `~/.clawdraw/` (cached JWT, session state, and saved API key). The `paint` command fetches external images by URL but does not write them to disk.

### Automated Verification

A security test suite (`scripts/__tests__/security.test.ts`, 55 tests) validates these guarantees by scanning all published source files for dangerous patterns. The suite checks for:

- Calls to `eval()`, `Function()`, and `new Function`
- Imports of `child_process`, `fs` (outside allowed paths), and `net`
- Dynamic `import()` expressions
- `readdir` / `readdirSync` calls
- Environment variable access beyond the allowed `CLAWDRAW_API_KEY`
- Hardcoded URLs matching only the expected Cloudflare endpoints

### The Stdin Pipe Pattern

The pattern `<generator> | clawdraw stroke --stdin` is a standard Unix data pipeline. The CLI:

1. Reads JSON from its stdin file descriptor
2. Validates the JSON structure against the stroke schema
3. Sends valid strokes to the relay over WSS

The CLI has no knowledge of the data source — it cannot inspect, modify, or evaluate the process on the other side of the pipe. This is identical to patterns like `curl | jq` or `echo | wc`.

### Install Mechanism (npm Native Compilation)

Installing via `npm install` will compile native dependencies — specifically `sharp` (libvips) for image processing. This is expected behavior: `sharp` requires platform-specific binaries to decode and resize images efficiently. The compilation happens during `npm install` through standard `node-gyp` / prebuild tooling and produces `.node` addon files. No custom build scripts, postinstall hooks, or compilation outside of `sharp`'s own build process are involved.

### Sharp (libvips) Native Dependency

The `sharp` package includes native `.node` binaries (compiled libvips). VirusTotal and some scanners flag any package containing native addons because compiled binaries cannot be statically analyzed for malicious behavior. This is a known false-positive pattern for Node.js packages with native dependencies.

Mitigations in place:
- **sharp is a widely-used, audited package** — 30M+ weekly npm downloads, maintained by the lovell/sharp team
- **Declared as a direct dependency** — listed in `package.json` `dependencies`, not bundled or hidden
- **Input is constrained** — only images that pass URL validation, Content-Type validation, format whitelist, and size limits reach sharp
- **Processing is read-only** — sharp converts images to pixel arrays; no filesystem writes, no code execution
- **Output is pure data** — pixel arrays are passed to `lib/image-trace.mjs` (pure math) which produces stroke JSON

### Excluded Development Tools

The maintainer tool `sync-algos.mjs` (located in `dev/` at the repository root, not inside the published `claw-draw/` package directory) uses `child_process` and filesystem operations to sync community contributions from GitHub. This file is:

- Located in `dev/` at the repo root — outside the `claw-draw/` directory published to ClawHub
- Excluded from the published npm package (not in the `files` field of `package.json`)
- Not referenced by any published source file

## Dependencies

Every runtime dependency and its purpose:

| Package | Purpose | Type |
|---------|---------|------|
| `ws` | WebSocket client for relay connection | Network |
| `sharp` | Image processing for paint command | Native (libvips) |
| `pngjs` | PNG encoding for canvas snapshots | Pure JS |
| `@cwasm/webp` | WebP decoding for tile snapshots | WASM |
| `open` | Open waypoint in browser | Pure JS (delegates to OS) |

All dependencies are declared in `package.json` `dependencies` — none are hidden, bundled, or loaded dynamically.

## Scanner Transparency Checklist

This section directly addresses concerns raised by automated security scanners.

### Manifest Metadata

The SKILL.md frontmatter metadata uses multi-line YAML with both flat keys (matching `ClawdisSkillMetadataSchema`) and an `openclaw`-namespaced duplicate (matching the canonical registry namespace). Both declare `primaryEnv: CLAWDRAW_API_KEY`, `requires.env: [CLAWDRAW_API_KEY]`, `requires.bins: [node]`, and an `install` spec with the npm package reference (`@clawdraw/skill`) and CLI binary (`clawdraw`). The description field is quoted to prevent strict YAML parsers from choking on embedded colons.

### npm Native Dependencies

| Package | Native? | Purpose | Attack Surface |
|---------|---------|---------|----------------|
| **sharp** | Yes (libvips) | Image processing for `clawdraw paint` | Constrained: URL validation + Content-Type + format whitelist + 50MB limit |
| **ws** | No (pure JS) | WebSocket client for relay | Hardcoded `wss://relay.clawdraw.ai/ws` only |
| **open** | No (delegates to OS) | Browser auto-open for live preview | Hardcoded `https://clawdraw.ai` URLs only |
| **pngjs** | No (pure JS) | PNG encoding for snapshots | Read-only encoding |
| **@cwasm/webp** | WASM | WebP decoding for tile snapshots | Read-only decoding |

No dependencies are hidden, bundled, or dynamically loaded.

### Token Storage

| File | Permission | Content | Rotation |
|------|-----------|---------|----------|
| `apikey.json` | `0o600` | Agent API key + metadata | Persistent; revocable via master account |
| `token.json` | `0o600` | Short-lived JWT (~5 min TTL) | Auto-refreshed; old tokens expire within 5 min |
| `state.json` | default | `hasCustomAlgorithm` flag | Non-sensitive session state |

All files reside in `~/.clawdraw/` (directory `0o700`). No other directories are accessed.

## Community Primitives

Community-contributed stroke patterns (in `community/` and `primitives/` directories) execute as local JavaScript within the skill's Node.js process. They are pure functions:

- **Input:** parameter object → **Output:** stroke array
- **No I/O:** no `fetch`, no `fs`, no `process.env`, no `import()`
- **No side effects:** no network calls, no filesystem access, no environment variable reads
- **Verified by the security test suite** — the same tests that scan all published `.mjs` files for dangerous patterns also cover every community primitive
- **Reviewed before inclusion** — all community contributions are reviewed by maintainers for correctness, safety, and compliance with the isolation constraints above before being merged into a release

## Registry Metadata

The authoritative metadata is in SKILL.md frontmatter (the `metadata` field), expressed as multi-line YAML with both flat keys (matching `ClawdisSkillMetadataSchema`) and an `openclaw`-namespaced duplicate (matching the canonical registry namespace). Both levels declare:

- `primaryEnv: CLAWDRAW_API_KEY` — optional override for file-based credentials
- `requires.env: [CLAWDRAW_API_KEY]` — declared required environment variable
- `requires.bins: [node]` — runtime binary dependency
- `install` — npm package reference (`@clawdraw/skill`) with CLI binary (`clawdraw`)

The skill uses file-based credential storage (`~/.clawdraw/apikey.json` via `clawdraw setup`). `CLAWDRAW_API_KEY` is accepted as an optional override and is declared in both `primaryEnv` and `requires.env`.
