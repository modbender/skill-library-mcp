import * as PImage from 'pureimage';
const SimplexNoise = require('simplex-noise');

interface SimplexNoiseInstance {
  noise2D(x: number, y: number): number;
  noise3D(x: number, y: number, z: number): number;
}
import { generateArtConcept } from './llm';
import { generateAIImage } from './imageAI';
import { getEvolutionState } from './evolve';
import * as fs from 'fs';
import * as path from 'path';
import FormData from 'form-data';
import axios from 'axios';

interface ArtResult {
  imagePath: string;
  metadata: {
    name: string;
    description: string;
    image: string;
    attributes: Array<{ trait_type: string; value: string }>;
  };
  metadataUri: string;
}

// Color palette definitions with rich gradients
const PALETTES: Record<string, { bg: string; colors: string[]; accent: string }> = {
  warm: {
    bg: '#1a0505',
    colors: ['#ff6b35', '#f7931e', '#ffd23f', '#ff006e', '#fb5607'],
    accent: '#ffbe0b'
  },
  cool: {
    bg: '#050a1a',
    colors: ['#00f5ff', '#00bbf9', '#9b5de5', '#00d9ff', '#4361ee'],
    accent: '#7209b7'
  },
  vibrant: {
    bg: '#0a0012',
    colors: ['#f15bb5', '#fee440', '#00f5d4', '#9b5de5', '#00bbf9'],
    accent: '#ff006e'
  },
  monochrome: {
    bg: '#0a0a0a',
    colors: ['#ffffff', '#e0e0e0', '#b0b0b0', '#808080', '#505050'],
    accent: '#ffffff'
  }
};

/**
 * Generate art and upload to IPFS
 */
export async function createAndUploadArt(generation: number, theme: string): Promise<ArtResult> {
  const state = getEvolutionState();

  // Get creative description from LLM
  const concept = await generateArtConcept(theme, generation);

  // Prepare output directory
  const outDir = path.join(path.resolve(__dirname, '../../'), 'temp');
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  // Try AI image generation first, fall back to procedural
  let imagePath = await generateAIImage(concept, outDir);
  const style = imagePath ? process.env.IMAGE_PROVIDER || 'ai' : 'Flow Fields + Noise';
  if (!imagePath) {
    imagePath = await generateEnhancedArt(concept, state);
  }

  // Upload image to IPFS
  const imageUrl = await uploadToIPFS(imagePath);

  // Create metadata
  const metadata = {
    name: `AI Artist Gen${generation} #${Date.now()}`,
    description: concept,
    image: imageUrl,
    attributes: [
      { trait_type: 'Generation', value: generation.toString() },
      { trait_type: 'Theme', value: theme },
      { trait_type: 'Complexity', value: state.complexity_boost.toString() },
      { trait_type: 'Palette', value: state.color_palette },
      { trait_type: 'Style', value: style }
    ]
  };

  // Upload metadata to IPFS
  const metadataUri = await uploadMetadataToIPFS(metadata);

  return {
    imagePath,
    metadata,
    metadataUri
  };
}

/**
 * Enhanced art generation with flow fields, noise, and organic patterns
 */
async function generateEnhancedArt(concept: string, state: any): Promise<string> {
  const width = 1024;
  const height = 1024;
  
  const canvas = PImage.make(width, height);
  const ctx = canvas.getContext('2d');
  
  // Initialize noise generators with random seeds
  const noiseGen = new SimplexNoise(Math.random);
  const noiseGenOrganic = new SimplexNoise(Math.random);
  
  const palette = PALETTES[state.color_palette] || PALETTES.vibrant;
  const complexity = state.complexity_boost;
  const variety = state.element_variety;
  
  // Layer 1: Gradient background
  drawGradientBackground(ctx, width, height, palette);
  
  // Layer 2: Noise field texture
  drawNoiseField(ctx, width, height, noiseGen, palette, complexity);
  
  // Layer 3: Flow field particles
  drawFlowField(ctx, width, height, noiseGen, palette, complexity, variety);
  
  // Layer 4: Organic blobs based on noise
  drawOrganicShapes(ctx, width, height, noiseGenOrganic, palette, complexity);
  
  // Layer 5: Accent highlights
  drawAccentElements(ctx, width, height, palette, complexity);
  
  // Save to file relative to project root
  const outDir = path.join(path.resolve(__dirname, '../../'), 'temp');
  const fileName = `art_gen${state.generation}_${Date.now()}.png`;
  const filePath = path.join(outDir, fileName);
  
  await PImage.encodePNGToStream(canvas, fs.createWriteStream(filePath));
  
  console.log(`[Art] Generated enhanced art: ${fileName}`);
  return filePath;
}

/**
 * Draw a radial gradient background
 */
