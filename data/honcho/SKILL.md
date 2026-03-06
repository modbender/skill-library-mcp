---
name: honcho-setup
description: >
  Install the @honcho-ai/openclaw-honcho plugin and migrate legacy file-based
  memory to Honcho. **UPLOADS WORKSPACE CONTENT TO EXTERNAL API**: Sends
  USER.md, MEMORY.md, IDENTITY.md, memory/, canvas/, SOUL.md, AGENTS.md,
  BOOTSTRAP.md, TOOLS.md, and HEARTBEAT.md contents to api.honcho.dev
  (managed, default) or your self-hosted HONCHO_BASE_URL. Requires user
  confirmation before uploading. Archives originals locally with user
  confirmation. Updates workspace docs to reference Honcho tools. Works with
  managed Honcho (requires API key) or self-hosted local instances (no key
  needed).
metadata:
  openclaw:
    emoji: "🧠"
    required_env: []  # Nothing is strictly required - self-hosted mode works without API key
    optional_env:
      - name: HONCHO_API_KEY
        description: "REQUIRED for managed Honcho (https://app.honcho.dev). NOT required for self-hosted instances. This skill reads this value from environment variables or ~/.openclaw/.env file."
      - name: HONCHO_BASE_URL
        description: "Base URL for a self-hosted Honcho instance (e.g. http://localhost:8000). Defaults to https://api.honcho.dev (managed)."
      - name: HONCHO_WORKSPACE_ID
        description: "Honcho workspace ID. Defaults to 'openclaw'."
      - name: WORKSPACE_ROOT
        description: "Path to the OpenClaw workspace root. Auto-detected from ~/.openclaw/openclaw.json if not set."
    required_binaries:
      - node
      - npm
    optional_binaries:
      - git
      - docker
      - docker-compose
    writes_to_disk: true
    archive_directory: "{workspace_root}/archive/"
    reads_sensitive_files:
      - "~/.openclaw/.env - reads ONLY the HONCHO_API_KEY value, no other environment variables are accessed"
      - "~/.openclaw/openclaw.json - reads workspace path configuration only"
    network_access:
      - "api.honcho.dev (managed mode, default)"
      - "User-configured HONCHO_BASE_URL (self-hosted mode)"
    data_handling:
      uploads_to_external: true
      requires_user_confirmation: true
      external_destinations:
        - "api.honcho.dev (managed Honcho, default)"
        - "User-configured HONCHO_BASE_URL (self-hosted mode)"
      uploaded_content:
        - "USER.md, MEMORY.md, IDENTITY.md (user profile/memory files)"
        - "All files under memory/ directory (structured memory)"
        - "All files under canvas/ directory (working memory)"
        - "SOUL.md, AGENTS.md, BOOTSTRAP.md, TOOLS.md, HEARTBEAT.md (agent configuration)"
      data_destination_purpose: "Migrates file-based memory system to Honcho API for AI agent memory/personalization"
  homepage: "https://honcho.dev"
  source: "https://github.com/plastic-labs/honcho"
---

# Honcho Setup

Install the Honcho plugin and migrate legacy workspace memory files to Honcho.

> ⚠️ **DATA UPLOAD WARNING**: This skill uploads the contents of your workspace memory files (USER.md, MEMORY.md, IDENTITY.md, memory/, canvas/, SOUL.md, AGENTS.md, BOOTSTRAP.md, TOOLS.md, HEARTBEAT.md) to an external API. By default, data is sent to `api.honcho.dev` (managed Honcho cloud service). For self-hosted instances, data is sent to your configured `HONCHO_BASE_URL`. You will be asked for explicit confirmation before any upload occurs, and you will see exactly which files will be uploaded and where they will be sent.

> **This skill modifies workspace files.** It will ask for confirmation before archiving or deleting any files. If the Honcho upload fails or is skipped, no files are moved or removed. All files are backed up to `{workspace_root}/archive/` before any deletion.

> **Sensitive file access:** This skill reads `~/.openclaw/.env` to check for `HONCHO_API_KEY` only (required for managed Honcho). No other environment variables are read from this file. It also reads `~/.openclaw/openclaw.json` to determine workspace location.
## Step 1: Install and Enable the Plugin

Install the Honcho plugin using the OpenClaw plugin system. **Use this exact command — do not install `@honcho-ai/sdk` directly or use `npm install` in the workspace.**

