# Adapter: GitHub

Use for issues, pull requests, reviews, and repo-hosted coordination.

## Capabilities
- Read/write issues.
- Read/write pull requests.
- Read repository metadata and files.
- Link phase tasks to issue/PR identifiers.

## Auth
- Require GitHub credential with appropriate repository scopes.
- Minimum scope depends on task (`read` for analysis, `write` for issues/PR updates).
- Detect missing auth by failed API/CLI permission checks.
- On auth failure: mark blocked capability, switch to degraded mode, ask user for authorization path.

## Inputs
- Repository owner/name.
- Branch/PR identifiers when applicable.
- Task-to-issue/PR mapping from hub.

## Outputs
```yaml
adapter_result:
  capability: github
  status: ok|partial|failed
  references: [issue_or_pr_or_commit_refs]
  notes: string
```

## Failure and Fallback
- If write unavailable but read available: continue read-only and produce local action queue.
- If GitHub unavailable: use local-repo adapter and tracker-generic adapter if present.
