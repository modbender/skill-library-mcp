---
name: multi-user-workspace
description: Multi-user workspace management with sandbox permissions, user profiles, and relationship networks.
---

# Friends

Configure per-user sessions with sandbox isolation, friend profiles, and relationship awareness.

## Core Concepts

- **UserId**: Lowercase unique identifier (e.g., `alice`, `bob`). Used in session keys, filenames, and cross-references.
- **Session**: One session per user, named `agent:<agentId>:<mainKey>` where `mainKey` typically contains the userId.
- **Sandbox**: Optional Docker isolation per session, configured in `openclaw.json`.
- **FRIENDS/**: User profile directory (one file per user, named `{userId}.md`).
- **RELATIONS/**: Relationship directory (files named `{userId1}-{userId2}.md`, alphabetically sorted, can be mutiple users).

## Example Workspace Structure

```
workspace/
├── USER.md              # User registry with permissions
├── AGENTS.md            # Multi-user guidance for assistant
├── FRIENDS/
│   ├── alice.md        # alice's profile
│   └── bob.md          # bob's profile
├── RELATIONS/
│   └── alice-bob.md    # Relationship between alice and bob
├── private/            # Admin-only files (optional)
...
```

## USER.md

Registry of all users. The assistant reads this to identify users and extract `userId` and `Name`.

**Format:**

```markdown
# User Registry

## Users

### alice
- UserId: alice
- Name: Alice
- Role: administrator

### bob
- UserId: bob
- Name: Bob
- Role: guest
```

**Note:** `userId` is unique and in lower case. Use `Role` to determine sandbox configuration in `openclaw.json`.

## FRIENDS/

User profiles. One Markdown file per user, named `{userId}.md`.

Content is flexible. Common sections include:

```markdown
# Alice

## Info
- UserId: alice
- Name: Alice
- Role: administrator
- Emails: alice@example.com
...
## Assistant Relationship
- How the user prefers to interact with the assistant
- Preferred communication style
- Ongoing projects or interests

## Notes
Free-form information about the user.
```

## RELATIONS/

Interpersonal relationships. Files named `{userId1}-{userId2}.md` (alphabetical order, can be mutiple users).

Content is flexible. Example:

```markdown
# Alice & Bob

## Users
- **alice**: Alice
- **bob**: Bob

## Relationship
Friends who collaborate on projects.

## Information Sharing
- Can mention each other's public projects
- Do not share private details without asking
```

## AGENTS.md

Instructions for the assistant. Add this section:

```markdown
## User Identification

When a session starts (after `/new`):

1. Get current session via `session_status`
2. Extract userId from the session key (e.g., `agent:main:alice` → `alice`)
3. Read `FRIENDS/{userId}.md` for user profile
4. Read `RELATIONS/*{userId}*.md` for all relationships involving this user
5. Greet the user by name

## Cross-User Boundaries

- Default: Information does not flow between users
- Exception: Only when explicitly defined in RELATIONS/
```

## Session Configuration

Each user gets an isolated session with configurable sandbox and tool permissions. Configure via `openclaw.json`.

### Administrator Configuration

Full access, no sandbox restrictions:

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
    },
    list: [
      {
        id: "main",
        // Administrator: no sandbox, all tools allowed
        sandbox: { mode: "off" },
      },
    ],
  },
  bindings: [
    // Route admin sessions to main agent without sandbox
    { agentId: "main", match: { session: { regex: "alice$" } } },
  ],
}
```

### Guest Configuration

Sandboxed session with isolated workspace. Guest can read/write/execute in their own directory only:

```json5
{
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
    },
    list: [
      {
        id: "main",
        // Guest: sandbox enabled, isolated directory
        sandbox: {
          mode: "all",
          scope: "session",
          workspaceAccess: "none",  // Don't mount main workspace
          docker: {
            binds: [
              // Mount guest's own directory as /workspace
              "~/.openclaw/workspace/guests/bob:/workspace:rw"
            ]
          }
        },
        tools: {
          allow: ["read", "write", "edit", "exec", "process"],
          deny: ["browser", "canvas", "nodes", "cron", "gateway"],
        },
      },
    ],
  },
  bindings: [
    // Route guest sessions to sandboxed agent
    { agentId: "main", match: { session: { regex: "bob$" } } },
  ],
}
```

**Directory Setup:**

```bash
mkdir -p ~/.openclaw/workspace/guests/bob
```

**Notes:**

- Guest sees `/workspace` as their root (isolated from main workspace)
- Can read/write/execute freely within their directory
- Cannot access USER.md, FRIENDS/, RELATIONS/, or other guests' data

### Configuration Options

**Sandbox:**

- `mode`: `"off"` | `"all"` — Disable or enable sandbox
- `scope`: `"session"` — One container per user session
- `workspaceAccess`: `"none"` | `"ro"` | `"rw"` — Workspace file access

**Tools:**

- `allow`: Array of permitted tool names
- `deny`: Array of prohibited tool names (overrides allow)

**Routing:**

- `bindings[].match.session.regex`: Match session key pattern (e.g., `alice$` matches sessions ending with "alice")
