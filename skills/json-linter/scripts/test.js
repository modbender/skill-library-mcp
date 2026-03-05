const fs = require('fs');
const path = require('path');
const { validateJsonFiles } = require('../index.js');

const testDir = path.join(__dirname, 'test_temp');

// Setup test environment
if (fs.existsSync(testDir)) {
    fs.rmSync(testDir, { recursive: true, force: true });
}
fs.mkdirSync(testDir);

// Create valid JSON
fs.writeFileSync(path.join(testDir, 'good.json'), JSON.stringify({ valid: true }));

// Create invalid JSON
fs.writeFileSync(path.join(testDir, 'bad.json'), '{ "invalid": true, }'); // Trailing comma

// Run validation
try {
    const report = validateJsonFiles(testDir);
    
    // Assertions
    if (report.total_files !== 2) throw new Error(`Expected 2 files, got ${report.total_files}`);
    if (report.valid_files !== 1) throw new Error(`Expected 1 valid file, got ${report.valid_files}`);
    if (report.invalid_files !== 1) throw new Error(`Expected 1 invalid file, got ${report.invalid_files}`);
    if (report.errors[0].path !== 'skills/json-linter/scripts/test_temp/bad.json' && report.errors[0].path !== 'bad.json') {
         // Path relative to CWD might vary depending on where script is run, checking suffix
         if (!report.errors[0].path.endsWith('bad.json')) {
             throw new Error(`Expected error path to end with bad.json, got ${report.errors[0].path}`);
         }
    }
    
    console.log('Test Passed!');
    process.exit(0);
} catch (err) {
    console.error('Test Failed:', err);
    process.exit(1);
} finally {
    // Cleanup
    if (fs.existsSync(testDir)) {
        fs.rmSync(testDir, { recursive: true, force: true });
    }
}
