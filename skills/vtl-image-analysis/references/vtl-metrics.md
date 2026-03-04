# VTL Metric Reference

Full mathematical definitions for the five VTL compositional coordinates.
This document is for reference — the agent instructions live in SKILL.md.

Framework: https://github.com/rusparrish/Visual-Thinking-Lens
Author: Russell Parrish — https://artistinfluencer.com

---

## Core Architecture

VTL treats composition as a **gradient-field problem**, not an object-recognition
problem. Given an input image I(x,y):

1. Convert to grayscale luminance
2. Normalize to [0, 1]
3. Compute Sobel gradient magnitude field
4. Derive **adaptive mass mask** from percentile band of gradient magnitude

High gradient magnitude = edges, contrast boundaries, texture transitions.
These are treated as **visual mass** — the substrate for all measurements.

**The mask is not semantic.** It does not identify objects. It identifies
structural activity in the pixel field.

### Frozen Preprocessing Constants

| Parameter | Value | Purpose |
|-----------|-------|---------|
| TARGET_MAX_SIDE | 1536px | Canonical working size |
| GRAD_LOW_PCT | 85.0 | Lower percentile of mass band |
| GRAD_HIGH_PCT | 97.0 | Upper percentile of mass band |
| EDGE_MARGIN_PX | 2 | Border guard (artifact suppression) |
| R_V_ABSOLUTE_THRESH | 0.15 | Absolute gradient threshold for void ratio |

Any change to preprocessing constants constitutes a new device version and
breaks cross-image comparability.

---

## Metric 1: Δx,y — Placement Offset

**Definition:** Normalized centroid distance from frame center on each axis.

**Computation:**
```
mass_mask = pixels in [P85, P97] gradient band, excluding edge margin
x_centroid = mean(x-coordinates of mask pixels)
Δx = (x_centroid - (frame_width - 1) / 2) / frame_width
Δy = (y_centroid - (frame_height - 1) / 2) / frame_height
```

**Output range:** [-0.5, +0.5] on each axis

**Interpretation:**
- Δx = 0 → centroid at horizontal center
- Δx > 0 → centroid right of center
- Δx < 0 → centroid left of center
- |Δx| > 0.15 → meaningful displacement
- Batch variance < 0.05 → compositional monoculture signal

**Empirical note:** Sora attractor coordinates cluster at Δx ≈ 0.38–0.45 in
off-center tests, while reverting to Δx ≈ 0.02 under neutral prompting
regardless of semantic content variation.

---

## Metric 2: rᵥ — Void Ratio

**Definition:** Fraction of frame where gradient magnitude falls below an
absolute threshold. Measures gradient sparsity.

**Computation:**
```
rᵥ = 1.0 - (count of pixels where gmag ≥ 0.15) / total_pixel_count
```

**Key distinction from mass_fraction:** rᵥ uses an absolute threshold
(contrast-sensitive by design). mass_fraction uses percentile-based masking
(contrast-invariant). They measure different things.

**Output range:** [0.0, 1.0]

**Interpretation:**
- rᵥ > 0.85 → gradient-quiet field (smooth surfaces, minimal structure)
- rᵥ < 0.65 → gradient-active field (textured, dense edges)
- rᵥ correlates ≈ -0.97 with gradient_floor_85 empirically

**Cross-engine warning:** Always report rᵥ alongside gradient_floor_85
(85th percentile gradient value). Different engines have different baseline
activation levels; rᵥ alone is ambiguous cross-engine.

---

## Metric 3: ρᵣ — Packing Density

**Definition:** Ratio of mass pixel count to convex hull area, scaled ×100.
Measures how densely mass fills its own bounding geometry.

**Computation:**
```
pts = (x, y) coordinates of all mass mask pixels
hull = ConvexHull(pts)
ρᵣ = 100 × (len(pts) / hull.volume)   # .volume = 2D polygon area in scipy
```

**Note:** In scipy's ConvexHull, `.volume` = polygon area and `.area` =
perimeter in 2D. Use `.volume` for the area calculation.

