const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

function smartRead(filePath, lines = 50) {
  try {
    const stat = fs.statSync(filePath);
    if (stat.isDirectory()) return `[INFO] ${filePath} is a directory.`;
    if (stat.size < 50 * 1024) { // < 50KB
      return fs.readFileSync(filePath, 'utf8');
    }
    
    // Use spawnSync for head/tail to avoid shell injection
    const headResult = spawnSync('head', ['-n', lines.toString(), filePath], { encoding: 'utf8' });
    const tailResult = spawnSync('tail', ['-n', lines.toString(), filePath], { encoding: 'utf8' });
    
    if (headResult.error) throw headResult.error;
    if (tailResult.error) throw tailResult.error;

    return `--- HEAD (${lines} lines) ---\n${headResult.stdout}\n...\n--- TAIL (${lines} lines) ---\n${tailResult.stdout}`;
  } catch (error) {
    return `Error reading file: ${error.message}`;
  }
}

function grepRead(filePath, pattern, context = 2) {
  try {
    if (fs.statSync(filePath).isDirectory()) return `[INFO] ${filePath} is a directory (grep skipped).`;

    // Use grep -n -C context
    const args = ['-n', '-C', context.toString(), pattern, filePath];
    const result = spawnSync('grep', args, { encoding: 'utf8' });

    if (result.error) throw result.error;
    if (result.status === 1) return "No matches found.";
    
    return result.stdout;
  } catch (error) {
    return `Error grepping file: ${error.message}`;
  }
}

function diffRead(filePath) {
  try {
    // Check if file is tracked
    const check = spawnSync('git', ['ls-files', '--error-unmatch', filePath], { stdio: 'ignore' });
    if (check.status !== 0) return "File not tracked by git.";

    const result = spawnSync('git', ['diff', 'HEAD', '--', filePath], { encoding: 'utf8' });
    
    if (result.error) throw result.error;
    
    return result.stdout || "No uncommitted changes.";
  } catch (error) {
    return `Error getting diff: ${error.message}`;
  }
}

function main() {
  const args = process.argv.slice(2);
  let filePath = '';
  let mode = 'smart';
  let lines = 50;
  let pattern = '';
  let context = 2;

  // Manual argument parsing
  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (arg === '--file') filePath = args[++i];
    else if (arg === '--mode') mode = args[++i];
    else if (arg === '--lines') lines = parseInt(args[++i], 10);
    else if (arg === '--pattern') pattern = args[++i];
    else if (args[i] === '--context') context = parseInt(args[++i], 10);
  }

  if (!filePath) {
    console.error("Usage: node skills/read-optimizer/index.js --file <path> [--mode smart|grep|diff]");
    process.exit(1);
  }

  if (!fs.existsSync(filePath)) {
    console.error(`File not found: ${filePath}`);
    process.exit(1);
  }

  let result;
  switch (mode) {
    case 'smart':
      result = smartRead(filePath, lines);
      break;
    case 'grep':
      if (!pattern) {
        console.error("Pattern required for grep mode.");
        process.exit(1);
      }
      result = grepRead(filePath, pattern, context);
      break;
    case 'diff':
      result = diffRead(filePath);
      break;
    default:
      console.error(`Unknown mode: ${mode}`);
      process.exit(1);
  }

  console.log(result);
}

if (require.main === module) {
  main();
}

module.exports = { smartRead, grepRead, diffRead, main };
