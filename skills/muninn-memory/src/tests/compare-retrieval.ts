/**
 * Compare simple vs hybrid retrieval
 */

import MemoryStore from '../storage/index.js';

async function run() {
  console.log('🔍 Comparing Simple vs Hybrid Retrieval\n');
  
  const store = new MemoryStore('/tmp/compare-test.db');
  
  // Store same data as benchmark
  const facts = [
    { content: 'Tech stack: React frontend, Node.js backend, PostgreSQL', salience: 0.8 },
    { content: 'Muninn uses Nomic embed text via Ollama for embeddings', salience: 0.8 },
    { content: 'Current priority: Elev8Advisory first (updated Feb 22)', salience: 0.8 },
    { content: 'Phillip prefers Australian English for casual, British for formal documents', salience: 0.8 },
    { content: 'Elev8Advisory target revenue is $1000/month (updated from $2000)', salience: 0.8 },
  ];
  
  // Simulate benchmark volume: 17 semantic + 65 episodic
  const conversations = [
    '[2026-02-10] assistant: Elev8Advisory sounds interesting! AI for HR is a growing space.',
    '[2026-02-10] user: About 72% complete. Stripe integration is live.',
    '[2026-02-12] assistant: BrandForge sounds like a natural complement to Elev8Advisory.',
    '[2026-02-12] user: Yes, both use React frontend and Node.js backend with PostgreSQL.',
    '[2026-02-15] assistant: Nice classification. What\'s the embedding model?',
    // Add more episodic to match benchmark ratio
    '[2026-02-10] user: I\'m building a SaaS called Elev8Advisory.',
    '[2026-02-10] assistant: That\'s a clear value proposition.',
    '[2026-02-10] user: Need to finish the AI content generator.',
    '[2026-02-10] assistant: Those are critical features.',
    '[2026-02-10] user: I work with an AI agent named KakāpōHiko.',
    '[2026-02-12] user: I prefer Australian English spelling in all content.',
    '[2026-02-12] assistant: Got it! I\'ll use Australian English.',
    '[2026-02-12] user: I hate corporate jargon.',
    '[2026-02-12] assistant: Noted - direct, authentic communication.',
    '[2026-02-12] user: My background is in psychology and business.',
    '[2026-02-12] assistant: Psychology and business - powerful combination.',
    '[2026-02-12] user: BrandForge is another one - AI-powered branding tool.',
    '[2026-02-12] assistant: Same tech stack?',
    '[2026-02-12] user: Yes, both use React frontend.',
    '[2026-02-15] assistant: Good to know. Is that configurable?',
  ];
  
  // Store semantic memories
  for (const fact of facts) {
    await store.remember(fact.content, 'semantic', { salience: fact.salience });
  }
  
  // Store conversation turns
  for (const conv of conversations) {
    await store.remember(conv, 'episodic', { salience: 0.5 });
  }
  
  console.log(`Stored ${facts.length} semantic + ${conversations.length} episodic memories\n`);
  
  // Test query
  const query = 'What tech stack does Phillip use for his projects?';
  
  // Get results
  const results = await store.recall(query, { limit: 5 });
  
  console.log(`Query: "${query}"\n`);
  console.log('Top 5 results:');
  results.forEach((r, i) => {
    console.log(`${i + 1}. [${r.type}] [sal: ${r.salience}] ${r.content.slice(0, 60)}...`);
  });
  
  // Check if semantic memory is in top 3
  const top3 = results.slice(0, 3);
  const hasSemanticInTop3 = top3.some(r => r.type === 'semantic');
  console.log(`\nSemantic memory in top 3: ${hasSemanticInTop3 ? '✅' : '❌'}`);
  
  store.close();
}

run().catch(console.error);
