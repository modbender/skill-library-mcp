# Predicate Snapshot Skill for OpenClaw

ML-powered DOM pruning that reduces browser prompt tokens by **up to 99.8%** while preserving actionable elements.

## Quick Start

### 1. Install the Skill

**Via ClawHub (Recommended):**
```bash
npx clawdhub@latest install predicate-snapshot
```

**Manual Installation:**
```bash
git clone https://github.com/PredicateSystems/openclaw-predicate-skill ~/.openclaw/skills/predicate-snapshot
cd ~/.openclaw/skills/predicate-snapshot
npm install
npm run build
```

### 2. Get Your API Key (Optional)

For ML-powered ranking (95% token reduction), get a free API key:

1. Go to [PredicateSystems.ai](https://www.PredicateSystems.ai)
2. Sign up for a **free account (includes 500 free credits/month)**
3. Navigate to **Dashboard > API Keys**
4. Click **Create New Key** and copy your key (starts with `sk-...`)

**Without API key:** Local heuristic-based pruning (~80% token reduction)
**With API key:** ML-powered ranking for cleaner output (~95% token reduction)

### 3. Configure the API Key

**Option A: Environment Variable (Recommended)**
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc.)
export PREDICATE_API_KEY="sk-your-key-here"
```

**Option B: OpenClaw Config File**

Add to `~/.openclaw/config.yaml`:
```yaml
skills:
  predicate-snapshot:
    api_key: "sk-your-key-here"
    max_credits_per_session: 100  # Optional: limit credits per session
```

### 4. Use the Skill

```bash
# In OpenClaw:
/predicate-snapshot              # Get ranked elements
/predicate-act click 42          # Click element by ID
/predicate-snapshot-local        # Free local mode (no API)
```

## Overview

This OpenClaw skill replaces the default accessibility tree snapshot with Predicate's ML-ranked DOM elements. Instead of sending 800+ elements (~18,000 tokens) to the LLM, it sends only the 50 most relevant elements (configurable) (~500 tokens).

### Real-World Demo Results

Tested with the included demo (`npm run demo`):

| Site | OpenClaw Snapshot (A11y Tree) | Predicate Snapshot | Savings |
|------|-----------|-----------|---------|
| slickdeals.net | 598,301 tokens (24,567 elements) | 1,283 tokens (50 elements) | **99.8%** |
| news.ycombinator.com | 16,484 tokens (681 elements) | 587 tokens (50 elements) | **96%** |
| example.com | 305 tokens (12 elements) | 164 tokens (4 elements) | **46%** |
| httpbin.org/html | 1,590 tokens (34 elements) | 164 tokens (4 elements) | **90%** |
| **Total** | **616,680 tokens** | **2,198 tokens** | **99.6%** |

> Ad-heavy sites like slickdeals.net show the most dramatic savings—from 598K tokens down to just 1.3K tokens. Simple pages like example.com have minimal elements, so savings are lower.

### Why Fewer Elements Is Better

You might wonder: "Isn't 50 elements vs 24,567 elements comparing apples to oranges?"

**No—and here's why:**

1. **Most elements are noise.** Of those 24,567 elements on slickdeals.net, the vast majority are:
   - Ad iframes and tracking pixels
   - Hidden elements and overlays
   - Decorative containers (`<div>`, `<span>`)
   - Non-interactive text nodes
   - Duplicate/redundant elements

2. **LLMs need actionable elements and enough context to reason.** For browser automation, the agent needs to:
   - Click buttons and links
   - Fill form fields
   - Read key content for decision-making

   Predicate's ML ranking identifies the ~50 most relevant elements—including both interactive controls and contextual text—while filtering out the noise.

3. **More elements = worse performance.** Sending 600K tokens to an LLM causes:
   - Higher latency (slower responses)
   - Higher cost ($11K+/month vs $5/month)
   - Context window overflow on complex pages
   - More hallucinations from irrelevant context

4. **Quality over quantity.** Predicate's snapshot includes:
   - ML-ranked importance scores
   - Dominant group detection (for ordinal tasks like "click 3rd item")
   - Visual cues (is_primary, position)
   - Semantic role information

   This structured context helps LLMs make better decisions than a raw element dump.

**The goal isn't to preserve all elements—it's to preserve the right elements.**

### Proven in Production

- **Small local LLM model (3B) success**: The Predicate Snapshot engine powered a complex browser automation task using only a 3B parameter local model—[featured on Hacker News front page](https://news.ycombinator.com/item?id=46790127)
- **Deep dive**: Read why the accessibility tree alone isn't enough for web automation: [Why A11y Alone Isn't Enough](https://predicatesystems.ai/blog/why-ax-alone-isnt-enough)

### Summary

| Approach | Tokens (avg) | Elements | Signal Quality |
|----------|--------|----------|----------------|
| Accessibility Tree | ~150,000+ | ~6,000+ | Low (noise) |
| Predicate Snapshot | ~500-1,300 | 50 | High (ML-ranked) |

## How It Works

### Does This Replace the Default A11y Tree?

**No, this skill does not automatically replace OpenClaw's default accessibility tree.** Instead, it provides an alternative snapshot command that you can use when you want better element ranking.

| Command | What It Does |
|---------|--------------|
| Default OpenClaw | Uses raw accessibility tree (~18,000 tokens) |
| `/predicate-snapshot` | Uses ML-ranked Predicate snapshot (~500 tokens) |
| `/predicate-snapshot-local` | Uses local heuristic ranking (free, no API) |

**To use Predicate snapshots in your workflow:**
1. Use `/predicate-snapshot` instead of the default page observation
2. Use `/predicate-act click <ID>` to interact with elements by their ID
3. The element IDs from Predicate snapshots work with `/predicate-act`

**Future:** OpenClaw may add configuration to set Predicate as the default snapshot provider.

---

## ⚡ Usage with Autonomous Agents

> **Important:** OpenClaw agents work autonomously—they don't wait for manual slash commands. Here's how to integrate Predicate snapshots into autonomous workflows.

### Option 1: Include in Task Instructions (Recommended)

Add Predicate snapshot instructions directly in your task prompt:

```
Navigate to amazon.com and find the cheapest laptop under $500.

