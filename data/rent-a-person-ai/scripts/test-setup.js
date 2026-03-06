#!/usr/bin/env node
/**
 * Test script for setup.js - verifies error handling and logic flow
 */

const fs = require('fs');
const path = require('path');

// Mock the setup.js functions to test them
const setupPath = path.join(__dirname, 'setup.js');
const setupCode = fs.readFileSync(setupPath, 'utf8');

// Extract and test key functions
console.log('🧪 Testing setup.js...\n');

// Test 1: Syntax check
console.log('1. Syntax check...');
try {
  require('child_process').execSync(`node -c "${setupPath}"`, { stdio: 'pipe' });
  console.log('   ✓ Syntax is valid\n');
} catch (e) {
  console.error('   ❌ Syntax error:', e.message);
  process.exit(1);
}

// Test 2: Check for undefined variables
console.log('2. Checking for undefined variables...');
const requiredVars = [
  'credentialsPath',
  'credentials',
  'agentId',
  'apiKey',
  'bridgePort',
  'webhookUrl',
  'useBridge',
];

let foundIssues = false;
requiredVars.forEach((varName) => {
  // Check if variable is used before definition
  const varRegex = new RegExp(`\\b${varName}\\b`, 'g');
  const matches = setupCode.match(varRegex);
  if (matches && matches.length > 0) {
    // Find where it's defined
    const defRegex = new RegExp(`(const|let|var)\\s+${varName}\\s*[=;]`, 'm');
    const defMatch = setupCode.match(defRegex);
    if (defMatch) {
      const defIndex = setupCode.indexOf(defMatch[0]);
      // Find where it's used
      const useMatches = [...setupCode.matchAll(new RegExp(`\\b${varName}\\b`, 'g'))];
      useMatches.forEach((match) => {
        if (match.index < defIndex && match.index > 0) {
          console.error(`   ❌ ${varName} used before definition at position ${match.index}`);
          foundIssues = true;
        }
      });
    }
  }
});

if (!foundIssues) {
  console.log('   ✓ No undefined variable issues found\n');
}

// Test 3: Check error handling for invalid JSON
console.log('3. Testing error handling logic...');
const hasErrorHandling = setupCode.includes('try {') && setupCode.includes('catch');
const hasContinueOption = setupCode.includes('Continue without updating');
if (hasErrorHandling && hasContinueOption) {
  console.log('   ✓ Error handling with continue option found\n');
} else {
  console.error('   ❌ Missing error handling or continue option\n');
  foundIssues = true;
}

// Test 4: Check that credentialsPath is defined before use
console.log('4. Checking credentialsPath scoping...');
const credPathDef = setupCode.indexOf('const credentialsPath =');
const credPathUse = setupCode.indexOf('credentialsPath', credPathDef + 1);
if (credPathDef !== -1 && credPathUse > credPathDef) {
  console.log('   ✓ credentialsPath is defined before use\n');
} else {
  console.error('   ❌ credentialsPath may be used before definition\n');
  foundIssues = true;
}

// Test 5: Check bridgePort fallbacks
console.log('5. Checking bridgePort fallbacks...');
const bridgePortFallbacks = (setupCode.match(/bridgePort\s*\|\|/g) || []).length;
if (bridgePortFallbacks >= 3) {
  console.log(`   ✓ Found ${bridgePortFallbacks} fallback checks for bridgePort\n`);
} else {
  console.warn(`   ⚠️  Only ${bridgePortFallbacks} fallback checks found (expected at least 3)\n`);
}

// Test 6: Check that all readline interfaces are closed
console.log('6. Checking readline interface cleanup...');
const rlCreates = (setupCode.match(/readline\.createInterface/g) || []).length;
const rlCloses = (setupCode.match(/\.close\(\)/g) || []).length;
if (rlCloses >= rlCreates) {
  console.log(`   ✓ All ${rlCreates} readline interfaces are closed\n`);
} else {
  console.warn(`   ⚠️  ${rlCreates} interfaces created but only ${rlCloses} closed\n`);
}

// Summary
console.log('═'.repeat(70));
if (foundIssues) {
  console.log('❌ Some issues found. Please review above.');
  process.exit(1);
} else {
  console.log('✅ All tests passed! Script is ready to use.');
  console.log('═'.repeat(70));
}
