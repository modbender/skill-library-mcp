#!/usr/bin/env node
/**
 * Mermaid Diagram to Image Generator
 * 
 * Converts Mermaid syntax diagrams to PNG/SVG images using mermaid.ink API.
 * Zero dependencies - uses only Node.js built-in modules.
 * 
 * Usage:
 *   node mermaid-to-image.js <input.mmd> <output.png>
 *   node mermaid-to-image.js - output.png          # stdin input
 *   echo "flowchart LR; A --> B" | node mermaid-to-image.js - output.png
 */

const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * Encode Mermaid code to URL-safe Base64
 */
function encodeMermaid(code) {
    return Buffer.from(code, 'utf-8')
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');
}

/**
 * Main
 */
function main() {
    const args = process.argv.slice(2);
    
    if (args.length < 2 || args.includes('--help')) {
        console.log(`
Mermaid Diagram to Image Generator

Usage:
  node mermaid-to-image.js <input.mmd> <output.png>
  node mermaid-to-image.js <input.mmd> <output.svg>
  node mermaid-to-image.js - output.png          # stdin input

Examples:
  node mermaid-to-image.js diagram.mmd diagram.png
  echo "flowchart LR; A --> B" | node mermaid-to-image.js - output.png
`);
        process.exit(args.length === 0 ? 1 : 0);
    }
    
    const [inputPath, outputPath] = args;
    const ext = path.extname(outputPath).toLowerCase().slice(1);
    const format = (ext === 'png' || ext === 'svg') ? ext : 'png';
    
    try {
        // Read input
        const code = inputPath === '-' 
            ? fs.readFileSync(0, 'utf-8')
            : fs.readFileSync(inputPath, 'utf-8');
        
        // Encode
        const b64 = encodeMermaid(code);
        
        // Download using curl (use spawnSync to avoid shell escaping issues)
        // mermaid.ink uses /img/ for PNG and /svg/ for SVG
        const apiFormat = (format === 'svg') ? 'svg' : 'img';
        const url = `https://mermaid.ink/${apiFormat}/${b64}`;
        const dir = path.dirname(outputPath);
        
        if (dir && dir !== '.') {
            fs.mkdirSync(dir, { recursive: true });
        }
        
        const result = spawnSync('curl', ['-sL', url, '-o', outputPath], {
            encoding: 'utf-8',
            timeout: 30000
        });
        
        if (result.error) {
            throw result.error;
        }
        if (result.status !== 0) {
            throw new Error(`curl failed: ${result.stderr}`);
        }
        
        // Verify output
        const stats = fs.statSync(outputPath);
        if (stats.size === 0) {
            throw new Error('Generated file is empty');
        }
        
        console.log(`✅ Generated: ${outputPath}`);
        
    } catch (err) {
        if (err.message.includes('ENOENT')) {
            console.error(`❌ File not found: ${inputPath}`);
        } else {
            console.error(`❌ Error: ${err.message}`);
        }
        process.exit(1);
    }
}

main();
