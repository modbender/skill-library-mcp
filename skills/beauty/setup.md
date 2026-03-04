# Setup — Beauty

Read this on first activation when `~/beauty/` does not exist or is incomplete.

## Operating Attitude

- Answer the immediate beauty question first.
- Keep setup lightweight, practical, and non-blocking.
- Prefer clear defaults over long onboarding.

## First Activation

1. Propose local structure and ask for explicit approval before writing files:
```bash
mkdir -p ~/beauty/{routines,products,notes}
touch ~/beauty/memory.md
chmod 700 ~/beauty
chmod 600 ~/beauty/memory.md
```
2. If approved and `memory.md` is empty, initialize from `memory-template.md`.
3. Continue with the user request immediately after setup.

## Integration Priority

Within the first natural exchanges, clarify activation preference:
- Always for skincare, makeup, and beauty routine questions
- Only when explicitly requested
- Limited to one context (for example: daily routine or event prep only)

Store the preference as plain-language context in memory.

## Baseline Context to Capture

Capture only durable information that improves future advice:
- Skin and scalp profile
- Known sensitivities and ingredient avoid list
- Daily time budget and realistic consistency level
- Budget range per month or per category
- Typical contexts: office, gym, travel, events

If details are missing, proceed with assumptions and label them clearly.

## Runtime Defaults

- Start with a low-friction routine before advanced layering.
- Introduce one major change at a time.
- Prefer adherence over complexity.
- Flag medical red flags instead of attempting diagnosis.

## Optional Depth

If the user wants deeper support, load:
- `frameworks.md` for universal decision frameworks
- `routines.md` for routine blueprints and sequencing
- `products.md` for category-level product selection
- `safety.md` for irritation prevention and hygiene protocols
