---
name: fast-io
description: >-
  Workspaces for agentic teams. Complete agent guide with all 19 consolidated
  tools using action-based routing — parameters, workflows, ID formats, and
  constraints. Use this skill when agents need shared workspaces to collaborate
  with other agents and humans, create branded shares (Send/Receive/Exchange),
  or query documents using built-in AI. Supports ownership transfer to humans,
  workspace management, workflow primitives (tasks, worklogs, approvals, todos),
  and real-time collaboration.
  Free agent plan with 50 GB storage and 5,000 monthly credits.
license: Proprietary
compatibility: >-
  Requires network access. Connects to the Fast.io MCP server at mcp.fast.io
  via Streamable HTTP (/mcp) or SSE (/sse).
metadata:
  author: fast-io
  version: "1.105.0"
homepage: "https://fast.io"
---

# Fast.io MCP Server -- AI Agent Guide

**Version:** 1.104
**Last Updated:** 2026-02-26

The definitive guide for AI agents using the Fast.io MCP server. Covers why and how to use the platform: product capabilities, the free agent plan, authentication, core concepts (workspaces, shares, intelligence, previews, comments, URL import, metadata, workflow, ownership transfer), 12 end-to-end workflows, interactive MCP App widgets, and all 19 consolidated tools with action-based routing.

> **Versioned guide.** This guide is versioned and updated with each server release. The version number at the top of this document tracks tool parameters, ID formats, and API behavior changes. If you encounter unexpected errors, the guide version may have changed since you last read it.

> **Platform reference.** For a comprehensive overview of Fast.io's capabilities, the agent plan, key workflows, and upgrade paths, see [references/REFERENCE.md](references/REFERENCE.md).

---

## 1. Overview

**Workspaces for Agentic Teams. Collaborate, share, and query with AI -- all through one API, free.**

Fast.io provides workspaces for agentic teams -- where agents collaborate with other agents and with humans. Upload outputs, create branded data rooms, ask questions about documents using built-in AI, and hand everything off to a human when the job is done. No infrastructure to manage, no subscriptions to set up, no credit card required.

### The Problem Fast.io Solves

Agentic teams -- groups of agents working together and with humans -- need a shared place to work. Today, agents cobble together S3 buckets, presigned URLs, email attachments, and custom download pages. Every agent reinvents collaboration, and there is no shared workspace where agents and humans can see the same files, track activity, and hand off work.

When agents need to *understand* documents -- not just store them -- they have to download files, parse dozens of formats, build search indexes, and manage their own RAG pipeline. That is a lot of infrastructure for what should be a simple question: "What does this document say?"

| Problem | Fast.io Solution |
|---------|-----------------|
| No shared workspace for agentic teams | Workspaces where agents and humans collaborate with file preview, versioning, and AI |
| Agent-to-agent coordination lacks structure | Shared workspaces with activity feeds, comments, and real-time sync across team members |
| Sharing outputs with humans is awkward | Purpose-built shares (Send, Receive, Exchange) with link sharing, passwords, expiration |
| Collecting files from humans is harder | Receive shares let humans upload directly to your workspace -- no email attachments |
| Understanding document contents | Built-in AI reads, summarizes, and answers questions about your files |
| Building a RAG pipeline from scratch | Enable intelligence on a workspace and documents are automatically indexed, summarized, and queryable |
| Finding the right file in a large collection | Semantic search finds documents by meaning, not just filename |
| Handing a project off to a human | One-click ownership transfer -- human gets the org, agent keeps admin access |
| Tracking what happened | Full audit trail with AI-powered activity summaries |
| Cost | Free. 50 GB storage, 5,000 monthly credits, no credit card |

### MCP Server

This MCP server exposes 19 consolidated tools that cover the full Fast.io REST API surface. Every authenticated API endpoint has a corresponding tool action, and the server handles session management automatically.

Once a user authenticates, the auth token is stored in the server session and automatically attached to all subsequent API calls. There is no need to pass tokens between tool invocations.

### Server Endpoints

- **Production:** `mcp.fast.io`
- **Development:** `mcp.fastdev1.com`

Two transports are available on each:

- **Streamable HTTP at `/mcp`** -- the preferred transport for new integrations.
- **SSE at `/sse`** -- a legacy transport maintained for backward compatibility.

### MCP Resources

The server exposes static MCP resources, widget resources, and file download resource templates. Clients can read them via `resources/list` and `resources/read`:

| URI | Name | Description | MIME Type |
|-----|------|-------------|-----------|
| `skill://guide` | skill-guide | Full agent guide (this document) with all 19 tools, workflows, and platform documentation | `text/markdown` |
| `session://status` | session-status | Current authentication state: `authenticated` boolean, `user_id`, `user_email`, `token_expires_at` (Unix epoch), `token_expires_at_iso` (ISO 8601), `scopes` (raw scope string or null), `scopes_detail` (array of hydrated scope objects with entity names/domains/parents, or null), `agent_name` (string or null) | `application/json` |
| `widget://*` | Widget HTML | Interactive HTML5 widgets (5 total) -- use the `apps` tool to discover and launch | `text/html` |

**File download resource templates** -- read file content directly through MCP without needing external HTTP access:

| URI Template | Name | Auth | Dynamic Listing | Description |
|---|---|---|---|---|
| `download://workspace/{workspace_id}/{node_id}` | download-workspace-file | Session token | Yes | Download a file from a workspace |
| `download://share/{share_id}/{node_id}` | download-share-file | Session token | Yes | Download a file from a share |
| `download://quickshare/{quickshare_id}` | download-quickshare-file | None (public) | No | Download a quickshare file |

Files up to 50 MB are returned inline as base64-encoded blob content. Larger files return a text fallback with a URL to the HTTP pass-through endpoint (see below). The `download` tool responses include a `resource_uri` field with the appropriate URI for each file.

