# Fast.io for AI Agents

> **Version:** 1.25.0 | **Last updated:** 2026-02-21
>
> This guide is available at the `/current/agents/` endpoint on the connected API server.

**Workspaces for Agentic Teams. Collaborate, share, and query with AI — all through one API, free.**

Fast.io provides workspaces for agentic teams — where agents collaborate with other agents and with humans. Upload
outputs, create branded data rooms, ask questions about documents using built-in AI, and hand everything off to a human
when the job is done. No infrastructure to manage, no subscriptions to set up, no credit card required.

**MCP-enabled agents** should connect via the Model Context Protocol for the simplest integration — no raw HTTP calls
needed.

**Connection endpoints:**
- **Streamable HTTP (recommended):** `https://mcp.fast.io/mcp`
- **Legacy SSE:** `https://mcp.fast.io/sse`

The MCP server exposes **19 consolidated tools** using action-based routing — each tool covers a domain (e.g., `auth`,
`storage`, `upload`) and uses an `action` parameter to select the operation. See the "MCP Tool Architecture" section
below for the full tool list.

MCP-connected agents receive comprehensive workflow guidance through SERVER_INSTRUCTIONS at connection time, and can
read resources (`resources/read`) including `skill://guide` for full tool documentation, `session://status` for current
authentication state, and `download://` resource templates for direct file content retrieval.

This guide covers platform concepts and capabilities; the MCP server provides tool-level details through its standard
protocol interface. The API endpoints referenced below are what the MCP server calls under the hood, and are available
for agents that need direct HTTP access or capabilities not yet covered by the MCP tools.

---

## Why Agents Use Fast.io

### The Problem

Agentic teams — groups of agents working together and with humans — need a shared place to work. Today, agents cobble
together S3 buckets, presigned URLs, email attachments, and custom download pages. Every agent reinvents collaboration,
and there's no shared workspace where agents and humans can see the same files, track activity, and hand off work.

Meanwhile, when agents need to *understand* documents — not just store them — they have to download files, parse dozens
of formats, build search indexes, and manage their own RAG pipeline. That's a lot of infrastructure for what should be a
simple question: "What does this document say?"

### What Fast.io Solves

| Problem                                      | Fast.io Solution                                                                                  |
|----------------------------------------------|---------------------------------------------------------------------------------------------------|
| No shared workspace for agentic teams        | Workspaces where agents and humans collaborate with file preview, versioning, and AI              |
| Agent-to-agent coordination lacks structure  | Shared workspaces with activity feeds, comments, and real-time sync across team members           |
| Sharing outputs with humans is awkward       | Purpose-built shares (Send, Receive, Exchange) with link sharing, passwords, expiration           |
| Collecting files from humans is harder       | Receive shares let humans upload directly to your workspace — no email attachments                |
| Understanding document contents              | Built-in AI reads, summarizes, and answers questions about your documents and code                |
| Building a RAG pipeline from scratch         | Enable intelligence on a workspace and documents are automatically indexed, summarized, and queryable |
| Finding the right file in a large collection | Semantic search finds documents by meaning, not just filename                                     |
| Handing a project off to a human             | One-click ownership transfer — human gets the org, agent keeps admin access                       |
| Tracking what happened                       | Full audit trail with AI-powered activity summaries                                               |
| Cost                                         | Free. 50 GB storage, 5,000 monthly credits, no credit card                                        |

---

## Getting Started — Choosing the Right Account Type

There are two ways to use Fast.io as an agent, depending on whether you're operating autonomously or assisting an
existing human user.

### Option 1: Autonomous Agent — Create an Agent Account

If you're operating as part of an agentic team (collaborating with other agents, sharing outputs with humans, running
workflows), create your own agent account:

1. `POST /current/user/` with `email_address`, `password`, `tos_agree=true`, `agent=true`
2. Authenticate with Basic Auth → get JWT
3. Verify your email address (required before using most endpoints):
   - `POST /current/user/email/validate/` with `email` — sends a verification code to your email
   - `POST /current/user/email/validate/` with `email` and `email_token` — validates the code and marks your account as verified
4. `POST /current/org/create/` with `domain` (required, 2-80 chars lowercase alphanumeric + hyphens) — an org is a collector of workspaces that can represent a company, team, business unit, or personal collection
5. `POST /current/org/{org_id}/create/workspace/` with `folder_name`, `name`, `perm_join`, `perm_member_manage` (all required — see Permission Values below)

Agent accounts get the free agent plan (50 GB, 5,000 monthly credits) and can transfer orgs to humans when ready. This
is the recommended path for autonomous agents.

#### Permission Values

Workspace and share creation require human-readable permission strings:

**Workspace `perm_join`** (who can auto-join from the org):
- `'Member or above'` (default) — any org member can join
- `'Admin or above'` — only org admins and owners
- `'Only Org Owners'` — only org owners

**Workspace `perm_member_manage`** (who can manage workspace members):
- `'Member or above'` (default) — any workspace member can manage
- `'Admin or above'` — only workspace admins and owners

**Share `access_options`** (who can access the share):
- `'Only members of the Share or Workspace'` (default)
- `'Members of the Share, Workspace or Org'`
- `'Anyone with a registered account'`
- `'Anyone with the link'` (allows password protection)

### Option 2: Assisting a Human — Use Their API Key

If a human already has a Fast.io account and wants your help managing their files, workspaces, or shares, they can
create an API key for you to use. No separate agent account is needed — you operate as the human user.

**How the human creates an API key:**

Go to **Settings → Devices & Agents → API Keys** and click **Create API Key**. Optionally enter a memo to label the
key (e.g., "CI pipeline" or "Agent access"), then click **Create**. Copy the key immediately — it is only displayed
once and cannot be retrieved later. Direct link: `https://go.fast.io/settings/api-keys`

Use the API key as a Bearer token: `Authorization: Bearer {api_key}`

The API key has the same permissions as the human user, so you can manage their workspaces, shares, and files directly.

### Option 3: Agent Account Invited to a Human's Org

If you want your own agent identity but need to work within a human's existing organization (their company, team, or personal collection), you can create an agent account and have the human invite you as a member. This gives you access to their workspaces and shares while keeping your own account separate.

**How the human invites the agent to their org:**

Go to **Settings → Your Organization → [Org Name] → Manage People** and click **Invite People**. Enter the agent's
email address, choose a permission level (Member or Admin), and click **Send Invites**. The agent account will receive
the invitation and can accept it via `POST /current/user/invitations/acceptall/`.

**How the human invites the agent to a workspace:**

Open the workspace, click the member avatars in the toolbar, then click **Manage Members**. Enter the agent's email
address, choose a permission level, and optionally check **Invite to org** to add them to the organization at the same
time. Click **Send Invites** — if the agent isn't already an org member and the toggle is off, they'll need an org
invite separately.

Alternatively, the human can invite the agent programmatically:
- **Org:** `POST /current/org/{org_id}/members/{agent_email}/` with `permission` level
- **Workspace:** `POST /current/workspace/{workspace_id}/members/{agent_email}/` with `permission` level

### Option 4: PKCE Browser Login — Secure Authentication Without Sharing Passwords

For the most secure authentication flow — especially when a human wants to authorize an agent without sharing their
password — use the PKCE (Proof Key for Code Exchange) browser login. No credentials pass through the agent at any point.

The `client_id` can be a pre-registered ID, a dynamically registered ID (via DCR), or an **HTTPS URL pointing to a
Client ID Metadata Document (CIMD)**. CIMD is the MCP specification's preferred registration method — the server
fetches client metadata from the URL on-the-fly, so no pre-registration is needed.

1. Agent calls `POST /current/oauth/authorize/` with PKCE parameters (`code_challenge`, `code_challenge_method=S256`,
   `client_id`, `redirect_uri`, `response_type=code`) — gets back an authorization URL
2. The user opens the URL in their browser, signs in (supports SSO), and approves access
3. The browser displays an authorization code that the user copies back to the agent
4. Agent calls `POST /current/oauth/token/` with `grant_type=authorization_code`, the authorization `code`, and the
   PKCE `code_verifier` — receives an access token and refresh token
5. The agent is now authenticated. Access tokens last **1 hour**, refresh tokens last **30 days**. Use
   `POST /current/oauth/token/` with `grant_type=refresh_token` to get new access tokens without repeating the flow.

This is the recommended approach when:
- A human wants to grant agent access without sharing their password
- The organization uses SSO and password-based auth isn't available
- You need the strongest security guarantees (no credentials stored by the agent)

### Recommendations

| Scenario | Recommended Approach |
|----------|---------------------|
| Operating autonomously, storing files, building for users | Create an agent account with your own org (your personal collection of workspaces) |
| Helping a human manage their existing account | Ask the human to create an API key for you |
| Working within a human's org with your own identity | Create an agent account, have the human invite you |
| Building something to hand off to a human | Create an agent account, build it, then transfer the org |
| Human wants to authorize an agent without sharing credentials | Use PKCE browser login (Option 4) |

### Authentication & Token Lifecycle

All API requests require `Authorization: Bearer {token}` in the header. How you get that token depends on your access
pattern:

**JWT tokens (agent accounts):** Authenticate with `GET /current/user/auth/` using HTTP Basic Auth (email:password). The
response includes an `auth_token` (JWT). OAuth access tokens last **1 hour** and refresh tokens last **30 days**. When
your token expires, re-authenticate to get a new one. If the account has 2FA enabled, the initial token has limited
scope until 2FA verification is completed via `/current/user/auth/2factor/auth/{token}/`.

**API keys (human accounts):** API keys are long-lived and do not expire unless the human revokes them. No refresh flow
needed.

**Verify your token:** Call `GET /current/user/auth/check/` at any time to validate your current token and get the
authenticated user's ID. This is useful at startup to confirm your credentials are valid before beginning work, or to
detect an expired token without waiting for a 401 error on a real request.

### OAuth Scopes — Controlling Access

When using PKCE browser login, you can request scoped access tokens that limit what the agent can do. Scopes follow
an inheritance model — broader scopes automatically include access to their children.

**Scope types:**

| Scope Type       | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| `all_orgs`       | Access to all organizations the user owns or is a member of                 |
| `all_workspaces` | Access to all workspaces across accessible organizations                    |
| `all_shares`     | Access to all shares across accessible organizations and workspaces         |

**Inheritance:** `all_orgs` includes `all_workspaces`, which includes `all_shares`. Requesting `all_orgs` grants full
access to all orgs, workspaces, and shares the user has access to.

Pass the desired `scope_type` when initiating the PKCE authorization flow (`POST /current/oauth/authorize/`). If
omitted, the token defaults to full access (equivalent to `all_orgs`).

### Organizations — Collectors of Workspaces

An organization (org) is a collector of workspaces. It can represent a company, a business unit, a team, or simply your own personal collection. Every workspace and share lives under an org, and orgs are the billable entity — storage, credits, and member limits are tracked at the org level.

### Internal vs External Orgs

When working with Fast.io, an agent may interact with orgs in two different ways:

**Internal orgs** — orgs you created or were invited to join as a member. You have org-level access: you can see all
workspaces (subject to permissions), manage settings if you're an admin, and appear in the org's member list. Your own
orgs always show `member: true` in API responses.

**External orgs** — orgs you can access only through workspace membership. If a human invites you to their workspace
but does not invite you to their org, the org appears as external. You can see the org's name and basic public info, but
you cannot manage org settings, see other workspaces, or add members at the org level. External orgs show
`member: false` in API responses.

This distinction matters because an agent invited to a single workspace cannot assume it has access to the rest of that
org. It can only work within the workspaces it was explicitly invited to.

**Full org discovery requires both endpoints:**

- `GET /current/orgs/list/` — returns orgs you are a member of (`member: true`)
- `GET /current/orgs/list/external/` — returns orgs you access via workspace membership only (`member: false`)

**Always call both.** An agent that only calls `/orgs/list/` will miss every org where it was invited to a workspace but
not to the org itself — which is the most common pattern when a human adds an agent to help with a specific project. If
you skip `/orgs/list/external/`, you won't discover those workspaces at all.

**Example:** A human invites your agent to their "Q4 Reports" workspace. You can upload files, run AI queries, and
collaborate in that workspace. But you cannot create new workspaces in their org, view their billing, or access their
other workspaces. The org shows up in `/orgs/list/external/` — not `/orgs/list/`.

