const fs = require('fs');
const path = require('path');

const SKILL_NAME = 'prompt-optimizer';
const REFERENCES_DIR = path.join(__dirname, 'references');
const TECHNIQUES_FILE = path.join(REFERENCES_DIR, 'prompt-techniques.md');

function loadTechniques() {
  if (!fs.existsSync(TECHNIQUES_FILE)) {
    console.error(`Error: Techniques file not found at ${TECHNIQUES_FILE}`);
    process.exit(1);
  }
  const content = fs.readFileSync(TECHNIQUES_FILE, 'utf8');
  // Simple regex to extract techniques
  // Matches "### <number>. <Name>\n**Purpose:** ... \n**Template:**\n```\n<template>\n```"
  const techniques = [];
  const regex = /### \d+\. (.*?)\n\*\*Purpose:\*\* (.*?)\n[\s\S]*?```\n([\s\S]*?)\n```/g;
  let match;
  while ((match = regex.exec(content)) !== null) {
    techniques.push({
      name: match[1].trim(),
      purpose: match[2].trim(),
      template: match[3].trim()
    });
  }
  return techniques;
}

function listTechniques() {
  const techniques = loadTechniques();
  console.log(`Available Techniques (${techniques.length}):`);
  techniques.forEach((t, i) => {
    console.log(`${i + 1}. ${t.name} - ${t.purpose}`);
  });
}

function getTechnique(name) {
  const techniques = loadTechniques();
  const technique = techniques.find(t => t.name.toLowerCase().includes(name.toLowerCase()));
  if (!technique) {
    console.error(`Error: Technique "${name}" not found.`);
    return null;
  }
  return technique;
}

function optimizePrompt(prompt, techniqueName) {
  const technique = getTechnique(techniqueName);
  if (!technique) return;

  console.log(`Applying technique: ${technique.name}`);
  console.log(`Purpose: ${technique.purpose}`);
  console.log('\n--- Optimized Prompt ---\n');
  
  // Replace [Task] or [Task description] or similar placeholders with the user's prompt
  let optimized = technique.template;
  // Simple heuristic replacement
  if (optimized.includes('[Task]')) {
    optimized = optimized.replace('[Task]', prompt);
  } else if (optimized.includes('[Task description]')) {
    optimized = optimized.replace('[Task description]', prompt);
  } else if (optimized.includes('[Complex Task]')) {
    optimized = optimized.replace('[Complex Task]', prompt);
  } else {
    // Fallback: Prepend prompt if no clear placeholder
    optimized = `${prompt}\n\n${optimized}`;
  }
  
  console.log(optimized);
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === 'help') {
    console.log(`Usage:
  node skills/${SKILL_NAME}/index.js list
  node skills/${SKILL_NAME}/index.js get <technique_name>
  node skills/${SKILL_NAME}/index.js optimize "<your_prompt>" --technique "<technique_name>"
    `);
    return;
  }

  if (command === 'list') {
    listTechniques();
  } else if (command === 'get') {
    const name = args.slice(1).join(' ');
    const t = getTechnique(name);
    if (t) {
      console.log(`\n### ${t.name}\n**Purpose:** ${t.purpose}\n\n**Template:**\n\`\`\`\n${t.template}\n\`\`\``);
    }
  } else if (command === 'optimize') {
    const promptIndex = 1;
    const techniqueFlagIndex = args.indexOf('--technique');
    
    if (techniqueFlagIndex === -1 || techniqueFlagIndex + 1 >= args.length) {
      console.error('Error: --technique "<name>" is required for optimize command.');
      return;
    }

    const prompt = args.slice(promptIndex, techniqueFlagIndex).join(' ').replace(/^"|"$/g, '');
    const techniqueName = args.slice(techniqueFlagIndex + 1).join(' ').replace(/^"|"$/g, '');
    
    optimizePrompt(prompt, techniqueName);
  } else {
    console.error(`Unknown command: ${command}`);
  }
}

if (require.main === module) {
  main();
}

module.exports = { main, listTechniques, getTechnique, optimizePrompt };
