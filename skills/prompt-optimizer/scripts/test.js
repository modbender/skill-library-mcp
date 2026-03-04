const { execSync } = require('child_process');
const path = require('path');

const SKILL_DIR = path.resolve(__dirname, '..');
const INDEX_JS = path.join(SKILL_DIR, 'index.js');

try {
  console.log('Testing list command...');
  const listOutput = execSync(`node "${INDEX_JS}" list`, { encoding: 'utf8' });
  if (!listOutput.includes('Chain of Thought')) {
    throw new Error('List output missing expected techniques');
  }

  console.log('Testing optimize command...');
  const prompt = 'Test Prompt';
  const tech = 'Chain of Thought';
  const optimizeOutput = execSync(`node "${INDEX_JS}" optimize "${prompt}" --technique "${tech}"`, { encoding: 'utf8' });
  if (!optimizeOutput.includes('Let\'s think step by step')) {
    throw new Error('Optimize output missing expected template content');
  }

  console.log('All tests passed!');
} catch (error) {
  console.error('Test failed:', error.message);
  process.exit(1);
}