IMPORTANT: For page observation, use /predicate-snapshot instead of the
default accessibility tree. Use /predicate-act to interact with elements
by their ID from the snapshot.
```

### Option 2: Modify Agent System Prompt

For consistent usage across all tasks, add to your agent's system prompt:

```
## Browser Observation
When observing web pages, always use /predicate-snapshot instead of the
default accessibility tree. This provides ML-ranked elements optimized
for efficient decision-making (~500 tokens vs ~18,000 tokens).

To interact with page elements:
1. Call /predicate-snapshot to get ranked elements with IDs
2. Call /predicate-act <action> <element_id> to perform actions
```

### Option 3: OpenClaw Config (Future)

OpenClaw may add support for setting the default snapshot provider:

```yaml
# ~/.openclaw/config.yaml (proposed future feature)
browser:
  snapshot_provider: predicate-snapshot
```

### Why This Matters

Without explicit instructions, the agent will use OpenClaw's default accessibility tree, which:
- Sends ~18,000 tokens per page observation
- Includes thousands of irrelevant elements
- Costs more and runs slower

By instructing the agent to use `/predicate-snapshot`, you get:
- ~500 tokens per observation (97% reduction)
- Only the 50 most relevant elements
- Faster, cheaper, more accurate automation

---

## Usage

### Capture Snapshot

```
/predicate-snapshot [--limit=50] [--include-ordinal]
```

Returns a pipe-delimited table of ranked elements:

```
ID|role|text|imp|is_primary|docYq|ord|DG|href
42|button|Add to Cart|0.95|true|320|1|cart-actions|
15|button|Buy Now|0.92|true|340|2|cart-actions|
23|link|Product Details|0.78|false|400|0||/dp/...
```

### Execute Actions

```bash
/predicate-act click 42        # Click element by ID
/predicate-act type 15 "query" # Type into element
/predicate-act scroll 23       # Scroll to element
```

### Local Mode (Free)

```
/predicate-snapshot-local [--limit=50]
```

Uses heuristic ranking without ML API calls. Lower accuracy but no credits consumed.

## Example Workflow

```
1. /predicate-snapshot              # Get ranked elements
2. /predicate-act click 42          # Click "Add to Cart"
3. /predicate-snapshot              # Refresh after action
4. Verify cart updated
```

## Output Format

| Column | Description |
|--------|-------------|
| ID | Unique element identifier for `/predicate-act` |
| role | ARIA role (button, link, textbox, etc.) |
| text | Visible text content (truncated to 30 chars) |
| imp | Importance score (0.0-1.0, ML-ranked) |
| is_primary | Whether element is a primary action |
| docYq | Vertical position in document |
| ord | Ordinal within dominant group |
| DG | Dominant group identifier |
| href | Link URL if applicable |

Each ML-powered snapshot consumes 1 credit. Local snapshots are free.

## Development

### Run in Docker (Recommended for Safe Testing)

Docker provides an **isolated environment** for testing browser automation—no risk to your local machine, browser profiles, or credentials.

```bash
cd predicate-snapshot-skill

