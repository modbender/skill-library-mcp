#!/usr/bin/env node

/**
 * Terminal Killer - Test Suite
 * 
 * Tests the command detector with various inputs.
 * 
 * Usage: node test-detector.js
 */

const { detectCommand } = require('./detect-command');

// Test cases with expected outcomes
const TEST_CASES = [
  // Clear commands - should EXECUTE
  { input: 'ls -la', expected: 'EXECUTE', description: 'List files with details' },
  { input: 'git status', expected: 'EXECUTE', description: 'Git status check' },
  { input: 'npm install', expected: 'EXECUTE', description: 'NPM install' },
  { input: 'cd ~/projects', expected: 'EXECUTE', description: 'Change directory' },
  { input: 'cat file.txt | grep test', expected: 'EXECUTE', description: 'Pipe command' },
  { input: 'echo $HOME', expected: 'EXECUTE', description: 'Echo env variable' },
  { input: 'find . -name "*.js"', expected: 'EXECUTE', description: 'Find command' },
  { input: 'docker ps', expected: 'EXECUTE', description: 'Docker command' },
  { input: 'python3 script.py', expected: 'EXECUTE', description: 'Python script' },
  { input: 'curl https://example.com', expected: 'EXECUTE', description: 'Curl request' },
  
  // Clear tasks - should LLM
  { input: 'help me write a script', expected: 'LLM', description: 'Help request' },
  { input: 'what does git status do?', expected: 'LLM', description: 'Question' },
  { input: 'please explain this code', expected: 'LLM', description: 'Explanation request' },
  { input: 'can you help me fix this bug', expected: 'LLM', description: 'Bug fix request' },
  { input: 'I need to create a new project', expected: 'LLM', description: 'Task description' },
  { input: 'how do I install node', expected: 'LLM', description: 'How-to question' },
  { input: 'write me a function that sorts arrays', expected: 'ASK', description: 'Code generation (borderline)' },
  
  // Borderline cases - short ambiguous phrases go to LLM
  { input: 'run tests', expected: 'LLM', description: 'Ambiguous command' },
  { input: 'build the project', expected: 'LLM', description: 'Ambiguous task' },
  { input: 'deploy', expected: 'LLM', description: 'Single verb' },
  
  // Dangerous commands - should ASK (even if looks like command)
  { input: 'rm -rf /', expected: 'ASK', description: 'Dangerous delete' },
  { input: 'sudo rm -rf /', expected: 'ASK', description: 'Dangerous sudo' },
  { input: 'dd if=/dev/zero', expected: 'ASK', description: 'Dangerous dd' },
];

// Run tests
console.log('🧪 Terminal Killer - Test Suite\n');
console.log('=' .repeat(60));
console.log('ℹ️  Note: Command detection uses your full shell environment');
console.log('   (sources ~/.zshrc, ~/.bash_profile, etc.)\n');

let passed = 0;
let failed = 0;

for (const test of TEST_CASES) {
  const result = detectCommand(test.input);
  const success = result.decision === test.expected;
  
  if (success) {
    passed++;
    console.log(`✅ PASS: "${test.input}"`);
  } else {
    failed++;
    console.log(`❌ FAIL: "${test.input}"`);
    console.log(`   Expected: ${test.expected}, Got: ${result.decision} (score: ${result.score})`);
  }
  console.log(`   ${test.description}`);
  console.log();
}

// Summary
console.log('=' .repeat(60));
console.log(`\n📊 Results: ${passed} passed, ${failed} failed (${TEST_CASES.length} total)`);

if (failed === 0) {
  console.log('\n🎉 All tests passed!\n');
  process.exit(0);
} else {
  console.log('\n⚠️  Some tests failed. Review detection logic.\n');
  process.exit(1);
}
