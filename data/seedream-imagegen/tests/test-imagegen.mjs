import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_SCRIPT = path.join(__dirname, '../scripts/generate_image.py');

const testResults = {
  total: 0,
  passed: 0,
  failed: []
};

function runTest(name, command) {
  testResults.total++;
  console.log(`\n▶️ Running Test: ${name}`);
  try {
    const output = execSync(command, { encoding: 'utf8', stdio: 'pipe' });
    console.log(`✅ Passed: ${name}`);
    testResults.passed++;
    return true;
  } catch (error) {
    console.log(`❌ Failed: ${name}`);
    testResults.failed.push({ name, error: error.message });
    return false;
  }
}

console.log('🎨 Seedream Imagegen Sanity Tests');
console.log('==================================');

// Test 1: Help message
runTest('Python Script Help', `python3 ${PYTHON_SCRIPT} --help`);

// Test 2: Check environment variable (should fail if not set, but we just check if script runs and detects missing key)
// We use a mock ARK_API_KEY for parameter validation test if possible
// But for now just check if the script basic execution works.

// Summary
console.log('\n==================================');
console.log(`📊 Test Summary: ${testResults.passed}/${testResults.total} passed`);
if (testResults.failed.length > 0) {
  console.log('❌ Failures:');
  testResults.failed.forEach(f => console.log(`  - ${f.name}`));
  process.exit(1);
} else {
  console.log('✅ All sanity tests passed!');
  process.exit(0);
}
