/**
 * Primitive registry — static imports from all category folders.
 *
 * Usage:
 *   import { getPrimitive, listPrimitives, getPrimitiveInfo } from './index.mjs';
 *
 *   const fn = getPrimitive('circle');
 *   const strokes = fn(0, 0, 100, '#ff0000', 5, 0.9);
 *
 *   const all = await listPrimitives();
 *   const info = await getPrimitiveInfo('fractalTree');
 */

// ---------------------------------------------------------------------------
// Built-in primitive imports (from category folders)
// ---------------------------------------------------------------------------

import * as basicShapes from './shapes/basic-shapes.mjs';
import * as organic from './organic/organic.mjs';
import * as flowAbstract from './flow/flow-abstract.mjs';
import * as fills from './fills/fills.mjs';
import * as decorative from './decorative/decorative.mjs';
import * as utility from './utility/utility.mjs';
import * as collaborator from './collaborator.mjs';

// ---------------------------------------------------------------------------
// Community primitive imports (static — organized by category)
// ---------------------------------------------------------------------------

// shapes
import * as hexGrid from './shapes/hex-grid.mjs';
import * as gear from './shapes/gear.mjs';
import * as schotter from './shapes/schotter.mjs';

// organic
import * as vineGrowth from './organic/vine-growth.mjs';
import * as phyllotaxisSpiral from './organic/phyllotaxis-spiral.mjs';
import * as lichenGrowth from './organic/lichen-growth.mjs';
import * as slimeMold from './organic/slime-mold.mjs';
import * as dla from './organic/dla.mjs';

// fractals
import * as mandelbrot from './fractals/mandelbrot.mjs';
import * as juliaSet from './fractals/julia-set.mjs';
import * as apollonianGasket from './fractals/apollonian-gasket.mjs';
import * as dragonCurve from './fractals/dragon-curve.mjs';
import * as kochSnowflake from './fractals/koch-snowflake.mjs';
import * as sierpinskiTriangle from './fractals/sierpinski-triangle.mjs';
import * as kaleidoscopicIfs from './fractals/kaleidoscopic-ifs.mjs';
import * as penroseTiling from './fractals/penrose-tiling.mjs';
import * as hyperbolicTiling from './fractals/hyperbolic-tiling.mjs';
import * as viridisVortex from './fractals/viridis-vortex.mjs';

// flow
import * as cliffordAttractor from './flow/clifford-attractor.mjs';
import * as hopalongAttractor from './flow/hopalong-attractor.mjs';
import * as doublePendulum from './flow/double-pendulum.mjs';
import * as orbitalDynamics from './flow/orbital-dynamics.mjs';
import * as gielisSuperformula from './flow/gielis-superformula.mjs';

// noise
import * as voronoiNoise from './noise/voronoi-noise.mjs';
import * as voronoiCrackle from './noise/voronoi-crackle.mjs';
import * as voronoiGrid from './noise/voronoi-grid.mjs';
import * as worleyNoise from './noise/worley-noise.mjs';
import * as domainWarping from './noise/domain-warping.mjs';
import * as turingPatterns from './noise/turing-patterns.mjs';
import * as reactionDiffusion from './noise/reaction-diffusion.mjs';
import * as grayScott from './noise/gray-scott.mjs';
import * as metaballs from './noise/metaballs.mjs';

// simulation
import * as gameOfLife from './simulation/game-of-life.mjs';
import * as langtonsAnt from './simulation/langtons-ant.mjs';
import * as waveFunctionCollapse from './simulation/wave-function-collapse.mjs';

// decorative (community)
import * as starburst from './decorative/starburst.mjs';
import * as clockworkNebula from './decorative/clockwork-nebula.mjs';
import * as matrixRain from './decorative/matrix-rain.mjs';

// 3d
import * as cube3d from './3d/cube-3d.mjs';
import * as sphere3d from './3d/sphere-3d.mjs';
import * as hypercube from './3d/hypercube.mjs';

// ---------------------------------------------------------------------------
// Registry
// ---------------------------------------------------------------------------

// Normalize legacy category names to new folder names
const CATEGORY_MAP = { 'basic-shapes': 'shapes', 'flow-abstract': 'flow' };

// Built-in modules
const builtinModules = [basicShapes, organic, flowAbstract, fills, decorative, utility, collaborator];

