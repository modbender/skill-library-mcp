# Skill: qmd-setup

**Name:** qmd-setup
**Description:** Install and configure QMD semantic search memory for the knowledge base.

## Overview

QMD adds semantic search to the memory system. Instead of relying solely on file paths and keyword matching, agents can query the knowledge base with natural language and get ranked results by meaning.

| Feature | Without QMD | With QMD |
|---|---|---|
| **Search method** | File path navigation + direct file reads | Semantic natural language queries |
| **Finding related info** | Must know which file to look in | Searches across all indexed files by meaning |
| **New file discovery** | Manual — agent must be told about new files | Automatic — new files indexed within 5 minutes |
| **Query example** | `read shared/brands/skincare/profile.md` | `"What ingredients does the skincare brand focus on?"` |
| **Best for** | Small knowledge bases with known structure | Growing knowledge bases where discovery matters |
| **Required?** | No — file-based memory works fine for small-to-medium KBs | Optional — adds power as the KB grows |

## When to Use

1. **Growing knowledge base** — When the KB has grown beyond what agents can navigate by file path alone. If agents are frequently missing relevant information because they didn't know which file to check, QMD helps.

2. **Cross-brand queries** — When agents need to find information across multiple brands or domains without knowing exactly where it lives. QMD searches everything at once.

3. **New team member onboarding** — When adding new agents or reconfiguring the team. QMD helps new agents discover existing knowledge without being briefed on every file.

## Setup Flow

### Step 1: Check Current State

First, check whether QMD is already installed and what the current memory configuration looks like.

```bash
# Check if qmd is installed
which qmd

# Check current memory config
cat ~/.openclaw/openclaw.json | python3 -m json.tool | grep -A 10 '"memory"'
```

**If QMD is already installed and configured:** You're done. Verify it's working (skip to Step 4).
**If QMD is installed but not configured:** Skip to Step 3.
**If QMD is not installed:** Continue to Step 2.

### Step 2: Install QMD

**Recommended: Install with bun (faster):**
```bash
bun install -g @tobilu/qmd
```

**Alternative: Install with npm:**
```bash
npm install -g @tobilu/qmd
```

**Verify installation:**
```bash
which qmd
qmd --version
```

If you see a path and version number, installation succeeded. If you get `ERR_DLOPEN_FAILED`, see the Troubleshooting section below.

### Step 3: Configure

**Option A: Automatic configuration (recommended):**
```bash
node scripts/patch-config.js --force-qmd
```

This patches `openclaw.json` to set:
- `memory.backend` to `"qmd"`
- `memory.qmd.paths` to the default shared KB directories
- `memory.qmd.update.interval` to `"5m"`

**Option B: Manual configuration:**

Edit `~/.openclaw/openclaw.json` and add or update the `memory` section:

```json
{
  "memory": {
    "backend": "qmd",
    "qmd": {
      "includeDefaultMemory": true,
      "paths": [
        { "path": "memory", "name": "daily-notes", "pattern": "**/*.md" },
        { "path": "skills", "name": "agent-skills", "pattern": "**/*.md" },
        { "path": "shared", "name": "shared-knowledge", "pattern": "**/*.md" }
      ],
      "update": { "interval": "5m" }
    }
  }
}
```

**Configuration fields:**

| Field | Description | Default |
|---|---|---|
| `memory.backend` | Memory backend to use | `"file"` (change to `"qmd"`) |
| `memory.qmd.includeDefaultMemory` | Include default MEMORY.md in index | `true` |
| `memory.qmd.paths` | Array of `{path, name, pattern}` objects defining indexed directories | (none — must be set) |
| `memory.qmd.update.interval` | Interval between automatic reindex runs | `"5m"` |

### Step 4: Restart and Verify

```bash
# Restart the gateway to pick up the new config
openclaw gateway restart

# Check the logs for QMD initialization
openclaw gateway logs | grep -i qmd
```

**Expected log output:**
```
[INFO] Memory backend: qmd
[INFO] QMD indexing 4 paths...
[INFO] QMD indexed 42 documents in 1.3s
[INFO] QMD ready — next reindex in 300s
```

**Test a semantic query:**
```bash
# If your system supports it:
openclaw memory search "skincare brand ingredients"
```

If results come back with relevant documents, QMD is working correctly.

---

## Troubleshooting

### better-sqlite3 Node Version Mismatch

QMD depends on `better-sqlite3`, which is a native Node.js addon. If the Node.js version used to install QMD differs from the Node.js version running the gateway, you will get:

```
Error: ERR_DLOPEN_FAILED
Module was compiled against a different Node.js version
```

**Fix:**

1. Identify which Node.js the gateway uses:
   ```bash
   which node
   node --version
   ```

2. Rebuild better-sqlite3 with that Node.js:
   ```bash
   # For bun global installs:
   cd ~/.bun/install/global/node_modules/better-sqlite3
   npm rebuild better-sqlite3

   # For npm global installs:
   cd $(npm root -g)/better-sqlite3
   npm rebuild better-sqlite3
   ```

3. Verify the fix:
   ```bash
   node -e "require('better-sqlite3')"
   # No output = success
   ```

4. Restart the gateway:
   ```bash
   openclaw gateway restart
   ```

### Other Common Issues

| Issue | Fix |
|---|---|
| `which qmd` returns nothing | QMD not installed. Run Step 2. |
| "backend not configured" | `memory.backend` not set to `"qmd"` in config. Run Step 3. |
| Search returns no results | Files may not be indexed yet. Wait 5 minutes for auto-reindex, or check `paths` config. |
| SQLite database missing | Check `memory.qmd.dbPath` is writable. QMD creates the file on first run. |
| Broken symlinks in index paths | Verify all paths in `paths` resolve correctly. Replace broken symlinks. |

---

## Uninstall

To remove QMD and revert to file-based memory:

1. **Update configuration:**
   Edit `~/.openclaw/openclaw.json` and change:
   ```json
   {
     "memory": {
       "backend": "file"
     }
   }
   ```
   You can leave the `qmd` section in place — it will be ignored when the backend is `"file"`.

2. **Restart the gateway:**
   ```bash
   openclaw gateway restart
   ```

3. **(Optional) Remove QMD package:**
   ```bash
   # If installed with bun:
   bun remove -g @tobilu/qmd

   # If installed with npm:
   npm uninstall -g @tobilu/qmd
   ```

4. **(Optional) Remove the SQLite database:**
   ```bash
   rm ~/.openclaw/memory/main.sqlite
   ```

After uninstalling, agents will use file-based memory (MEMORY.md + direct file reads). This works fine for small-to-medium knowledge bases and requires no additional dependencies.