If the human later invites you to the org itself (via org member invitation), the org moves from external to internal and
you gain org-level access based on your permission level.

### Pagination

All list endpoints support offset-based pagination via query parameters. Use pagination to keep responses within token
limits and iterate through large collections.

**Query parameters:**

| Parameter | Type | Default | Max | Description                |
|-----------|------|---------|-----|----------------------------|
| `limit`   | int  | 100     | 500 | Number of items to return  |
| `offset`  | int  | 0       | —   | Number of items to skip    |

**Response metadata:** Every paginated response includes a `pagination` object:

```json
{
  "pagination": {
    "total": 42,
    "limit": 100,
    "offset": 0,
    "has_more": false
  }
}
```

**Paginating through results:**

```
# First page
GET /current/orgs/list/?limit=10&offset=0
# → pagination.has_more = true, pagination.total = 42

# Second page
GET /current/orgs/list/?limit=10&offset=10
# → pagination.has_more = true

# Continue until has_more = false
```

**Endpoints supporting pagination:**

| Endpoint                                             | Collection Key     |
|------------------------------------------------------|--------------------|
| `GET /current/orgs/all/`                             | `orgs`             |
| `GET /current/orgs/list/`                            | `orgs`             |
| `GET /current/orgs/list/external/`                   | `orgs`             |
| `GET /current/shares/all/`                           | `shares`           |
| `GET /current/workspace/{id}/members/list/`          | `users`            |
| `GET /current/org/{id}/billing/usage/members/list/`  | `billable_members` |
| `GET /current/workspace/{id}/list/shares/`           | `shares`           |
| `GET /current/user/me/list/shares/`                  | `shares`           |
| `GET /current/org/{id}/list/workspaces/`             | `workspaces`       |
| `GET /current/org/{id}/members/list/`                | `users`            |
| `GET /current/workspace/{id}/storage/search/`        | `files`            |
| `GET /current/share/{id}/storage/search/`            | `files`            |
| `GET /current/share/{id}/members/list/`              | `users`            |

---

## Core Capabilities

### 1. Workspaces — Shared Spaces for Agentic Teams

Workspaces are where agentic teams do their work. Each workspace has its own storage, member list, AI chat, and
activity feed — a shared environment where agents collaborate with other agents and with humans.

- **50 GB included storage** on the free agent plan
- **Files up to 1 GB** per upload
- **File versioning** — every edit creates a new version, old versions are recoverable
- **Folder hierarchy** — organize files however you want
- **Full-text and semantic search** — find files by name or content, and documents by meaning
- **Member roles** — Owner, Admin, Editor, Viewer with granular permissions
- **Real-time sync** — changes appear instantly for all members via WebSockets

#### Intelligence: On or Off

Workspaces have an **intelligence** toggle that controls whether AI features are active. This is a critical decision:

**Intelligence OFF** — the workspace stores files without AI indexing. You can still attach files directly to an AI chat
conversation (up to 20 files), but files are not persistently indexed. This is fine for coordination workflows where
you don't need to query your content.

**Intelligence ON** — the workspace becomes an AI-powered knowledge base. Every document and code file uploaded is automatically ingested,
summarized, and indexed for RAG. This enables:

- **RAG (retrieval-augmented generation)** — scope AI chat to entire folders or the full workspace and ask questions
  across your indexed documents and code. The AI retrieves relevant passages and answers with citations.
- **Semantic search** — find files by meaning, not just keywords. "Show me contracts with indemnity clauses" works even
  if those exact words don't appear in the filename.
- **Auto-summarization** — short and long summaries generated for every indexed document and code file, searchable and visible in the UI.
- **Metadata extraction** — AI pulls structured metadata from documents, code, and images automatically using templates.
  Assign a template to a workspace, and every document uploaded is automatically extracted against that schema during
  ingestion. You can also trigger extraction manually or in batch. See section 14 (Metadata) for the full API.

> **Coming soon:** RAG indexing support for images, video, and audio files. Currently only documents and code are indexed.

Intelligence is enabled by default when creating workspaces via the API for agent accounts. If your team only needs a
shared workspace for coordination, you can disable it to conserve credits. If you want to query your content — enable it.

**Agent use case:** Create a workspace per project or client. Enable intelligence if agents or humans need to query the
content. Upload reports, datasets, and deliverables. Invite other agents and human stakeholders. Everything is organized,
searchable, and versioned — and the whole team can see it.

### 2. Shares — Structured Agent-Human Exchange

Shares are purpose-built spaces for exchanging files between your agentic team and external humans. Three modes cover
every exchange pattern:

| Mode         | What It Does                  | Agent Use Case                                |
|--------------|-------------------------------|-----------------------------------------------|
| **Send**     | Recipients can download files | Deliver reports, exports, generated content   |
| **Receive**  | Recipients can upload files   | Collect documents, datasets, user submissions |
| **Exchange** | Both upload and download      | Collaborative workflows, review cycles        |

#### Share Features

- **Password protection** — require a password for link access
- **Expiration dates** — shares auto-expire after a set period
- **Download controls** — enable or disable file downloads
- **Access levels** — `'Only members of the Share or Workspace'`, `'Members of the Share, Workspace or Org'`, `'Anyone with a registered account'`, or `'Anyone with the link'`
- **Custom branding** — background images, gradient colors, accent colors, logos
- **Post-download messaging** — show custom messages and links after download
- **Up to 3 custom links** per share for context or calls-to-action
- **Guest chat** — let share recipients ask questions in real-time
- **AI-powered auto-titling** — shares automatically generate smart titles from their contents
- **Activity notifications** — get notified when files are sent or received
- **Comment controls** — configure who can see and post comments (owners, guests, or both)

#### Two Storage Modes

When creating a share, you choose a `storage_mode` that determines how the share's files are managed:

- **`room`** (independent storage, default) — the share has its own isolated storage. Files are added directly to the
  share and are independent of any workspace. This creates a self-contained data room — changes to workspace files don't
  affect the room, and vice versa. Perfect for final deliverables, compliance packages, archived reports, or any
  scenario where you want an immutable snapshot.

- **`shared_folder`** (workspace-backed) — the share is backed by a specific folder in a workspace. The share displays
  the live contents of that folder — any files added, updated, or removed in the workspace folder are immediately
  reflected in the share. No file duplication, so no extra storage cost. To create a shared folder, pass
  `storage_mode=shared_folder` and `folder_node_id={folder_opaque_id}` when creating the share. Note: expiration dates
  are not allowed on shared folder shares since the content is live.

Both modes look the same to share recipients — a branded data room with file preview, download controls, and all share
features. The difference is whether the content is a snapshot (room) or a live view (shared folder).

**Agent use case:** Generate a quarterly report, create a Send share with your client's branding, set a 30-day
expiration, and share the link. The client sees a branded page with instant file preview — not a raw download link.

### 3. QuickShare — Instant File Handoff

Need to toss a file to someone right now? QuickShare creates a share from a single file with zero configuration.
Automatic 30-day expiration. No setup, no decisions.

**Agent use case:** Debug log, sample output, or quick artifact? QuickShare it and send the link. Done.

### 4. Built-In AI — Ask Questions About Your Files

Fast.io's AI is a **read-only tool** — it can read and analyze file contents, but it cannot modify files, change
workspace settings, manage members, or read events. It answers questions about your documents, nothing more. For any
action beyond reading file content, your agent must use the API or MCP server directly.

Fast.io's AI lets agents query documents through two chat types, with or without persistent indexing. Both types
augment file knowledge with information from the web when relevant.

#### Chat Types

**`chat`** — Basic AI conversation. Does not use file context from the workspace index. Use this for general questions
or when you don't need to reference stored files.

**`chat_with_files`** — AI conversation grounded in your files. This is the type you use when you want the AI to read,
analyze, and cite your documents. Requires the workspace to have **intelligence enabled** if using folder/file scope
(RAG). Supports two mutually exclusive modes for providing file context:

1. **Folder/file scope** (RAG) — limits the search space for retrieval. The AI searches the indexed content of files
   within the specified scope, retrieves relevant passages, and answers with citations. Requires intelligence enabled
   and files in `ready` AI state.

2. **File attachments** — files are directly attached to the conversation. The AI reads the full content of the attached
   files. Does not require intelligence — any file with a ready preview can be attached. Max 20 files, 200MB total.

These two modes cannot be combined in a single chat — use scope OR attachments, not both.

**Auto-promotion:** If you create a chat with `type=chat` but include `files_scope`, `folders_scope`, or `files_attach`,
the system automatically promotes the type to `chat_with_files`. You don't need to worry about setting the type exactly
right — the intent is unambiguous when file parameters are present.

#### Intelligence Setting — When to Enable It

The `intelligence` toggle on a workspace controls whether uploaded documents and code files are automatically ingested, summarized, and
indexed for RAG.

**Enable intelligence when:**
- You have many files and need to search across them to answer questions
- You want scoped RAG queries against folders or the entire workspace
- You need auto-summarization and metadata extraction
- You're building a persistent knowledge base

**Disable intelligence when:**
- You're using the workspace purely for team coordination and file exchange
- You only need to analyze specific files (use file attachments instead)
- You want to conserve credits (ingestion costs 10 credits/page)

Even with intelligence disabled, you can still use `chat_with_files` with **file attachments** — any file that has a
ready preview can be attached directly to a chat for one-off analysis.

#### AI State — File Readiness for RAG

Every document and code file in an intelligent workspace has an `ai_state` field that tracks its ingestion progress:

| State         | Meaning                                           |
|---------------|---------------------------------------------------|
| `disabled`    | AI processing disabled for this file              |
| `pending`     | Queued for processing                             |
| `in_progress` | Currently being ingested and indexed              |
| `ready`       | Processing complete — file is available for RAG   |
| `failed`      | Processing failed                                 |

**Only documents and code files with `ai_state: ready` are included in folder/file scope searches.** If you upload files and immediately
create a scoped chat, recently uploaded files may not yet be indexed. Use the activity polling endpoint to wait for
`ai_state` changes before querying.

#### Folder Scope vs File Attachments

| Feature              | Folder/File Scope (RAG)                    | File Attachments                         |
|----------------------|--------------------------------------------|------------------------------------------|
| How it works         | Limits RAG search space                    | Files read directly by AI                |
| Requires intelligence| Yes                                        | No                                       |
| Requires `ai_state`  | Files must be `ready`                      | Files must have a ready preview          |
| Best for             | Many files, knowledge retrieval            | Specific files, direct analysis          |
| Max references       | 100 folder refs (subfolder tree expansion) | 20 files, 200MB total                    |
| Default behavior     | No scope = entire workspace                | N/A                                      |

**Folder scope parameters:**
- `folders_scope` — comma-separated `nodeId:depth` pairs (depth 1-10, max 100 subfolder refs). The depth controls how
  many levels of subfolders are expanded — only subfolder references count toward the 100 limit, not individual files
  within those folders. The RAG backend automatically searches all indexed documents inside the scoped folders.
- `files_scope` — comma-separated `nodeId:versionId` pairs (max 100 refs). nodeId is required; versionId is required
  in the pair format but will be **auto-resolved to the node's current version** if left empty (e.g., `nodeId:` with
  nothing after the colon). Get the versionId from the file's `version` field in storage list/details responses.
  Limits RAG retrieval to specific file versions.
- **Default scope is the entire workspace** — if you omit both `files_scope` and `folders_scope`, the AI searches
  all indexed documents. This is the recommended approach when you want to query across everything. Only provide scope
  parameters when you need to narrow the search to specific files or folders.

**Important — how folder scope works internally:**
Folder scope defines a search boundary, not a file list. When you pass `folders_scope`, the system expands the specified
folders into a set of subfolder references up to the given depth. The RAG backend then searches all indexed documents within
those folders automatically. You do **not** need to enumerate or list individual files — just provide the top-level
folder ID and the desired depth. A folder containing thousands of files with only a few subfolders will work fine,
because only the subfolder references (not file references) count toward the 100 limit. If you need to query the
entire workspace, omit `folders_scope` entirely — the default scope is already the full workspace.

