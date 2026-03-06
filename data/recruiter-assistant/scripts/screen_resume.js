#!/usr/bin/env node

/**
 * Resume Screening Script (Enhanced with Feishu Doc Creation)
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
  console.log(`\n[AGENT INSTRUCTION]: Evaluate this resume specifically for a ${lang} position with ${yoe} years of experience in Chinese (简体中文). 
  
  CRITICAL: You must evaluate the candidate's **AI Proficiency** (usage of Cursor, Copilot, LLM integration, etc.) as defined in references/hiring-criteria.md. 

  STRICT SCORING: Only experience relevant to ${lang} should contribute to the final score. Irrelevant tech stacks must not inflate the score. Data quantification is MANDATORY. Any resume without specific results (e.g., "reduced latency by 20%", "handled 10k QPS") MUST NOT score above 60.
  
  MANDATORY SECTIONS:
  - Evaluation Format: Use the exact structure and content defined in references/hiring-criteria.md.
  - Mandatory Output Language: Chinese (简体中文).
  - Detailed Pros: List at least 3-4 specific technical advantages.
  - Detailed Cons: List at least 2-3 specific technical gaps or weaknesses.
  
  ACTION PLAN:
  1. Provide the evaluation in the requested format in Chinese.
  2. IDENTIFY the name of the candidate.
  3. CALL the feishu_doc tool with action="create" to generate a doc for the candidate.
  4. CRITICAL: Use a clean, vertical layout (Headings and Paragraphs) in the Feishu doc. AVOID complex markdown/tables to ensure the content is visible.
  5. PRESENT the final report and the public Feishu document link directly in the chat.
  6. DO NOT use message attachments for the report.`);
} catch (e) {
  console.error('Error reading file:', e.message);
  process.exit(1);
}
