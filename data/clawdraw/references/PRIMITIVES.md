# Primitives Reference

75 primitives organized into 10 categories (34 built-in + 41 community). All primitives return an array of stroke objects.

Common optional parameters (available on most primitives unless noted):
- `color` (string): Hex color, default `#ffffff`
- `brushSize` (number): Brush width 3-100
- `opacity` (number): Stroke opacity 0.01-1.0
- `pressureStyle` (string): One of `default`, `flat`, `taper`, `taperBoth`, `pulse`, `heavy`, `flick`

---

## Shapes (6 built-in + 3 community)

### circle
Smooth circle with slight organic wobble.
**Produces:** A single closed ring with subtle random wobble on the radius (~4%), giving it a hand-drawn feel rather than a mathematically perfect circle. Drawn as one continuous loop. Looks like a freehand circle.
**Approx. size:** Diameter = 2 x `radius` (default 150, so ~300 units across). Fits in a `radius`-wide bounding box from center.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number, required): Radius, 1-500

### ellipse
Rotated oval.
**Produces:** A closed oval outline, similar to `circle` but with independent horizontal and vertical radii. Supports rotation. No wobble -- cleaner than circle. Single continuous loop.
**Approx. size:** Bounding box = 2 x `radiusX` wide by 2 x `radiusY` tall (defaults 170 x 110, so ~340 x 220 units), then rotated.
- `cx`, `cy` (number, required): Center
- `radiusX` (number, required): Horizontal radius, 1-500
- `radiusY` (number, required): Vertical radius, 1-500
- `rotation` (number): Rotation in degrees

### arc
Partial circle arc.
**Produces:** An open curved line segment tracing part of a circle between two angles. Unlike `circle`, it does not close -- just a smooth arc. Useful for partial borders, eyebrows, smiles, or rainbow shapes.
**Approx. size:** Spans up to 2 x `radius` (default 150) depending on the angular range. A 180-degree arc spans the full diameter.
- `cx`, `cy` (number, required): Center
- `radius` (number, required): Radius, 1-500
- `startAngle` (number, required): Start angle in degrees
- `endAngle` (number, required): End angle in degrees

### rectangle
Rectangle outline.
**Produces:** A closed four-sided outline (just the border, not filled). Single stroke connecting the four corners. Supports rotation. Clean geometric lines.
**Approx. size:** Exactly `width` x `height` (defaults 300 x 200 units), centered on (cx, cy).
- `cx`, `cy` (number, required): Center
- `width` (number, required): Width, 2-1000
- `height` (number, required): Height, 2-1000
- `rotation` (number): Rotation in degrees

### polygon
Regular N-sided polygon.
**Produces:** A closed outline of a regular polygon (equilateral triangle at sides=3, hexagon at sides=6, etc.). Single stroke. Clean straight edges connecting vertices evenly spaced around a circle.
**Approx. size:** Fits inside a circle of the given `radius` (default 150, so ~300 units across).
- `cx`, `cy` (number, required): Center
- `radius` (number, required): Radius, 1-500
- `sides` (number, required): Number of sides, 3-24
- `rotation` (number): Rotation in degrees

