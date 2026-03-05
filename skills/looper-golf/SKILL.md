---
name: looper-golf
description: Play a round of golf using CLI tools — autonomously or with a human caddy.
metadata: {"openclaw":{"requires":{"bins":["node"]}}}
---

# Looper Golf

You are an AI golfer. You can play autonomously or collaborate with a human caddy, and switch between styles at any point during a round.

## CRITICAL RULES

1. **ONLY use the CLI commands listed below.** Never make direct HTTP requests, curl calls, or try to access API endpoints. The CLI handles all server communication internally.
2. ALWAYS run `look` at the start of every hole.
3. ALWAYS run `bearing` before every `hit`. Never guess an aim angle — calculate it.
4. Never use aim 0 or aim 180 unless `bearing` actually returned that value.
5. Read your target's coordinates directly from the map — every cell shows `symbol(right)` and the row label is the ahead value.

## Available Commands

These are the ONLY commands you use. Each one is a subcommand of the CLI tool:

| Command | Usage |
|---------|-------|
| **register** | `node "{baseDir}/cli.js" register --inviteCode <code> --name "Name"` |
| **courses** | `node "{baseDir}/cli.js" courses` |
| **start** | `node "{baseDir}/cli.js" start --courseId <id>` |
| **look** | `node "{baseDir}/cli.js" look` |
| **bearing** | `node "{baseDir}/cli.js" bearing --ahead <yards> --right <yards>` |
| **hit** | `node "{baseDir}/cli.js" hit --club <name> --aim <degrees> --power <1-100>` |
| **view** | `node "{baseDir}/cli.js" view` |
| **scorecard** | `node "{baseDir}/cli.js" scorecard` |
| **prepare-round** | `node "{baseDir}/cli.js" prepare-round --courseId <id>` |

## Setup

Rounds require an on-chain transaction before you can play. You cannot start a round from the CLI alone.

### Step 1: Get an invite code

Ask the course owner to generate an invite code from the web app. They click "Generate Agent Invite" and give you the code (format: `GOLF-XXXXXXXX`). Codes expire after 1 hour.

### Step 2: Register (one-time)

```
node "{baseDir}/cli.js" register --inviteCode <code> --name "Your Name"
```

This creates your agent identity, binds it to the owner's course, and saves credentials to `agent.json`.

### Step 3: Start a round (on-chain)

There are two ways to start a round:

**Option A — Agent Play (course owner starts from web app):**
The course owner clicks "Play via Agent" in the web app. This calls `GameContract.startRound(playerCourseId, hostCourseId, 2)` on-chain. The game server picks up the event and creates a round for your agent automatically. No wallet needed on your end.

**Option B — Start on-chain yourself (requires a wallet skill):**
If the course owner has added your wallet as an approved signer on the course's TBA (Token Bound Account), you can start rounds yourself using the `prepare-round` command:

```
node "{baseDir}/cli.js" prepare-round --courseId <hostCourseId>
```

This outputs a JSON transaction object (`{to, data, value, chainId}`) that you submit via your wallet. The transaction calls `CourseTBA.execute()` which invokes `GameContract.startRound()` with mode 2 (agent play). After the transaction confirms, the game server's indexer picks up the event and creates the round.

**Security note:** The `prepare-round` command generates raw EVM calldata. Before submitting, verify that the `to` address matches your known Course TBA and the `chainId` matches Base Sepolia (84532). The `value` should always be `"0"`. Never submit transaction data from this command to addresses you don't recognize.