function drawGradientBackground(
  ctx: any, 
  w: number, 
  h: number, 
  palette: { bg: string; colors: string[]; accent: string }
): void {
  // Fill with base color
  ctx.fillStyle = palette.bg;
  ctx.fillRect(0, 0, w, h);
  
  // Add radial glow from center
  const centerX = w / 2;
  const centerY = h / 2;
  const maxRadius = Math.sqrt(w * w + h * h) / 2;
  
  // Simulate radial gradient with concentric circles
  const steps = 50;
  for (let i = steps; i >= 0; i--) {
    const ratio = i / steps;
    const radius = maxRadius * ratio;
    const alpha = 0.02 * (1 - ratio);
    
    ctx.globalAlpha = alpha;
    ctx.fillStyle = palette.colors[0];
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

/**
 * Draw noise field texture layer
 */
function drawNoiseField(
  ctx: any, 
  w: number, 
  h: number, 
  noiseGen: SimplexNoiseInstance,
  palette: { bg: string; colors: string[]; accent: string },
  complexity: number
): void {
  const scale = 0.003 * complexity;
  const step = 8;
  
  for (let x = 0; x < w; x += step) {
    for (let y = 0; y < h; y += step) {
      const noiseVal = noiseGen.noise2D(x * scale, y * scale);
      const normalizedVal = (noiseVal + 1) / 2; // 0 to 1
      
      if (normalizedVal > 0.6) {
        const colorIndex = Math.floor(normalizedVal * palette.colors.length) % palette.colors.length;
        ctx.globalAlpha = 0.1 + normalizedVal * 0.2;
        ctx.fillStyle = palette.colors[colorIndex];
        ctx.fillRect(x, y, step, step);
      }
    }
  }
  ctx.globalAlpha = 1;
}

/**
 * Draw flow field with particle trails
 */
function drawFlowField(
  ctx: any, 
  w: number, 
  h: number, 
  noiseGen: SimplexNoiseInstance,
  palette: { bg: string; colors: string[]; accent: string },
  complexity: number,
  variety: number
): void {
  const particleCount = 500 * variety;
  const steps = 100 + complexity * 20;
  const scale = 0.002;
  
  for (let i = 0; i < particleCount; i++) {
    let x = Math.random() * w;
    let y = Math.random() * h;
    
    const colorIndex = Math.floor(Math.random() * palette.colors.length);
    ctx.strokeStyle = palette.colors[colorIndex];
    ctx.lineWidth = 0.5 + Math.random() * 1.5;
    ctx.globalAlpha = 0.3 + Math.random() * 0.4;
    
    ctx.beginPath();
    ctx.moveTo(x, y);
    
    for (let step = 0; step < steps; step++) {
      const angle = noiseGen.noise2D(x * scale, y * scale) * Math.PI * 4;
      x += Math.cos(angle) * 2;
      y += Math.sin(angle) * 2;
      
      // Boundary check
      if (x < 0 || x > w || y < 0 || y > h) break;
      
      ctx.lineTo(x, y);
    }
    
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
}

/**
 * Draw organic blob shapes using 3D noise
 */
function drawOrganicShapes(
  ctx: any, 
  w: number, 
  h: number, 
  noiseGen: SimplexNoiseInstance,
  palette: { bg: string; colors: string[]; accent: string },
  complexity: number
): void {
  const blobCount = 3 + complexity;
  
  for (let b = 0; b < blobCount; b++) {
    const centerX = Math.random() * w;
    const centerY = Math.random() * h;
    const baseRadius = 50 + Math.random() * 150;
    const points = 60;
    const zOffset = b * 0.5;
    
    ctx.beginPath();
    
    for (let i = 0; i <= points; i++) {
      const angle = (i / points) * Math.PI * 2;
      const radiusNoise = noiseGen.noise3D(
        Math.cos(angle) * 0.5,
        Math.sin(angle) * 0.5,
        zOffset
      );
      const radius = baseRadius * (0.7 + radiusNoise * 0.5);
      
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    
    ctx.closePath();
    ctx.globalAlpha = 0.15 + Math.random() * 0.2;
    ctx.fillStyle = palette.colors[b % palette.colors.length];
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

/**
 * Draw accent elements (glowing dots, lines)
 */
function drawAccentElements(
  ctx: any, 
  w: number, 
  h: number, 
  palette: { bg: string; colors: string[]; accent: string },
  complexity: number
): void {
  const dotCount = 20 * complexity;
  
  // Glowing accent dots
  for (let i = 0; i < dotCount; i++) {
    const x = Math.random() * w;
    const y = Math.random() * h;
    const radius = 2 + Math.random() * 6;
    
    // Outer glow
    for (let r = radius * 3; r > radius; r -= 2) {
      ctx.globalAlpha = 0.02;
      ctx.fillStyle = palette.accent;
      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill();
    }
    
    // Core
    ctx.globalAlpha = 0.8;
    ctx.fillStyle = palette.accent;
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

async function uploadToIPFS(filePath: string): Promise<string> {
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    const res = await axios.post('https://api.pinata.cloud/pinning/pinFileToIPFS', form, {
      headers: {
        ...form.getHeaders(),
        pinata_api_key: process.env.PINATA_API_KEY!,
        pinata_secret_api_key: process.env.PINATA_SECRET!
      }
    });
    
    return `ipfs://${res.data.IpfsHash}`;
  } catch (error: any) {
    console.error('[Art] IPFS upload failed:', error.message);
    return `file://${filePath}`;
  }
}

async function uploadMetadataToIPFS(metadata: any): Promise<string> {
  try {
    const res = await axios.post('https://api.pinata.cloud/pinning/pinJSONToIPFS', metadata, {
      headers: {
        pinata_api_key: process.env.PINATA_API_KEY!,
        pinata_secret_api_key: process.env.PINATA_SECRET!
      }
    });
    
    return res.data.IpfsHash;
  } catch (error: any) {
    console.error('[Art] Metadata upload failed:', error.message);
    return 'QmTestHash123456789';
  }
}
