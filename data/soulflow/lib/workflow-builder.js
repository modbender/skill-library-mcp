#!/usr/bin/env node

/**
 * Interactive workflow builder
 * Helps create custom workflow JSON definitions
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function main() {
  console.log('\n🌊 SoulFlow Workflow Builder\n');
  
  const id = await question('Workflow ID (lowercase-with-dashes): ');
  const name = await question('Workflow Name (human-readable): ');
  const description = await question('Description: ');
  
  console.log('\n📋 Define Steps\n');
  console.log('For each step, provide:');
  console.log('- ID: step identifier (e.g. "research", "draft", "edit")');
  console.log('- Name: human-readable name');
  console.log('- Input: the prompt/instructions for the agent');
  console.log('- Expects: what output format to expect (e.g. "STATUS: done")');
  console.log('\nType "done" when finished adding steps.\n');
  
  const steps = [];
  let stepNum = 1;
  
  while (true) {
    const stepId = await question(`\nStep ${stepNum} ID (or "done"): `);
    if (stepId.toLowerCase() === 'done') break;
    
    const stepName = await question(`Step ${stepNum} Name: `);
    
    console.log('\nStep Input (multi-line, end with empty line):');
    const inputLines = [];
    while (true) {
      const line = await question('> ');
      if (line === '') break;
      inputLines.push(line);
    }
    const input = inputLines.join('\n');
    
    const expects = await question('Expects (e.g. "STATUS: done"): ');
    const maxRetries = parseInt(await question('Max Retries (default: 1): ') || '1');
    
    steps.push({
      id: stepId,
      name: stepName,
      input,
      expects,
      maxRetries
    });
    
    stepNum++;
  }
  
  const workflow = {
    id,
    name,
    version: 1,
    description,
    steps
  };
  
  const workflowsDir = path.join(__dirname, '..', 'workflows');
  const filePath = path.join(workflowsDir, `${id}.workflow.json`);
  
  // Ensure workflows dir exists
  if (!fs.existsSync(workflowsDir)) {
    fs.mkdirSync(workflowsDir, { recursive: true });
  }
  
  fs.writeFileSync(filePath, JSON.stringify(workflow, null, 2));
  
  console.log(`\n✅ Workflow saved to: ${filePath}\n`);
  console.log(`Run it with: node soulflow.js run ${id} "your task description"\n`);
  
  rl.close();
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
