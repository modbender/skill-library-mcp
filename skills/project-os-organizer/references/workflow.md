# Workflow

## Setup
1. Create config and db paths dedicated to OpenClaw test mode.
2. Include broad local roots and chat roots.

## Refresh
1. Scan local roots recursively.
2. Include non-git project marker folders and strict collection subfolder discovery.
3. Sync GitHub when token/user available.
4. Index sessions and promote unmatched sessions into chat projects.
5. Regenerate summaries and recommendations.
6. Derive `What it is` project descriptions from local project files where possible.
7. Write memory snapshot.

## Resume
1. Open dashboard for visual context and jump links.
2. Use `View Chat` and both resume actions (`Resume in Claude` and `Resume in Codex`) to jump into active sessions (only when session link is valid).
3. Keep dashboard language simple: check `What it is`, `Where left off`, and `Do next`.
4. Use memory markdown for quick command-driven resume.
