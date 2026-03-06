/**
 * 3D Cube — wireframe cube with rotation and perspective.
 *
 * Community primitive for ClawDraw.
 */

import { clamp, lerp, makeStroke, samplePalette } from './helpers.mjs';

/** Auto-discovery metadata -- required for registry */
export const METADATA = {
  name: 'cube3d',
  description: 'Wireframe 3D cube with rotation and depth shading',
  category: 'community',
  author: 'kajukabla',
  parameters: {
    cx:            { type: 'number', required: true, description: 'Center X' },
    cy:            { type: 'number', required: true, description: 'Center Y' },
    size:          { type: 'number', required: false, default: 120, description: 'Cube half-size' },
    rotateX:       { type: 'number', required: false, default: 25, description: 'X rotation in degrees' },
    rotateY:       { type: 'number', required: false, default: 35, description: 'Y rotation in degrees' },
    rotateZ:       { type: 'number', required: false, default: 0, description: 'Z rotation in degrees' },
    subdivisions:  { type: 'number', required: false, default: 0, description: 'Edge subdivisions for wireframe detail (0-5)' },
    color:         { type: 'string', required: false, default: '#ffffff', description: 'Hex color (ignored if palette set)' },
    brushSize:     { type: 'number', required: false, default: 4, description: 'Brush width (3-100)' },
    opacity:       { type: 'number', required: false, default: 0.9, description: 'Stroke opacity (0-1)' },
    palette:       { type: 'string', required: false, description: 'Palette name' },
    pressureStyle: { type: 'string', required: false, default: 'default', description: 'Pressure style' },
  },
};

/**
 * Generate a wireframe 3D cube.
 *
 * Computes 8 cube vertices, applies 3-axis rotation, projects to 2D,
 * and draws each of the 12 edges as a stroke. Back edges are drawn
 * at reduced opacity for depth. Optional subdivisions add grid lines
 * on each face.
 *
 * @returns {Array} Array of stroke objects
 */
export function cube3d(cx, cy, size, rotateX, rotateY, rotateZ, subdivisions, color, brushSize, opacity, palette, pressureStyle) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 120, 10, 500);
  rotateX = (Number(rotateX) || 25) * Math.PI / 180;
  rotateY = (Number(rotateY) || 35) * Math.PI / 180;
  rotateZ = (Number(rotateZ) || 0) * Math.PI / 180;
  subdivisions = clamp(Math.round(Number(subdivisions) || 0), 0, 5);
  brushSize = clamp(Number(brushSize) || 4, 3, 100);
  opacity = clamp(Number(opacity) || 0.9, 0.01, 1);

  const cosX = Math.cos(rotateX), sinX = Math.sin(rotateX);
  const cosY = Math.cos(rotateY), sinY = Math.sin(rotateY);
  const cosZ = Math.cos(rotateZ), sinZ = Math.sin(rotateZ);

  function rotate(x, y, z) {
    // Rotate Z
    let x1 = x * cosZ - y * sinZ;
    let y1 = x * sinZ + y * cosZ;
    // Rotate Y
    let x2 = x1 * cosY - z * sinY;
    let z1 = x1 * sinY + z * cosY;
    // Rotate X
    let y2 = y1 * cosX - z1 * sinX;
    let z2 = y1 * sinX + z1 * cosX;
    return { x: x2, y: y2, z: z2 };
  }

  function project(p) {
    return { x: cx + p.x, y: cy + p.y, z: p.z };
  }

  // 8 cube vertices
  const s = size;
  const rawVerts = [
    [-s, -s, -s], [s, -s, -s], [s, s, -s], [-s, s, -s],
    [-s, -s,  s], [s, -s,  s], [s, s,  s], [-s, s,  s],
  ];
  const verts = rawVerts.map(([x, y, z]) => project(rotate(x, y, z)));

  // 12 edges
  const edges = [
    [0,1],[1,2],[2,3],[3,0], // front face
    [4,5],[5,6],[6,7],[7,4], // back face
    [0,4],[1,5],[2,6],[3,7], // connecting edges
  ];

  const result = [];

  function drawEdge(p0, p1, edgeIndex, totalEdges) {
    const midZ = (p0.z + p1.z) / 2;
    const isFront = midZ >= 0;
    const t = edgeIndex / totalEdges;
    const c = palette ? samplePalette(palette, t) : (color || '#ffffff');
    const edgeOpacity = isFront ? opacity : opacity * 0.35;

    // Add slight wobble for hand-drawn feel
    const wobbleAmt = size * 0.006;
    const pts = [];
    const segs = 8;
    for (let i = 0; i <= segs; i++) {
      const f = i / segs;
      pts.push({
        x: lerp(p0.x, p1.x, f) + (Math.random() - 0.5) * wobbleAmt,
        y: lerp(p0.y, p1.y, f) + (Math.random() - 0.5) * wobbleAmt,
      });
    }
    result.push(makeStroke(pts, c, brushSize, edgeOpacity, pressureStyle));
  }

  // Draw main edges
  for (let i = 0; i < edges.length && result.length < 200; i++) {
    const [a, b] = edges[i];
    drawEdge(verts[a], verts[b], i, edges.length);
  }

  // Subdivisions — grid lines on each face
  if (subdivisions > 0) {
    const faces = [
      [0,1,2,3], [4,5,6,7], // front, back
      [0,1,5,4], [2,3,7,6], // top, bottom
      [0,3,7,4], [1,2,6,5], // left, right
    ];

    for (const face of faces) {
      const [a, b, c, d] = face.map(i => verts[i]);
      for (let sub = 1; sub <= subdivisions && result.length < 200; sub++) {
        const f = sub / (subdivisions + 1);
        // Lines parallel to ab-dc direction
        const p0 = project(rotate(0,0,0)); // dummy to get type
        const s0 = { x: lerp(a.x, d.x, f), y: lerp(a.y, d.y, f), z: lerp(a.z, d.z, f) };
        const s1 = { x: lerp(b.x, c.x, f), y: lerp(b.y, c.y, f), z: lerp(b.z, c.z, f) };
        drawEdge(s0, s1, result.length, 200);

        if (result.length >= 200) break;

        // Lines parallel to ad-bc direction
        const s2 = { x: lerp(a.x, b.x, f), y: lerp(a.y, b.y, f), z: lerp(a.z, b.z, f) };
        const s3 = { x: lerp(d.x, c.x, f), y: lerp(d.y, c.y, f), z: lerp(d.z, c.z, f) };
        drawEdge(s2, s3, result.length, 200);
      }
    }
  }

  return result.slice(0, 200);
}