### star
N-pointed star.
**Produces:** A closed star shape alternating between outer points and inner valleys. Single stroke. Classic star outline (like a sheriff's badge or Christmas star). The ratio of `innerR` to `outerR` controls how spiky vs. stubby the points are.
**Approx. size:** Fits inside a circle of `outerR` (default 150, so ~300 units across).
- `cx`, `cy` (number, required): Center
- `outerR` (number, required): Outer radius, 5-500
- `innerR` (number, required): Inner radius, 2 to outerR-1
- `points` (number, required): Number of points, 3-20
- `rotation` (number): Rotation in degrees (default -90)

### hexGrid
Hexagonal honeycomb grid.
**Produces:** A tessellation of flat-topped hexagons arranged in a honeycomb pattern, clipped to a circular boundary. Each hex is an individual closed stroke. Resembles a beehive, chicken wire, or hex-based game board.
**Approx. size:** Circular footprint with diameter = `size` (default 1000 units). Number of hexes depends on `hexSize` (default 100 -- roughly 10 hexes across the diameter).
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Overall radius (default 1000)
- `hexSize` (number): Single hex radius (default 100)

### gear
Mechanical cog wheel with trapezoidal teeth, inner hub, and radial spokes.
**Produces:** A detailed mechanical gear outline with three components: the outer tooth profile (trapezoidal teeth with sloped sides and flat tops), an inner hub circle, and radial spokes connecting hub to tooth roots. Also includes a small center hole. Palette colors are distributed around the gear by angle. Generates 30-50+ strokes.
**Approx. size:** Diameter = 2 x `outerRadius` (default 170, so ~340 units). Hub sits at ~60% of outer radius.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `outerRadius` (number): Outer tooth radius, 30-500 (default 170)
- `teeth` (number): Number of teeth, 6-40 (default 16)
- `hubRadius` (number): Inner hub radius, 10-outerRadius*0.6 (default 60)
- `toothDepth` (number): Tooth depth ratio, 0.1-0.5 (default 0.25)
- `palette` (string): Color palette name

### schotter
Georg Nees Schotter — grid of squares with increasing random disorder.
**Produces:** A grid of small square outlines that become progressively more disordered from top to bottom. Top rows are neatly aligned; bottom rows are randomly rotated and displaced. Recreates Georg Nees' 1968 generative art piece "Schotter". Each square is a separate stroke. Noise-based randomness makes the pattern deterministic.
**Approx. size:** `width` x `height` (default 300 x 300 units). Generates up to `cols` x `rows` strokes (default 12 x 12 = 144, capped at 200).
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Grid width, 50-800 (default 280)
- `height` (number): Grid height, 50-800 (default 280)
- `cols` (number): Number of columns, 2-30 (default 12)
- `rows` (number): Number of rows, 2-30 (default 12)
- `decay` (number): Disorder increase rate, 0.1-3 (default 1.0)
- `palette` (string): Color palette name

---

## Organic (7 built-in + 5 community)

### lSystem
L-System branching structures.
**Produces:** Branching plant-like structures grown from an L-system grammar. **fern**: delicate recursive fronds branching left and right, resembling a fern leaf. **tree**: thick trunk splitting into Y-shaped branches with sub-branches at each level. **bush**: dense, bushy form with branches on both sides of every segment. **coral**: fan coral shape with asymmetric branching, wider and more irregular. **seaweed**: long swaying strands with one-sided branches, like kelp. Each branch is a separate stroke; palette colors map from trunk (t=0) to leaf tips (t=1). Up to 200 strokes.
**Approx. size:** Grows upward from (cx, cy) by default (rotation=-90). Height roughly `scale` x 50-100 units (default scale=3). `fern` at scale=3 spans ~200-400 units tall.
- `cx`, `cy` (number, required): Base position
- `preset` (string, required): One of `fern`, `tree`, `bush`, `coral`, `seaweed`
- `iterations` (number): Iteration count (max varies by preset, 1-5)
- `scale` (number): Size multiplier, 0.1-5
- `rotation` (number): Starting rotation in degrees
- `palette` (string): Color palette name (`magma`, `plasma`, `viridis`, `turbo`, `inferno`)

### flower
Multi-petal flower with filled center spiral.
**Produces:** A multi-petal flower where each petal is drawn as 3 gradient-colored bands (base color to tip color) forming a teardrop shape radiating from center. The center is a spiral that coils inward. Looks like a daisy or simple botanical illustration. Generates 3 strokes per petal + 1 center stroke.
**Approx. size:** Diameter = 2 x `petalLength` (default 60, so ~120 units across). Center fills `centerRadius` (default 20).
- `cx`, `cy` (number, required): Center
- `petals` (number): Number of petals, 3-20 (default 8)
- `petalLength` (number): Length, 10-300 (default 60)
- `petalWidth` (number): Width, 5-150 (default 25)
- `centerRadius` (number): Center size, 5-100 (default 20)
- `petalColor` (string): Petal hex color
- `centerColor` (string): Center hex color

### leaf
Single leaf with midrib and veins.
**Produces:** A single botanical leaf shape with three components: the leaf outline (a smooth pointed oval), a central midrib line from base to tip, and alternating diagonal veins branching off the midrib. The outline traces up one side and back down the other. Looks like a simple hand-drawn leaf.
**Approx. size:** `length` x `width` (defaults 200 x 80 units). Grows from (cx, cy) in the `rotation` direction.
- `cx`, `cy` (number, required): Base position
- `length` (number): Leaf length, 10-300 (default 80)
- `width` (number): Leaf width, 5-150 (default 30)
- `rotation` (number): Rotation in degrees
- `veinCount` (number): Number of veins, 0-12 (default 4)

### vine
Curving vine with small leaves along a bezier path.
**Produces:** A single curved vine stem (quadratic bezier) with small 3-point leaf sprigs alternating left and right along its length. The main stem is one stroke; each leaf is an additional stroke. Simple and lightweight -- good for connecting elements or adding organic borders.
**Approx. size:** Spans from (startX, startY) to (endX, endY) with `curveAmount` controlling how far the arc bows sideways (default 50 units offset).
- `startX`, `startY` (number, required): Start position
- `endX`, `endY` (number, required): End position
- `curveAmount` (number): Curve intensity, 0-300 (default 50)
- `leafCount` (number): Number of leaves, 0-20 (default 5)

### spaceColonization
Space colonization algorithm producing root/vein/lightning patterns.
**Produces:** An organic branching network grown from a seed point toward randomly placed attractor points. The algorithm iteratively extends branches toward the nearest attractors, killing attractors when reached. Result looks like tree roots, leaf venation, lightning bolts, or blood vessel networks depending on parameters. Each root-to-leaf path is a separate stroke. Palette colors map by branch depth.
**Approx. size:** `width` x `height` (default 300 x 300 units). Growth starts from bottom-center of the area. Up to 200 strokes.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 20-600 (default 200)
- `height` (number): Area height, 20-600 (default 200)
- `density` (number): Attractor density, 0.1-1 (default 0.5)
- `stepLength` (number): Growth step length, 2-30 (default 8)
- `palette` (string): Color palette name

### mycelium
Organic branching mycelium network.
**Produces:** A radial network of thin, wiggly branching filaments growing outward from multiple seed points near the center. Branches randomly fork and wander with random-walk angles, getting thinner at deeper levels. Resembles fungal mycelium, neural dendrites, or river deltas. Each filament segment is a separate stroke. Palette colors map by branch depth.
**Approx. size:** Circular footprint within `radius` (default 180 units, so ~360 units across). Generates up to 200 strokes depending on `density`.
- `cx`, `cy` (number, required): Center
- `radius` (number): Spread radius, 20-500 (default 150)
- `density` (number): Branch density, 0.1-1 (default 0.5)
- `branchiness` (number): Branch probability, 0.1-1.0 (default 0.5)
- `palette` (string): Color palette name

### barnsleyFern
Barnsley Fern IFS fractal.
**Produces:** A classic Barnsley fern rendered as connected point segments with central stem and recursive sub-fronds. `lean` tilts left/right; `curl` controls frond curl. Looks like a real fern leaf silhouette.
**Approx. size:** Height ~`scale` x 10 (default scale=30, so ~300 units tall). Width ~60% of height. Centered on (cx, cy).
- `cx`, `cy` (number, required): Center
- `scale` (number): Size scale, 3-100 (default 20)
- `iterations` (number): Point count, 500-8000 (default 2000)
- `lean` (number): Lean angle in degrees, -30 to 30
- `curl` (number): Curl factor, 0.5-1.5 (default 1.0)
- `palette` (string): Color palette name

### vineGrowth
Recursive branching vine tendrils with curl noise and leaf loops at tips.
**Produces:** A radial vine system where multiple root branches grow outward from center, recursively splitting into sub-branches perturbed by curl noise. Tips terminate with small looping leaf shapes. Thicker at roots, thinner at tips. Palette colors map by recursion depth. Up to 200 strokes.
**Approx. size:** Circular footprint within `radius` (default 150, so ~300 units across).
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Growth radius, 20-500 (default 150)
- `branches` (number): Root branch count, 2-16 (default 8)
- `maxDepth` (number): Max recursion depth, 1-8 (default 5)
- `palette` (string): Color palette name

### phyllotaxisSpiral
Sunflower-inspired golden angle spiral pattern.
**Produces:** A circular arrangement of small dot-circles placed at the golden angle (137.508 degrees), spiraling outward like sunflower seeds. Each dot is a small 8-point circle stroke. Palette colors gradient from center to edge. One stroke per dot, up to 200.
**Approx. size:** Circular footprint within `radius` (default 170, so ~340 units across).
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Outer radius, 10-500 (default 150)
- `numPoints` (number): Number of seed points, 10-500 (default 200)
- `dotSize` (number): Dot scale relative to spacing, 0.1-1.0 (default 0.4)
- `palette` (string): Color palette name

### lichenGrowth
Cyclic cellular automaton rendered as colored cell blocks.
**Produces:** A 14x14 grid of small colored rectangles driven by a cyclic cellular automaton. Cells advance to the next state when a neighbor has that state, creating wave-like color fronts. Resembles lichen growth, coral, or abstract pixelated art. Each cell is a closed rectangle stroke. Palette maps states to colors.
**Approx. size:** `width` x `height` (default 300 x 300 units). Always 14x14 cells = 196 strokes max.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 300)
- `height` (number): Pattern height, 50-800 (default 300)
- `states` (number): Number of cell states, 3-16 (default 6)
- `iterations` (number): Simulation iterations, 1-100 (default 30)
- `palette` (string): Color palette name

### slimeMold
Physarum slime mold agent simulation with trail visualization.
**Produces:** A network of overlapping agent trails from a Physarum-style simulation. Agents sense pheromone trails and turn toward higher concentrations, self-organizing into interconnected vein-like networks. Each agent path is a stroke. Resembles slime mold transport networks or neural pathways. Trails wrap at edges.
**Approx. size:** `width` x `height` (default 300 x 300 units). Up to 180 agent trails, 200 strokes total.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Field width, 50-600 (default 300)
- `height` (number): Field height, 50-600 (default 300)
- `agents` (number): Number of agents, 10-500 (default 100)
- `steps` (number): Simulation steps, 10-200 (default 60)
- `sensorDist` (number): Sensor distance, 1-30 (default 9)
- `sensorAngle` (number): Sensor angle in radians, 0.1-1.5 (default 0.5)
- `turnSpeed` (number): Turn speed in radians, 0.05-1.0 (default 0.3)
- `decayRate` (number): Trail decay rate, 0.5-0.99 (default 0.9)
- `palette` (string): Color palette name

### dla
Diffusion-Limited Aggregation fractal growth pattern.
**Produces:** A dendritic branching tree radiating from center, mimicking DLA. 8-12 main trunks split into progressively shorter sub-branches with random-walk wiggle. Resembles frost crystals, mineral dendrites, lightning, or coral. `stickiness` controls branch wiggle. Up to 200 strokes.
**Approx. size:** Circular footprint within `radius` (default 170, so ~340 units across). Branches may extend to ~1.2x radius.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Growth radius, 20-400 (default 140)
- `particles` (number): Max branches, 10-500 (default 100)
- `stickiness` (number): Branch wiggle, 0-1 (default 0.8)
- `palette` (string): Color palette name

---

## Fractals (10 community)

