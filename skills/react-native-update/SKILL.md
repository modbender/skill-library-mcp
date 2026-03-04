---
name: react-native-update
description: Unified integration skill for React Native Update / Pushy（统一入口）across OpenClaw and Claude Code workflows. Use for 安装配置, appKey/update.json 接线, iOS/Android 原生改动, 更新策略（checkStrategy/updateStrategy）, expo-updates 冲突排查, and 热更新接入 troubleshooting in mixed agent CLI environments.
---

# React Native Update Integration

## Overview
Use this skill to get a project from “not integrated” to “hot update works in release builds”.
Prioritize copy-paste-safe steps, smallest viable changes, and explicit verification checkpoints.

## Workflow
1. Detect app type (React Native CLI vs Expo) and target platforms.
2. Apply dependency/install steps from `references/integration-playbook.md`.
3. Apply required native config (Bundle URL / MainApplication integration points).
4. Add `Pushy` client + `UpdateProvider` minimal bootstrapping.
5. Run `scripts/integration_doctor.sh <app-root>` to detect common misses.
6. Return a short action list: done / missing / next verification.


## Platform routing
- If user context is OpenClaw: provide OpenClaw-first instructions and file/workspace conventions.
- If user context is Claude Code: provide Claude Code-first command style and workflow wording.
- If context is unknown: provide neutral steps first, then append OpenClaw/Claude Code notes.
- Keep technical steps identical; only adapt command conventions and delivery style.

## Guardrails
- Keep user code changes minimal and localized.
- Do not promise hot update works in debug mode; emphasize release verification.
- Warn about `expo-updates` conflict in Expo projects.
- Preserve existing app architecture; adapt snippets to current project style.
- If native files differ heavily (monorepo/mixed native), provide targeted patch guidance instead of broad rewrites.

## Outputs to provide
- Minimal integration diff (exact files and snippets).
- Verification checklist (build, check update, download, switch version).
- Troubleshooting hints for common failures.
- Scenario examples when requested (including class component integration and custom whitelist rollout).

## Resources
- Read `references/integration-playbook.md` before giving steps.
- Use `scripts/integration_doctor.sh` for quick project diagnosis.
