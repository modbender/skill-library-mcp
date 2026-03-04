# Setup - Hugging Face

Read this on first activation when `~/hugging-face/` does not exist or is incomplete.

## Operating Attitude

- Answer the immediate request first.
- Keep setup short and non-blocking.
- Prefer practical defaults that can be refined through real tasks.

## First Activation

1. Propose local structure and ask for explicit approval before writing files:
```bash
mkdir -p ~/hugging-face/exports
touch ~/hugging-face/{memory.md,shortlists.md,evaluations.md,endpoints.md}
chmod 700 ~/hugging-face
chmod 600 ~/hugging-face/{memory.md,shortlists.md,evaluations.md,endpoints.md}
```
2. If approved and `memory.md` is empty, initialize it using `memory-template.md`.
3. Continue with the user task immediately after setup.

## Integration Priority

Within the first natural exchanges, clarify activation preference:
- Always for requests about Hugging Face models, datasets, Spaces, or inference endpoints
- Only when explicitly requested
- Restricted to one project or repository

Store this preference as plain language context in local memory.

## Baseline Context to Capture

Capture only context that improves future recommendations:
- Preferred task families (chat, embedding, vision, speech, multimodal)
- Runtime constraints (local CPU, local GPU, hosted endpoint)
- License posture (open-only, permissive-only, or case-by-case)
- Output priorities (quality, speed, cost, reproducibility)

If context is missing, proceed with explicit assumptions and keep moving.

## Runtime Defaults

- Start with discovery-first flow: shortlist before inference.
- Default to at least three candidates for comparison.
- Require license and access validation before final recommendation.

## Optional Depth

If the user wants deeper rigor, load:
- `discovery.md` for search and filtering strategy
- `evaluation.md` for comparable scoring rubric
- `inference.md` for endpoint execution patterns
- `troubleshooting.md` for failure recovery
