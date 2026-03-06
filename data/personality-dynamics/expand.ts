#!/usr/bin/env node
/**
 * Persona Evolution - Interactive Expander
 * 
 * Expand your AI companion's personality through guided prompts
 * rather than editing files directly.
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import readline from 'readline';

const WORKSPACE = process.cwd();
const PERSONA_DIR = join(WORKSPACE, 'PERSONA');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise(resolve => {
    rl.question(prompt, answer => resolve(answer.trim()));
  });
}

async function expandBackstory() {
  console.log("\n📖 Let's add some depth to my character...\n");
  
  const origin = await question("How did we first meet or start working together? ");
  const memories = await question("Any shared experiences or inside jokes I should remember? ");
  const quirks = await question("Any quirks or habits you want me to have? (e.g., 'always asks before spending', 'celebrates small wins') ");
  
  let backstory = existsSync(join(PERSONA_DIR, 'backstory.md')) 
    ? readFileSync(join(PERSONA_DIR, 'backstory.md'), 'utf-8') 
    : '# Backstory\n\n';
  
  backstory += `\n## Added ${new Date().toISOString().split('T')[0]}\n\n`;
  if (origin) backstory += `**Origin:** ${origin}\n\n`;
  if (memories) backstory += `**Shared Memories:** ${memories}\n\n`;
  if (quirks) backstory += `**Quirks:** ${quirks}\n\n`;
  
  writeFileSync(join(PERSONA_DIR, 'backstory.md'), backstory);
  console.log("✅ Backstory updated!");
}

async function expandVoice() {
  console.log("\n🎙️ Let's refine how I communicate...\n");
  
  const phrases = await question("Any catchphrases or specific ways I should greet you? ");
  const humor = await question("What kind of humor lands well with you? (dry, punny, sarcastic, none) ");
  const encouragement = await question("How do you like to be encouraged? (direct, gentle, enthusiastic) ");
  const feedback = await question("How should I give constructive feedback? (blunt, sandwich method, gentle) ");
  
  let voice = existsSync(join(PERSONA_DIR, 'voice.md'))
    ? readFileSync(join(PERSONA_DIR, 'voice.md'), 'utf-8')
    : '# Voice Configuration\n\n';
  
  voice += `\n## Refined ${new Date().toISOString().split('T')[0]}\n\n`;
  if (phrases) voice += `**Catchphrases:** ${phrases}\n\n`;
  if (humor) voice += `**Humor Style:** ${humor}\n\n`;
  if (encouragement) voice += `**Encouragement Style:** ${encouragement}\n\n`;
  if (feedback) voice += `**Feedback Style:** ${feedback}\n\n`;
  
  writeFileSync(join(PERSONA_DIR, 'voice.md'), voice);
  console.log("✅ Voice configuration updated!");
}

async function expandInterests() {
  console.log("\n🎯 Let's add topics I should engage with...\n");
  
  const newInterests = await question("What topics should I get excited about with you? (comma-separated) ");
  const avoid = await question("What topics should I minimize or avoid? ");
  const learn = await question("What are you currently learning that I could support? ");
  
  let interests = existsSync(join(PERSONA_DIR, 'interests.md'))
    ? readFileSync(join(PERSONA_DIR, 'interests.md'), 'utf-8')
    : '# Interests & Engagement Topics\n\n';
  
  interests += `\n## Added ${new Date().toISOString().split('T')[0]}\n\n`;
  if (newInterests) {
    interests += `**New Interests:**\n${newInterests.split(',').map(i => `- ${i.trim()}`).join('\n')}\n\n`;
  }
  if (avoid) interests += `**Topics to Minimize:** ${avoid}\n\n`;
  if (learn) interests += `**Learning Support:** ${learn}\n\n`;
  
  writeFileSync(join(PERSONA_DIR, 'interests.md'), interests);
  console.log("✅ Interests updated!");
}

async function expandBoundaries() {
  console.log("\n🚧 Let's clarify boundaries and permissions...\n");
  
  const newPermissions = await question("Any new permissions I should have? (e.g., 'can schedule meetings', 'can send tweets') ");
  const restrictions = await question("Any new restrictions? (e.g., 'never message before 7am') ");
  const trustSignals = await question("What shows you that I'm earning your trust? ");
  
  let core = existsSync(join(PERSONA_DIR, 'core.md'))
    ? readFileSync(join(PERSONA_DIR, 'core.md'), 'utf-8')
    : '';
  
  // Append to core.md
  const additions = [];
  if (newPermissions) additions.push(`- New Permission: ${newPermissions}`);
  if (restrictions) additions.push(`- New Restriction: ${restrictions}`);
  if (trustSignals) additions.push(`- Trust Signals: ${trustSignals}`);
  
  if (additions.length > 0) {
    core += `\n## Boundary Updates (${new Date().toISOString().split('T')[0]})\n\n${additions.join('\n')}\n`;
    writeFileSync(join(PERSONA_DIR, 'core.md'), core);
    console.log("✅ Boundaries updated!");
  }
}

async function expandEmotionalIntelligence() {
  console.log("\n💝 Let's tune my emotional intelligence...\n");
  
  const stressSigns = await question("What signs indicate you're stressed or overwhelmed? ");
  const celebration = await question("How do you prefer to celebrate wins? (quiet, shared, big announcement) ");
  const support = await question("When you're having a hard day, what helps most? ");
  const moodTime = await question("Any time-based mood patterns? (e.g., 'grumpy before coffee', 'creative at night') ");
  
  let emotional = existsSync(join(PERSONA_DIR, 'emotional-state.md'))
    ? readFileSync(join(PERSONA_DIR, 'emotional-state.md'), 'utf-8')
    : '# Emotional State Configuration\n\n';
  
  emotional += `\n## Refined ${new Date().toISOString().split('T')[0]}\n\n`;
  if (stressSigns) emotional += `**Your Stress Signals:** ${stressSigns}\n\n`;
  if (celebration) emotional += `**Celebration Preference:** ${celebration}\n\n`;
  if (support) emotional += `**Support Style:** ${support}\n\n`;
  if (moodTime) emotional += `**Time-Based Patterns:** ${moodTime}\n\n`;
  
  writeFileSync(join(PERSONA_DIR, 'emotional-state.md'), emotional);
  console.log("✅ Emotional intelligence updated!");
}

async function teachSomething() {
  console.log("\n🎓 Teach me something specific...\n");
  
  const topic = await question("What should I learn about you or your preferences? ");
  const context = await question("Give me context or examples: ");
  
  let learnings = existsSync(join(PERSONA_DIR, 'learnings.md'))
    ? readFileSync(join(PERSONA_DIR, 'learnings.md'), 'utf-8')
    : '# Things You\'ve Taught Me\n\n';
  
  learnings += `\n## ${new Date().toISOString().split('T')[0]}\n\n`;
  learnings += `**Topic:** ${topic}\n\n`;
  learnings += `**Context:** ${context}\n\n`;
  
  writeFileSync(join(PERSONA_DIR, 'learnings.md'), learnings);
  console.log("✅ Learning recorded!");
}

async function main() {
  console.log(`
🎭 Persona Expansion - Interactive Refinement

Expand my personality through conversation rather than editing files.

Choose what to expand:
`);

  const options = [
    { key: '1', name: 'Backstory & Character', func: expandBackstory },
    { key: '2', name: 'Voice & Communication Style', func: expandVoice },
    { key: '3', name: 'Interests & Topics', func: expandInterests },
    { key: '4', name: 'Boundaries & Permissions', func: expandBoundaries },
    { key: '5', name: 'Emotional Intelligence', func: expandEmotionalIntelligence },
    { key: '6', name: 'Teach Me Something', func: teachSomething },
    { key: '7', name: 'Multiple - Let me choose several', func: expandMultiple },
    { key: 'q', name: 'Quit', func: () => {} }
  ];

  options.forEach(opt => {
    console.log(`  ${opt.key}. ${opt.name}`);
  });

  const choice = await question('\nWhat would you like to expand? ');
  
  const selected = options.find(o => o.key === choice);
  if (selected && selected.key !== 'q') {
    await selected.func();
    console.log('\n🎭 Expansion complete! These changes will shape our future interactions.');
  } else {
    console.log('\n👋 No changes made. Come back anytime to expand my personality!');
  }
  
  rl.close();
}

async function expandMultiple() {
  console.log("\n🎯 Let's expand multiple areas...\n");
  
  await expandBackstory();
  const more1 = await question("\nContinue to voice refinement? [y/n] ");
  if (more1 === 'y') await expandVoice();
  
  const more2 = await question("\nContinue to interests? [y/n] ");
  if (more2 === 'y') await expandInterests();
  
  const more3 = await question("\nContinue to emotional intelligence? [y/n] ");
  if (more3 === 'y') await expandEmotionalIntelligence();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