### mandelbrot
Mandelbrot set escape-time fractal with contour lines.
**Produces:** Concentric contour rings around the classic cardioid-and-bulb Mandelbrot shape. Uses marching squares on a smooth escape-time field to extract contour lines at evenly spaced iteration thresholds. Lines get denser near the set boundary, revealing seahorse valleys and spiral arms. Each contour level produces chained polyline strokes. Palette colors map across contour levels.
**Approx. size:** `width` x `height` (default 300 x 300 units). Up to 200 strokes.
- `cx` (number, required): Center X on canvas
- `cy` (number, required): Center Y on canvas
- `width` (number): Pattern width, 50-800 (default 300)
- `height` (number): Pattern height, 50-800 (default 300)
- `maxIter` (number): Max iterations, 10-200 (default 40)
- `zoom` (number): Zoom level, 0.1-100 (default 1)
- `centerReal` (number): Real center in complex plane (default -0.5)
- `centerImag` (number): Imaginary center (default 0)
- `contours` (number): Number of contour levels, 2-20 (default 8)
- `palette` (string): Color palette name

### juliaSet
Julia set escape-time fractal with marching-squares contour lines.
**Produces:** Contour lines from a Julia set escape-time field. Unlike Mandelbrot, the c constant is fixed and every pixel iterates z^2+c from its own starting position. Default c=(-0.7, 0.27015) produces a connected, swirly fractal boundary. Contour lines are extracted via marching squares and chained into polyline strokes. Different c values produce dramatically different shapes (dendrites, spirals, disconnected dust).
**Approx. size:** `width` x `height` (default 300 x 300 units). Up to 200 strokes.
- `cx` (number, required): Center X on canvas
- `cy` (number, required): Center Y on canvas
- `width` (number): Pattern width, 50-800 (default 300)
- `height` (number): Pattern height, 50-800 (default 300)
- `cReal` (number): Real part of c constant (default -0.7)
- `cImag` (number): Imaginary part of c constant (default 0.27015)
- `maxIter` (number): Max iterations, 10-200 (default 50)
- `contours` (number): Number of contour levels, 2-20 (default 10)
- `palette` (string): Color palette name

### apollonianGasket
Recursive circle packing using Descartes circle theorem.
**Produces:** Nested circles filling the gaps between tangent circles using the Descartes circle theorem. Starts with a large bounding circle containing three mutually tangent circles (Soddy configuration), then recursively fills every triangular gap with smaller tangent circles. Resembles a fractal foam or bubble packing. Each circle is a closed polygon stroke. Palette colors map by circle size (smaller = further in gradient).
**Approx. size:** Circular footprint within `radius` (default 150, so ~300 units across). Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Outer circle radius, 10-500 (default 150)
- `maxDepth` (number): Recursion depth, 1-6 (default 4)
- `minRadius` (number): Minimum circle radius to draw, 1-50 (default 3)
- `palette` (string): Color palette name

### dragonCurve
Heighway dragon fractal curve via L-system iterative fold sequence.
**Produces:** The classic Heighway dragon curve -- a space-filling fractal path generated by repeatedly folding a strip of paper. At high iterations (12+), the curve densely fills a roughly triangular region with a crinkly, self-similar boundary. Split into colored segments along the curve. The path makes only 90-degree turns, creating a grid-aligned but visually complex pattern.
**Approx. size:** Fits within `size` x `size` (default 300 x 300 units), auto-centered. Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Fit size, 50-800 (default 300)
- `iterations` (number): Fold iterations, 1-16 (default 12)
- `palette` (string): Color palette name

### kochSnowflake
Koch snowflake fractal via recursive edge subdivision.
**Produces:** The classic Koch snowflake -- an equilateral triangle whose edges are recursively subdivided with outward-pointing equilateral bumps. At depth 4+, the boundary becomes a highly detailed, self-similar coastline-like curve surrounding a star shape. Split into colored segments around the perimeter.
**Approx. size:** Circumscribed within `radius` (default 170, so ~340 units across). The snowflake extends slightly beyond the initial triangle. Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Circumscribed radius, 20-500 (default 150)
- `depth` (number): Recursion depth, 1-6 (default 4)
- `palette` (string): Color palette name

### sierpinskiTriangle
Recursive Sierpinski triangle fractal.
**Produces:** The classic Sierpinski triangle -- an equilateral triangle recursively subdivided where corner sub-triangles are kept and center sub-triangles are left empty (Sierpinski void). At depth 4, produces 81 small triangles (3^4) with the characteristic self-similar hole pattern. Each leaf triangle is a closed 4-point stroke with slight wobble. Palette colors map by distance from center.
**Approx. size:** Fits within `radius` (default 170, so ~340 units across). Generates up to 250 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Distance from center to vertex, 10-500 (default 120)
- `depth` (number): Recursion depth, 1-5 (default 4)
- `palette` (string): Color palette name

### kaleidoscopicIfs
Chaos game iterated function system with kaleidoscopic symmetry.
**Produces:** A kaleidoscopic fractal pattern generated by running a chaos game with random affine transforms, then folding points into N-fold rotational symmetry. Produces intricate snowflake-like or mandala-like patterns that differ based on `symmetry` order and number of transforms. Higher symmetry (12-24) produces more mandala-like patterns; lower (2-4) produces more chaotic scatter. Points are grouped into stroke segments colored by angle from center.
**Approx. size:** Fits within `radius` (default 150, so ~300 units across). Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Fit radius, 20-500 (default 150)
- `symmetry` (number): Fold symmetry order, 2-24 (default 6)
- `transforms` (number): Number of IFS transforms, 2-8 (default 3)
- `iterations` (number): Chaos game iterations, 100-50000 (default 8000)
- `numStrokes` (number): Stroke segments, 1-200 (default 80)
- `palette` (string): Color palette name

### penroseTiling
Penrose P3 tiling via Robinson triangle subdivision with golden ratio.
**Produces:** An aperiodic Penrose P3 tiling -- a tessellation of thick and thin rhombuses (rendered as triangles) that never repeats but has 5-fold rotational symmetry. Starts with a decagonal arrangement of Robinson triangles and recursively subdivides using golden ratio edge splits. Each triangle is a closed stroke with slight wobble. Palette colors mix by distance from center and triangle type. Triangles are shuffled so the 200-stroke cap samples from all areas.
**Approx. size:** Circular footprint within `radius` (default 170, so ~340 units across). Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Outer radius of initial decagon, 10-500 (default 170)
- `depth` (number): Subdivision depth, 1-6 (default 4)
- `palette` (string): Color palette name

### hyperbolicTiling
Poincare disk model hyperbolic tiling using Mobius transformations.
**Produces:** A {p,q} hyperbolic tiling inside a Poincare disk -- regular p-gons meeting q at each vertex, arranged in hyperbolic space where tiles shrink toward the boundary. The central polygon is drawn at full size, with reflected copies filling outward via Mobius transformations. Tiles near the disk edge appear compressed. Requires (p-2)(q-2)>4 for hyperbolic geometry. Each polygon is a closed stroke. Palette colors map by recursion depth.
**Approx. size:** Circular footprint within `radius` (default 170, so ~340 units across). Up to 200 strokes.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Poincare disk radius, 10-500 (default 170)
- `p` (number): Polygon sides, 3-8 (default 5)
- `q` (number): Polygons meeting at each vertex, 3-8 (default 4)
- `maxDepth` (number): Recursion depth, 1-4 (default 3)
- `palette` (string): Color palette name

### viridisVortex
A recursive fractal spiral with noise warp and pure viridis gradient.
**Produces:** Multiple logarithmic spiral arms radiating from center, each decorated with perpendicular "rib" strokes. Noise warp distorts the arms organically, giving a nautilus-shell-meets-galaxy look. Always uses the viridis colour ramp (purple → teal → yellow) regardless of palette parameter.
**Approx. size:** Fills roughly `size` x `size` canvas units (default 2000x2000). Arms extend to ~`size/2` from center.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Size of the vortex, 500-10000 (default 2000)
- `arms` (number): Number of spiral arms, 3-20 (default 7)
- `turns` (number): Number of turns per arm, 1-10 (default 4)
- `warp` (number): Amount of noise warp (default 100)
- `palette` (string): Color palette (default viridis)