```bash
openclaw plugins install @honcho-ai/openclaw-honcho
```

Then enable it:

```bash
openclaw plugins enable openclaw-honcho
```

After enabling, verify the plugin loaded without errors. If the gateway logs show `Cannot find module '@honcho-ai/sdk'`, the plugin's dependencies need to be installed manually:

```bash
cd ~/.openclaw/extensions/openclaw-honcho && npm install
```

Then restart the gateway. This is a known issue with the OpenClaw plugin installer not running dependency resolution for plugin packages.

If the plugin is already installed and enabled, skip to Step 2.

## Step 2: Verify Honcho Connection

Honcho can run as a **managed cloud service** or as a **self-hosted local instance**. Determine which the user is using.

### Option A: Managed Honcho (default)

Confirm that `HONCHO_API_KEY` is set. Check the environment variables first. If not found, read ONLY the `HONCHO_API_KEY` value from `~/.openclaw/.env` if that file exists. **Do not read or access any other environment variables from the .env file** — only extract the HONCHO_API_KEY value needed for this migration.

If the key is **not** set in either location, stop and tell the user:

> `HONCHO_API_KEY` is not set. Add it to your environment or `~/.openclaw/.env`, then re-run this skill. You can get a key at https://app.honcho.dev

### Option B: Self-hosted / local Honcho

Honcho is open source and can be run locally. If the user is running their own instance, they need to set `HONCHO_BASE_URL` to point to it (e.g., `http://localhost:8000`). The SDK `environment` should be set to `"local"`.

A local instance can be started with docker-compose from the Honcho repo (requires `git`, `docker`, and `docker-compose`):

```bash
git clone https://github.com/plastic-labs/honcho
cd honcho
cp .env.template .env
cp docker-compose.yml.example docker-compose.yml
docker compose up
```

For local instances, `HONCHO_API_KEY` may not be required depending on the user's configuration. Verify connectivity before proceeding.

See https://github.com/plastic-labs/honcho?tab=readme-ov-file#local-development for full self-hosting instructions.

**Do not proceed with migration until the connection is verified.** No files will be read, uploaded, archived, or removed without a working Honcho connection.

## Step 3: Detect Legacy Memory Files

Scan the workspace root for legacy memory files. The workspace root is determined by (in priority order):

1. The `WORKSPACE_ROOT` environment variable
2. The `agent.workspace` or `agents.defaults.workspace` field in `~/.openclaw/openclaw.json`
3. `~/.openclaw/workspace`

### Files to detect

**User/owner files** (content describes the user):
- `USER.md`
- `IDENTITY.md`
- `MEMORY.md`

**Agent/self files** (content describes the agent):
- `SOUL.md`
- `AGENTS.md`
- `TOOLS.md`
- `BOOTSTRAP.md`
- `HEARTBEAT.md`

**Directories:**
- `memory/` — recursively read all files
- `canvas/` — recursively read all files

Files inside `memory/` and `canvas/` are treated as user/owner content.

Report what was found to the user before proceeding. **IMPORTANT: You MUST ask for explicit confirmation before proceeding.** 

When asking for confirmation, provide this exact information to the user:

> **Found legacy memory files ready for migration:**
> - [List each file found with its size]
>
> **What will happen next if you confirm:**
> 1. **Upload**: All file contents will be uploaded to [api.honcho.dev OR your self-hosted URL]
> 2. **Archive**: Files will be copied to {workspace_root}/archive/ for backup
> 3. **Remove**: Legacy-only files (USER.md, MEMORY.md, IDENTITY.md, HEARTBEAT.md, memory/, canvas/) will be removed after successful archive
> 4. **Update**: Workspace docs (SOUL.md, AGENTS.md, BOOTSTRAP.md) will be updated to use Honcho tools
>
> **Data destination**: Your file contents will be sent to [show actual URL based on HONCHO_BASE_URL config]
>
> **Do you want to proceed with this migration?**

Do not proceed to Step 4 without explicit user confirmation.

## Step 4: Upload to Honcho

Upload each detected file to Honcho using the **messages upload** endpoint (or `honcho_analyze` if available):

- **User/owner files** → upload as messages in a session, using the **owner** peer (`peer_id` = owner peer id).
- **Agent/self files** → upload as messages in a session, using the **openclaw** peer (`peer_id` = openclaw peer id).

