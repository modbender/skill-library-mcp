/**
 * Debug entity extraction
 */

// Inline entity extractor (same as in storage/index.ts)
function extractEntitiesFromText(text: string): string[] {
  const entities: string[] = [];
  const patterns = [
    'Phillip', 'KakāpōHiko', 'Kakāpō', 'Hiko',
    'Elev8Advisory', 'BrandForge', 'Muninn', 'OpenClaw',
    'Sammy Clemens', 'Charlie Babbage', 'Donna Paulsen',
    'Brisbane', 'Australia', 'React', 'Node.js', 'PostgreSQL',
    'SQLite', 'Ollama', 'Stripe'
  ];
  
  for (const p of patterns) {
    if (text.toLowerCase().includes(p.toLowerCase())) {
      entities.push(p);
    }
  }
  
  return [...new Set(entities)];
}

const queries = [
  "Who are all the AI agents on Phillip's team?",
  "What projects is Phillip building?",
  "What default port does OpenClaw gateway use?",
];

console.log('🔍 Entity Extraction Debug\n');

for (const q of queries) {
  const entities = extractEntitiesFromText(q);
  console.log(`Query: "${q}"`);
  console.log(`Entities: [${entities.join(', ')}]\n`);
}