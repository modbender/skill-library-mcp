---
name: decision-topology
description: Records the structure of conversations where ideas evolve, branch, get rejected, pivot, or combine. Saves each structural shift as a node in a local JSON tree the user can browse on demand. Zero network access, zero external dependencies. Covers proposals, rejections, pivots, and merges with cross-tree concept linking.
metadata: {"openclaw":{"always":true,"emoji":"🌳","requires":{"bins":["node"]}}}
---

# Decision Topology

Records how ideas branch and evolve during conversations, producing a browsable tree the user can review at any time. Like `git log` for thinking — the structure is always there when you want to inspect it.

**Privacy note:** This skill is installed and enabled by the user. All data stays on disk in the configured trees directory — nothing is sent externally. The user can view, delete, or relocate their trees at any time.

## Security Properties

- **Zero network access** — no HTTP calls, no sockets, no DNS lookups. Works fully offline.
- **Zero external dependencies** — uses only Node.js built-in `fs` and `path` modules.
- **No conversation content stored** — nodes contain short structural summaries (5-15 words), never verbatim quotes.
- **No process spawning** — no `child_process`, no `exec`, no `eval`, no `Function()`.
- **Stdin-only input** — all user-derived content is piped via stdin as JSON to prevent shell injection. See [SECURITY.md](SECURITY.md) for details.
- **User-controlled storage** — trees are local JSON files the user can inspect, move, or delete at any time.
- **ID generation** — uses `Math.random()` for 6-char hex node IDs. Cryptographic randomness is not needed — IDs only require tree-local uniqueness across 5-30 nodes.

## Activation

Active by default (user can set `always: false` in metadata to require explicit invocation). When a conversation involves brainstorming, problem-solving, or exploring options, record the structure as a tree.

Skip pure Q&A ("what time is it"), greetings, and small talk.

## Output Style

Do not insert status messages about tree operations into the conversation. The goal is a clean conversational experience — like how git commits happen without the developer seeing each one.

- Do not say "logging node," "branch created," "adding to tree" — this adds noise without value.
- Do not change your conversational behavior because of the skill. The user gets the same conversation they'd get without it.
- The user can ask to see the topology at any time ("show me what we explored", "what did we kill?").
- Think: git commits in the background. Low-noise, not hidden — the user knows it's installed and can inspect it whenever they want.

## When to Record a Node

**Create a node when:**
- You propose a distinct idea, direction, solution, or option
- The user introduces a new angle or topic
- The user rejects, pushes back, or corrects — this is a branch kill, always record the reason
- The conversation pivots direction because of something said
- An insight combines elements from earlier dead branches (merge node)
- An analogy, metaphor, or reframe changes how the problem is understood
- A question redirects the exploration (pivot node)

**Skip when:**
- Same idea continues without meaningful evolution
- Minor refinement within the same direction
- Trivial "no" to something small that doesn't change direction
- Factual answers to factual questions

**Depth calibration:** A good tree has 5-30 nodes recording the shape of an exploration. Not 200 nodes transcribing every sentence. Only create nodes when the direction of thinking meaningfully shifts. Heuristic: would this rejection or pivot change what comes next? If yes, record it. If no, skip it.

## Auto-Initialization

Do NOT create a tree when a conversation starts. Wait until the conversation actually branches — until there is a rejection, a pivot, or a second distinct direction. Only then initialize.

Most conversations won't need a tree. That's fine.

When initializing, auto-generate the filename from the date and a 2-4 word topic slug:
- `2026-02-24-business-model-exploration.json`
- `2026-02-24-vacation-planning.json`

## Auto-Association

When a conversation starts and ideas begin branching, check if this connects to an existing tree before creating a new one.

**How to check:** Run the associate command with the core topic:
```bash
echo '{"query": "short description of current topic"}' | node {baseDir}/scripts/topology.js associate
```

This scans existing trees and returns the best match with a relevance score.
- Score >= 0.4 — continue that tree (load it, add nodes to it)
- Score 0.25-0.4 — ambiguous. Ask the user naturally: "This feels related to [topic] we explored on [date]. Continuing that thread, or fresh start?"
- Score < 0.25 — new tree

Never ask the user to pick a tree by ID. If you need to disambiguate, ask naturally in conversation.

## Setup

**Script:** `{baseDir}/scripts/topology.js`

**Storage:** Trees are stored in `{baseDir}/trees/` by default. Override with the `TOPOLOGY_TREES_DIR` environment variable if you want trees stored elsewhere (e.g. in a memory directory for semantic search indexing).

**Invocation:** Always pipe JSON args via stdin to prevent shell injection from user-derived content:
```bash
echo '<JSON args>' | node {baseDir}/scripts/topology.js <command>
```

## Core Operations

### Initialize a tree
```bash
echo '{"topic": "short topic description"}' | node {baseDir}/scripts/topology.js init
```
Returns the file path and root node ID. Remember both for the session.

### Add a node
```bash
echo '{"file": "<path>", "parent_id": "<id>", "type": "proposal", "summary": "one-line description", "reasoning": "why", "concepts": ["keyword1", "keyword2"]}' | node {baseDir}/scripts/topology.js add-node
```
Types: `proposal`, `pivot`, `merge`. The `concepts` array is optional — short keyword tags extracted from the node content, used for cross-tree linking.

