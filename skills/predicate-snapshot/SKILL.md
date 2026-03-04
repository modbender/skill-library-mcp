---
name: predicate-snapshot
description: ML-powered DOM pruning for 95% smaller browser prompts
homepage: https://predicate.systems/skills/snapshot
user-invocable: true
command-dispatch: tool
command-tool: predicate-snapshot
---

# Predicate Snapshot Engine

Replaces default browser snapshots with Predicate's ML-ranked DOM elements.
Reduces prompt token usage by **95%** while preserving actionable elements.

## Why Use This?

| Approach | Tokens | Elements | Signal Quality |
|----------|--------|----------|----------------|
| Accessibility Tree (default) | ~18,000 | ~800 | Low (noise) |
| Predicate Snapshot | ~800 | 50 | High (ranked) |

**Result:** Faster LLM inference, lower costs, fewer retries.

## Requirements

- Node.js 18+
- `PREDICATE_API_KEY` environment variable (optional)

**Without API key:** Local heuristic-based pruning (~80% token reduction)
**With API key:** ML-powered ranking for cleaner output (~95% token reduction, less noise)

Get your free API key at [predicate.systems/keys](https://predicate.systems/keys)

## Installation

```bash
npx clawdhub@latest install predicate-snapshot
```

Or manually:

```bash
git clone https://github.com/predicate-systems/predicate-snapshot-skill ~/.openclaw/skills/predicate-snapshot
cd ~/.openclaw/skills/predicate-snapshot && npm install && npm run build
```

## Configuration

For enhanced ML-powered ranking, set your API key:

```bash
export PREDICATE_API_KEY="sk-..."
```

Or configure in `~/.openclaw/config.yaml`:

```yaml
skills:
  predicate-snapshot:
    api_key: "sk-..."
    # Optional: set usage limits
    max_credits_per_session: 100
```

## Usage

### `/predicate-snapshot`

Capture a pruned DOM snapshot optimized for LLM consumption.

```
/predicate-snapshot [--limit=50] [--include-ordinal]
```

**Options:**
- `--limit=N` - Maximum elements to return (default: 50)
- `--include-ordinal` - Include ordinal ranking for list items

**Output format:**

```
ID|role|text|imp|is_primary|docYq|ord|DG|href
42|button|Add to Cart|0.95|true|320|1|cart-actions|
15|button|Buy Now|0.92|true|340|2|cart-actions|
23|link|Product Details|0.78|false|400|0||/dp/...
```

### `/predicate-act`

Execute an action on an element by its Predicate ID.

```
/predicate-act <action> <element_id> [value]
```

**Examples:**

```bash
# Click element 42
/predicate-act click 42

# Type into element 15
/predicate-act type 15 "search query"

# Scroll to element 23
/predicate-act scroll 23
```

### `/predicate-snapshot-local`

Local-only snapshot without ML re-ranking (free, lower accuracy).

```
/predicate-snapshot-local [--limit=50]
```

Use this for development or when you don't need ML-powered ranking.

## Example Workflow

```
1. Navigate to page
2. /predicate-snapshot          # Get ranked elements
3. /predicate-act click 42      # Click "Add to Cart" (element 42)
4. /predicate-snapshot          # Refresh snapshot
5. Verify cart updated
```

## Pricing

| Tier | Credits/Month | Price |
|------|---------------|-------|
| Hobby | 500 | Free |
| Builder | 20,000 | $19/mo |
| Pro | 40,000 | $49/mo |
| Teams | 120,000 | $149/mo |
| Enterprise | Custom | Contact us |

Each snapshot consumes 1 credit. Local snapshots are free.

## Comparison: Before & After

**Before (Accessibility Tree):**
```
@e1 navigation "Skip to main content"
@e2 link "Amazon"
@e3 search "Search Amazon"
... (800+ elements)
@e742 button "Add to Cart"  <-- buried in noise
... (more elements)
```

**After (Predicate Snapshot):**
```
ID|role|text|imp|is_primary|docYq|ord|DG|href
42|button|Add to Cart|0.98|true|520|1|cart-actions|  <-- ranked #1
15|button|Buy Now|0.95|true|540|2|cart-actions|
23|link|See All Buying...|0.72|false|560|3|cart-actions|
```

## Support

- Documentation: [predicatesystems.ai/docs](https://predicatesystems.ai/docs)
- Issues: [GitHub Issues](https://github.com/predicate-systems/predicate-snapshot-skill/issues)
- Discord: [Predicate Community](https://discord.gg/predicate)
