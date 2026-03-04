# Architecture

## Data Flow

```
skills/ (shipped with package)
    ↓
buildIndex()
    ↓
SkillEntry[] (in-memory index)
    ↓
┌─────────────┴─────────────┐
↓                           ↓
searchSkills()          loadSkill()
↓                           ↓
SearchResult[]       string (content)
↓                           ↓
MCP tool:              MCP tool:
search_skill          load_skill
```

1. **Index build** (`src/skill-index.ts`): Reads all `skills/*/SKILL.md` files, parses YAML frontmatter, tokenizes name+description, detects resources. Returns `SkillEntry[]`.

2. **Search** (`src/search.ts`): Token-based scoring against the in-memory index. No external dependencies.

3. **Load** (`src/loader.ts`): Reads SKILL.md content from disk. Optionally appends resource files alphabetically.

4. **Server** (`src/server.ts`): Wraps search and load into MCP tools with a lookup map for direct name/dirName access.

## Search Algorithm

Given a query string, the algorithm:

1. **Tokenizes** query: lowercase, remove non-alphanumeric (except hyphens), split on whitespace
2. **Scores** each skill entry:
   - For each query token × search token pair:
     - Exact match: **+1.0**
     - Substring match (either contains the other): **+0.5**
   - Bonus: query is substring of skill name: **+0.5**
   - Bonus: query is substring of skill description: **+0.3**
3. **Normalizes** by dividing total score by query token count
4. **Filters** results below 0.2 threshold
5. **Sorts** descending by score, limits to top N (default 20)

## Plugin Mode

The server can also run as a Claude Code plugin. The plugin layout:

```
.claude-plugin/plugin.json   — Plugin manifest (name, description, version, etc.)
.mcp.json                    — MCP server config using ${CLAUDE_PLUGIN_ROOT}
```

When installed as a plugin (`claude plugin install skill-library-mcp`), Claude Code:
1. Downloads/installs the package
2. Reads `.mcp.json` to discover MCP servers
3. Starts the MCP server automatically on launch
4. Exposes `search_skill`, `load_skill`, and `list_categories` as tools

The `${CLAUDE_PLUGIN_ROOT}` variable resolves to the plugin's install directory, so `dist/index.js` and `skills/` are found correctly. This works because the npm package ships both `dist/` and `skills/` in its `files` array.

## Design Decisions

- **In-memory index**: Skills are indexed once at startup. The index is small (frontmatter + tokens only, not full content). Search is O(n) over entries — fast enough for hundreds of skills.

- **Lazy content loading**: Full SKILL.md content is only read from disk when `load_skill` is called. This keeps memory usage low.

- **Token-based search over full-text**: Simpler, no external dependencies, good enough for skill names and descriptions. Avoids pulling in a search library.

- **YAML frontmatter**: Standard format used by many tools (Jekyll, Hugo, MDX). Makes skills compatible with existing tooling.

- **ESM-only**: Modern Node.js (22+) target. No CJS compatibility needed.

## Performance

- Index build: ~50ms for 700 skills (sequential file reads)
- Search: <1ms for typical queries against 700 entries
- Load: Single file read (~1ms), plus resource files if requested