**Output range:** Approximately [0, 100], relative interpretation

**Interpretation:**
- Low ρᵣ → scattered elements, large empty convex hull
- High ρᵣ → dense, compressed mass
- Combined with rᵥ: distinguishes "quiet because sparse" vs "quiet because smooth"

---

## Metric 4: G3 — Curvature Torque

**Source:** VCLI-G (Visual Cognitive Load Index — Geometric), G3 component.
Not a kernel metric. Measures directional tension and perceptual load.

**Definition:** Variance of signed curvature κ along image contours, plus
inflection point density.

**Computation:**
```
gray_smooth = gaussian_filter(gray, σ=1.0)
contours = find_contours(gray_smooth, level=gray_smooth.mean())

for each contour with len ≥ 9:
    smooth x,y with Savitzky-Golay (window=9, poly=2)
    dx = gradient(xs), dy = gradient(ys)
    ddx = gradient(dx), ddy = gradient(dy)
    κ = (dx·ddy - dy·ddx) / (dx² + dy²)^1.5

k_var = var(concat all κ values)
infl_density = total_sign_changes / total_contour_length
```

**Output:**
- `k_var` — curvature variance (spread of directional pressure)
- `infl_density` — inflection points per unit path length

**Interpretation:**
- k_var < 0.5 → smooth, unresisted flow (LOW_TENSION flag)
- k_var > 2.0 → strong turbulence, high perceptual load
- AI defaults cluster toward k_var < 0.3 under neutral prompting
- High infl_density = many directional reversals = friction, recursion

---

## Metric 5: dRC — Radial Compliance Delta (RCA-2)

**Source:** Dual-Center Radial Compliance Analyzer (RCA-2).
Most diagnostic metric for detecting AI compositional default behavior.

**Definition:** Difference between mass-centered and frame-centered radial
compliance. Indicates which coordinate system the image's radial structure
stabilizes around.

**Computation:**
```
# Build radial mass profiles in concentric rings (N=20)
profile_f = radial_mass_profile(gmag, center=frame_center)
profile_s = radial_mass_profile(gmag, center=mass_centroid)

# Fit ideal exponential decay to each profile
RC_f = 1 - JSD(profile_f, ideal_exponential_f)
RC_s = 1 - JSD(profile_s, ideal_exponential_s)

dRC = RC_s - RC_f
```

Where JSD = Jensen-Shannon divergence between actual profile and fitted
exponential decay ideal.

**Radial eligibility:** RC_s is not independently meaningful if the mass
centroid is within ~3% of frame dimensions from the frame center. In this
case, report as "dual-center" rather than a dRC value.

**Output range:** [-1.0, +1.0]

**Classification:**
| dRC | Label |
|-----|-------|
| < -0.06 | Frame-dominant (radial collapse — AI default) |
| -0.06 to +0.06 | Neutral |
| > +0.06 | Mass-dominant (subject-anchored) |
| centroid ≈ frame center | Dual-center |

**Why this matters:** AI models exhibit a strong default behavior of
organizing radial structure around the frame center regardless of where
the semantic subject is placed. A prompt may successfully shift a subject
off-center while the underlying radial geometry snaps back to frame-center
compliance. dRC < -0.06 reveals this reversion.

**Steering note:** Specifying subject position explicitly
("place the subject at the upper-left third") is more reliably effective
than style instructions ("use off-center composition"). The model anchors
radial decay to mass position when given a coordinate.

---

## Framework Context

VTL metrics are a coordinate system, not a quality score. They locate an
image in compositional space. The diagnostic power is in **distribution
analysis across batches**, not individual image values.

**Core finding from empirical testing (600+ images, Sora / MidJourney /
OpenArt):** Semantically diverse prompts map to structurally identical
coordinates. AI models exhibit measurable compositional priors — attractor
basins that persist regardless of prompt content. VTL instruments this
decoupling between semantic intent and structural realization.

Full notebooks, data, and documentation:
https://github.com/rusparrish/Visual-Thinking-Lens
