# Security

## Summary

Kanban Workflow integrates with project-management platforms via **local command-line tools** (CLIs) only.

It does **not**:
- store or manage platform API tokens itself
- implement OAuth flows
- directly authenticate to remote services via HTTP

Instead, it executes platform CLIs (e.g. `gh`, `plane`, `linear`, `planka-cli`) and relies on whatever authentication/session those tools already have on the machine.

## Threat model / implications

- **Privilege inheritance**: the skill can do anything the authenticated CLI can do.
  - Example: if `gh` can edit issues and projects in a repo, this skill can too.
- **No sandbox**: command execution happens on the host running the skill.
- **Data exposure**: command output (including task titles/bodies/comments) can be printed to stdout/stderr and may be captured by logs.

## Recommendations

- Use **least-privilege** accounts/tokens for your platform CLIs.
- Prefer scoped tokens (repo/project limited) where the platform supports it.
- Review your CLI auth state before use:
  - `gh auth status`
  - `plane whoami` (or equivalent for your wrapper)
  - `linear whoami` (or equivalent for your wrapper)
- Treat `config/kanban-workflow.json` as **sensitive metadata** (IDs and workspace/repo references). It should not contain secrets, but it can reveal internal structure.

## Reporting

If you discover a security issue in this repository, please open an issue describing:
- the impact
- reproduction steps
- any suggested mitigation
