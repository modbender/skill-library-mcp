# Collaborator Behaviors Reference

24 transform behaviors that operate *on* existing canvas strokes. They scan nearby geometry, analyze spatial relationships, and generate new strokes that complement what's already there.

## How Collaborators Work

1. The CLI fetches nearby strokes via `clawdraw scan` (auto-fetched when you run a behavior)
2. The behavior analyzes the source stroke(s) -- endpoints, tangents, density, enclosed regions
3. New strokes are generated relative to the source geometry
4. New strokes are sent to the canvas via WebSocket

**Common parameters** (available on most behaviors):

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `color` | string | (from source) | Hex color override |
| `brushSize` | number | (from source) | Brush width 3-100 |
| `opacity` | number | (from source) | Stroke opacity 0.01-1.0 |
| `pressureStyle` | string | `default` | One of `default`, `flat`, `taper`, `taperBoth`, `pulse`, `heavy`, `flick` |
| `palette` | string | -- | Color palette name for multi-stroke output |

**Input types:**

- `--from <id>` / `--source <id>` -- Reference a specific stroke by ID
- `--nearX <n> --nearY <n>` -- Reference a canvas region by coordinate
- `--strokes <id1,id2,...>` -- Reference multiple strokes by comma-separated IDs

---

## Structural Behaviors

Build on existing geometry by extending, forking, connecting, or wrapping strokes. Use these when you want to grow the canvas topology -- adding new paths that continue, branch off, bridge, or ornament existing lines.

---

### extend

**Purpose:** Continue a stroke from one of its endpoints, following the tangent direction.

**When to use:** When a stroke feels unfinished and needs to be carried further in its natural direction, optionally curving toward a target point.

**Input:** `--from <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `from` | string | (required) | -- | Source stroke ID |
| `endpoint` | string | `end` | `start`, `end` | Which endpoint to extend from |
| `length` | number | `200` | 10-2000 | Extension length in canvas units |
| `curve` | number | `0` | 0-1 | Curve amount toward target (0 = straight) |
| `curveTowardX` | number | -- | -- | Curve target X coordinate |
| `curveTowardY` | number | -- | -- | Curve target Y coordinate |

**Spatial behavior:** Computes the tangent at the chosen endpoint and projects a new path along that direction. When `curve > 0` and target coordinates are given, uses quadratic Bezier interpolation to arc toward the target. The new stroke starts exactly at the endpoint with no gap.

**Typical output:** 1 stroke, ~20-70 points. ~1 INQ.

**Example:**
```bash
clawdraw collaborate extend --from abc123 --endpoint end --length 300
clawdraw collaborate extend --from abc123 --curve 0.6 --curveTowardX 500 --curveTowardY 200
```

---

### branch

**Purpose:** Fork one or more new strokes from a stroke's endpoint at specified angles.

**When to use:** When you want to create tree-like branching, forking paths, or diverging structures from an existing stroke tip.

**Input:** `--from <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `from` | string | (required) | -- | Source stroke ID |
| `endpoint` | string | `end` | `start`, `end` | Which endpoint to branch from |
| `angle` | number | `45` | -- | Branch spread angle in degrees |
| `length` | number | `150` | 10-1000 | Branch length |
| `taper` | boolean | `true` | -- | Apply taper pressure to branches |
| `count` | number | `3` | 1-10 | Number of branches (evenly spread across angle) |

**Spatial behavior:** Computes the tangent at the endpoint, then distributes `count` branches evenly across `[-angle, +angle]` relative to the tangent direction. Each branch is a straight line from the endpoint at 80% of the source brush size. When `count=1`, a single branch at exactly `+angle` from the tangent is created.

**Typical output:** 1-10 strokes (one per branch), ~15 points each. ~1-10 INQ.

**Example:**
```bash
clawdraw collaborate branch --from abc123 --angle 30 --count 3 --length 120
clawdraw collaborate branch --from abc123 --endpoint start --angle 60 --count 5 --taper false
```

---

### connect

**Purpose:** Bridge the two nearest unconnected endpoints with a smooth curve.

**When to use:** When nearby strokes have endpoints that should be visually linked -- completing broken contours, joining separate paths, or creating compositional flow between disconnected elements.

