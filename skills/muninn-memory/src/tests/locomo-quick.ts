/**
 * Quick LOCOMO test — skip slow embedding generation
 */

import MemoryStore from '../storage/index.js';

const keyFacts = [
  { content: 'Phillip lives in Brisbane, Australia (timezone AEST)', entities: ['Phillip', 'Brisbane', 'Australia'] },
  { content: 'Elev8Advisory is an AI-powered HR tool that helps small businesses create HR policies automatically', entities: ['Elev8Advisory'] },
  { content: 'Elev8Advisory target revenue is $1000/month (updated from $2000)', entities: ['Elev8Advisory'] },
  { content: 'BrandForge is an AI-powered branding tool with $320 revenue', entities: ['BrandForge'] },
  { content: 'Tech stack: React frontend, Node.js backend, PostgreSQL', entities: ['React', 'Node.js', 'PostgreSQL'] },
  { content: 'Muninn is a memory system using SQLite storage and Nomic embeddings via Ollama, stores episodic/semantic/procedural memories', entities: ['Muninn', 'SQLite', 'Ollama'] },
  { content: 'OpenClaw gateway default port is 18789, configurable via OPENCLAW_PORT environment variable', entities: ['OpenClaw'] },
  { content: 'Phillip prefers Australian English for casual, British for formal documents', entities: ['Phillip'] },
  { content: 'KakāpōHiko handles strategy, Sammy Clemens handles content, Charlie Babbage handles code, Donna Paulsen handles operations', entities: ['KakāpōHiko', 'Sammy Clemens', 'Charlie Babbage', 'Donna Paulsen'] },
  { content: "Kakāpō is the world's rarest parrot, Hiko means lightning in Māori", entities: ['KakāpōHiko'] },
  { content: 'Muninn Phase 1 complete: 100% router accuracy, 91% entity precision', entities: ['Muninn'] },
  { content: 'Elev8Advisory has a customer paying $500/month for HR policy generation', entities: ['Elev8Advisory'] },
  { content: 'Current priority: Elev8Advisory first, then BrandForge (updated Feb 22)', entities: ['Elev8Advisory', 'BrandForge'] },
];

const questions = [
  { id: 'q14', query: 'What default port does OpenClaw gateway use?', expected: '18789' },
  { id: 'q11', query: 'Who are all the AI agents on Phillip\'s team?', expected: 'KakāpōHiko' },
  { id: 'q13', query: 'What projects is Phillip building?', expected: 'Elev8Advisory' },
];

async function run() {
  console.log('⚡ Quick LOCOMO Test\n');
  
  const store = new MemoryStore('/tmp/locomo-quick.db');
  
  for (const fact of keyFacts) {
    await store.remember(fact.content, 'semantic', { entities: fact.entities, salience: 0.8 });
  }
  
  console.log(`Stored ${keyFacts.length} memories\n`);
  
  for (const q of questions) {
    const results = await store.recall(q.query, { limit: 3 });
    const topResult = results[0]?.content || 'N/A';
    const passed = topResult.toLowerCase().includes(q.expected.toLowerCase());
    console.log(`${q.id}: ${passed ? '✅' : '❌'} "${topResult.slice(0, 60)}..."`);
  }
  
  store.close();
}

run().catch(console.error);