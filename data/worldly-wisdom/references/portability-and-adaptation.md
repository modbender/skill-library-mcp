# Portability and adaptation

Use this reference when the skill is running in a different agent client, IDE, or tool environment.

## Core rule

Keep the decision workflow stable while adapting the execution details.

## Environment policy

- Never assume a specific product, model family, or tool namespace.
- Treat shell access and local script execution as optional enhancements, not prerequisites.
- Use relative paths from the skill root when referencing bundled files.
- Prefer simple, portable commands such as `python3 scripts/decision_matrix.py` over client-specific wrappers.
- For time-sensitive claims, fetch fresh evidence when possible. If live retrieval is unavailable, state the gap plainly.

## Fallback patterns

### No shell access

Use the templates in `assets/` and perform calculations directly in the response. Show the arithmetic or weighting logic so the user can audit it.

### Shell access but no Python 3

Do small calculations manually. For larger calculations, ask the user for a compact table of options, criteria, weights, or scenarios so you can compute the result reliably in-text.

### Web access unavailable

Use only user-provided data and clearly separate knowns, assumptions, and unknowns. Do not imply an outside view if you cannot actually build one.

## Output policy

- Prefer structured intermediate outputs for calculations.
- Keep final user-facing advice concise, explicit, and updateable.
- Separate facts, assumptions, and judgement.
- Always state what would change your mind.

## Minimal adaptation checklist

1. Confirm whether scripts can run in the current environment.
2. If they can, use the bundled scripts with relative paths.
3. If they cannot, reproduce the same method manually.
4. Check whether fresh evidence is needed.
5. Deliver a recommendation with confidence, key risks, and reversal conditions.
