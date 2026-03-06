const fs = require('fs');
const path = require('path');
const { generateStructure, printAsciiTree } = require('../index.js');

const tmpDir = path.join(__dirname, 'tmp-test');

function createTestDir() {
  if (fs.existsSync(tmpDir)) {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
  fs.mkdirSync(tmpDir);
  fs.mkdirSync(path.join(tmpDir, 'subdir'));
  fs.writeFileSync(path.join(tmpDir, 'file1.txt'), 'content');
  fs.writeFileSync(path.join(tmpDir, 'subdir', 'file2.txt'), 'content');
}

function cleanup() {
  if (fs.existsSync(tmpDir)) {
    fs.rmSync(tmpDir, { recursive: true, force: true });
  }
}

function test() {
  console.log('Running test...');
  try {
    createTestDir();
    const tree = generateStructure(tmpDir);
    const ascii = printAsciiTree(tree);
    
    console.log('Generated Tree:');
    console.log(ascii);

    if (!ascii.includes('file1.txt')) throw new Error('Missing file1.txt');
    if (!ascii.includes('subdir')) throw new Error('Missing subdir');
    if (!ascii.includes('file2.txt')) throw new Error('Missing file2.txt');

    console.log('Test Passed!');
  } catch (err) {
    console.error('Test Failed:', err);
    process.exit(1);
  } finally {
    cleanup();
  }
}

test();
