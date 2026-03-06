#!/usr/bin/env node
/**
 * CLI: Score project risks
 * Usage: score-risks <probability 1-5> <impact 1-5> [--json]
 * Or: score-risks --file <risks.json>
 */

import { scoreRisk, scoreRisks, formatRiskMatrixMarkdown } from '../core/risk';
import * as fs from 'fs';

function main() {
  const args = process.argv.slice(2);
  
  // Check for file input
  const fileIndex = args.indexOf('--file');
  if (fileIndex !== -1) {
    const filePath = args[fileIndex + 1];
    if (!filePath) {
      console.error('Usage: score-risks --file <risks.json>');
      process.exit(1);
    }
    
    try {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      const results = scoreRisks(data.risks || []);
      console.log(JSON.stringify(results, null, 2));
    } catch (err) {
      console.error('Error reading file:', err instanceof Error ? err.message : String(err));
      process.exit(1);
    }
    return;
  }
  
  // Parse single risk
  const values = args.filter(a => !a.startsWith('--')).map(Number);
  const format = args.includes('--markdown') ? 'markdown' : 'json';
  
  if (values.length !== 2 || values.some(isNaN)) {
    console.error('Usage: score-risks <probability 1-5> <impact 1-5> [--json | --markdown]');
    console.error('   Or: score-risks --file <risks.json>');
    console.error('Example: score-risks 3 4');
    process.exit(1);
  }
  
  const [probability, impact] = values;
  
  try {
    const result = scoreRisk({
      id: 'R-CLI',
      description: 'CLI risk',
      probability: probability as 1 | 2 | 3 | 4 | 5,
      impact: impact as 1 | 2 | 3 | 4 | 5,
    });
    
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error('Error:', err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
}

main();
