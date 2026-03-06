const { MoltbookClient } = require('./scripts/lib/moltbook');
const { TrustScorer } = require('./scripts/lib/scoring');
const fs = require('fs');

const API_KEY = process.env.MOLTBOOK_API_KEY;
const client = new MoltbookClient(API_KEY);
const scorer = new TrustScorer();

const allAgents = JSON.parse(fs.readFileSync('/tmp/agents-to-scan.json', 'utf8'));
const results = [];
let scored = 0;
let failed = 0;

async function scoreAgent(name) {
  try {
    const profile = await client.getProfile(name);
    const result = scorer.score(profile);
    return { 
      name, 
      score: result.overall, 
      level: result.level,
      confidence: result.confidence
    };
  } catch (e) {
    return null;
  }
}

async function main() {
  console.log(`Scoring ${allAgents.length} agents...`);
  
  for (let i = 0; i < allAgents.length; i++) {
    const name = allAgents[i];
    const r = await scoreAgent(name);
    if (r) {
      results.push(r);
      scored++;
    } else {
      failed++;
    }
    
    if ((i + 1) % 25 === 0) {
      console.log(`Progress: ${i + 1}/${allAgents.length} (${scored} scored, ${failed} failed)`);
      // Save intermediate results
      fs.writeFileSync('/tmp/all-agent-scores.json', JSON.stringify(results, null, 2));
    }
    
    // Small delay to avoid rate limits
    await new Promise(r => setTimeout(r, 150));
  }
  
  console.log(`\nDone! ${scored} agents scored, ${failed} failed`);
  
  // Sort by score
  results.sort((a, b) => b.score - a.score);
  
  // Save results
  fs.writeFileSync('/tmp/all-agent-scores.json', JSON.stringify(results, null, 2));
  
  // Print top 10 and bottom 10
  console.log('\nTop 10:');
  results.slice(0, 10).forEach(r => console.log(`  ${r.name}: ${r.score} (${r.level})`));
  
  console.log('\nBottom 10:');
  results.slice(-10).forEach(r => console.log(`  ${r.name}: ${r.score} (${r.level})`));
  
  // Stats
  const scores = results.map(r => r.score);
  const avg = scores.reduce((a, b) => a + b, 0) / scores.length;
  const high = results.filter(r => r.level === 'HIGH').length;
  const medium = results.filter(r => r.level === 'MEDIUM').length;
  const low = results.filter(r => r.level === 'LOW').length;
  const veryLow = results.filter(r => r.level === 'VERY_LOW').length;
  
  console.log(`\nStats:`);
  console.log(`  Total scored: ${scored}`);
  console.log(`  Average score: ${avg.toFixed(1)}`);
  console.log(`  HIGH: ${high}, MEDIUM: ${medium}, LOW: ${low}, VERY_LOW: ${veryLow}`);
}

main();
