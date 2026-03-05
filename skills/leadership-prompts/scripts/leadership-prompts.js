#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

const PROMPTS_FILE = path.join(__dirname, '..', 'prompts.json');

function loadPrompts() {
  return JSON.parse(fs.readFileSync(PROMPTS_FILE, 'utf8'));
}

function getCategories(prompts) {
  const cats = {};
  for (const p of prompts) {
    cats[p.category] = (cats[p.category] || 0) + 1;
  }
  return cats;
}

function printPrompt(p, verbose = true) {
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`🎯 ${p.title}`);
  console.log(`   Category: ${p.category} | ID: ${p.id}`);
  console.log(`${'─'.repeat(60)}`);
  if (verbose) {
    console.log(`\n📋 PROMPT:\n${p.prompt}`);
    console.log(`\n🕐 WHEN TO USE:\n${p.context}`);
    console.log(`\n📄 OUTPUT FORMAT:\n${p.output_format}`);
    console.log(`\n💡 EXAMPLE:\n${p.example}`);
  }
  console.log();
}

const [,, command, ...args] = process.argv;
const query = args.join(' ');

switch (command) {
  case 'list': {
    const prompts = loadPrompts();
    const cats = getCategories(prompts);
    console.log('\n📂 Leadership Prompt Categories:\n');
    for (const [cat, count] of Object.entries(cats)) {
      console.log(`  ${cat} (${count} prompts)`);
    }
    console.log(`\n  Total: ${prompts.length} prompts`);
    console.log('\nUse: node leadership-prompts.js category "Category Name"');
    break;
  }

  case 'random': {
    const prompts = loadPrompts();
    const filtered = query
      ? prompts.filter(p => p.category.toLowerCase().includes(query.toLowerCase()))
      : prompts;
    if (!filtered.length) { console.log('No prompts found.'); break; }
    printPrompt(filtered[Math.floor(Math.random() * filtered.length)]);
    break;
  }

  case 'search': {
    if (!query) { console.log('Usage: leadership-prompts.js search <keyword>'); break; }
    const prompts = loadPrompts();
    const q = query.toLowerCase();
    const results = prompts.filter(p =>
      p.title.toLowerCase().includes(q) ||
      p.prompt.toLowerCase().includes(q) ||
      p.context.toLowerCase().includes(q) ||
      p.category.toLowerCase().includes(q)
    );
    if (!results.length) { console.log(`No prompts matching "${query}"`); break; }
    console.log(`\n🔍 ${results.length} prompt(s) matching "${query}":\n`);
    for (const p of results) printPrompt(p, false);
    break;
  }

  case 'show': {
    if (!query) { console.log('Usage: leadership-prompts.js show <prompt-id>'); break; }
    const prompts = loadPrompts();
    const p = prompts.find(p => p.id === query);
    if (!p) { console.log(`No prompt with ID "${query}". Use 'list' or 'search' to find IDs.`); break; }
    printPrompt(p);
    break;
  }

  case 'category': {
    if (!query) { console.log('Usage: leadership-prompts.js category "Category Name"'); break; }
    const prompts = loadPrompts();
    const q = query.toLowerCase();
    const results = prompts.filter(p => p.category.toLowerCase().includes(q));
    if (!results.length) { console.log(`No category matching "${query}"`); break; }
    console.log(`\n📂 ${results[0].category} (${results.length} prompts):\n`);
    for (const p of results) printPrompt(p, false);
    break;
  }

  default:
    console.log(`
🎯 Leadership Prompts CLI

Usage:
  node leadership-prompts.js list                    List all categories
  node leadership-prompts.js random [category]       Random prompt (optionally from category)
  node leadership-prompts.js search <keyword>        Search prompts by keyword
  node leadership-prompts.js show <prompt-id>        Show a specific prompt
  node leadership-prompts.js category "Name"         All prompts in a category
`);
}