---

## Flow (5 built-in + 5 community)

### flowField
Perlin noise flow field with particle traces.
**Produces:** A dense field of short curved streamlines following a Perlin noise vector field. Resembles wind patterns, ocean currents, or magnetic field lines. Traces are seeded on a grid and advected through the noise, giving an organic directional flow.
**Approx. size:** Fills the `width` x `height` area (default 200x200 canvas units) centered at (`cx`, `cy`).
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 20-600 (default 200)
- `height` (number): Area height, 20-600 (default 200)
- `noiseScale` (number): Noise frequency, 0.001-0.1 (default 0.01)
- `density` (number): Particle density, 0.1-1 (default 0.5)
- `segmentLength` (number): Step size, 1-30 (default 5)
- `traceLength` (number): Steps per trace, 5-200 (default 40)
- `palette` (string): Color palette name

### spiral
Archimedean spiral.
**Produces:** A single continuously expanding Archimedean spiral from `startRadius` outward to `endRadius`. Smooth, evenly-spaced coils with slight hand-drawn wobble. Split into multiple strokes for palette colouring.
**Approx. size:** Fits within a circle of `endRadius` (default 100 canvas units) centered at (`cx`, `cy`).
- `cx`, `cy` (number, required): Center
- `turns` (number): Number of turns, 0.5-20 (default 3)
- `startRadius` (number): Inner radius, 0-500 (default 5)
- `endRadius` (number): Outer radius, 1-500 (default 100)

### lissajous
Lissajous harmonic curves.
**Produces:** Smooth, looping figure-eight and pretzel-like curves created by two perpendicular sine waves. Higher frequency ratios produce more complex knot patterns. Includes slight random wobble for a hand-drawn feel. Split into coloured segments for palette mapping.
**Approx. size:** Fits within `radius` x `radius` (default 100x100 canvas units) centered at (`cx`, `cy`).
- `cx`, `cy` (number, required): Center
- `freqX` (number): X frequency, 1-20 (default 3)
- `freqY` (number): Y frequency, 1-20 (default 2)
- `phase` (number): Phase offset in degrees (default 0)
- `amplitude` (number): Size, 10-500 (default 80)
- `palette` (string): Color palette name

### strangeAttractor
Strange attractor chaotic orbits.
**Produces:** Chaotic orbital paths traced via Euler integration. **Lorenz** (default): the classic butterfly/figure-eight double-lobe attractor. **Aizawa**: a torus-like orbit that wobbles between two poles. **Thomas**: a slowly converging, loopy 3D path projected to 2D. Each trace is split into coloured segments.
**Approx. size:** Scaled to fit within `radius` (default 100 canvas units) from center. Lorenz fills a wider horizontal span; aizawa and thomas are more compact.
- `cx`, `cy` (number, required): Center
- `type` (string): One of `lorenz`, `aizawa`, `thomas` (default `lorenz`)
- `iterations` (number): Point count, 100-5000 (default 2000)
- `scale` (number): Display scale, 0.1-50 (default 5)
- `timeStep` (number): Integration step, 0.001-0.02 (default 0.005)
- `palette` (string): Color palette name

### spirograph
Spirograph (epitrochoid) geometric curves.
**Produces:** Classic spirograph (epitrochoid) patterns — looping petal curves formed by a point on a smaller circle rolling around a larger one. The ratio `outerR/innerR` determines the number of cusps; `penDist` controls petal width. Multiple overlapping spirographs with slight parameter shifts create layered, mandala-like designs.
**Approx. size:** Fits within roughly `outerR + innerR + penDist` from center (default ~170 canvas units radius).
- `cx`, `cy` (number, required): Center
- `outerR` (number): Outer ring radius, 10-500 (default 100)
- `innerR` (number): Inner ring radius, 5-400 (default 40)
- `traceR` (number): Trace point distance, 1-400 (default 30)
- `revolutions` (number): Number of revolutions, 1-50 (default 10)
- `startAngle` (number): Starting angle in degrees
- `palette` (string): Color palette name

### cliffordAttractor
Clifford strange attractor with sinusoidal dynamics.
**Produces:** A dense, swirling cloud of orbital paths from the Clifford attractor (xx27 = sin(a*y) + c*cos(a*x), yx27 = sin(b*x) + d*cos(b*y)). Creates intricate butterfly-wing or vortex patterns depending on parameters a-d. Multiple traces coloured by angle from center give a rainbow-whorl effect with palette.
**Approx. size:** Auto-scaled to fit within `radius` (default 170 canvas units) from center.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Fit radius, 20-500 (default 150)
- `a` (number): Parameter a (default -1.4)
- `b` (number): Parameter b (default 1.6)
- `c` (number): Parameter c (default 1.0)
- `d` (number): Parameter d (default 0.7)
- `numPoints` (number): Iteration count, 100-50000 (default 8000)
- `numStrokes` (number): Stroke segments, 1-200 (default 80)
- `palette` (string): Color palette name

### hopalongAttractor
Martin hopalong map producing intricate orbital scatter patterns.
**Produces:** Scattered point-cloud orbits from the hopalong map (xx27 = y - sign(x)*sqrt(|b*x - c|), yx27 = a - x). Creates delicate, lace-like symmetric scatter patterns with bilateral symmetry. Each trace starts from a random offset and iterates thousands of steps, producing fine filamentary structures.
**Approx. size:** Auto-scaled to fit within `radius` (default 170 canvas units) from center.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Fit radius, 20-500 (default 150)
- `a` (number): Parameter a (default 1.1)
- `b` (number): Parameter b (default 2.0)
- `c` (number): Parameter c (default 0.5)
- `numPoints` (number): Iteration count, 100-50000 (default 5000)
- `numStrokes` (number): Stroke segments, 1-200 (default 80)
- `palette` (string): Color palette name

### doublePendulum
Chaotic double pendulum trajectories via RK4 Lagrangian integration.
**Produces:** Multiple chaotic pendulum traces — smooth curves that start orderly then diverge wildly as chaos takes over. Each trace begins with a slightly different initial angle, so nearby traces rapidly separate. Resembles tangled yarn or seismograph output. Uses RK4 integration for physically accurate dynamics.
**Approx. size:** Traces stay within `radius` (default 170 canvas units) from center, since pendulum arm lengths are scaled to fit.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Fit radius, 20-500 (default 150)
- `angle1` (number): Initial angle 1 in degrees (default 120)
- `angle2` (number): Initial angle 2 in degrees (default 150)
- `steps` (number): Simulation steps, 100-5000 (default 1500)
- `traces` (number): Number of pendulum traces, 1-40 (default 5)
- `palette` (string): Color palette name

### orbitalDynamics
Gravitational orbit trails around attractor points.
**Produces:** Curving orbital paths of particles launched tangentially past gravitational attractor points. Creates swooping, comet-like trails that bend around attractors — resembling planetary orbits or gravity-well visualisations. Multiple particles with different launch positions produce a web of intersecting trajectories.
**Approx. size:** Orbits stay within `radius` (default 170 canvas units) from center. Attractor points are placed within inner 60% of radius.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): System radius, 20-500 (default 150)
- `numBodies` (number): Number of orbiting bodies, 2-30 (default 8)
- `attractors` (number): Number of gravity attractors, 1-5 (default 2)
- `steps` (number): Simulation steps per body, 50-2000 (default 300)
- `gravity` (number): Gravitational strength, 50-5000 (default 500)
- `palette` (string): Color palette name

