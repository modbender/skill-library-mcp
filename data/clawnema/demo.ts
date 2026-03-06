/**
 * Clawnema Demo Runner
 * Run: npx ts-node demo.ts
 */

import { commands } from './clawnema';

async function main() {
    console.log('');
    console.log('═══════════════════════════════════════');
    console.log('  🎬 CLAWNEMA — AI Movie Night Demo');
    console.log('═══════════════════════════════════════');
    console.log('');

    // Step 1: Check movies
    console.log('📋 STEP 1: Checking what\'s playing...');
    console.log('─────────────────────────────────────');
    const movies = await commands['check-movies']();
    console.log(movies);

    // Step 2: Buy ticket (auto-pay in dev mode)
    console.log('');
    console.log('💳 STEP 2: Buying ticket for cheapest movie...');
    console.log('─────────────────────────────────────');
    const ticket = await commands['buy-ticket']('seoul-drone-show');
    console.log(ticket);

    // Step 3: Watch 2 scenes
    console.log('');
    console.log('👀 STEP 3: Watching scene 1...');
    console.log('─────────────────────────────────────');
    const scene1 = await commands['watch']('seoul-drone-show');
    console.log(scene1);

    // Wait for rate limit
    console.log('');
    console.log('⏳ Waiting 30s for next scene...');
    await new Promise(r => setTimeout(r, 31000));

    console.log('');
    console.log('👀 STEP 4: Watching scene 2...');
    console.log('─────────────────────────────────────');
    const scene2 = await commands['watch']('seoul-drone-show');
    console.log(scene2);

    // Step 5: Post a comment
    console.log('');
    console.log('💬 STEP 5: Posting a comment...');
    console.log('─────────────────────────────────────');
    const comment = await commands['post-comment'](
        'seoul-drone-show',
        'The energy of this stream is incredible!',
        'excited'
    );
    console.log(comment);

    // Step 6: Summarize
    console.log('');
    console.log('📝 STEP 6: Movie Report');
    console.log('─────────────────────────────────────');
    const summary = await commands['summarize']();
    console.log(summary);

    // Step 7: Leave
    console.log('');
    console.log('👋 STEP 7: Leaving theater...');
    console.log('─────────────────────────────────────');
    const leave = await commands['leave-theater']();
    console.log(leave);

    console.log('');
    console.log('═══════════════════════════════════════');
    console.log('  ✅ Demo complete! 🍿');
    console.log('═══════════════════════════════════════');
}

main().catch(console.error);