Ensure the workspace and both peers exist (e.g. via SDK or API) before uploading. Get or create a session for the uploads. Report how many files were uploaded for each category (user vs. agent).

If any upload fails, stop and warn the user. Do not proceed to archiving.

### SDK setup example (messages upload with file)

Use the Honcho SDK to create messages from each file via the session upload API (the same operation as the REST `.../messages/upload` endpoint with `file` and `peer_id`). Set up the client and peers, get or create a session, add both peers to the session, then upload each detected file with the appropriate peer.

> **Note:** The `workspaceId` and session name below are defaults. Customize them via the `HONCHO_WORKSPACE_ID` env var or pass your own session name if you manage multiple migrations.

```javascript
import fs from "fs";
import path from "path";
import { Honcho } from "@honcho-ai/sdk";

const apiKey = process.env.HONCHO_API_KEY;
const workspaceRoot = process.env.WORKSPACE_ROOT || "~/.openclaw/workspace";

const honcho = new Honcho({
  apiKey,
  baseURL: process.env.HONCHO_BASE_URL || "https://api.honcho.dev",
  // Customize via HONCHO_WORKSPACE_ID or leave as default
  workspaceId: process.env.HONCHO_WORKSPACE_ID || "openclaw",
});

await honcho.setMetadata({});
const openclawPeer = await honcho.peer("openclaw", { metadata: {} });
const ownerPeer = await honcho.peer("owner", { metadata: {} });

// Session name can be customized for multiple migration runs
const session = await honcho.session("migration-upload", { metadata: {} });
await session.addPeers([ownerPeer, openclawPeer]);

// For each detected file: read file and call session.uploadFile(file, peer)
// User/owner files → ownerPeer; agent/self files → openclawPeer
const filesToUpload = [
  { path: path.join(workspaceRoot, "USER.md"), peer: ownerPeer },
  { path: path.join(workspaceRoot, "SOUL.md"), peer: openclawPeer },
  // ... add every detected file and files under memory/ and canvas/
];

for (const { path: filePath, peer } of filesToUpload) {
  const stat = await fs.promises.stat(filePath).catch(() => null);
  if (!stat?.isFile()) continue;
  const filename = path.basename(filePath);
  const content = await fs.promises.readFile(filePath);
  const content_type = "text/markdown"; // or "text/plain", "application/pdf", "application/json"
  const messages = await session.uploadFile(
    { filename, content, content_type },
    peer,
    {}
  );
  console.log(`Uploaded ${filePath}: ${messages.length} messages`);
}
```