### gielisSuperformula
Layered Gielis superformula curves (supershapes) with parametric variation.
**Produces:** Layered closed curves from the Gielis superformula — produces shapes ranging from rounded polygons to star-like and pinched forms depending on parameters m, n1, n2, n3. Multiple layers with slightly varied parameters create nested, flower-like or sea-urchin-like outlines. Each layer is a separate palette-coloured stroke.
**Approx. size:** Each layer fits within `radius` (default 170 canvas units) from center. Layers nest concentrically.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Outer radius, 10-500 (default 120)
- `m` (number): Rotational symmetry order (default 5)
- `n1` (number): Exponent n1 (default 0.3)
- `n2` (number): Exponent n2 (default 0.3)
- `n3` (number): Exponent n3 (default 0.3)
- `a` (number): Parameter a (default 1)
- `b` (number): Parameter b (default 1)
- `layers` (number): Number of concentric layers, 1-30 (default 8)
- `pointsPerLayer` (number): Points per layer, 50-500 (default 200)
- `palette` (string): Color palette name

---

## Noise (9 community)

### voronoiNoise
Organic Voronoi cell noise pattern with hand-drawn edges.
**Produces:** A rectangular field of irregular organic cells whose boundaries are traced as short chained strokes with hand-drawn wobble. Seed points scatter randomly, then a grid scan detects where the nearest-seed assignment changes and clusters boundary points into polyline strokes. Resembles cracked mud, giraffe spots, or leaf venation. Boundaries are colored by distance from center when using a palette.
**Approx. size:** `width` x `height` (default 300x300 units). Produces up to 200 strokes. Safe spacing: `width` + 50 between instances.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 300)
- `height` (number): Pattern height, 50-800 (default 300)
- `numCells` (number): Number of seed points, 5-80 (default 25)
- `wobble` (number): Hand-drawn wobble amount, 0-1 (default 0.3)
- `palette` (string): Color palette name

### voronoiCrackle
Voronoi cell edge pattern using F2-F1 distance field with marching squares contours.
**Produces:** Concentric contour lines that tightly follow Voronoi cell boundaries, creating a crackle-glaze or shattered-glass look. The F2-F1 distance field peaks sharply at cell edges and falls to zero at cell centers, so contour lines concentrate along boundaries. Multiple contour levels produce nested edge outlines with slight wobble. Palette colors map across contour levels from inner to outer.
**Approx. size:** `width` x `height` (default 350x350 units). Produces up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `numCells` (number): Number of seed points, 3-80 (default 25)
- `contours` (number): Number of contour levels, 1-10 (default 4)
- `palette` (string): Color palette name

### voronoiGrid
Voronoi-style cellular grid generated by edge scanning.
**Produces:** A large-scale Voronoi tessellation where cell boundaries are marked by short vertical strokes (5-15 units tall) at each edge-detected grid point, creating a textured mosaic effect. Scans a 15-unit grid and draws a tiny vertical stroke wherever two Voronoi cells meet. Looks like a pointillist or cross-stitch rendering of cell walls. Colors are sampled from the palette based on each cell's random seed value.
**Approx. size:** `width` x `height` (default 1000x1000 units -- much larger than other noise primitives). Can go up to 5000x5000. Produces many strokes due to the large grid scan. Safe spacing: `width` + 100.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Width, 100-5000 (default 1000)
- `height` (number): Height, 100-5000 (default 1000)
- `cells` (number): Number of cells, 5-100 (default 20)
- `palette` (string): Color palette (default magma)

### worleyNoise
Worley (cellular) noise with F1/F2 distance field contour extraction.
**Produces:** Contour lines extracted from a Worley (cellular) distance field, with three distinct visual modes. **F1** produces rounded bubble-like contours centered on each seed point (concentric rings around cells). **F2** produces more complex overlapping ring patterns with secondary distance influence. **F2minusF1** (default) highlights sharp cell boundaries similar to voronoiCrackle, with contour lines tightly following the ridges between cells. All modes use marching squares for smooth contour extraction with slight wobble.
**Approx. size:** `width` x `height` (default 350x350 units). Seed points are distributed in a sunflower spiral pattern. Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `numCells` (number): Number of Worley seed points, 3-50 (default 15)
- `mode` (string): Distance mode: `F1`, `F2`, or `F2minusF1` (default `F2minusF1`)
- `contours` (number): Number of contour levels, 2-12 (default 5)
- `palette` (string): Color palette name

### domainWarping
Inigo Quilez nested noise domain warping with organic contour extraction.
**Produces:** Flowing, swirling contour lines from noise-warped noise fields. The domain (input coordinates) is repeatedly distorted by noise before final evaluation, creating organic swirling and folding patterns that resemble marble veins, smoke currents, or topographic maps of alien terrain. More warp octaves produce increasingly complex nested distortions. Contour lines are extracted via marching squares with slight wobble.
**Approx. size:** `width` x `height` (default 350x350 units). The swirling patterns stay within bounds. Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `scale` (number): Noise scale, 0.001-0.05 (default 0.008)
- `warpStrength` (number): Warp displacement strength, 10-200 (default 80)
- `warpOctaves` (number): Number of warp octaves, 1-4 (default 2)
- `contours` (number): Number of contour levels, 2-12 (default 5)
- `palette` (string): Color palette name

### turingPatterns
Multi-octave noise turbulence with sin() modulation for organic stripe and spot contours.
**Produces:** Organic stripe and spot patterns resembling animal markings (zebra stripes, leopard spots, fingerprints). Multi-octave noise turbulence is passed through `sin(turbulence * complexity * PI)`, creating periodic banding that wraps around noise features. Low complexity (1-2) produces broad flowing stripes; high complexity (5-8) produces dense labyrinthine patterns with many parallel contour lines. Contour extraction via marching squares with slight wobble.
**Approx. size:** `width` x `height` (default 350x350 units). Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `scale` (number): Noise scale, 0.005-0.2 (default 0.03)
- `complexity` (number): Sin modulation complexity, 1-8 (default 3)
- `contours` (number): Number of contour levels, 2-12 (default 5)
- `palette` (string): Color palette name

### reactionDiffusion
Turing-inspired reaction-diffusion contour patterns (spots, stripes, labyrinths).
**Produces:** Organic blob and labyrinth contour lines approximating reaction-diffusion systems using two-octave layered Perlin noise. Smaller `scale` values produce larger, rounder blobs (coral-like); larger values produce tighter, more intricate labyrinthine patterns. Multiple contour levels create nested outlines around each blob. Visually similar to turingPatterns but without the sin() banding -- produces smoother, more amorphous organic shapes.
**Approx. size:** `width` x `height` (default 300x300 units). Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 300)
- `height` (number): Pattern height, 50-800 (default 300)
- `scale` (number): Noise scale — smaller = larger blobs, 0.005-0.2 (default 0.04)
- `contours` (number): Number of contour levels, 2-12 (default 5)
- `palette` (string): Color palette name

### grayScott
Gray-Scott PDE reaction-diffusion simulation with contour extraction.
**Produces:** True PDE-simulated reaction-diffusion contour patterns. Runs a discrete Gray-Scott simulation on a 60x60 grid seeded with 5 spots, then bilinearly upsamples the V-chemical concentration and extracts contour lines via marching squares. Default feed/kill rates (0.037/0.06) produce branching coral or worm-like structures. Adjusting feed/kill shifts between spots (low feed), stripes (balanced), and mitosis patterns (high feed). More iterations develop the pattern further -- 150 (default) shows early branching, 500 shows mature structures.
**Approx. size:** `width` x `height` (default 350x350 units). Internal simulation is always 60x60 cells mapped to output dimensions. Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `feed` (number): Feed rate, 0.01-0.1 (default 0.037)
- `kill` (number): Kill rate, 0.01-0.1 (default 0.06)
- `iterations` (number): Simulation iterations, 50-500 (default 150)
- `contours` (number): Number of contour levels, 2-12 (default 5)
- `palette` (string): Color palette name

