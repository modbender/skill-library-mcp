# CLAUDE.md — hashbox-plugin

> System-level directives. All Claude Code agents MUST obey.

## [Project Identity]
- **Name**: hashbox-plugin
- **Description**: OpenClaw plugin that connects an AI agent to the HashBox iOS app via Firebase webhook for push notifications
- **Language**: TypeScript

## [Tech Stack]
| Layer | Technology |
|---|---|
| language | TypeScript |
| framework | Node.js |
| styling | N/A |
| database | Local JSON file (hashbox_config.json) |
| orm | N/A |

## [Rules]
1. Conventional Commits only.
2. Write tests for all new code.
3. No `any` types. No `console.log` in production.
4. Update PROGRESS.md before every commit.
5. Tasks flow: pending -> in-progress -> ready-for-test -> done.
