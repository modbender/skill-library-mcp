/**
 * Symmetry system for ClawDraw stroke generation.
 *
 * Modes:
 *   - none:      no copies, no constraints
 *   - vertical:  mirror across Y axis (flip X around center)
 *   - horizontal: mirror across X axis (flip Y around center)
 *   - both:      4-fold mirror (3 copies: flip X, flip Y, flip both)
 *   - radial:N   N copies rotated evenly around center
 *
 * All functions are pure (no global state). Symmetry center is passed explicitly.
 */

// @security-manifest
// env: none
// endpoints: none
// files: none
// exec: none

let _symSeq = 0;

// ---------------------------------------------------------------------------
// Parsing
// ---------------------------------------------------------------------------

/**
 * Parse a symmetry mode string into a structured descriptor.
 * @param {string} str - One of 'none', 'vertical', 'horizontal', 'both', 'radial:N'
 * @returns {{ mode: string, folds: number }}
 */
export function parseSymmetryMode(str) {
  if (!str || str === 'none') return { mode: 'none', folds: 1 };

  const lower = String(str).trim().toLowerCase();

  if (lower === 'vertical')   return { mode: 'vertical', folds: 2 };
  if (lower === 'horizontal') return { mode: 'horizontal', folds: 2 };
  if (lower === 'both')       return { mode: 'both', folds: 4 };

  const radialMatch = /^radial[:\s]+(\d+)$/i.exec(lower);
  if (radialMatch) {
    const n = Math.max(2, parseInt(radialMatch[1], 10));
    return { mode: 'radial', folds: n };
  }

  return { mode: 'none', folds: 1 };
}

// ---------------------------------------------------------------------------
// Internal helper
// ---------------------------------------------------------------------------

/**
 * Deep-clone a stroke with a new ID and transformed points.
 * @param {object} stroke - Source stroke
 * @param {(pt: {x:number, y:number}) => {x:number, y:number}} transformFn
 * @returns {object} New stroke with transformed points
 */
function cloneStroke(stroke, transformFn) {
  const id = `sym-${Date.now().toString(36)}-${(++_symSeq).toString(36)}`;
  return {
    ...stroke,
    id,
    points: stroke.points.map(p => {
      const np = transformFn(p);
      return { ...p, x: np.x, y: np.y };
    }),
  };
}

// ---------------------------------------------------------------------------
// Constraint enforcement
// ---------------------------------------------------------------------------

/**
 * Mutate stroke points so the stroke's centroid lies in the canonical region
 * for the given symmetry mode. This ensures the original stroke is in the
 * "primary" zone before copies are generated.
 *
 * - vertical:   centroid must be in right half  (x >= centerX)
 * - horizontal: centroid must be in top half    (y <= centerY)
 * - both:       centroid must be in top-right quadrant
 * - radial:     centroid must be in wedge [0, 2pi/N)
 *
 * The entire stroke is transformed as a rigid body to preserve shape.
 *
 * @param {object} stroke - Stroke to mutate in place
 * @param {string} mode - 'none' | 'vertical' | 'horizontal' | 'both' | 'radial'
 * @param {number} folds - Number of folds (only used for radial)
 * @param {number} centerX - Symmetry center X
 * @param {number} centerY - Symmetry center Y
 */
