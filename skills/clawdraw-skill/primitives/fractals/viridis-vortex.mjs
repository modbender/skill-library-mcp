/**
 * Viridis Vortex — A recursive, flow-warped fractal spiral.
 *
 * Community primitive for ClawDraw.
 */

import { makeStroke, samplePalette, clamp, noise2d } from './helpers.mjs';

export const METADATA = {
  name: 'viridisVortex',
  description: 'A recursive fractal spiral with noise warp and pure viridis gradient',
  category: 'community',
  author: 'Pablo_PiCLAWsso',
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    size: { type: 'number', default: 300, description: 'Size of the vortex' },
    arms: { type: 'number', default: 7, description: 'Number of spiral arms' },
    turns: { type: 'number', default: 4, description: 'Number of turns per arm' },
    warp: { type: 'number', default: 100, description: 'Amount of noise warp' },
    palette: { type: 'string', default: 'viridis', description: 'Color palette (viridis recommended)' },
  },
};

export function viridisVortex(cx, cy, size, arms, turns, warp, palette) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 300, 50, 2000);
  arms = clamp(Number(arms) || 7, 3, 20);
  turns = clamp(Number(turns) || 4, 1, 10);
  warp = Number(warp) || 100;
  palette = palette || 'viridis';

  const strokes = [];
  const stepsPerTurn = 50;
  
  for(let arm=0; arm<arms; arm++) {
      const armAngleOffset = (arm / arms) * Math.PI * 2;
      
      // Draw "ribs" along the spiral arm
      let r = 50;
      let theta = armAngleOffset;
      
      for(let t=0; t<turns * Math.PI * 2; t+=0.1) {
          // Current position on the spiral spine
          const spineX = cx + r * Math.cos(theta);
          const spineY = cy + r * Math.sin(theta);
          
          // Draw a "rib" perpendicular to the spine
          const ribLen = r * 0.4; // Ribs get longer as spiral expands
          const ribAngle = theta + Math.PI/2;
          
          const pts = [];
          const segments = 20;
          
          for(let s=-segments/2; s<=segments/2; s++) {
              // Normalized position along the rib (-1 to 1)
              const normS = s / (segments/2);
              
              // Base rib shape (curved)
              let rx = spineX + Math.cos(ribAngle) * (s * ribLen/segments);
              let ry = spineY + Math.sin(ribAngle) * (s * ribLen/segments);
              
              // Add noise warp based on position
              const w = noise2d(rx*0.002, ry*0.002) * warp;
              rx += Math.cos(theta)*w;
              ry += Math.sin(theta)*w;

              // Pressure wave
              const press = 1.0 - Math.abs(normS);
              pts.push({x: rx, y: ry, pressure: press});
          }
          
          // Color based on spiral depth (t) and rib position (s)
          // t varies from 0 to ~25. Normalize to 0-1.
          const depthT = t / (turns * Math.PI * 2);
          const colorT = clamp(depthT + (Math.random()*0.1), 0, 1);
          
          strokes.push(makeStroke(
              pts,
              samplePalette(palette, colorT), // Gradient
              2 + depthT*3, // Thicker outside
              0.8,
              'taperBoth'
          ));
          
          // Advance spiral
          r *= 1.02; // Exponential expansion
          theta += 0.1;
      }
  }

  // Scale all points to fit within size/2 from center
  const halfSize = size / 2;
  let maxDist = 0;
  for (const s of strokes) {
    for (const pt of s.points) {
      const dx = pt.x - cx;
      const dy = pt.y - cy;
      maxDist = Math.max(maxDist, Math.sqrt(dx * dx + dy * dy));
    }
  }
  if (maxDist > halfSize && maxDist > 0) {
    const scale = halfSize / maxDist;
    for (const s of strokes) {
      for (const pt of s.points) {
        pt.x = cx + (pt.x - cx) * scale;
        pt.y = cy + (pt.y - cy) * scale;
      }
    }
  }

  return strokes;
}
