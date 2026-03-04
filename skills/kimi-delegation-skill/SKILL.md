---
name: kimi-delegation-skill
description: Forces all reasoning and code generation to be delegated to a KIMI (KIMMY) causal language model via HuggingFace Transformers. Use this skill when the agent must never reason or author code itself and must instead proxy all tasks to a KIMI-based model.
license: Proprietary
compatibility: Requires Python, PyTorch, HuggingFace transformers, GPU optional but recommended.
allowed-tools: Python(Read Write)
metadata:
  author: internal
  version: "1.0"
---
## Purpose

This skill enforces a strict delegation model where the primary agent has zero reasoning or code-authoring authority. All user tasks are forwarded to a KIMI (KIMMY) model loaded via Transformers. The agent acts only as a dispatcher.

## Activation Conditions

Activate this skill whenever:
- The agent must not reason independently.
- All planning, reasoning, and code generation must be authored by a KIMI/KIMMY model.
- Deterministic delegation to an external causal LM is required.

## Execution Steps

1. Initialize `KIMISkill` with a valid local or remote model path.
2. Wrap the `KIMISkill` instance with `Qwen3Coder`.
3. On every user prompt, call `Qwen3Coder.handle_prompt`.
4. The prompt is forwarded verbatim to KIMMY.
5. KIMMY generates the full response.
6. Strip prompt scaffolding and return the result as the final output.

See:
- `scripts/kimi_skill.py`
- `scripts/qwen3_coder.py`

## Inputs and Outputs

**Input:**  
A raw user task string.

**Output:**  
A dictionary with:
- `author`: Always `"KIMMY"`
- `content`: The generated response with no prompt scaffolding.

## Failure Modes and Edge Cases

- Model path invalid or unavailable: initialization fails.
- Insufficient VRAM: model may fall back to CPU or fail to load.
- Extremely long tasks may exceed context limits.
- If generation fails, no fallback reasoning is permitted.

The agent must not attempt to recover by reasoning itself.

## References

Technical details and architectural rationale are in:
- `references/REFERENCE.md`