**Dynamic resource listing:** When authenticated, workspace and share file resources are dynamically listed via `resources/list`. MCP clients (such as Claude Desktop's `@` mention picker) can discover available files without any tool calls. Up to 10 workspaces and 10 shares are enumerated, with up to 25 most recently updated root-level files from each. Resources appear as "WorkspaceName / filename.ext" or "ShareTitle / filename.ext". Results are cached for 1 minute per session. Only root-level files are listed -- subdirectories are not recursively enumerated. Use the `storage` tool with action `list` to browse deeper. The quickshare template remains template-only and is not dynamically enumerable.

### MCP Prompts

The server registers MCP prompts that appear in the client's "Add From" / "+" menu as user-clickable app launchers. These are primarily for desktop MCP clients (e.g., Claude Desktop); code-mode clients (Claude Code, Cursor) do not surface prompts.

| Prompt Name | Description |
|---|---|
| `App: Choose Workspace or Org` | Launch the Workspace Picker to browse orgs, select workspaces, and manage shares |
| `App: Pick a File` | Launch the File Picker with built-in workspace navigator for browsing, searching, and selecting files |
| `App: Open Workflow` | Launch the Workflow Manager (auto-selects workspace if only one, otherwise opens Workspace Picker first) |
| `App: Available Apps` | List all available MCP App widgets with descriptions and launch instructions |

### HTTP File Pass-Through

For files larger than 50 MB or when raw binary streaming is needed, the server provides an HTTP pass-through endpoint that streams file content directly from the API:

| Endpoint | Auth | Description |
|---|---|---|
| `GET /file/workspace/{workspace_id}/{node_id}` | `Mcp-Session-Id` header | Stream a workspace file |
| `GET /file/share/{share_id}/{node_id}` | `Mcp-Session-Id` header | Stream a share file |
| `GET /file/quickshare/{quickshare_id}` | None (public) | Stream a quickshare file |

The response includes proper `Content-Type`, `Content-Length`, and `Content-Disposition` headers from the upstream API. Errors are returned as HTML pages. The `Mcp-Session-Id` header is the same session identifier used for MCP protocol communication.

### Workflow Overview

The server includes workflow features for project tracking: **tasks** (structured work items with priorities and assignees), **worklogs** (append-only activity logs), **approvals** (formal sign-off requests), and **todos** (simple checklists). Enable workflow on a workspace with `workspace` action `enable-workflow` before using these tools. See the **Full Agent Workflow** recipe in section 6 for the complete pattern.

**Best practice (IMPORTANT):** After state-changing actions (uploading files, creating shares, changing task status, member changes, file moves/deletes), append a worklog entry describing what you did and why. Without worklog entries, agent work is invisible to humans reviewing the workspace. For multiple related actions (e.g., uploading several files), you may log once after the batch completes rather than after each individual action. Worklog entries are append-only and permanent.

### Additional References

- **Agent guide (this file):** `/skill.md` on the MCP server -- tool documentation, workflows, and constraints.
- **REST API reference:** `https://api.fast.io/llms.txt` -- endpoint documentation for the underlying Fast.io API.
- **Platform guide:** [references/REFERENCE.md](references/REFERENCE.md) -- capabilities, agent plan details, key workflows, and upgrade paths.

---

## 2. Authentication (Critical First Step)

Authentication is required before calling any tool except these unauthenticated tools:

- `auth` with actions: `signin`, `signup`, `set-api-key`, `pkce-login`, `email-check`, `password-reset-request`, `password-reset`
- `download` with action: `quickshare-details`

### Choosing the Right Approach

There are three ways to use Fast.io as an agent, depending on whether you are operating autonomously or assisting an existing human user.

**Option 1: Autonomous Agent -- Create an Agent Account**

If you are operating independently (storing files, running workflows, building workspaces for users), create your own agent account with `auth` action `signup`. Agent accounts get the free agent plan (50 GB, 5,000 monthly credits) and can transfer orgs to humans when ready. This is the recommended path for autonomous agents. See **Agent Account Creation** below for steps.

**Option 2: Assisting a Human -- Use Their API Key**

If a human already has a Fast.io account and wants your help managing their files, workspaces, or shares, they can create an API key for you to use. No separate agent account is needed -- you operate as the human user. The human creates a key at Settings -> Devices & Agents -> API Keys (direct link: `https://go.fast.io/settings/api-keys`). Call `auth` with action `set-api-key` and the key to authenticate -- the key is validated and stored in the session automatically. API keys work as Bearer tokens and by default have the same permissions as the account owner. Keys can optionally be scoped to specific organizations, workspaces, or shares (using the same scope system as OAuth tokens), tagged with an `agent_name` for tracking, and given an expiration date. Unscoped keys do not expire unless revoked. Agents can also manage API keys programmatically with `auth` actions `api-key-create`, `api-key-update`, `api-key-list`, `api-key-get`, and `api-key-delete`.

**Option 3: Agent Account Invited to a Human's Org**

If you want your own agent identity but need to work within a human's existing organization, create an agent account with `auth` action `signup`, then have the human invite you to their org with `member` action `add` (entity_type `org`) or to a workspace with `member` action `add` (entity_type `workspace`). Alternatively the human can invite via the UI: Settings -> Your Organization -> Manage People. This gives you access to their workspaces and shares while keeping your own account separate. After accepting invitations with `user` action `accept-all-invitations`, use `auth` action `signin` to authenticate normally. **Note:** If the human only invites you to a workspace (not the org), the org will appear as external -- see **Internal vs External Orgs** in the Organizations section.

**Option 4: Browser Login (PKCE)**

If you prefer not to send a password through the agent, use browser-based PKCE login. Call `auth` action `pkce-login` (optionally with an `email` hint) to get a login URL. The user opens the URL in a browser, signs in (email/password or SSO like Google/Microsoft), and approves access. The browser displays an authorization code which the user copies back to the agent. Call `auth` action `pkce-complete` with the code to finish signing in. This is the most secure option -- no credentials pass through the agent.

PKCE login supports optional **scoped access** via the `scope_type` parameter. By default, `scope_type` is `"user"` (full account access). Other scope types restrict the token to specific entity types:

| scope_type | Access granted |
|------------|---------------|
| `user` | Full account access (default) |
| `org` | User selects specific organizations |
| `workspace` | User selects specific workspaces |
| `all_orgs` | All organizations the user belongs to |
| `all_workspaces` | All workspaces the user has access to |
| `all_shares` | All shares the user is a member of (`share:*:<mode>`) |

**Scope inheritance:** Broader scopes include access to child entities automatically:

- `all_orgs` includes all orgs + all workspaces + all shares within those orgs
- `all_workspaces` includes all workspaces + all shares within those workspaces
- `org` scope on a specific org includes access to all workspaces and shares within that org
- `workspace` scope on a specific workspace includes access to shares within that workspace
- `all_shares` grants direct access to all shares the user has membership in, bypassing workspace/org inheritance

The `agent_name` parameter controls what the user sees on the approval screen -- the screen displays "**[agent_name]** will act on your behalf". If omitted, only the client name is shown. Use a descriptive name so the user knows which agent is requesting access.

**Approval flow by scope_type:**

- **`user`** (default): Full account access. The user sees a simple approve/decline prompt with no entity picker.
- **`org`**, **`workspace`**: The user sees an entity selection screen listing their accessible entities with checkboxes, plus a read-only / read-write toggle. The user picks which entities to grant, then approves or declines.
- **`all_orgs`**, **`all_workspaces`**, **`all_shares`**: The user sees a summary of the wildcard access being requested (no entity picker), then approves or declines.

The MCP server defaults to `scope_type="user"` for backward compatibility.

| Scenario | Recommended Approach |
|----------|---------------------|
| Operating autonomously, storing files, building for users | Create an agent account with your own org (Option 1) |
| Helping a human manage their existing account | Ask the human to create an API key for you (Option 2) |
| Working within a human's org with your own identity | Create an agent account, have the human invite you (Option 3) |
| Building something to hand off to a human | Create an agent account, build it, then transfer the org (Option 1) |
| Signing in without sending a password through the agent | Browser-based PKCE login (Option 4) |

**Credit limits by account type:** Agent accounts (Options 1, 3) can transfer orgs to humans when credits run out -- see Ownership Transfer in section 3. Human accounts (Option 2) cannot use the transfer/claim API; direct the human to upgrade their plan at `https://go.fast.io/settings/billing` or via `org` action `billing-create`.

### Standard Sign-In Flow

1. Call `auth` with action `signin`, `email` and `password`.
2. The server returns a JWT `auth_token` and stores it in the session automatically.
3. All subsequent tool calls use this token without any manual passing.

### Agent Account Creation

When creating a new account (Options 1 and 3 above), agents **MUST** use `auth` action `signup` which automatically registers with `agent=true`. Never sign up as a human account. Agent accounts provide:

- `account_type` set to `"agent"`
- Free agent plan assigned automatically
- Transfer/claim workflow enabled for handing orgs off to humans

**Steps:**

1. Optionally call `auth` action `email-check` with the desired `email` to verify it is available for registration before attempting signup.
2. Call `auth` action `signup` with `first_name`, `last_name`, `email`, and `password`. The `agent=true` flag is sent automatically by the MCP server.
3. The account is created and a session is established automatically -- the agent is signed in immediately.
4. **Verify your email** (required before using most endpoints): Call `auth` action `email-verify` with `email` to send a verification code, then call `auth` action `email-verify` again with `email` and `email_token` to validate the code.
5. No credit card is required. No trial period. No expiration. The account persists indefinitely.

### Two-Factor Authentication Flow

1. Call `auth` action `signin` with `email` and `password`.
2. If the response includes `two_factor_required: true`, the returned token has limited scope.
3. Call `auth` action `2fa-verify` with the 2FA `code` (TOTP, SMS, or WhatsApp).
4. The server replaces the limited-scope token with a full-scope token automatically.

### Browser Login (PKCE) Flow

1. Call `auth` action `pkce-login` (optionally with `email` to pre-fill the sign-in form, `scope_type` to request scoped access, and `agent_name` to identify the agent).
2. The tool returns a `login_url` -- present it to the user to open in a browser.
3. The user signs in (email/password or SSO).
4. The user sees the approval screen showing the `agent_name` (or client name if not provided). Depending on `scope_type`: for `user` they simply approve; for `org`/`workspace` they select specific entities and read-only/read-write access; for `all_orgs`/`all_workspaces`/`all_shares` they review the wildcard access summary.
5. The user clicks Approve. The browser displays an authorization code. The user copies it.
6. Call `auth` action `pkce-complete` with the `code` to exchange it for an access token.
7. The session is established automatically -- all subsequent tool calls are authenticated. If scoped access was granted, `scopes` and `agent_name` are included in the response and stored in the session.

### Checking Session Status

- `auth` action `status` -- checks the local Durable Object session. No API call is made. Returns authentication state, user ID, email, token expiry, scopes, and agent_name.
- `auth` action `check` -- validates the token against the Fast.io API. Returns the user ID if the token is still valid.

### Session Expiry

JWT tokens last **1 hour**. API keys do not expire by default, but can optionally have an expiration set via `api-key-create` or `api-key-update` with the `key_expires` parameter. When a JWT session expires or a time-limited API key expires, tool calls return a clear error indicating that re-authentication is needed. Call `auth` action `signin` again to establish a new session. The MCP server does not auto-refresh tokens.

**Tip:** For long-running sessions, use `auth` action `status` to check remaining token lifetime before starting a multi-step workflow. If the token is close to expiring, re-authenticate first to avoid mid-workflow interruptions.

### Signing Out

Call `auth` action `signout` to clear the stored session from the Durable Object.

---

## 3. Core Concepts

### Organizations

Organizations are top-level containers that collect workspaces. An organization can represent a company, a business unit, a team, or simply your own personal collection. Every user belongs to one or more organizations. Organizations have:

- **Workspaces** — the file storage containers that belong to the organization.
- **Members** with roles: owner, admin, member, guest, view.
- **Billing and subscriptions** managed through Stripe integration.
- **Plan limits** that govern storage, transfer, AI tokens, and member counts.

Organizations are identified by a 19-digit numeric profile ID or a domain string.

**IMPORTANT:** When creating orgs, agents MUST use `org` action `create` which automatically assigns `billing_plan: "agent"`. This ensures the org gets the free agent plan (50 GB, 5,000 credits/month). Do not use any other billing plan for agent-created organizations.

#### Org Discovery (IMPORTANT)

To discover all available orgs, agents **must call both actions**:

1. `org` action `list` -- returns internal orgs where you are a direct member (`member: true`)
2. `org` action `discover-external` -- returns external orgs you access via workspace membership only (`member: false`)

**An agent that only checks `org` action `list` will miss external orgs entirely and won't discover the workspaces it's been invited to.** External orgs are the most common pattern when a human invites an agent to help with a specific project -- they add the agent to a workspace but not to the org itself.

#### Internal vs External Orgs

**Internal orgs** (`member: true`) -- orgs you created or were invited to join as a member. You have org-level access: you can see all workspaces (subject to permissions), manage settings if you're an admin, and appear in the org's member list.

**External orgs** (`member: false`) -- orgs you can access only through workspace membership. You can see the org's name and basic public info, but you cannot manage org settings, see other workspaces, or add members at the org level. Your access is limited to the specific workspaces you were explicitly invited to.

**Example:** A human invites your agent to their "Q4 Reports" workspace. You can upload files, run AI queries, and collaborate in that workspace. But you cannot create new workspaces in their org, view their billing, or access their other workspaces. The org shows up via `org` action `discover-external` -- not `org` action `list`. If the human later invites you to the org itself, the org moves from external to internal.

### Workspaces

Workspaces are file storage containers within organizations. Each workspace has:

- Its own set of **members** with roles (owner, admin, member, guest).
- A **storage tree** of files and folders (storage nodes).
- Optional **AI features** for RAG-powered chat.
- **Shares** that can be created within the workspace.
- **Archive/unarchive** lifecycle management.
- **50 GB included storage** on the free agent plan, with files up to 1 GB per upload.
- **File versioning** -- every edit creates a new version, old versions are recoverable.
- **Full-text and semantic search** -- find files by name or content, and documents by meaning.

Workspaces are identified by a 19-digit numeric profile ID.

#### Intelligence: On or Off

Workspaces have an **intelligence** toggle that controls whether AI features are active:

**Intelligence OFF** -- the workspace is pure file storage. You can still attach files directly to an AI chat conversation (up to 20 files, 200 MB total), but files are not persistently indexed. This is fine for simple storage and sharing where you do not need to query your content.

**Intelligence ON** -- the workspace becomes an AI-powered knowledge base. Every document and code file uploaded is automatically ingested, summarized, and indexed for RAG. This enables:

- **RAG (retrieval-augmented generation)** -- scope AI chat to entire folders or the full workspace and ask questions across your indexed documents and code. The AI retrieves relevant passages and answers with citations.
- **Semantic search** -- find files by meaning, not just keywords. "Show me contracts with indemnity clauses" works even if those exact words do not appear in the filename.
- **Auto-summarization** -- short and long summaries generated for every indexed document and code file, searchable and visible in the UI.
- **Metadata extraction** -- AI pulls key metadata from documents automatically.

> **Coming soon:** RAG indexing support for images, video, and audio files. Currently only documents and code are indexed.

Intelligence defaults to ON for workspaces created via the API by agent accounts. If the workspace is only used for file storage and sharing, disable it to conserve credits. If you need to query your content, leave it enabled.

**Agent use case:** Create a workspace per project or client. Enable intelligence if you need to query the content later. Upload reports, datasets, and deliverables. Invite other agents and human stakeholders. Everything is organized, searchable, and versioned.

For full details on AI chat types, file context modes, AI state, and how intelligence affects them, see the **AI Chat** section below.

### Shares

Shares are purpose-built spaces for exchanging files with people outside your workspace. They can exist within workspaces and have three types:

| Mode | What It Does | Agent Use Case |
|------|-------------|----------------|
| **Send** | Recipients can download files | Deliver reports, exports, generated content |
| **Receive** | Recipients can upload files | Collect documents, datasets, user submissions |
| **Exchange** | Both upload and download | Collaborative workflows, review cycles |

#### Share Features

- **Password protection** -- require a password for link access
- **Expiration dates** -- shares auto-expire after a set period
- **Download controls** -- enable or disable file downloads
- **Access levels** -- Members Only, Org Members, Registered Users, or Public (anyone with the link)
- **Custom branding** -- background images, gradient colors, accent colors, logos
- **Post-download messaging** -- show custom messages and links after download
- **Up to 3 custom links** per share for context or calls-to-action
- **Guest chat** -- let share recipients ask questions in real-time
- **AI-powered auto-titling** -- shares automatically generate smart titles from their contents
- **Activity notifications** -- get notified when files are sent or received
- **Comment controls** -- configure who can see and post comments (owners, guests, or both)

#### Two Storage Modes

When creating a share with `share` action `create`, the `storage_mode` parameter determines how files are stored:

- **`room`** (independent storage, default) -- The share has its own isolated storage. Files are added directly to the share and are independent of any workspace. This creates a self-contained data room -- changes to workspace files do not affect the room, and vice versa. Use for final deliverables, compliance packages, archived reports, or any scenario where you want an immutable snapshot.

- **`shared_folder`** (workspace-backed) -- The share is backed by a specific folder in a workspace. The share displays the live contents of that folder -- any files added, updated, or removed in the workspace folder are immediately reflected in the share. No file duplication, so no extra storage cost. To create a shared folder, pass `storage_mode=shared_folder` and `folder_node_id={folder_opaque_id}` when creating the share. **Note:** Expiration dates are not allowed on shared folder shares since the content is live.

Both modes look the same to share recipients -- a branded data room with file preview, download controls, and all share features. The difference is whether the content is a snapshot (room) or a live view (shared folder).

Shares are identified by a 19-digit numeric profile ID.

**Agent use case:** Generate a quarterly report, create a Send share with your client's branding, set a 30-day expiration, and share the link. The client sees a professional, branded page with instant file preview -- not a raw download link.

### Storage Nodes

Files and folders are represented as storage nodes. Each node has an opaque ID (a 30-character alphanumeric string, displayed with hyphens, e.g. `f3jm5-zqzfx-pxdr2-dx8z5-bvnb3-rpjfm4`). The special value `root` refers to the root folder of a workspace or share, and `trash` refers to the trash folder.

Key operations on storage nodes: list, create-folder, move, copy, rename, delete (moves to trash), purge (permanently deletes), restore (recovers from trash), search, add-file (link an upload), and add-link (create a share reference).

Nodes have versions. Each file modification creates a new version. Version history can be listed and files can be restored to previous versions.

**Conflict resolution (REPLACE by default):** When a file operation encounters an existing file with the same name in the target folder, the default behavior is to **replace** (overwrite) the existing file:

- **Upload (addfile)** -- silently overwrites the existing file. The previous content is preserved as a version entry, recoverable via `storage` action `version-list` / `version-restore`.
- **Move / Copy** -- trashes the existing conflicting file, then completes the operation. The old file is recoverable from trash.
- **Restore from trash** -- trashes the existing conflicting file, then restores.
- **Folder conflicts and type mismatches** (file vs folder) still fall back to rename (e.g. `folder (2)`).

This means uploading a file with the same name as an existing file will **overwrite it**, not create a renamed copy like `report (2).pdf`. If you need multiple files with the same name to coexist, rename them before uploading.

### Notes

Notes are a storage node type (alongside files and folders) that store markdown content directly on the server. They live in the same folder hierarchy as files, are versioned like any other node, and appear in storage listings with `type: "note"`.

#### Creating and Updating Notes

Create notes with `workspace` action `create-note`, read with `workspace` action `read-note`, and update with `workspace` action `update-note`.

**Creating:** Provide `workspace_id`, `parent_id` (folder opaque ID or `"root"`), `name` (must end in `.md`, max 100 characters), and `content` (markdown text, max 100 KB).

**Reading:** Provide `workspace_id` and `node_id`. Returns the note's markdown content and metadata.

**Updating:** Provide `workspace_id`, `node_id`, and at least one of `name` (must end in `.md`) or `content` (max 100 KB).

| Constraint | Limit |
|------------|-------|
| Content encoding | Valid UTF-8 (UTF8MB4). Invalid byte sequences and control characters (`\p{C}` except `\t`, `\n`, `\r`) are stripped. |
| Content size | 100 KB max |
| Filename | 1-100 characters, must end in `.md` |
| Markdown validation | Code blocks and emphasis markers must be balanced |
| Rate limit | 2 per 10s, 5 per 60s |

#### Notes as Long-Term Knowledge Grounding

In an intelligent workspace, notes are automatically ingested and indexed just like uploaded documents. This makes notes a way to bank knowledge over time -- any facts, context, or decisions stored in notes become grounding material for future AI queries.

When an AI chat uses folder scope (or defaults to the entire workspace), notes within that scope are searched alongside files. The AI retrieves relevant passages from notes and cites them in answers.

Key behaviors:

- Notes are ingested for RAG when workspace intelligence is enabled
- Notes within a folder scope are included in scoped queries
- Notes with `ai_state: ready` are searchable via RAG
- Notes can also be attached directly to a chat via `files_attach` (check `ai.attach` is `true` in storage details)

**Use cases:**

- Store project context, decisions, and rationale. Months later, ask "Why did we choose vendor X?" and the AI retrieves the note.
- Save research findings in a note. Future AI chats automatically use those findings as grounding.
- Create reference documents (style guides, naming conventions) that inform all future AI queries in the workspace.

#### Other Note Operations

Notes support the same storage operations as files and folders: move (via `storage` action `move`), copy (`storage` action `copy`), delete/trash (`storage` action `delete`), restore (`storage` action `restore`), version history (`storage` action `version-list`), and details (`storage` action `details`).

#### Linking Users to Notes

- **Note in workspace context** (opens workspace with note panel): `https://{domain}.fast.io/workspace/{folder_name}/storage/root?note={note_id}`
- **Note preview** (standalone view): `https://{domain}.fast.io/workspace/{folder_name}/preview/{note_id}`

### AI Chat

AI chat lets agents ask questions about files stored in workspaces and shares. Two chat types are available, each with different file context options.

**AI chat is read-only.** It can read, analyze, search, and answer questions about file contents, but it cannot modify files, change workspace settings, manage members, or access events. Any action beyond reading file content — uploading, deleting, moving files, changing settings, managing shares, reading events — must be done through the MCP tools directly. Do not attempt to use AI chat as a general-purpose tool for workspace management.

#### Two Chat Types

- **`chat`** — Basic AI conversation with no file context from the workspace index. Use for general questions only.
- **`chat_with_files`** — AI grounded in your files. Two mutually exclusive modes for providing file context:
  - **Folder/file scope (RAG)** — limits the retrieval search space. Requires intelligence enabled; files must be in `ready` AI state.
  - **File attachments** — files read directly by the AI. No intelligence required; files must have `ai.attach: true` in storage details (the file must be a supported type for AI analysis). Max 20 files, 200 MB total.

**Auto-promotion:** If you create a chat with `type=chat` but include `files_scope`, `folders_scope`, or `files_attach`, the system automatically promotes the type to `chat_with_files`. You don't need to worry about setting the type exactly right — the intent is unambiguous when file parameters are present.

Both types augment answers with web knowledge when relevant.

#### File Context: Scope vs Attachments

For `chat_with_files`, choose one of these mutually exclusive approaches:

| Feature | Folder/File Scope (RAG) | File Attachments |
|---------|------------------------|------------------|
| How it works | Limits RAG search space | Files read directly by AI |
| Requires intelligence | Yes | No |
| File readiness requirement | `ai_state: ready` | `ai.attach: true` |
| Best for | Many files, knowledge retrieval | Specific files, direct analysis |
| Max references | 100 folder refs (subfolder tree expansion) or 100 file refs | 20 files / 200 MB |
| Default (no scope given) | Entire workspace | N/A |

**Scope parameters** (REQUIRES intelligence — will error if intelligence is off):

- `folders_scope` — comma-separated `nodeId:depth` pairs (depth 1-10, max 100 subfolder refs). Defines a search boundary — the RAG backend finds documents within scoped folders automatically. Just pass folder IDs with depth; do not enumerate individual files. A folder with thousands of files and few subfolders works fine.
- `files_scope` — comma-separated `nodeId:versionId` pairs (max 100). Limits RAG to specific indexed files. nodeId is required; versionId is required in the pair format but will be **auto-resolved to the node's current version** if left empty (e.g., `nodeId:` with nothing after the colon). Get `versionId` from the file's `version` field in `storage` action `list` or `details` responses.
- **If neither is specified, the default scope is the entire workspace (all indexed documents).** This is the recommended default — omit scope parameters unless you specifically need to narrow the search.

**Attachment parameter** (no intelligence required):

- `files_attach` — comma-separated `nodeId:versionId` pairs (max 20, 200 MB total). nodeId is required; versionId will be **auto-resolved to the current version** if left empty. Files are read directly, not via RAG. **FILES ONLY: passing a folder nodeId returns a 406 error.** To include folder contents in AI context, use `folders_scope` instead (requires intelligence). **Only files with `ai.attach: true` in storage details can be attached** — check before using.

**Do not** list folder contents and pass individual file IDs as `files_scope` when you mean to search a folder — use `folders_scope` with the folder's nodeId instead. `files_scope` is only for targeting specific known file versions.

**Scope vs attach:** `files_scope` and `folders_scope` narrow the RAG search boundary and **require workspace intelligence to be enabled** — they will error on non-intelligent workspaces. `files_attach` sends files directly to the AI without indexing and works regardless of intelligence setting, but accepts only file nodeIds (not folders).

`files_scope`/`folders_scope` and `files_attach` are mutually exclusive — sending both will error.

#### Intelligence and AI State

The workspace intelligence toggle (see Workspaces above) controls whether uploaded documents and code files are auto-ingested, summarized, and indexed for RAG. When intelligence is enabled, each file has an `ai_state` indicating its readiness:

| State | Meaning |
|-------|---------|
| `disabled` | AI processing disabled for this file |
| `pending` | Queued for processing |
| `in_progress` | Currently being ingested and indexed |
| `ready` | Complete — available for folder/file scope queries |
| `failed` | Processing failed |

Only files with `ai_state: ready` are included in folder/file scope searches. Check file state via `storage` action `details` with `context_type: "workspace"`.

#### Attachability — the `ai.attach` Flag

File nodes in storage list/details responses include an `ai` object with three fields:

| Field | Type | Meaning |
|-------|------|---------|
| `ai.state` | string | AI indexing state (`disabled`, `pending`, `inprogress`, `ready`, `failed`) |
| `ai.attach` | boolean | Whether the file can be used with `files_attach` |
| `ai.summary` | boolean | Whether the file already has an AI-generated summary |

**Before using `files_attach`, check that `ai.attach` is `true`.** A file is attachable when its type supports AI analysis (documents, code, images, PDFs, spreadsheets, etc.) or when it already has a summary from prior processing. Files with `ai.attach: false` (unsupported formats, corrupt files, or files still processing) will be rejected by the API.

This flag is independent of the workspace intelligence setting — a file can have `ai.attach: true` even when intelligence is off.

**When to enable intelligence:** You need scoped RAG queries, cross-file search, auto-summarization, or a persistent knowledge base.

**When to disable intelligence:** The workspace is for storage/sharing only, or you only need to analyze specific files via attachments. Saves credits (ingestion costs 10 credits/page).

Even with intelligence off, `chat_with_files` with file attachments still works for files with `ai.attach: true`.

#### How to Phrase Questions

**With folder/file scope (RAG):** Write questions likely to match content in indexed files. The AI searches the scope, retrieves passages, and cites them.

- Good: "What are the payment terms in the vendor contracts?"
- Good: "Summarize the key findings from the Q3 analysis reports"
- Bad: "Tell me about these files" — too vague, no specific content to match
- Bad: "What's in this workspace?" — cannot meaningfully search for "everything"

**With file attachments:** Be direct — the AI reads the full file content. No retrieval step.

- "Describe this image in detail"
- "Extract all dates and amounts from this invoice"
- "Convert this CSV data into a summary table"

**Personality:** The `personality` parameter controls the tone and length of AI responses. Pass it when creating a chat or sending a message:

- `concise` — short, brief answers
- `detailed` — comprehensive answers with context and evidence (default)

Use `concise` when you need a quick fact, a yes/no answer, or a brief summary. Use `detailed` (or omit the parameter) when you need thorough analysis with supporting evidence and citations. The personality can also be overridden per follow-up message.

**Controlling verbosity in questions:** You can also guide verbosity through how you phrase the question itself:

- "In one sentence, what is the main conclusion of this report?"
- "List only the file names that mention GDPR compliance, no explanations"
- "Give me a brief summary — 2-3 bullet points max"

Combining `personality: "concise"` with a direct question produces the shortest answers and uses the fewest AI credits.

#### Chat Parameters

Create a chat with `ai` action `chat-create` (with `context_type: "workspace"`) or `ai` action `chat-create` (with `context_type: "share"`):

- `type` (required) — `chat` or `chat_with_files`
- `query_text` (required for workspace, optional for share) — initial message, 2-12,768 characters
- `personality` (optional) — `concise` or `detailed` (default: `detailed`)
- `privacy` (optional) — `private` or `public` (default: `public`)
- `files_scope` (optional) — `nodeId:versionId,...` (max 100, requires `chat_with_files` + intelligence). nodeId required; versionId auto-resolved if empty. **Omit to search all indexed documents (recommended default).**
- `folders_scope` (optional) — `nodeId:depth,...` (depth 1-10, max 100 subfolder refs, requires `chat_with_files` + intelligence). Folder scope = search boundary, not file enumeration. **Omit to search all indexed documents (recommended default).**
- `files_attach` (optional) — `nodeId:versionId,...` (max 20 / 200 MB, nodeId required, versionId auto-resolved if empty, mutually exclusive with scope params)

#### Follow-up Messages

Send follow-ups with `ai` action `message-send` (with `context_type: "workspace"` or `"share"`). The chat type is inherited from the parent chat. Each follow-up can update the scope, attachment, and personality parameters.

#### Waiting for AI Responses

After creating a chat or sending a message, the AI response is asynchronous. Message states progress: `ready` → `in_progress` → `complete` (or `errored`).

**Recommended:** Call `ai` action `message-read` (with `context_type: "workspace"` or `"share"`) with the returned `message_id`. The tool polls automatically (up to 15 attempts, 2-second intervals, ~30 seconds). If the response is still processing after that window, use `event` action `activity-poll` with the workspace/share ID instead of calling the read action in a loop — see Activity Polling in section 7.

#### Response Citations

Completed AI responses include citations pointing to source files:

- `nodeId` — storage node opaque ID
- `versionId` — file version opaque ID
- `entries[].page` — page number
- `entries[].snippet` — text excerpt
- `entries[].timestamp` — audio/video timestamp

#### Linking Users to AI Chats

Append `?chat={chat_opaque_id}` to the workspace storage URL:

`https://{domain}.fast.io/workspace/{folder_name}/storage/root?chat={chat_id}`

#### Share AI Chats

Shares support AI chat with identical capabilities. All workspace AI endpoints have share equivalents accessible via `ai` actions with `context_type: "share"`.

### AI Share / Export

Generate temporary markdown-formatted download URLs for files that can be pasted into external AI tools (ChatGPT, Claude, etc.). Use `ai` action `share-generate` (with `context_type: "workspace"` or `"share"`). URLs expire after 5 minutes. Limits: 25 files maximum, 50 MB per file, 100 MB total.

### Profile IDs

Organizations, workspaces, and shares are all identified by 19-digit numeric profile IDs. These appear throughout the tool parameters as `workspace_id`, `share_id`, `org_id`, `profile_id`, and `member_id`.

Most endpoints also accept custom names as identifiers:
| Profile Type | Numeric ID | Custom Name |
|-------------|-----------|-------------|
| Workspace | 19-digit ID | Folder name (e.g., `my-project`) |
| Share | 19-digit ID | URL name (e.g., `q4-financials`) |
| Organization | 19-digit ID | Domain name (e.g., `acme`) |
| User | 19-digit ID | Email address (e.g., `user@example.com`) |

### QuickShares

QuickShares are temporary public download links for individual files in workspaces (not available for shares). They can be accessed without authentication. Expires in seconds from creation (default 10,800 = 3 hours, max 86,400 = 24 hours). Max file size: 1 GB. Each quickshare has an opaque identifier used to retrieve metadata and download the file.

### File Preview

Files uploaded to Fast.io get automatic preview generation. When humans open a share or workspace, they see the content immediately -- no "download and open in another app" friction.

Supported preview formats:

- **Images** -- full-resolution with auto-rotation and zoom
- **Video** -- HLS adaptive streaming (50--60% faster load than raw video)
- **Audio** -- interactive waveform visualization
- **PDF** -- page navigation, zoom, text selection
- **Spreadsheets** -- grid navigation with multi-sheet support
- **Code and text** -- syntax highlighting, markdown rendering

Use `storage` action `preview-url` (with `context_type: "workspace"` or `"share"`) to generate preview URLs. Use `storage` action `preview-transform` (with `context_type: "workspace"` or `"share"`) for image resize, crop, and format conversion.

**Agent use case:** Your generated PDF report does not just appear as a download link. The human sees it rendered inline, can flip through pages, zoom in, and comment on specific sections -- all without leaving the browser.

### Comments and Annotations

Humans and agents can leave feedback directly on files, anchored to specific content using the `reference` parameter:

- **Image comments** -- anchored to spatial regions (normalized x/y/width/height coordinates)
- **Video comments** -- anchored to timestamps with spatial region selection
- **Audio comments** -- anchored to timestamps or time ranges
- **PDF comments** -- anchored to specific pages with optional text snippet selection
- **Threaded replies** -- single-level threading only; replies to replies are auto-flattened to the parent
- **Emoji reactions** -- one reaction per user per comment; adding a new reaction replaces the previous one
- **Mention tags** -- reference users and files inline using bracket syntax: `@[profile:id]`, `@[user:opaqueId:Display Name]`, `@[file:fileId:filename.ext]`. Get IDs from member lists, user details, or storage listings. The display name segment is optional for profile tags but recommended for user and file tags

Comments use JSON request bodies (`Content-Type: application/json`), unlike most other endpoints which use form-encoded data.

**Listing comments:** Use `comment` action `list` for per-file comments and `comment` action `list-all` for all comments across a workspace or share. Both support `sort`, `limit` (2-200), `offset`, `include_deleted`, `reference_type` filter, and `include_total`.

**Adding comments:** Use `comment` action `add` with `profile_type`, `profile_id`, `node_id`, and `text`. Optionally include `parent_comment_id` for replies and `reference` to anchor to a specific position. Supports mention tags in the body. Two character limits apply: total body including tags max 8,192 chars, display text (body with `@[...]` tags stripped) max 2,048 chars. Optionally include `linked_entity_type` and `linked_entity_id` to link the comment to a task or approval at creation time.

**Deleting comments:** `comment` action `delete` is recursive -- deleting a parent also removes all replies. `comment` action `bulk-delete` is NOT recursive -- replies to deleted comments are preserved.

**Comment Linking:** Comments can be linked to workflow entities (tasks or approvals). Each comment supports one link at a time (nullable). Use `comment` action `link` to associate an existing comment with a task or approval, `comment` action `unlink` to remove the association, and `comment` action `linked` to reverse-lookup all comments linked to a given entity. You can also link at creation time by passing `linked_entity_type` and `linked_entity_id` to the `add` action. Comment responses include `linked_entity_type` and `linked_entity_id` fields (null when unlinked).

**Linking users to comments:** The preview URL opens the comments sidebar automatically. Deep link query parameters let you target a specific comment or position:

| Parameter | Format | Purpose |
|-----------|--------|---------|
| `?comment={id}` | Comment opaque ID | Scrolls to and highlights a specific comment for 2 seconds |
| `?t={seconds}` | e.g. `?t=45.5` | Seeks to timestamp for audio/video comments |
| `?p={pageNum}` | e.g. `?p=3` | Navigates to page for PDF comments |

Workspace: `https://{org.domain}.fast.io/workspace/{folder_name}/preview/{file_opaque_id}?comment={comment_id}`

Share: `https://go.fast.io/shared/{custom_name}/{title-slug}/preview/{file_opaque_id}?comment={comment_id}`

Parameters can be combined -- e.g. `?comment={id}&t=45.5` to deep link to a video comment at a specific timestamp. In shares, the comments sidebar only opens if the share has comments enabled.

**Agent use case:** You generate a design mockup. The human comments "Change the header color" on a specific region of the image. You read the comment, see exactly what region they are referring to via the `reference.region` coordinates, and regenerate.

### URL Import

Agents can import files directly from URLs without downloading them locally first. Fast.io's server fetches the file, processes it, and adds it to your workspace or share.

- Supports any HTTP/HTTPS URL
- Supports OAuth-protected sources: **Google Drive, OneDrive, Dropbox**
- Files go through the same processing pipeline (preview generation, AI indexing if intelligence is enabled, virus scanning)

Use `upload` action `web-import` with the source URL, target profile, and parent node ID. Use `upload` action `web-status` to check progress and `upload` action `web-list` to list active import jobs.

**Agent use case:** A user says "Add this Google Doc to the project." You call `upload` action `web-import` with the URL. Fast.io downloads it server-side, generates previews, indexes it for AI, and it appears in the workspace. No local I/O.

### Metadata

Metadata enables structured data annotation on files within workspaces. The system uses a template-based approach: administrators create templates that define the fields (name, type, constraints), then assign a template to the workspace. Files can then have metadata values set against the template fields.

Key points:

- **One template per workspace** -- each workspace supports at most one assigned metadata template at a time.
- **Template categories** -- legal, financial, business, medical, technical, engineering, insurance, educational, multimedia, hr.
- **Field types** -- string, int, float, bool, json, url, datetime -- each with optional constraints (min, max, default, fixed_list, can_be_null).
- **Two metadata types** -- template metadata conforms to template field definitions; custom metadata is freeform key-value pairs not tied to any template.
- **System templates** -- pre-built templates that are automatically cloned when assigned to a workspace, so customizations do not affect the global definition.
- **AI extraction** -- the `extract` action uses AI to analyze file content and automatically populate metadata fields. Extracted values are flagged with `is_auto: true`. Consumes AI credits.
- **Version history** -- metadata changes are tracked with version snapshots, accessible via the `versions` action.
- **Requires billing feature** -- the organization must have the metadata billing feature enabled.
- **Template IDs** are alphanumeric strings prefixed with `mt_` (e.g. `mt_abc123def456`).

### Ownership Transfer

The primary way agents deliver value: build something, then give it to a human. Also the recommended action when the agent plan runs out of credits and API calls start returning 402 Payment Required -- transfer the org to a human who can upgrade to a paid plan.

**IMPORTANT: Account type restriction.** The transfer/claim workflow (`org` actions `transfer-token-create`, `transfer-token-list`, `transfer-token-delete`, `transfer-claim`) is only available when the agent created an **agent account** (via `auth` action `signup`) and that agent account owns the org. If the agent is signed in with a **human account** (via `auth` action `signin`), the transfer/claim API cannot be used. Human-owned orgs must be upgraded directly by the human through the Fast.io dashboard.

**The flow:**

1. Agent creates an agent account with `auth` action `signup` and an org with `org` action `create`, sets up workspaces with `org` action `create-workspace`, uploads files, configures shares
2. Agent generates a transfer token (valid 72 hours) with `org` action `transfer-token-create`
3. Agent sends the claim URL to the human: `https://go.fast.io/claim?token=<token>`
4. Human clicks the link and claims the org with their account

**When to transfer:**

- The org is ready for human use (workspaces configured, files uploaded, shares set up)
- The agent plan runs out of credits (402 Payment Required) -- transfer so the human can upgrade
- The human explicitly asks to take over the org

**Managing transfer tokens:**

- `org` action `transfer-token-list` -- check for existing pending tokens before creating new ones
- `org` action `transfer-token-delete` -- revoke a token if the transfer is no longer needed
- `org` action `transfer-claim` -- claim an org using a token (used by the receiving human's agent)

**What happens after transfer:**

- Human becomes the owner of the org and all workspaces
- Agent retains admin access (can still manage files and shares)
- Human gets a free plan (credit-based, no trial period)
- Human can upgrade to Pro or Business at any time

**Agent use case:** A user says "Set up a project workspace for my team." You create the org, build out the workspace structure, upload templates, configure shares for client deliverables, invite team members -- then transfer ownership. The human walks into a fully configured platform. You stay on as admin to keep managing things.

**402 Payment Required use case (agent account):** While working, the agent hits credit limits. Call `org` action `transfer-token-create`, send the claim URL to the human, and explain they can upgrade to continue. The agent keeps admin access and resumes work once the human upgrades.

**402 Payment Required use case (human account):** The agent cannot transfer the org. Instead, inform the user that their org has run out of credits and they need to upgrade their billing plan. Direct them to the Fast.io dashboard or use `org` action `billing-create` to update to a paid plan.

### Workflow (Tasks, Worklogs, Approvals, Todos)

Workspaces and shares support an optional workflow layer that adds structured task management, activity logging, approval gates, and simple checklists. Workflow features are controlled by a toggle -- they must be explicitly enabled before use.

#### Enabling Workflow

- **Workspaces:** `workspace` action `enable-workflow` with `workspace_id`
- **Shares:** `share` action `enable-workflow` with `share_id`

Check whether workflow is enabled via `workspace` action `details` or `share` action `details` -- look for `workflow: true` in the response.

Disabling workflow (`workspace` action `disable-workflow` or `share` action `disable-workflow`) makes all workflow data inaccessible but preserves it. Re-enabling restores access.

#### Task Lists and Tasks

Tasks are organized into lists. Each workspace or share can have multiple task lists, and each list contains individual tasks.

- **Task lists** have a name and optional description. Create with `task` action `create-list`, list with `task` action `list-lists`.
- **Tasks** have a title, description, status, priority, assignee, dependencies, and optional node link. Create with `task` action `create-task`, list with `task` action `list-tasks`.
- **Statuses:** `pending`, `in_progress`, `complete`, `blocked`
- **Priorities:** 0 = none, 1 = low, 2 = medium, 3 = high, 4 = critical
- **Assignees** are profile IDs (workspace or share members). Use `task` action `assign-task` to assign or unassign.
- **Bulk operations:** `task` action `bulk-status` changes status on up to 100 tasks at once.
- **Moving tasks:** `task` action `move-task` moves a task from one list to another within the same profile. Requires the source `list_id`, `task_id`, and `target_task_list_id`. Optionally set `sort_order` to control position in the target list (default: 0).
- **Reordering:** `task` action `reorder-tasks` sets the display order of tasks within a list. `task` action `reorder-lists` sets the display order of task lists within a profile. Pass arrays of IDs in the desired order; the server converts them to `{id, sort_order}` objects for the API.
- **Creator tracking:** Tasks and task lists include a `created_by` field (profile ID of the creator).
- **Markdown output:** Pass `format: "md"` to get human-readable markdown instead of JSON.

#### Worklogs

Worklogs are append-only chronological activity logs scoped to tasks, task lists, storage nodes, or profiles. Entries cannot be edited or deleted after creation.

- **Entries:** Regular log entries appended with `worklog` action `append`. Use for progress updates, decisions, reasoning, and status changes.
- **Interjections:** Priority corrections created with `worklog` action `interject`. Interjections are always urgent and require acknowledgement from other participants.
- **Acknowledgement:** `worklog` action `acknowledge` marks an interjection as seen. `worklog` action `unacknowledged` lists interjections that still need acknowledgement. Entries include an `acknowledgable` boolean -- when `true`, the entry is an unacknowledged interjection that can be acknowledged.
- **Response fields:** Entries include `acknowledged` (boolean), `acknowledgable` (boolean), `updated` (ISO 8601 timestamp), and `created` (ISO 8601 timestamp).
- **Markdown output:** Pass `format: "md"` for human-readable output.

#### Approvals

Formal approval requests scoped to tasks, storage nodes, or worklog entries. Use when a decision requires explicit sign-off.

- **Create:** `approval` action `create` with `profile_id`, `description` (1-5000 chars), `entity_type` ("task", "node", or "worklog_entry"), and optionally `approver_id` (a single profile ID, must be an entity member).
- **Resolve:** `approval` action `resolve` with `resolve_action: "approve"` or `"reject"` and an optional comment. Only designated approvers can resolve.
- **Statuses:** `pending`, `approved`, `rejected`
- **Markdown output:** Pass `format: "md"` for human-readable output.

#### Todos

Simple flat checklists scoped to workspaces and shares. No nesting -- just a list of items that can be checked off.

- **Create:** `todo` action `create` with a title.
- **Toggle:** `todo` action `toggle` flips the done state of a single todo. `todo` action `bulk-toggle` sets done state on up to 100 todos at once.
- **Update/Delete:** `todo` action `update` changes title. `todo` action `delete` soft-deletes a todo.
- **Creator tracking:** Todos include a `created_by` field (profile ID of the creator).
- **Markdown output:** Pass `format: "md"` for human-readable output.

#### Notes as Agent Knowledge Layer

Notes (`type: "note"`) are markdown files stored in workspace storage (see **Notes** above). When combined with workflow features, notes become a knowledge layer:

- **Automatic AI indexing:** When workspace intelligence is enabled, notes are ingested and indexed for RAG just like uploaded files.
- **Link tasks to notes:** Tasks can reference storage nodes, including notes. Create context notes for project background, requirements, or reference material, then create tasks that link to those notes for full context.
- **Worklogs for reasoning:** Use worklog entries to record decisions, progress, and reasoning over time. The chronological log builds a narrative that complements the structured task list.
- **AI can search all context:** With intelligence enabled, AI chat can search across notes, worklogs, task descriptions, and uploaded files -- giving comprehensive answers grounded in the project's full history.

**Recommended pattern:** Create notes for project context and requirements. Create task lists for work phases. Link tasks to relevant notes. Log progress with worklogs. Request approvals for decisions. The AI can then answer questions like "Why did we choose this approach?" by searching across all of these artifacts.

### Permission Parameter Values

Several tools use permission parameters with specific allowed values. Use these exact strings when calling the tools.

#### Organization Creation (`org` action `create`)

| Parameter | Allowed Values | Default |
|-----------|----------------|---------|
| `perm_member_manage` | `Owner only`, `Admin or above`, `Member or above` | `Member or above` |
| `industry` | `unspecified`, `technology`, `healthcare`, `financial`, `education`, `manufacturing`, `construction`, `professional`, `media`, `retail`, `real_estate`, `logistics`, `energy`, `automotive`, `agriculture`, `pharmaceutical`, `legal`, `government`, `non_profit`, `insurance`, `telecommunications`, `research`, `entertainment`, `architecture`, `consulting`, `marketing` | `unspecified` |
| `background_mode` | `stretched`, `fixed` | `stretched` |

#### Workspace Creation (`org` action `create-workspace`) and Update (`workspace` action `update`)

| Parameter | Allowed Values | Default |
|-----------|----------------|---------|
| `perm_join` | `Only Org Owners`, `Admin or above`, `Member or above` | `Member or above` |
| `perm_member_manage` | `Admin or above`, `Member or above` | `Member or above` |

#### Share Creation (`share` action `create`)

| Parameter | Allowed Values | Default |
|-----------|----------------|---------|
| `type` | `send`, `receive`, `exchange` | `exchange` |
| `storage_mode` | `independent`, `workspace_folder` | `independent` |
| `access_options` | `Only members of the Share or Workspace`, `Members of the Share, Workspace or Org`, `Anyone with a registered account`, `Anyone with the link` | `Only members of the Share or Workspace` |
| `invite` | `owners`, `guests` | `owners` |
| `notify` | `never`, `notify_on_file_received`, `notify_on_file_sent_or_received` | `never` |
| `display_type` | `list`, `grid` | `grid` |
| `intelligence` | `true`, `false` | `false` |
| `comments_enabled` | `true`, `false` | `true` |
| `download_enabled` | `true`, `false` | `true` |
| `guest_chat_enabled` | `true`, `false` | `false` |
| `workspace_style` | `true`, `false` | `true` |
| `background_image` | `0`-`128` | `0` |

**Share constraints:**

- Receive and Exchange shares cannot use `Anyone with the link` access -- this option is only available for Send shares.
- Password protection (`password` parameter) is only allowed when `access_options` is `Anyone with the link`.
- Expiration (`expires` parameter in MySQL format `YYYY-MM-DD HH:MM:SS`) is not allowed on `workspace_folder` shares.
- Field length and format constraints for `custom_name`, `title`, and `description` are documented in the **Profile Field Constraints** table below.
- Color parameters (`accent_color`, `background_color1`, `background_color2`) accept JSON strings.
- `create_folder` creates a new workspace folder for the share when used with `storage_mode='workspace_folder'`.

### Profile Field Constraints

All profile fields are validated server-side. Requests that violate these constraints are rejected with a 400 error.

| Entity | Field | API Key | Min | Max | Pattern | Required | Nullable |
|--------|-------|---------|-----|-----|---------|----------|----------|
| Org | domain | `domain` | 2 | 80 | `^[a-z0-9]([-a-z0-9]{0,61}[a-z0-9])?$` | Yes (create) | No |
| Org | name | `name` | 3 | 100 | No control chars | Yes | No |
| Org | description | `description` | 10 | 1000 | No control chars | No | Yes |
| Workspace | folder_name | `folder_name` | 4 | 80 | `^[\p{L}\p{N}-]+$` (letters, digits, hyphens) | Yes (create) | No |
| Workspace | name | `name` | 2 | 100 | No control chars | Yes | No |
| Workspace | description | `description` | 10 | 1000 | No control chars | No | Yes |
| Share | custom_name | `custom_name` | 4 | 80 | `^[\p{L}\p{N}]+$` (letters, digits only) | Yes (create) | No |
| Share | custom_url | `custom_url` | 10 | 100 | — | Yes | Yes |
| Share | title | `title` | 2 | 80 | No control chars | Yes | Yes |
| Share | description | `description` | 10 | 500 | No control chars | No | Yes |

- **"No control chars"** = rejects Unicode control characters (`\p{C}`)
- **Org domain**: lowercase ASCII alphanumeric + hyphens; cannot start/end with hyphen
- **Workspace folder_name**: Unicode letters, digits, and hyphens. **Globally unique** -- not scoped to an org. Recommend `{org_id}-{name}` convention to avoid collisions (auto-applied by `create-workspace` when name is taken)
- **Share custom_name**: Unicode letters and digits only (no hyphens or special chars)
- **Share description** max is 500 (org/workspace is 1000)

---

## 4. Agent Plan -- Free Tier

The agent plan is a free tier designed for AI agents. No credit card, no trial period, no expiration. Enough resources to build and demonstrate value, with room to grow when the org transfers to a human on a paid plan.

### Resource Limits

| Resource | Included |
|----------|----------|
| **Price** | $0 -- no credit card, no trial period, no expiration |
| **Storage** | 50 GB |
| **Max file size** | 1 GB |
| **Monthly credits** | 5,000 (resets every 30 days) |
| **Workspaces** | 5 |
| **Shares** | 50 |
| **Members per workspace** | 5 |
| **Share invitations** | 10 per share |
| **Account auto-deletion** | Never |

### Credit Costs

All platform activity consumes credits from the monthly 5,000 allowance:

| Resource | Cost |
|----------|------|
| Storage | 100 credits/GB |
| Bandwidth | 212 credits/GB |
| AI chat tokens | 1 credit per 100 tokens |
| Document pages ingested | 10 credits/page |
| Video ingested | 5 credits/second |
| Audio ingested | 0.5 credits/second |
| Images ingested | 5 credits/image |
| File conversions | 25 credits/conversion |

When credits run out, the org enters a reduced-capability state and API calls return 402 Payment Required. The org is never deleted. Use `org` action `limits` to check current credit usage and remaining balance.

**When you hit 402 or run low on credits:**

- **Agent account (created via `auth` action `signup`):** Transfer the org to the human. Call `org` action `transfer-token-create` to generate a transfer token, then send the human the claim URL: `https://go.fast.io/claim?token=<token>`. Once they claim the org they can upgrade to a paid plan with unlimited credits. You retain admin access and can resume work immediately after the upgrade. This is the expected workflow -- agents build on the free plan, then hand off to humans who pay when they are ready.
- **Human account (signed in via `auth` action `signin`):** You cannot use the transfer/claim API. Tell the user they need to upgrade the org's billing plan directly. They can do this from the Fast.io dashboard or by calling `org` action `billing-create` to update their subscription to a paid plan.

### After Transfer -- Human Plan Options

Once an agent transfers an org to a human, the human gets a free plan (credit-based, no trial period) and can upgrade:

| Feature | Agent (Free) | Free (Human) | Pro | Business |
|---------|-------------|--------------|-----|----------|
| Monthly credits | 5,000 | 5,000 | Unlimited | Unlimited |
| Storage | 50 GB | 50 GB | 1 TB | 5 TB |
| Max file size | 1 GB | 1 GB | 25 GB | 50 GB |
| Workspaces | 5 | 5 | 10 | 1,000 |
| Shares | 50 | 50 | 1,000 | 50,000 |

The transfer flow is the primary way agents deliver value: set everything up on the free agent plan, then hand it off. The human upgrades when they are ready, and the agent retains admin access to keep managing things.

---

## 5. Tool Categories

The 19 tools use action-based routing. Each tool covers a specific area of the Fast.io platform and exposes multiple actions.

### auth

Authentication, sign-in/sign-up, two-factor authentication, API key management, and OAuth session management. This is always the starting point for any agent interaction.

**Actions:** signin, signout, signup, check, session, status, set-api-key, email-check, email-verify, password-reset-request, password-reset, 2fa-verify, 2fa-status, 2fa-enable, 2fa-disable, 2fa-send, 2fa-verify-setup, pkce-login, pkce-complete, api-key-create, api-key-update, api-key-list, api-key-get, api-key-delete, oauth-list, oauth-details, oauth-revoke, oauth-revoke-all

### user

Retrieve and update the current user profile, search for other users, manage invitations, upload and delete user assets (profile photos), check account eligibility, and list shares the user belongs to.

**Actions:** me, update, search, close, details-by-id, profiles, allowed, org-limits, list-shares, invitation-list, invitation-details, accept-all-invitations, asset-upload, asset-delete, asset-types, asset-list

### org

Organization CRUD, member management, billing and subscription operations, workspace creation, invitation workflows, asset management (upload, delete), organization discovery, and ownership transfer.

**Actions:** list, details, create, update, close, public-details, limits, list-workspaces, list-shares, create-workspace, billing-plans, billing-create, billing-cancel, billing-details, billing-activate, billing-reset, billing-members, billing-meters, members, invite-member, remove-member, update-member-role, member-details, leave, transfer-ownership, join, invitations-list, invitation-update, invitation-delete, transfer-token-create, transfer-token-list, transfer-token-delete, transfer-claim, discover-all, discover-available, discover-check-domain, discover-external, asset-upload, asset-delete, asset-types, asset-list

### workspace

Workspace-level settings, lifecycle operations (update, delete, archive, unarchive), listing and importing shares, managing workspace assets, workspace discovery, notes (create, read, update), quickshare management, metadata operations (template CRUD, assignment, file metadata get/set/delete, AI extraction), and workflow toggle (enable/disable tasks, worklogs, approvals, and todos).

**Actions:** list, details, update, delete, archive, unarchive, members, list-shares, import-share, available, check-name, create-note, read-note, update-note, quickshare-get, quickshare-delete, quickshares-list, metadata-template-create, metadata-template-delete, metadata-template-list, metadata-template-details, metadata-template-update, metadata-template-clone, metadata-template-assign, metadata-template-unassign, metadata-template-resolve, metadata-template-assignments, metadata-get, metadata-set, metadata-delete, metadata-extract, metadata-list-files, metadata-list-templates-in-use, metadata-versions, enable-workflow, disable-workflow

### share

Share CRUD, public details, archiving, password authentication, asset management, share name availability checks, and workflow toggle (enable/disable tasks, worklogs, approvals, and todos).

**Actions:** list, details, create, update, delete, public-details, archive, unarchive, password-auth, members, available, check-name, quickshare-create, enable-workflow, disable-workflow

### storage

File and folder operations within workspaces and shares. List, list recently modified files across all folders, create folders, move, copy, delete, rename, purge, restore, search, add files from uploads, add share links, transfer nodes, manage trash, version operations, file locking, and preview/transform URL generation. Requires `context_type` parameter (`workspace` or `share`).

**Actions:** list, recent, details, search, trash-list, create-folder, copy, move, delete, rename, purge, restore, add-file, add-link, transfer, version-list, version-restore, lock-acquire, lock-status, lock-release, preview-url, preview-transform

### upload

File upload operations. Single-step text file upload, chunked upload lifecycle (create session, stage binary blobs, upload chunks as plain text / base64 / blob reference, finalize, check status, cancel), web imports from external URLs, upload limits and file extension restrictions, and session management.

**Actions:** create-session, chunk, finalize, status, cancel, list-sessions, cancel-all, chunk-status, chunk-delete, stage-blob, text-file, web-import, web-list, web-cancel, web-status, limits, extensions

### download

Generate download URLs and ZIP archive URLs for workspace files, share files, and quickshare links. MCP tools cannot stream binary data -- these actions return URLs that can be opened in a browser or passed to download utilities. Requires `context_type` parameter (`workspace` or `share`) for file-url and zip-url actions. Responses include a `resource_uri` field (e.g. `download://workspace/{id}/{node_id}`) that MCP clients can use to read file content directly via MCP resources. Direct download URLs include `?error=html` so errors render as human-readable HTML in browsers.

**Actions:** file-url, zip-url, quickshare-details

### ai

AI-powered chat with RAG, semantic search, and document analysis in workspaces and shares. Create chats, send messages, read AI responses (with polling), list and manage chats, search indexed documents and code by meaning with relevance scores, publish private chats, generate AI share markdown, track AI token usage, and auto-title generation. Requires `context_type` parameter (`workspace` or `share`).

**Actions:** chat-create, chat-list, chat-details, chat-update, chat-delete, chat-publish, message-send, message-list, message-details, message-read, search, share-generate, transactions, autotitle

### comment

Comments are scoped to `{entity_type}/{parent_id}/{node_id}` where entity_type is `workspace` or `share`, parent_id is the 19-digit profile ID, and node_id is the storage node opaque ID. List comments on files (per-node and profile-wide with sort/limit/offset/filter params), add comments with optional reference anchoring (image regions, video/audio timestamps, PDF pages with text selection), single-level threaded replies, recursive single delete, non-recursive bulk delete, get comment details, emoji reactions (one per user per comment), and workflow linking (link/unlink comments to tasks or approvals, reverse lookup). Comments use JSON request bodies.

**Actions:** list, list-all, add, delete, bulk-delete, details, reaction-add, reaction-remove, link, unlink, linked

### event

Search the audit/event log with rich filtering by category, subcategory, and event name (see **Event Filtering Reference** in section 7 for the full taxonomy). Get AI-powered summaries of activity, retrieve full details for individual events, list recent activity, and long-poll for activity changes.

**Actions:** search, summarize, details, activity-list, activity-poll

### member

Member management for organizations, workspaces, and shares. Add, remove, update roles, transfer ownership, leave, join, and join via invitation. Requires `entity_type` parameter (`workspace` or `share`).

**Actions:** add, remove, details, update, transfer-ownership, leave, join, join-invitation

### invitation

Invitation management for organizations, workspaces, and shares. List invitations, list by state, update, and delete. Requires `entity_type` parameter (`workspace` or `share`).

**Actions:** list, list-by-state, update, delete

### asset

Asset management (upload, delete, list, read) for organizations, workspaces, shares, and users. Requires `entity_type` parameter (`org`, `workspace`, `share`, or `user`).

**Actions:** upload, delete, types, list, read

### task

Task list and task management for workspaces and shares. Create and manage task lists, then create tasks within them with statuses, priorities, assignees, and dependencies. Supports bulk status changes, reordering, and markdown output. Tasks and lists include `created_by` (creator profile ID). Requires workflow to be enabled on the target entity.

**Actions:** list-lists, create-list, list-details, update-list, delete-list, list-tasks, create-task, task-details, update-task, delete-task, change-status, assign-task, bulk-status, move-task, reorder-tasks, reorder-lists

### worklog

Activity log for tracking agent work. After uploads, task changes, share creation, or any significant action, log what you did and why — builds a searchable audit trail for humans and AI. Also create urgent interjections that require acknowledgement. Entries are append-only and permanent. Requires workflow to be enabled on the target entity.

**Actions:** append, list, interject, details, acknowledge, unacknowledged

### approval

Formal approval requests scoped to tasks, storage nodes, or worklog entries. Create approval requests with designated approvers, then resolve them with approve or reject decisions. Requires workflow to be enabled on the target entity.

**Actions:** list, create, details, resolve

### todo

Simple flat checklists scoped to workspaces and shares. Create, update, delete, toggle todos individually or in bulk. Todos include `created_by` (creator profile ID). No nesting. Requires workflow to be enabled on the target entity.

**Actions:** list, create, details, update, delete, toggle, bulk-toggle

### apps

Interactive MCP App widget discovery and launching. List available widgets, get details for a specific widget, launch a widget with workspace or share context, and find widgets associated with a specific tool domain.

**Actions:** list, details, launch, get-tool-apps

---

## 6. Common Workflows

### 1. Create an Account and Sign In

See **Choosing the Right Approach** in section 2 for which option fits your scenario.

**Option 1 -- Autonomous agent (new account):**

1. Optionally call `auth` action `email-check` with the desired `email` to verify availability.
2. `auth` action `signup` with `first_name`, `last_name`, `email`, and `password` -- registers as an agent account (agent=true is sent automatically) and signs in immediately.
3. `auth` action `email-verify` with `email` -- sends a verification code. Then `auth` action `email-verify` with `email` and `email_token` -- validates the code. Required before using most endpoints.
4. `org` action `create` to create a new org on the agent plan, or `org` action `list` to check existing orgs.

**Option 2 -- Assisting a human (API key):**

1. The human creates an API key at `https://go.fast.io/settings/api-keys` and provides it to the agent.
2. Call `auth` action `set-api-key` with the API key. The key is validated against the API and stored in the session -- all subsequent tool calls are authenticated automatically. No account creation needed.
3. `org` action `list` and `org` action `discover-external` to discover all available organizations (see **Org Discovery**).

**Option 3 -- Agent invited to a human's org:**

1. Create an agent account with `auth` action `signup` (same as Option 1).
2. Have the human invite you via `org` action `invite-member` or `member` action `add` (with `entity_type: "workspace"`).
3. Accept invitations with `user` action `accept-all-invitations`.
4. `org` action `list` and `org` action `discover-external` to discover all available orgs (see **Org Discovery**). If the human only invited you to a workspace (not the org), it will only appear via `discover-external`.

**Returning users:**

1. `auth` action `signin` with `email` and `password`.
2. If `two_factor_required: true`, call `auth` action `2fa-verify` with the 2FA `code`.
3. `org` action `list` and `org` action `discover-external` to discover all available organizations (see **Org Discovery**).

### 2. Browse and Download a File

1. `org` action `list` and `org` action `discover-external` -- discover all available organizations (see **Org Discovery**). Note the `org_id` values.
2. `org` action `list-workspaces` with `org_id` -- get workspaces in the organization. Note the `workspace_id` values.
3. `storage` action `list` with `context_type: "workspace"`, `context_id` (workspace ID), and `node_id: "root"` -- browse the root folder. Note the `node_id` values for files and subfolders.
4. `storage` action `details` with `context_type: "workspace"`, `context_id`, and `node_id` -- get full details for a specific file (name, size, type, versions).
5. `download` action `file-url` with `context_type: "workspace"`, `context_id`, and `node_id` -- get a temporary download URL with an embedded token. The response also includes a `resource_uri` (e.g. `download://workspace/{id}/{node_id}`) that MCP clients can use to read file content directly. Return the download URL to the user, or use the resource URI to read the file through MCP.

### 3. Upload a File to a Workspace

**Text files (recommended):** Use `upload` action `text-file` with `profile_type: "workspace"`, `profile_id`, `parent_node_id`, `filename`, and `content` (plain text). This single action creates the session, uploads, finalizes, and polls until stored — returns `new_file_id` on success. Use this for code, markdown, CSV, JSON, config files, and any other text content.

**Binary or large files (chunked flow):**

1. `upload` action `create-session` with `profile_type: "workspace"`, `profile_id` (the workspace ID), `parent_node_id` (target folder or `"root"`), `filename`, and `filesize` in bytes. Returns an `upload_id`, `recommended_mcp_chunk_bytes` (default 24576), and `total_chunks` — use these to split the file.
2. `upload` action `chunk` with `upload_id`, `chunk_number` (1-indexed), and chunk data. **Split files into pieces of `recommended_mcp_chunk_bytes`** (24 KB binary / ~32 KB base64) — even small files. Three options for passing data (provide exactly one):
   - **`content`** — for text (strings, code, JSON, etc.). Do NOT use `data` for text.
   - **`data`** — base64-encoded binary (**≤32 KB per call**). The simplest approach for binary uploads through MCP tool calls. Split the file and send each piece as a separate chunk.
   - **`blob_ref`** — blob ID from `upload` action `stage-blob` or `POST /blob`. Useful when pre-staging data or when using the HTTP blob endpoint from non-MCP clients. Blobs expire after 5 minutes and are consumed (deleted) on use.
   Repeat for each chunk. Wait for each chunk to return success before sending the next.
3. `upload` action `finalize` with `upload_id` -- triggers file assembly and polls until stored. Returns the final session state with `status: "stored"` or `"complete"` on success (including `new_file_id`), or throws on assembly failure. The file is automatically added to the target workspace and folder specified in step 1 -- no separate add-file call is needed.

**Note:** `storage` action `add-file` is only needed if you want to link the upload to a *different* location than the one specified during session creation.

**Same-name uploads:** If a file with the same name already exists in the target folder, the upload **replaces** (overwrites) it. The previous content is preserved as a version. To keep both files, rename before uploading.

### 4. Import a File from URL

Use this when you have a file URL (HTTP/HTTPS, Google Drive, OneDrive, Box, Dropbox) and want to add it to a workspace without downloading locally.

1. `upload` action `web-import` with `url` (the source URL), `profile_type: "workspace"`, `profile_id` (the workspace ID), and `parent_node_id` (target folder or `"root"`). Returns an `upload_id`.
2. `upload` action `web-status` with `upload_id` -- check import progress. The server downloads the file, scans it, generates previews, and indexes it for AI (if intelligence is enabled).
3. The file appears in the workspace storage tree once the job completes.

### 5. Deliver Files to a Client

Create a branded, professional data room for outbound file delivery. This replaces raw download links, email attachments, and S3 presigned URLs.

1. Upload files to the workspace (see workflow 3 or 4).
2. `share` action `create` with `workspace_id`, `name`, and `type: "send"` -- creates a Send share. Returns a `share_id`.
3. `share` action `update` with `share_id` to configure:
   - `password` -- require a password for access
   - `expiry_date` -- auto-expire the share after a set period
   - `access_level` -- Members Only, Org Members, Registered Users, or Public
   - `allow_downloads` -- enable or disable file downloads
   - Branding options: `background_color`, `accent_color`, `gradient_color`
   - `post_download_message` and `post_download_url` -- show a message after download
4. `member` action `add` with `entity_type: "share"`, `entity_id` (share ID), and `email_or_user_id` -- adds the recipient. An invitation is sent if they do not have a Fast.io account.
5. `asset` action `upload` with `entity_type: "share"` and `entity_id` (share ID) to add a logo or background image for branding.
6. The recipient sees a branded page with instant file preview, not a raw download link.

### 6. Collect Documents from a User

Create a Receive share so humans can upload files directly to you -- no email attachments, no cloud drive links.

1. `share` action `create` with `workspace_id`, `name` (e.g., "Upload your tax documents here"), and `type: "receive"`. Returns a `share_id`.
2. `share` action `update` with `share_id` to set access level, expiration, and branding as needed.
3. `member` action `add` with `entity_type: "share"`, `entity_id` (share ID), and `email_or_user_id` to invite the uploader.
4. The human uploads files through a clean, branded interface.
5. Files appear in your workspace. If intelligence is enabled, they are auto-indexed by AI.
6. Use `ai` action `chat-create` with `context_type: "share"` scoped to the receive share's folder to ask questions like "Are all required forms present?"

### 7. Build a Knowledge Base

Create an intelligent workspace that auto-indexes all content for RAG queries.

1. `org` action `create-workspace` with `org_id` and `name`. Intelligence is enabled by default.
2. Upload reference documents (see workflow 3 or 4). AI auto-indexes and summarizes everything on upload.
3. `ai` action `chat-create` with `context_type: "workspace"`, `context_id` (workspace ID), `query_text`, `type: "chat_with_files"`, and `folders_scope` (comma-separated `nodeId:depth` pairs) to query across folders or the entire workspace.
4. `ai` action `message-read` with `context_type: "workspace"`, `context_id`, `chat_id`, and `message_id` -- polls until the AI response is complete. Returns `response_text` and `citations` pointing to specific files, pages, and snippets.
5. `storage` action `search` with `context_type: "workspace"`, `context_id`, and a query string for semantic search -- find files by meaning, not just filename.
6. Answers include citations to specific pages and files. Pass these back to the user with source references.

### 8. Ask AI About Files

Two modes depending on whether intelligence is enabled on the workspace.

**With intelligence (persistent index):**

1. `ai` action `chat-create` with `context_type: "workspace"`, `context_id` (workspace ID), `query_text`, `type: "chat_with_files"`, and either `files_scope` (comma-separated `nodeId:versionId` pairs) or `folders_scope` (comma-separated `nodeId:depth` pairs, depth range 1-10). **Important:** `files_scope` and `files_attach` are mutually exclusive — sending both will error. Returns `chat_id` and `message_id`.
2. `ai` action `message-read` with `context_type: "workspace"`, `context_id`, `chat_id`, and `message_id` -- polls the API up to 15 times (2-second intervals, approximately 30 seconds) until the AI response is complete. Returns `response_text` and `citations`. **Tip:** If the built-in polling window expires, use `event` action `activity-poll` with the workspace ID instead of calling `message-read` in a loop — see the Activity Polling section above.
3. `ai` action `message-send` with `context_type: "workspace"`, `context_id`, `chat_id`, and `query_text` for follow-up questions. Returns a new `message_id`.
4. `ai` action `message-read` again with the new `message_id` to get the follow-up response.

**Without intelligence (file attachments):**

1. `ai` action `chat-create` with `context_type: "workspace"`, `context_id`, `query_text`, `type: "chat_with_files"`, and `files_attach` pointing to specific files (comma-separated `nodeId:versionId`, max 20 files / 200 MB). Files must have `ai.attach: true` (check via `storage` action `details`). The AI reads attached files directly without persistent indexing.
2. `ai` action `message-read` to get the response. No ingestion credit cost -- only chat token credits are consumed.

### 9. Set Up a Project for a Human

The full agent-to-human handoff workflow. This is the primary way agents deliver value on Fast.io.

1. `org` action `create` -- creates a new org on the agent billing plan. The agent becomes owner. An agent-plan subscription (free, 50 GB, 5,000 credits/month) is created automatically.
2. `org` action `create-workspace` with `org_id` and `name` -- create workspaces for each project area.
3. `storage` action `create-folder` with `context_type: "workspace"` to build out folder structure (templates, deliverables, reference docs, etc.).
4. Upload files to each workspace (see workflow 3 or 4).
5. `share` action `create` with `type: "send"` for client deliverables, `type: "receive"` for intake/collection.
6. `share` action `update` to configure branding, passwords, expiration, and access levels on each share.
7. `org` action `invite-member` or `member` action `add` with `entity_type: "workspace"` to invite team members.
8. `org` action `transfer-token-create` with `org_id` -- generates a transfer token valid for 72 hours. Send the claim URL (`https://go.fast.io/claim?token=<token>`) to the human.
9. Human clicks the link and claims the org. They become owner, agent retains admin access. Human gets a free plan.

### 10. Manage Organization Billing

1. `org` action `billing-plans` -- list all available billing plans with pricing and features.
2. `org` action `billing-create` with `org_id` and optionally `billing_plan` -- create or update a subscription. For new subscriptions, this creates a Stripe Setup Intent.
3. `org` action `billing-details` with `org_id` -- check the current subscription status, Stripe customer info, and payment details.
4. `org` action `limits` with `org_id` -- check credit usage against plan limits, including storage, transfer, AI tokens, and billing period info.

### 11. Manage Tasks in a Workspace

Track work with structured task lists and tasks.

1. `workspace` action `enable-workflow` with `workspace_id` -- enable workflow features (required before using task, worklog, approval, or todo tools).
2. `task` action `create-list` with `profile_type: "workspace"`, `profile_id` (workspace ID), and `name` -- create a task list. Returns `list_id`.
3. `task` action `create-task` with `list_id`, `title`, and optionally `description`, `priority` (0-4), `assignee_id`, `dependencies`, `node_id`, and `status` -- add tasks to the list.
4. `task` action `list-tasks` with `list_id` -- view all tasks, optionally filtered by `status` or `assignee`.
5. `task` action `change-status` with `list_id`, `task_id`, and `status` -- update task progress (`pending` → `in_progress` → `complete`).
6. `task` action `assign-task` with `list_id`, `task_id`, and `assignee_id` -- assign work to team members.
7. `task` action `bulk-status` with `list_id`, `task_ids`, and `status` -- batch-update up to 100 tasks at once.

### 12. Full Agent Workflow (Tasks + Worklogs + Approvals)

The complete agentic workflow pattern: plan work, execute with logging, and gate decisions with approvals.

1. `workspace` action `enable-workflow` with `workspace_id` -- enable workflow features on the workspace.
2. `workspace` action `create-note` -- create context notes with project background, requirements, and reference material.
3. `task` action `create-list` -- create task lists for each work phase (e.g., "Research", "Implementation", "Review").
4. `task` action `create-task` -- add tasks linked to context. Include descriptive titles and reference note node_ids in descriptions.
5. `task` action `change-status` with `status: "in_progress"` -- mark a task as started.
6. `worklog` action `append` with `entity_type` ("task", "task_list", "node", or "profile"), `entity_id` (the corresponding entity's opaque ID, or profile 19-digit ID for entity_type "profile"), and `content` -- log progress, decisions, and reasoning as you work. Build a chronological narrative.
7. If a priority correction is needed: `worklog` action `interject` -- creates an urgent entry that requires acknowledgement from other participants.
8. `worklog` action `unacknowledged` -- check for unacknowledged interjections before proceeding.
9. `worklog` action `acknowledge` -- mark interjections as seen.
10. When a decision needs sign-off: `approval` action `create` with `profile_id`, `description`, `entity_type` ("task", "node", or "worklog_entry"), and optionally `approver_id` -- request formal approval.
11. `approval` action `resolve` with `resolve_action: "approve"` or `"reject"` and optional `comment` -- approvers resolve the request.
12. `task` action `change-status` with `status: "complete"` -- mark completed tasks.
13. `todo` action `create` -- track simple checklist items alongside the main task flow.
14. With intelligence enabled, `ai` action `chat-create` -- the AI can search across notes, task descriptions, and worklogs to answer questions about the project.

---

## 7. Key Patterns and Gotchas

### ID Format

Profile IDs (org, workspace, share, user) are 19-digit numeric strings. Most endpoints also accept custom names as identifiers -- workspace folder names, share URL names, org domain names, or user email addresses. Both formats are interchangeable in URL path parameters.

All other IDs (node IDs, upload IDs, chat IDs, comment IDs, invitation IDs, etc.) are 30-character alphanumeric opaque IDs (displayed with hyphens). Do not apply numeric validation to these.

### Pagination

Two pagination styles are used depending on the endpoint:

**Cursor-based (storage list endpoints):** `sort_by`, `sort_dir`, `page_size`, and `cursor`. The response includes a `next_cursor` value when more results are available. Pass this cursor in the next call to retrieve the next page. Page sizes are typically 100, 250, or 500. Used by: `storage` action `list` (with `context_type: "workspace"` or `"share"`).

**Limit/offset (all other list endpoints):** `limit` (1-500, default 100) and `offset` (default 0). Used by: `org` actions `list`, `members`, `list-workspaces`, `list-shares`, `billing-members`, `discover-all`, `discover-external`; `share` actions `list`, `members`; `workspace` actions `list`, `members`, `list-shares`; `user` action `list-shares`; `storage` action `search`.

### Binary Downloads

MCP tools return download URLs -- they never stream binary content directly. `download` action `file-url` (with `context_type: "workspace"` or `"share"`) and `download` action `quickshare-details` call the `/requestread/` endpoint to obtain a temporary token, then construct a full download URL. The agent should return these URLs to the user or pass them to a download utility.

`download` actions `zip-url` (workspace and share) return the URL along with the required `Authorization` header value.

### Binary Uploads

Three approaches for uploading binary data as chunks, each suited to different situations.

> **Chunk size limit for MCP agents.** MCP tool parameters pass through the AI model's output, which limits how much data you can include in a single tool call. **Keep each chunk's base64 `data` under 32 KB** (~24 KB of binary). For example, a 145 KB PDF needs at least 6 chunks, and even a 17 KB file should be split into 1-2 chunks rather than assumed to fit in one call. The `create-session` response includes a `recommended_mcp_chunk_bytes` hint (default 24576) — use it to calculate the number of chunks: `ceil(filesize / recommended_mcp_chunk_bytes)`. Always split files into multiple chunks when using `data` or `stage-blob` through MCP tool calls.

**1. `data` parameter (base64) — simplest for MCP agents**

Pass base64-encoded binary directly in the `data` parameter of `upload` action `chunk`. No extra steps required. Works with any MCP client. Adds ~33% size overhead from base64 encoding. **Split files into chunks of ≤24 KB binary (≤32 KB base64)** to stay within MCP client parameter limits.

**2. `stage-blob` action — MCP tool-based blob staging**

Use `upload` action `stage-blob` with `data` (base64) to pre-stage binary data as a blob. Returns a `blob_id` that you pass as `blob_ref` in the chunk call. Useful when you want to decouple staging from uploading, or when preparing multiple chunks in advance. The same **32 KB base64 limit per call** applies — stage one chunk-sized piece at a time.

**Flow:**
1. `upload` action `stage-blob` with `data` (base64-encoded binary, ≤32 KB). Returns `{ "blob_id": "<uuid>", "size": <bytes> }`.
2. `upload` action `chunk` with `blob_ref: "<blob_id>"`. The server retrieves the staged bytes and uploads them.

**3. `POST /blob` endpoint — HTTP blob staging for non-MCP clients**

A sidecar HTTP endpoint that accepts raw binary data outside the JSON-RPC pipe. This avoids base64 encoding entirely — useful for clients that can make direct HTTP requests alongside MCP tool calls. No chunk size splitting needed with this approach.

**Flow:**
1. `POST /blob` with headers `Mcp-Session-Id: <session_id>` and `Content-Type: application/octet-stream`. Send raw binary bytes as the request body. Returns `{ "blob_id": "<uuid>", "size": <bytes> }` (HTTP 201).
2. `upload` action `chunk` with `blob_ref: "<blob_id>"`.

**Blob constraints (apply to both staging methods):**
- Blobs expire after **5 minutes**. Stage and consume them promptly.
- Each blob is consumed (deleted) on first use — it cannot be reused.
- Maximum blob size: **100 MB**.
- SSE transport clients must add `?transport=sse` to the `/blob` URL.

### Event Filtering Reference

The `event` tool's `search` and `summarize` actions accept `category`, `subcategory`, and `event` parameters to narrow results. Use these to target specific activity instead of scanning all events.

#### Event Categories

| Category | What It Covers |
|---|---|
| `user` | Account creation, updates, deletion, avatar changes |
| `org` | Organization lifecycle, settings, transfers |
| `workspace` | Workspace creation, updates, archival, file operations |
| `share` | Share lifecycle, settings, file operations |
| `node` | File and folder operations (cross-profile) |
| `ai` | AI chat, summaries, RAG indexing |
| `invitation` | Member invitations sent, accepted, declined |
| `billing` | Subscriptions, trials, credit usage |
| `domain` | Custom domain configuration |
| `apps` | Application integrations |
| `metadata` | Metadata extraction, templates, key-value updates |

#### Event Subcategories

| Subcategory | What It Covers |
|---|---|
| `storage` | File/folder add, move, copy, delete, restore, download |
| `comments` | Comment created, updated, deleted, mentioned, replied, reaction |
| `members` | Member added/removed from org, workspace, or share |
| `lifecycle` | Profile created, updated, deleted, archived |
| `settings` | Configuration and preference changes |
| `security` | Security-related events (2FA, password) |
| `authentication` | Login, SSO, session events |
| `ai` | AI processing, chat, indexing |
| `invitations` | Invitation management |
| `billing` | Subscription and payment events |
| `assets` | Avatar/asset updates |
| `upload` | Upload session management |
| `transfer` | Cross-profile file transfers |
| `quickshare` | Quick share operations |
| `metadata` | Metadata operations |

#### Common Event Names

**File operations (workspace):** `workspace_storage_file_added`, `workspace_storage_file_deleted`, `workspace_storage_file_moved`, `workspace_storage_file_copied`, `workspace_storage_file_updated`, `workspace_storage_file_restored`, `workspace_storage_folder_created`, `workspace_storage_folder_deleted`, `workspace_storage_folder_moved`, `workspace_storage_download_token_created`, `workspace_storage_zip_downloaded`, `workspace_storage_file_version_restored`, `workspace_storage_link_added`

**File operations (share):** `share_storage_file_added`, `share_storage_file_deleted`, `share_storage_file_moved`, `share_storage_file_copied`, `share_storage_file_updated`, `share_storage_file_restored`, `share_storage_folder_created`, `share_storage_folder_deleted`, `share_storage_folder_moved`, `share_storage_download_token_created`, `share_storage_zip_downloaded`

**Comments:** `comment_created`, `comment_updated`, `comment_deleted`, `comment_mentioned`, `comment_replied`, `comment_reaction`

**Membership:** `added_member_to_org`, `added_member_to_workspace`, `added_member_to_share`, `removed_member_from_org`, `removed_member_from_workspace`, `removed_member_from_share`, `membership_updated`

**Workspace lifecycle:** `workspace_created`, `workspace_updated`, `workspace_deleted`, `workspace_archived`, `workspace_unarchived`

**Share lifecycle:** `share_created`, `share_updated`, `share_deleted`, `share_archived`, `share_unarchived`, `share_imported_to_workspace`

**AI:** `ai_chat_created`, `ai_chat_new_message`, `ai_chat_updated`, `ai_chat_deleted`, `ai_chat_published`, `node_ai_summary_created`, `workspace_ai_share_created`

**Metadata:** `metadata_kv_update`, `metadata_kv_delete`, `metadata_kv_extract`, `metadata_template_update`, `metadata_template_delete`, `metadata_template_settings_update`, `metadata_view_update`, `metadata_view_delete`, `metadata_template_select`

**Quick shares:** `workspace_quickshare_created`, `workspace_quickshare_updated`, `workspace_quickshare_deleted`, `workspace_quickshare_file_downloaded`, `workspace_quickshare_file_previewed`

**Invitations:** `invitation_email_sent`, `invitation_accepted`, `invitation_declined`

**User:** `user_created`, `user_updated`, `user_deleted`, `user_email_reset`, `user_asset_updated`

**Org:** `org_created`, `org_updated`, `org_closed`, `org_transfer_token_created`, `org_transfer_completed`

**Billing:** `subscription_created`, `subscription_cancelled`, `billing_free_trial_ended`

#### Example Queries

- **Recent comments in a workspace:** `event` action `search` with `workspace_id` and `subcategory: "comments"`
- **Files uploaded to a share:** `event` action `search` with `share_id` and `event: "share_storage_file_added"`
- **All membership changes across an org:** `event` action `search` with `org_id` and `subcategory: "members"`
- **AI activity in a workspace:** `event` action `search` with `workspace_id` and `category: "ai"`
- **Who downloaded files from a share:** `event` action `search` with `share_id` and `event: "share_storage_download_token_created"`

### Activity Polling

Three mechanisms for detecting changes, listed from most to least preferred:

1. **`event` action `activity-poll`** — The server holds the connection for up to 95 seconds and returns immediately when something changes. Returns activity keys (e.g. `ai_chat:{chatId}`, `storage`, `members`) and a `lastactivity` timestamp for the next poll. Use this for any "wait for something to happen" scenario, including AI chat completion.
2. **WebSocket** — For real-time push events. Best for live UIs.
3. **`event` action `activity-list`** — Retrieves recent activity events on demand. Use when you need a one-time snapshot rather than continuous monitoring.

**Why this matters:** Do not poll detail endpoints (like `ai` action `message-read`) in tight loops. Instead, use `event` action `activity-poll` to detect when something has changed, then fetch the details once.

#### AI Message Completion

`ai` action `message-read` (with `context_type: "workspace"` or `"share"`) implements built-in polling (up to 15 attempts, 2-second intervals). If the response is still processing after that window, use `event` action `activity-poll` with the workspace or share ID instead of calling the read action in a loop:

1. Call `event` action `activity-poll` with `entity_id` set to the workspace/share ID.
2. When the response includes an `ai_chat:{chatId}` key matching your chat, call `ai` action `message-read` once to get the completed response.

#### Activity Poll Workflow

1. Make an API call (e.g. `ai` action `chat-create`) and note the `server_date` field in the response.
2. Call `event` action `activity-poll` with `entity_id` (workspace or share ID) and `lastactivity` set to the `server_date` value.
3. The server holds the connection. When something changes (or the wait period expires), it returns activity keys.
4. Inspect the keys to determine what changed, then fetch the relevant detail (e.g. `ai` action `message-read`, `storage` action `list`).
5. Use the new `lastactivity` value from the poll response (or the latest `server_date`) for the next poll call. Repeat as needed.

### Trash, Delete, and Purge

- `storage` action `delete` (with `context_type: "workspace"` or `"share"`) moves items to the trash. They are recoverable.
- `storage` action `restore` recovers items from the trash.
- `storage` action `purge` permanently and irreversibly deletes items from the trash.

Always confirm with the user before calling purge operations.

### Node Types

Storage nodes can be files, folders, notes, or links. The type is indicated in the storage details response. Notes are markdown files created with `workspace` action `create-note`, read with `workspace` action `read-note`, and updated with `workspace` action `update-note`. Links are share reference nodes created with `storage` action `add-link`.

### Text Content and Newlines

All text content (notes, comments, worklogs, file uploads, descriptions) must use Unix-style line feeds (`\n`, U+000A) for newlines. The frontend normalizes all line endings to `\n` before saving -- Windows-style `\r\n` (CRLF) and legacy Mac `\r` (CR) are converted automatically. Agents should use `\n` exclusively to avoid mismatches in content comparison and display.

**Encoding rules:**

- **Newlines:** Use `\n` (U+000A). Never send `\r\n` or `\r` alone.
- **Allowed control characters:** Only `\t` (U+0009), `\n` (U+000A), and `\r` (U+000D) survive server-side sanitization. All other Unicode control characters (`\p{C}`) are stripped.
- **Empty lines in markdown:** Use two consecutive `\n` characters (`\n\n`) for paragraph breaks. Do not use non-breaking spaces (U+00A0) or other whitespace characters as line placeholders.
- **Trailing newlines:** Content may or may not end with a trailing `\n`. Do not assume either convention -- both are valid.

This applies to: `workspace` actions `create-note` and `update-note`, `upload` action `text-file`, `comment` action `add`, `worklog` actions `append` and `interject`, and any other tool that accepts free-text or markdown content.

### Error Pattern

Failed API calls throw errors with two fields: `code` (unique numeric error ID) and `text` (human-readable description). Tools surface these as error text in the MCP response. Common HTTP status codes include 401 (unauthorized), 403 (forbidden), 404 (not found), and 429 (rate limited).

### Session State

The auth token, user ID, email, and token expiry are persisted in the server session. There is no need to pass tokens between tool calls. The session survives across multiple tool invocations within the same MCP connection.

### Human-Facing URLs

MCP tools manage data via the API, but humans access Fast.io through a web browser. **Always use the `web_url` field from tool responses** -- it is a ready-to-use, clickable URL for the resource. Include it in your responses whenever you create or reference a workspace, share, file, note, or transfer. The human cannot see API responses directly -- the URL you provide is how they get to their content. Fall back to the URL patterns below only when `web_url` is absent (e.g., share-context storage operations):

> **Automatic `web_url` field.** All entity-returning tool responses include a `web_url` field — a ready-to-use, human-friendly URL for the resource. **NEVER construct URLs manually — always use the `web_url` field from tool responses.** It appears on: org list/details/create/update/public-details/discover-*, org list-workspaces/list-shares, workspace list/details/update/available/list-shares, share list/details/create/update/public-details/available, storage list/details/search/trash-list/copy/move/rename/restore/add-file/create-folder/version-list/version-restore/preview-url/preview-transform, quickshare create/get/list, upload text-file/finalize, download file-url/quickshare-details, AI chat-create/chat-details/chat-list, transfer-token create/list, and notes create/update. Fall back to the URL patterns below only when `web_url` is absent (e.g., share context storage operations).

Organization `domain` values become subdomains: `"acme"` → `https://acme.fast.io/`. The base domain `go.fast.io` handles public routes that do not require org context.

#### Authenticated Links (require login)

| What the human needs | URL pattern |
|---------------------|-------------|
| Workspace root | `https://{domain}.fast.io/workspace/{folder_name}/storage/root` |
| Specific folder | `https://{domain}.fast.io/workspace/{folder_name}/storage/{node_id}` |
| File preview | `https://{domain}.fast.io/workspace/{folder_name}/preview/{node_id}` |
| File with specific comment | `https://{domain}.fast.io/workspace/{folder_name}/preview/{node_id}?comment={comment_id}` |
| File at video/audio time | `https://{domain}.fast.io/workspace/{folder_name}/preview/{node_id}?t={seconds}` |
| File at PDF page | `https://{domain}.fast.io/workspace/{folder_name}/preview/{node_id}?p={page_num}` |
| AI chat in workspace | `https://{domain}.fast.io/workspace/{folder_name}/storage/root?chat={chat_id}` |
| Note in workspace | `https://{domain}.fast.io/workspace/{folder_name}/storage/root?note={note_id}` |
| Note preview | `https://{domain}.fast.io/workspace/{folder_name}/preview/{note_id}` |
| Browse workspaces | `https://{domain}.fast.io/browse-workspaces` |
| Edit share settings | `https://{domain}.fast.io/workspace/{folder_name}/share/{custom_name}` |
| Org settings | `https://{domain}.fast.io/settings` |
| Billing | `https://{domain}.fast.io/settings/billing` |

#### Public Links (no login required)

| What the human needs | URL pattern |
|---------------------|-------------|
| Public share | `https://go.fast.io/shared/{custom_name}/{title-slug}` |
| Org-branded share | `https://{domain}.fast.io/shared/{custom_name}/{title-slug}` |
| File in share | `https://go.fast.io/shared/{custom_name}/{title-slug}/preview/{node_id}` |
| File in share with comment | `https://go.fast.io/shared/{custom_name}/{title-slug}/preview/{node_id}?comment={comment_id}` |
| QuickShare | `https://go.fast.io/quickshare/{quickshare_id}` |
| Claim org transfer | `https://go.fast.io/claim?token={transfer_token}` |
| Onboarding | `https://go.fast.io/onboarding` or `https://go.fast.io/onboarding?orgId={org_id}&orgDomain={domain}` |

#### Where the values come from

| Value | API source |
|-------|-----------|
| `domain` | `org` action `create` or `details` response |
| `folder_name` | `org` action `create-workspace` or `workspace` action `details` response |
| `node_id` | `storage` action `list`, `create-folder`, or `add-file` response |
| `custom_name` | `share` action `create` or `details` response (the `{title-slug}` is cosmetic -- the share resolves on `custom_name` alone) |
| `quickshare_id` | `workspace` action `quickshare-create` response |
| `transfer_token` | `org` action `transfer-token-create` response |
| `chat_id` | `ai` action `chat-create` or `chat-list` response |
| `note_id` | `workspace` action `create-note` or `storage` action `list` response (node opaque ID) |
| `comment_id` | `comment` action `add` or `list` response |
| `org_id` | `org` action `create` or `list` response |

**Always provide URLs to the human in these situations:**

- **Created a workspace?** Include the workspace URL in your response. Example: `https://acme.fast.io/workspace/q4-reports/storage/root`
- **Created or configured a share?** Include the share URL. Example: `https://go.fast.io/shared/q4-financials/Q4-Financial-Report` -- this is the branded page the human (or their recipients) will open.
- **Generated a transfer token?** Include the claim URL. Example: `https://go.fast.io/claim?token=abc123` -- this is the only way the human can claim ownership.
- **Uploaded files or created folders?** Include the workspace URL pointing to the relevant folder so the human can see what you built.
- **Human asks "where can I see this?"** Construct the URL from API response data you already have and provide it.

**Important:** The `domain` is the org's domain string (e.g. `acme`), not the numeric org ID. The `folder_name` is the workspace's folder name string (e.g. `q4-reports`), not the numeric workspace ID. Both are returned by their respective API tools.

### Response Hints (`_next`, `_warnings`, and `_recovery`)

Workflow-critical tool responses include a `_next` field -- a short array of suggested next actions using exact tool and action names. Use these hints to guide your workflow instead of guessing what to do next. Example:

```json
{
  "workspace_id": "...",
  "web_url": "https://acme.fast.io/workspace/q4-reports/storage/root",
  "_next": [
    "Upload files: upload action text-file or web-import",
    "Create a share: share action create",
    "Query with AI: ai action chat-create"
  ]
}
```

**`_warnings`** appear on destructive, irreversible, or potentially problematic actions. Always read warnings before proceeding -- they flag permanent consequences or important caveats. Actions with `_warnings`: storage purge, storage bulk copy/move/delete/restore (partial failures), workspace details (intelligence=false), workspace update (intelligence=false), workspace archive/delete, org close, org billing-create, share delete, share archive, share update (type change), ai chat-delete, download file-url (token expiry), download zip-url (auth required), upload stage-blob (5-min expiry), org transfer-token-create.

**`_recovery`** hints appear on error responses (when `isError: true`). They provide recovery actions based on HTTP status codes AND error message pattern matching. Error messages also include action context (e.g., "during: org create") to help pinpoint the failing operation.

| HTTP Status | Recovery |
|-------------|----------|
| 400 | Check required parameters and ID formats |
| 401 | Re-authenticate: auth action signin or pkce-login |
| 402 | Credits exhausted -- check balance: org action limits |
| 403 | Permission denied -- check role: org action details |
| 404 | Resource not found -- verify the ID, use list actions to discover valid IDs |
| 409 | Conflict -- resource may already exist |
| 413 | Request too large -- reduce file/chunk size |
| 422 | Validation error -- check field formats and constraints |
| 429 | Rate limited -- wait 2-4s and retry with exponential backoff |
| 500/503 | Server error -- retry after 2-5 seconds |

Pattern-based recovery: error messages are also matched against common patterns (e.g., "email not verified", "workspace not found", "intelligence disabled") to provide specific recovery steps even when the HTTP status is generic.

**`ai_capabilities`** is included in workspace details responses. It shows which AI modes are available based on the workspace intelligence setting:
- Intelligence ON: `files_scope`, `folders_scope`, `files_attach` (full RAG with indexed document search)
- Intelligence OFF: `files_attach` only (max 20 files, 200 MB, no RAG indexing)

**`_ai_state_legend`** is included in storage list and search responses when files have AI indexing state. States: `ready` (indexed, queryable), `pending` (queued), `inprogress` (indexing), `disabled` (intelligence off), `failed` (re-upload needed). Also includes `_attach_field` explaining the `ai.attach` boolean — check this flag before using `files_attach`.

**`_context`** provides contextual metadata on specific responses. Currently used by comment add when anchoring is involved, providing `anchor_formats` with the expected format for image regions, video/audio timestamps, and PDF pages.

**All tool actions now include `_next` hints.** Every successful tool response includes contextual next-step suggestions. Key workflow transitions: auth → org list/create, org create → workspace create, workspace create → upload/share/AI, upload → AI chat/comment/download, share create → add files/members, AI chat create → message read. The hints include the exact tool name, action, and relevant IDs from the current response.

**Tool annotations:** Tools include MCP annotation hints -- `readOnlyHint`, `destructiveHint`, `idempotentHint` (download, event), and `openWorldHint` (org, user, workspace, share, storage) -- to help clients understand tool behavior without documentation.

**Resource completion and listing:** The workspace and share download resource templates support both dynamic listing (`resources/list`) and tab-completion (`completion/complete`). Dynamic listing shows root-level files across workspaces and shares in the client's resource picker. Tab-completion suggests valid workspace and share IDs as you type.

### Unauthenticated Tools

The following actions work without a session: `auth` actions `signin`, `signup`, `set-api-key`, `pkce-login`, `email-check`, `password-reset-request`, `password-reset`; and `download` action `quickshare-details`.

---

## 8. MCP Apps (Interactive UI Widgets)

Fast.io MCP Server includes interactive HTML5 widgets that render rich UIs directly in agent conversations. Widgets communicate with the MCP server through tool calls and display file browsers, dashboards, workflow managers, and more.

### Available Widgets

| Widget | Resource URI | Description |
|--------|-------------|-------------|
| File Picker | `widget://file-picker` | Browse and pick files to attach to your conversation — navigate folders, search, preview, select files for the agent. Also supports file management (upload, move, copy, delete) in workspace and share contexts |
| Workspace Picker | `widget://workspace-picker` | Org/workspace/share selection with search, 4-step workspace creation wizard, 5-step share creation wizard |
| File Viewer | `widget://file-viewer` | Unified file preview (image, PDF, video, audio, code, spreadsheet) with info panel (details, versions, AI summary, metadata) |
| Workflow Manager | `widget://workflow` | Task board, task detail, approvals panel, todos checklist, worklog viewer |
| Comments Panel | `widget://comments` | Threaded comments, reactions, anchored comments (image regions, timestamps) |

### Using the Apps Tool

The `apps` tool provides widget discovery and launching:

1. **List apps:** `apps` action `list` -- returns all available widgets with metadata
2. **App details:** `apps` action `details` with `app_id` -- full metadata for a specific widget
3. **Launch app:** `apps` action `launch` with `app_id`, `context_type`, `context_id` -- opens widget with context
4. **Find apps for a tool:** `apps` action `get-tool-apps` with `tool_name` -- maps tools to their widgets

### Widget Context

All widgets accept workspace or share context:
- `context_type: "workspace"` + `context_id: "<workspace_id>"`
- `context_type: "share"` + `context_id: "<share_id>"`

### Design System

Widgets use a shared design system matching the Fast.io frontend:
- Light and dark mode support (follows system preference or explicit `data-theme` attribute)
- Consistent typography, spacing, colors, and icons derived from the frontend theme
- Responsive layout (desktop, tablet, mobile breakpoints)

### Example: Launch File Picker

```
apps action launch app_id file-picker context_type workspace context_id <workspace_id>
```

### Example: Find Widgets for Storage Operations

```
apps action get-tool-apps tool_name storage
```

---

## 9. Complete Tool Reference

All 19 tools with their actions organized by functional area. Each entry shows the action name and its description. Workflow tools (task, worklog, approval, todo) require workflow to be enabled on the target workspace or share.

### auth

**signin** -- Sign in to Fast.io with email and password. Returns a JWT auth token. If the account has 2FA enabled the token will have limited scope until 2fa-verify is called. The token is stored in the session automatically.

**set-api-key** -- Authenticate using a Fast.io API key. API keys work as Bearer tokens and by default have the same permissions as the account owner. Scoped keys restrict access to specific entities (same scope system as OAuth tokens). The key is validated against the API and stored in the session. All subsequent tool calls are authenticated automatically. Unscoped API keys do not expire unless revoked; scoped keys may have an optional expiration.

**signup** -- Create a new Fast.io agent account (agent=true), then automatically sign in. Sets account_type to "agent" and assigns the free agent plan. Email verification is required after signup -- call email-verify to send a code, then call it again with the code to verify. Most endpoints require a verified email. No authentication required for signup itself.

**check** -- Check whether the current session token is still valid. Returns the user ID associated with the token.

**session** -- Get current session information for the authenticated user, including profile details such as name, email, and account flags.

**signout** -- Sign out by clearing the stored session. If currently authenticated the token is verified first.

**2fa-verify** -- Complete two-factor authentication by submitting a 2FA code. Call this after signin returns two_factor_required: true. The new full-scope token is stored automatically.

**email-check** -- Check if an email address is available for registration. No authentication required.

**password-reset-request** -- Request a password reset email. Always returns success for security (does not reveal whether the email exists). No authentication required.

**password-reset** -- Set a new password using a reset code received by email. No authentication required.

**email-verify** -- Send or validate an email verification code. When email_token is omitted a new code is sent. When provided the code is validated and the email marked as verified.

**status** -- Check local session status. No API call is made. Returns whether the user is authenticated, and if so their user_id, email, token expiry, scopes (raw string), scopes_detail (hydrated array with entity names, domains, and parent hierarchy -- or null if not yet fetched), and agent_name (if set).

**pkce-login** -- Start a browser-based PKCE login flow. Returns a URL for the user to open in their browser. After signing in and approving access, the browser displays an authorization code. The user copies the code and provides it to pkce-complete to finish signing in. No password is sent through the agent. Optional params: `scope_type` (default `"user"` for full access; use `"org"`, `"workspace"`, `"all_orgs"`, `"all_workspaces"`, or `"all_shares"` for scoped access), `agent_name` (displayed in the approval screen and audit logs; defaults to MCP client name).

**pkce-complete** -- Complete a PKCE login flow by exchanging the authorization code for an access token. Call this after the user has approved access in the browser and copied the code from the screen. The token is stored in the session automatically. If scoped access was granted, the response includes `scopes` (JSON array of granted scope strings like `"org:123:rw"`) and `agent_name`.

**api-key-create** -- Create a new persistent API key. The full key value is only returned once at creation time -- store it securely. Optional parameters: `name` (memo/label), `scopes` (JSON array of scope strings like `["org:123:rw", "workspace:456:r"]` for restricted access -- omit for full access), `agent_name` (agent/application name, max 128 chars), `key_expires` (ISO 8601 expiration datetime -- omit for no expiration). Scoped keys use the same scope system as v2.0 JWT tokens.

**api-key-update** -- Update an existing API key's metadata. Requires `key_id`. Optional parameters: `name` (memo/label), `scopes` (JSON scope array -- send empty string to clear and restore full access), `agent_name` (send empty string to clear), `key_expires` (send empty string to clear expiration). Only specified fields are updated.

**api-key-list** -- List all API keys for the authenticated user. Key values are masked (only last 4 characters visible). Responses include `scopes`, `agent_name`, and `expires` fields for each key.

**api-key-get** -- Get details of a specific API key. The key value is masked. Response includes `scopes`, `agent_name`, and `expires` fields.

**api-key-delete** -- Revoke (delete) an API key. This action cannot be undone.

**2fa-status** -- Get the current two-factor authentication configuration status (enabled, unverified, or disabled).

**2fa-enable** -- Enable two-factor authentication on the specified channel. For TOTP, returns a binding URI for QR code display. The account enters an 'unverified' state until 2fa-verify-setup is called.

**2fa-disable** -- Disable (remove) two-factor authentication from the account. Requires a valid 2FA code to confirm when 2FA is in the enabled (verified) state.

**2fa-send** -- Send a 2FA verification code to the user's phone via SMS, voice call, or WhatsApp.

**2fa-verify-setup** -- Verify a 2FA setup code to confirm enrollment. Transitions 2FA from the 'unverified' state to 'enabled'.

**oauth-list** -- List all active OAuth sessions for the authenticated user.

**oauth-details** -- Get details of a specific OAuth session.

**oauth-revoke** -- Revoke a specific OAuth session (log out that device).

**oauth-revoke-all** -- Revoke all OAuth sessions. Optionally exclude the current session to enable 'log out everywhere else'.

### user

**me** -- Get the current authenticated user's profile details.

**update** -- Update the current user's profile (name, email, etc.).

**search** -- Search for users by name or email address.

**close** -- Close/delete the current user account (requires email confirmation).

**details-by-id** -- Get another user's public profile details by their user ID.

**profiles** -- Check what profile types (orgs, workspaces, shares) the user has access to.

**allowed** -- Check if the user's country allows creating shares and organizations.

**org-limits** -- Get free org creation eligibility, limits, and cooldown status.

**list-shares** -- List all shares the current user is a member of.

**invitation-list** -- List all pending invitations for the current user.

**invitation-details** -- Get details of a specific invitation by its ID or key.

**accept-all-invitations** -- Accept all pending invitations at once.

**asset-upload** -- Upload a user asset (e.g. profile photo). Provide either plain-text content or base64-encoded content_base64 (not both).

**asset-delete** -- Delete a user asset (e.g. profile photo).

**asset-types** -- List available asset types for users.

**asset-list** -- List all user assets.

### org

**list** -- List internal organizations (orgs the user is a direct member of, `member: true`). Each org includes `web_url`. Returns member orgs with subscription status, user permission, and plan info. Non-admin members only see orgs with active subscriptions. Does not include external orgs -- use discover-external for those.

**details** -- Get detailed information about an organization. Returns `web_url`. Fields returned vary by the caller's role: owners see encryption keys and storage config, admins see billing and permissions, members see basic info.

**members** -- List all members of an organization with their IDs, emails, names, and permission levels.

**invite-member** -- Invite a user to the organization by email. The email is passed in the URL path (not the body). If the user already has a Fast.io account they are added directly; otherwise an email invitation is sent. Cannot add as owner.

**remove-member** -- Remove a member from the organization. Requires member management permission as configured by the org's perm_member_manage setting.

**update-member-role** -- Update a member's role/permissions in the organization. Cannot set role to 'owner' -- use transfer-ownership instead.

**limits** -- Get organization plan limits and credit usage. Returns credit limits, usage stats, billing period, trial info, and run-rate projections. Requires admin or owner role.

**list-workspaces** -- List workspaces in an organization that the current user can access. Each workspace includes `web_url`. Owners and admins see all workspaces; members see workspaces matching the join permission setting.

**list-shares** -- List shares accessible to the current user. Each share includes `web_url`. Returns all shares including parent org and workspace info. Use parent_org in the response to identify shares belonging to a specific organization.

**create** -- Create a new organization on the "agent" billing plan. The authenticated user becomes the owner. A storage instance and agent-plan subscription (free, 50 GB, 5,000 credits/month) are created automatically. Returns the new org and trial status.

**update** -- Update organization details. Returns `web_url`. Only provided fields are changed. Supports identity, branding, social links, permissions, and billing email. Requires admin or owner role.

**close** -- Close/delete an organization. Cancels any active subscription and initiates deletion. Requires owner role. The confirm field must match the org domain or org ID.

**public-details** -- Get public details for an organization. Returns `web_url`. Does not require membership -- returns public-level fields only (name, domain, logo, accent color). The org must exist and not be closed/suspended.

**create-workspace** -- Create a new workspace within the organization. Returns `web_url`. Checks workspace feature availability and creation limits based on the org billing plan. The creating user becomes the workspace owner. **Namespace:** Workspace `folder_name` is globally unique across the platform. If the requested name is already taken and does not contain a dash, the server automatically prefixes it with the org ID (e.g. `reports` → `3587676312889739297-reports`). Names with dashes are sent as-is. The final `folder_name` is returned in the response.

**billing-plans** -- List available billing plans with pricing, features, and plan defaults. Returns plan IDs needed for subscription creation.

**billing-create** -- Create a new subscription or update an existing one. For new subscriptions, creates a Stripe Setup Intent. For existing subscriptions, updates the plan. Requires admin or owner.

**billing-cancel** -- Cancel the organization's subscription. Requires owner role. Some plans may cause the org to be closed on cancellation.

**billing-details** -- Get comprehensive billing and subscription details including Stripe customer info, subscription status, setup intents, payment intents, and plan info. Requires admin or owner.

**billing-activate** -- Activate a billing plan (development environment only). Simulates Stripe payment setup and activates the subscription using a test payment method.

**billing-reset** -- Reset billing status (development environment only). Deletes the Stripe customer and removes the subscriber flag.

**billing-members** -- List billable members with their workspace memberships. Shows who the org is being billed for. Requires admin or owner role.

**billing-meters** -- Get usage meter time-series data (storage, transfer, AI, etc). Returns grouped data points with cost and credit calculations. Requires admin or owner role.

**leave** -- Leave an organization. Removes the current user's own membership. Owners cannot leave -- they must transfer ownership or close the org first.

**member-details** -- Get detailed membership information for a specific user in the organization, including permissions, invite status, notification preference, and expiration.

**transfer-ownership** -- Transfer organization ownership to another member. The current owner is demoted to admin. Requires owner role.

**transfer-token-create** -- Create a transfer token (valid 72 hours) for an organization. Send the claim URL `https://go.fast.io/claim?token=<token>` to a human. Use when handing off an org or when hitting 402 Payment Required on the agent plan. Requires owner role.

**transfer-token-list** -- List all active transfer tokens for an organization. Each token includes `web_url` (claim URL). Requires owner role.

**transfer-token-delete** -- Delete (revoke) a pending transfer token. Requires owner role.

**transfer-claim** -- Claim an organization using a transfer token. The authenticated user becomes the new owner and the previous owner is demoted to admin.

**invitations-list** -- List all pending invitations for the organization. Optionally filter by invitation state. Requires any org membership.

**invitation-update** -- Update an existing invitation for the organization. Can change state, permissions, or expiration.

**invitation-delete** -- Revoke/delete an invitation for the organization.

**join** -- Join an organization via invitation or authorized domain auto-join. Optionally provide an invitation key and action (accept/decline).

**asset-upload** -- Upload an org asset (e.g. logo, banner). Provide either plain-text content or base64-encoded file_base64 (not both). Requires admin or owner role.

**asset-delete** -- Delete an asset from the organization. Requires admin or owner role.

**asset-types** -- List available asset types for organizations.

**asset-list** -- List all organization assets.

**discover-all** -- List all accessible organizations (joined + invited). Each org includes `web_url`. Returns org data with user_status indicating relationship.

**discover-available** -- List organizations available to join. Each org includes `web_url`. Excludes orgs the user is already a member of.

**discover-check-domain** -- Check if an organization domain name is available for use. Validates format, checks reserved names, and checks existing domains.

**discover-external** -- List external organizations (`member: false`). Each org includes `web_url`. Orgs the user can access only through workspace membership, not as a direct org member. Common when a human invites an agent to a workspace without inviting them to the org. See **Internal vs External Orgs** in the Organizations section.

### workspace

**list** -- List all workspaces the user has access to across all organizations. Each workspace includes `web_url`.

**details** -- Get detailed information about a specific workspace. Returns `web_url`.

**update** -- Update workspace settings such as name, description, branding, and permissions. Returns `web_url`.

**delete** -- Permanently close (soft-delete) a workspace. Requires Owner permission and confirmation.

**archive** -- Archive a workspace (blocks modifications, preserves data). Requires Admin+.

**unarchive** -- Restore an archived workspace to active status. Requires Admin+.

**members** -- List all members of a workspace with their roles and status.

**list-shares** -- List all shares within a workspace, optionally filtered by archive status. Each share includes `web_url`.

**import-share** -- Import a user-owned share into a workspace. You must be the sole owner of the share.

**available** -- List workspaces the current user can join but has not yet joined. Each workspace includes `web_url`.

**check-name** -- Check if a workspace folder name is available for use. Workspace names are globally unique. Pass optional `check_org_id` to get an org-ID-prefixed alternative suggestion (e.g. `3587676312889739297-reports`) if the name is taken.

**create-note** -- Create a new markdown note in workspace storage. Returns `web_url` (note preview link).

**update-note** -- Update a note's markdown content and/or name (at least one required). Returns `web_url` (note preview link).

**read-note** -- Read a note's markdown content and metadata. Returns the note content and `web_url` (note preview link).

**quickshare-get** -- Get existing quickshare details for a node. Returns `web_url`.

**quickshare-delete** -- Revoke and delete a quickshare link for a node.

**quickshares-list** -- List all active quickshares in the workspace. Each quickshare includes `web_url`.

**metadata-template-create** -- Create a new metadata template in the workspace. Requires name, description, category (legal, financial, business, medical, technical, engineering, insurance, educational, multimedia, hr), and fields (JSON-encoded array of field definitions). Each field has name, description, type (string, int, float, bool, json, url, datetime), and optional constraints (min, max, default, fixed_list, can_be_null).

**metadata-template-delete** -- Delete a metadata template. System templates and locked templates cannot be deleted. Requires template_id.

**metadata-template-list** -- List metadata templates. Optional template_filter: enabled, disabled, custom (non-system), or system. Returns all non-deleted templates when no filter is specified.

**metadata-template-details** -- Get full details of a metadata template including all field definitions. Requires template_id.

**metadata-template-update** -- Update an existing metadata template. Any combination of name, description, category, and fields can be updated. Requires template_id.

**metadata-template-clone** -- Clone a metadata template with optional modifications. Creates a new template based on an existing one. Same parameters as metadata-template-update. Requires template_id.

**metadata-template-assign** -- Assign a metadata template to a workspace. Each workspace can have at most one assigned template. Assigning a system template automatically clones it. Requires template_id. Optional node_id (null for workspace-level assignment).

**metadata-template-unassign** -- Remove the template assignment from a workspace. Requires workspace admin permission.

**metadata-template-resolve** -- Resolve which metadata template applies to a given node. Returns the workspace-level template (node_id is accepted but currently inherits from workspace). Returns null if no template is assigned.

**metadata-template-assignments** -- List all template assignments in the workspace.

**metadata-get** -- Get all metadata for a file, including both template-conforming metadata and custom (freeform) key-value pairs. Returns node details, template_id, template_metadata array, and custom_metadata array. Requires node_id.

**metadata-set** -- Set or update metadata key-value pairs on a file. Values must conform to the template field definitions. Requires node_id, template_id, and key_values (JSON object of key-value pairs).

**metadata-delete** -- Delete metadata from a file. Provide keys (JSON array of key names) to delete specific entries, or omit to delete all metadata. Only works on files and notes, not folders. Requires node_id.

**metadata-extract** -- Trigger AI-powered metadata extraction from a file. The AI analyzes file content and populates metadata fields according to the template. Extracted values are marked with is_auto: true. Consumes AI credits. Optional template_id (defaults to workspace template). Requires node_id.

**metadata-list-files** -- List files that have metadata for a specific template, with optional filtering and sorting. Requires node_id (folder to search in) and template_id. Optional metadata_filters (JSON-encoded), order_by (field key), and order_desc.

**metadata-list-templates-in-use** -- List which metadata templates are in use within a folder, with usage counts per template. Requires node_id.

**metadata-versions** -- Get metadata version history for a file. Returns snapshots of metadata changes over time. Requires node_id.

**enable-workflow** -- Enable workflow features (tasks, worklogs, approvals, todos) on a workspace. Must be called before using workflow tools on the workspace.

**disable-workflow** -- Disable workflow features on a workspace. All workflow data is preserved but inaccessible until re-enabled.

### share

**list** -- List shares the authenticated user has access to. Each share includes `web_url`.

**details** -- Get full details of a specific share. Returns `web_url`.

**create** -- Create a new share in a workspace.

**update** -- Update share settings (partial update).

**delete** -- Delete (close) a share. Requires the share ID or custom name as confirmation.

**public-details** -- Get public-facing share info (no membership required, just auth).

**archive** -- Archive a share. Blocks guest access and restricts modifications.

**unarchive** -- Restore a previously archived share to active status.

**password-auth** -- Authenticate with a share password. Returns a scoped JWT for the share.

**members** -- List all members of a share.

**available** -- List shares available to join (joined and owned, excludes pending invitations). Each share includes `web_url`.

**check-name** -- Check if a share custom name (URL name) is available.

**quickshare-create** -- Create a temporary QuickShare link for a file in a workspace.

**enable-workflow** -- Enable workflow features (tasks, worklogs, approvals, todos) on a share. Must be called before using workflow tools on the share.

**disable-workflow** -- Disable workflow features on a share. All workflow data is preserved but inaccessible until re-enabled.

### storage

All storage actions require `context_type` parameter (`workspace` or `share`) and `context_id` (the 19-digit profile ID).

**list** -- List files and folders in a directory with pagination. Each item includes `web_url` (workspace only). Requires `context_type`, `context_id`, and `node_id` (use `root` for root folder).

**recent** -- List recently modified files and folders across all directories, sorted by updated descending. Unlike `list` which is scoped to a single folder, this returns nodes from the entire storage tree. Supports optional `type` filter (`file`, `folder`, `link`, `note`), `page_size` (100, 250, or 500), and `cursor` for pagination. For workspace folder shares, results are automatically filtered to the share's subtree.

**details** -- Get full details of a specific file or folder. Returns `web_url` (human-friendly link to the file preview or folder in the web UI, workspace only).

**search** -- Search for files by keyword or semantic query. Each result includes `web_url` (workspace only).

**trash-list** -- List items currently in the trash. Each item includes `web_url` (workspace only).

**create-folder** -- Create a new folder. Returns `web_url` (workspace only).

**copy** -- Copy files/folders. Single copy via `node_id` (workspace or share). Bulk copy via `node_ids` array (workspace only). Returns `web_url` on the new copy (workspace only).

**move** -- Move files/folders. Single move via `node_id` (workspace or share). Bulk move via `node_ids` array (workspace only). Returns `web_url` (workspace only).

**delete** -- Delete files/folders by moving them to the trash. Single delete via `node_id` (workspace or share). Bulk delete via `node_ids` array (workspace only).

**rename** -- Rename a file or folder. Returns `web_url` (workspace only).

**purge** -- Permanently delete a trashed node (irreversible). Requires Member permission.

**restore** -- Restore files/folders from the trash. Single restore via `node_id` (workspace or share). Bulk restore via `node_ids` array (workspace only). Returns `web_url` on the restored node (workspace only).

**add-file** -- Link a completed upload to a storage location. Returns `web_url` (workspace only).

**add-link** -- Add a share reference link node to storage.

**transfer** -- Copy a node to another workspace or share storage instance.

**version-list** -- List version history for a file. Returns `web_url` for the file (workspace only).

**version-restore** -- Restore a file to a previous version. Returns `web_url` for the file (workspace only).

**lock-acquire** -- Acquire an exclusive lock on a file to prevent concurrent edits.

**lock-status** -- Check the lock status of a file.

**lock-release** -- Release an exclusive lock on a file.

**preview-url** -- Get a preauthorized preview URL for a file (thumbnail, PDF, image, video, audio, spreadsheet). Requires `preview_type` parameter. Returns `preview_url` (ready-to-use URL) and `web_url` (human-friendly link to the file in the web UI, workspace only).

**preview-transform** -- Request a file transformation (image resize, crop, format conversion) and get a download URL for the result. Requires `transform_name` parameter. Returns `transform_url` (ready-to-use URL) and `web_url` (human-friendly link to the file in the web UI, workspace only).

### upload

**create-session** -- Create a chunked upload session for a file.

**chunk** -- Upload a single chunk. Use `content` for text/strings, `data` for base64-encoded binary, or `blob_ref` for binary staged via `stage-blob` action or `POST /blob`. Provide exactly one.

**finalize** -- Finalize an upload session, trigger file assembly, and poll until fully stored or failed. Returns the final session state.

**status** -- Get the current status of an upload session. Supports server-side long-poll via optional `wait` parameter (in milliseconds, 0 = immediate).

**cancel** -- Cancel and delete an active upload session.

**list-sessions** -- List all active upload sessions for the current user.

**cancel-all** -- Cancel and delete ALL active upload sessions at once.

**chunk-status** -- Get chunk information for an upload session.

**chunk-delete** -- Delete/reset a chunk in an upload session.

**stage-blob** -- Stage base64-encoded binary data as a blob for later use with the `chunk` action's `blob_ref` parameter. Pass `data` (base64 string). Returns `{ blob_id, size }`. Blobs expire after 5 minutes and are consumed on first use. Alternative to passing `data` directly in the chunk call.

**text-file** -- Upload a text file in a single step. Creates an upload session, uploads the content, finalizes, and polls until stored. Returns the new file ID. Use for text-based files (code, markdown, CSV, JSON, config) instead of the multi-step chunked flow.

**web-import** -- Import a file from an external URL into a workspace or share.

**web-list** -- List the user's web upload jobs with optional filtering.

**web-cancel** -- Cancel an active web upload job.

**web-status** -- Get detailed status of a specific web upload job.

**limits** -- Get upload size and chunk limits for the user's plan.

**extensions** -- Get restricted and allowed file extensions for uploads.

### download

**file-url** -- Get a download token and URL for a file. Optionally specify a version. Requires `context_type`, `context_id`, and `node_id`.

**zip-url** -- Get a ZIP download URL for a folder or entire workspace/share. Returns the URL with auth instructions. Requires `context_type`, `context_id`, and `node_id` (use `root` for entire storage tree).

**quickshare-details** -- Get metadata and download info for a quickshare link. No authentication required.

### ai

All AI actions require `context_type` parameter (`workspace` or `share`) and `context_id` (the 19-digit profile ID).

**chat-create** -- Create a new AI chat with an initial question. Default scope is the entire workspace (all indexed documents) — omit `files_scope` and `folders_scope` unless you need to narrow the search. When using scope or attachments, provide `nodeId:versionId` pairs — versionId is auto-resolved to the current version if left empty (get explicit `versionId` from storage list/details `version` field). When using `files_attach`, verify `ai.attach` is `true` for each file first (check via storage details). Type is auto-promoted from `chat` to `chat_with_files` when file parameters are present. Returns chat ID and initial message ID -- use message-read to get the AI response.

**chat-list** -- List AI chats.

**chat-details** -- Get AI chat details including full message history.

**chat-update** -- Update the name of an AI chat.

**chat-delete** -- Delete an AI chat.

**chat-publish** -- Publish a private AI chat, making it visible to all members.

**message-send** -- Send a follow-up message in an existing AI chat. Returns message ID -- use message-read to get the AI response.

**message-list** -- List all messages in an AI chat.

**message-details** -- Get details for a specific message in an AI chat including response text and citations.

**message-read** -- Read an AI message response. Polls the message details endpoint until the AI response is complete, then returns the full text.

**search** -- Semantic search across indexed documents and code. Returns ranked document chunks with relevance scores -- faster and lighter than AI chat (stateless GET, no LLM inference). Requires Intelligence ON. Params: `query_text` (2-1,000 chars), optional `files_scope`, `folders_scope` (same format as chat scoping), `limit` (1-500, default 100), `offset`. Results include content snippets, scores, and source file details with `web_url` (workspace only). Use search to find relevant documents, then chat to ask questions about them.

**share-generate** -- Generate AI Share markdown with temporary download URLs for files that can be pasted into external AI chatbots.

**transactions** -- List AI token usage transactions for billing tracking.

**autotitle** -- Generate AI-powered title and description based on contents (share context only).

### comment

All comment endpoints use the path pattern `/comments/{entity_type}/{parent_id}/` or `/comments/{entity_type}/{parent_id}/{node_id}/` where `entity_type` is `workspace` or `share`, `parent_id` is the 19-digit profile ID, and `node_id` is the file's opaque ID.

**list** -- List comments on a specific file (node). Params: sort (`created`/`-created`), limit (2-200), offset, include_deleted, reference_type filter, include_total.

**list-all** -- List all comments across a workspace or share (not node-specific). Same listing params as list.

**add** -- Add a comment to a specific file. Body: text (max 8,192 chars total, max 2,048 chars display text with `@[...]` mention tags stripped). Supports mention tags: `@[profile:id]`, `@[user:opaqueId:Name]`, `@[file:fileId:name.ext]`. Optional parent_comment_id (single-level threading, replies to replies auto-flatten), optional reference (type, timestamp, page, region, text_snippet for content anchoring), optional linked_entity_type (`task` or `approval`) and linked_entity_id to link the comment to a workflow entity at creation time. Uses JSON body.

**delete** -- Delete a comment. Recursive: deleting a parent also removes all its replies.

**bulk-delete** -- Bulk soft-delete multiple comments (max 100). NOT recursive: replies to deleted comments are preserved.

**details** -- Get full details of a single comment by its ID. Response includes `linked_entity_type` and `linked_entity_id` (null when not linked).

**reaction-add** -- Add or change your emoji reaction. One reaction per user per comment; new replaces previous.

**reaction-remove** -- Remove your emoji reaction from a comment.

**link** -- Link an existing comment to a workflow entity. Params: comment_id, linked_entity_type (`task` or `approval`), linked_entity_id. One link per comment; linking replaces any existing link. Returns the updated comment with linked fields populated.

**unlink** -- Remove the workflow link from a comment. Params: comment_id. Returns the updated comment with linked fields set to null.

**linked** -- Reverse lookup: find all comments linked to a given workflow entity. Params: linked_entity_type (`task` or `approval`), linked_entity_id. Returns a list of comments linked to the specified entity.

### event

**search** -- Search the audit/event log with filters for profile, event type, category, subcategory, event name, and date range. See **Event Filtering Reference** in section 7 for the full taxonomy of categories, subcategories, and event names.

**summarize** -- Search events and return an AI-powered natural language summary of the activity. Accepts the same category/subcategory/event filters as search.

**details** -- Get full details for a single event by its ID.

**activity-list** -- Poll for recent activity events on a workspace or share.

**activity-poll** -- Long-poll for activity changes on a workspace or share. The server holds the connection until a change occurs or the wait period expires. Returns activity keys indicating what changed and a lastactivity timestamp for the next poll.

### member

All member actions require `entity_type` parameter (`workspace` or `share`) and `entity_id` (the 19-digit profile ID).

**add** -- Add an existing user by user ID, or invite by email. Pass the email address or user ID as `email_or_user_id`. For workspaces, set access level with `permissions` (admin/member/guest). For shares, use `role` (admin/member/guest/view).

**remove** -- Remove a member (cannot remove the owner).

**details** -- Get detailed membership info for a specific member. For workspaces, pass `member_id`; for shares, pass `user_id`.

**update** -- Update a member's role, notifications, or expiration.

**transfer-ownership** -- Transfer ownership to another member (current owner is demoted to admin).

**leave** -- Leave (remove yourself). Owner must transfer ownership first.

**join** -- Self-join based on organization membership.

**join-invitation** -- Accept or decline an invitation using an invitation key.

### invitation

All invitation actions require `entity_type` parameter (`workspace` or `share`) and `entity_id` (the 19-digit profile ID).

**list** -- List all pending invitations.

**list-by-state** -- List invitations filtered by state.

**update** -- Resend or update an invitation (by ID or invitee email).

**delete** -- Revoke and delete a pending invitation.

### asset

All asset actions require `entity_type` parameter (`org`, `workspace`, `share`, or `user`) and `entity_id` (the 19-digit profile ID for org/workspace/share).

**upload** -- Upload an asset (e.g. logo, banner, profile photo). Provide either plain-text content or base64-encoded data (not both).

**delete** -- Delete an asset.

**types** -- List available asset types for the entity.

**list** -- List all assets for the entity.

**read** -- Read/download an asset.

### task

Task list and task management for workspaces and shares. All task actions require workflow to be enabled on the target entity (`workspace` action `enable-workflow` or `share` action `enable-workflow`).

**list-lists** -- List all task lists for a workspace or share. Requires `profile_type` and `profile_id`. Supports `sort_by` (created, updated, name), `sort_dir`, `limit` (1-200), `offset`, and `format` ("md" for markdown).

**create-list** -- Create a new task list. Requires `profile_type`, `profile_id`, and `name` (1-255 chars). Optional `description` (max 2000 chars).

**list-details** -- Get details of a specific task list. Requires `list_id`. Supports `format`.

**update-list** -- Update a task list's name or description. Requires `list_id`. Optional `name`, `description`.

**delete-list** -- Soft-delete a task list and all its tasks. Requires `list_id`. Destructive.

**list-tasks** -- List tasks in a task list. Requires `list_id`. Supports `status` filter, `assignee` filter, `sort_by` (created, updated, name, priority, status), `sort_dir`, `limit` (1-200), `offset`, and `format`.

**create-task** -- Create a new task in a list. Requires `list_id` and `title` (1-500 chars). Optional `description` (max 5000 chars), `status` (pending, in_progress, complete, blocked), `priority` (0=none, 1=low, 2=medium, 3=high, 4=critical), `assignee_id` (profile ID), `dependencies` (array of task IDs), `node_id` (link to file/folder/note).

**task-details** -- Get full details of a specific task. Requires `list_id` and `task_id`. Supports `format`.

**update-task** -- Update a task's title, description, status, priority, assignee, dependencies, or node link. Requires `list_id` and `task_id`.

**delete-task** -- Soft-delete a task. Requires `list_id` and `task_id`. Destructive.

**change-status** -- Change a task's status. Requires `list_id`, `task_id`, and `status`.

**assign-task** -- Assign or unassign a task. Requires `list_id` and `task_id`. Pass `assignee_id` (profile ID) to assign, or null/omit to unassign.

**bulk-status** -- Change status on multiple tasks at once. Requires `list_id`, `task_ids` (array of task IDs, max 100), and `status`.

**move-task** -- Move a task from one list to another within the same profile. Requires `list_id` (source list), `task_id`, and `target_task_list_id` (destination list). Optional `sort_order` (position in target list, default 0). Source and target lists must belong to the same profile. Returns the updated task with `old_task_list_id` and `new_task_list_id`.

**reorder-tasks** -- Reorder tasks within a list. Requires `list_id` and `task_ids` (array of task IDs in the desired display order). The server converts this to `{order: [{id, sort_order}, ...]}` for the API.

**reorder-lists** -- Reorder task lists within a workspace or share. Requires `profile_type`, `profile_id`, and `list_ids` (array of task list IDs in the desired display order). The server converts this to `{order: [{id, sort_order}, ...]}` for the API.

### worklog

Activity log for tracking agent work. After uploads, task changes, share creation, or any significant action, log what you did and why — builds a searchable audit trail for humans and AI. All worklog actions require workflow to be enabled on the target entity.

**append** -- Append a new entry to the worklog. Requires `entity_type` ("task", "task_list", "node", or "profile"), `entity_id`, and `content` (1-10000 chars). Use after making changes to record what was done and why. Entries are immutable after creation.

**list** -- List worklog entries. Requires `entity_type` ("task", "task_list", "node", or "profile") and `entity_id` (the corresponding entity's opaque ID, or profile 19-digit ID for entity_type "profile"). Supports `type` filter ("entry" or "interjection"), `sort_dir` ("asc" or "desc", default "desc"), `limit` (1-200), `offset`, and `format` ("md" for markdown).

**interject** -- Create an urgent interjection entry that requires acknowledgement. Requires `entity_type` ("task", "task_list", "node", or "profile"), `entity_id`, and `content` (1-10000 chars). Interjections are priority corrections -- always treated as urgent.

**details** -- Get full details of a specific worklog entry. Requires `entry_id`. Supports `format`.

**acknowledge** -- Acknowledge an interjection entry, marking it as seen. Requires `entry_id`. Only entries with `acknowledgable: true` can be acknowledged.

**unacknowledged** -- List unacknowledged interjections (entries where `acknowledgable` is `true`). Requires `entity_type` ("task", "task_list", "node", or "profile") and `entity_id`. Supports `limit`, `offset`, and `format`. Always check for unacknowledged interjections before proceeding with work.

### approval

Formal approval requests scoped to tasks, storage nodes, or worklog entries. All approval actions require workflow to be enabled on the target entity.

**list** -- List approval requests for a workspace or share. Requires `profile_type` and `profile_id`. Supports `status` filter (pending, approved, rejected), `limit` (1-200, default 100), `offset`, and `format`.

**create** -- Create a new approval request. Requires `entity_type` ("task", "node", or "worklog_entry"), `entity_id`, `profile_id`, and `description` (1-5000 chars). Optional `approver_id` (profile ID of designated approver), `deadline` (ISO 8601), `node_id` (artifact reference).

**details** -- Get full details of an approval request including approver list and resolution. Requires `approval_id` (opaque alphanumeric). Supports `format`.

**resolve** -- Resolve an approval request. Requires `approval_id` and `resolve_action` ("approve" or "reject"). Optional `comment` (max 5000 chars). Only designated approvers can resolve.

### todo

Simple flat checklists scoped to workspaces and shares. No nesting. All todo actions require workflow to be enabled on the target entity.

**list** -- List todos for a workspace or share. Requires `profile_type` and `profile_id`. Supports `filter_done` (boolean), `sort_by` (created, updated, title), `sort_dir`, `limit` (1-200, default 50), `offset`, and `format`.

**create** -- Create a new todo item. Requires `profile_type`, `profile_id`, and `title` (1-500 chars). Optional `assignee_id`.

**details** -- Get full details of a todo. Requires `todo_id` (opaque alphanumeric). Supports `format`.

**update** -- Update a todo. Requires `todo_id`. Supports `title`, `assignee_id`, `done`.

**delete** -- Soft-delete a todo. Requires `todo_id`. Destructive.

**toggle** -- Toggle the done state of a todo. Requires `todo_id`. Flips between done and not done.

**bulk-toggle** -- Set done state on multiple todos at once. Requires `profile_type`, `profile_id`, `todo_ids` (array of todo IDs, max 100), and `done` (boolean: true to mark done, false to mark not done).

### apps

Interactive MCP App widget discovery and launching. Widgets are interactive HTML5 UIs that render in agent conversations.

**list** -- List all available MCP App widgets with their metadata (title, description, supported tools, supported actions, resource URI).

**details** -- Get full metadata for a specific widget. Requires `app_id` (the widget name, e.g., "file-picker").

**launch** -- Launch a widget with workspace or share context. Requires `app_id`, `context_type` ("workspace" or "share"), and `context_id` (the 19-digit profile ID). Returns the widget HTML content ready for rendering.

**get-tool-apps** -- Find widgets associated with a specific tool domain. Requires `tool_name` (e.g., "storage", "ai", "comment"). Returns widgets that provide UI for that tool's operations.

---

## 10. Code Mode (Headless Agents)

When connecting from a headless agent (Claude Code, Cursor, Continue, etc.), the server automatically enables Code Mode -- a lightweight alternative to the full 19-tool set. Code Mode exposes 4 tools total:

| Tool | Purpose |
|------|---------|
| `auth` | Authentication (signin, signup, API keys, PKCE, 2FA) |
| `upload` | File uploads (chunked, text, web-import) |
| `search` | Discover API endpoints by keyword, tag, or concept |
| `execute` | Run JavaScript against the Fast.io API |

Clients with MCP Apps support (Claude Desktop, Cline) continue to receive the full 19-tool set plus 12 app-* widget tools. Unknown clients default to the full tool set.

### search Tool

Query the API spec by keywords, paths, or concepts. Returns matching endpoints with method, path, parameters, and descriptions.

```
search query="list files in workspace" tag="storage"
search query="create share" tag="share"
search query="authentication"
search query="pagination" include_concepts=true
```

Parameters:
- `query` (string, required) -- Keywords, endpoint paths, or concepts to search for
- `tag` (string, optional) -- Filter by domain: auth, workspace, storage, ai, share, upload, org, user, member, comment, event, metadata, etc.
- `include_concepts` (boolean, optional) -- Include concept docs (pagination, IDs, errors). Default true.

### execute Tool

Write JavaScript code that uses the `fastio` object for authenticated API calls:

- `fastio.get(path, params?)` -- GET request with optional query parameters
- `fastio.post(path, body?, params?)` -- POST with form-encoded body (default API format)
- `fastio.postJson(path, body?, params?)` -- POST with JSON body
- `fastio.delete(path, params?)` -- DELETE request
- `fastio.put(path, body?, params?)` -- PUT with form-encoded body

The auth token is injected automatically. Path parameters must be filled by the caller (replace `{workspace_id}` with the actual ID). Return a value to include it in the response. `console.log()` output is captured and returned.

```javascript
// Example: List workspaces in an org
return await fastio.get('/org/1234567890123456789/list/workspaces/');
```

```javascript
// Example: Create a folder and upload a note
const folder = await fastio.post('/workspace/1234567890123456789/storage/root/createfolder/', {
  name: 'reports'
});
const folderId = folder.node.opaque_id;
const note = await fastio.post(`/workspace/1234567890123456789/storage/${folderId}/createnote/`, {
  name: 'summary.md',
  content: '# Summary\n\nKey findings from the analysis.'
});
return { folder: folder.node, note: note.node };
```

Parameters:
- `code` (string, required) -- JavaScript code (async function body). Use `return` to include a value in the response.
- `timeout_ms` (number, optional) -- Timeout in ms (default 30000, max 60000)