export function enforceConstraints(stroke, mode, folds, centerX, centerY) {
  if (mode === 'none') return;
  if (!stroke.points || stroke.points.length === 0) return;

  // Compute centroid
  let sumX = 0, sumY = 0;
  for (const pt of stroke.points) { sumX += pt.x; sumY += pt.y; }
  const centX = sumX / stroke.points.length;
  const centY = sumY / stroke.points.length;

  if (mode === 'vertical') {
    if (centX < centerX) {
      for (const pt of stroke.points) pt.x = 2 * centerX - pt.x;
    }
  } else if (mode === 'horizontal') {
    if (centY > centerY) {
      for (const pt of stroke.points) pt.y = 2 * centerY - pt.y;
    }
  } else if (mode === 'both') {
    if (centX < centerX) {
      for (const pt of stroke.points) pt.x = 2 * centerX - pt.x;
    }
    if (centY > centerY) {
      for (const pt of stroke.points) pt.y = 2 * centerY - pt.y;
    }
  } else if (mode === 'radial') {
    const dx = centX - centerX, dy = centY - centerY;
    const r = Math.sqrt(dx * dx + dy * dy);
    if (r < 1) return; // Centered at origin — inherently symmetric

    const maxAngle = (2 * Math.PI) / folds;
    let angle = Math.atan2(dy, dx);
    if (angle < 0) angle += 2 * Math.PI;

    if (angle > maxAngle) {
      const targetAngle = angle % maxAngle;
      const rotationDelta = targetAngle - angle;
      const cos = Math.cos(rotationDelta), sin = Math.sin(rotationDelta);
      for (const pt of stroke.points) {
        const pdx = pt.x - centerX, pdy = pt.y - centerY;
        pt.x = centerX + pdx * cos - pdy * sin;
        pt.y = centerY + pdx * sin + pdy * cos;
      }
    }
  }
}

// ---------------------------------------------------------------------------
// Copy generation
// ---------------------------------------------------------------------------

/**
 * Generate symmetry copies of a stroke (not including the original).
 *
 * @param {object} stroke - Original stroke
 * @param {string} mode - 'none' | 'vertical' | 'horizontal' | 'both' | 'radial'
 * @param {number} folds - Number of folds (only used for radial)
 * @param {number} centerX - Symmetry center X
 * @param {number} centerY - Symmetry center Y
 * @returns {object[]} Array of cloned strokes with transformed points
 */
export function generateCopies(stroke, mode, folds, centerX, centerY) {
  if (mode === 'none') return [];

  const cx = centerX;
  const cy = centerY;

  if (mode === 'vertical') {
    return [cloneStroke(stroke, p => ({ x: 2 * cx - p.x, y: p.y }))];
  }

  if (mode === 'horizontal') {
    return [cloneStroke(stroke, p => ({ x: p.x, y: 2 * cy - p.y }))];
  }

  if (mode === 'both') {
    return [
      cloneStroke(stroke, p => ({ x: 2 * cx - p.x, y: p.y })),
      cloneStroke(stroke, p => ({ x: p.x, y: 2 * cy - p.y })),
      cloneStroke(stroke, p => ({ x: 2 * cx - p.x, y: 2 * cy - p.y })),
    ];
  }

  if (mode === 'radial') {
    const copies = [];
    for (let i = 1; i < folds; i++) {
      const angle = (i / folds) * Math.PI * 2;
      const cos = Math.cos(angle), sin = Math.sin(angle);
      copies.push(cloneStroke(stroke, p => {
        const dx = p.x - cx, dy = p.y - cy;
        return {
          x: cx + dx * cos - dy * sin,
          y: cy + dx * sin + dy * cos,
        };
      }));
    }
    return copies;
  }

  return [];
}

// ---------------------------------------------------------------------------
// High-level API
// ---------------------------------------------------------------------------

/**
 * Apply symmetry to an array of strokes. Returns a new array containing
 * the originals plus all generated symmetry copies.
 *
 * Constraints are enforced on the originals before copies are generated,
 * so originals may be mutated in place.
 *
 * @param {object[]} strokes - Original strokes
 * @param {string} mode - 'none' | 'vertical' | 'horizontal' | 'both' | 'radial'
 * @param {number} folds - Number of folds
 * @param {number} centerX - Symmetry center X
 * @param {number} centerY - Symmetry center Y
 * @returns {object[]} Originals + symmetry copies
 */
export function applySymmetry(strokes, mode, folds, centerX, centerY) {
  if (mode === 'none') return strokes;

  const result = [];
  for (const stroke of strokes) {
    enforceConstraints(stroke, mode, folds, centerX, centerY);
    result.push(stroke);
    result.push(...generateCopies(stroke, mode, folds, centerX, centerY));
  }
  return result;
}