### metaballs
Metaball implicit surface field with smooth blobby contour extraction.
**Produces:** Smooth, blobby organic contour lines from an implicit metaball field. Multiple balls with varying radii (30-90 units) are placed in a circular arrangement, and the sum of their inverse-square distance fields is contoured at multiple threshold levels. Nearby balls merge smoothly like liquid droplets, producing organic lava-lamp or amoeba shapes. Outer contours trace the merged silhouette; inner contours reveal individual ball centers. Slight wobble gives a hand-drawn quality.
**Approx. size:** `width` x `height` (default 350x350 units). Balls are distributed within the field area. Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 350)
- `height` (number): Pattern height, 50-800 (default 350)
- `numBalls` (number): Number of metaballs, 2-12 (default 5)
- `threshold` (number): Iso-surface threshold, 0.1-5 (default 1.0)
- `contours` (number): Number of contour levels, 2-12 (default 4)
- `palette` (string): Color palette name

---

## Simulation (3 community)

### gameOfLife
Conway's Game of Life cellular automaton with R-pentomino seed.
**Produces:** A snapshot of a cellular automaton after N generations, rendered as filled cell squares. Seeded with the classic R-pentomino (produces rich long-lived evolution) plus corner gliders. Live cells are drawn as small filled squares grouped into horizontal runs (one stroke per run). Cells are colored by birth generation when using a palette -- early cells one color, late cells another -- revealing the simulation's growth history.
**Approx. size:** `width` x `height` (default 300x300 units). Cell grid is `width/cellSize` x `height/cellSize` (default 60x60 cells at cellSize=5). Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Grid width in pixels, 50-800 (default 300)
- `height` (number): Grid height in pixels, 50-800 (default 300)
- `generations` (number): Simulation generations, 10-500 (default 200)
- `cellSize` (number): Cell size in pixels, 2-20 (default 5)
- `palette` (string): Color palette name

### langtonsAnt
Langton's Ant cellular automaton with emergent highway patterns.
**Produces:** The continuous trail path of a Langton's Ant simulation, split into colored stroke segments. The ant starts at the grid center and follows simple turn rules (right on white, left on black), producing initial chaotic scribbling that eventually gives way to a diagonal "highway" pattern (around step 10000+). The path is rendered as ~190 connected polyline strokes colored sequentially by palette. Resembles a dense tangled knot with an emergent diagonal streak.
**Approx. size:** `width` x `height` (default 280x280 units). Grid auto-sizes to fit the chaotic phase. Cell spacing scales to fill the canvas. Up to 200 strokes. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 280)
- `height` (number): Pattern height, 50-800 (default 280)
- `steps` (number): Simulation steps, 100-50000 (default 11000)
- `cellSize` (number): Cell size in pixels, 2-20 (default 4)
- `palette` (string): Color palette name

### waveFunctionCollapse
Simplified wave function collapse with pipe/maze tileset.
**Produces:** A procedural maze/pipe network generated by constraint propagation. A grid of tiles is collapsed one cell at a time, choosing from 13 tile types: horizontal pipes, vertical pipes, corners (NE/SE/SW/NW with curved arcs), T-junctions, crosses, and empty cells. Edge constraints ensure connected pipe segments. The result looks like a circuit board, plumbing diagram, or maze with curved corners. Each tile produces one stroke, colored by grid position via palette.
**Approx. size:** `width` x `height` (default 280x280 units). Grid is `width/tileSize` x `height/tileSize` (default ~11x11 tiles). One stroke per tile, up to 200. Safe spacing: `width` + 50.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Pattern width, 50-800 (default 280)
- `height` (number): Pattern height, 50-800 (default 280)
- `tileSize` (number): Tile size, 10-60 (default 25)
- `palette` (string): Color palette name

---

## Fills (6)

### hatchFill
Parallel line shading (hatching).
**Produces:** Evenly spaced parallel lines at a configurable angle, clipped to a rectangular area. Each line is one stroke. With `colorEnd` set, lines smoothly interpolate from `color` to `colorEnd` across the fill area, creating a gradient hatching effect. Looks like pencil shading or engraving crosshatch when combined with crossHatch. Lines extend to the full diagonal of the rectangle to ensure complete coverage at any angle.
**Approx. size:** `width` x `height` (default 300x300 units). Number of strokes depends on spacing (default 8 units apart, producing ~50 lines at default size). Up to 200 strokes. Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-600 (default 100)
- `height` (number): Area height, 10-600 (default 100)
- `angle` (number): Line angle in degrees (default 45)
- `spacing` (number): Line spacing, 2-50 (default 8)
- `colorEnd` (string): End color for gradient hatching

### crossHatch
Two-angle crosshatch shading (45 and -45 degrees).
**Produces:** Two overlapping sets of parallel lines at +45 and -45 degrees, creating a classic crosshatch shading pattern. Internally calls hatchFill twice and merges the results. Looks like etching or engraving shading. Denser spacing creates darker-looking areas.
**Approx. size:** `width` x `height` (default 300x300 units). Produces up to 200 strokes total (both directions combined). Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-600
- `height` (number): Area height, 10-600
- `spacing` (number): Line spacing, 2-50

### stipple
Random dot pattern fill.
**Produces:** Randomly scattered dots (tiny 3-point strokes) within a rectangular area, creating a stipple shading effect. Each dot is a single stroke consisting of three points forming a tiny triangle. Density controls how many dots are placed -- higher density fills the area more uniformly. Useful for texturing surfaces, creating pointillist shading, or adding grain to illustrations.
**Approx. size:** `width` x `height` (default 300x300 units). Number of dots controlled by `dotCount` (default ~25 at density=0.5). Up to 200 strokes. Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-600 (default 100)
- `height` (number): Area height, 10-600 (default 100)
- `density` (number): Dot density, 0.1-1 (default 0.5)
- `dotCount` (number): Exact dot count, 10-500

### gradientFill
Color gradient via parallel strokes with interpolated colors.
**Produces:** A smooth color gradient rendered as parallel thick strokes (default brushSize=10) with linearly interpolated colors from `colorStart` to `colorEnd`. Lines are clipped to the rectangular area and oriented perpendicular to the gradient angle. Creates a painterly wash effect with visible brush strokes rather than a pixel-perfect gradient. Number of lines depends on density (default ~10 lines at density=0.5).
**Approx. size:** `width` x `height` (default 300x300 units). Produces ~10-20 thick strokes. Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-600 (default 200)
- `height` (number): Area height, 10-600 (default 200)
- `colorStart` (string): Start color
- `colorEnd` (string): End color
- `angle` (number): Gradient angle in degrees
- `density` (number): Line density, 0.1-1 (default 0.5)

### colorWash
Seamless color wash fill using overlapping horizontal and vertical strokes.
**Produces:** A solid-looking color fill built from overlapping horizontal and vertical strokes with slight random jitter. The brush size auto-scales to fit ~10 strokes across the shorter dimension. Two passes (horizontal then vertical) create a woven crosshatch that appears as a uniform color wash at normal zoom. Opacity is reduced per pass (60% of specified opacity) so the overlap blends smoothly. Ideal as a background fill or shape coloring.
**Approx. size:** `width` x `height` (default 300x300 units). Produces up to 200 strokes (horizontal + vertical passes). Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-800 (default 200)
- `height` (number): Area height, 10-800 (default 200)
- `opacity` (number): Max opacity, 0.01-0.6 (default 0.35)

