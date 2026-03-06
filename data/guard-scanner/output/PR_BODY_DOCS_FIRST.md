# PR & Issue Comment — Copy-Paste Ready

Updated: 2026-02-18

---

## ① Issue #18677 に貼るコメント（cleaned up）

以下をそのまま GitHub Issue にコピペ：

---

Thanks everyone — here's a cleaned, approval-oriented proposal focused on **docs-first** and **backward compatibility**.

### Proposal: docs-first, no behavior break

I'd like to add a **reference section** to `docs/automation/hooks.md` covering a runtime security guard pattern using the existing `agent:before_tool_call` event.

**Proposed event field additions** (all optional, backward-compatible):

```ts
interface InternalHookEvent {
  // ... existing fields unchanged ...
  cancel?: boolean;        // default false — no-op if runtime doesn't support it yet
  cancelReason?: string;   // user-visible reason when canceled
  policyMode?: "warn" | "balanced" | "strict";
}
```

**Compatibility / rollout:**

- Existing hooks remain unchanged — zero breaking changes.
- Default behavior is **warn-only** unless the runtime supports cancellation *and* a hook explicitly sets `cancel = true`.
- This enables an **observability-first rollout** (`warn`) with optional later enforcement (`balanced` / `strict`).

**What the docs PR would include:**

1. A new subsection in `docs/automation/hooks.md` under "Bundled hook reference"
2. A `HOOK.md` sample with `events: ["agent:before_tool_call"]`
3. A `handler.ts` sample demonstrating three policy modes:
   - `warn` — log/warn only (current reality)
   - `balanced` — cancel high-confidence dangerous patterns
   - `strict` — cancel any policy hit
4. A note clarifying that current runtimes are warn-only

If this direction looks good, I can open a PR immediately with **docs-ready text only** (no runtime behavior change in this PR).

---

## ② PR 本文（GitHub PR の Description に貼る）

**PR タイトル:**
```
docs: add Runtime Security Guard reference to hooks.md
```

**PR Description に以下をコピペ：**

---

## Summary

Adds a reference implementation section to `docs/automation/hooks.md` documenting a runtime security guard pattern using the existing `agent:before_tool_call` hook event.

**This PR contains documentation only — no runtime behavior changes.**

## Motivation

Closes #18677 (docs-first phase).

OpenClaw's VirusTotal integration handles traditional malware signatures well. However, LLM-specific threats — prompt injection, memory poisoning, identity hijacking, MCP tool poisoning — require complementary static/runtime analysis.

The `agent:before_tool_call` event already exists and is usable for observability. This reference shows how to build a runtime policy hook on top of it, with a clear path from monitoring to enforcement.

## What's included

A new subsection **"Runtime Security Guard"** under "Bundled hook reference" in `docs/automation/hooks.md`:

- **Proposed event fields** (`cancel?`, `cancelReason?`, `policyMode?`) — all optional, backward-compatible
- **HOOK.md sample** — standard frontmatter for `agent:before_tool_call`
- **handler.ts sample** — reference implementation with three policy modes (`warn` / `balanced` / `strict`)
- **Operational note** — clarifies current warn-only status and future enforcement path

## Design decisions

| Decision | Rationale |
|----------|-----------|
| Docs-only, no code changes | Minimum friction for review; establishes schema consensus before implementation |
| All new fields are optional | Existing hooks continue working without modification |
| Default `warn` mode | Observability-first — no surprise blocks for existing users |
| Three policy modes | Gives operators clear, graduated control |

## Checklist

- [x] Docs only — no runtime changes
- [x] Backward-compatible — existing hooks unaffected
- [x] Follows existing `docs/automation/hooks.md` structure and style
- [x] Reference implementation tested in production (guard-scanner v1.1.1)

## Related

- Issue: #18677
- Reference implementation: [guard-scanner](https://github.com/koatora20/guard-scanner) (186 patterns, 56 tests, zero dependencies)
- ClawHub: `guard-scanner@1.1.1`, `guava-guard@1.2.0`

---

## ③ 実際のドキュメント diff（PR に含めるファイル変更）

`docs/automation/hooks.md` に以下を追加（"Bundled hook reference" セクションの末尾、boot-md の後）：

```md
### Runtime Security Guard (Reference)

> **Status**: Reference pattern — the `agent:before_tool_call` event is already supported. The optional `cancel` / `cancelReason` / `policyMode` fields are proposed additions for future enforcement.

This reference demonstrates a backward-compatible runtime hook pattern for tool-call safety checks.

**Events**: `agent:before_tool_call`

**Requirements**: None (runs on all platforms)

**What it does**:

1. Intercepts tool calls before execution
2. Scans tool arguments against configurable risk patterns
3. Warns (or blocks, if cancellation is supported) on detection

**Proposed event fields** (backward-compatible additions):

```ts
interface InternalHookEvent {
  // ... existing fields unchanged ...
  cancel?: boolean;        // default false
  cancelReason?: string;   // user-visible reason when canceled
  policyMode?: "warn" | "balanced" | "strict";
}
```

**Policy modes**:

| Mode | Behavior |
|------|----------|
| `warn` | Log/warn only — never blocks (current default) |
| `balanced` | Block high-confidence dangerous patterns |
| `strict` | Block any policy hit |

**Example HOOK.md**:

```md
---
name: security-runtime-guard
description: "Runtime guard hook for tool-call safety checks"
metadata:
  { "openclaw": { "emoji": "🛡️", "events": ["agent:before_tool_call"] } }
---

# security-runtime-guard

Monitors tool calls for risky patterns (prompt injection, shell injection, SSRF).
Default mode: warn-only.
```

**Example handler.ts**:

```ts
import type { HookHandler } from "../../src/hooks/hooks.js";

const HIGH_RISK = [
  /curl\s+.*\|\s*sh/i,
  /reverse\s*shell/i,
  /169\.254\.169\.254/,
];

const handler: HookHandler = async (event) => {
  if (event.type !== "agent" || event.action !== "before_tool_call") return;

  const mode = (event as any).policyMode ?? "warn";
  const text = JSON.stringify(event.context ?? {});
  const hit = HIGH_RISK.find((re) => re.test(text));
  if (!hit) return;

  event.messages.push(`🛡️ Runtime guard: risky pattern detected — ${hit}`);

  if (mode === "warn") return;

  // Future: when cancel API is available
  // (event as any).cancel = true;
  // (event as any).cancelReason =
  //   mode === "strict"
  //     ? "Blocked by strict runtime policy"
  //     : "Blocked (high-risk pattern)";
};

export default handler;
```

**Operational note**:

Current OpenClaw runtimes are warn-only for `agent:before_tool_call` hooks. This reference works as an observability-first policy (`warn` mode). Enforcement activates once the runtime supports the `cancel` / `cancelReason` fields.

**Reference implementation**: [`guard-scanner`](https://github.com/koatora20/guard-scanner) — 186 threat patterns across 20 categories, 56 tests, zero dependencies.
```
