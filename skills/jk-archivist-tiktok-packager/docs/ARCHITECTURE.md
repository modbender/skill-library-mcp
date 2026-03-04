# Architecture

The skill bundle uses a hybrid runtime layout:

- `scripts/` provides stable command entrypoints.
- `src/node/` contains orchestration and contract assembly logic.
- `src/python/` contains deterministic rendering and slide verification.

## Flow

1. Run `node scripts/tiktok-intro-draft.mjs`.
2. Node writes `_slide_spec.json` and invokes `python3 scripts/render_slides_pillow.py`.
3. Python renders six deterministic PNG slides.
4. Node writes `caption.txt`.
5. Node invokes `python3 scripts/verify_slides.py` to validate outputs.