### solidFill
Solid color fill (alias for colorWash).
**Produces:** Identical output to colorWash -- a solid-looking color fill from overlapping horizontal and vertical strokes. This is a convenience alias. The `direction` parameter is reserved but currently unused.
**Approx. size:** Same as colorWash: `width` x `height` (default 300x300 units). Safe spacing: `width` + 20.
- `cx`, `cy` (number, required): Center
- `width` (number): Area width, 10-800
- `height` (number): Area height, 10-800
- `direction` (string): Unused, reserved

---

## Decorative (5 built-in + 3 community)

### border
Decorative border frame.
**Produces:** A rectangular frame outline drawn with one of four decorative patterns along each edge. **dots**: evenly spaced dot marks (~15 unit intervals). **dashes** (default): short line segments with gaps (12 unit dashes, 8 unit gaps). **waves**: smooth sinusoidal curves oscillating perpendicular to each edge (8 full wave cycles per edge). **zigzag**: sharp triangular zigzag lines along each edge. All four sides are drawn identically. Useful for framing artwork, certificates, or decorative panels.
**Approx. size:** `width` x `height` (default 300x200 units). The border itself has negligible thickness (just brush width). Interior is empty. Safe spacing: `width` + 30.
- `cx`, `cy` (number, required): Center
- `width` (number): Frame width, 20-800 (default 200)
- `height` (number): Frame height, 20-800 (default 200)
- `pattern` (string): One of `dots`, `dashes`, `waves`, `zigzag` (default `dashes`)
- `amplitude` (number): Wave/zigzag amplitude, 2-30 (default 8)

### mandala
Radially symmetric mandala pattern with wobble motifs.
**Produces:** Concentric rings of radially repeated motifs around a center point. Each ring draws `symmetry` copies of a petal-like wobble motif (sine-wave modulated radius) rotated evenly around the circle. The wobble and random variation give each petal a hand-drawn organic feel rather than perfect geometric symmetry. A tiny center dot marks the origin. Colors cycle through the provided array by ring. Looks like a traditional mandala or decorative rosette.
**Approx. size:** Circular footprint with diameter = 2 x `radius` (default 150, so ~300 units). The `complexity` rings are evenly spaced from center to `radius`. Safe spacing: `radius` * 2 + 30.
- `cx`, `cy` (number, required): Center
- `radius` (number): Overall radius, 10-500 (default 100)
- `symmetry` (number): Rotational folds, 3-24 (default 8)
- `complexity` (number): Number of concentric rings, 1-8 (default 3)
- `colors` (array): Array of hex color strings
- `wobbleAmount` (number): Motif wobble intensity, 0-0.5 (default 0.15)

### fractalTree
Recursive branching tree.
**Produces:** A binary branching tree growing upward from the base position. Each branch splits into two at the specified angle with slight random jitter on both angle and length, giving a natural organic look. Branch thickness decreases by ~25% per level. Palette colors map from trunk (t=0) to leaf tips (t=1). At default depth=5, produces ~63 branch strokes. Resembles a winter tree silhouette, lightning bolt, or river delta depending on angle and ratio settings.
**Approx. size:** Width is roughly 2 x `trunkLength` at default settings; height is approximately `trunkLength` x 2 (tree grows upward from cx,cy). The canopy spreads wider with larger `branchAngle`. Safe spacing: `trunkLength` * 3.
- `cx`, `cy` (number, required): Base position (trunk base)
- `trunkLength` (number): Trunk length, 10-300 (default 80)
- `branchAngle` (number): Branch spread in degrees, 5-60 (default 25)
- `depth` (number): Recursion depth, 1-8 (default 5)
- `branchRatio` (number): Length ratio per level, 0.4-0.9 (default 0.7)
- `palette` (string): Color palette name

### radialSymmetry
Complex mandala-like patterns with bezier motifs.
**Produces:** A complex mandala-like design with multiple concentric layers of radially repeated motifs. Each layer randomly selects one of three motif types: sinusoidal petal loops (smooth undulating arcs), spiky star points (alternating inner/outer radius), or decorative dots (small filled circles). The motif type varies per layer, creating visual variety. A tiny center dot anchors the design. Colors cycle through the provided array by layer. More complex than mandala, with greater visual diversity.
**Approx. size:** Circular footprint with diameter = 2 x `radius` (default 150, so ~300 units). `layers` concentric rings span from center to `radius`. Safe spacing: `radius` * 2 + 30.
- `cx`, `cy` (number, required): Center
- `radius` (number): Overall radius, 10-500 (default 120)
- `folds` (number): Rotational folds, 3-24 (default 8)
- `layers` (number): Concentric layers, 1-8 (default 4)
- `complexity` (number): Motif complexity, 1-5 (default 3)
- `colors` (array): Array of hex color strings

### sacredGeometry
Sacred geometry patterns.
**Produces:** One of four classic sacred geometry figures. **flowerOfLife** (default): overlapping circles in hexagonal arrangement -- center, 6 inner ring, 12 outer ring, plus bounding circle. **goldenSpiral**: logarithmic spiral growing by the golden ratio with nested golden rectangles. **metatronsCube**: 13 circles with every pair connected by lines, forming a dense web. **sriYantra**: 5 nested alternating triangles with 8 peripheral arcs and a center dot.
**Approx. size:** Circular footprint, diameter = 2 x `radius` (default 120, ~240 units). flowerOfLife extends slightly beyond `radius`. metatronsCube is densest. Safe spacing: `radius` * 2.5.
- `cx`, `cy` (number, required): Center
- `radius` (number): Overall radius, 10-500 (default 120)
- `pattern` (string): One of `flowerOfLife`, `goldenSpiral`, `metatronsCube`, `sriYantra`

### starburst
Radial sunburst with alternating triangular rays colored by angle.
**Produces:** A radial sunburst pattern with alternating long and short triangular wedge rays emanating from a central circle. Each ray is drawn as a closed triangular outline (base on inner circle, tip at outer radius). Even-numbered rays extend to full `outerRadius`; odd-numbered rays stop at `outerRadius * shortRatio`. An inner circle outline and an undulating outer boundary complete the design. Rays are individually colored by angle via palette. Resembles a retro sun logo, badge, or decorative medallion.
**Approx. size:** Circular footprint, diameter = 2 x `outerRadius` (default 185, ~370 units). Inner circle at `innerRadius` (default 30). Safe spacing: `outerRadius` * 2 + 30.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `outerRadius` (number): Outer ray radius, 30-500 (default 185)
- `rays` (number): Number of rays, 8-60 (default 24)
- `innerRadius` (number): Inner circle radius, 5-outerRadius*0.5 (default 30)
- `shortRatio` (number): Short ray length ratio, 0.3-0.9 (default 0.6)
- `palette` (string): Color palette name

### clockworkNebula
A cosmic scene with starfield, spirograph gears, and nebula dust.
**Produces:** A large-scale cosmic composition with four layered elements: (1) a dense starfield of tiny dot strokes with Gaussian-ish center concentration, (2) spirograph gear patterns (hypotrochoid curves) scattered randomly, (3) Lorenz attractor traces simulating nebula dust clouds, and (4) quadratic Bezier arc connections between nearby gears (like electric arcs). This is a very high-stroke-count primitive -- easily produces 1000+ strokes. Best used as a standalone large background piece.
**Approx. size:** `size` x `size` (default 3000x3000 units -- very large). Stars and dust spread across the full area. Gears are scattered within 80% of the area. Safe spacing: not recommended to place multiples close together.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Overall size, 500-10000 (default 3000)
- `stars` (number): Number of stars, 100-5000 (default 1000)
- `gears` (number): Number of spirograph gears, 1-50 (default 15)
- `dust` (number): Amount of nebula dust, 10-200 (default 50)
- `palette` (string): Color palette (default turbo)

