# Project Definition

A project is anything the user may need to resume and ship.

## Inclusion Rules
1. Git repo roots.
2. Nested project folders with code markers even without `.git`.
3. Chat-derived projects from Claude/Codex sessions when no existing project match exists.
4. Collection subfolders only when they have strong project signals (markers/code/hint dirs), not docs-only noise.
5. For Claude chats, infer nested workspace project from Claude session folder segment when direct hint is too generic.
6. Do not promote low-signal chat transcripts to projects (UUID-like title + generic snippet + no useful hint).

## Project Description Rules
1. Prefer manifest descriptions (`package.json`, `pyproject.toml`, `Cargo.toml`).
2. Else use first meaningful README paragraph.
3. Else infer concise type from stack (`Next.js`, Python, Go, Rust, etc).
4. For chat-only projects, prefer hint-path label (for example workspace subfolder name) over UUID session titles.
5. Else fallback to short chat/title-based summary.

## Currentness Signals
1. Latest commit time/message.
2. Latest GitHub push.
3. Latest chat session activity.
4. Explicit status and open next-step items.

## Left-Off Summary Priority
1. TODO-like signals.
2. Latest commit message.
3. Latest chat session title/snippet.
4. Fallback: simple plain-language phrase (`Working on <project>`).