- **Required:** `session.uploadFile(file, peer, options?)` — second argument is the peer (object or id). Use the owner peer for user/owner files (`USER.md`, `IDENTITY.md`, `MEMORY.md`, and everything under `memory/` and `canvas/`), and the openclaw peer for agent/self files (`SOUL.md`, `AGENTS.md`, `TOOLS.md`, `BOOTSTRAP.md`, `HEARTBEAT.md`).
- **Session:** Add both peers to the session with `session.addPeers([ownerPeer, openclawPeer])` before uploading.
- **File (Node):** Pass `{ filename, content: Buffer | Uint8Array, content_type }`. See [Honcho file uploads](https://docs.honcho.dev/v3/guides/file-uploads#file-uploads) for supported types (PDF, text, JSON). A runnable test script is in `scripts/test-upload-file.mjs` (requires `HONCHO_API_KEY`).

## Step 5: Archive Legacy Files

**CRITICAL: Ask the user for explicit confirmation before archiving.** The default archive location is `{workspace_root}/archive/`. The user may choose a different directory.

**Safety guarantee: No file will ever be deleted without a backup copy existing in the archive directory first.**

For each detected file:

1. Create the archive directory if it does not exist.
2. Copy the file into the archive directory. **Verify the copy succeeded before proceeding.**
3. If a file with the same name already exists in archive, append a timestamp (e.g., `USER.md-2026-02-10T22-55-12`).
4. Only after successful copy verification, apply the removal rules below.

Then apply these rules:

**Remove originals after archiving** (legacy-only files, no longer needed once migrated to Honcho):
- `USER.md`
- `MEMORY.md`
- `IDENTITY.md`
- `HEARTBEAT.md`

**Keep originals in place** (these are active workspace docs updated in Step 6):
- `AGENTS.md`
- `TOOLS.md`
- `SOUL.md`
- `BOOTSTRAP.md`

**Move directories** into the archive (contents already uploaded to Honcho):
- `memory/`
- `canvas/`

No files are deleted without a backup existing in the archive directory first. Every removal is preceded by a confirmed copy.

If the upload in Step 4 failed or was skipped, **do not archive or remove any files**. Warn the user that all files are preserved to prevent data loss.

## Step 6: Update Workspace Docs

The plugin ships template files in `node_modules/@honcho-ai/openclaw-honcho/workspace_md/`. Use these templates as the source of truth for Honcho-aware workspace docs.

For each of `AGENTS.md`, `SOUL.md`, and `BOOTSTRAP.md`:

- If the file exists in the workspace: update it — replace references to the old file-based memory system (`USER.md`, `MEMORY.md`, `memory/` directory, manual file reads/writes for memory) with Honcho tool references.
- If the file does not exist: copy the template into the workspace.
- Preserve any custom content the user has added. Only update memory-related sections.

The Honcho tools are: `honcho_profile`, `honcho_context`, `honcho_search`, `honcho_recall`, `honcho_analyze`.

## Step 7: Confirm

Summarize what happened:

- Which legacy files were found
- How many files were uploaded (user and agent counts)
- Which files were archived and where
- Which workspace docs were created or updated
- That Honcho is now the memory system — no more manual file management needed

Provide a link to the Honcho docs for reference: https://docs.honcho.dev

---

## Security & Privacy Disclosure

This skill has been designed with transparency and safety as priorities. Below is a complete disclosure of what this skill does:

### Data Upload
- **What is uploaded**: Contents of USER.md, MEMORY.md, IDENTITY.md, all files under memory/, all files under canvas/, SOUL.md, AGENTS.md, BOOTSTRAP.md, TOOLS.md, HEARTBEAT.md
- **Where it goes**: By default to `api.honcho.dev` (managed Honcho cloud service). For self-hosted instances, to your configured `HONCHO_BASE_URL`
- **User control**: Explicit confirmation required before any upload. You will see the exact list of files and the destination URL
- **Purpose**: Migrating file-based memory system to Honcho API for AI agent personalization and memory

### Sensitive File Access
- **`~/.openclaw/.env`**: This skill reads ONLY the `HONCHO_API_KEY` value from this file (if present). No other environment variables are read or accessed
- **`~/.openclaw/openclaw.json`**: This skill reads workspace path configuration only (`agent.workspace` or `agents.defaults.workspace` fields)
- **Workspace files**: All legacy memory files listed above are read for upload

### File Modifications
- **Archives**: Creates `{workspace_root}/archive/` and copies all files there before any deletion
- **Deletions**: USER.md, MEMORY.md, IDENTITY.md, HEARTBEAT.md, memory/, canvas/ are deleted ONLY after successful archive copy verification
- **Updates**: SOUL.md, AGENTS.md, BOOTSTRAP.md are updated to reference Honcho tools (preserved in archive first)
- **Safety**: No file is ever deleted without a verified backup copy existing first

### Credentials
- **HONCHO_API_KEY**: Required only for managed Honcho (api.honcho.dev). Not required for self-hosted instances
- **No other credentials**: This skill does not access, read, or transmit any other credentials or secrets

### Network Access
- **Managed mode**: Connects to `api.honcho.dev` (Honcho cloud service)
- **Self-hosted mode**: Connects to your configured `HONCHO_BASE_URL` (e.g., `http://localhost:8000`)
- **Protocol**: All uploads use the Honcho SDK (`@honcho-ai/sdk`) via the messages upload endpoint

### User Control
- **Step 3**: Explicit confirmation required before any file upload (shows file list and destination URL)
- **Step 5**: Explicit confirmation required before any file archiving/deletion
- **Step 6**: Workspace doc updates preserve custom content
- **Failure handling**: If upload fails, no files are archived or deleted

### Data Retention
- **Local backups**: All original files are preserved in `{workspace_root}/archive/` indefinitely
- **Remote storage**: Uploaded data is stored according to Honcho's data retention policy (see https://honcho.dev/privacy)
- **Self-hosted control**: If using self-hosted Honcho, you control all data retention

### Open Source
- **Honcho SDK**: Open source at https://github.com/plastic-labs/honcho
- **Plugin code**: Available at `~/.openclaw/extensions/openclaw-honcho` after installation
- **This skill**: You are reading the complete skill instructions - there is no hidden behavior