**File attachment parameter:**
- `files_attach` — comma-separated `nodeId:versionId` pairs (max 20 files, 200MB total). nodeId is required;
  versionId will be **auto-resolved to the current version** if left empty. **Only file nodes are accepted — passing
  a folder nodeId will be rejected.** Files are read directly, not searched via RAG. To include folder contents, use
  `folders_scope` instead.

#### Notes as Knowledge Grounding

Notes are markdown documents created directly in workspace storage via the API
(`POST /current/workspace/{id}/storage/{folder}/createnote/`). In an intelligent workspace, notes are ingested and
indexed just like uploaded files. This makes notes a way to store long-term knowledge that becomes grounding material
for future AI queries.

**Agent use case:** Store project context, decision logs, or reference material as notes. When you later ask the AI
"What was the rationale for choosing vendor X?", the note containing that decision is retrieved and cited — even months
later.

Notes within a folder scope are included in RAG queries when intelligence is enabled.

#### How to Write Effective Questions

The way you phrase questions depends on whether you're using folder scope (RAG) or file attachments.

**With folder/file scope (RAG):**

Write questions that are likely to match content in your indexed files. The AI searches the scope for relevant passages,
retrieves them, and uses them as citations to answer your question. Think of it as a search query that returns context
for an answer.

- Good: "What are the payment terms in the vendor contracts?" — matches specific content in files
- Good: "Summarize the key findings from the Q3 analysis reports" — retrieves relevant sections
- Good: "What risks were identified in the security audit?" — finds specific content to cite
- Bad: "Tell me about these files" — too vague for retrieval, no specific content to match
- Bad: "What's in this workspace?" — the AI can't meaningfully search for "everything"

If no folder scope is specified, the search defaults to all indexed documents in the workspace. For large workspaces, narrowing the
scope to specific folders improves relevance and reduces token usage.

**With file attachments:**

You can be more direct and simplistic since the AI reads the full file content. No retrieval step — the AI has the
complete file in context.

- "Describe this image in detail"
- "Extract all dates and amounts from this invoice"
- "Convert this CSV data into a summary table"
- "What programming language is this code written in and what does it do?"

**Personality:** The `personality` parameter controls the tone and length of AI responses. Pass it when creating a chat
or sending a message:

- `concise` — short, direct answers with minimal explanation
- `detailed` — comprehensive answers with context and evidence (default)

This makes a significant difference in response quality for your use case. Agents that need to extract data or get quick
answers should use `concise` to avoid wasting tokens on lengthy explanations. Use `detailed` when you need thorough
analysis with supporting evidence.

You can also control verbosity in the question itself — for example, "In one sentence, summarize this report" or "List
only the file names, no explanations." Combining `concise` personality with direct questions produces the shortest
responses.

#### Waiting for AI Responses

After sending a message, the AI processes it asynchronously. You need to wait for the response to be ready.

**Message states:**

| State             | Meaning                              |
|-------------------|--------------------------------------|
| `ready`           | Queued for processing                |
| `in_progress`     | AI is generating the response        |
| `complete`        | Response finished                    |
| `errored`         | Processing failed                    |
| `post_processing` | Finalizing (citations, formatting)   |

**Option 1: SSE streaming (recommended for real-time display)**

`GET /current/workspace/{id}/ai/chat/{chat_id}/message/{message_id}/read/`

Returns a `text/event-stream` with response chunks as they're generated. The stream ends with a `done` event when the
response is complete. Response chunks include the AI's text, citations pointing to specific files/pages/snippets, and
any structured data (tables, analysis).

**Option 2: Activity polling (recommended for background processing)**

Don't poll the message endpoint in a loop. Instead, use the activity long-poll:

`GET /current/activity/poll/{workspace_id}?wait=95&lastactivity={timestamp}`

When `ai_chat:{chatId}` appears in the activity response, the chat has been updated — fetch the message details to get
the completed response. This is the most efficient approach when you don't need to stream the response in real-time.

**Option 3: Fetch completed response**

`GET /current/workspace/{id}/ai/chat/{chat_id}/message/{message_id}/details/`

Check the `state` field. If `complete`, the `response.text` contains the full answer and `response.citations` contains
the file references.

#### Linking Users to AI Chats

To send a user directly to an AI chat in the workspace UI, append a `chat` query parameter to the workspace storage
URL:

`https://{org.domain}.fast.io/workspace/{workspace.folder_name}/storage/root?chat={chat_opaque_id}`

This opens the workspace with the specified chat visible in the AI panel.

#### Supported Content Types

**Indexed for RAG** (requires Intelligence ON):
- Documents (PDF, Word, text, markdown)
- Code files (all common languages)

**File attachments only** (no RAG indexing):
- Spreadsheets (Excel, CSV)
- Images (all common formats) — *RAG indexing coming soon*
- Video (all common formats) — *RAG indexing coming soon*
- Audio (all common formats) — *RAG indexing coming soon*

#### AI Share — Export to External AI Tools

Generate temporary download URLs for your files, formatted as markdown, for pasting into external AI assistants like
ChatGPT or Claude. Up to 25 files, 50MB per file, 100MB total. Links expire after 5 minutes. This is separate from the
built-in AI chat — use it when you want to analyze files with a different model or tool.

**Agent use case:** A user asks "What were Q3 margins?" You have 50 financial documents in an intelligent workspace.
Instead of downloading and parsing all 50, create a `chat_with_files` scoped to the finance folder and ask. The AI
searches the indexed content, retrieves relevant passages, and answers with citations. Pass the cited answer — with
source references — back to the user.

### 5. File Preview — No Download Required

Files uploaded to Fast.io get automatic preview generation. When humans open a share or workspace, they see the content
immediately — no "download and open in another app" friction.

**Supported preview formats:**

- **Images** — full-resolution with auto-rotation and zoom
- **Video** — HLS adaptive streaming (50-60% faster load than raw video)
- **Audio** — interactive waveform visualization
- **PDF** — page navigation, zoom, text selection
- **Spreadsheets** — grid navigation with multi-sheet support
- **Code & text** — syntax highlighting, markdown rendering

**Agent use case:** Your generated PDF report doesn't just appear as a download link. The human sees it rendered inline,
can flip through pages, zoom in, and comment on specific sections — all without leaving the browser.

### 6. Notes — Markdown Documents as Knowledge

Notes are a storage node type (alongside files and folders) that store markdown content directly on the server. They
live in the same folder hierarchy as files, are versioned like any other node, and appear in storage listings with
`type: "note"`.

#### Creating and Updating Notes

**Create:** `POST /current/workspace/{id}/storage/{parent_id}/createnote/`

- `name` (required) — filename, must end in `.md`, max 100 characters (e.g., `"project-context.md"`)
- `content` (required) — markdown text, max 100 KB. Must be valid UTF-8 (UTF8MB4). Control characters (`\p{C}` except `\t`, `\n`, `\r`) are stripped.

**Update:** `POST /current/workspace/{id}/storage/{node_id}/updatenote/`

- `name` (optional) — rename the note (must end in `.md`)
- `content` (optional) — replace the markdown content (max 100 KB). Must be valid UTF-8 (UTF8MB4). Control characters (`\p{C}` except `\t`, `\n`, `\r`) are stripped.
- At least one of `name` or `content` must be provided

Notes can also be moved, copied, deleted, and restored using the same storage endpoints as files and folders.

#### Notes as Long-Term Knowledge Grounding

In an intelligent workspace, notes are automatically ingested and indexed just like uploaded documents. This makes notes a
powerful way to **bank knowledge over time** — any facts, context, or decisions stored in notes become grounding
material for future AI queries.

When an AI chat uses folder scope (or defaults to the entire workspace), notes within that scope are searched alongside
files. The AI retrieves relevant passages from notes and cites them in its answers.

**Use cases:**
- Store project context, decisions, and rationale as notes. Months later, ask "Why did we choose vendor X?" and the AI
  retrieves the note with that decision.
- After researching a topic, save key findings in a note. Future AI chats automatically use those findings as grounding.
- Create reference documents (style guides, naming conventions, process docs) that inform all future AI queries in the
  workspace.

#### Linking Users to Notes

**Open a note in the workspace UI** — append `?note={opaque_id}` to the workspace storage URL:

`https://{org.domain}.fast.io/workspace/{folder_name}/storage/root?note={note_opaque_id}`

**Link directly to the note preview** — use the standard file preview URL:

`https://{org.domain}.fast.io/workspace/{folder_name}/preview/{note_opaque_id}`

The preview link is more effective if you want the user to focus on reading just that note, while the `?note=` link
opens the note within the full workspace context.

### 7. Comments & Annotations

Humans can leave feedback directly on files, anchored to specific content:

- **Image comments** — anchored to regions of the image
- **Video comments** — anchored to timestamps with frame-stepping and spatial region selection
- **Audio comments** — anchored to timestamps or time ranges
- **PDF comments** — anchored to specific pages with optional text selection
- **Threaded replies** — single-level threads under each comment (replies to replies are auto-flattened)
- **Emoji reactions** — one reaction per user per comment, new replaces previous
- **Mentions** — tag users with `@[user:USER_ID:Display Name]` syntax in the comment body

**Character limits:** The comment `body` field has a hard maximum of **8,192 characters** — this includes the full mention tag markup. When you convert a short `@name` reference into the bracket syntax (e.g., `@[user:abc123:Jane Smith]`), the expanded string is what counts toward the limit. The display text (everything except mention markup) is separately capped at **500 characters**. Build your comment body with the expanded tags first, then verify the total length before submitting.

**Linking users to comments:** Link users to the file preview URL. The comments sidebar opens automatically in workspace
previews, and in share previews when comments are enabled on the share.

Base preview URL:

`https://{org.domain}.fast.io/workspace/{folder_name}/preview/{file_opaque_id}`

For shares: `https://go.fast.io/shared/{custom_name}/{title-slug}/preview/{file_opaque_id}`

**Deep linking to a specific comment:** Append `?comment={comment_id}` to the preview URL. The UI scrolls to and
highlights the comment automatically:

`https://{org.domain}.fast.io/workspace/{folder_name}/preview/{file_opaque_id}?comment={comment_id}`

**Deep linking to media/document positions:** For comments anchored to specific locations, combine with position
parameters:

- `?t={seconds}` — seeks to a timestamp in audio/video (e.g., `?comment={id}&t=45.5`)
- `?p={pageNum}` — navigates to a page in PDFs (e.g., `?comment={id}&p=3`)

**Agent use case:** You generate a design mockup. The human comments "Change the header color" on a specific region of
the image. You read the comment, see exactly what region they're referring to, and regenerate.

### 8. File Uploads — Getting Files Into Fast.io

Agents upload files through a session-based API. There are two paths depending on file size:

#### Small Files (Under 4 MB)

For files under 4 MB, upload in a single request. Send the file as `multipart/form-data` with the `chunk` field
containing the file data, plus `org` (your org domain), `name`, `size`, and `action=create`.

