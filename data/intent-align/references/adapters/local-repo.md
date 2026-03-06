# Adapter: Local Repository

Use for local filesystem repositories, including non-Git and multi-repo workspaces.

## Capabilities
- Read project files and project-local guidance.
- Create/update artifacts, plans, and implementation files.
- Run local verification steps when available.
- Maintain per-repo status in shared alignment hub.

## Auth
- Require filesystem access to target paths.
- Require command/tool execution permission where needed.
- Detect missing access by read/write/exec failures.
- On access failure: mark blocked capability, request path or permission change, continue on accessible repos.

## Inputs
- Absolute repo/workspace paths.
- Phase and file ownership mapping.
- Local verification command list (if defined by project).

## Outputs
```yaml
adapter_result:
  capability: local_repo
  status: ok|partial|failed
  artifacts: [file_paths_or_logs]
  notes: string
```

## Failure and Fallback
- If one repo path fails in multi-repo mode: continue other repos and mark dependency risk.
- If no write permission: run read-only analysis and produce patch plan.
