const fs = require('fs');
const path = require('path');
const vm = require('vm');
const util = require('util');

function repairJson(content) {
  try {
    // Try standard JSON.parse first (fast path)
    return JSON.stringify(JSON.parse(content), null, 2);
  } catch (e) {
    // Try loose parsing via vm (safe sandbox)
    try {
      // Evaluate content as a JS expression
      // Wrap in parentheses to handle object literals starting with '{'
      const sandbox = {};
      const script = new vm.Script('result = (' + content + ')');
      const context = vm.createContext(sandbox);
      script.runInContext(context);
      
      const result = sandbox.result;
      
      if (typeof result === 'function' || typeof result === 'symbol' || typeof result === 'undefined') {
        throw new Error('Result is not serializable data (function/symbol/undefined)');
      }
      
      return JSON.stringify(result, null, 2);
    } catch (vmError) {
      throw new Error(`Failed to repair JSON: ${vmError.message}`);
    }
  }
}

function processFile(filePath, outFile, options) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const repaired = repairJson(content);
    
    // Check if changed
    // Normalize original (remove whitespace) to compare structure? 
    // No, just check if repaired is different string.
    // Actually, we want to fix invalid JSON, so original content might throw.
    
    // If output file is different, write to output
    if (outFile && outFile !== filePath) {
      fs.writeFileSync(outFile, repaired);
      console.log(`Repaired: ${filePath} -> ${outFile}`);
      return;
    }
    
    // In-place repair
    if (options.backup !== false) {
      fs.copyFileSync(filePath, `${filePath}.bak`);
    }
    fs.writeFileSync(filePath, repaired);
    console.log(`Repaired: ${filePath}`);
    
  } catch (err) {
    console.error(`Error processing ${filePath}: ${err.message}`);
    if (options.failFast) process.exit(1);
  }
}

function scanDirectory(dir, recursive) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat.isDirectory()) {
      if (recursive && file !== 'node_modules' && file !== '.git') {
        scanDirectory(fullPath, recursive);
      }
    } else if (file.endsWith('.json')) {
      // Check if valid JSON first
      try {
        JSON.parse(fs.readFileSync(fullPath, 'utf8'));
        // Valid, skip unless forced? For now, skip valid.
      } catch (e) {
        console.log(`Found invalid JSON: ${fullPath}`);
        processFile(fullPath, null, { backup: true });
      }
    }
  }
}

function main() {
  const args = process.argv.slice(2);
  let file = null;
  let out = null;
  let dir = null;
  let recursive = false;
  let backup = true;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--file') file = args[++i];
    else if (args[i] === '--out') out = args[++i];
    else if (args[i] === '--dir') dir = args[++i];
    else if (args[i] === '--recursive') recursive = true;
    else if (args[i] === '--no-backup') backup = false;
  }

  if (file) {
    processFile(file, out, { backup });
  } else if (dir) {
    scanDirectory(dir, recursive);
  } else {
    console.log('Usage: node index.js --file <path> [--out <path>] [--no-backup]');
    console.log('       node index.js --dir <path> [--recursive]');
  }
}

if (require.main === module) {
  main();
}

module.exports = { repairJson, processFile, scanDirectory };
