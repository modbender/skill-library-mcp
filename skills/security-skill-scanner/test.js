#!/usr/bin/env node

/**
 * Test script for Security Skill Scanner
 * Runs tests against example skills
 */

const { SecurityScanner } = require('./scanner.js');
const path = require('path');

console.log('🧪 Running Security Skill Scanner Tests\n');

const scanner = new SecurityScanner();

// Test 1: Clean skill should pass
console.log('Test 1: Scanning clean skill...');
const cleanResult = scanner.scanSkill(path.join(__dirname, 'examples/clean-skill/SKILL.md'));

if (cleanResult.success && (cleanResult.overallRisk === 'INFO' || cleanResult.overallRisk === 'LOW')) {
  console.log('✅ PASS: Clean skill detected as safe\n');
} else {
  console.log('❌ FAIL: Clean skill flagged incorrectly');
  console.log('   Risk level:', cleanResult.overallRisk);
  console.log('   Findings:', cleanResult.findings.length, '\n');
}

// Test 2: Malicious skill should fail
console.log('Test 2: Scanning malicious skill...');
const maliciousResult = scanner.scanSkill(path.join(__dirname, 'examples/malicious-skill/SKILL.md'));

if (maliciousResult.success && maliciousResult.overallRisk === 'CRITICAL') {
  console.log('✅ PASS: Malicious skill detected as CRITICAL\n');
} else {
  console.log('❌ FAIL: Malicious skill not detected properly');
  console.log('   Risk level:', maliciousResult.overallRisk);
  console.log('   Findings:', maliciousResult.findings.length, '\n');
}

// Test 3: Check specific patterns were detected
console.log('Test 3: Verifying malicious pattern detection...');
const requiredPatterns = [
  'EXTERNAL_DOWNLOAD',
  'CREDENTIAL_HARVESTING',
  'SHELL_INJECTION',
  'SUSPICIOUS_API_CALLS'
];

const detectedPatterns = maliciousResult.findings.map(f => f.pattern);
let allDetected = true;

requiredPatterns.forEach(pattern => {
  if (detectedPatterns.includes(pattern)) {
    console.log(`  ✅ ${pattern} detected`);
  } else {
    console.log(`  ❌ ${pattern} NOT detected`);
    allDetected = false;
  }
});

if (allDetected) {
  console.log('✅ PASS: All critical patterns detected\n');
} else {
  console.log('❌ FAIL: Some patterns missed\n');
}

// Test 4: Generate reports
console.log('Test 4: Report generation...');
try {
  const cleanReport = scanner.generateReport(cleanResult);
  const maliciousReport = scanner.generateReport(maliciousResult);
  
  if (cleanReport.includes('SAFE') && maliciousReport.includes('DO NOT INSTALL')) {
    console.log('✅ PASS: Reports generated correctly\n');
  } else {
    console.log('❌ FAIL: Report content incorrect\n');
  }
} catch (error) {
  console.log('❌ FAIL: Report generation error:', error.message, '\n');
}

// Summary
console.log('═══════════════════════════════════════════════════');
console.log('Test Summary:');
console.log('  Clean skill findings:', cleanResult.findings.length);
console.log('  Malicious skill findings:', maliciousResult.findings.length);
console.log('  Malicious skill risk:', maliciousResult.overallRisk);
console.log('═══════════════════════════════════════════════════\n');

// Show detailed report for malicious skill
console.log('Detailed Malicious Skill Report:');
console.log(scanner.generateReport(maliciousResult));
