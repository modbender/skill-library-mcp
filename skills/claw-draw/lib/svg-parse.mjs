/**
 * SVG path parser — plain JS port of packages/shared/src/utils/svg-parse.ts
 *
 * Parses SVG `d` attribute strings into point arrays.
 */

/** Number of args expected per SVG command */
const ARGS_PER_COMMAND = {
  M: 2, m: 2, L: 2, l: 2, H: 1, h: 1, V: 1, v: 1,
  C: 6, c: 6, S: 4, s: 4, Q: 4, q: 4, T: 2, t: 2,
  A: 7, a: 7, Z: 0, z: 0,
};

/**
 * Tokenize an SVG path `d` attribute into {command, args} pairs.
 * @param {string} d
 * @returns {Array<{command: string, args: number[]}>}
 */
export function tokenizeSvgPath(d) {
  const tokens = [];
  if (!d || d.trim().length === 0) return tokens;

  const re = /([MmLlHhVvCcSsQqTtAaZz])|([+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?)/g;
  let current = null;
  let match;

  while ((match = re.exec(d)) !== null) {
    if (match[1]) {
      if (current) tokens.push(current);
      current = { command: match[1], args: [] };
    } else if (match[2]) {
      if (!current) current = { command: 'M', args: [] };
      current.args.push(parseFloat(match[2]));
    }
  }
  if (current) tokens.push(current);

  // Split tokens with too many args into repeated commands
  const result = [];
  for (const token of tokens) {
    const cmd = token.command;
    const expected = ARGS_PER_COMMAND[cmd];
    if (expected === undefined || expected === 0 || token.args.length <= expected) {
      result.push(token);
      continue;
    }
    result.push({ command: cmd, args: token.args.slice(0, expected) });
    const repeatCmd = cmd === 'M' ? 'L' : cmd === 'm' ? 'l' : cmd;
    for (let i = expected; i < token.args.length; i += expected) {
      result.push({ command: repeatCmd, args: token.args.slice(i, i + expected) });
    }
  }
  return result;
}

/**
 * Evaluate a cubic bezier at parameter t.
 * @param {{p0:{x:number,y:number},p1:{x:number,y:number},p2:{x:number,y:number},p3:{x:number,y:number}}} curve
 * @param {number} t
 * @returns {{x:number,y:number}}
 */
function evaluateBezier(curve, t) {
  const mt = 1 - t;
  const mt2 = mt * mt;
  const mt3 = mt2 * mt;
  const t2 = t * t;
  const t3 = t2 * t;
  return {
    x: mt3 * curve.p0.x + 3 * mt2 * t * curve.p1.x + 3 * mt * t2 * curve.p2.x + t3 * curve.p3.x,
    y: mt3 * curve.p0.y + 3 * mt2 * t * curve.p1.y + 3 * mt * t2 * curve.p2.y + t3 * curve.p3.y,
  };
}

/**
 * Compute the angle between two vectors.
 */
function angleBetween(ux, uy, vx, vy) {
  const dot = ux * vx + uy * vy;
  const lenU = Math.sqrt(ux * ux + uy * uy);
  const lenV = Math.sqrt(vx * vx + vy * vy);
  let cos = dot / (lenU * lenV);
  if (cos < -1) cos = -1;
  if (cos > 1) cos = 1;
  const angle = Math.acos(cos);
  return (ux * vy - uy * vx) < 0 ? -angle : angle;
}

/**
 * Sample an SVG arc using center parameterization.
 */
function sampleArc(x1, y1, rxIn, ryIn, phi, largeArc, sweep, x2, y2, numSamples, addPoint) {
  if (rxIn === 0 || ryIn === 0 || (x1 === x2 && y1 === y2)) {
    addPoint(x2, y2);
    return;
  }

  let rx = rxIn;
  let ry = ryIn;
  const cosPhi = Math.cos(phi);
  const sinPhi = Math.sin(phi);

  const dx2 = (x1 - x2) / 2;
  const dy2 = (y1 - y2) / 2;
  const x1p = cosPhi * dx2 + sinPhi * dy2;
  const y1p = -sinPhi * dx2 + cosPhi * dy2;

  const x1pSq = x1p * x1p;
  const y1pSq = y1p * y1p;
  let rxSq = rx * rx;
  let rySq = ry * ry;

  const lambda = x1pSq / rxSq + y1pSq / rySq;
  if (lambda > 1) {
    const sqrtLambda = Math.sqrt(lambda);
    rx *= sqrtLambda;
    ry *= sqrtLambda;
    rxSq = rx * rx;
    rySq = ry * ry;
  }

  let num = rxSq * rySq - rxSq * y1pSq - rySq * x1pSq;
  const den = rxSq * y1pSq + rySq * x1pSq;
  if (num < 0) num = 0;
  let sq = Math.sqrt(num / den);
  if (largeArc === sweep) sq = -sq;

  const cxp = sq * (rx * y1p / ry);
  const cyp = sq * (-(ry * x1p / rx));

  const cxr = cosPhi * cxp - sinPhi * cyp + (x1 + x2) / 2;
  const cyr = sinPhi * cxp + cosPhi * cyp + (y1 + y2) / 2;

  const theta1 = angleBetween(1, 0, (x1p - cxp) / rx, (y1p - cyp) / ry);
  let dtheta = angleBetween(
    (x1p - cxp) / rx, (y1p - cyp) / ry,
    (-x1p - cxp) / rx, (-y1p - cyp) / ry,
  );

  if (!sweep && dtheta > 0) dtheta -= 2 * Math.PI;
  if (sweep && dtheta < 0) dtheta += 2 * Math.PI;

  for (let i = 1; i <= numSamples; i++) {
    const t = i / numSamples;
    const angle = theta1 + dtheta * t;
    const cosA = Math.cos(angle);
    const sinA = Math.sin(angle);
    const px = cosPhi * rx * cosA - sinPhi * ry * sinA + cxr;
    const py = sinPhi * rx * cosA + cosPhi * ry * sinA + cyr;
    addPoint(px, py);
  }
}

/**
 * Parse an SVG path `d` attribute string into an array of points.
 *
 * @param {string} d - SVG path string
 * @param {{samplesPerSegment?: number, scale?: number, translate?: {x: number, y: number}}} [options]
 * @returns {Array<{x: number, y: number, pressure: number, timestamp: number}>}
 */
export function parseSvgPath(d, options) {
  const tokens = tokenizeSvgPath(d);
  if (tokens.length === 0) return [];

  const samples = options?.samplesPerSegment ?? 20;
  const scale = options?.scale ?? 1;
  const tx = options?.translate?.x ?? 0;
  const ty = options?.translate?.y ?? 0;

  const points = [];
  let cx = 0, cy = 0;
  let startX = 0, startY = 0;
  let lastCp2X = 0, lastCp2Y = 0;
  let lastCmd = '';

  function addPoint(x, y) {
    points.push({ x: x * scale + tx, y: y * scale + ty, pressure: 0.5, timestamp: 0 });
  }

  function sampleCubic(x0, y0, cp1x, cp1y, cp2x, cp2y, x3, y3) {
    const curve = { p0: { x: x0, y: y0 }, p1: { x: cp1x, y: cp1y }, p2: { x: cp2x, y: cp2y }, p3: { x: x3, y: y3 } };
    for (let i = 1; i <= samples; i++) {
      const pt = evaluateBezier(curve, i / samples);
      addPoint(pt.x, pt.y);
    }
  }

  for (const token of tokens) {
    const cmd = token.command;
    const args = token.args;
    const isRel = cmd === cmd.toLowerCase() && cmd !== 'Z' && cmd !== 'z';

    switch (cmd.toUpperCase()) {
      case 'M': {
        const x = isRel ? cx + args[0] : args[0];
        const y = isRel ? cy + args[1] : args[1];
        addPoint(x, y);
        cx = x; cy = y; startX = x; startY = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'L': {
        const x = isRel ? cx + args[0] : args[0];
        const y = isRel ? cy + args[1] : args[1];
        addPoint(x, y);
        cx = x; cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'H': {
        const x = isRel ? cx + args[0] : args[0];
        addPoint(x, cy);
        cx = x;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'V': {
        const y = isRel ? cy + args[0] : args[0];
        addPoint(cx, y);
        cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'C': {
        const cp1x = isRel ? cx + args[0] : args[0];
        const cp1y = isRel ? cy + args[1] : args[1];
        const cp2x = isRel ? cx + args[2] : args[2];
        const cp2y = isRel ? cy + args[3] : args[3];
        const x = isRel ? cx + args[4] : args[4];
        const y = isRel ? cy + args[5] : args[5];
        sampleCubic(cx, cy, cp1x, cp1y, cp2x, cp2y, x, y);
        lastCp2X = cp2x; lastCp2Y = cp2y;
        cx = x; cy = y;
        break;
      }
      case 'S': {
        let cp1x, cp1y;
        if ('CcSs'.includes(lastCmd)) {
          cp1x = 2 * cx - lastCp2X;
          cp1y = 2 * cy - lastCp2Y;
        } else {
          cp1x = cx; cp1y = cy;
        }
        const scp2x = isRel ? cx + args[0] : args[0];
        const scp2y = isRel ? cy + args[1] : args[1];
        const sx = isRel ? cx + args[2] : args[2];
        const sy = isRel ? cy + args[3] : args[3];
        sampleCubic(cx, cy, cp1x, cp1y, scp2x, scp2y, sx, sy);
        lastCp2X = scp2x; lastCp2Y = scp2y;
        cx = sx; cy = sy;
        break;
      }
      case 'Q': {
        const qcpx = isRel ? cx + args[0] : args[0];
        const qcpy = isRel ? cy + args[1] : args[1];
        const qx = isRel ? cx + args[2] : args[2];
        const qy = isRel ? cy + args[3] : args[3];
        const c1x = cx + (2 / 3) * (qcpx - cx);
        const c1y = cy + (2 / 3) * (qcpy - cy);
        const c2x = qx + (2 / 3) * (qcpx - qx);
        const c2y = qy + (2 / 3) * (qcpy - qy);
        sampleCubic(cx, cy, c1x, c1y, c2x, c2y, qx, qy);
        lastCp2X = qcpx; lastCp2Y = qcpy;
        cx = qx; cy = qy;
        break;
      }
      case 'T': {
        let qcpx, qcpy;
        if ('QqTt'.includes(lastCmd)) {
          qcpx = 2 * cx - lastCp2X;
          qcpy = 2 * cy - lastCp2Y;
        } else {
          qcpx = cx; qcpy = cy;
        }
        const tx2 = isRel ? cx + args[0] : args[0];
        const ty2 = isRel ? cy + args[1] : args[1];
        const c1x = cx + (2 / 3) * (qcpx - cx);
        const c1y = cy + (2 / 3) * (qcpy - cy);
        const c2x = tx2 + (2 / 3) * (qcpx - tx2);
        const c2y = ty2 + (2 / 3) * (qcpy - ty2);
        sampleCubic(cx, cy, c1x, c1y, c2x, c2y, tx2, ty2);
        lastCp2X = qcpx; lastCp2Y = qcpy;
        cx = tx2; cy = ty2;
        break;
      }
      case 'A': {
        const rx = Math.abs(args[0]);
        const ry = Math.abs(args[1]);
        const xRot = args[2] * (Math.PI / 180);
        const largeArc = args[3] !== 0;
        const sweep = args[4] !== 0;
        const x = isRel ? cx + args[5] : args[5];
        const y = isRel ? cy + args[6] : args[6];
        sampleArc(cx, cy, rx, ry, xRot, largeArc, sweep, x, y, samples, addPoint);
        cx = x; cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'Z': {
        if (cx !== startX || cy !== startY) addPoint(startX, startY);
        cx = startX; cy = startY;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
    }
    lastCmd = cmd;
  }

  return points;
}

/**
 * Parse an SVG path `d` attribute into multiple subpath point arrays.
 * Splits at each M/m command so separate shapes don't get connected.
 *
 * @param {string} d - SVG path string
 * @param {{samplesPerSegment?: number, scale?: number, translate?: {x: number, y: number}}} [options]
 * @returns {Array<Array<{x: number, y: number, pressure: number, timestamp: number}>>}
 */
export function parseSvgPathMulti(d, options) {
  const tokens = tokenizeSvgPath(d);
  if (tokens.length === 0) return [];

  const samples = options?.samplesPerSegment ?? 20;
  const scale = options?.scale ?? 1;
  const tx = options?.translate?.x ?? 0;
  const ty = options?.translate?.y ?? 0;

  const subpaths = [];
  let current = [];
  let cx = 0, cy = 0;
  let startX = 0, startY = 0;
  let lastCp2X = 0, lastCp2Y = 0;
  let lastCmd = '';

  function addPoint(x, y) {
    current.push({ x: x * scale + tx, y: y * scale + ty, pressure: 0.5, timestamp: 0 });
  }

  function sampleCubic(x0, y0, cp1x, cp1y, cp2x, cp2y, x3, y3) {
    const curve = { p0: { x: x0, y: y0 }, p1: { x: cp1x, y: cp1y }, p2: { x: cp2x, y: cp2y }, p3: { x: x3, y: y3 } };
    for (let i = 1; i <= samples; i++) {
      const pt = evaluateBezier(curve, i / samples);
      addPoint(pt.x, pt.y);
    }
  }

  for (const token of tokens) {
    const cmd = token.command;
    const args = token.args;
    const isRel = cmd === cmd.toLowerCase() && cmd !== 'Z' && cmd !== 'z';

    switch (cmd.toUpperCase()) {
      case 'M': {
        // Start a new subpath — flush the previous one
        if (current.length >= 2) subpaths.push(current);
        current = [];
        const x = isRel ? cx + args[0] : args[0];
        const y = isRel ? cy + args[1] : args[1];
        addPoint(x, y);
        cx = x; cy = y; startX = x; startY = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'L': {
        const x = isRel ? cx + args[0] : args[0];
        const y = isRel ? cy + args[1] : args[1];
        addPoint(x, y);
        cx = x; cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'H': {
        const x = isRel ? cx + args[0] : args[0];
        addPoint(x, cy);
        cx = x;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'V': {
        const y = isRel ? cy + args[0] : args[0];
        addPoint(cx, y);
        cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'C': {
        const cp1x = isRel ? cx + args[0] : args[0];
        const cp1y = isRel ? cy + args[1] : args[1];
        const cp2x = isRel ? cx + args[2] : args[2];
        const cp2y = isRel ? cy + args[3] : args[3];
        const x = isRel ? cx + args[4] : args[4];
        const y = isRel ? cy + args[5] : args[5];
        sampleCubic(cx, cy, cp1x, cp1y, cp2x, cp2y, x, y);
        lastCp2X = cp2x; lastCp2Y = cp2y;
        cx = x; cy = y;
        break;
      }
      case 'S': {
        let cp1x, cp1y;
        if ('CcSs'.includes(lastCmd)) {
          cp1x = 2 * cx - lastCp2X;
          cp1y = 2 * cy - lastCp2Y;
        } else {
          cp1x = cx; cp1y = cy;
        }
        const scp2x = isRel ? cx + args[0] : args[0];
        const scp2y = isRel ? cy + args[1] : args[1];
        const sx = isRel ? cx + args[2] : args[2];
        const sy = isRel ? cy + args[3] : args[3];
        sampleCubic(cx, cy, cp1x, cp1y, scp2x, scp2y, sx, sy);
        lastCp2X = scp2x; lastCp2Y = scp2y;
        cx = sx; cy = sy;
        break;
      }
      case 'Q': {
        const qcpx = isRel ? cx + args[0] : args[0];
        const qcpy = isRel ? cy + args[1] : args[1];
        const qx = isRel ? cx + args[2] : args[2];
        const qy = isRel ? cy + args[3] : args[3];
        const c1x = cx + (2 / 3) * (qcpx - cx);
        const c1y = cy + (2 / 3) * (qcpy - cy);
        const c2x = qx + (2 / 3) * (qcpx - qx);
        const c2y = qy + (2 / 3) * (qcpy - qy);
        sampleCubic(cx, cy, c1x, c1y, c2x, c2y, qx, qy);
        lastCp2X = qcpx; lastCp2Y = qcpy;
        cx = qx; cy = qy;
        break;
      }
      case 'T': {
        let qcpx, qcpy;
        if ('QqTt'.includes(lastCmd)) {
          qcpx = 2 * cx - lastCp2X;
          qcpy = 2 * cy - lastCp2Y;
        } else {
          qcpx = cx; qcpy = cy;
        }
        const tx2 = isRel ? cx + args[0] : args[0];
        const ty2 = isRel ? cy + args[1] : args[1];
        const c1x = cx + (2 / 3) * (qcpx - cx);
        const c1y = cy + (2 / 3) * (qcpy - cy);
        const c2x = tx2 + (2 / 3) * (qcpx - tx2);
        const c2y = ty2 + (2 / 3) * (qcpy - ty2);
        sampleCubic(cx, cy, c1x, c1y, c2x, c2y, tx2, ty2);
        lastCp2X = qcpx; lastCp2Y = qcpy;
        cx = tx2; cy = ty2;
        break;
      }
      case 'A': {
        const rx = Math.abs(args[0]);
        const ry = Math.abs(args[1]);
        const xRot = args[2] * (Math.PI / 180);
        const largeArc = args[3] !== 0;
        const sweep = args[4] !== 0;
        const x = isRel ? cx + args[5] : args[5];
        const y = isRel ? cy + args[6] : args[6];
        sampleArc(cx, cy, rx, ry, xRot, largeArc, sweep, x, y, samples, addPoint);
        cx = x; cy = y;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
      case 'Z': {
        if (cx !== startX || cy !== startY) addPoint(startX, startY);
        cx = startX; cy = startY;
        lastCp2X = cx; lastCp2Y = cy;
        break;
      }
    }
    lastCmd = cmd;
  }

  // Flush final subpath
  if (current.length >= 2) subpaths.push(current);

  return subpaths;
}
