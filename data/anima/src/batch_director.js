#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
// Load .env from skill folder only (least-privilege: never read parent .env)
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });
const { generateVideo } = require('./video_engine');
const { textToSpeech } = require('./audio_engine');

// Simple batch processor for Anima
// Reads a JSON script file and generates videos sequentially
// Usage: node batch_director.js <script.json>

async function processBatch(scriptPath) {
  try {
    const scriptContent = fs.readFileSync(scriptPath, 'utf8');
    const script = JSON.parse(scriptContent);
    
    if (!Array.isArray(script)) {
      throw new Error("Script must be an array of video definitions.");
    }

    console.log(`🎬 Starting batch processing of ${script.length} videos...`);

    for (let i = 0; i < script.length; i++) {
      const item = script[i];
      console.log(`\n▶️ Processing video ${i + 1}/${script.length}: ${item.title || 'Untitled'}`);
      
      const { text, emotion, output } = item;
      
      if (!text) {
        console.warn(`⚠️ Skipping item ${i}: Missing 'text' field.`);
        continue;
      }

      // 1. Audio
      console.log(`  🔊 Generating audio...`);
      const audioPath = await textToSpeech(text);
      
      // 2. Video
      console.log(`  🎥 Rendering video...`);
      // Default to a random background if not specified, or use a specific one
      const bgPath = item.background || path.resolve(__dirname, '../assets/bg/classroom_day.jpg'); 
      const finalOutputPath = output || path.resolve(__dirname, `../output/batch_${Date.now()}_${i}.mp4`);
      
      await generateVideo({
        audioPath,
        text,
        emotion: emotion || 'neutral',
        backgroundPath: bgPath,
        outputPath: finalOutputPath
      });
      
      console.log(`  ✅ Video saved to: ${finalOutputPath}`);
    }

    console.log("\n✨ Batch processing complete!");

  } catch (error) {
    console.error("❌ Batch processing failed:", error);
    process.exit(1);
  }
}

const scriptArg = process.argv[2];
if (scriptArg) {
  processBatch(scriptArg);
} else {
  console.log("Usage: node batch_director.js <script.json>");
}

module.exports = { processBatch };