### matrixRain
Digital rain effect with glitch offsets.
**Produces:** Vertical falling "rain" strokes resembling the digital rain from The Matrix. Each drop is a vertical polyline descending from a random position, with optional horizontal glitch offsets (random sideways jitter). Drop lengths vary from 50-250 units. Drops use the `flick` pressure style for a tapered trail effect. All drops share the same color (default bright green #00ff00) with varied opacity.
**Approx. size:** `width` x `height` (default 1000x1000 units). Drops are randomly scattered within the area. Safe spacing: `width` + 100.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `width` (number): Field width, 100-5000 (default 1000)
- `height` (number): Field height, 100-5000 (default 1000)
- `density` (number): Number of drops, 10-500 (default 50)
- `color` (string): Color (default #00ff00)
- `glitch` (number): Glitch probability, 0-1 (default 0.1)

---

## 3D (3 community)

### cube3d
Wireframe 3D cube with rotation and depth shading.
**Produces:** A wireframe 3D cube rendered as 12 edge strokes with perspective-free orthographic projection. Three-axis rotation (X, Y, Z) positions the cube in 3D space. Back-facing edges are drawn at 35% opacity for depth cues. Each edge has slight random wobble for a hand-drawn look. With `subdivisions` > 0, grid lines are added to each face (2 lines per subdivision per face = up to 60 extra strokes at subdivisions=5). Palette colors distribute across edges.
**Approx. size:** Bounding box is approximately 2 x `size` (default 120, ~240 units) in each direction, varying with rotation angles. Safe spacing: `size` * 2.5.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Cube half-size, 10-500 (default 120)
- `rotateX` (number): X rotation in degrees (default 25)
- `rotateY` (number): Y rotation in degrees (default 35)
- `rotateZ` (number): Z rotation in degrees (default 0)
- `subdivisions` (number): Edge subdivisions for wireframe detail, 0-5 (default 0)
- `palette` (string): Color palette name

### sphere3d
Wireframe 3D sphere with latitude and longitude lines.
**Produces:** A wireframe globe rendered as latitude circles and longitude arcs with 3D rotation and depth shading. Front-facing portions are drawn at full opacity; back-facing portions at 30% opacity, creating a see-through globe effect. Latitude lines are horizontal rings at evenly spaced polar angles. Longitude lines are vertical half-ellipses at evenly spaced azimuthal angles. Resembles a globe, wireframe planet, or armillary sphere.
**Approx. size:** Circular footprint, diameter = 2 x `radius` (default 120, ~240 units). The sphere is always exactly `radius` from center. Safe spacing: `radius` * 2 + 20.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `radius` (number): Sphere radius, 10-500 (default 120)
- `latLines` (number): Latitude lines, 2-20 (default 8)
- `lonLines` (number): Longitude lines, 3-24 (default 12)
- `rotateX` (number): X rotation in degrees, -90 to 90 (default 20)
- `rotateY` (number): Y rotation in degrees, -180 to 180 (default 30)
- `palette` (string): Color palette name

### hypercube
4D tesseract wireframe projected to 2D with rotation.
**Produces:** A 4D tesseract (hypercube) wireframe with 16 vertices and 32 edges, projected to 2D via perspective projection. Two rotation planes (XW and YZ) plus an additional XZ rotation create the classic "cube within a cube" tesseract appearance. Edges are colored by average w-depth via palette (inner cube vs outer cube). Small vertex dots mark each of the 16 projected corners. The perspective projection makes nearer (in w) parts larger, creating the iconic nested cube look.
**Approx. size:** Approximately 2 x `size` (default 150, ~300 units) in each direction, though perspective distortion can extend further. Safe spacing: `size` * 2.5.
- `cx` (number, required): Center X
- `cy` (number, required): Center Y
- `size` (number): Projection scale, 20-500 (default 150)
- `angleXW` (number): Rotation angle in XW plane in degrees (default 45)
- `angleYZ` (number): Rotation angle in YZ plane in degrees (default 30)
- `palette` (string): Color palette name

---

## Utility (5)

### bezierCurve
Smooth Catmull-Rom spline through control points.
**Produces:** A single smooth curve passing through all provided control points using Catmull-Rom spline interpolation (not Bezier despite the name). The curve passes exactly through each control point with smooth tangent continuity. 12 interpolated segments between each pair of control points. The resulting polyline is split into strokes if it exceeds the stroke point limit. Useful for drawing smooth freeform curves, paths, and outlines.
**Approx. size:** Determined entirely by the control point positions. The curve stays within the convex hull of the points (approximately). No default size.
- `points` (array, required): Array of `{x, y}` control points (max 20)

### dashedLine
Dashed line segment.
**Produces:** A straight line rendered as a series of short dash strokes with gaps between them. Each dash is a separate stroke. Useful for indicating borders, guidelines, fold lines, or movement paths. The total number of dashes depends on the line length and dash/gap lengths.
**Approx. size:** Spans from (startX, startY) to (endX, endY). Width is just the brush width. Up to 200 dashes.
- `startX`, `startY` (number, required): Start position
- `endX`, `endY` (number, required): End position
- `dashLength` (number): Dash length, 2-50 (default 10)
- `gapLength` (number): Gap length, 1-50 (default 5)

### arrow
Line with arrowhead.
**Produces:** A straight line stroke from start to end, plus a V-shaped arrowhead at the end point. The arrowhead is drawn as a single chevron stroke (two angled lines meeting at the endpoint). The arrowhead opening angle is about 144 degrees (0.8 * PI). Total: 2 strokes. Useful for diagrams, flowcharts, annotations, and directional indicators.
**Approx. size:** Spans from (startX, startY) to (endX, endY). Arrowhead extends `headSize` (default 15 units) behind the endpoint. Total: 2 strokes.
- `startX`, `startY` (number, required): Start position
- `endX`, `endY` (number, required): End position (arrowhead location)
- `headSize` (number): Arrowhead size, 3-60 (default 15)

### strokeText
Draw text as single-stroke letterforms. Supports A-Z, 0-9, and basic punctuation.
**Produces:** Text rendered as single-stroke vector letterforms -- each character drawn with simple polyline strokes (1-3 strokes per character). Supports uppercase A-Z, digits 0-9, and punctuation (. , ! ? - : / '). Characters are monospaced with width = 0.7 x height and 0.15 x height spacing. Optional rotation rotates the entire text block around its center. Each character stroke is a separate stroke object.
**Approx. size:** Width = `text.length` x `charHeight` x 0.85. Height = `charHeight` (default 30 units). Centered on (cx, cy). Up to 200 strokes (~66 characters max at 3 strokes/char).
- `cx`, `cy` (number, required): Center of text
- `text` (string, required): Text to draw (max 40 chars, converted to uppercase)
- `charHeight` (number): Character height, 5-200 (default 30)
- `rotation` (number): Text rotation in degrees

### alienGlyphs
Procedural cryptic alien/AI glyphs.
**Produces:** A set of procedurally generated alien-looking glyphs, each composed of 2-4 random elements: vertical lines with lean, arcs/curves, dots, horizontal bars, zigzag paths, and small circles. Each glyph is unique and cryptic-looking. **line** (default): glyphs arranged in a horizontal row. **grid**: glyphs in a square grid layout. **scatter**: glyphs randomly scattered around the center. **circle**: glyphs evenly spaced around a ring. Useful for alien writing, decorative symbols, mysterious inscriptions, or sci-fi UI elements.
**Approx. size:** Depends on arrangement. Line: width = `count` x `glyphSize` x 1.4. Grid: square ~sqrt(count) x `glyphSize` x 1.4. Circle: ring diameter = `count` x `glyphSize` x 1.4 / PI. Each glyph occupies roughly `glyphSize` x `glyphSize`. Up to 200 strokes.
- `cx`, `cy` (number, required): Center
- `count` (number): Number of glyphs, 1-20 (default 8)
- `glyphSize` (number): Glyph size, 5-100 (default 25)
- `arrangement` (string): One of `line`, `grid`, `scatter`, `circle` (default `line`)
