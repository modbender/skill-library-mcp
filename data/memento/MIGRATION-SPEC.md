# Migration: Existing Memory Files → Memento Knowledge Base

## Overview
One-time migration to bootstrap Memento's knowledge base from existing agent memory files.
Can also be re-run incrementally (skips already-processed files).

## Agent Inventories

Agent workspace paths are configured per-environment in `~/.engram/migration-config.json`
(see the Migration Script section below). The paths below are illustrative examples.

### Main agent
- Workspace: `~/your-workspace/` (set via `MEMENTO_WORKSPACE_MAIN` or migration-config.json)
- Files: `MEMORY.md` + `memory/*.md`
- Content: User preferences, family, tech setup, career, everything

### Specialist agents (optional)
- Workspace: configured per agent in `~/.engram/migration-config.json`
- Files: `MEMORY.md` + `memory/*.md` + domain-specific files
- Content: Domain-specific knowledge (medical records, project files, etc.)

### Visibility Classification
**IMPORTANT**: Visibility is determined by the CONTENT of each fact, NOT by which agent produced it.
The classifier analyzes each extracted fact independently:
- Medical diagnoses, prescriptions, health data → `secret`
- Credentials, passwords, API keys → `secret`
- User preferences, family info, general knowledge → `shared`
- Project-specific technical details → `private`
- A preference discussed with another agent is still `shared`
- A password mentioned to the main agent is still `secret`

No `defaultVisibility` per agent — let the classifier decide per fact.

## Migration Script (`src/extraction/migrate.ts`)

### Interface
```typescript
interface MigrationConfig {
  agents: Array<{
    agentId: string;
    workspace: string;
    paths: string[];           // glob patterns relative to workspace
    defaultVisibility: 'private' | 'shared' | 'secret';
  }>;
  extractionModel: string;     // from plugin config
  dryRun?: boolean;            // log what would be extracted without calling LLM
  skipAlreadyProcessed?: boolean; // default true
}
```

### Default Configuration

Agent workspaces are loaded from `~/.engram/migration-config.json` (created by the user).
Example config:

```json
{
  "agents": [
    {
      "agentId": "main",
      "workspace": "/home/yourname/your-workspace",
      "paths": ["MEMORY.md", "memory/*.md"]
    },
    {
      "agentId": "specialist",
      "workspace": "/home/yourname/other-workspace",
      "paths": ["MEMORY.md", "memory/*.md", "domain/*.md"]
    }
  ]
}
```

Alternatively, set `MEMENTO_WORKSPACE_MAIN` environment variable for the main agent.

```typescript
// NOTE: No defaultVisibility per agent — the classifier determines
// visibility from the content of each extracted fact.
const DEFAULT_EXTRACTION_MODEL = 'anthropic/claude-sonnet-4-6';
```

### Process
1. For each agent, glob the specified paths
2. For each file:
   a. Check if already in `extraction_log` (by creating a synthetic conversation_id from the file path hash)
   b. If not processed (or force=true), read the file content
   c. Create a synthetic conversation entry in the DB (source='migration', raw_text=file content)
   d. Run the extraction prompt with the file content
   e. Insert extracted facts with the agent's default visibility (overridable by classifier)
   f. Log in extraction_log
3. Report summary: files processed, facts extracted, per agent

### Special Handling
- **SOUL.md, AGENTS.md, USER.md, IDENTITY.md**: Skip these — they're system files, not memory
- **HEARTBEAT.md, TOOLS.md**: Skip — operational config, not knowledge
- **Files > 50KB**: Split into chunks before extraction
- **Dr Robby medical files**: Force visibility=secret regardless of classifier output

### CLI Integration
Should be runnable as:
```bash
# Via openclaw plugin command (if registered)
openclaw memento migrate --dry-run
openclaw memento migrate --agent main
openclaw memento migrate --all

# Or directly via node
node -e "require('./src/extraction/migrate.ts').runMigration()"
```

## Tracking
- Each migrated file creates a `conversations` entry with `channel='migration'`
- The `extraction_log` tracks processing status
- Re-running skips already-processed files unless `--force` is passed
