#!/usr/bin/env node
// Self-Review Gate v1.0
// Usage: cat output.txt | node skills/self-review/index.js

const stdin = process.stdin;
let data = '';

stdin.on('data', chunk => data += chunk);
stdin.on('end', () => {
  const output = data.trim();
  
  // Simple heuristic checks (token-based, no API call)
  const checks = {
    length: output.length > 100 ? 'pass' : 'warn',
    hasAction: /应该|需要|建议|请|please|should|need|recommend/i.test(output) ? 'pass' : 'warn',
    clarity: output.split('\n').length > 3 ? 'pass' : 'warn',
    hasStructure: /^#+ |^\* |^- /.test(output) ? 'pass' : 'warn'
  };
  
  const passCount = Object.values(checks).filter(c => c === 'pass').length;
  const total = Object.keys(checks).length;
  const score = passCount / total;
  
  console.log(`[Self-Review] Score: ${(score*100).toFixed(1)}% (${passCount}/${total} checks passed)`);
  
  if (score < 0.7) {
    console.log('[Self-Review] ⚠️  Output needs improvement:');
    for (const [check, result] of Object.entries(checks)) {
      console.log(`  - ${check}: ${result === 'pass' ? '✅' : '⚠️'}`);
    }
    console.log('[Self-Review] Suggestion: Add more structure, clear actions, or expand details.');
    process.exit(1);  // Signal: needs rework
  } else {
    console.log('[Self-Review] ✅ Approved for delivery.');
    process.exit(0);
  }
});