#!/usr/bin/env node
/**
 * SAM TTS CLI - Human-readable output
 * 
 * Usage: node sam-tts.js "text" output.wav [options]
 */

const fs = require('fs');

// Try to load sam-js
let SamJs;
try {
  SamJs = require('sam-js');
} catch (err) {
  console.error('Error: sam-js not installed.');
  console.error('Run: npm install');
  process.exit(1);
}

const args = process.argv.slice(2);

if (args.length < 2) {
  console.log('SAM TTS - Software Automatic Mouth');
  console.log('');
  console.log('Usage: node sam-tts.js "text" output.wav [options]');
  console.log('');
  console.log('Options:');
  console.log('  --pitch=N    Voice pitch (0-255, default: 64)');
  console.log('  --speed=N    Speech speed (1-255, default: 72, lower=faster)');
  console.log('  --mouth=N    Mouth cavity size (0-255, default: 128)');
  console.log('  --throat=N   Throat size (0-255, default: 128)');
  console.log('  --phonetic   Input is phonetic notation');
  console.log('');
  console.log('Examples:');
  console.log('  node sam-tts.js "Hello world" hello.wav');
  console.log('  node sam-tts.js "Hello world" hello.wav --pitch=80 --speed=60');
  process.exit(0);
}

const text = args[0];
const outputPath = args[1];

// Parse options
const options = {
  pitch: 64,
  speed: 72,
  mouth: 128,
  throat: 128,
  phonetic: false
};

for (let i = 2; i < args.length; i++) {
  const arg = args[i];
  if (arg.startsWith('--pitch=')) {
    options.pitch = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--speed=')) {
    options.speed = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--mouth=')) {
    options.mouth = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--throat=')) {
    options.throat = parseInt(arg.slice(9), 10);
  } else if (arg === '--phonetic') {
    options.phonetic = true;
  }
}

// Generate
try {
  console.log(`Generating SAM audio...`);
  console.log(`Text: "${text}"`);
  console.log(`Output: ${outputPath}`);
  console.log(`Pitch: ${options.pitch}, Speed: ${options.speed}, Mouth: ${options.mouth}, Throat: ${options.throat}`);
  
  const sam = new SamJs({
    pitch: options.pitch,
    speed: options.speed,
    mouth: options.mouth,
    throat: options.throat,
    phonetic: options.phonetic
  });
  
  const wavBuffer = sam.buf8(text);
  fs.writeFileSync(outputPath, Buffer.from(wavBuffer));
  
  const stats = fs.statSync(outputPath);
  
  console.log(`✓ Generated: ${outputPath}`);
  console.log(`  Size: ${stats.size} bytes`);
  
} catch (err) {
  console.error(`Error: ${err.message}`);
  process.exit(1);
}
