# Vision Guidelines

> Project direction, contribution policy, and merge guardrails from OpenClaw's VISION.md.
> PRs should be evaluated against these guidelines to catch scope, policy, and architectural misalignment early.

---

## 1. Contribution Rules

1. **One PR = one issue/topic.** Do not bundle multiple unrelated fixes/features.
2. **PRs over ~5,000 changed lines** are reviewed only in exceptional circumstances.
3. **Do not open large batches of tiny PRs at once;** each PR has review cost.
4. **For very small related fixes,** grouping into one focused PR is encouraged.

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| PR touches multiple unrelated modules/issues | 🔴 | Suggest splitting into separate PRs |
| Diff exceeds ~5,000 lines | 🔴 | Flag as likely too large for review |
| PR mixes feature + refactor + bugfix | 🟡 | Recommend separating concerns |
| Trivial fix that could be grouped with related trivials | 🟢 | Suggest grouping if other small PRs exist |

---

## 2. Security Philosophy

Security is a deliberate tradeoff: **strong defaults without killing capability.**

- Prioritize secure defaults.
- Expose clear knobs for trusted high-power workflows.
- Risky paths must be explicit and operator-controlled.

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| New capability enabled by default without opt-in | 🔴 | Should default to off; operator enables |
| Security knob removed or hidden | 🔴 | Operator must retain explicit control |
| New external integration without SSRF/auth consideration | 🟡 | Verify security surface |

---

## 3. Plugin & Core Boundary

Core stays lean; optional capability should ship as plugins.

- Preferred plugin path: npm package distribution + local extension loading for dev.
- Plugins should be hosted/maintained in their own repository.
- **The bar for adding optional plugins to core is intentionally high.**

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| New optional capability added directly to core | 🔴 | Should be a plugin unless strong product/security reason |
| Plugin added to core repo instead of separate repo | 🟡 | Recommend external hosting |

---

## 4. Skills Policy

- Bundled skills exist for baseline UX only.
- **New skills should be published to ClawHub first**, not added to core.
- Core skill additions should be rare and require strong product or security reason.

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| New skill added to core without clear product/security justification | 🔴 | Recommend ClawHub publication instead |

---

## 5. MCP Support

OpenClaw supports MCP through `mcporter` (external bridge).

- MCP integration stays decoupled from core runtime.
- Prefer the bridge model over first-class MCP runtime in core.

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| First-class MCP runtime added to core | 🔴 | Should use mcporter bridge instead |
| MCP server management logic in core | 🟡 | Verify it doesn't duplicate mcporter |

---

## 6. Setup & Onboarding

- Terminal-first by design — keeps setup explicit.
- Users must see docs, auth, permissions, and security posture up front.
- **Do not add convenience wrappers that hide critical security decisions.**

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| Setup wrapper that auto-accepts security defaults | 🔴 | User must explicitly see and decide |
| Auth/permission step hidden behind automation | 🟡 | Should remain visible and explicit |

---

## 7. What Will Not Be Merged (Current Policy)

These are explicit guardrails — PRs matching these patterns will not be merged:

1. **New core skills** when they can live on ClawHub.
2. **Full-doc translation sets** — deferred; AI-generated translations planned.
3. **Commercial service integrations** that don't fit model-provider category.
4. **Wrapper channels** around already-supported channels without clear capability/security gap.
5. **First-class MCP runtime** in core when mcporter provides the path.
6. **Agent-hierarchy frameworks** (manager-of-managers / nested planner trees) as default architecture.
7. **Heavy orchestration layers** that duplicate existing agent and tool infrastructure.

### Red Flags

| Signal | Severity | What to flag |
| --- | --- | --- |
| PR matches any "will not merge" category | 🔴 | Flag with specific category match |
| PR adds i18n doc translations directly | 🔴 | Use scripts/docs-i18n pipeline |
| PR adds nested agent orchestration as default | 🔴 | Against architectural direction |

---

## 8. Project Priorities (Current Focus)

When evaluating whether a PR aligns with current priorities:

**Priority (highest):**
- Security and safe defaults
- Bug fixes and stability
- Setup reliability and first-run UX

**Next priorities:**
- Supporting all major model providers
- Improving major messaging channels
- Performance and test infrastructure
- Better computer-use and agent harness capabilities
- CLI and web frontend ergonomics
- Companion apps (macOS, iOS, Android, Windows, Linux)

### Scoring Guidance

- PRs aligned with top priorities get lower risk scores for scope.
- PRs that conflict with priorities or "will not merge" list get higher scores.
- This is informational context, not a gate — a well-executed PR in a lower-priority area is still fine.