To have the file automatically added to a workspace or share, include `instance_id` (the workspace or share ID) and
optionally `folder_id` (the target folder's OpaqueId, or omit for root). The response includes `new_file_id` — the
permanent OpaqueId of the file in storage. No further steps needed.

```
POST /current/upload/
Content-Type: multipart/form-data

Fields: org, name, size, action=create, instance_id, folder_id, chunk (file)
→ Response: { "result": true, "id": "session-id", "new_file_id": "2abc..." }
```

#### Large Files (4 MB and Above)

Large files use chunked uploads. The flow has five steps:

1. **Create a session** — `POST /current/upload/` with `org`, `name`, `size`, `action=create`, `instance_id`, and
   optionally `folder_id`. Returns a session `id`.

2. **Upload chunks** — Split the file into **5 MB chunks** (last chunk may be smaller). For each chunk, send
   `POST /current/upload/{session_id}/chunk/` as `multipart/form-data` with the `chunk` field (binary data), `order`
   (1-based — first chunk is `order=1`), and `size`. You can upload up to **3 chunks in parallel** per session.

3. **Trigger assembly** — Once all chunks are uploaded, call `POST /current/upload/{session_id}/complete/`. The server
   verifies chunks and combines them into a single file.

4. **Poll for completion** — The upload progresses through states asynchronously. Poll the session details with the
   built-in long-poll:

   `GET /current/upload/{session_id}/details/?wait=60`

   The server holds the connection for up to 60 seconds and returns immediately when the status changes:

   | Status | Meaning | What to Do |
   |--------|---------|------------|
   | `ready` | Awaiting chunks | Upload chunks |
   | `uploading` | Receiving chunks | Continue uploading |
   | `assembling` | Combining chunks | Keep polling |
   | `complete` | Assembled, awaiting storage | Keep polling |
   | `storing` | Being added to storage | Keep polling |
   | **`stored`** | **Done** — file is in storage | Read `new_file_id`, clean up |
   | `assembly_failed` | Assembly error (terminal) | Check `status_message` |
   | `store_failed` | Storage error (retryable) | Keep polling, server retries |

   Stop polling when status is `stored`, `assembly_failed`, or `store_failed`.

5. **Clean up** — Delete the session after completion: `DELETE /current/upload/{session_id}/`.

#### Optional Integrity Hashing

Include `hash` (SHA-256 hex digest) and `hash_algo=sha256` on each chunk for server-side integrity verification. You can
also provide a full-file hash in the session creation request instead.

#### Resuming Interrupted Uploads

If a connection drops mid-upload, the session persists on the server. To resume:

1. Fetch the session: `GET /current/upload/{session_id}/details/`
2. Read the `chunks` map — keys are chunk numbers already uploaded, values are byte sizes
3. Upload only the missing chunks
4. Trigger assembly and continue as normal

#### Manual Storage Placement

If you omit `instance_id` when creating the session, the file is uploaded but not placed in any workspace or share. You
can add it to storage manually afterward:

```
POST /current/workspace/{id}/storage/{folder}/addfile/
Body: from={"type":"upload","upload":{"id":"{session_id}"}}
```

This is useful when you need to upload first and decide where to place the file later.

#### MCP Binary Upload — Three Approaches

MCP agents have three ways to pass binary data when uploading chunks. Each uses the `upload` tool's `chunk` action
with exactly one of `data`, `blob_ref`, or `content` (for text):

**1. `data` parameter (base64) — simplest for MCP agents**

Pass base64-encoded binary directly in the `data` parameter of the `chunk` action. No extra steps required. Works
with any MCP client. Adds ~33% size overhead from base64 encoding.

**2. `stage-blob` action — MCP tool-based blob staging**

Use the `upload` tool's `stage-blob` action with `data` (base64) to pre-stage binary data as a blob. Returns a
`blob_id` that you pass as `blob_ref` in the `chunk` call. Useful when decoupling staging from uploading or preparing
multiple chunks in advance.

1. `upload` action `stage-blob` with `data` (base64-encoded binary) → returns `{ blob_id, size }`
2. `upload` action `chunk` with `blob_ref` set to the `blob_id`

**3. `POST /blob` endpoint — HTTP blob staging for non-MCP clients**

A sidecar HTTP endpoint that accepts raw binary data outside the JSON-RPC pipe, avoiding base64 encoding entirely.
Useful for clients that can make direct HTTP requests alongside MCP tool calls.

1. `POST /blob` with `Mcp-Session-Id` header and raw bytes as the request body → returns `{ blob_id, size }`
2. `upload` action `chunk` with `blob_ref` set to the `blob_id`

**Blob constraints (apply to both staging methods):**
- Blobs expire after **5 minutes** — stage and consume them promptly
- Each blob is consumed (deleted) on first use and cannot be reused
- Maximum blob size: **100 MB**

**Agent use case:** You're generating a 200 MB report. Create an upload session targeting the client's workspace, split
the file into 5 MB chunks, upload 3 at a time, trigger assembly, and poll until `stored`. The file appears in the
workspace with previews generated automatically. Use the activity polling endpoint (section 13) to know when AI indexing
completes if intelligence is enabled.

### 9. URL Import — Pull Files From Anywhere

When you need to add a file from the web, use `POST /current/web_upload/` with `source_url` instead of downloading it
locally and re-uploading. This is faster because the file transfers server-to-server — your agent never touches the
bytes.

- Supports any HTTP/HTTPS URL
- Supports OAuth-protected sources: **Google Drive, OneDrive, Dropbox**
- Files go through the same processing pipeline (preview generation, AI indexing if intelligence is enabled, virus
  scanning)

**Check progress after submitting.** Web uploads are processed asynchronously by Fast.io's server-side fetch agent,
which may be blocked or rate-limited by the source. The import can fail silently if the source rejects the request, times
out, or returns an error. Monitor the upload status to confirm the file was actually retrieved and stored before
reporting success to the user.

**Security note:** The `web_upload` endpoint instructs the Fast.io cloud server to fetch the URL — not the agent's
local environment. The Fast.io server is a public cloud service with no access to the agent's local network, internal
systems, or private infrastructure. It can only reach publicly accessible URLs and supported OAuth-authenticated cloud
storage providers. No internal or private data is exposed beyond what the agent could already access through its own
network requests.

**Agent use case:** A user says "Add this Google Doc to the project." You call `POST /current/web_upload/` with the URL.
Fast.io downloads it server-side, generates previews, indexes it for AI, and it appears in the workspace. No local I/O —
and no bandwidth consumed by your agent.

### 10. Real-Time Collaboration

Fast.io uses WebSockets for instant updates across all connected clients:

- **Live presence** — see who's currently viewing a workspace or share
- **Cursor tracking** — see where other users are navigating
- **Follow mode** — click a user to mirror their exact navigation
- **Instant file sync** — uploads, edits, and deletions appear immediately for all viewers

### 11. Ownership Transfer — Hand Off to Humans

The killer feature for agents: build something, then give it to a human. This is also the upgrade path when the agent
plan's 5,000 monthly credits are exhausted or plan limits are reached — transferring to a human is the only way to
upgrade beyond the agent plan.

**Important:** Only `agent` account types can create transfer tokens. This is why agents should **always** create
accounts with `agent=true`. If you created a human account, you cannot use the transfer/claim API — you must direct the
user to upgrade the org themselves.

1. Agent creates an org, sets up workspaces, uploads files, configures shares
2. Agent generates a transfer token via `POST /current/org/{org_id}/transfer/token/create/` (64-char string, valid 72
   hours, max 5 active tokens per org)
3. Agent sends the claim URL to the human: `https://go.fast.io/claim?token={token}`
4. Human clicks the link, logs in (or creates an account), and claims the org

**What happens:**

- Human becomes the owner of the org and all workspaces
- Agent is demoted to admin (can still manage files and shares)
- Human gets the free plan (credit-based, no trial period)
- Human can upgrade to Pro or Business at any time for unlimited credits and expanded limits

**Agent use case:** A user says "Set up a project workspace for my team." You create the org, build out workspace
structure, upload templates, configure shares for client deliverables, invite agents and human team members — then
transfer ownership. The human walks into a fully configured platform with an agentic team already in place. You stay on
as admin to keep managing things.

**Credit exhaustion use case:** Your agent hits the 5,000 credit limit mid-month. Create a transfer token, send the
claim URL to the human user, and let them know they can upgrade to Pro or Business for unlimited credits. After
claiming, the human upgrades and the org is no longer credit-limited.

### 12. Events — Real-Time Audit Trail

Events give agents a real-time audit trail of everything that happens across an organization. Instead of scanning entire
workspaces to detect what changed, query the events feed to see exactly which files were uploaded, modified, renamed, or
deleted — and by whom, and when. This makes it practical to build workflows that react to changes: processing a document
the moment it arrives, flagging unexpected permission changes, or generating a daily summary of activity for a human.

The activity log is also the most efficient way for an agent to stay in sync with a workspace over time. Rather than
periodically listing every file and comparing against a previous snapshot, check events since your last poll to get a
precise diff. This is especially valuable in large workspaces where full directory listings are expensive.

#### What Events Cover

- **File operations** — uploads, downloads, moves, renames, deletes, version changes
- **Membership changes** — new members added, roles changed, members removed
- **Share activity** — share created, accessed, files downloaded by recipients
- **Settings updates** — workspace or org configuration changes
- **Billing events** — credit usage, plan changes
- **AI operations** — ingestion started, indexing complete, chat activity

#### Querying Events

Search and filter events with `GET /current/events/search/`:

- **Scope by profile** — filter by `workspace_id`, `share_id`, `org_id`, or `user_id`
- **Filter by type** — narrow to specific event names, categories, or subcategories (see reference below)
- **Date range** — use `created-min` and `created-max` for time-bounded queries
- **Pagination** — offset-based with `limit` (1-250) and `offset`

Get full details for a single event with `GET /current/event/{event_id}/details/`, or mark it as read with
`GET /current/event/{event_id}/ack/`.

#### Event Categories

Use the `category` parameter to filter by broad area:

| Category      | What It Covers                                        |
|---------------|-------------------------------------------------------|
| `user`        | Account creation, updates, deletion, avatar changes   |
| `org`         | Organization lifecycle, settings, transfers            |
| `workspace`   | Workspace creation, updates, archival, file operations |
| `share`       | Share lifecycle, settings, file operations              |
| `node`        | File and folder operations (cross-profile)             |
| `ai`          | AI chat, summaries, RAG indexing                       |
| `invitation`  | Member invitations sent, accepted, declined            |
| `billing`     | Subscriptions, trials, credit usage                    |
| `domain`      | Custom domain configuration                            |
| `apps`        | Application integrations                               |
| `metadata`    | Metadata extraction, templates, key-value updates      |

#### Event Subcategories

Use the `subcategory` parameter for finer filtering within a category:

| Subcategory      | What It Covers                                       |
|------------------|------------------------------------------------------|
| `storage`        | File/folder add, move, copy, delete, restore, download |
| `comments`       | Comment created, updated, deleted, mentioned, replied, reaction |
| `members`        | Member added/removed from org, workspace, or share   |
| `lifecycle`      | Profile created, updated, deleted, archived          |
| `settings`       | Configuration and preference changes                 |
| `security`       | Security-related events (2FA, password)              |
| `authentication` | Login, SSO, session events                           |
| `ai`             | AI processing, chat, indexing                        |
| `invitations`    | Invitation management                                |
| `billing`        | Subscription and payment events                      |
| `assets`         | Avatar/asset updates                                 |
| `upload`         | Upload session management                            |
| `transfer`       | Cross-profile file transfers                         |
| `import_export`  | Data import/export operations                        |
| `quickshare`     | Quick share operations                               |
| `metadata`       | Metadata operations                                  |

#### Common Event Names

Use the `event` parameter to filter by exact event name. Here are the most useful ones for agents:

**File operations (workspace):**
`workspace_storage_file_added`, `workspace_storage_file_deleted`, `workspace_storage_file_moved`,
`workspace_storage_file_copied`, `workspace_storage_file_updated`, `workspace_storage_file_restored`,
`workspace_storage_folder_created`, `workspace_storage_folder_deleted`, `workspace_storage_folder_moved`,
`workspace_storage_download_token_created`, `workspace_storage_zip_downloaded`,
`workspace_storage_file_version_restored`, `workspace_storage_link_added`

**File operations (share):**
`share_storage_file_added`, `share_storage_file_deleted`, `share_storage_file_moved`,
`share_storage_file_copied`, `share_storage_file_updated`, `share_storage_file_restored`,
`share_storage_folder_created`, `share_storage_folder_deleted`, `share_storage_folder_moved`,
`share_storage_download_token_created`, `share_storage_zip_downloaded`

**Comments:**
`comment_created`, `comment_updated`, `comment_deleted`, `comment_mentioned`, `comment_replied`,
`comment_reaction`

**Membership:**
`added_member_to_org`, `added_member_to_workspace`, `added_member_to_share`,
`removed_member_from_org`, `removed_member_from_workspace`, `removed_member_from_share`,
`membership_updated`

**Workspace lifecycle:**
`workspace_created`, `workspace_updated`, `workspace_deleted`, `workspace_archived`, `workspace_unarchived`

**Share lifecycle:**
`share_created`, `share_updated`, `share_deleted`, `share_archived`, `share_unarchived`,
`share_imported_to_workspace`

**AI:**
`ai_chat_created`, `ai_chat_new_message`, `ai_chat_updated`, `ai_chat_deleted`, `ai_chat_published`,
`node_ai_summary_created`, `workspace_ai_share_created`

**Metadata:**
`metadata_kv_update`, `metadata_kv_delete`, `metadata_kv_extract`,
`metadata_template_update`, `metadata_template_delete`,
`metadata_view_update`, `metadata_view_delete`, `metadata_template_select`

**Quick shares:**
`workspace_quickshare_created`, `workspace_quickshare_updated`, `workspace_quickshare_deleted`,
`workspace_quickshare_file_downloaded`, `workspace_quickshare_file_previewed`

**Invitations:**
`invitation_email_sent`, `invitation_accepted`, `invitation_declined`

**User:**
`user_created`, `user_updated`, `user_deleted`, `user_email_reset`, `user_asset_updated`

**Org:**
`org_created`, `org_updated`, `org_closed`, `org_transfer_token_created`, `org_transfer_completed`

**Billing:**
`subscription_created`, `subscription_cancelled`, `billing_free_trial_ended`

#### Example Queries

**Recent comments in a workspace:**
```
GET /current/events/search/?workspace_id={id}&subcategory=comments&limit=50
```

**Files uploaded to a share in the last 24 hours:**
```
GET /current/events/search/?share_id={id}&event=share_storage_file_added&created-min=2025-01-19T00:00:00Z
```

**All membership changes across an org:**
```
GET /current/events/search/?org_id={id}&subcategory=members
```

**AI activity in a workspace:**
```
GET /current/events/search/?workspace_id={id}&category=ai
```

**Who downloaded files from a share:**
```
GET /current/events/search/?share_id={id}&event=share_storage_download_token_created
```

#### AI-Powered Summaries

Request a natural language recap of recent activity with `GET /current/events/search/summarize/`. Returns event counts,
category breakdowns, and a narrative summary. Focus the summary on a specific workspace or share, or summarize across
the entire org.

**Agent use case — stay in sync:** You manage a workspace with 10,000 files. Instead of listing the entire directory
tree to find what changed, query events since your last check. You get a precise list: "3 files uploaded, 1 renamed,
2 new members added" — with timestamps, actors, and affected resources.

**Agent use case — react to changes:** A client uploads tax documents to a Receive share. The events feed shows the
upload immediately. Your agent detects it, processes the documents, and notifies the accountant — no polling the file
list required.

**Agent use case — report to humans:** A human asks "What happened on the project this week?" You call the AI summary
endpoint scoped to their workspace and return a clean narrative report — no log parsing required.

### 13. Activity Polling — Wait for Changes Efficiently

After triggering an async operation (uploading a file, enabling intelligence, creating a share), don't loop on the
resource endpoint to check if it's done. Instead, use the activity long-poll endpoint:

`GET /current/activity/poll/{entity_id}?wait=95&lastactivity={timestamp}`

The `{entity_id}` is the profile ID of the resource you're watching — a workspace ID, share ID, or org ID. For
**upload sessions**, use the **user ID** (since uploads are user-scoped, not workspace-scoped until the file is added
to storage).

The server holds the connection open for up to 95 seconds and returns **immediately** when something changes on that
entity — file uploads complete, previews finish generating, AI indexing completes, comments are added, etc.

The response includes activity keys that tell you *what* changed (e.g., `storage:{fileId}` for file changes,
`preview:{fileId}` for preview readiness, `ai_chat:{chatId}` for chat updates, `ai_state:{fileId}` for AI indexing
state changes, `upload:{uploadId}` for upload completion). Pass the returned `lastactivity` timestamp into your next
poll to receive only newer changes.

This gives you near-instant reactivity with a single open connection per entity, instead of hammering individual
endpoints.

**WebSocket upgrade:** For true real-time delivery (~300ms latency vs ~1s for polling), connect via WebSocket at
`wss://{host}/api/websocket/?token={auth_token}`. The server pushes activity arrays as they happen:

```json
{"response": "activity", "activity": ["storage:2abc...", "preview:2abc..."]}
```

You then fetch only the resources that changed. If the WebSocket connection fails, fall back to long-polling — the data
is identical, just slightly higher latency.

**Agent use case:** You upload a 500-page PDF and need to know when AI indexing is complete before querying it. Instead
of polling the file details endpoint every few seconds, open a single long-poll on the workspace. When
`ai_state:{fileId}` appears in the activity response, the file is indexed and ready for AI chat.

### 14. Metadata — Structured Data on Files

The metadata system lets agents attach structured, typed key-value data to files. This goes beyond filenames and
timestamps — you can store invoice amounts, contract parties, document categories, or any domain-specific fields, then
query and sort files by those fields.

#### Architecture

The system has three layers:

1. **Templates** — define a metadata schema: named fields with types (`string`, `int`, `float`, `bool`, `json`, `url`,
   `datetime`), constraints (`min`, `max`, `fixed_list`), and descriptions. Templates belong to a workspace and are
   grouped by category (`legal`, `financial`, `business`, `medical`, `technical`, `engineering`, `insurance`,
   `educational`, `multimedia`, `hr`).

2. **Template Assignments** — bind a single template to a workspace. All files in the workspace inherit that template
   automatically. One template per workspace — assigning a new template replaces the previous one. This keeps resolution
   simple and efficient (a single lookup instead of a tree-walk).

3. **Node Metadata** — the actual key-value pairs stored on individual files. Each file's metadata is split into
   **template metadata** (conforming to the resolved template's field definitions) and **custom metadata** (user-defined
   fields not tied to any template).

#### Template Management

| Endpoint | Description |
|----------|-------------|
| `GET /current/metadata/templates/categories/` | List available template categories |
| `POST /current/workspace/{id}/metadata/templates/` | Create a template (name, description, category, fields JSON) |
| `DELETE /current/workspace/{id}/metadata/templates/` | Delete a template |
| `GET /current/workspace/{id}/metadata/templates/list/` | List templates (sub-paths: `all`, `custom`, `system`, `enabled`, `disabled`) |
| `GET /current/workspace/{id}/metadata/templates/{template_id}/details/` | Get template details with all fields |
| `POST /current/workspace/{id}/metadata/templates/{template_id}/settings/` | Enable/disable, set priority (1-5) |
| `POST /current/workspace/{id}/metadata/templates/{template_id}/update/` | Update definition (append `/create/` to copy) |

#### Template Assignment & Resolution

| Endpoint | Description |
|----------|-------------|
| `POST /current/workspace/{id}/metadata/template/assign/` | Assign template to the workspace (one per workspace) |
| `DELETE /current/workspace/{id}/metadata/template/unassign/` | Remove the workspace template assignment |
| `GET /current/workspace/{id}/metadata/template/resolve/{node_id}/` | Resolve the workspace template (`node_id` accepted for compat, ignored) |
| `GET /current/workspace/{id}/metadata/template/assignments/` | List the workspace template assignment |

#### Node Metadata Operations

| Endpoint | Description |
|----------|-------------|
| `GET /current/workspace/{id}/storage/{node_id}/metadata/details/` | Get all metadata (`template_metadata` + `custom_metadata`) |
| `POST /current/workspace/{id}/storage/{node_id}/metadata/update/{template_id}/` | Set/update key-value pairs |
| `DELETE /current/workspace/{id}/storage/{node_id}/metadata/` | Delete metadata keys |
| `POST /current/workspace/{id}/storage/{node_id}/metadata/extract/` | AI-extract metadata from file content (documents, images, code) |
| `POST /current/workspace/{id}/storage/{node_id}/metadata/extract-all/` | Batch-extract metadata for all files in a folder (async, returns job_id) |
| `GET /current/workspace/{id}/storage/{node_id}/metadata/list/{template_id}/` | List files with metadata for a template |
| `GET /current/workspace/{id}/storage/{node_id}/metadata/templates/` | List templates in use across files |
| `GET /current/workspace/{id}/storage/{node_id}/metadata/versions/` | Metadata version history |

#### Saved Views

Saved views persist filter/sort configurations for browsing metadata across files in a spreadsheet-like interface.

| Endpoint | Description |
|----------|-------------|
| `POST /current/workspace/{id}/storage/{node_id}/metadata/view/` | Create or update a saved view |
| `DELETE /current/workspace/{id}/storage/{node_id}/metadata/view/` | Delete a saved view |
| `GET /current/workspace/{id}/storage/{node_id}/metadata/views/` | List all saved views |

#### AI-Powered Extraction

Metadata extraction works in three modes:

1. **Automatic (during ingestion)** — when intelligence is enabled and a template is assigned to the workspace, every
   file uploaded is automatically extracted against the template schema during the ingestion pipeline. No API call
   needed — metadata appears on the file after ingestion completes. This includes documents, spreadsheets, images
   (PNG, JPEG, WebP up to 30 MB), and code files.

2. **Manual (per file)** — the extract endpoint (`POST .../metadata/extract/`) resolves the workspace template, reads
   the file content, and uses AI to populate the template fields. You can optionally pass `template_id` to override the
   workspace template. Extraction is synchronous — the response includes the extracted metadata immediately.

3. **Batch (per folder)** — the extract-all endpoint (`POST .../metadata/extract-all/`) enqueues an async job that
   processes every file in a folder against the workspace template. Returns a `job_id` for tracking. Rate-limited to
   2 requests/minute, 10/hour. Use this when you assign a template to a workspace that already contains files.

A daily background process also detects stale metadata — files whose extraction predates the template's last update —
and automatically re-extracts them, ensuring metadata stays current when templates evolve.

For example, uploading an invoice to a workspace with a "financial" template automatically fills in fields like
`invoice_number`, `amount`, `vendor_name`, and `due_date` — no extraction call required if intelligence is enabled.

#### Field Definition Structure

When creating templates, each field in the `fields` JSON array supports:

| Property | Type | Description |
|----------|------|-------------|
| `name` | string | Field identifier (alphanumeric + underscore) |
| `description` | string | Human-readable description |
| `type` | string | `string`, `int`, `float`, `bool`, `json`, `url`, `datetime` |
| `min` | number | Minimum value constraint |
| `max` | number | Maximum value constraint |
| `default` | mixed | Default value |
| `fixed_list` | array | Allowed values (dropdown) |
| `can_be_null` | bool | Whether null is allowed |

#### Agent Use Cases

- **Automatic classification:** Assign a template to the workspace, enable intelligence, upload files. Every file gets
  structured metadata extracted automatically during ingestion — no manual extraction calls needed.
- **Data pipeline:** Create a workspace with an invoice template assigned. Upload invoices — metadata (amounts, vendors,
  dates) is extracted automatically. Query by field values using the list endpoint.
- **Compliance tracking:** Create a template with required fields (review_date, reviewer, status). Assign to the
  workspace. The metadata view shows which files are missing required fields at a glance.
- **Bulk backfill:** Assign a template to a workspace that already has files, then use `extract-all` on each folder to
  batch-extract metadata for existing content. The daily staleness walker re-extracts when templates are updated.
- **Custom + template fields:** Files support both template metadata (structured, schema-enforced) and custom metadata
  (user-defined, ad-hoc). Use template fields for consistent extraction and custom fields for one-off annotations.

### 15. Reference Values — Enums & Constraints

This section lists valid values for commonly used parameters across the API.

#### Preview Types

Valid `preview_type` values (used in preview read/preauthorize endpoints):
`thumbnail`, `image`, `hlsstream`, `pdf`, `spreadsheet`

Preview states returned in file details: `unknown`, `not possible`, `not generated`, `error`, `in progress`, `ready`

#### Image Transformations

The `transform_name` in transform endpoints is `image`. Supported query parameters:

| Parameter | Values | Description |
|-----------|--------|-------------|
| `output-format` | `png`, `jpg` | Output image format |
| `width`, `height` | pixels | Resize dimensions |
| `cropwidth`, `cropheight` | pixels | Crop region size |
| `cropx`, `cropy` | pixels | Crop region origin |
| `rotate` | `0`, `90`, `180`, `270` | Rotation angle |
| `size` | `IconSmall`, `IconMedium`, `Preview` | Predefined size presets |

Transformation states: `rendered`, `rendering`, `unrendered`, `unable to render`

#### AI File States

When intelligence is enabled, each file progresses through AI processing states (visible in node details `ai.state`):
`disabled` → `pending` → `inprogress` → `ready` (or `failed`)

#### AI Chat Parameters

| Parameter | Constraint |
|-----------|-----------|
| `type` | `chat` or `chat_with_files` |
| `personality` | `concise`, `detailed` (default) |
| `privacy` / `visibility` | `private`, `public` (default: `public`) |
| `name` | Max 100 characters |
| `question` | Max 12,768 characters |
| `files_attach` | Max 20 files, 200 MB total |
| `files_scope` | Max 100 `nodeId:versionId` pairs |

#### Quick Share Constraints

- Single file only, max 1 GB
- Default expiration: 3 hours, maximum: 24 hours
- Auto-deleted on expiration, public access (no auth)
- Can update expiration but not beyond the original 24-hour window

#### Download Tokens

Use `GET .../storage/{node_id}/requestread/` to generate a temporary auth-free download token. Pass the returned
`token` as a query parameter: `GET .../storage/{node_id}/read/?token={token}`. This is useful for opening files in
browser tabs without sending Authorization headers.

**MCP agents** have additional download options: use the `download://` resource templates for direct content retrieval
(up to 50 MB), or the `/file/` HTTP pass-through endpoint for streaming larger files. See the "MCP Tool Architecture"
section for details.

#### Unit Calculations

- **Storage** is measured in GibiBytes (1024^3 bytes)
- **Bandwidth** is measured in GigaBytes (1000^3 bytes)

---

## Agent Plan — What's Included (Free)

The agent plan is a free tier designed to get agents started. It's intentionally lightweight — enough to build and
demonstrate value, with room to grow when the org transfers to a human on a paid plan.

| Resource                  | Included                                            |
|---------------------------|-----------------------------------------------------|
| **Price**                 | $0 — no credit card, no trial period, no expiration |
| **Storage**               | 50 GB                                               |
| **Max file size**         | 1 GB                                                |
| **Monthly credits**       | 5,000 (resets every 30 days)                        |
| **Workspaces**            | 5                                                   |
| **Shares**                | 50                                                  |
| **Members per workspace** | 5                                                   |
| **Share invitations**     | 10 per share                                        |
| **Account auto-deletion** | Never                                               |

### What Credits Cover

All platform activity consumes credits from the monthly 5,000 allowance:

| Resource                | Cost                    |
|-------------------------|-------------------------|
| Storage                 | 100 credits/GB          |
| Bandwidth               | 212 credits/GB          |
| AI chat tokens          | 1 credit per 100 tokens |
| Document pages ingested | 10 credits/page         |
| Video ingested          | 5 credits/second        |
| Audio ingested          | 0.5 credits/second      |
| Images ingested         | 5 credits/image         |
| File conversions        | 25 credits/conversion   |

When credits run out, the org enters a reduced-capability state — file storage and access continue to work, but
credit-consuming operations (AI chat, file ingestion, bandwidth-heavy downloads) are limited until the 30-day reset.
The org is never deleted.

**When you hit the credit limit:** The recommended path is to transfer the org to a human user who can upgrade to a
paid plan with unlimited credits. See "Ownership Transfer" above. If the agent account is using a human account type
(not recommended), direct the user to upgrade at `https://go.fast.io/onboarding` or via the billing API.

### After Transfer — Human Plan Options

Once an agent transfers an org to a human, they get the free plan (credit-based, no trial period) and can upgrade:

| Feature         | Agent (Free) | Free (Human) | Pro       | Business  |
|-----------------|--------------|--------------|-----------|-----------|
| Monthly credits | 5,000        | 5,000        | Unlimited | Unlimited |
| Storage         | 50 GB        | 50 GB        | 1 TB      | 5 TB      |
| Max file size   | 1 GB         | 1 GB         | 25 GB     | 50 GB     |
| Workspaces      | 5            | 5            | 10        | 1,000     |
| Shares          | 50           | 50           | 1,000     | 50,000    |

The transfer flow is the primary way agents deliver value — and the only way to upgrade beyond the agent plan. Set
everything up on the free agent plan, transfer ownership when the work is complete or when credits are exhausted, and
the human upgrades when they're ready. The agent retains admin access to keep managing things.

---

## Common Workflows

### Deliver a Report to a Client

1. Upload report PDF to workspace
2. Create a Send share with password protection and 30-day expiration
3. Share the link with the client
4. Client sees a branded page, previews the PDF inline, downloads if needed
5. You get a notification when they access it

### Collect Documents From a User

1. Create a Receive share ("Upload your tax documents here")
2. Share the link
3. User uploads files through a clean, branded interface
4. Files appear in your workspace, auto-indexed by AI (if intelligence is on)
5. Ask the AI: "Are all required forms present?"

### Build a Knowledge Base

1. Create a workspace **with intelligence enabled**
2. Upload all reference documents
3. AI auto-indexes and summarizes everything on upload
4. Use AI chat scoped to folders or the full workspace to query across all documents
5. Use `ai` action `search` to find files by meaning, not just filename — returns ranked document chunks with relevance scores
6. Answers include citations to specific pages and files

### Set Up an Agentic Team Workspace

1. Create org + workspace + folder structure
2. Upload templates and reference docs
3. Invite other agents and human team members
4. Create shares for client deliverables (Send) and intake (Receive)
5. Configure branding, passwords, expiration
6. Transfer ownership to a human when ready — they get a fully configured platform, agents keep admin access

### Collaborative Review Cycle (Exchange Share)

1. Create an Exchange share ("Review these designs and upload your feedback")
2. Upload draft files for the recipient
3. Share the link — recipient can both download your files and upload theirs
4. Comments and annotations on files enable inline feedback
5. AI summarizes what changed between rounds (if intelligence is on)

### Extract Structured Metadata From Documents

1. Create a workspace **with intelligence enabled**
2. Create a metadata template with the fields you need (e.g., invoice_number, amount, vendor, due_date)
3. Assign the template to the workspace (`POST .../metadata/template/assign/`)
4. Upload files — metadata is automatically extracted during ingestion against the template schema
5. For existing files, use `POST .../metadata/extract-all/` on each folder to batch-extract
6. Query files by metadata fields using the list endpoint, or view in the spreadsheet-like metadata view
7. Custom fields can be added to any file independently of the template

### One-Off Document Analysis (No Intelligence Needed)

1. Create a workspace (intelligence off is fine)
2. Upload the files you want to analyze
3. Create an AI chat and attach the specific files directly (up to 20 files)
4. Ask questions — AI reads the attachments and responds with citations
5. No persistent indexing, no credit cost for ingestion

### Choose Between Room and Shared Folder

**Use a Room (independent storage) when:**

- Delivering final, immutable outputs (reports, compliance packages)
- You want a snapshot that won't change if workspace files are updated
- Files are "done" and shouldn't reflect future edits

**Use a Shared Folder (workspace-backed) when:**

- Files are actively being updated (live data feeds, ongoing projects)
- You want zero storage duplication
- Recipients should always see the latest version

### Manage Credit Budget

1. Check current usage: `GET /current/org/{org_id}/billing/usage/limits/credits/`
2. Storage costs 100 credits/GB — a 10 GB workspace costs 1,000 credits/month
3. Document ingestion costs 10 credits/page — a 50-page PDF costs 500 credits
4. Disable intelligence on storage-only workspaces to avoid ingestion costs
5. Use attach-only AI chat (no intelligence needed) for one-off analysis to save credits
6. When credits run low, transfer the org to a human who can upgrade to unlimited credits

---

## MCP Tool Architecture

The MCP server exposes **19 consolidated tools**, each covering a domain. Every tool uses an `action` parameter to
select the specific operation — agents don't need to discover hundreds of separate tools, just 19 tools with clearly
named actions.

| Tool         | Domain                          | Example Actions                                                               |
|--------------|---------------------------------|-------------------------------------------------------------------------------|
| `auth`       | Authentication                  | `signin`, `signup`, `set-api-key`, `pkce-login`, `pkce-complete`, `status`, `signout` |
| `org`        | Organizations                   | `list`, `details`, `create`, `update`, `discover-all`                         |
| `workspace`  | Workspaces & metadata           | `list`, `details`, `create`, `update`, `check-name`, plus 17 `metadata-*` actions for template management, node metadata CRUD, AI extraction, and saved views |
| `share`      | Shares                          | `list`, `create`, `update`, `delete`, `quickshare-create`                     |
| `storage`    | Files, folders, locks, previews | `list`, `details`, `search`, `create-folder`, `create-note`, `move`, `delete`, `lock-acquire`, `lock-status`, `lock-release`, `preview-url` (returns constructed `preview_url`), `preview-transform` (returns constructed `transform_url`) |
| `upload`     | File uploads                    | `create-session`, `stage-blob`, `chunk`, `finalize`, `text-file`, `web-import` |
| `download`   | Downloads                       | `file-url`, `zip-url`, `quickshare-details`                                   |
| `ai`         | AI chat and semantic search (scope defaults to entire workspace — omit scope params to search all indexed documents). Folder scope expands subfolder tree only — documents within scoped folders are searched automatically by RAG, not enumerated individually. | `chat-create`, `message-send`, `message-read`, `chat-list`, `search` |
| `member`     | Members                         | `add`, `update`, `remove`, `details`                                          |
| `invitation` | Invitations                     | `list`, `send`, `revoke`, `accept-all`                                        |
| `asset`      | Branding assets                 | `types`, `list`, `upload`, `delete`                                           |
| `comment`    | Comments                        | `list`, `create`, `details`, `delete`                                         |
| `event`      | Events & audit                  | `search`, `details`, `summarize`, `activity-poll`                             |
| `user`       | Account mgmt                    | `me`, `update`, `invitation-list`, `allowed`                                  |
| `task`       | Task lists & tasks              | `list-lists`, `create-list`, `list-details`, `update-list`, `delete-list`, `list-tasks`, `create-task`, `task-details`, `update-task`, `delete-task`, `change-status`, `assign-task`, `bulk-status`, `reorder-tasks`, `reorder-lists` |
| `todo`       | Todo checklists                 | `list`, `create`, `details`, `update`, `delete`, `toggle`, `bulk-toggle`      |
| `approval`   | Approval workflows              | `list`, `create`, `details`, `resolve`                                        |
| `worklog`    | Activity logs & interjections   | `list`, `append`, `interject`, `details`, `acknowledge`, `unacknowledged`     |
| `apps`       | Apps discovery                  | `list`                                                                        |

### `web_url` in Tool Responses — Use It Instead of Building URLs

All entity-returning tool responses include a `web_url` field containing a ready-to-use link to the resource in the Fast.io web UI.
**Use `web_url` directly** instead of constructing URLs manually from API response fields. This avoids errors from
slug generation, subdomain routing, or parameter formatting.

Tools that return `web_url`:

| Tool | Actions |
|------|---------|
| `org` | `list`, `details`, `create`, `update`, `public-details`, `list-workspaces`, `list-shares`, `create-workspace`, `transfer-token-create`, `transfer-token-list`, `discover-all`, `discover-available`, `discover-external` |
| `workspace` | `list`, `details`, `update`, `available`, `list-shares`, `create-note`, `update-note`, `quickshare-get`, `quickshares-list` |
| `share` | `list`, `details`, `create`, `update`, `public-details`, `available` |
| `storage` | `list`, `details`, `search`, `trash-list`, `create-folder`, `copy`, `move`, `rename`, `restore`, `add-file`, `version-list`, `version-restore`, `preview-url`, `preview-transform` |
| `ai` | `chat-create`, `chat-details`, `chat-list` |
| `upload` | `text-file`, `finalize` |
| `download` | `file-url`, `quickshare-details` |

When presenting links to users, always use `web_url` from tool responses. Never construct URLs manually.

**Resources** available via `resources/read`:
- `skill://guide` — full tool documentation with parameters and examples
- `session://status` — current authentication state
- `download://workspace/{workspace_id}/{node_id}` — download a workspace file (returns base64 content up to 50 MB)
- `download://share/{share_id}/{node_id}` — download a share file (returns base64 content up to 50 MB)
- `download://quickshare/{quickshare_id}` — download a quickshare file (public, no auth required, up to 50 MB)

The `download://` resource templates provide direct file content retrieval via the MCP `resources/read` protocol.
Files up to 50 MB are returned inline as base64 blobs. Larger files return a fallback message directing to the HTTP
pass-through endpoint (see below). The `download` tool's `file-url` and `quickshare-details` actions include a
`resource_uri` field in their response that points to the corresponding `download://` resource URI.

**HTTP pass-through endpoint** for file downloads:

The MCP server exposes a `/file/` HTTP endpoint that streams file content directly with proper `Content-Type`,
`Content-Length`, and `Content-Disposition` headers — useful for large files that exceed the 50 MB MCP resource limit
or when streaming is preferred over base64 encoding.

| Path | Auth | Description |
|------|------|-------------|
| `GET /file/workspace/{workspace_id}/{node_id}` | `Mcp-Session-Id` header required | Stream a workspace file |
| `GET /file/share/{share_id}/{node_id}` | `Mcp-Session-Id` header required | Stream a share file |
| `GET /file/quickshare/{quickshare_id}` | None (public) | Stream a quickshare file |

For workspace and share downloads, include the `Mcp-Session-Id` header from your active MCP session. The server uses
the session's auth token to fetch the file and streams it back.

**Query parameters:**
- `?error=html` — returns error pages as HTML instead of JSON (useful for browser-facing links)

**Size limits:** The `download://` resource templates return file content inline (base64) for files up to **50 MB**.
Larger files return a fallback message directing to the `/file/` HTTP pass-through endpoint.

**`web_url` in download responses:** The `download` tool's `file-url` and `quickshare-details` actions include both
a `resource_uri` (for MCP resource reads) and a `web_url` (for browser-facing links) in their responses.

**Resource completion** — The workspace and share `download://` resource templates support MCP `completion/complete`
for tab-completion of IDs. Agents can use this to discover valid workspace IDs, share IDs, and node IDs without
needing to call separate list actions first.

### Tool Annotations — Safety & Side Effects

All 19 tools include explicit MCP annotations (`title`, `readOnlyHint`, `destructiveHint`, `idempotentHint`,
`openWorldHint`) so agents and agent frameworks can make informed decisions about confirmation prompts, retries, and
automated execution.

**Read-only tools** (safe, no confirmation needed, `idempotentHint: true`):
- `download`, `event`, `apps` — these tools only read data, never modify state, and are safe to retry

**Non-destructive mutation tools** (create or update, no delete actions):
- `upload`, `invitation`, `worklog` — these tools create or modify resources but cannot delete them

**Destructive tools** (include delete, purge, or close actions — require user confirmation):
- `auth`, `user`, `org`, `workspace`, `share`, `storage`, `ai`, `comment`, `member`, `asset`, `task`, `todo`, `approval` — these tools have at
  least one action that permanently removes or closes a resource. Agent frameworks should prompt for confirmation before
  executing destructive actions.

**Discovery tools** (`openWorldHint: true`):
- `org`, `user`, `workspace`, `share`, `storage` — these tools can discover resources beyond the agent's current
  context. Agents may encounter resources they haven't seen before in list/search results.

**Credit-consuming operations** to be aware of:
- AI chat: 1 credit per 100 tokens
- File uploads: storage credits (100 credits/GB)
- Downloads: bandwidth credits (212 credits/GB)
- Document ingestion: 10 credits/page (when intelligence is enabled)

### Code Mode — Streamlined Tools for Headless Agents

The MCP server (v2026.02.102+) detects the connecting client and serves one of two tool sets:

**Named Mode** (Claude Desktop, Cline, unknown clients): All 19 core tools listed above plus 12 app-specific widget
tools — the full interactive experience with action-based routing across every domain.

**Code Mode** (Claude Code, Cursor, Continue): 4 tools optimized for programmatic workflows:

| Tool       | Purpose                                                                                     |
|------------|---------------------------------------------------------------------------------------------|
| `auth`     | Authentication — same as Named Mode (`signin`, `signup`, `set-api-key`, `pkce-login`, etc.) |
| `upload`   | File uploads — same as Named Mode (`create-session`, `chunk`, `finalize`, `text-file`, etc.)|
| `search`   | Keyword/tag search over 285 API endpoints                                                   |
| `execute`  | Run agent-provided JavaScript against the Fast.io API in a sandboxed environment            |

#### `search` Tool

Discovers API endpoints by keyword and tag. Returns scored matches with method, path, summary, parameters, and relevant
concept docs (pagination, error codes, etc.).

**Parameters:**

| Parameter          | Type    | Required | Description                                                    |
|--------------------|---------|----------|----------------------------------------------------------------|
| `query`            | string  | Yes      | Keyword search query (e.g., "list workspaces", "upload file")  |
| `tag`              | string  | No       | Filter results by API tag (e.g., "workspace", "storage", "ai") |
| `include_concepts` | boolean | No       | Include related concept docs (pagination, error codes, etc.)   |
| `max_results`      | number  | No       | Maximum number of endpoint matches to return                   |

#### `execute` Tool

Runs agent-provided JavaScript in a sandboxed `AsyncFunction` with a `fastio` proxy object that handles auth
injection, envelope parsing, and error extraction. The sandbox has whitelisted globals only (`JSON`, `Math`, `Date`,
etc.), blocks prototype chain escapes, and enforces a 60-second timeout.

**Parameters:**

| Parameter    | Type   | Required | Description                                              |
|--------------|--------|----------|----------------------------------------------------------|
| `code`       | string | Yes      | JavaScript code to execute in the sandbox                |
| `timeout_ms` | number | No       | Execution timeout in milliseconds (1,000–60,000)         |

**`fastio` proxy methods:**

| Method              | Description                           |
|---------------------|---------------------------------------|
| `fastio.get(path)`  | `GET` request to the Fast.io API      |
| `fastio.post(path, body)` | `POST` with form-encoded body   |
| `fastio.postJson(path, body)` | `POST` with JSON body        |
| `fastio.put(path, body)` | `PUT` request                    |
| `fastio.delete(path)` | `DELETE` request                   |

The proxy automatically injects the authenticated session token, unwraps the API response envelope, and extracts errors
— agents receive clean response data without boilerplate.

#### Code Mode Workflow Pattern

Code Mode agents follow a **search → review → execute → iterate** loop:

1. **Search** — use the `search` tool to discover relevant API endpoints by keyword or tag
2. **Review** — examine the returned endpoint details (method, path, parameters, summary)
3. **Execute** — call the endpoint programmatically via the `execute` tool using the `fastio` proxy
4. **Iterate** — refine based on results, search for additional endpoints as needed

This pattern replaces the need for 19+ individually named tools. Agents discover endpoints dynamically via search and
call them programmatically via execute, without needing pre-registered tool definitions for each operation.

**Example — list workspaces in an org:**

```javascript
// Search: search tool with query "list workspaces"
// → returns: GET /current/org/{id}/list/workspaces/

// Execute:
const result = await fastio.get('/current/org/{org_id}/list/workspaces/');
return result;
```

### Response Hints — Guided Agent Workflows

Tool responses include structured hints that help agents navigate multi-step workflows, handle errors gracefully, and
understand resource state. Agents should read and act on these hints rather than guessing the next step.

**`_next` — Suggested next actions:**

Successful tool responses include a `_next` array of contextual next-step suggestions using exact tool names, action
names, and IDs from the response. Agents should follow these hints instead of guessing the next step or consulting
docs. Present on approximately 30 actions across all tools.

Example: after `storage` action `list`, `_next` might suggest `["storage folder-details {node_id}",
"download file-url {node_id}", "ai chat"]` with actual IDs from the response populated in the suggestions.

**`_warnings` — Destructive or gated action warnings:**

Actions that are destructive, irreversible, or have significant side effects include `_warnings` strings in their
response. Agents should read these warnings before proceeding and present them to the user when appropriate. Present on
the following actions:
- `storage`: purge, bulk copy/move/delete/restore (partial failure warnings)
- `workspace`: update (intelligence disable), archive, delete
- `org`: close, billing-create
- `share`: delete, archive, update (type change)
- `ai`: chat-delete
- `download`: file-url (token expiry), zip-url
- `upload`: stage-blob (5-minute expiry)
- `org`: transfer-token-create
- `task`: delete-list (cascade to child tasks), delete-task (soft-delete)
- `approval`: resolve (irreversible approve/reject)

**`_recovery` — Error recovery hints:**

Error responses (`isError: true`) include `_recovery` hints as actionable bullet points appended to the error text.
Hints are matched by HTTP status code (10 codes) and error message patterns (12 patterns), guiding agents toward the
correct resolution. All errors also include `(during: <tool> <action>)` so agents know exactly which operation failed.

| Status | Recovery hint |
|--------|---------------|
| 400    | Bad request — check required parameters and value formats |
| 401    | Re-authenticate using `auth` action `signin` or `pkce-login` |
| 402    | Credits exhausted — check with `org` action `limits` |
| 403    | Permission denied — check role with `org` action `details` |
| 404    | Resource not found — verify the ID is correct |
| 405    | Method not allowed — check the action name is valid for this tool |
| 409    | Conflict — resource may already exist |
| 413    | Payload too large — reduce file size or use chunked upload |
| 422    | Validation failed — check field values against documented constraints |
| 429    | Rate limited — wait 2–4 seconds, retry with exponential backoff |

Error message pattern matching provides additional context-specific recovery steps (e.g., "email not verified" →
use `auth` action `email-verify`; "workspace not found" → check workspace ID with `workspace` action `list`;
"workflow not enabled" → use `workspace` or `share` action `enable-workflow`; "already resolved" → check status with
`approval` action `details`; "only interjection" → verify entry type with `worklog` action `details`).

**`ai_capabilities` — AI mode availability:**

Included in `workspace` action `details` responses. Shows the available AI modes for the workspace:
- **Intelligence ON:** `files_scope`, `folders_scope`, `files_attach` (full RAG with indexed search), plus `search` action for semantic search (vector-based document chunk retrieval with relevance scores)
- **Intelligence OFF:** `files_attach` only (max 20 files, 200 MB total). Semantic search is not available.

**`_ai_state_legend` — File AI processing state:**

Included in `storage` action `list` and `search` responses when files have AI state. Describes the possible states:
- `ready` — file is indexed and available for AI queries
- `pending` — file is queued for AI processing
- `inprogress` — file is currently being processed
- `disabled` — AI processing is disabled for this file
- `failed` — AI processing failed for this file

**`_context` — Contextual metadata:**

Certain responses include `_context` with additional metadata specific to the operation. For example, `comment` action
`add` responses include `anchor_formats` describing supported anchor types for positioning comments on files (image
regions, video/audio timestamps, PDF pages).

---

## MCP Workflow Guidance

> **Note:** The MCP server does not provide guided prompts. All workflow guidance is available through
> SERVER_INSTRUCTIONS (received at connection time), the `skill://guide` resource, and the `/skill.md` endpoint.

---

## URL Structure & Link Construction

Fast.io uses subdomain-based routing. Organization domains become subdomains, and every resource (workspace, folder,
file, share) has a URL-safe identifier from API responses that you use to build links.

### How Org Domains Become Subdomains

When you create an organization, you choose a `domain` (2-80 characters, lowercase alphanumeric and hyphens). This
becomes the subdomain for all org URLs:

Organization domain: `"acme"` → All org URLs live at: `https://acme.fast.io/...`

The base domain `go.fast.io` is used for routes that don't require org context (public shares, auth, claim).

> **Prefer `web_url`.** The URL patterns below are reference material. In practice, always use the `web_url` field from tool responses — it handles subdomain routing, slug generation, and edge cases automatically. Only fall back to manual construction when `web_url` is absent (e.g., share-context storage operations).

### Building URLs From API Responses

Every URL parameter comes from a field in the API response. You never need to generate or guess identifiers — use the
values the API gives you.

| URL Parameter | API Response Field            | Format                                | Example                               |
|---------------|-------------------------------|---------------------------------------|---------------------------------------|
| Subdomain     | `organization.domain`         | User-chosen slug                      | `acme`                                |
| Workspace     | `workspace.folder_name`       | URL-safe slug                         | `q4-planning`                         |
| Folder        | `folder.id` (storage node ID) | Opaque ID, or `root` / `trash`        | `2rii2hzajpc2s3kce3itd2z5esygv`       |
| File          | `file.id` (storage node ID)   | Opaque ID                             | `2xzvfaq3slqwa54qtezi66rrcly6w`       |
| Share         | `share.custom_name`           | Server-generated identifier           | `abc123xyz`                           |
| QuickShare    | `quickshare.id`               | Server-generated identifier           | `qs-abc123xyz`                        |
| Claim token   | Transfer API response         | 64-character token                    | `abcdef1234...`                       |

### Deep Links Into Workspaces

These URLs require the user to be logged in and a member of the org. Use the org's `domain` as the subdomain and the
workspace's `folder_name` as the workspace identifier.

| Link Type          | URL Pattern                                                                  |
|--------------------|-----------------------------------------------------------------------------|
| Workspace root     | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/storage/root` |
| Specific folder    | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/storage/{folder.id}` |
| File preview       | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/preview/{file.id}` |
| AI chat            | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/storage/root?chat={chat_id}` |
| Note (in workspace)| `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/storage/root?note={note_id}` |
| Note (preview)     | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/preview/{note_id}` |
| Browse workspaces  | `https://{org.domain}.fast.io/browse-workspaces`                            |

#### Workspace View Query Parameters

Append query parameters to workspace storage URLs to control the initial view mode and info panel tab:

| Parameter | Values                                              | Effect                              |
|-----------|-----------------------------------------------------|-------------------------------------|
| `view`    | `list`, `grid`, `metadata`                          | Sets file list layout mode          |
| `tab`     | `info`, `metadata`, `comments`, `activity`, `versions` | Opens info panel on specified tab |

Parameters are applied on page load only — they set the initial view state but are not updated during in-app navigation.

**Examples:**
- `https://acme.fast.io/workspace/q4-planning/storage/root?view=metadata`
- `https://acme.fast.io/workspace/q4-planning/storage/root?tab=metadata`
- `https://acme.fast.io/workspace/q4-planning/storage/root?view=metadata&tab=info`

**Examples:**
- `https://acme.fast.io/workspace/q4-planning/storage/root`
- `https://acme.fast.io/workspace/q4-planning/storage/2rii2hzajpc2s3kce3itd2z5esygv`
- `https://acme.fast.io/workspace/q4-planning/preview/2xzvfaq3slqwa54qtezi66rrcly6w`

### Shareable Links (No Auth Required)

These are the URLs you send to humans. Access depends on share settings, not authentication.

| Link Type              | URL Pattern                                                                        |
|------------------------|-----------------------------------------------------------------------------------|
| Public share           | `https://go.fast.io/shared/{share.custom_name}/{title-slug}`                      |
| Org-branded share      | `https://{org.domain}.fast.io/shared/{share.custom_name}/{title-slug}`            |
| File within a share    | `https://go.fast.io/shared/{share.custom_name}/{title-slug}/preview/{file.id}`    |
| QuickShare             | `https://go.fast.io/quickshare/{quickshare.id}`                                   |
| Claim (transfer)       | `https://go.fast.io/claim?token={transfer_token}`                                 |

The `{title-slug}` is the share title converted to a URL slug (lowercase, spaces to hyphens, special chars removed).
It's optional — routing works with just the `custom_name` — but improves link readability.

**Examples:**
- `https://go.fast.io/shared/abc123xyz/q4-financial-report`
- `https://acme.fast.io/shared/abc123xyz/q4-financial-report`
- `https://go.fast.io/shared/abc123xyz/q4-financial-report/preview/2xzvfaq3slqwa54qtezi66rrcly6w`
- `https://go.fast.io/quickshare/qs-abc123xyz`
- `https://go.fast.io/claim?token=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890`

### Share Management Links (For Owners/Admins)

| Link Type                    | URL Pattern                                                                          |
|------------------------------|--------------------------------------------------------------------------------------|
| Edit share (from workspace)  | `https://{org.domain}.fast.io/workspace/{workspace.folder_name}/share/{share.custom_name}` |
| Edit share (direct)          | `https://{org.domain}.fast.io/share/{share.custom_name}`                             |

### Settings & Account Links

| Link Type   | URL Pattern                                                                          |
|-------------|--------------------------------------------------------------------------------------|
| Org settings| `https://{org.domain}.fast.io/settings`                                              |
| Billing     | `https://{org.domain}.fast.io/settings/billing`                                      |
| Onboarding  | `https://go.fast.io/onboarding` or `https://go.fast.io/onboarding?orgId={org.id}&orgDomain={org.domain}` |

### Typical Agent Flow: Create and Link

1. **Create org** → API returns `org.domain` (e.g., `"acme"`)
2. **Create workspace** → API returns `workspace.folder_name` (e.g., `"client-docs"`)
3. **Upload files to folder** → API returns `file.id` for each file
4. **Create share from folder** → API returns `share.custom_name`
5. **Build links for the human:**
   - Workspace link: `https://acme.fast.io/workspace/client-docs/storage/root`
   - Share link: `https://go.fast.io/shared/{custom_name}/client-docs`
   - File link: `https://go.fast.io/shared/{custom_name}/client-docs/preview/{file.id}`
6. **Transfer ownership** → API returns token
   - Claim link: `https://go.fast.io/claim?token={token}`

---

## Workflow Primitives

Fast.io provides five workflow primitives for structured agent collaboration. These enable agents and humans to organize
work, track progress, handle urgent corrections, manage approvals, and maintain simple checklists — all within the same
workspaces and shares where files live.

**MCP-connected agents** use four workflow tools — `task`, `worklog`, `approval`, `todo` — instead of calling these
REST endpoints directly. Enable workflow first via `workspace` action `enable-workflow` or `share` action
`enable-workflow`.

### 1. Task Lists & Tasks

Organize work into lists with individual tasks. Task lists belong to a workspace or share and contain ordered tasks.

- **Task statuses:** `pending` → `in_progress` → `complete`, `blocked` (blocked → pending to unblock)
- **Priorities:** `0` (none), `1` (low), `2` (medium), `3` (high), `4` (critical) — integer values
- **Assignees:** assign tasks to specific members
- **Dependencies:** tasks can depend on other tasks
- **File linking:** connect tasks to files or notes via `node_id` — the linked node provides context and is indexed by AI

| Endpoint | Description |
|----------|-------------|
| `GET /tasks/workspace/{workspace_id}/` | List task lists in a workspace |
| `GET /tasks/share/{share_id}/` | List task lists in a share |
| `POST /tasks/workspace/{workspace_id}/create/` | Create a task list in a workspace |
| `POST /tasks/share/{share_id}/create/` | Create a task list in a share |
| `GET /tasks/{list_id}/details/` | Get task list details |
| `POST /tasks/{list_id}/update/` | Update a task list |
| `POST /tasks/{list_id}/delete/` | Delete a task list |
| `GET /tasks/{list_id}/items/` | List tasks in a list |
| `POST /tasks/{list_id}/items/create/` | Create a task |
| `GET /tasks/{list_id}/items/{task_id}/` | Get task details |
| `POST /tasks/{list_id}/items/{task_id}/update/` | Update a task |
| `POST /tasks/{list_id}/items/{task_id}/delete/` | Delete a task |
| `POST /tasks/{list_id}/items/{task_id}/status/` | Change task status |
| `POST /tasks/{list_id}/items/{task_id}/assign/` | Assign a task |
| `POST /tasks/{list_id}/items/bulk-status/` | Bulk status change |
| `POST /tasks/{list_id}/items/reorder/` | Bulk reorder tasks |
| `POST /tasks/workspace/{workspace_id}/reorder/` | Bulk reorder task lists |
| `POST /tasks/share/{share_id}/reorder/` | Bulk reorder task lists |

### 2. Worklogs

Append-only activity logs attached to any entity (task, task list, profile, node). Worklogs provide a chronological
record of progress, decisions, and issues — visible to all members with access to the entity.

- **Entry types:** `info`, `decision`, `error`, `status_change`, `request`, `interjection`
- **Priority levels:** support priority to highlight important entries
- **Attached to any entity:** task, task list, workspace, share, or node

| Endpoint | Description |
|----------|-------------|
| `GET /worklogs/{entity_type}/{entity_id}/` | List worklog entries |
| `POST /worklogs/{entity_type}/{entity_id}/append/` | Append a worklog entry |
| `GET /worklogs/{entry_id}/details/` | Get entry details |

### 3. Interjections

Urgent priority corrections or instructions that require acknowledgement. Interjections are created via a dedicated
endpoint and are always urgent priority. They must be acknowledged before being cleared — ensuring critical messages
are not missed.

| Endpoint | Description |
|----------|-------------|
| `POST /worklogs/{entity_type}/{entity_id}/interjection/` | Create an interjection |
| `GET /worklogs/{entity_type}/{entity_id}/interjections/` | List unacknowledged interjections |
| `POST /worklogs/{entry_id}/acknowledge/` | Acknowledge an interjection |

**Agent use case:** A human notices an agent is heading in the wrong direction. They create an interjection on the
task. The agent checks for unacknowledged interjections before continuing work, sees the correction, acknowledges it,
and adjusts course.

### 4. Approvals

Request/response approval workflow. Create an approval request with a designated approver, who can approve or reject
with a comment.

- **Statuses:** `pending` → `approved` or `rejected`
- **Scoped to workspace or share** — list all approvals for a given profile

| Endpoint | Description |
|----------|-------------|
| `GET /approvals/workspace/{workspace_id}/` | List approvals in a workspace |
| `GET /approvals/share/{share_id}/` | List approvals in a share |
| `POST /approvals/{entity_type}/{entity_id}/create/` | Create an approval request |
| `GET /approvals/{approval_id}/details/` | Get approval details |
| `POST /approvals/{approval_id}/resolve/` | Resolve (approve or reject) |

**Agent use case:** An agent completes a deliverable and needs human sign-off before publishing. It creates an
approval request. The human reviews, approves or rejects with a comment, and the agent proceeds accordingly.

### 5. Todos

Simple checklist items with toggle. Lightweight compared to full tasks — no statuses, no dependencies, just done or
not done. Support assignees and bulk toggle operations.

| Endpoint | Description |
|----------|-------------|
| `GET /todos/workspace/{workspace_id}/` | List todos in a workspace |
| `GET /todos/share/{share_id}/` | List todos in a share |
| `POST /todos/workspace/{workspace_id}/create/` | Create a todo in a workspace |
| `POST /todos/share/{share_id}/create/` | Create a todo in a share |
| `GET /todos/{todo_id}/details/` | Get todo details |
| `POST /todos/{todo_id}/details/update/` | Update a todo |
| `POST /todos/{todo_id}/details/delete/` | Delete a todo |
| `POST /todos/{todo_id}/details/toggle/` | Toggle done/not done |
| `POST /todos/workspace/{workspace_id}/bulk-toggle/` | Bulk toggle in a workspace |
| `POST /todos/share/{share_id}/bulk-toggle/` | Bulk toggle in a share |

### Enabling Workflow

Workflow features must be enabled on each workspace or share before use:

| Endpoint | Description |
|----------|-------------|
| `POST /workspace/{workspace_id}/workflow/enable/` | Enable workflow on a workspace |
| `POST /workspace/{workspace_id}/workflow/disable/` | Disable workflow on a workspace |
| `POST /share/{share_id}/workflow/enable/` | Enable workflow on a share |
| `POST /share/{share_id}/workflow/disable/` | Disable workflow on a share |

### Key Patterns for Agents

- **Enable workflow first:** Call `POST /workspace/{id}/workflow/enable/` before using any workflow endpoints on that
  workspace.
- **All workflow endpoints require the `workflow` feature enabled** on the target workspace or share.
- **All GET endpoints support `format=md`** for LLM-friendly Markdown output — use this when consuming responses in
  agent context windows.
- **Create notes for context, link tasks to notes via `node_id`** — notes are indexed by AI/RAG, so linked context
  becomes searchable and citable in AI chat.
- **Always log your work:** After any significant state-changing action, use `POST /worklogs/{entity_type}/{entity_id}/append/` to record what was done and why. Without worklog entries, agent activity is invisible to humans reviewing the workspace.
- **Pattern:** Create context note → Create task list → Link tasks to notes → Log progress → AI searches across all.

### Recommended Workflow for Agent Teams

1. Enable workflow on the workspace
2. Create a task list for the project
3. Create tasks with descriptions and link to reference notes
4. Log activity with worklog entries — after uploads, task changes, share creation, member changes, or file moves/deletes, append a worklog entry describing what was done and why. This is how humans track agent activity. For batches of related actions, a single summary entry is sufficient.
5. Use interjections for urgent corrections
6. Request approvals for important decisions
7. Use todos for simple checklists