### Kill a branch
```bash
echo '{"file": "<path>", "node_id": "<id>", "reason": "why it was rejected"}' | node {baseDir}/scripts/topology.js kill-branch
```
Then add the new direction as a child (pivot node linked to what was killed).

### Merge branches
```bash
echo '{"file": "<path>", "source_ids": ["<id1>", "<id2>"], "summary": "merged insight", "reasoning": "combines X from A with Y from B"}' | node {baseDir}/scripts/topology.js merge
```

### Fork from any node
```bash
echo '{"file": "<path>", "node_id": "<id>", "summary": "re-exploring from this point", "reasoning": "reason for revisiting"}' | node {baseDir}/scripts/topology.js fork
```

## Node Types

| Type | When |
|---|---|
| `root` | Core topic (created by `init`) |
| `proposal` | You suggest a direction, idea, or option |
| `pivot` | New direction that emerged from a rejection or redirection |
| `merge` | Insight combining elements from multiple branches |

Status values: `active` (still exploring), `dead` (rejected, has `killed_by`), `merged` (combined into a merge node).

## Viewing the Topology

The user does NOT need to learn slash commands. They ask naturally:
- "Show me what we explored"
- "What did we kill?"
- "What shape is this conversation?"
- "What paths did we reject and why?"
- "Go back to that idea about X"

You understand the intent and run the appropriate commands. Present results conversationally, not as raw script output.

**`/tree` is an optional shortcut** — works if the user types it, but don't teach it or require it.

### Rendering
```bash
echo '{"file": "<path>"}' | node {baseDir}/scripts/topology.js render
```
After the tree, append a one-line summary: `{N} branches explored, {M} killed, {K} active, depth {D}`

### List all trees
```bash
node {baseDir}/scripts/topology.js list
```

### Statistics
```bash
echo '{"file": "<path>"}' | node {baseDir}/scripts/topology.js stats
```

### Export as Mermaid
```bash
echo '{"file": "<path>"}' | node {baseDir}/scripts/topology.js export
```

### Revisiting a dead branch
When the user asks about a killed path, find the node, present:
- What was proposed
- Why it was proposed
- Why it was killed
- What came after

### Cross-tree analysis
```bash
node {baseDir}/scripts/topology.js analyze
```
Rebuilds the concept index, scans all trees, finds concepts appearing across multiple trees, reports which ideas keep surviving vs keep getting killed, identifies cross-root connections, and regenerates all companion .md files with updated cross-tree links and weights. Shows index health stats (total concepts, cross-tree count, orphans).

### Query the concept index
```bash
echo '{"name": "trust"}' | node {baseDir}/scripts/topology.js concept
echo '{"list": true}' | node {baseDir}/scripts/topology.js concept
echo '{"orphans": true}' | node {baseDir}/scripts/topology.js concept
```
- `name` — reverse-lookup: shows every node across every tree that references a concept
- `list` — all concepts sorted by cross-tree spread, `*` marks concepts spanning multiple trees
- `orphans` — concepts that exist in only one tree (candidates for future linking)

### Rebuild concept index
```bash
node {baseDir}/scripts/topology.js rebuild-index
```
Full rebuild of `concepts.json` from all tree files. Also regenerates all companion .md files with cross-tree links and updated weights. Use as a recovery tool or after manual edits to tree JSON files.

## Concept Index

A reverse-index at `{trees_dir}/concepts.json` that maps every concept keyword to all nodes and trees that reference it.

- **Automatic:** Updated incrementally on every tree save (add-node, kill-branch, merge, fork, init). No manual intervention needed.
- **Cross-tree links:** Companion .md files include a `## Related trees` section with `[[wikilinks]]` to other trees that share concepts. Useful for semantic search indexing.
- **Weight field:** Node `weight` is auto-set to the number of distinct trees sharing that node's concepts. `weight: 1` = single-tree concept. `weight: 2+` = concept spans multiple trees.
- **Lazy discovery:** Links form organically as nodes are added to any tree. A new node with `concepts: ["trust"]` will immediately link its tree to every other tree that also references "trust" — no need to wait for `analyze`.

## Rules

1. **Clean output.** Do not insert tree-operation status messages into the conversation. The user can inspect trees whenever they want.
2. **Judgment over completeness.** Record the shape, not the transcript. 5-30 nodes per tree. Summaries only — never store verbatim conversation content.
3. **Causal links.** Show WHY the conversation evolved, not just WHAT was said. Link rejections to pivots.
4. **Persist.** Trees are JSON files that survive sessions. They can be searched if stored in an indexed directory.
5. **Continue, don't duplicate.** If a conversation continues a previous topic, load and extend that tree.
6. **Graceful failures.** Missing or corrupted tree — re-initialize. Missing node ID — say so clearly. Never crash.
7. **Natural interface.** The user asks in plain language. You translate to the right operation. Slash commands are optional shortcuts, not the primary interface.
8. **Local only.** All data stays on disk. No network calls, no external APIs, no telemetry. The user owns their data.
