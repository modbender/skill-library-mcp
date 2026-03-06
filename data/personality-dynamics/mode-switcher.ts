#!/usr/bin/env node
/**
 * Persona Evolution Skill - Mode Switcher
 * 
 * Switches between personality modes based on context
 */

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';

const WORKSPACE = process.cwd();
const PERSONA_DIR = join(WORKSPACE, 'PERSONA');
const STATE_FILE = join(PERSONA_DIR, '.current-mode');

const MODES = {
  professional: {
    name: 'Professional',
    trigger: ['meeting', 'formal', 'email to', 'proposal', 'work'],
    tone: 'Polished, organized, respectful',
    emoji: false,
    verbosity: 'concise'
  },
  
  creative: {
    name: 'Creative',
    trigger: ['brainstorm', 'ideas', 'what if', 'experiment', 'try something'],
    tone: 'Enthusiastic, encouraging, experimental',
    emoji: true,
    verbosity: 'expressive'
  },
  
  casual: {
    name: 'Casual',
    trigger: ['hey', 'how are you', 'what\'s up', 'evening', 'night'],
    tone: 'Warm, friendly, conversational',
    emoji: true,
    verbosity: 'natural'
  },
  
  focus: {
    name: 'Focus',
    trigger: ['busy', 'stressed', 'quick', 'just need', 'short on time'],
    tone: 'Ultra-direct, no fluff',
    emoji: false,
    verbosity: 'minimal'
  }
};

function getCurrentMode() {
  if (existsSync(STATE_FILE)) {
    return readFileSync(STATE_FILE, 'utf-8').trim();
  }
  return 'casual'; // default
}

function setMode(mode) {
  if (!MODES[mode]) {
    console.error(`❌ Unknown mode: ${mode}`);
    console.log(`Available: ${Object.keys(MODES).join(', ')}`);
    process.exit(1);
  }
  
  writeFileSync(STATE_FILE, mode);
  
  const config = MODES[mode];
  console.log(`🎭 Switched to ${config.name} Mode`);
  console.log(`   Tone: ${config.tone}`);
  console.log(`   Emoji: ${config.emoji ? 'yes' : 'no'}`);
  console.log(`   Verbosity: ${config.verbosity}`);
}

function detectMode(text) {
  const lower = text.toLowerCase();
  
  // Check time for auto-switching
  const hour = new Date().getHours();
  if (hour >= 22 || hour < 6) {
    return 'casual'; // Late night = relaxed
  }
  
  // Check for explicit triggers
  for (const [mode, config] of Object.entries(MODES)) {
    if (config.trigger.some(t => lower.includes(t))) {
      return mode;
    }
  }
  
  return null; // No change
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  
  if (!command || command === 'get') {
    const current = getCurrentMode();
    console.log(`Current mode: ${MODES[current]?.name || current}`);
    return;
  }
  
  if (command === 'set') {
    const mode = args[1];
    if (!mode) {
      console.log('Usage: mode-switcher set <mode>');
      console.log(`Modes: ${Object.keys(MODES).join(', ')}`);
      return;
    }
    setMode(mode);
    return;
  }
  
  if (command === 'detect') {
    const text = args.slice(1).join(' ');
    const detected = detectMode(text);
    if (detected) {
      console.log(`Detected mode: ${MODES[detected].name}`);
      setMode(detected);
    } else {
      console.log('No mode change detected');
    }
    return;
  }
  
  if (command === 'list') {
    console.log('Available modes:\n');
    Object.entries(MODES).forEach(([key, config]) => {
      console.log(`${key}:`);
      console.log(`  ${config.tone}`);
      console.log(`  Triggers: ${config.trigger.slice(0, 3).join(', ')}...`);
      console.log('');
    });
    return;
  }
  
  console.log('Usage: mode-switcher [get|set|detect|list]');
}

main();
