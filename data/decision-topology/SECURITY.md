# Security

## Threat Model

Decision Topology is a **local-only** conversation structure mapper. It runs inside an OpenClaw agent on the user's own machine. There is no server component, no cloud storage, and no network communication of any kind.

The primary threat surface is the host filesystem: the script reads and writes JSON tree files in a single configured directory. The user controls this directory and can inspect, move, or delete any file at any time.

## What This Skill Does NOT Do

- **No network access** — no HTTP/HTTPS requests, no WebSocket connections, no DNS lookups. The script works fully offline.
- **No external dependencies** — only Node.js built-in `fs` and `path` modules are used. No `node_modules/`, no `package.json`, no install step.
- **No `eval` or dynamic code execution** — no `eval()`, no `new Function()`, no `vm.runInContext()`.
- **No child process spawning** — no `child_process`, no `exec`, no `spawn`, no `execFile`.
- **No telemetry or analytics** — nothing is collected, reported, or phoned home.
- **No conversation content stored** — nodes contain short structural summaries (5-15 words each), never verbatim conversation quotes.
- **No data exfiltration path** — even if the filesystem were compromised, tree files contain only topic labels and structural metadata, not conversation content.

## Modules Used

| Module | Purpose |
|--------|---------|
| `fs` | Read/write JSON tree files and markdown companion files in the configured trees directory |
| `path` | Resolve file paths relative to the script location and trees directory |

That's it. No other modules are imported.

## Input Handling

All user-derived input (topics, summaries, queries, concept keywords) is passed via **stdin as JSON**. This prevents shell injection attacks that could occur if user content were embedded in shell command strings.

The script also accepts a JSON argument as `argv[3]` for programmatic use. Commands that take no arguments (`list`, `analyze`, `rebuild-index`) skip stdin entirely.

Input is parsed with `JSON.parse()` — malformed JSON produces an error message and `process.exit(1)`, nothing else.

## Filesystem Scope

The script reads and writes files in exactly one directory: the trees directory, determined by:

1. The `TOPOLOGY_TREES_DIR` environment variable (if set), or
2. `{script_directory}/../trees/` (default)

No files outside this directory are read, written, or deleted.

## ID Generation

Node IDs are 6-character hex strings generated with `Math.random()`. These IDs only need to be unique within a single tree (typically 5-30 nodes). The `uniqueId()` function retries on collision. Cryptographic randomness is unnecessary for this use case.

## Vulnerability Reporting

If you find a security issue, please open an issue on the ClewHub skill page or contact the maintainer directly. There is no bug bounty — this is a local-only tool with no network surface — but reports are appreciated and will be addressed.
