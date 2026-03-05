const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

/**
 * Run the benchmark result ingestion.
 */
function runResult(args = []) {
  const scriptPath = path.join(__dirname, 'run_result.js');
  const proc = spawn('node', [scriptPath, ...args], {
    stdio: 'inherit'
  });
  
  return new Promise((resolve, reject) => {
    proc.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`run_result.js exited with code ${code}`));
    });
  });
}

/**
 * Run the benchmark pipeline.
 */
function runPipeline(args = []) {
  const scriptPath = path.join(__dirname, 'run_pipeline.js');
  const proc = spawn('node', [scriptPath, ...args], {
    stdio: 'inherit'
  });

  return new Promise((resolve, reject) => {
    proc.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`run_pipeline.js exited with code ${code}`));
    });
  });
}

/**
 * Main entry point for CLI.
 */
function main() {
  const args = process.argv.slice(2);
  const mode = args.find(a => a.startsWith('--mode='))?.split('=')[1] || 'result';
  
  if (mode === 'pipeline') {
    return runPipeline(args);
  } else {
    return runResult(args);
  }
}

if (require.main === module) {
  main().catch(err => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = {
  runResult,
  runPipeline,
  main
};
