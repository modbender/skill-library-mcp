/**
 * Debug q13 - why is it pulling wrong memory?
 */

import MemoryStore from '../storage/index.js';

async function run() {
  console.log('🔍 Debugging q13\n');
  
  const store = new MemoryStore('/tmp/debug-q13.db');
  
  // Store the key facts
  const keyFacts = [
    { content: 'Elev8Advisory is an AI-powered HR tool that helps small businesses create HR policies automatically', entities: ['Elev8Advisory'], salience: 0.8 },
    { content: 'BrandForge is an AI-powered branding tool with $320 revenue', entities: ['BrandForge'], salience: 0.8 },
    { content: 'Muninn is a memory system using SQLite storage and Nomic embeddings via Ollama, stores episodic/semantic/procedural memories', entities: ['Muninn'], salience: 0.8 },
    { content: 'Current priority: Elev8Advisory first, then BrandForge (updated Feb 22)', entities: ['Elev8Advisory', 'BrandForge'], salience: 0.8 },
    { content: 'The programme is scheduled to launch in Q3', entities: ['programme'], salience: 0.2 },
  ];
  
  for (const fact of keyFacts) {
    await store.remember(fact.content, 'semantic', {
      entities: fact.entities,
      salience: fact.salience
    });
  }
  
  const query = 'What projects is Phillip building and what are their current statuses?';
  console.log(`Query: "${query}"\n`);
  
  const results = await store.recall(query, { limit: 5 });
  
  console.log('Top 5 results:');
  results.forEach((r, i) => {
    console.log(`${i + 1}. [sal: ${r.salience}] ${r.content.slice(0, 80)}...`);
  });
  
  store.close();
}

run().catch(console.error);