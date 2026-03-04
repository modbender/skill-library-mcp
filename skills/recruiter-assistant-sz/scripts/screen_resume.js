#!/usr/bin/env node

/**
 * Resume Screening Script (Dynamic Version with AI Proficiency)
 */

const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const resumePath = args[0];

// Parse simple flags
let lang = 'General Backend';
let yoe = 'Any';

for (let i = 0; i < args.length; i++) {
  if (args[i] === '--lang') lang = args[i+1];
  if (args[i] === '--yoe') yoe = args[i+1];
}

if (!resumePath) {
  console.error('Usage: node screen_resume.js <path_to_resume> --lang <language> --yoe <yoe>');
  process.exit(1);
}

try {
  const content = fs.readFileSync(resumePath, 'utf8');
  console.log('--- SYSTEM CONFIGURATION ---');
  console.log(`Target Language: ${lang}`);
  console.log(`Experience Requirement: ${yoe} years`);
  console.log('----------------------------\n');
  console.log('--- RESUME CONTENT START ---');
  console.log(content);
  console.log('--- RESUME CONTENT END ---');
  console.log(`\n[AGENT INSTRUCTION]: Evaluate this resume specifically for a ${lang} position with ${yoe} years of experience. 
  
  CRITICAL: You must also evaluate the candidate's **AI Proficiency** (usage of Cursor, Copilot, LLM integration, etc.) as defined in references/hiring-criteria.md. 
  
  Provide a score (0-100), pros/cons, and a Hire/No-Hire recommendation.`);
} catch (e) {
  console.error('Error reading file:', e.message);
  process.exit(1);
}
