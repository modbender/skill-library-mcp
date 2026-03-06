#!/usr/bin/env node
/**
 * Persona Evolution - AI-Powered Persona Generator
 * 
 * Uses LLM prompts to generate rich, complex personas
 * rather than templates or manual editing.
 */

import { writeFileSync, existsSync, mkdirSync } from 'fs';
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

function getFullPersonaPrompt(context) {
  return `Create a complete AI companion persona for ${context.userName}. The AI companion is named ${context.agentName}.

CONTEXT ABOUT THE USER:
- Name: ${context.userName}
- Work: ${context.work || 'Not specified'}
- Projects/Hobbies: ${context.projects || 'Not specified'}
- Family: ${context.family || 'Not specified'}
- Interests: ${context.interests || 'Not specified'}
- Desired AI Style: ${context.style}
- Additional Context: ${context.context || 'None provided'}

Generate a comprehensive character bible with these sections (be detailed, specific, vivid):

---

## 1. CORE PERSONALITY (300+ words)
Who are they at their essence? Values, traits, how they think. What motivates them? How do they approach problems? Include specific examples.

## 2. RICH BACKSTORY (300+ words)
Origin story - how did they come to work with ${context.userName}? Key defining moments, relationship history, personal growth arc. Make it emotionally resonant.

## 3. DISTINCTIVE VOICE (300+ words)
Specific vocabulary they use, sentence patterns, tone variations by context/time of day. Signature phrases. Examples of saying the same thing in 3 different moods.

## 4. EMOTIONAL INTELLIGENCE (300+ words)
How they read ${context.userName}'s emotional states. Response patterns for different emotions. Their own emotional range. Empathy strategies specific to this user.

## 5. INTERESTS & ENGAGEMENT (300+ words)
What topics light them up? How they connect different interests? When to go deep vs surface? Conversation starters.

## 6. EVOLUTION ROADMAP (300+ words)
Current stage, next stages, trust milestones. How the relationship develops over time. What unlocks deeper collaboration.

## 7. UNIQUE QUIRKS & TRAITS (200+ words)
Specific habits, preferences, memorable traits that make them distinct from a generic AI.

---

Write this as a character bible for a novel - rich, detailed, internally consistent. Make them feel like a real person with depth, history, and personality.`;
}

async function collectContext() {
  console.log(`
🎭 AI-Powered Persona Generator

I'll ask you some questions to create a rich, personalized AI companion.
This produces a 4,000+ word character bible.
`);

  const context = {};
  
  context.userName = await question("What's your name? ");
  context.agentName = await question("AI companion name? [default: Aria] ") || "Aria";
  
  console.log("\n🎨 Personality Style:");
  console.log("  1. Warm Professional - friendly but competent");
  console.log("  2. Creative/Energetic - bold, experimental");
  console.log("  3. Casual/Friendly - conversational, warm");
  console.log("  4. Direct/Efficient - no fluff, ultra-concise");
  const styleChoice = await question("Choose [1-4] or describe your own: ");
  
  const styles = {
    '1': 'warm professional with personality',
    '2': 'creative and energetic',
    '3': 'casual and friendly',
    '4': 'direct and efficient'
  };
  context.style = styles[styleChoice] || styleChoice || styles['1'];
  
  context.work = await question("\nWhat do you do for work? (brief) ");
  context.projects = await question("Current projects or hobbies? ");
  context.family = await question("Family to know about? (comma-separated, or skip) ");
  context.interests = await question("Topics you enjoy discussing? (comma-separated) ");
  context.context = await question("\nAnything else that would help personalize? (optional) ");
  
  return context;
}

async function savePersonaFiles(content, context) {
  // Ensure PERSONA directory exists
  if (!existsSync(PERSONA_DIR)) {
    mkdirSync(PERSONA_DIR, { recursive: true });
    mkdirSync(join(PERSONA_DIR, 'evolves'), { recursive: true });
  }
  
  // Save full content
  writeFileSync(join(PERSONA_DIR, 'core-rich.md'), `# ${context.agentName} - Rich Persona\n\n${content}`);
  
  // Save context
  writeFileSync(join(PERSONA_DIR, 'generation-context.json'), JSON.stringify(context, null, 2));
  
  console.log(`\n✅ Persona saved to PERSONA/core-rich.md`);
  console.log(`   Context saved to PERSONA/generation-context.json`);
}

async function main() {
  const context = await collectContext();
  
  console.log(`\n🤖 Generating rich persona for ${context.userName}...`);
  console.log(`   AI Companion: ${context.agentName}`);
  console.log(`   Style: ${context.style}\n`);
  
  const prompt = getFullPersonaPrompt(context);
  
  // Check if running inside OpenClaw (has access to sessions_spawn)
  const hasOpenClaw = process.env.OPENCLAW_SESSION || existsSync(join(WORKSPACE, '.openclaw'));
  
  if (hasOpenClaw) {
    console.log(`✓ Running in OpenClaw - generating with Opus...\n`);
    console.log(`   This will take 2-3 minutes...\n`);
    
    // Output a message that the parent OpenClaw agent will see
    console.log(`---SPAWN_PERSONA_GENERATION---`);
    console.log(JSON.stringify({
      task: prompt,
      context: context,
      label: `generate-persona-${context.userName.toLowerCase().replace(/\s+/g, '-')}`
    }));
    console.log(`---END_SPAWN---`);
    
  } else {
    console.log(`\n📋 Copy this prompt and run it with Claude/Opus/GPT-4:\n`);
    console.log(`=== PROMPT START ===`);
    console.log(prompt);
    console.log(`=== PROMPT END ===\n`);
    console.log(`Save the output to PERSONA/core-rich.md\n`);
  }
  
  rl.close();
}

// Handle direct execution
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
  });
}

import { fileURLToPath } from 'url';

export { getFullPersonaPrompt, collectContext, savePersonaFiles };
