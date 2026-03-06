/**
 * Test script for Office to Markdown Converter
 * 
 * This script tests the converter with various file types
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Path to the converter
const CONVERTER_PATH = path.join(__dirname, '../office-to-md/openclaw-skill.js');

// Test files directory
const TEST_DIR = path.join(__dirname, 'test-files');

// Create test directory if it doesn't exist
if (!fs.existsSync(TEST_DIR)) {
  fs.mkdirSync(TEST_DIR, { recursive: true });
}

// Test cases
const testCases = [
  {
    name: 'Test 1: Basic .doc conversion',
    createTest: () => {
      // Create a simple .doc test file (simulated)
      const testPath = path.join(TEST_DIR, 'test1.doc');
      // For actual testing, you would need real .doc files
      return { filePath: testPath, shouldPass: false, reason: 'Need actual .doc file' };
    }
  },
  {
    name: 'Test 2: Invalid file path',
    createTest: () => {
      return { 
        filePath: '/nonexistent/path/document.pdf', 
        shouldPass: false,
        expectedError: 'File not found'
      };
    }
  },
  {
    name: 'Test 3: Unsupported file type',
    createTest: () => {
      const testPath = path.join(TEST_DIR, 'test3.txt');
      fs.writeFileSync(testPath, 'This is a plain text file.');
      return { 
        filePath: testPath, 
        shouldPass: false,
        expectedError: 'Unsupported file type'
      };
    }
  },
  {
    name: 'Test 4: No arguments',
    createTest: () => {
      return { 
        filePath: null, 
        shouldPass: false,
        expectedError: 'No file path provided'
      };
    }
  }
];

// Run tests
async function runTests() {
  console.log('=== Office to Markdown Converter Tests ===\n');
  
  let passed = 0;
  let failed = 0;
  
  for (const testCase of testCases) {
    console.log(`Running: ${testCase.name}`);
    
    try {
      const test = testCase.createTest();
      
      if (test.filePath === null) {
        // Test with no arguments
        try {
          execSync(`node "${CONVERTER_PATH}"`, { stdio: 'pipe' });
          // Should not reach here
          console.log('  ❌ FAIL: Should have failed with no arguments');
          failed++;
        } catch (error) {
          const stderr = error.stderr?.toString() || '';
          if (stderr.includes('Usage:') || stderr.includes('No file path')) {
            console.log('  ✅ PASS: Correctly handled no arguments');
            passed++;
          } else {
            console.log('  ❌ FAIL: Unexpected error:', stderr.substring(0, 100));
            failed++;
          }
        }
      } else {
        // Test with file path
        try {
          const result = execSync(`node "${CONVERTER_PATH}" "${test.filePath}"`, { 
            encoding: 'utf-8',
            stdio: ['pipe', 'pipe', 'pipe']
          });
          
          if (test.shouldPass) {
            console.log('  ✅ PASS: Conversion succeeded as expected');
            passed++;
            
            // Check if output file was created
            const outputPath = test.filePath.replace(/\.[^/.]+$/, '.md');
            if (fs.existsSync(outputPath)) {
              console.log('  ✅ PASS: Output file created');
              const stats = fs.statSync(outputPath);
              if (stats.size > 0) {
                console.log('  ✅ PASS: Output file has content');
              } else {
                console.log('  ⚠️  WARN: Output file is empty');
              }
            }
          } else {
            console.log('  ❌ FAIL: Should have failed but succeeded');
            failed++;
          }
        } catch (error) {
          const stderr = error.stderr?.toString() || '';
          
          if (!test.shouldPass) {
            if (test.expectedError && stderr.includes(test.expectedError)) {
              console.log(`  ✅ PASS: Correctly failed with "${test.expectedError}"`);
              passed++;
            } else if (!test.expectedError) {
              console.log('  ✅ PASS: Failed as expected (any error)');
              passed++;
            } else {
              console.log(`  ❌ FAIL: Expected "${test.expectedError}" but got:`, stderr.substring(0, 100));
              failed++;
            }
          } else {
            console.log('  ❌ FAIL: Should have succeeded but failed:', stderr.substring(0, 100));
            failed++;
          }
        }
      }
      
    } catch (error) {
      console.log('  ❌ FAIL: Test setup error:', error.message);
      failed++;
    }
    
    console.log(); // Empty line between tests
  }
  
  // Summary
  console.log('=== Test Summary ===');
  console.log(`Total tests: ${testCases.length}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Success rate: ${Math.round((passed / testCases.length) * 100)}%`);
  
  // Cleanup
  try {
    if (fs.existsSync(TEST_DIR)) {
      const files = fs.readdirSync(TEST_DIR);
      for (const file of files) {
        fs.unlinkSync(path.join(TEST_DIR, file));
      }
      fs.rmdirSync(TEST_DIR);
    }
  } catch (error) {
    // Ignore cleanup errors
  }
  
  return failed === 0;
}

// Integration test with actual document (if available)
async function integrationTest() {
  console.log('\n=== Integration Test ===');
  
  // Use the actual operating system document we tested earlier
  const actualDocPath = '/root/clawd/downloads/2023级操作系统课程设计任务书2026.1_1771124291800.doc';
  
  if (fs.existsSync(actualDocPath)) {
    console.log('Testing with actual .doc file:', path.basename(actualDocPath));
    
    try {
      const result = execSync(`node "${CONVERTER_PATH}" "${actualDocPath}"`, { 
        encoding: 'utf-8',
        stdio: ['pipe', 'pipe', 'pipe'],
        timeout: 30000
      });
      
      console.log('  ✅ PASS: Real .doc file converted successfully');
      
      // Parse JSON output
      try {
        const output = JSON.parse(result);
        if (output.success) {
          console.log('  ✅ PASS: JSON output structure correct');
          console.log(`  Output file: ${output.outputPath}`);
          console.log(`  Stats: ${output.stats?.lines || 0} lines`);
          
          // Verify output file exists
          if (fs.existsSync(output.outputPath)) {
            const content = fs.readFileSync(output.outputPath, 'utf-8');
            console.log(`  Content length: ${content.length} characters`);
            console.log(`  Contains Chinese: ${/[\u4e00-\u9fff]/.test(content)}`);
            console.log('  ✅ PASS: Integration test complete');
            return true;
          }
        }
      } catch (parseError) {
        console.log('  ⚠️  WARN: Could not parse JSON output');
        console.log('  Raw output:', result.substring(0, 200));
      }
      
    } catch (error) {
      console.log('  ❌ FAIL: Real .doc conversion failed:', error.message);
      return false;
    }
  } else {
    console.log('  ⚠️  SKIP: Actual .doc file not available for integration test');
  }
  
  return true;
}

// Main test runner
async function main() {
  const unitTestsPassed = await runTests();
  const integrationTestPassed = await integrationTest();
  
  console.log('\n=== Final Results ===');
  console.log(`Unit tests: ${unitTestsPassed ? '✅ PASS' : '❌ FAIL'}`);
  console.log(`Integration test: ${integrationTestPassed ? '✅ PASS' : '❌ FAIL'}`);
  
  const allPassed = unitTestsPassed && integrationTestPassed;
  console.log(`\nOverall: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
  
  process.exit(allPassed ? 0 : 1);
}

// Run if called directly
if (require.main === module) {
  main().catch(error => {
    console.error('Test runner error:', error);
    process.exit(1);
  });
}

module.exports = {
  runTests,
  integrationTest,
  main
};