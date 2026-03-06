# Memory Frameworks (2025-2026)

This note tracks external memory/context frameworks used by `close-loop`.
Use it to keep guidance current and avoid stale assumptions.

## Selection rules

- Prefer primary sources (paper, official docs, or official repo).
- Record publication date and a stable link.
- Keep operational takeaways concrete and testable.

## Framework map

| Framework | Source | Date | What it contributes |
|---|---|---|---|
| InfiAgent | arXiv:2601.03204 | 2026-01 | Infinite-horizon continuity and long-run state handling |
| A-MEM | arXiv:2502.12110 | 2025-02 | Memory formation/consolidation from interactions |
| Mem0 | arXiv:2504.19413 | 2025-04 | Practical memory layer with selective retention |
| CoALA | arXiv:2309.02427 | 2023-09 | Human-inspired memory split (working/episodic/semantic/procedural) |
| Letta Memory | docs.letta.com | ongoing | Explicit memory blocks and block-level controls |
| LangGraph Memory | docs.langchain.com | ongoing | Typed short-term/long-term state and namespaces |
| Rowboat | github.com/rowboatlabs/rowboat | ongoing | Event-threaded agent orchestration and traceability |

## Security and integrity references

| Topic | Source | Why it matters |
|---|---|---|
| Memory poisoning | AgentPoison (arXiv:2407.12784) | Prevents malicious memory write patterns |
| Adversarial memory safety | Progent (arXiv:2504.11703) | Adds integrity checks for long-lived agents |

## How `close-loop` applies this

- Typed memory buckets come from CoALA-style separation.
- Selective persistence (`score >= 5`) is inspired by A-MEM/Mem0.
- Provenance and confidence labeling support auditability.
- Contradiction handling uses `needs-review` state instead of overwrite.
- Retention is type-based with explicit TTL policy.
- External side effects (push/deploy/publish) are safety-gated.
- Memory writes exclude sensitive data by default.
- Security checkpoint resists memory poisoning and prompt injection.

## Update checklist

Run this checklist before changing framework guidance:

1. Verify links are still valid.
2. Confirm publication date/version did not change.
3. Capture exactly one operational change per framework.
4. Update `close-loop/SKILL.md` only when behavior must change.
5. Keep this file concise; move deep notes to separate references if needed.
