# ClawHub notes

## Dependency model
- This skill assumes Taskwarrior is installed in the runtime/base image.
- The skill does **not** run system package installs at runtime.

If `task --version` fails, return a dependency message like:
“Taskwarrior is required but not present. Please install system package `taskwarrior` (or `task`) in the runtime image, then re-run.”

## Workspace scoping
- Always store data under `.openclaw/taskwarrior/` within the resolved workspace root.
- Do not use or modify global `~/.task` unless the user explicitly requests global storage.

## Optional environment inputs
The skill may read these if provided, but does not require them:
- OPENCLAW_WORKSPACE
- WORKSPACE
- PROJECT_DIR
- REPO_ROOT

Fallback is always the current working directory.
