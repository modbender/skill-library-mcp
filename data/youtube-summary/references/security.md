# Security and installation considerations

Review this before installing or enabling the skill.

## 1) Runtime dependencies are mandatory

The runner relies on:

- Node.js 18+
- preinstalled `youtube2md` executable on PATH
- `python3` (for transcript text preparation via `prepare.py`)

## 2) Command execution hardening

The runner executes only a resolved local executable path from `type -P youtube2md`.

Hardening behavior:

- no runtime npm execution (`npx`) path exists
- legacy env-based command overrides are blocked:
  - `YOUTUBE2MD_BIN`
  - `YOUTUBE2MD_ALLOW_RUNTIME_NPX`

This removes both arbitrary command override vectors and runtime npm execution at run time.

## 3) Installation-time supply-chain boundary

Even without runtime `npx`, trust still depends on how `youtube2md` is installed.

Recommended baseline:

- install pinned version: `npm i -g youtube2md@1.0.1`
- in stricter environments: use a vetted internal mirror or vendored reviewed package
- re-audit dependencies before any version bump

## 4) OPENAI_API_KEY data exposure boundary

Providing `OPENAI_API_KEY` enables full summarization mode in youtube2md workflows.

Practical implication:

- transcript text and/or related content may be sent to OpenAI APIs.

If content is sensitive, do not set `OPENAI_API_KEY`; use extract-only mode and summarize locally from prepared transcript text.

## 5) Upstream trust and review

`prepare.py` and the local shell runner are simple and readable, but the highest trust boundary is still the upstream `youtube2md` package and its dependencies.

Before production use in sensitive environments:

- review upstream source and release history
- verify dependency tree and lock strategy
- define an update cadence and re-audit process

## Recommended maintainer actions

1. Keep runtime dependencies explicit in skill docs (`Node.js/python3`, plus `youtube2md` executable requirement).
2. Keep runtime command behavior fail-closed (no env-based command override execution).
3. Keep package target fixed at `youtube2md@1.0.1` unless there is an explicit reviewed version bump.
4. Document `OPENAI_API_KEY` behavior as an explicit data-sharing choice.
5. Re-audit upstream package versions before bumping pins.
6. Exclude generated `summaries/*` outputs from release packages.
