#!/usr/bin/env node

/**
 * Batch Example - Generate multiple devotionals
 */

require('dotenv').config();
const VoiceDevotion = require('../scripts/voice-devotional');

async function main() {
  const vd = new VoiceDevotion({
    apiKey: process.env.ELEVEN_LABS_API_KEY,
    outputDir: './output'
  });

  try {
    console.log('🎙️ Batch Generation Example\n');

    // Define themes for a week
    const weekThemes = [
      'peace',
      'hope',
      'faith',
      'love',
      'strength',
      'joy',
      'grace'
    ];

    console.log(`Generating ${weekThemes.length} devotionals...\n`);

    const results = await vd.generateBatch(weekThemes, {
      voiceId: 'josh',
      delay: 2000,  // 2 second delay between requests
      includeManifest: true
    });

    console.log(`\n✓ Generated ${results.length} devotionals\n`);

    results.forEach((result, index) => {
      console.log(`${index + 1}. ${result.lesson.theme}`);
      console.log(`   File: ${result.lesson.theme}.mp3`);
      console.log(`   Duration: ${result.lesson.estimatedDuration}s\n`);
    });

    console.log('✅ Batch generation completed!');
    console.log('Check ./output/ for all generated files.');

  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
