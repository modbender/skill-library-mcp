const fs = require('fs');
const path = require('path');
const { checkFile } = require('../index');

// Create test file
const testFile = 'test.md';
const brokenFile = 'broken.md';

fs.writeFileSync(testFile, 'This is a test file. [Link](test.md)');
fs.writeFileSync(brokenFile, 'This is a broken link. [Broken](does_not_exist.md)');

const report1 = checkFile(testFile);
const report2 = checkFile(brokenFile);

console.log('Report 1:', report1.valid); // true
console.log('Report 2:', report2.valid); // false

// Cleanup
fs.unlinkSync(testFile);
fs.unlinkSync(brokenFile);

if (report1.valid && !report2.valid) {
    console.log('PASS: markdown-validator works');
    process.exit(0);
} else {
    console.log('FAIL: markdown-validator failed');
    process.exit(1);
}
