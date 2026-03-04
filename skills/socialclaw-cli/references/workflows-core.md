# Core Workflows

Use these playbooks for `auth`, `query`, `post`, and `instagram`.

## Auth Workflow

1. Run status check.
2. If unauthenticated, run login for required API.
3. Re-check status and scopes.

```bash
social auth status
social auth login --api facebook
social auth status
```

Use app credential setup only when required by advanced checks:

```bash
social auth app
social auth debug-token
```

## Query Workflow (Read-Only)

Prefer read-only commands for discovery and baseline state.

```bash
social query me --fields id,name
social query pages --table
social query instagram-media --limit 10
```

Use custom endpoint query when the user provides a path:

```bash
social query custom /me/photos --fields id,name,created_time
```

## Post Workflow (Facebook Page)

1. Validate auth and default page.
2. Set default page if missing.
3. Draft post command with content and optional link.
4. Request confirmation before execution.

```bash
social post pages --set-default
```

If scheduling or publishing is requested, include exact date-time and timezone assumptions in plain text, then require explicit confirmation before proposing write commands.

## Instagram Workflow

Start with account and media discovery, then move to writes.

```bash
social instagram accounts list
social instagram media list --limit 10
social instagram insights --ig-media-id <MEDIA_ID> --metric reach,impressions --period day
```

For write-like operations (publish/comment actions), classify as write and require explicit confirmation before command execution.

## Profile-Aware Execution

When user names a client or profile, keep every command scoped:

```bash
social --profile clientA auth status
social --profile clientA query pages --table
```
