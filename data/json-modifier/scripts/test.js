const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const testFile = path.join(__dirname, 'test.json');
const patchFile = path.join(__dirname, 'patch.json');

// Setup
const initialContent = {
  version: "1.0.0",
  features: ["a", "b"]
};

fs.writeFileSync(testFile, JSON.stringify(initialContent, null, 2));

const patch = [
  { op: "replace", path: "/version", value: "2.0.0" },
  { op: "add", path: "/features/-", value: "c" }
];

fs.writeFileSync(patchFile, JSON.stringify(patch));

try {
  // Execute
  const cmd = `node ../index.js --file ${testFile} --patch-file ${patchFile}`;
  console.log(`Running: ${cmd}`);
  execSync(cmd, { cwd: __dirname });

  // Verify
  const newContent = JSON.parse(fs.readFileSync(testFile, 'utf8'));
  
  if (newContent.version !== "2.0.0") {
    throw new Error(`Version mismatch: expected "2.0.0", got "${newContent.version}"`);
  }
  
  if (newContent.features.length !== 3 || newContent.features[2] !== "c") {
    throw new Error(`Feature mismatch: expected ["a", "b", "c"], got ${JSON.stringify(newContent.features)}`);
  }
  
  console.log('Test Passed!');
} catch (err) {
  console.error('Test Failed:', err.message);
  process.exit(1);
} finally {
  // Cleanup
  if (fs.existsSync(testFile)) fs.unlinkSync(testFile);
  if (fs.existsSync(patchFile)) fs.unlinkSync(patchFile);
}
