#!/usr/bin/env node
/**
 * OpenScan CLI
 * Scan binaries and scripts for malicious patterns
 */

const fs = require('fs');
const path = require('path');
const { scanFile, scanDirectory, formatResult } = require('../lib/scanner');

const VERSION = '1.0.0';

function printHelp() {
  console.log(`
OpenScan v${VERSION}
Scan binaries and scripts for malicious patterns.

Usage:
  scan <path> [options]

Options:
  --json          Output results as JSON
  --quiet         Only output threats (score > 20)
  --no-color      Disable colored output
  --max-size=N    Max file size in MB (default: 50)
  --help          Show this help
  --version       Show version

Examples:
  scan /usr/local/bin/some-binary
  scan ./my-skill --json
  scan /path/to/file --quiet
`);
}

async function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    printHelp();
    process.exit(0);
  }

  if (args.includes('--version') || args.includes('-v')) {
    console.log(VERSION);
    process.exit(0);
  }

  // Parse options
  const options = {
    json: args.includes('--json'),
    quiet: args.includes('--quiet'),
    noColor: args.includes('--no-color')
  };

  const maxSizeArg = args.find(a => a.startsWith('--max-size='));
  if (maxSizeArg) {
    options.maxSize = parseInt(maxSizeArg.split('=')[1], 10) * 1024 * 1024;
  }

  // Get target path
  const targetPath = args.find(a => !a.startsWith('--'));
  
  if (!targetPath) {
    console.error('Error: No path specified');
    printHelp();
    process.exit(1);
  }

  const fullPath = path.resolve(targetPath);

  if (!fs.existsSync(fullPath)) {
    console.error(`Error: Path not found: ${fullPath}`);
    process.exit(1);
  }

  const stats = fs.statSync(fullPath);
  let results;

  if (stats.isDirectory()) {
    if (!options.json) {
      console.log(`Scanning directory: ${fullPath}\n`);
    }
    results = await scanDirectory(fullPath, options);
  } else {
    results = [await scanFile(fullPath, options)];
  }

  // Filter if quiet mode
  if (options.quiet) {
    results = results.filter(r => r.threatScore > 20);
  }

  // Output
  if (options.json) {
    console.log(JSON.stringify(results, null, 2));
  } else {
    let threatCount = 0;
    let highThreatCount = 0;

    for (const result of results) {
      console.log(formatResult(result, options));
      if (result.threatScore > 20) threatCount++;
      if (result.threatScore > 60) highThreatCount++;
    }

    console.log('\n' + '='.repeat(50));
    console.log(`Scanned: ${results.length} file(s)`);
    console.log(`Threats: ${threatCount} suspicious, ${highThreatCount} high-risk`);
    console.log('='.repeat(50));
  }

  // Exit code based on findings
  const maxScore = Math.max(...results.map(r => r.threatScore), 0);
  if (maxScore > 60) {
    process.exit(2); // High threat
  } else if (maxScore > 20) {
    process.exit(1); // Suspicious
  }
  process.exit(0); // Clean
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
