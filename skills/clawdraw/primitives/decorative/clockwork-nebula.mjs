/**
 * The Clockwork Nebula — A cosmic composition of stars, spirograph gears, and nebula dust.
 *
 * Community primitive for ClawDraw.
 */

import { makeStroke, samplePalette, clamp, noise2d } from './helpers.mjs';

export const METADATA = {
  name: 'clockworkNebula',
  description: 'A cosmic scene with starfield, spirograph gears, and nebula dust',
  category: 'community',
  author: 'Pablo_PiCLAWsso',
  parameters: {
    cx: { type: 'number', required: true, description: 'Center X' },
    cy: { type: 'number', required: true, description: 'Center Y' },
    size: { type: 'number', default: 3000, description: 'Overall size of the nebula' },
    stars: { type: 'number', default: 1000, description: 'Number of stars' },
    gears: { type: 'number', default: 15, description: 'Number of spirograph gears' },
    dust: { type: 'number', default: 50, description: 'Amount of nebula dust' },
    palette: { type: 'string', default: 'turbo', description: 'Color palette (turbo recommended)' },
  },
};

// Inline spirograph helper to keep this primitive self-contained
function generateSpiro(cx, cy, outerR, innerR, traceR, revolutions, color, brushSize) {
  const steps = revolutions * 100;
  const diff = outerR - innerR;
  const pts = [];
  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * revolutions * Math.PI * 2;
    const x = cx + diff * Math.cos(t) + traceR * Math.cos(t * diff / innerR);
    const y = cy + diff * Math.sin(t) - traceR * Math.sin(t * diff / innerR);
    pts.push({ x, y });
  }
  
  // Split long strokes
  const result = [];
  const MAX = 4000;
  for(let i=0; i<pts.length; i+=MAX) {
    const chunk = pts.slice(i, i+MAX);
    if(chunk.length > 2) {
      result.push(makeStroke(chunk, color, brushSize, 0.8, 'taperBoth'));
    }
  }
  return result;
}

export function clockworkNebula(cx, cy, size, stars, gears, dust, palette) {
  cx = Number(cx) || 0;
  cy = Number(cy) || 0;
  size = clamp(Number(size) || 3000, 500, 10000);
  stars = clamp(Number(stars) || 1000, 100, 5000);
  gears = clamp(Number(gears) || 15, 1, 50);
  dust = clamp(Number(dust) || 50, 10, 200);
  palette = palette || 'turbo';

  const strokes = [];

  // 1. Starfield (Stippling)
  for(let i=0; i<stars; i++) {
    // Gaussian-ish distribution for density at center
    const r = (Math.random() + Math.random() + Math.random()) / 3 * size;
    const angle = Math.random() * Math.PI * 2;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    
    const t = 1 - (r / size); // Brighter/Different color at center
    strokes.push(makeStroke(
        [{x, y}, {x: x+1, y: y+1}], 
        samplePalette(palette, clamp(t, 0, 1)), 
        Math.random() * 3 + 1, 
        0.6, 
        'flat'
    ));
  }

  // 2. Gears (Spirographs)
  const gearCenters = [];
  for(let i=0; i<gears; i++) {
    const r = 100 + Math.random() * 400;
    const gx = cx + (Math.random() - 0.5) * size * 0.8;
    const gy = cy + (Math.random() - 0.5) * size * 0.8;
    gearCenters.push({x: gx, y: gy});
    
    const gearStrokes = generateSpiro(
      gx, gy,
      r,
      r * (0.2 + Math.random() * 0.6), // innerR
      r * 0.5, // offset
      20, // revolutions
      samplePalette(palette, Math.random()),
      3
    );
    strokes.push(...gearStrokes);
  }

  // 3. Nebula Dust (Strange Attractors - Lorenz-like traces)
  for(let i=0; i<dust; i++) {
    const scale = 30 + Math.random() * 20;
    const dcx = cx + (Math.random() - 0.5) * size;
    const dcy = cy + (Math.random() - 0.5) * size;
    const c = samplePalette(palette, Math.random());
    
    let x = 0.1, y = 0, z = 0;
    const dt = 0.01;
    const pts = [];
    // Simple Lorenz attractor trace
    for(let j=0; j<500; j++) {
      const dx = 10 * (y - x);
      const dy = x * (28 - z) - y;
      const dz = x * y - (8/3) * z;
      x += dx * dt; y += dy * dt; z += dz * dt;
      pts.push({ x: dcx + x * scale, y: dcy + y * scale });
    }
    strokes.push(makeStroke(pts, c, 2, 0.4, 'taper'));
  }

  // 4. Web Connections (Electric Arcs between gears)
  for(let i=0; i<gearCenters.length; i++) {
    for(let j=i+1; j<gearCenters.length; j++) {
      const p1 = gearCenters[i];
      const p2 = gearCenters[j];
      const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
      
      if (dist < 800) {
        const midX = (p1.x + p2.x) / 2;
        const midY = (p1.y + p2.y) / 2;
        const cpX = midX + (Math.random() - 0.5) * 200;
        const cpY = midY + (Math.random() - 0.5) * 200;
        
        const pts = [];
        for(let t=0; t<=1; t+=0.05) {
            const xx = (1-t)*(1-t)*p1.x + 2*(1-t)*t*cpX + t*t*p2.x;
            const yy = (1-t)*(1-t)*p1.y + 2*(1-t)*t*cpY + t*t*p2.y;
            pts.push({x: xx, y: yy});
        }
        strokes.push(makeStroke(pts, '#ffffff', 1, 0.5, 'pulse'));
      }
    }
  }

  return strokes;
}