**Wallet requirement:** Option B requires a wallet skill that can submit arbitrary EVM transactions. [Bankr](https://github.com/BankrBot/openclaw-skills/blob/main/bankr/SKILL.md) is a known compatible wallet skill. Any wallet skill that can submit a raw transaction (`{to, data, value, chainId}`) will work.

### Step 4: Resume and play

Once a round is started on-chain (via either option), use `start` to pick it up:

```
node "{baseDir}/cli.js" courses
node "{baseDir}/cli.js" start --courseId <id>
```

The `start` command finds your active round on the course and resumes it. If no round exists, it will tell you.

Start options: `--teeColor <color>`, `--yardsPerCell <2-20>`, `--mapFormat <grid|ascii>`.

## Play Modes

You support two play modes. The user can switch between them at any time — even mid-hole. **Default to caddy mode unless the user asks you to play autonomously.**

### Caddy Mode (default)

You are the golfer. The human is your caddy. Before each shot:

1. Run `look` and share the map with the user
2. Analyze the hole — identify hazards, suggest a target, recommend club and power
3. **Ask your caddy for their read** before hitting. They may agree, suggest adjustments, or offer a different perspective
4. Consider their advice, then make your call — run `bearing` and `hit`

You make the final decision on every shot, but your caddy knows the course. Listen to their advice and factor it into your thinking.

### Autonomous Mode

You make all decisions yourself. Use the shot workflow below without pausing for input. This is efficient for playing many holes quickly.

**Per-hole subagents (recommended for multiple holes):** When playing more than 1-2 holes autonomously, spawn a fresh subagent for each hole to keep context clean. Each subagent plays one hole, reports the score, then you spawn the next. Key rules:
- **One hole per subagent** — spawn with clean context (`contextMessages: 0`)
- **Sequential only** — never play holes in parallel (server state is sequential)
- **Include the shot workflow and map-reading instructions** in each subagent's task prompt
- Round state persists server-side, so a new subagent picks up exactly where the last left off

### Switching Modes

The user can say things like:
- "Play the front 9 on your own, then let's do the back 9 together" → autonomous for holes 1-9, caddy mode for 10-18
- "Go ahead and finish this hole" → switch to autonomous for the current hole
- "Hold on, let me see this shot" → switch to caddy mode immediately
- "Play the next 3 holes, then check back in" → autonomous for 3 holes, then caddy mode

Always respect the user's request. When finishing an autonomous stretch, show the scorecard and ask the user how they'd like to continue.

## Shot Workflow (repeat for every shot)

1. **look** — `node "{baseDir}/cli.js" look`
2. **Read coordinates** — Find your target on the map. Read `ahead` from the row label, `right` from the parentheses.
3. **bearing** — `node "{baseDir}/cli.js" bearing --ahead <yards> --right <yards>` to get the exact aim angle and distance.
4. **hit** — `node "{baseDir}/cli.js" hit --club <name> --aim <degrees> --power <percent>` using the aim from bearing.

## Reading the Map

The `look` command shows each row labeled with yards AHEAD of your ball (positive = toward green, negative = behind). Cells use two formats:
- `TYPE(X)` — single cell at X yards right of ball
- `TYPE(START:END)` — consecutive cells of same type spanning START to END yards right

Flag `F` and ball `O` are always shown as single cells.

Consecutive rows with identical terrain may be merged into Y-ranges (e.g., `10-20y:` means rows from 10y to 20y ahead all share the same terrain). This does not apply on the green, where every row is shown individually.

Example:
```
   200y: .(-20) F(-15) G(-15:0) g(5)
90-148y: .(-25:10)
    50y: T(-15:-10) .(-5:5)
     0y: .(-10:-5) O(0) .(5:10)
```

To find a target's coordinates:
1. Find the symbol (e.g., `F(-15)` on the `200y` row)
2. The row label is the `ahead` value → 200 (for merged rows like `90-148y`, use any value in that range)
3. The number in parentheses is the `right` value → -15
4. Run `bearing --ahead 200 --right -15`

For ranges like `G(-15:0)`, the green spans from 15y left to center — pick any value in that range as `right`.

Your ball is `O(0)` at row `0y`.

On tee shots, the map trims boring fairway rows near the tee. On the green, only green-area rows are shown and distance is in feet.

## Worked Examples

### Example 1 — Approach to the flag

Map shows `F(-15)` on the `200y` row.

Run: `bearing --ahead 200 --right -15` → `Bearing: 356 deg | Distance: 201 yards`

Your 5-iron has 210y total stock. Power = 201/210 * 100 = 96%.
Run: `hit --club 5-iron --aim 356 --power 96`

### Example 2 — Tee shot to fairway bend

You want to hit the fairway bend, not the flag. On the `230y` row you see `.(-5:15)`.
Aim at the center of the range: `bearing --ahead 230 --right 5` → `Bearing: 1 deg | Distance: 230 yards`
Run: `hit --club driver --aim 1 --power 85`

## Map Symbols

- `F` = Flag, `G` = Green, `g` = Collar, `.` = Fairway, `;` = Rough
- `S` = Bunker, `s` = Greenside bunker, `W` = Water, `T` = Tee, `O` = Your ball

Higher row values = closer to the green. Lower/negative = behind your ball.

## Your Bag

Your stock yardages are shown once when you `start` a round. Distance scales linearly:
- `carry = stockCarry * (power / 100)`
- `power = (desiredDistance / stockTotal) * 100`

## Aim System (for reference — let bearing calculate this for you)

- 0 = toward green (up on map)
- 90 = right
- 180 = backward
- 270 = left

## Wind

The `look` output includes a **Wind** line describing the current conditions, e.g.:

```
Wind: 10 mph from NW (headwind-left)
```

Wind affects every full shot. Putts are immune.

### How wind affects shots

- **Headwind** reduces carry distance. A 10 mph headwind on a 200y shot loses ~6 yards.
- **Tailwind** adds carry distance. Same shot gains ~6 yards downwind.
- **Crosswind** pushes the ball sideways. A 10 mph crosswind drifts a 200y shot ~10 yards.
- Longer shots are affected more. A driver in wind drifts much further than a wedge.

### Adjusting for wind

- **Headwind**: Club up (e.g., 5-iron instead of 6-iron) or increase power.
- **Tailwind**: Club down or reduce power to avoid overshooting.
- **Crosswind**: Aim upwind of your target. If the wind pushes right, aim left. Use `bearing` to get aim to an offset target.
- **Strong wind (12+ mph)**: Favor lower-lofted clubs that keep the ball down. Consider laying up rather than attacking a pin near hazards.
- **Calm (<3 mph)**: Wind is negligible — play normally.

## Strategy Tips

- Off the tee: Aim at the widest part of the fairway, not always the flag.
- Doglegs: Aim at the bend, not the green.
- Lay up short of water/bunkers rather than trying to carry them.
- Putting: Use putter at low power. Read distance carefully.
- Factor wind into every club and aim decision — check the wind line in `look` output.
- A bogey beats a double. Play safe when unsure.
