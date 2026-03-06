# Command Reference

## workplace init [path]

Initialize a new workplace. If path is omitted, uses current directory.

**Empty directory:**
```
> workplace init /path/to/new-project --name my-app
```
Ask the user for: project name, description, language/framework, agent roles, deploy environments.

**Existing project:**
```
> workplace init .
```
1. Run `scripts/scan_workplaces.sh` to check if `.git` exists
2. Run `scripts/init_workplace.sh <path>` to create `.workplace/`
3. Scan all `*.md` files in the project for context
4. Read `structure.json` to understand the codebase
5. Suggest agents based on project analysis (e.g., Node.js project → suggest coder, tester, devops)
6. Confirm with user, then create agent `.md` files in `.workplace/agents/`

## workplace list

List all registered workplaces. Show as inline buttons for switching.

```bash
jq '.[] | "\(.name) (\(.uuid | .[0:8])...) — \(.path)"' ~/.openclaw/workspace/.workplaces/registry.json
```

Use `message` action with inline buttons where `callback_data` = `workplace switch <uuid>`.

## workplace switch <name|uuid>

Switch the active workplace.

1. Find workplace in `registry.json` by name or UUID (partial match OK)
2. Update `~/.openclaw/workspace/.workplaces/current.json`
3. Update `lastActive` in registry
4. Load `.workplace/config.json` for context
5. Report: name, path, active agents, last activity

## workplace scan [path]

Discover workplaces under a path.

```bash
scripts/scan_workplaces.sh <path> --max-depth 5
# Add --register to auto-register discovered workplaces
scripts/scan_workplaces.sh <path> --register
```

## workplace link <path>

Link a related workplace to the current one.

1. Read current workplace from `current.json`
2. Resolve target path, find its `.workplace/config.json`
3. Add target UUID to current workplace's `config.json` → `linked[]`
4. Rebuild `full-tree.md`

## workplace unlink <path|uuid>

Remove a linked workplace.

1. Find target in current workplace's `config.json` → `linked[]`
2. Remove the UUID
3. Rebuild `full-tree.md`

## workplace status

Show current workplace details.

```
📁 my-app (a1b2c3d4-...)
   Path: /Users/dev/projects/my-app
   Host: macbook-pro
   Parent: parent-project (if any)
   Linked: [list of linked workplaces]
   
   Agents:
   - kernel: running (since 2026-02-17T10:00:00Z)
   - coder: idle
   - reviewer: idle
   
   Last activity: 2 hours ago
```

Read from `config.json` + `process-status.json`.

## workplace agents

List agents in current workplace with their roles and status.

```bash
# List agent files
ls .workplace/agents/*.md
# Parse frontmatter for each
```

## workplace agent start <name>

Start an agent by name.

1. Read `.workplace/agents/<name>.md`
2. Parse frontmatter (role, triggers, handoff_to)
3. Read `.workplace/structure.json` for context
4. Build system prompt from agent definition + workplace context
5. `sessions_spawn` with the constructed prompt
6. Update `process-status.json` with agent status
7. If multiple agents, start the Rust file-watcher server for `chat.md`

## workplace agent stop <name>

Stop a running agent.

1. Find the agent's session via `subagents(action=list)`
2. `subagents(action=kill, target=<session>)`
3. Update `process-status.json`

## workplace kernel start

Start the kernel agent (persistent mode).

1. Read `.workplace/agents/kernel.md`
2. Spawn as sub-agent with instructions to:
   - Scan and update `structure.json`
   - Rebuild `full-tree.md`
   - Save structure to supermemory (containerTag = workplace UUID)
3. Start the Rust file-watcher server in background

## workplace kernel stop

Stop the kernel agent and file-watcher server.

## workplace export [zip|json]

**ZIP export:**
```bash
cd /path/to/project
zip -r workplace-export.zip .workplace/ -x ".workplace/memory/*"
```

**JSON export:**
Combine `config.json`, agent definitions, deploy docs, and skills list into a single JSON manifest.

## workplace import <file>

1. Detect format (zip or JSON)
2. Extract/parse contents
3. Generate new UUID
4. Create `.workplace/` at target path
5. Register in central registry
6. Attempt to re-link related workplaces if found locally

## workplace load <path|name|uuid>

Load/open a registered workplace so it stays available for quick access and cross-workspace operations.

Loaded workplaces are tracked in `~/.openclaw/workspace/.workplaces/loaded.json`.

```bash
scripts/loaded_workplaces.sh load <path|name|uuid>
```

1. Resolve the target by path, UUID, or name from `registry.json`
2. Verify `.workplace/config.json` exists at the resolved path
3. Add entry to `loaded.json` with UUID, name, path, timestamp, and source
4. If not already linked to the current workplace, optionally add to `linked[]`

**Example:**
```
> workplace load /Users/dev/opensource/log-stream
✅ Loaded: log-stream
   UUID: 74cdd6fd-...
   Path: /Users/dev/opensource/log-stream
```

## workplace unload <name|uuid>

Remove a workplace from the loaded set.

```bash
scripts/loaded_workplaces.sh unload <name|uuid>
```

Does not delete the workplace or its `.workplace/` directory — just removes it from the loaded/open set.

## workplace loaded

List all currently loaded workplaces.

```bash
scripts/loaded_workplaces.sh list
```

Shows name, UUID, path, and when each was loaded.

## workplace delete <name|uuid>

1. Find in registry by name or UUID
2. Confirm with user
3. Remove from `registry.json`
4. Optionally delete `.workplace/` directory (ask first)
5. Clean supermemory entries (containerTag = UUID)

## workplace sync <ide>

Generate IDE context files from workplace config. Target: `cursor`, `claude`, `opencode`, or `all`.

```
> workplace sync cursor    # Generate .cursor/rules/workplace.mdc
> workplace sync claude    # Generate/update CLAUDE.md
> workplace sync opencode  # Update opencode.jsonc instructions
> workplace sync all       # Sync all detected IDEs
```

See [ide-sync.md](ide-sync.md) for full implementation details and file formats.

## workplace deploy <env>

Show deployment instructions for an environment.

1. Read `.workplace/deploy/<env>.md`
2. Present to user
3. Optionally execute commands if user confirms