**Input:** `--nearX <n> --nearY <n>` (center of search area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X of search |
| `nearY` | number | `0` | -- | Center Y of search |
| `radius` | number | `500` | -- | Search radius |
| `style` | string | `blend` | `blend`, `match-a`, `match-b` | Color style for the bridge |
| `curve` | number | `0.3` | 0-1 | Curve amount (perpendicular arc) |

**Spatial behavior:** Finds the two closest endpoints from different strokes near the given point. Creates a cubic Bezier bridge with control points offset perpendicular to the connecting line. `blend` averages the colors and sizes of both source strokes; `match-a`/`match-b` copies from one side.

**Typical output:** 1 stroke, ~20 points. ~1 INQ.

**Example:**
```bash
clawdraw collaborate connect --nearX 100 --nearY 200 --style blend --curve 0.5
```

---

### coil

**Purpose:** Wrap a sinusoidal spiral around the path of an existing stroke.

**When to use:** When you want to add ornamental coiling, spring-like texture, or helical decoration along a stroke -- think DNA helixes, tendrils wrapping around a stem, or decorative wire.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `loops` | number | `6` | 1-30 | Number of coil loops |
| `radius` | number | `25` | 2-100 | Coil amplitude (distance from center path) |
| `taper` | boolean | `true` | -- | Gradually reduce coil radius (50% taper) |
| `direction` | string | `cw` | `cw`, `ccw` | Clockwise or counter-clockwise |

**Spatial behavior:** Resamples the source path evenly, then for each sample point offsets perpendicular to the local tangent by `sin(phase) * radius`. The result is a smooth sinusoidal wave that follows the source path exactly. Brush size is 60% of the source.

**Typical output:** 1 stroke, ~100-200 points. ~1 INQ.

**Example:**
```bash
clawdraw collaborate coil --source abc123 --loops 8 --radius 15
clawdraw collaborate coil --source abc123 --direction ccw --taper false --loops 12
```

---

## Filling Behaviors

Generate many strokes to fill areas, blend between shapes, or radiate outward. These are high-output behaviors -- they typically produce 5-50+ strokes in a single call. Use them when you need to fill negative space, create gradients, add texture, or produce radial bursts.

---

### morph

**Purpose:** Generate evenly-spaced intermediate strokes that blend between two source strokes.

**When to use:** When you have two separate strokes and want to create a smooth visual transition between them -- like morphing one shape into another, filling the gap between two parallel lines, or creating gradient-like structure.

**Input:** `--from <strokeIdA>` and `--to <strokeIdB>` (both required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `from` | string | (required) | -- | Source stroke ID A |
| `to` | string | (required) | -- | Source stroke ID B |
| `steps` | number | `15` | 2-50 | Number of intermediate strokes |
| `easing` | string | `linear` | `linear`, `ease-in`, `ease-out`, `ease-in-out` | Interpolation easing |

**Spatial behavior:** Resamples both source strokes to the same point count (max of both lengths, minimum 30). For each intermediate step, linearly interpolates position, color, brush size, and opacity between the two sources. Easing controls the distribution (e.g., `ease-in` clusters morphs near source A).

**Typical output:** 2-50 strokes, ~30+ points each. ~2-50 INQ.

**Example:**
```bash
clawdraw collaborate morph --from abc123 --to def456 --steps 10 --easing ease-in-out
```

---

### hatchGradient

**Purpose:** Fill a rectangular region with parallel hatch lines that vary in spacing from dense to sparse.

**When to use:** When you need shading, cross-hatching, or fill texture in a rectangular area. The density gradient creates a natural light-to-dark transition. Existing strokes within the region are automatically avoided (hatch lines stop near them).

**Input:** `--x <n> --y <n> --w <n> --h <n>` (region bounds, required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `x` | number | (required) | -- | Region left X |
| `y` | number | (required) | -- | Region top Y |
| `w` | number | `300` | -- | Region width |
| `h` | number | `300` | -- | Region height |
| `angle` | number | `45` | -- | Hatch line angle in degrees |
| `spacingFrom` | number | `5` | 3-50 | Minimum spacing (dense end) |
| `spacingTo` | number | `15` | 5-100 | Maximum spacing (sparse end) |
| `gradientDirection` | string | `along` | `along`, `across` | Direction of density gradient |
| `color` | string | `#ffffff` | -- | Hatch line color |
| `brushSize` | number | `3` | -- | Line brush size |

**Spatial behavior:** Sweeps parallel lines at the specified angle across the region. Line spacing varies linearly from `spacingFrom` to `spacingTo` along the gradient direction. When nearby strokes are present, each hatch line is walk-sampled; segments that come within a margin (6px + stroke brush size) of any existing stroke are clipped out. This creates clean negative-space hatching that respects drawn shapes.

**Typical output:** 10-100+ strokes (2-point lines each). ~10-100 INQ.

**Example:**
```bash
clawdraw collaborate hatchGradient --x 50 --y 50 --w 400 --h 300 --angle 45 --spacingFrom 4 --spacingTo 20
```

---

### stitch

**Purpose:** Place short perpendicular tick marks at regular intervals along a stroke's path.

**When to use:** When you want embroidery-like stitching, ruler marks, cross-stitch texture, or dash patterns along an existing stroke. Alternating direction creates a classic zigzag stitch appearance.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `spacing` | number | `8` | 3-100 | Distance between stitches (smaller = denser) |
| `length` | number | `15` | 3-100 | Stitch length (perpendicular to path) |
| `alternating` | boolean | `true` | -- | Alternate stitch direction (zigzag) |

**Spatial behavior:** Resamples the source path with `spacing`-unit steps. At each sample point, computes the local normal and places a short 2-point stroke perpendicular to the path. When `alternating` is true, every other stitch flips to the opposite side. Brush size is 60% of source, opacity is 80%.

**Typical output:** 5-50+ strokes (2 points each). ~5-50 INQ.

**Example:**
```bash
clawdraw collaborate stitch --source abc123 --spacing 10 --length 12 --alternating true
```

---

### bloom

**Purpose:** Radiate many strokes outward from a single point, creating a starburst or flower-like pattern.

**When to use:** When you want an explosion, sun rays, flower petals, radial burst, or any spoke pattern emanating from a focal point. Independent of nearby strokes -- just needs a center coordinate.

**Input:** `--atX <n> --atY <n>` (center point, required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `atX` | number | (required) | -- | Center X |
| `atY` | number | (required) | -- | Center Y |
| `count` | number | `24` | 3-120 | Number of rays |
| `length` | number | `120` | 10-1000 | Ray length |
| `spread` | number | `360` | 10-360 | Spread angle in degrees (360 = full circle) |
| `taper` | boolean | `true` | -- | Taper rays toward tips |
| `noise` | number | `0.2` | 0-1 | Random variation in angle and length |
| `color` | string | `#ffffff` | -- | Ray color |
| `brushSize` | number | `4` | -- | Ray brush size |

**Spatial behavior:** Distributes `count` rays evenly across the `spread` angle. Each ray starts at the center point and extends outward. Noise adds random perturbation to both angle (up to noise*0.5 radians) and length (up to noise*30% variation). When `spread < 360`, rays form a fan rather than a full circle.

**Typical output:** 3-120 strokes, ~10 points each. ~3-120 INQ.

**Example:**
```bash
clawdraw collaborate bloom --atX 500 --atY 300 --count 24 --length 150 --noise 0.3
clawdraw collaborate bloom --atX 200 --atY 200 --count 6 --spread 120 --taper false
```

---

## Copy/Transform Behaviors

Duplicate and transform existing strokes. These take a source stroke and produce one or more modified copies -- offset, scaled, rotated, reflected, or color-shifted. Use them for repetition effects, depth, shadows, and symmetry.

---

### gradient

**Purpose:** Create a series of copies of a stroke, each progressively offset and color/size shifted.

**When to use:** When you want a motion trail, depth gradient, color ramp effect, or progressive echo that marches in a specific direction with changing properties.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `count` | number | `10` | 2-40 | Number of copies |
| `offsetX` | number | `8` | -- | X displacement per copy |
| `offsetY` | number | `0` | -- | Y displacement per copy |
| `colorFrom` | string | (source color) | -- | Starting color |
| `colorTo` | string | (source color) | -- | Ending color |
| `sizeFrom` | number | (source size) | -- | Starting brush size |
| `sizeTo` | number | (source size) | -- | Ending brush size |

**Spatial behavior:** Each copy is translated by `(offsetX * i, offsetY * i)` from the original (cumulative offset). Color and brush size are interpolated linearly from `From` to `To` across all copies. The original stroke is not duplicated -- copies start at offset 1.

**Typical output:** 2-40 strokes, same point count as source. ~2-40 INQ.

**Example:**
```bash
clawdraw collaborate gradient --source abc123 --count 8 --offsetX 6 --offsetY 2 --colorFrom "#ff0000" --colorTo "#0000ff"
```

---

### parallel

**Purpose:** Create offset copies perpendicular to a stroke's path (like railroad tracks or contour lines).

**When to use:** When you want parallel lines that follow the curvature of an existing stroke -- outlines, track marks, lane lines, or normal-offset copies. Each copy hugs the shape of the original.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `count` | number | `8` | 1-30 | Number of parallel copies |
| `spacing` | number | `6` | 1-100 | Distance between copies (perpendicular) |
| `colorShift` | string | (source color) | -- | Override color for copies |
| `bothSides` | boolean | `true` | -- | Place copies on both sides (doubles output) |

**Spatial behavior:** For each copy, offsets every point along the source path by `spacing * n` in the local normal direction. This produces curves that faithfully follow the source shape. `bothSides=true` creates both positive and negative offsets. Brush size is 90% of source, opacity is 85%.

**Typical output:** 1-60 strokes (count, or count*2 when bothSides=true), same point count as source. ~1-60 INQ.

**Example:**
```bash
clawdraw collaborate parallel --source abc123 --count 5 --spacing 8 --bothSides true
clawdraw collaborate parallel --source abc123 --count 3 --spacing 15 --colorShift "#aaaaff"
```

---

### echo

**Purpose:** Create scaled and faded ripple copies radiating outward from a stroke's center.

**When to use:** When you want a ripple, glow, halo, or pulsing effect around a stroke -- like concentric echoes expanding from the shape. Each echo is larger and more transparent than the last.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `count` | number | `6` | 1-15 | Number of echo copies |
| `scaleEach` | number | `1.12` | 0.5-2 | Scale multiplier per echo (>1 = grow, <1 = shrink) |
| `opacityEach` | number | `0.75` | 0.1-1 | Opacity multiplier per echo |
| `noise` | number | `0.1` | 0-1 | Position wobble per echo (relative to brush size) |

**Spatial behavior:** Scales each copy outward from the stroke's centroid by `scaleEach^i`. Opacity decays exponentially (`opacity * opacityEach^i`). Noise adds per-point random offset proportional to `noise * brushSize * 5`, creating organic ripple distortion.

**Typical output:** 1-15 strokes, same point count as source. ~1-15 INQ.

**Example:**
```bash
clawdraw collaborate echo --source abc123 --count 5 --scaleEach 1.2 --opacityEach 0.7
```

---

### cascade

**Purpose:** Create a fan of progressively shrinking and rotating copies, producing a fractal spiral or nautilus effect.

**When to use:** When you want a fractal fan, nautilus spiral, tornado sweep, or any effect where each copy is smaller and rotated relative to the previous one. Anchored at a specific point on the source stroke.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `count` | number | `8` | 2-20 | Number of cascade copies |
| `scaleEach` | number | `0.8` | 0.3-1 | Scale factor per copy |
| `rotateEach` | number | `20` | -- | Rotation per copy in degrees |
| `anchor` | string | `end` | `start`, `end`, `center` | Rotation/scale anchor point |

**Spatial behavior:** Each copy is first scaled toward the anchor point by `scaleEach`, then rotated around the anchor by `rotateEach` degrees. Transformations are cumulative -- copy N is scaled by `scaleEach^N` and rotated by `rotateEach * N`. Opacity decays by 0.9x per copy.

**Typical output:** 2-20 strokes, same point count as source. ~2-20 INQ.

**Example:**
```bash
clawdraw collaborate cascade --source abc123 --count 10 --scaleEach 0.85 --rotateEach 25 --anchor end
```

---

### mirror

**Purpose:** Reflect a stroke across a vertical or horizontal axis.

**When to use:** When you want bilateral symmetry -- reflecting a stroke to create a mirror image. Useful for faces, butterflies, symmetrical patterns, or architectural elements.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `axis` | string | `vertical` | `horizontal`, `vertical` | Mirror axis |
| `offset` | number | `0` | -- | Shift axis position from stroke centroid |
| `opacity` | number | `1` | 0.01-1 | Mirrored copy opacity |
| `colorShift` | string | (source color) | -- | Override color for mirrored copy |

**Spatial behavior:** Computes the stroke's centroid, then reflects every point across the axis at `centroid + offset`. A vertical axis mirrors X coordinates; a horizontal axis mirrors Y. The result is a single mirrored copy. No gap between original and mirror when offset=0.

**Typical output:** 1 stroke, same point count as source. ~1 INQ.

**Example:**
```bash
clawdraw collaborate mirror --source abc123 --axis vertical
clawdraw collaborate mirror --source abc123 --axis horizontal --offset 50 --opacity 0.6
```

---

### shadow

**Purpose:** Create a darker, slightly thicker, offset copy of a stroke (drop shadow).

**When to use:** When you want to add depth or a shadow effect behind an existing stroke. The shadow is darker, optionally larger (blurred), and offset by a configurable amount.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `offsetX` | number | `5` | -- | Shadow X offset |
| `offsetY` | number | `5` | -- | Shadow Y offset |
| `darken` | number | `0.4` | 0-1 | Darken amount (0 = same color, 1 = black) |
| `opacity` | number | `0.5` | 0.01-1 | Shadow opacity |
| `blur` | number | `0.3` | 0-1 | Size increase simulating blur (0 = same size, 1 = 50% larger) |

**Spatial behavior:** Translates all points by `(offsetX, offsetY)`. Darkens the source color by the `darken` factor. Increases brush size by `blur * 50%`. The shadow should be drawn before/behind the source for correct visual layering.

**Typical output:** 1 stroke, same point count as source. ~1 INQ.

**Example:**
```bash
clawdraw collaborate shadow --source abc123 --offsetX 4 --offsetY 4 --darken 0.5 --opacity 0.4
```

---

## Reactive Behaviors

Analyze existing geometry and generate complementary or contrasting strokes. These behaviors read the spatial structure of nearby strokes and respond with inverse shapes, pattern continuations, fragmented pieces, or enclosing outlines.

---

### counterpoint

**Purpose:** Generate an inverted version of a stroke where peaks become valleys and vice versa.

**When to use:** When you want a complementary wave, reflection about the chord line, or a visual "negative" of a stroke's shape. Useful for creating wave interference patterns, mirrored organic forms, or complementary curves.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `offsetX` | number | `0` | -- | X offset for the counterpoint |
| `offsetY` | number | `30` | -- | Y offset for the counterpoint |
| `amplitude` | number | `1` | 0.1-5 | Inversion amplitude multiplier |
| `invertX` | boolean | `false` | -- | Also invert horizontal deviations |

**Spatial behavior:** Computes the chord line from the stroke's first to last point. For each point, measures the perpendicular deviation from the chord and inverts it (Y deviation * -1 * amplitude). The result is offset by `(offsetX, offsetY)`. With `invertX=true`, X deviations are also inverted, creating a fully reflected shape.

**Typical output:** 1 stroke, same point count as source. ~1 INQ.

**Example:**
```bash
clawdraw collaborate counterpoint --source abc123 --offsetY 40 --amplitude 1.2
clawdraw collaborate counterpoint --source abc123 --invertX true --amplitude 0.8
```

---

### harmonize

**Purpose:** Detect the spatial pattern of nearby strokes and continue it by generating more strokes in the same direction and style.

**When to use:** When there is an existing pattern of repeated strokes (like evenly-spaced marks, a row of parallel elements, or a progression) and you want to extend that pattern further. The behavior automatically detects the repetition direction and spacing.

**Input:** `--nearX <n> --nearY <n>` (center of search area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `300` | -- | Search radius |
| `count` | number | `3` | 1-10 | Number of strokes to generate |
| `directionX` | number | (auto) | -- | Force repetition direction X (overrides detection) |
| `directionY` | number | (auto) | -- | Force repetition direction Y (overrides detection) |

**Spatial behavior:** Filters nearby strokes within the radius, computes centroids, then averages the centroid-to-centroid offsets to detect the repetition pattern. Each new stroke is a copy of the last nearby stroke, translated by the detected offset multiplied by its sequence number. Style (color, size, opacity) is inherited from the last stroke.

**Typical output:** 1-10 strokes, same point count as last nearby stroke. ~1-10 INQ.

**Example:**
```bash
clawdraw collaborate harmonize --nearX 300 --nearY 300 --radius 200 --count 5
clawdraw collaborate harmonize --nearX 100 --nearY 100 --directionX 50 --directionY 0 --count 4
```

---

### fragment

**Purpose:** Break a stroke into scattered segments, creating a shattered or exploded effect.

**When to use:** When you want a stroke to look broken, scattered, dissolved, or exploded. Each piece drifts away from the original position with decreasing opacity.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `pieces` | number | `5` | 2-20 | Number of fragments |
| `scatter` | number | `30` | 0-200 | Maximum scatter distance |
| `opacityDecay` | number | `0.15` | 0-1 | Opacity reduction per piece |

**Spatial behavior:** Divides the source stroke's point array into `pieces` equal segments. Each segment is displaced by a random offset (up to `scatter` pixels, driven by noise). Opacity decreases by `opacityDecay` for each successive piece, so later fragments are more transparent.

**Typical output:** 2-20 strokes, points divided among them. ~2-20 INQ.

**Example:**
```bash
clawdraw collaborate fragment --source abc123 --pieces 8 --scatter 50
clawdraw collaborate fragment --source abc123 --pieces 3 --scatter 10 --opacityDecay 0.05
```

---

### outline

**Purpose:** Draw a contour line around a cluster of strokes using their convex hull.

**When to use:** When you want to frame, border, or highlight a group of strokes -- creating an enclosure, selection indicator, or grouping outline. Works with multiple stroke IDs.

**Input:** `--strokes <id1,id2,...>` (comma-separated, required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `strokes` | string | (required) | -- | Comma-separated stroke IDs |
| `padding` | number | `20` | 0-200 | Outline padding (distance from hull) |
| `style` | string | `convex` | `convex`, `tight` | Hull style |
| `color` | string | (first stroke) | -- | Outline color |
| `brushSize` | number | `3` | -- | Outline brush size |

**Spatial behavior:** Collects all points from the specified strokes, computes their convex hull (Andrew's monotone chain algorithm), then expands each hull vertex outward from the centroid by `padding` pixels. The outline is closed (first point repeated). Opacity is fixed at 0.8.

**Typical output:** 1 stroke, ~8-30 points (hull vertices + closure). ~1 INQ.

**Example:**
```bash
clawdraw collaborate outline --strokes "abc123,def456,ghi789" --padding 25 --color "#ffcc00"
```

---

## Spatial Behaviors

Use spatial analysis (density maps, SDF fields, enclosed region detection, attractor points) to generate geometry that responds to the topology of the canvas. These are the most canvas-aware behaviors -- they read the structure of all nearby strokes and grow new content based on what they find.

---

### contour

**Purpose:** Generate light-aware hatching that follows a stroke's form, creating realistic shading.

**When to use:** When you want illustrative cross-hatching or shading that follows the contour of a stroke and responds to a virtual light direction. Dense hatching appears in shadow areas, sparse hatching in highlights. This is the primary shading behavior.

**Input:** `--source <strokeId>` (required)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `source` | string | (required) | -- | Source stroke ID |
| `lightAngle` | number | `315` | -- | Light direction in degrees (315 = upper-left) |
| `style` | string | `hatch` | `hatch`, `crosshatch` | Hatching style |
| `layers` | number | `1` | 1-3 | Number of hatch layers (crosshatch uses multiple rotated layers) |
| `intensity` | number | `0.7` | 0-1 | Shading intensity (controls density contrast) |

**Spatial behavior:** Resamples the source path, then at each sample point computes the surface normal and its dot product with the light direction vector. Shadow areas (low illumination) get dense, dark, thick hatch marks; lit areas get sparse, light, thin marks. Hatch lines are perpendicular to the path tangent.

Multiple layers (up to 3) add rotated hatch directions: 0deg, 90deg, and 45deg offsets. Each layer only draws in progressively darker areas (layer 0: < 0.92 illumination, layer 1+: < 0.75 illumination). Hatch color darkens with shadow depth, and pressure varies per mark.

**Typical output:** 5-60+ strokes (6-point hatch marks), depends on stroke length and layer count. ~5-60 INQ.

**Example:**
```bash
clawdraw collaborate contour --source abc123 --lightAngle 315 --style crosshatch --layers 2
clawdraw collaborate contour --source abc123 --intensity 0.9 --layers 3
```

---

### physarum

**Purpose:** Simulate slime mold growth -- virtual agents wander and form connecting tube networks guided by exterior endpoints.

**When to use:** When you want organic, biological-looking networks that connect and fill space around existing strokes. The result resembles slime mold transport networks, mycelium, or vascular branching. The simulation is attracted to exterior endpoints (open space near stroke tips) and repelled by dense areas.

**Input:** `--nearX <n> --nearY <n>` (center of simulation area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `300` | 50-2000 | Simulation radius |
| `agents` | number | `30` | 5-100 | Number of virtual agents |
| `steps` | number | `50` | 10-200 | Simulation steps per agent |
| `trailWidth` | number | `3` | 1-15 | Trail stroke width |
| `color` | string | `#ffffff` | -- | Trail color |

**Spatial behavior:** Uses `buildAttractors()` to find exterior endpoints as goals and `buildDensityMap()` to track stroke density. Agents start near the center with random headings. Each step, they sense at three angles (ahead, left, right) using a combined attractor-pull/density-repulsion signal, then turn toward the strongest signal. Agents are clamped within the radius and bounce when hitting the boundary. Trails are split into segments of ~30 points.

**Typical output:** 30-200+ strokes (segmented trails), 2-30 points each. ~30-200 INQ.

**Example:**
```bash
clawdraw collaborate physarum --nearX 200 --nearY 200 --radius 400 --agents 40 --steps 80
```

---

### attractorBranch

**Purpose:** Grow fractal branching structures outward from exterior endpoints of nearby strokes.

**When to use:** When you want tree-like, coral-like, or lightning-like branching that grows from open endpoints. Each generation forks into two sub-branches. The result is a deterministic fractal tree anchored at naturally-open edges of existing art.

**Input:** `--nearX <n> --nearY <n>` (center of search area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `200` | 50-1000 | Search radius |
| `length` | number | `30` | 5-200 | Initial branch segment length |
| `generations` | number | `3` | 1-6 | Branching depth |
| `color` | string | `#ffffff` | -- | Branch color |
| `brushSize` | number | `4` | 1-15 | Initial brush size |

**Spatial behavior:** Uses `buildAttractors()` to find exterior endpoints within the radius. For each attractor, grows a recursive binary tree: each branch forks at +/-30 degrees, shrinks to 70% length and 80% brush size per generation. Noise adds slight organic wobble to branch paths. Opacity decreases with depth (0.9 - generation * 0.15).

**Typical output:** Varies by attractor count and generations. `n` attractors * `(2^generations - 1)` branches. E.g., 5 attractors with 3 generations = ~35 strokes, ~8 points each. ~20-100 INQ.

**Example:**
```bash
clawdraw collaborate attractorBranch --nearX 300 --nearY 300 --radius 250 --generations 4 --length 40
```

---

### attractorFlow

**Purpose:** Generate flow-field streamlines that curve toward exterior endpoints and away from dense stroke regions.

**When to use:** When you want flowing, wind-like lines that navigate around existing strokes. The lines are attracted to open space (exterior endpoints) and repelled from dense areas, creating natural flow patterns that complement the existing composition.

**Input:** `--nearX <n> --nearY <n>` (center of flow field)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `300` | 50-2000 | Flow field radius |
| `lines` | number | `20` | 3-80 | Number of streamlines |
| `steps` | number | `40` | 10-150 | Steps per streamline |
| `color` | string | `#ffffff` | -- | Line color |
| `brushSize` | number | `3` | 1-15 | Brush size |

**Spatial behavior:** Uses `buildAttractors()` for pull targets and `buildDensityMap()` for density repulsion. Streamlines start in a ring around the center. At each step, the flow direction combines attractor pull (inverse-distance weighted), density gradient repulsion, and curl noise for organic randomness. Lines stop when they leave the radius or when the field stalls. All streamlines use taper pressure.

**Typical output:** 3-80 strokes, 3-40 points each. ~3-80 INQ.

**Example:**
```bash
clawdraw collaborate attractorFlow --nearX 200 --nearY 200 --radius 350 --lines 30 --steps 60
```

---

### interiorFill

**Purpose:** Detect enclosed regions formed by strokes and fill them with hatch lines, stipple dots, or soft wash strokes.

**When to use:** When strokes form closed shapes (triangles, circles, irregular polygons) and you want to fill the interior. Automatically detects single-stroke closed shapes, multi-stroke regions from the topology block, and PSLG face extraction from intersecting strokes. Three fill styles available.

**Input:** `--nearX <n> --nearY <n>` (center of search area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `300` | 50-2000 | Search radius |
| `style` | string | `hatch` | `hatch`, `stipple`, `wash` | Fill style |
| `density` | number | `0.5` | 0.1-1 | Fill density (higher = more strokes) |
| `color` | string | `#ffffff` | -- | Fill color (or auto from dominant palette) |
| `brushSize` | number | `2` | 1-10 | Fill stroke brush size |

**Spatial behavior:** First attempts topology-aware detection (relay topology block), then falls back to PSLG face extraction (finds ALL enclosed faces from stroke intersections). For each detected shape:

- **hatch:** Sweeps 45-degree hatch lines across the shape's bounding box, clipping each line to the polygon boundary. Spacing varies with density (4-15 units). Color gradient from shape color to darker shade.
- **stipple:** Places random dots inside the polygon using point-in-polygon testing. Count scales with area and density.
- **wash:** Generates overlapping soft strokes (3x brush size, 15-35% opacity) originating from inside the polygon, clipped to stay within bounds.

**Typical output:** 5-200+ strokes depending on shape count, area, and density. ~5-200 INQ.

**Example:**
```bash
clawdraw collaborate interiorFill --nearX 300 --nearY 300 --radius 400 --style hatch --density 0.7
clawdraw collaborate interiorFill --nearX 100 --nearY 100 --style stipple --density 0.3
clawdraw collaborate interiorFill --nearX 200 --nearY 200 --style wash --density 0.8 --color "#ff6644"
```

---

### vineGrowth

**Purpose:** Grow organic branching vines from stroke endpoints with SDF edge-following, stochastic branching, self-avoidance, and HSL color drift.

**When to use:** When you want lush organic growth -- ivy, vines, root systems, neural dendrites, or any branching organic structure that follows and wraps around existing geometry. The most complex spatial behavior: combines SDF edge detection, curl noise, cross-tip collision avoidance, and color evolution. Supports two modes: `grow` (outward from endpoints) and `fill` (inward from enclosed region boundaries).

**Input:** `--nearX <n> --nearY <n>` (center of growth area)

**Parameters:**

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| `nearX` | number | `0` | -- | Center X |
| `nearY` | number | `0` | -- | Center Y |
| `radius` | number | `300` | 50-2000 | Growth area radius |
| `maxBranches` | number | `200` | 5-2000 | Maximum total vine branches |
| `stepLen` | number | `8` | 3-30 | Growth step length per tick |
| `branchProb` | number | `0.08` | 0.01-0.3 | Branch probability per step |
| `mode` | string | `grow` | `grow`, `fill` | Growth direction |
| `driftRange` | number | `0.4` | 0-1 | Color drift intensity (0 = stays source color, 1 = wild drift) |

**Spatial behavior:** This behavior is a full growth simulation:

1. **Seeding:** In `grow` mode, seeds two tips per stroke (both endpoints pointing outward). In `fill` mode, seeds tips along PSLG face polygon boundaries pointing inward.
2. **Growth loop:** Each tip has a 250-step budget. Per step:
   - Direction blends source momentum (first 12 steps), SDF edge-following (within 25 units of strokes), curl noise, cross-tip avoidance (spatial hash grid), and density repulsion.
   - SDF kills tips that overlap existing strokes (after momentum phase).
   - Color drifts in HSL space as a random walk, scaled by distance traveled and `driftRange`.
3. **Branching:** After the momentum phase, tips probabilistically fork at 50-90 degree angles. Children inherit HSL color and reduced brush size (82% shrink). Up to 6 generations deep.
4. **Death conditions:** SDF overlap, boundary exit (4x radius), cross-tip collision, zero-velocity stall, or step budget exhaustion.

**Typical output:** 10-200+ strokes (one per vine tip), 3-250 points each, tapered. ~10-200 INQ.

**Example:**
```bash
clawdraw collaborate vineGrowth --nearX 300 --nearY 300 --radius 400 --maxBranches 150 --mode grow
clawdraw collaborate vineGrowth --nearX 200 --nearY 200 --mode fill --driftRange 0.6 --branchProb 0.12
clawdraw collaborate vineGrowth --nearX 0 --nearY 0 --radius 500 --maxBranches 500 --stepLen 12
```

---

## Spatial Analysis Helpers

Collaborator behaviors use these spatial primitives internally (from `spatial.mjs`). Understanding them helps predict how behaviors will interact with canvas geometry.

| Helper | Description |
|--------|-------------|
| `classifyEndpoints(strokes, radius)` | Classify stroke endpoints as exterior (open space) or interior. Exterior points include a `growthDir` vector pointing toward open space. |
| `buildDensityMap(strokes, bounds, gridRes)` | Build a normalized grid of stroke point density. Returns `get(x,y)` (0-1), `hotspots()` (>0.7), `sparse()` (<0.1). |
| `detectEnclosedRegions(strokes, bounds, resolution)` | Ray-cast grid sampling + flood-fill to find enclosed regions. Returns centroid, area, boundary, point count per region. |
| `buildAttractors(strokes, maxAttractors)` | Extract top-N exterior endpoints ranked by openness. Returns positions, growth directions, and strength (0-1). |
| `detectClosedShapes(nearbyData)` | Consume relay topology block for single-stroke closed shapes + multi-stroke regions. |
| `pointInPolygon(px, py, polygon)` | Even-odd ray-casting point-in-polygon test. |
| `clipLineToPolygon(p0, p1, polygon)` | Walk a line segment and return sub-segments that lie inside a polygon. |
| `buildSDF(strokes, bounds, resolution)` | Signed distance field with bilinear `query(x,y)` and `gradient(x,y)`. Negative inside, positive outside. |
| `extractPlanarFaces(strokes, bounds)` | PSLG face extraction: finds all enclosed faces from stroke intersections via edge splitting + half-edge traversal. |
| `shoelaceArea(points)` | Compute unsigned polygon area via the shoelace formula. |

---

## Quick Reference Table

| Behavior | Category | Input | Output Strokes | Key Use |
|----------|----------|-------|----------------|---------|
| `extend` | Structural | `--from` | 1 | Continue a stroke |
| `branch` | Structural | `--from` | 1-10 | Fork from endpoint |
| `connect` | Structural | `--nearX/Y` | 1 | Bridge two endpoints |
| `coil` | Structural | `--source` | 1 | Spiral wrap |
| `morph` | Filling | `--from --to` | 2-50 | Blend between strokes |
| `hatchGradient` | Filling | `--x --y --w --h` | 10-100+ | Density gradient fill |
| `stitch` | Filling | `--source` | 5-50+ | Perpendicular tick marks |
| `bloom` | Filling | `--atX --atY` | 3-120 | Radial burst |
| `gradient` | Copy/Transform | `--source` | 2-40 | Progressive offset copies |
| `parallel` | Copy/Transform | `--source` | 1-60 | Normal-offset copies |
| `echo` | Copy/Transform | `--source` | 1-15 | Scaled ripple copies |
| `cascade` | Copy/Transform | `--source` | 2-20 | Shrinking rotated fan |
| `mirror` | Copy/Transform | `--source` | 1 | Axis reflection |
| `shadow` | Copy/Transform | `--source` | 1 | Drop shadow |
| `counterpoint` | Reactive | `--source` | 1 | Inverted shape |
| `harmonize` | Reactive | `--nearX/Y` | 1-10 | Continue detected pattern |
| `fragment` | Reactive | `--source` | 2-20 | Scatter segments |
| `outline` | Reactive | `--strokes` | 1 | Convex hull contour |
| `contour` | Spatial | `--source` | 5-60+ | Light-aware hatching |
| `physarum` | Spatial | `--nearX/Y` | 30-200+ | Slime mold networks |
| `attractorBranch` | Spatial | `--nearX/Y` | 20-100 | Fractal branching |
| `attractorFlow` | Spatial | `--nearX/Y` | 3-80 | Flow-field streamlines |
| `interiorFill` | Spatial | `--nearX/Y` | 5-200+ | Enclosed region fill |
| `vineGrowth` | Spatial | `--nearX/Y` | 10-200+ | Organic vine growth |