# Run the skill MCP tools test (no API keys required)
./docker-test.sh skill

# Run the login demo (requires LLM API key)
./docker-test.sh demo:login
```

**Test options:**

| Command | What it tests | API Keys Required? |
|---------|---------------|-------------------|
| `./docker-test.sh` | Skill MCP tools & browser integration | No |
| `./docker-test.sh skill` | Same as above (explicit) | No |
| `./docker-test.sh openclaw` | OpenClaw full runtime integration | No |
| `./docker-test.sh demo:login` | Full 6-step login workflow | Yes (LLM) |
| `./docker-test.sh demo` | Basic token comparison | Yes (LLM) |

**Passing API Keys:**

The `demo:login` and `demo` tests require at least one LLM API key (OpenAI or Anthropic) for element selection:

```bash
# Option 1: Export environment variables
export OPENAI_API_KEY="sk-..."          # OpenAI API key
export ANTHROPIC_API_KEY="sk-ant-..."   # OR Anthropic API key
export PREDICATE_API_KEY="sk-..."       # Optional: for ML-ranked snapshots

./docker-test.sh demo:login

# Option 2: Inline (single command)
OPENAI_API_KEY="sk-..." PREDICATE_API_KEY="sk-..." ./docker-test.sh demo:login

# Option 3: Using docker-compose with .env file
# Create a .env file with your keys:
echo "OPENAI_API_KEY=sk-..." >> .env
echo "PREDICATE_API_KEY=sk-..." >> .env
docker-compose up demo-login
```

| API Key | Required? | Purpose |
|---------|-----------|---------|
| `OPENAI_API_KEY` | One of these required | LLM for element selection |
| `ANTHROPIC_API_KEY` | One of these required | LLM for element selection |
| `PREDICATE_API_KEY` | Optional | ML-ranked snapshots (reduces noise & tokens) |

**Why Docker is safer:**

| Concern | Docker Isolation |
|---------|------------------|
| Browser profile | Fresh Chromium instance, no cookies or history |
| Network traffic | Contained, won't trigger corporate firewalls |
| File system | Only `./test-output/` is mounted |
| Credentials | None stored—test site uses fake credentials |

**Using docker-compose:**

```bash
docker-compose up skill-test      # Skill MCP tools test
docker-compose up openclaw-test   # OpenClaw full runtime test
docker-compose up demo-login      # Login demo
```

The test uses a purpose-built test site (`https://www.localllamaland.com/login`) with fake credentials (`testuser` / `password123`)—no real accounts involved.

### Run Demo (Local)

Compare token usage between accessibility tree and Predicate snapshot:

Get free credits for testing at https://www.PredicateSystems.ai

```bash
# With API key (REAL ML-ranked snapshots)
PREDICATE_API_KEY=sk-... npm run demo

# Without API key (uses extension's local ranking)
npm run demo
```

Example output:
```
======================================================================
 TOKEN USAGE COMPARISON: Accessibility Tree vs. Predicate Snapshot
======================================================================
 Mode: PredicateBrowser with extension loaded
 Snapshots: REAL (API key detected)
======================================================================

Analyzing: https://news.ycombinator.com
  Capturing accessibility tree...
  Capturing Predicate snapshot (REAL - ML-ranked via API)...

======================================================================
 RESULTS
======================================================================

news.ycombinator.com (REAL)
  +---------------------------------------------------------+
  | Accessibility Tree:   16,484 tokens (681 elements)      |
  | Predicate Snapshot:      587 tokens (50 elements)       |
  | Savings:                  96%                           |
  +---------------------------------------------------------+

======================================================================
 TOTAL: 616,680 -> 2,198 tokens (99.6% reduction)
======================================================================

 MONTHLY COST PROJECTION (5,000 tasks × 5 snapshots = 25,000 snapshots)
   Accessibility Tree: $11,562.75 (LLM tokens only)
   Predicate Snapshot: $5.12 ($1.37 LLM + $3.75 API)
   Monthly Savings:    $11,557.63
```

### Run Login Demo (Multi-Step Workflow)

This demo demonstrates real-world browser automation with a **6-step login workflow**:

