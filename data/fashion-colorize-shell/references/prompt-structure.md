# Prompt Structure

This skill uses a fixed "colorized product render" template:

1. Task mode:
   - convert sketch to ecommerce-style render
2. Output frame:
   - single garment, front view, white background, centered
3. Material frame:
   - 3-layer laminated hardshell, taped seam feel, realistic shell texture
4. Structure preservation:
   - keep hood / CF zipper / slanted chest pocket lines / cuff adjusters / hem silhouette
5. Negative constraints:
   - no model, no scene, no text overlays, no technical multi-view board

Variant strategy for `--count`:

- v1: balanced
- v2: stronger commercial realism
- v3: stronger structure fidelity

Revision strategy:

- Feed previous best output as `--style-ref` and append explicit revision deltas in `--brief`.
- Keep revisions atomic (2-4 changes each round) for stable convergence.
