#!/usr/bin/env node

/**
 * Basic Example - Using voice-devotional programmatically
 */

require('dotenv').config();
const VoiceDevotion = require('../scripts/voice-devotional');

async function main() {
  // Initialize
  const vd = new VoiceDevotion({
    apiKey: process.env.ELEVEN_LABS_API_KEY,
    outputDir: './output'
  });

  try {
    console.log('🎙️ Voice Devotional - Basic Examples\n');

    // Example 1: Daily devotional
    console.log('📖 Generating daily devotional on peace...');
    const daily = await vd.generateDaily({
      theme: 'peace',
      voiceId: 'josh'
    });
    console.log(`✓ Created: ${daily.audioPath}`);
    console.log(`  Duration: ${daily.lesson.estimatedDuration}s\n`);

    // Example 2: Scripture reading
    console.log('📖 Generating scripture reading (John 3:16)...');
    const scripture = await vd.generateScripture({
      passage: 'John 3:16',
      voiceId: 'josh',
      includeNotes: true
    });
    console.log(`✓ Created: ${scripture.audioPath}`);
    console.log(`  Passage: ${scripture.scripture.reference}\n`);

    // Example 3: Reading plan
    console.log('📚 Generating 7-day hope study plan...');
    const plan = await vd.generatePlan({
      topic: 'hope',
      days: 7,
      voiceId: 'josh'
    });
    console.log(`✓ Created ${plan.results.length} files at: ${plan.planDir}\n`);

    // Example 4: Roman Road
    console.log('⛪ Generating Roman Road gospel presentation...');
    const romanRoad = await vd.generateRomanRoad({
      voiceId: 'chris',
      length: 'standard'
    });
    console.log(`✓ Created: ${romanRoad.audioPath}\n`);

    console.log('✅ All examples completed successfully!');
    console.log('\nCheck ./output/ for generated audio files.');

  } catch (err) {
    console.error('❌ Error:', err.message);
    process.exit(1);
  }
}

main();
