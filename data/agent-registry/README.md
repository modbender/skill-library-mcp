# Agent Registry

[![Version](https://img.shields.io/badge/version-2.0.1-blue)](https://github.com/MaTriXy/Agent-Registry/releases/tag/v2.0.1) [![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> **Lazy-loading system for Claude Code agents that reduces context window usage by 70-90%**

As your agent collection grows, Claude Code loads **every single agent** into every conversation.

With dozens or hundreds of agents installed, this creates token overhead that wastes your context window on agents you'll never use in that session.

**Agent Registry solves this** with on-demand loading: index your agents once, then load only what you need.

## The Problem

Claude Code's default behavior loads **all agents upfront** into every conversation:

- **Token overhead:** ~117 tokens per agent x agent count = wasted context
- **Scales poorly:** 50 agents = 5.8k, 150 agents = 17.5k, 300+ agents = 35k+ tokens
- **Context waste:** Typically only 1-3 agents are relevant per conversation
- **All or nothing:** You pay the full cost even if you use zero agents
- **Slow startup:** Processing hundreds of agent files delays conversation start

### Real-World Impact: Before & After

Here's the actual difference from a real Claude Code session with 140 agents:

<table>
<tr>
<td width="50%">

### Before: All Agents Loaded

![Before Agent Registry](docs/images/context-usage-before.png)

**Context consumption:**
- Custom agents: **16.4k tokens (8.2%)**
- Total: 76k/200k (38%)
- **Problem:** 14k tokens wasted on unused agents

</td>
<td width="50%">

### After: Agent Registry

![After Agent Registry](docs/images/context-usage-after.png)

**Context consumption:**
- Custom agents: **2.7k tokens (1.4%)**
- Total: 42k/200k (21%)
- **Savings:** 13.7k tokens freed = **83% reduction**

</td>
</tr>
</table>

**Bottom line:** Agent Registry **freed up 34k tokens** in total context (38% -> 21%), giving you **56% more free workspace** (79k -> 113k available) for your actual code and conversations.

> **Testing methodology:** Both screenshots were captured from the same repository in separate Claude Code sessions. Each session was started fresh using the `/clear` command to ensure zero existing context, providing accurate baseline measurements of agent-related token overhead.

## The Solution

**Agent Registry** shifts from **eager loading** to **lazy loading**:

```
Before: Load ALL agents -> Context Window -> Use 1-2 agents
        (~16-35k tokens)    (limited)      (~200-300 tokens)

        Wastes 90%+ of agent tokens on unused agents

After:  Search registry -> Load specific agent -> Use what you need
        (~2-4k tokens)   (instant)          (~200-300 tokens)

        Saves 70-90% of agent-related tokens
```

### Automatic Discovery (Hook)

A `UserPromptSubmit` hook makes agent discovery **fully automatic**. Every user prompt is analyzed by an in-process BM25 search engine (JavaScript, runs on Bun -- Claude Code's runtime). If high-confidence matches are found (score >= 0.5), they're injected as context before Claude responds.

```
User: "review my authentication code for security issues"

-> Hook finds: security-auditor (0.89), code-reviewer (0.71)
-> Claude sees suggestions in additionalContext
-> Loads the best match and follows its instructions
```

No manual search step. Runs in ~100ms. Fails silently on any error -- never blocks the user.

**The math (140 agents example):**
- **Before:** 16.4k tokens (all agents loaded)
- **After:** 2.7k tokens (registry index loaded, agents on-demand)
- **Savings:** 13.7k tokens saved -> **83% reduction**

**Scaling examples:**
- 50 agents: Save ~3-4k tokens (5.8k -> 2.5k) = 60-70% reduction
- 150 agents: Save ~14k tokens (17.5k -> 3k) = 80% reduction
- 300 agents: Save ~30k tokens (35k -> 3.5k) = 85-90% reduction

## What This Skill Provides

### Smart Search (BM25 + Keyword Matching)
Find agents by intent, not by name:
```bash
bun bin/search.js "code review security"
# Returns: security-auditor (0.89), code-reviewer (0.71)

bun bin/search-paged.js "backend api" --page 1 --page-size 10
# Paginated results for large agent collections
```

**Supported:**
- Intent-based search using BM25 algorithm
- Keyword matching with fuzzy matching
- Relevance scoring (0.0-1.0)
- Pagination for 100+ agent results
- JSON output mode for scripting

### Interactive Migration UI
Beautiful selection interface with advanced features:
- **Multi-level Select All:** Global, per-category, per-page selection
- **Pagination:** Automatic 10-item pages for large collections (100+ agents)
- **Visual indicators:** Color-coded token estimates (<1k, 1-3k, >3k)
- **Category grouping:** Auto-organized by subdirectory structure
- **Keyboard navigation:** Arrow keys navigate, Space toggle, Enter confirm
- **Selection persistence:** Selections preserved across page navigation
- **Graceful fallback:** Text input mode if @clack/prompts unavailable

**Supported:**
- Interactive checkbox UI with @clack/prompts
- Page-based navigation
- Finish selection workflow
- Text-based fallback mode

### Lightweight Index
Registry stores only metadata -- not full agent content:
- Agent name and summary
- Keywords for search matching
- Token estimates for capacity planning
- File paths for lazy loading
- Content hashes for change detection

**Index size scales slowly:**
- 50 agents = ~2k tokens
- 150 agents = ~3-4k tokens
- 300 agents = ~6-8k tokens

**Much smaller than loading all agents:**
- Traditional: ~117 tokens/agent x count
- Registry: ~20-25 tokens/agent in index

## Installation

### Prerequisites
- Bun (ships with Claude Code -- no separate installation needed)
- Git (for traditional installation)

### Method 1: Skills CLI (Recommended)

Install via Skills CLI (one command):
```bash
npx skills add MaTriXy/Agent-Registry@agent-registry
```

Discover skills interactively:
```bash
npx skills find
```

Update existing skills:
```bash
npx skills update
```

**Then run migration:**
```bash
cd ~/.claude/skills/agent-registry
bun bin/init.js
```

### Method 2: npm Install

```bash
npm install @claude-code/agent-registry
```

### Method 3: Traditional Install

Clone and install:
```bash
# Clone to Claude skills directory
git clone https://github.com/MaTriXy/Agent-Registry.git ~/.claude/skills/agent-registry

# Run installer
cd ~/.claude/skills/agent-registry
./install.sh
```

**What the installer does:**
1. Verifies installation directory
2. Creates registry structure (`references/`, `agents/`, `lib/`, `bin/`)
3. Optionally installs dependencies with `./install.sh --install-deps`

### Post-Installation

**All methods require migration:**
```bash
bun bin/init.js
```

This interactive wizard:
1. Scans your `~/.claude/agents/` directory
2. Shows all available agents with token estimates
3. Lets you select which agents to copy (or move with `--move`)
4. Builds the searchable registry index

### Migrate Your Agents

```bash
# Run interactive migration
bun bin/init.js

# Optional: destructive migration (moves source files)
bun bin/init.js --move
```

**Interactive selection modes:**

**With @clack/prompts** (default):
```
? Select agents to add to registry (arrow keys navigate, Space toggle, Enter confirm)
  ---------- FRONTEND ----------
> [x] react-expert - React specialist for modern component... [1850 tokens]
  [ ] angular-expert - Angular framework expert with... [3200 tokens]
  [ ] vue-expert - Vue.js specialist for reactive UIs... [750 tokens]
  ---------- BACKEND ----------
  [ ] django-expert - Django web framework specialist... [2100 tokens]
  [ ] fastapi-expert - FastAPI for high-performance APIs... [980 tokens]
```

**Without @clack/prompts** (fallback):
```
Select agents to add to the registry:
  Enter numbers separated by commas (e.g., 1,3,5)
  Enter 'all' to add all agents
```

## Usage

### The Search-First Pattern

Instead of Claude loading all agents, use this pattern:

```bash
# 1. User asks: "Can you review my authentication code for security issues?"

# 2. Search for relevant agents
bun bin/search.js "code review security authentication"

# Output:
# Found 2 matching agents:
#   1. security-auditor (score: 0.89) - Analyzes code for security vulnerabilities
#   2. code-reviewer (score: 0.71) - General code review and best practices

# 3. Load the best match
bun bin/get.js security-auditor

# 4. Follow loaded agent's instructions
```

### Available Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `search.js` | Find agents matching intent | `bun bin/search.js "react hooks"` |
| `search-paged.js` | Paged search for large registries | `bun bin/search-paged.js "query" --page 1` |
| `get.js` | Load specific agent | `bun bin/get.js react-expert` |
| `list.js` | Show all indexed agents | `bun bin/list.js` |
| `rebuild.js` | Rebuild index after changes | `bun bin/rebuild.js` |

> **Note:** The `UserPromptSubmit` hook (`hooks/user_prompt_search.js`) runs automatically on every prompt -- no manual search step is needed for typical usage. The commands above are available for direct use when needed.

## Architecture

### How It Works

```
Traditional Approach (Eager Loading)

  Load ALL agents -> Context Window -> Use 1-2 agents
  (~16-35k tokens)   (limited)        (~200-400 tokens)

  Wastes 85-90% of loaded agent tokens

Agent Registry Approach (Lazy Loading)

  registry.json -> Search -> Load specific agent
  (~2-4k tokens) (fast)   (~200-400 tokens)

  Saves 70-90% of agent-related tokens
```

### Registry Structure

```
~/.claude/skills/agent-registry/
├── SKILL.md                 # Skill definition + hook registration
├── install.sh               # Installer script
├── package.json             # Dependencies (@clack/prompts)
├── hooks/
│   └── user_prompt_search.js  # UserPromptSubmit hook (Bun)
├── references/
│   └── registry.json        # Lightweight agent index
├── agents/                  # Migrated agents stored here
│   ├── frontend/
│   │   ├── react-expert.md
│   │   └── vue-expert.md
│   └── backend/
│       ├── django-expert.md
│       └── fastapi-expert.md
├── lib/
│   ├── registry.js          # Path utilities + registry I/O
│   ├── parse.js             # Agent file parsing
│   ├── search.js            # BM25 search engine
│   └── telemetry.js         # Anonymous telemetry
└── bin/
    ├── cli.js               # CLI dispatcher
    ├── init.js              # Interactive migration
    ├── search.js            # Search by intent
    ├── search-paged.js      # Paginated search
    ├── get.js               # Load specific agent
    ├── list.js              # List all agents
    └── rebuild.js           # Rebuild index
```

### Registry Format

```json
{
  "version": 1,
  "agents": [
    {
      "name": "react-expert",
      "path": "frontend/react-expert.md",
      "summary": "React specialist focused on modern component architecture...",
      "keywords": ["react", "javascript", "frontend", "hooks"],
      "token_estimate": 1850,
      "content_hash": "a3f2b1c4"
    }
  ],
  "stats": {
    "total_agents": 150,
    "total_tokens": 17500,
    "tokens_saved_vs_preload": 14000
  }
}
```

**Index stays small:** Even with 300+ agents, the registry index typically stays under 8k tokens (vs 35k+ for loading all agents).

## Dependencies

- **Bun** -- Ships with Claude Code, no separate installation needed
- **@clack/prompts** -- Interactive selection UI (optional, install with `./install.sh --install-deps`)

Core functionality works without optional dependencies (text fallback UI is built in).

## Telemetry Disclosure

> **Notice:** Agent Registry can collect anonymous usage data to help improve the tool.
> This is **disabled by default** and only runs when explicitly enabled.

### What We Collect

We collect **anonymous, aggregate metrics only**:

| Data | Example | Purpose |
|------|---------|---------|
| Event type | `search`, `get`, `list` | Know which features are used |
| Result counts | `5 results` | Understand search effectiveness |
| Timing | `45ms` | Monitor performance |
| System info | `darwin`, `bun 1.x` | Ensure compatibility |
| Tool version | `2.0.1` | Track adoption |

### What We Do NOT Collect

- **No search queries** - We never see what you search for
- **No agent names** - We don't know which agents you use
- **No file paths** - We don't see your directory structure
- **No IP addresses** - We don't track your location
- **No personal information** - Completely anonymous

### Enable Telemetry (Optional)

```bash
# Explicit opt-in
export AGENT_REGISTRY_TELEMETRY=1
```

### Disable Telemetry

```bash
# Remove opt-in
unset AGENT_REGISTRY_TELEMETRY

# Universal standard (also respected)
export DO_NOT_TRACK=1
```

### Automatic Opt-Out

Telemetry is **automatically disabled** in CI environments:
- GitHub Actions, GitLab CI, CircleCI, Travis CI, Buildkite, Jenkins

### Transparency

The telemetry implementation is fully open source: [`lib/telemetry.js`](lib/telemetry.js)

## Configuration

The skill works at two levels:

- **User-level:** `~/.claude/skills/agent-registry/` (default)
- **Project-level:** `.claude/skills/agent-registry/` (optional override)

Agents not migrated remain in `~/.claude/agents/` and load normally.

## Benefits

### Token Efficiency
- **Before:** ~117 tokens/agent x count loaded upfront
- **After:** ~20-25 tokens/agent in index + full agent only when used
- **Savings:** 70-90% reduction in agent-related token overhead

**Real-world examples:**
- 50 agents: Save ~3-4k tokens (5.8k -> 2.5k) = 60-70% reduction
- 140 agents: Save ~13.7k tokens (16.4k -> 2.7k) = 83% reduction
- 300 agents: Save ~30k tokens (35k -> 5k) = 85-90% reduction

### Performance
- **Faster startup:** Less context to process at conversation start
- **Efficient loading:** Only pay token cost for agents actually used
- **Instant search:** BM25 + keyword matching in <100ms
- **Scalable:** Handles 300+ agents without performance degradation

### Organization
- **Category grouping:** Agents auto-organized by subdirectory
- **Visual indicators:** Color-coded token estimates
- **Easy discovery:** Search by intent, not memorized names
- **Pagination:** Browse large collections without terminal overflow

### Flexibility
- **Opt-in migration:** Choose exactly which agents to index
- **Graceful degradation:** Text fallback if @clack/prompts unavailable
- **Backward compatible:** Non-migrated agents load normally
- **No lock-in:** Agents can stay in original `~/.claude/agents/` if preferred

## Workflow Integration

### For Users

1. **Install once:** Run `./install.sh`
2. **Migrate agents:** Run `bun bin/init.js`
3. **Use normally:** Claude automatically searches registry on-demand

### For Claude

The skill provides a CRITICAL RULE:

> **NEVER assume agents are pre-loaded.** Always use this registry to discover and load agents.

Claude follows this pattern:
```
User Request -> search_agents(intent) -> select best match -> get_agent(name) -> execute
```

## Development

### Running Tests

```bash
bun test
```

101 tests across 5 files covering:
- **Unit tests:** lib/registry, lib/search, lib/parse, lib/telemetry
- **CLI integration tests:** all bin/ scripts tested via subprocess
- **Hook tests:** user_prompt_search.js stdin/stdout behavior

## Contributing

Found an issue or want to improve the registry? PRs welcome!

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Run tests (`bun test`)
4. Commit your changes (`git commit -m 'Add improvement'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Open a Pull Request

## License

MIT

## Credits

Built for the Claude Code community to solve the "~16k tokens" agent loading problem.

**Author:** Yossi Elkrief ([@MaTriXy](https://github.com/MaTriXy))

---

**Questions?** Open an issue on [GitHub](https://github.com/MaTriXy/Agent-Registry/issues)
