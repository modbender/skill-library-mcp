import { execSync } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT_DIR = path.join(__dirname, '../scripts');
const ROOT_DIR = path.join(__dirname, '../../../../');
console.log(`ROOT_DIR: ${ROOT_DIR}`);

const testResults = {
  total: 0,
  passed: 0,
  failed: []
};

function runTest(name, command) {
  testResults.total++;
  console.log(`\n▶️ Running Test: ${name}`);
  try {
    const output = execSync(command, { 
      encoding: 'utf8', 
      stdio: 'pipe',
      cwd: ROOT_DIR // Run from project root
    });
    console.log(`✅ Passed: ${name}`);
    testResults.passed++;
    return true;
  } catch (error) {
    console.log(`❌ Failed: ${name}`);
    console.log(`Error: ${error.message}`);
    if (error.stdout) console.log(`Stdout: ${error.stdout}`);
    if (error.stderr) console.log(`Stderr: ${error.stderr}`);
    testResults.failed.push({ name, error: error.message });
    return false;
  }
}

console.log('🦐 OpenClaw Toolbox Sanity Tests');
console.log('=================================');

// Test 1: Backup Dry Run (Full)
runTest('Backup Full (Dry Run)', `bash ${path.join(SCRIPT_DIR, 'backup-now.sh')} --full --dry-run`);

// Test 2: Backup Dry Run (Skills)
runTest('Backup Skills (Dry Run)', `bash ${path.join(SCRIPT_DIR, 'backup-now.sh')} --skills --dry-run`);

// Test 3: Setup Verify Only
runTest('Setup Verification', `bash ${path.join(SCRIPT_DIR, 'setup.sh')} --verify-only`);

// Summary
console.log('\n=================================');
console.log(`📊 Test Summary: ${testResults.passed}/${testResults.total} passed`);
if (testResults.failed.length > 0) {
  console.log('❌ Failures:');
  testResults.failed.forEach(f => console.log(`  - ${f.name}: ${f.error}`));
  process.exit(1);
} else {
  console.log('✅ All sanity tests passed!');
  process.exit(0);
}
