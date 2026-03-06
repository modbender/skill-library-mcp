#!/usr/bin/env node
/**
 * CLI for es6-refactor skill
 * Usage: es6-refactor [options] [file]
 *
 * Options:
 *   --from, -f        Source language version (ignored currently)
 *   --to, -t          Target ES version (ignored currently)
 *   --type, -l        Force language: 'js' or 'ts'
 *   --output, -o      Output file (default: stdout)
 *   --no-format       Skip Prettier formatting
 *   --rules, -r       Comma-separated list of rule names to apply
 *   --help, -h        Show help
 */

const { Command } = require('commander');
const fs = require('fs');
const path = require('path');
const { refactor } = require('./index');

async function run(argv = process.argv.slice(2)) {
  const program = new Command();

  program
    .name('es6-refactor')
    .description('Refactor JavaScript/TypeScript to modern ES6+ patterns')
    .version('1.0.0')
    .option('-f, --from <version>', 'Source version (ignored)')
    .option('-t, --to <version>', 'Target version (ignored)')
    .option('-l, --type <language>', 'Force language: js or ts')
    .option('-o, --output <file>', 'Output file path')
    .option('--no-format', 'Skip Prettier formatting')
    .option('-r, --rules <list>', 'Comma-separated list of rule names to apply')
    .argument('[file]', 'Input file (defaults to stdin)')
    .action(async (inputFile, options) => {
      // Determine language
      let language = options.type || 'javascript';
      if (language === 'ts') language = 'typescript';

      let code;
      if (inputFile) {
        const absPath = path.resolve(inputFile);
        code = fs.readFileSync(absPath, 'utf8');
        if (!options.type) {
          const ext = path.extname(absPath).toLowerCase();
          if (ext === '.ts' || ext === '.tsx') {
            language = 'typescript';
          } else if (ext === '.js' || ext === '.jsx') {
            language = 'javascript';
          }
        }
      } else {
        // Read from stdin asynchronously
        const chunks = [];
        for await (const chunk of process.stdin) {
          chunks.push(chunk);
        }
        code = Buffer.concat(chunks).toString('utf8');
      }

      const refactorOptions = {
        format: options.format !== false,
        rules: options.rules ? options.rules.split(',').map(s => s.trim()) : undefined
      };

      const result = refactor({ code, language, options: refactorOptions });

      if (options.output) {
        fs.writeFileSync(options.output, result, 'utf8');
      } else {
        process.stdout.write(result);
      }
    });

  await program.parseAsync(argv);
}

// If run directly (node scripts/cli.js), execute run()
if (require.main === module) {
  run().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}

// Export for programmatic use
module.exports = { run };