# Decision Topology

An OpenClaw skill that records the structure of conversations where ideas evolve, branch, get rejected, pivot, or combine. Saves each structural shift as a node in a local JSON tree. Like git for thinking — the structure is always there when you want to inspect it. Zero network access, zero external dependencies.

## What It Does

During conversations, the agent records how ideas evolve as a tree structure:

- **Proposals** — distinct ideas or directions suggested
- **Pivots** — new directions emerging from rejections
- **Merges** — insights combining elements from multiple branches
- **Kills** — rejected paths with captured reasoning

The result is a persistent tree structure that captures *why* a conversation evolved, not just what was said.

## Features

- **Low-noise operation** — active during every conversation by default, viewable on request
- **Auto-association** — checks existing trees before creating new ones
- **Concept indexing** — cross-tree linking via keyword concepts
- **ASCII rendering** — visual tree display in terminal
- **Mermaid export** — diagram export for documentation
- **Cross-tree analysis** — find patterns across multiple explorations
- **Companion .md files** — auto-generated for semantic search indexing

## Install

```bash
clawhub install decision-topology
```

Or manually copy the `SKILL.md`, `scripts/`, and `references/` folders into your OpenClaw workspace skills directory.

## Configuration

**Storage:** Trees are stored in `{baseDir}/trees/` by default. Override with the `TOPOLOGY_TREES_DIR` environment variable to store trees elsewhere (e.g. in a memory directory for semantic search indexing).

**Always-on mode:** The skill ships with `always: true` in its metadata, meaning it is active during every conversation by default. If you prefer on-demand recording only, edit the metadata line in `SKILL.md`:

```yaml
# Change always to false — the skill will only record when explicitly invoked
metadata: {"openclaw":{"always":false,"emoji":"🌳","requires":{"bins":["node"]}}}
```

## Usage

The skill runs automatically — no setup needed. The user interacts naturally:

- *"Show me what we explored"*
- *"What did we kill?"*
- *"What shape is this conversation?"*
- *"What paths did we reject and why?"*
- *"Go back to that idea about X"*

### CLI Commands

Args are piped via stdin to avoid shell injection from user-derived content:

```bash
echo '{"topic": "exploration topic"}' | node scripts/topology.js init
echo '{"file": "<path>", "parent_id": "<id>", "type": "proposal", "summary": "description"}' | node scripts/topology.js add-node
echo '{"file": "<path>", "node_id": "<id>", "reason": "why rejected"}' | node scripts/topology.js kill-branch
echo '{"file": "<path>", "source_ids": ["<id1>", "<id2>"], "summary": "merged insight"}' | node scripts/topology.js merge
echo '{"file": "<path>"}' | node scripts/topology.js render
echo '{"file": "<path>"}' | node scripts/topology.js export
node scripts/topology.js list
echo '{"file": "<path>"}' | node scripts/topology.js stats
node scripts/topology.js analyze
echo '{"list": true}' | node scripts/topology.js concept
```

### Example Tree Output

```
What stack to use for the web app?

(*) What stack to use for the web app?
|-- [x] Use a full React SPA (killed: too heavy for our use case)
|-- [*] Server-rendered with HTMX
|   |-- [x] Go + templ (killed: team doesn't know Go)
|   `-- (*) Node + Express + HTMX
`-- [x] Static site with JS sprinkles (killed: need real-time features)

5 branches explored, 3 killed, 2 active, depth 2
```

## Requirements

- Node.js (any recent version)
- OpenClaw (for skill integration)

## Schema

See [references/schema.md](references/schema.md) for the full v2 tree and node schema.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## License

MIT
