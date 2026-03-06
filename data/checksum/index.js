#!/usr/bin/env node
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { Transform } = require('stream');

/**
 * Checksum Utility
 * Generates cryptographic hashes for files and directories.
 */

const ALGOS = ['md5', 'sha1', 'sha256', 'sha512'];

async function hashFile(filePath, algo = 'md5') {
  return new Promise((resolve, reject) => {
    if (!fs.existsSync(filePath)) {
      return reject(new Error(`File not found: ${filePath}`));
    }
    
    const hash = crypto.createHash(algo);
    const input = fs.createReadStream(filePath);
    
    input.on('error', reject);
    
    input.pipe(hash).on('finish', () => {
      resolve(hash.digest('hex'));
    });
  });
}

async function hashDir(dirPath, algo = 'md5', recursive = true) {
  if (!fs.existsSync(dirPath)) {
    throw new Error(`Directory not found: ${dirPath}`);
  }

  const results = {};
  
  async function scan(currentDir) {
    const list = fs.readdirSync(currentDir);
    // Sort to ensure deterministic order if we were hashing the dir itself (future)
    list.sort(); 
    
    for (const file of list) {
      if (file === '.git' || file === 'node_modules') continue;
      
      const fullPath = path.join(currentDir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        if (recursive) await scan(fullPath);
      } else {
        const hash = await hashFile(fullPath, algo);
        // Store relative path
        const relativePath = path.relative(dirPath, fullPath);
        results[relativePath] = hash;
      }
    }
  }
  
  await scan(dirPath);
  return results;
}

async function main() {
  const args = process.argv.slice(2);
  const fileArg = args.indexOf('--file');
  const dirArg = args.indexOf('--dir');
  const algoArg = args.indexOf('--algo');
  const verifyArg = args.indexOf('--verify'); // Placeholder for future
  const jsonArg = args.indexOf('--json');

  if (args.includes('--help') || args.length === 0) {
    console.log(`
Checksum Utility v1.0.0
Usage:
  node skills/checksum/index.js --file <path> [--algo md5|sha1|sha256]
  node skills/checksum/index.js --dir <path> [--algo md5|sha1|sha256] [--json]

Options:
  --file <path>   Calculate hash for a single file
  --dir <path>    Recursively calculate hashes for all files in a directory
  --algo <alg>    Hash algorithm (default: md5)
  --json          Output results as JSON (default: standard 'hash  file' format)
    `);
    return;
  }

  const algo = (algoArg !== -1 && args[algoArg + 1]) ? args[algoArg + 1] : 'md5';
  
  if (!ALGOS.includes(algo)) {
    console.error(`Error: Unsupported algorithm '${algo}'. Supported: ${ALGOS.join(', ')}`);
    process.exit(1);
  }

  try {
    if (fileArg !== -1 && args[fileArg + 1]) {
      const filePath = args[fileArg + 1];
      const hash = await hashFile(filePath, algo);
      if (jsonArg !== -1) {
        console.log(JSON.stringify({ file: filePath, algo, hash }, null, 2));
      } else {
        console.log(`${hash}  ${filePath}`);
      }
    } else if (dirArg !== -1 && args[dirArg + 1]) {
      const dirPath = args[dirArg + 1];
      const results = await hashDir(dirPath, algo);
      
      if (jsonArg !== -1) {
        console.log(JSON.stringify(results, null, 2));
      } else {
        Object.keys(results).sort().forEach(relPath => {
           console.log(`${results[relPath]}  ${relPath}`);
        });
      }
    } else {
      console.error("Error: Missing --file or --dir argument.");
      process.exit(1);
    }
  } catch (err) {
    console.error(`Error: ${err.message}`);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { hashFile, hashDir };
