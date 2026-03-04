#!/usr/bin/env node
/**
 * Voice.ai TTS CLI
 * Usage: node scripts/tts.js --text "Hello!" --voice ellie --output hello.mp3
 */

const VoiceAI = require('../voice-ai-tts-sdk');
const fs = require('fs');
const path = require('path');

const VOICES_PATH = path.join(__dirname, '..', 'voices.json');
let cachedVoiceData = null;

function loadVoiceData() {
  if (!cachedVoiceData) {
    const raw = fs.readFileSync(VOICES_PATH, 'utf8');
    cachedVoiceData = JSON.parse(raw);
  }
  return cachedVoiceData;
}

function getVoiceMap() {
  const data = loadVoiceData();
  return data.voices || {};
}

function listVoiceNames() {
  return Object.keys(getVoiceMap()).sort().join(', ');
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { output: 'output.mp3', stream: false };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--text' && args[i + 1]) opts.text = args[++i];
    else if (args[i] === '--voice' && args[i + 1]) opts.voice = args[++i];
    else if (args[i] === '--output' && args[i + 1]) opts.output = args[++i];
    else if (args[i] === '--stream') opts.stream = true;
    else if (args[i] === '--help') {
      console.log(`
Voice.ai TTS CLI

Usage:
  node scripts/tts.js --text "Hello!" --voice ellie
  node scripts/tts.js --text "Long text..." --voice oliver --stream
  node scripts/tts.js --text "Custom output" --output custom.mp3

Options:
  --text     Text to convert to speech (required)
  --voice    Voice name: ${listVoiceNames()}
  --output   Output file (default: output.mp3)
  --stream   Use streaming mode (good for long texts)

Environment:
  VOICE_AI_API_KEY  Your Voice.ai API key
`);
      process.exit(0);
    }
  }
  return opts;
}

async function main() {
  const opts = parseArgs();
  
  if (!opts.text) {
    console.error('Error: --text is required');
    process.exit(1);
  }
  
  const apiKey = process.env.VOICE_AI_API_KEY;
  if (!apiKey) {
    console.error('Error: VOICE_AI_API_KEY is required (set it as an environment variable)');
    process.exit(1);
  }
  
  const client = new VoiceAI(apiKey);
  const voiceMap = getVoiceMap();
  const voiceName = opts.voice ? opts.voice.toLowerCase() : undefined;
  const voiceEntry = voiceName ? voiceMap[voiceName] : undefined;
  if (voiceName && !voiceEntry) {
    console.error(`Error: Unknown voice "${opts.voice}". Available voices: ${listVoiceNames()}`);
    process.exit(1);
  }
  const voiceId = voiceEntry ? voiceEntry.voice_id : undefined;
  
  console.log(`Generating speech${opts.stream ? ' (streaming)' : ''}...`);
  
  if (opts.stream) {
    await client.streamSpeechToFile({ text: opts.text, voice_id: voiceId }, opts.output);
  } else {
    await client.generateSpeechToFile({ text: opts.text, voice_id: voiceId }, opts.output);
  }
  
  console.log(`✅ Saved to ${opts.output}`);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
