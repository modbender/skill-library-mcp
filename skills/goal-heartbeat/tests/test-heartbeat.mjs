import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_DIR = path.join(__dirname, '..');
const ROOT_DIR = path.join(SKILL_DIR, '../../..');

const testResults = {
  total: 0,
  passed: 0,
  failed: []
};

function checkFile(name, filePath) {
  testResults.total++;
  console.log(`\n▶️ Checking: ${name}`);
  if (fs.existsSync(filePath)) {
    console.log(`✅ Found: ${filePath}`);
    testResults.passed++;
    return true;
  } else {
    console.log(`❌ Missing: ${filePath}`);
    testResults.failed.push({ name, error: 'File not found' });
    return false;
  }
}

console.log('💓 Goal Heartbeat Engine Sanity Tests');
console.log('=====================================');

checkFile('Agent Config', path.join(SKILL_DIR, 'agents/openai.yaml'));
checkFile('Pulse State Machine', path.join(ROOT_DIR, 'workspace/memory/PULSE.md'));
checkFile('Goals Board', path.join(ROOT_DIR, 'workspace/memory/GOALS.md'));
checkFile('Heartbeat Engine Config', path.join(ROOT_DIR, 'workspace/HEARTBEAT.md'));

// Summary
console.log('\n=====================================');
console.log(`📊 Test Summary: ${testResults.passed}/${testResults.total} passed`);
if (testResults.failed.length > 0) {
  process.exit(1);
} else {
  console.log('✅ All sanity tests passed!');
  process.exit(0);
}