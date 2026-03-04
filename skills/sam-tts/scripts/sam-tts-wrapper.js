#!/usr/bin/env node
/**
 * SAM TTS Wrapper - JSON output for OpenClaw integration
 * Adds proper WAV header for ffmpeg compatibility
 */

const fs = require('fs');
const path = require('path');

// Try to load sam-js
let SamJs;
try {
  SamJs = require('sam-js');
} catch (err) {
  console.error(JSON.stringify({
    success: false,
    error: 'sam-js not installed. Run: npm install'
  }));
  process.exit(1);
}

// Create WAV header for 8-bit mono PCM at 22050 Hz
function createWavHeader(dataLength) {
  const buffer = Buffer.alloc(44);
  const sampleRate = 22050;
  const numChannels = 1;
  const bitsPerSample = 8;
  const byteRate = sampleRate * numChannels * bitsPerSample / 8;
  const blockAlign = numChannels * bitsPerSample / 8;

  // RIFF chunk descriptor
  buffer.write('RIFF', 0);
  buffer.writeUInt32LE(36 + dataLength, 4);
  buffer.write('WAVE', 8);

  // fmt sub-chunk
  buffer.write('fmt ', 12);
  buffer.writeUInt32LE(16, 16); // Subchunk1Size (16 for PCM)
  buffer.writeUInt16LE(1, 20); // AudioFormat (1 for PCM)
  buffer.writeUInt16LE(numChannels, 22);
  buffer.writeUInt32LE(sampleRate, 24);
  buffer.writeUInt32LE(byteRate, 28);
  buffer.writeUInt16LE(blockAlign, 32);
  buffer.writeUInt16LE(bitsPerSample, 34);

  // data sub-chunk
  buffer.write('data', 36);
  buffer.writeUInt32LE(dataLength, 40);

  return buffer;
}

// Parse arguments
const args = process.argv.slice(2);
const options = {
  text: '',
  output: null,
  quiet: false,
  pitch: 64,
  speed: 72,
  mouth: 128,
  throat: 128,
  phonetic: false
};

for (let i = 0; i < args.length; i++) {
  const arg = args[i];
  
  if (arg === '--quiet') {
    options.quiet = true;
  } else if (arg === '--phonetic') {
    options.phonetic = true;
  } else if (arg.startsWith('--output=')) {
    options.output = arg.slice(9);
  } else if (arg.startsWith('--pitch=')) {
    options.pitch = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--speed=')) {
    options.speed = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--mouth=')) {
    options.mouth = parseInt(arg.slice(8), 10);
  } else if (arg.startsWith('--throat=')) {
    options.throat = parseInt(arg.slice(9), 10);
  } else if (!arg.startsWith('--') && !options.text) {
    options.text = arg;
  }
}

// Validate
if (!options.text) {
  console.error(JSON.stringify({
    success: false,
    error: 'No text provided. Usage: node sam-tts-wrapper.js "text" --output=/path/to/out.wav'
  }));
  process.exit(1);
}

if (!options.output) {
  console.error(JSON.stringify({
    success: false,
    error: 'No output path provided. Use --output=/path/to/out.wav'
  }));
  process.exit(1);
}

// Ensure output directory exists
const outputDir = path.dirname(options.output);
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Generate audio
try {
  const sam = new SamJs({
    pitch: options.pitch,
    speed: options.speed,
    mouth: options.mouth,
    throat: options.throat,
    phonetic: options.phonetic
  });

  const pcmData = sam.buf8(options.text);
  const wavHeader = createWavHeader(pcmData.length);
  const wavBuffer = Buffer.concat([wavHeader, Buffer.from(pcmData)]);
  
  fs.writeFileSync(options.output, wavBuffer);

  const fileSize = fs.statSync(options.output).size;

  const result = {
    success: true,
    outputPath: options.output,
    size: fileSize,
    params: {
      pitch: options.pitch,
      speed: options.speed,
      mouth: options.mouth,
      throat: options.throat
    }
  };

  if (options.quiet) {
    console.log(JSON.stringify(result));
  } else {
    console.log('SAM TTS generated successfully:');
    console.log(JSON.stringify(result, null, 2));
  }

} catch (err) {
  const error = {
    success: false,
    error: err.message
  };
  console.error(options.quiet ? JSON.stringify(error) : JSON.stringify(error, null, 2));
  process.exit(1);
}
