# OpenClaw Minecraft Cron Prompt (every 30 seconds)

Follow these steps on each cron-triggered agent turn.

Allowed actions (use only these):
`chat`, `move_to`, `move_relative`, `move`, `dig`, `place`, `equip`, `use_item`, `attack`, `follow`, `jump`.

Action schemas (params + mode rules):
- `chat`: `{"message":"..."}`. Mode: `once` (or `loop` with `intervalMs` + `maxIterations`).
- `move_to`: `{"x":10,"y":64,"z":-12}`. Mode: `until` requires `stopCondition` (e.g., `{"type":"reach_position","radius":1.5}`) and `timeoutMs`.
- `move_relative`: `{"forward":2,"durationMs":800}` or `{"back":1,"durationMs":400}`. Mode: `once` (or `loop`). Do NOT use `dx/dy/dz`.
- `move`: `{"forward":true,"durationMs":250}` (booleans or numbers). Mode: `once` (or `loop`).
- `dig`: `{"x":10,"y":64,"z":-12}`. Mode: `once` (or `loop`).
- `place`: `{"x":10,"y":64,"z":-12,"item":"minecraft:stone"}`. Mode: `once` (or `loop`).
- `equip`: `{"item":"minecraft:iron_pickaxe","slot":"hand"}`. Mode: `once`.
- `use_item`: `{"hand":"main"}`. Mode: `once` (or `loop`).
- `attack`: `{"target":"nearest"}` or `{"target":"player:steve"}`. Mode: `once` (or `loop`).
- `follow`: `{"target":"player:steve","distance":3}`. Mode: `once` (or `loop`).
- `jump`: `{"durationMs":250}`. Mode: `once` (or `loop`).

0. Auth + bot context (every tick):
   - Load `memory/mc-auth.json` and read `accessToken`.
   - Use `Authorization: Bearer <accessToken>` for **all** API requests.
   - Load `memory/mc-bot.json` and read `botId`.
   - Use that `botId` in all `/v1/bots/{botId}/...` URLs (never leave it blank).
   - Base URL: `https://56eb-125-246-120-211.ngrok-free.app/v1`.
   - If token or botId is missing, stop and report the exact reason.
   - Cron environment note: do NOT use `jq` or `python` (not available).
   - If JSON parsing is needed, use `node -e` instead.
1. Observe: `GET /v1/bots/{botId}/state`.
   - `nearby` is an object: `{ "entities": [...], "blocks": [...] }` (not an array).
2. Busy check: ONLY treat as busy if `metadata.currentTaskId` is a non-empty string OR `metadata.queueLength` > 0.
   - If busy, wait 2 seconds and end this cycle.
   - If `currentTaskId` is `null`/empty and `queueLength` is 0, you MUST continue to steps 3-6 in order. Do not stop early.
3. Plan: decide an action bundle (5 to 10 steps) based on `nearby`, `health`, `hunger`, and persona `priorityRules`.
   - If the previous bundle failed, choose a safer fallback bundle.
   - If you cannot find enough actions, use safe fillers (`move_relative`, `move`, `jump`, `chat`) to reach 5 steps.
4. Build a batch action list:
   - First action is a chat announce using persona `chatTemplate`, e.g., `[plan][carpenter] {plan}`.
   - Then append each action step in order.
   - `mode: "until"` is only allowed for `move_to` and must include `stopCondition`.
   - For `chat`, `jump`, `move`, `move_relative`, use `mode: "once"` (or `loop` with `intervalMs` + `maxIterations`).
5. Submit the batch in one call:
   - `POST /v1/bots/{botId}/act-batch` with `{ "actions": [ ... ] }`.
   - Use `mode: until` or `mode: loop` and set `timeoutMs` per action.
   - If a step fails, stop the remaining steps and use a fallback bundle next cycle.
6. Log decisions in `memory/mc-autonomy.json` with timestamps.

Example 10-step bundle:
1) move_to (nearest tree)
2) dig (tree block)
3) dig (tree block)
4) move_to (next tree)
5) dig (tree block)
6) move_to (safe point)
7) place (crafting table)
8) equip (tool)
9) move_to (resource)
10) dig (resource)

## Decision Hints
- If health is low, move to a safe spot and end the cycle.
- If idle, explore by moving to a nearby random point.
- If interesting blocks are nearby, move closer and inspect.
- Avoid spamming actions; one batch per cycle.