1. Navigate to login page and wait for delayed hydration
2. Fill username field (LLM selects element + human-like typing)
3. Fill password field (button state: disabled → enabled)
4. Click login button
5. Navigate to profile page
6. Extract username from profile card

![Local Llama Land Login Form with Predicate Overlay](demo/localLlamaLand_demo.png)

*The Predicate overlay shows ML-ranked element IDs (green borders) that the LLM uses to select form fields.*

Target site: `https://www.localllamaland.com/login` - a test site with intentional challenges:
- **Delayed hydration**: Form loads after ~600ms (SPA pattern)
- **State transitions**: Login button disabled until both fields filled
- **Late-loading content**: Profile card loads after 800-1200ms

**Setup:**

1. Copy the example env file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```bash
# .env
OPENAI_API_KEY=sk-your-openai-api-key-here

# Optional: for ML-ranked snapshots
PREDICATE_API_KEY=sk-your-predicate-api-key-here
```

3. Run the demo with visible browser and element overlay:
```bash
npm run demo:login -- --headed --overlay
```

**Alternative LLM providers:**
```bash
# Anthropic Claude
ANTHROPIC_API_KEY=sk-... npm run demo:login -- --headed --overlay

# Local LLM (Ollama)
SENTIENCE_LOCAL_LLM_BASE_URL=http://localhost:11434/v1 npm run demo:login -- --headed --overlay

# Headless mode (no browser window)
npm run demo:login
```

**Flags:**
- `--headed` - Run browser in visible window (not headless)
- `--overlay` - Show green borders around captured elements (requires `--headed`)

This demo compares A11y Tree vs Predicate Snapshot across **all 6 steps**, measuring:
- **Tokens per step**: Input size for each LLM call
- **Latency**: Time per step including form interactions
- **Success rate**: Step completion across the workflow

#### Key Observations

| Metric | OpenClaw A11y Tree Snapshot | Predicate Snapshot | Delta |
|--------|-----------|-------------------|-------|
| **Steps Completed** | 6/6 | **6/6** | Both pass |
| **Total Tokens** | 5,366 | **1,565** | **-71%** |
| **Token Savings** | baseline | **67-74% per step** | Significant |

**Why Predicate Snapshot is better:**

1. **Dramatic token reduction**: 71% fewer tokens across the entire workflow (5,366 → 1,565 tokens)
2. **ML-ranked elements**: Only the most relevant interactable elements are included with enough context, reducing noise
3. **Stable identifiers**: `data-predicate-id` attributes survive SPA re-renders
4. **`runtime.check().eventually()`**: Properly waits for SPA hydration before capturing snapshots

#### Raw Demo Logs

