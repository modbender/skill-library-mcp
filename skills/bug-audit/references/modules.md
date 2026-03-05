# Audit Modules

Read only the sections matching the project's type tags from Step 1.

## 🔒 S — Security (projects with user systems)

### S1 Input Validation
- SQL: all `prepare()` parameterized, no string concatenation
- XSS: frontend `esc()` + server-side strip `<>`
- Numbers: `parseInt` + `Math.max(0,...)` + upper clamp
- Array/object type check (prevent array params crashing server)
- Prototype pollution: lookup maps use `Object.create(null)`

### S2 Auth & Permissions
- Cookie: `Secure` + `SameSite=Lax`
- CORS: whitelist array, never `origin:true` (reflects any origin = critical vuln)
- Admin password via header, not GET query (query appears in nginx logs + browser history)
- Brute force protection: N failures → lock IP
- Password comparison: `crypto.timingSafeEqual`
- Admin grant endpoints: reject negative amounts

### S3 Infrastructure
- `express.json({limit:'100kb'})`
- `app.disable('x-powered-by')`
- Global error middleware (no stack traces to client)
- Socket.IO: `maxHttpBufferSize: 16384`
- Max connection limit (prevent DDoS entity creation)

---

## 📊 D — Data Consistency (projects with databases)

### D1 Atomic Operations
- Resource deduction: `SET x=x-? WHERE x>=?` (SQLite naturally prevents double-spend)
- Dedup: UNIQUE INDEX + INSERT OR IGNORE
- Float precision: `Math.floor()` safety net (JS float accumulation → 290402.0000000001)
- Cross-SQLite DB: cannot JOIN, query separately then merge
- SQLite strings: single quotes `''` (double quotes `""` = column identifiers, causes crashes)

### D2 Timezone
- `toISOString()` returns UTC! Chinese time: use `getFullYear/getMonth/getDate`
- Daily reset: Beijing midnight (not UTC midnight = Beijing 8am)
- China servers (Asia/Shanghai): no manual +8h needed
- SQLite: `datetime('now','localtime')` vs `datetime('now')`

### D3 Data Tool Specifics (📊 only)
- Feishu sheets: find by name, not index (write-back sheets push Sheet1 to higher index)
- DOU+ stat_cost: unit is fen (÷100 for yuan); is spend within specified date range, not cumulative
- fetch-report only updates orders with data in date range; use `_rfaBefore` timestamp to filter
- After fetch-report, run fetch-all once to catch missed new orders
- Data snapshot/backup mechanism for rollback

---

## ⚡ P — Performance (large or realtime projects)

### P1 Memory Leaks
- Every `setInterval` has matching `clearInterval`
- No destroy/splice during forEach (use `.slice()` snapshot — hit in 3+ projects)
- Game mode end: clean up all AI entities (timed/elimination/royale)
- Socket reconnect: don't stack timers (store ref + clear on disconnect)
- AudioNode: disconnect after stop (onended auto-disconnect)

### P2 Hot Path
- Cache DOM queries (not `getElementById` every frame — 12/frame = 720/sec)
- Config file: mtime cache (not readFileSync per request)
- Leaderboard: 60s memory cache (58 users × 6 SQL = 348 queries/request)
- Large lists: pagination

---

## 🎮 G — Game Logic (game projects only)

### G1 State Guards
- gameOver/endBattle: dedup flag + **reset flag in init** (otherwise 2nd battle never triggers!)
- battleState: correctly set back to `player_turn` in spirit-defeated→switch chain
- visibilitychange pause: needs state lock to prevent duplicate calls
- Physics engine: delta doesn't accumulate across tab switches

### G2 Anti-Cheat
- Rewards computed server-side (never trust client values: quest rewards, shop quantities, seal levels)
- Quest taskKey: whitelist validation (attacker fills progress with fake keys to bypass completion check)
- quest/start: check prerequisite quests (prevents chapter-skipping for high-tier rewards)
- Star-up/merge: validate rarity (R-grade used as SSR material)
- Tower/level skip: `floor > currentMax + 1` check
- Trade/gift/wish: daily limit (unlimited wish-wall = infinite gold exploit)
- Safe-box items: check ALL exit points (trade, gift, merge, sell, fuse)

### G3 Rendering & Interaction
- Phaser canvas as pure background: `pointer-events:none` + disable input (otherwise intercepts game touches)
- After display toggle: `requestAnimationFrame` before reading clientWidth/Height (may be 0 before reflow)
- Overlay: mutual exclusion (open A → close B) + click-outside to close
- Animation overlays: `pointer-events:none` (don't block game controls)
- Resize: rebuild physics walls
- Global touchmove preventDefault: whitelist selectors must match actual HTML
- Phaser camera: don't follow physics body directly (engine-level jitter bug, use lerp + separate position)
- Phaser container + setScrollFactor(0): click offset bug → use standalone elements + setDepth
- Multiple panels sharing DOM ID: clear innerHTML on switch
- `<img src="">`: browser requests current page URL → use inline SVG placeholder

### G4 Config Validation
- config.json values actually read in code (not just written — admin changes have no effect otherwise)
- Module load-time config reads get defaults (fetch not complete yet) → read at runtime
- Frontend hardcoded cost must match backend config (fragment exchange: frontend 50 ≠ backend 150)
- Admin config save: preserve password field (prevent loss if frontend omits it)

---

## 🔧 W — WeChat Compatibility (wechat projects only)

### W1 Syntax
- No ES6+: optional chaining `?.`, nullish coalescing `??`, computed property `{[key]:val}`
- No JS template literals (backticks cause issues with file-write tools)
- `backdrop-filter`: add `-webkit-` prefix
- `safe-area-inset` support (notch screens)

### W2 WeChat APIs
- OAuth callback URL + state parameter (distinguish sources like v2/v3)
- access_token: cache + auto-refresh (2h expiry)
- JS-SDK signature: use current page URL (not fixed URL)
- Image upload: use JPEG (large blank-area PNGs fail WeChat decode)

### W3 Environment
- CDN libraries: download to server (jsdelivr unreliable in China — curl returns HTTP 000/0 bytes)
- After replacing Phaser version: verify Matter.js API compatibility (3.80.1 removed Runner module)
- WeChat cache: add `?v=N` to all JS references (extremely sticky cache)
- Debugging: `navigator.sendBeacon` remote logging > screenshot debug panel (10x more efficient)

---

## 🔌 A — API Service (api-service projects only)

### A1 Interface Standards
- Unified error format: `{ok:false, error:"..."}`
- Parameter type validation
- Proper HTTP status codes (not all 200)
- Large file: streaming response

### A2 Auth & Rate Limiting
- API Key middleware
- Per-key or per-IP rate limiting
- Key revocation mechanism (whitelist)

### A3 External Dependencies
- Upstream API timeout fallback
- Degraded response (cache/defaults) when upstream is down
- Tunnel/proxy health check (e.g., Gemini image generation tunnel)

---

## 🤖 B — Bot (bot projects only)

### B1 Message Handling
- AI reply timeout fallback
- Duplicate message dedup (WeChat may resend)
- Sensitive word filter
- Friendly error replies (no technical details to users)

---

## 🚀 R — Deploy (all projects)

### R1 Basics
- PM2 online, no restart loop
- nginx proxy correct (sub-path prefix strip)
- HTTPS certificate valid
- Static assets: version `?v=N`

### R2 Deploy Safety
- SDK/init code not overwritten by deployment (5 games lost SDK init from deploy overwrite)
- Local vs server file SHA match
- After replacing dependency: verify API compatibility (`grep -c "Runner" phaser.min.js`)