// Community modules grouped by target category
const communityModules = [
  { category: 'shapes', modules: [hexGrid, gear, schotter] },
  { category: 'organic', modules: [vineGrowth, phyllotaxisSpiral, lichenGrowth, slimeMold, dla] },
  { category: 'fractals', modules: [mandelbrot, juliaSet, apollonianGasket, dragonCurve, kochSnowflake, sierpinskiTriangle, kaleidoscopicIfs, penroseTiling, hyperbolicTiling, viridisVortex] },
  { category: 'flow', modules: [cliffordAttractor, hopalongAttractor, doublePendulum, orbitalDynamics, gielisSuperformula] },
  { category: 'noise', modules: [voronoiNoise, voronoiCrackle, voronoiGrid, worleyNoise, domainWarping, turingPatterns, reactionDiffusion, grayScott, metaballs] },
  { category: 'simulation', modules: [gameOfLife, langtonsAnt, waveFunctionCollapse] },
  { category: 'decorative', modules: [starburst, clockworkNebula, matrixRain] },
  { category: '3d', modules: [cube3d, sphere3d, hypercube] },
];

/** @type {Map<string, { fn: Function, meta: object }>} */
const registry = new Map();

// Register built-in primitives (normalize category names)
for (const mod of builtinModules) {
  if (!mod.METADATA) continue;
  const metaList = Array.isArray(mod.METADATA) ? mod.METADATA : [mod.METADATA];
  for (const meta of metaList) {
    const fn = mod[meta.name];
    if (typeof fn === 'function') {
      const category = CATEGORY_MAP[meta.category] || meta.category;
      registry.set(meta.name, { fn, meta: { ...meta, category } });
    }
  }
}

// Register community primitives with correct category + source
for (const { category, modules } of communityModules) {
  for (const mod of modules) {
    if (!mod.METADATA) continue;
    const metaList = Array.isArray(mod.METADATA) ? mod.METADATA : [mod.METADATA];
    for (const meta of metaList) {
      const fn = mod[meta.name];
      if (typeof fn === 'function') {
        registry.set(meta.name, { fn, meta: { ...meta, category, source: 'community' } });
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Get a primitive function by name.
 * @param {string} name - Primitive name (e.g. 'circle', 'fractalTree')
 * @returns {Function|null} The primitive function, or null if not found
 */
export function getPrimitive(name) {
  const entry = registry.get(name);
  return entry ? entry.fn : null;
}

/**
 * List all registered primitives.
 * @param {object} [opts]
 * @param {string} [opts.category] - Filter by category
 * @param {boolean} [opts.includeCommunity=true] - Include community primitives
 * @returns {Promise<Array<{name: string, description: string, category: string}>>}
 */
export async function listPrimitives(opts = {}) {
  const results = [];
  for (const [name, { meta }] of registry) {
    if (opts.category && meta.category !== opts.category) continue;
    if (opts.includeCommunity === false && meta.source === 'community') continue;
    results.push({
      name,
      description: meta.description,
      category: meta.category,
      source: meta.source || 'builtin',
    });
  }
  return results.sort((a, b) => a.category.localeCompare(b.category) || a.name.localeCompare(b.name));
}

/**
 * Get detailed info about a specific primitive.
 * @param {string} name - Primitive name
 * @returns {Promise<object|null>} Full metadata including parameters, or null
 */
export async function getPrimitiveInfo(name) {
  const entry = registry.get(name);
  if (!entry) return null;
  return { ...entry.meta, source: entry.meta.source || 'builtin' };
}

/**
 * Execute a primitive by name with args object.
 * @param {string} name - Primitive name
 * @param {object} args - Arguments as key-value pairs
 * @returns {Array} Array of stroke objects
 */
export function executePrimitive(name, args) {
  const entry = registry.get(name);
  if (!entry) throw new Error(`Unknown primitive: ${name}`);

  const meta = entry.meta;
  const paramNames = Object.keys(meta.parameters || {});
  const positionalArgs = paramNames.map(p => args[p]);
  return entry.fn(...positionalArgs);
}

// Re-export all primitive functions for direct import
export { circle, ellipse, arc, rectangle, polygon, star } from './shapes/basic-shapes.mjs';
export { lSystem, flower, leaf, vine, spaceColonization, mycelium, barnsleyFern } from './organic/organic.mjs';
export { flowField, spiral, lissajous, strangeAttractor, spirograph } from './flow/flow-abstract.mjs';
export { hatchFill, crossHatch, stipple, gradientFill, colorWash, solidFill } from './fills/fills.mjs';
export { border, mandala, fractalTree, radialSymmetry, sacredGeometry } from './decorative/decorative.mjs';
export { bezierCurve, dashedLine, arrow, strokeText, alienGlyphs } from './utility/utility.mjs';
export { extend, branch, connect, coil, morph, hatchGradient, stitch, bloom, gradient, parallel, echo, cascade, mirror, shadow, counterpoint, harmonize, fragment, outline, contour, physarum, attractorBranch, attractorFlow, interiorFill, vineGrowth, setNearbyCache, getNearbyCache } from './collaborator.mjs';