Full Docker demo output: [pastebin.com/ksETcQ4C](https://pastebin.com/ksETcQ4C)

<details>
<summary>Click to expand results summary</summary>

```
======================================================================
 RESULTS SUMMARY
======================================================================

+-----------------------------------------------------------------------+
| Metric              | A11y Tree        | Predicate        | Delta     |
+-----------------------------------------------------------------------+
| Total Tokens        |             5366 |             1565 | -71%      |
| Total Latency (ms)  |            51675 |            75555 | +46%      |
| Steps Passed        |              6/6 |              6/6 |           |
+-----------------------------------------------------------------------+

Key Insight: Predicate snapshots use 71% fewer tokens
for a multi-step login workflow with form filling.

Step-by-step breakdown:
----------------------------------------------------------------------
Step 1: Wait for login form hydration
  A11y: 0 tokens, 12060ms, PASS
  Pred: 0 tokens, 10792ms, PASS (0% savings)
Step 2: Fill username field
  A11y: 1251 tokens, 7613ms, PASS
  Pred: 361 tokens, 12324ms, PASS (71% savings)
Step 3: Fill password field
  A11y: 1305 tokens, 13691ms, PASS
  Pred: 362 tokens, 18410ms, PASS (72% savings)
Step 4: Click login button
  A11y: 1377 tokens, 7909ms, PASS
  Pred: 362 tokens, 13233ms, PASS (74% savings)
Step 5: Navigate to profile page
  A11y: 0 tokens, 1ms, PASS
  Pred: 0 tokens, 0ms, PASS (0% savings)
Step 6: Extract username from profile
  A11y: 1433 tokens, 10401ms, PASS
  Pred: 480 tokens, 20796ms, PASS (67% savings)
```

</details>

#### Summary

| Step | A11y Tree | Predicate Snapshot | Token Savings |
|------|-----------|-------------------|---------------|
| Step 1: Wait for login form hydration | PASS | PASS | - |
| Step 2: Fill username | 1,251 tokens, PASS | 361 tokens, PASS | **71%** |
| Step 3: Fill password | 1,305 tokens, PASS | 362 tokens, PASS | **72%** |
| Step 4: Click login | 1,377 tokens, PASS | 362 tokens, PASS | **74%** |
| Step 5: Navigate to profile | PASS | PASS | - |
| Step 6: Extract username | 1,433 tokens, PASS | 480 tokens, PASS | **67%** |
| **Total** | **5,366 tokens, 6/6 steps** | **1,565 tokens, 6/6 steps** | **71%** |

> **Key Insight:** Predicate Snapshot reduces tokens by **67-74% per step** while maintaining the same pass rate. For multi-step workflows, this translates to significant cost savings and faster LLM inference.

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

## Why Predicate Snapshot Over Accessibility Tree?

OpenClaw and similar browser automation frameworks default to the **Accessibility Tree (A11y)** for navigating websites. While A11y works for simple cases, it has fundamental limitations that make it unreliable for production LLM-driven automation:

### A11y Tree Limitations

| Problem | Description | Impact on LLM Agents |
|---------|-------------|----------------------|
| **Optimized for Consumption, Not Action** | A11y is designed for assistive technology (screen readers), not action verification or layout reasoning | Lacks precise semantic geometry and ordinality (e.g., "the first item in a list") that agents need for reliable reasoning |
| **Hydration Lag & Structural Inconsistency** | In JS-heavy SPAs, A11y often lags behind hydration or misrepresents dynamic overlays and grouping | Snapshots miss interactive nodes or incorrectly label states (e.g., confusing `focused` with `active`) |
| **Shadow DOM & Iframe Blind Spots** | A11y struggles to maintain global order across Shadow DOM and iframe boundaries | Cross-shadow ARIA delegation is inconsistent; iframe contents are often missing or lose spatial context |
| **Token Inefficiency** | Extracting the entire A11y tree for small actions wastes context window and compute | Superfluous nodes (like `genericContainer`) consume tokens without helping the agent |
| **Missing Visual/Layout Bugs** | A11y trees miss rendering-time issues like overlapping buttons or z-index conflicts | Agent reports elements as "correct" but cannot detect visual collisions |

### Predicate Snapshot Advantages

| Capability | How Predicate Solves It |
|------------|------------------------|
| **Post-Rendered Geometry** | Layers in actual bounding boxes and grouping missing from standard A11y representations |
| **Live DOM Synchronization** | Anchors on the live, post-rendered DOM ensuring perfect sync with actual page state |
| **Unified Cross-Boundary Grounding** | Rust/WASM engine prunes and ranks elements across Shadow DOM and iframes, maintaining unified element ordering |
| **Token-Efficient Pruning** | Specifically prunes uninformative branches while preserving all interactive elements, enabling 3B parameter models to perform at larger model levels |
| **Deterministic Verification** | Binds intent to deterministic outcomes via snapshot diff, providing an auditable "truth" layer rather than just a structural "report" |

> **Bottom Line:** A11y trees tell you what *should* be there. Predicate Snapshots tell you what *is* there—and prove it.

## Architecture

```
predicate-snapshot-skill/
├── src/
│   ├── index.ts      # MCP tool definitions
│   ├── snapshot.ts   # PredicateSnapshotTool implementation
│   └── act.ts        # PredicateActTool implementation
├── demo/
│   ├── compare.ts    # Token comparison demo
│   ├── llm-action.ts # Simple LLM action demo (single clicks)
│   └── login-demo.ts # Multi-step login workflow demo
├── SKILL.md          # OpenClaw skill manifest
└── package.json
```

## Dependencies

- `@predicatesystems/runtime` - Predicate SDK with PredicateContext
- `playwright` (peer) - Browser automation

## License

(MIT OR Apache-2.0)

## Support

- **ClawHub:** [clawhub.ai/rcholic/predicate-snapshot](https://clawhub.ai/rcholic/predicate-snapshot)
- **GitHub:** [github.com/PredicateSystems/openclaw-predicate-skill](https://github.com/PredicateSystems/openclaw-predicate-skill)
- **Documentation:** [predicatesystems.ai/docs](https://predicatesystems.ai/docs)
- **Issues:** [GitHub Issues](https://github.com/PredicateSystems/openclaw-predicate-skill/issues)
