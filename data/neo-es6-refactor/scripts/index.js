#!/usr/bin/env node
/**
 * es6-refactor skill entry point
 *
 * As a library:
 *   const { refactor } = require('es6-refactor');
 *   const result = refactor({ code, language, options });
 *
 * As a CLI (via bin):
 *   es6-refactor [options] [file]
 *
 * See CLI help: es6-refactor --help
 */

const path = require('path');

function refactor(context) {
  const { code, language = 'javascript', options = {} } = context;
  
  let transformer;
  if (language === 'typescript' || language === 'ts') {
    transformer = require('./types');
    if (typeof transformer.refactorTypeScript !== 'function') {
      throw new Error('types module does not export a refactorTypeScript function');
    }
    return transformer.refactorTypeScript(code, options);
  } else {
    transformer = require('./refactor');
    if (typeof transformer.refactorCode !== 'function') {
      throw new Error('refactor module does not export a refactorCode function');
    }
    return transformer.refactorCode(code, options);
  }
}

// Export for external use
module.exports = { refactor };

// If executed directly (e.g., `node scripts/index.js`), run as CLI
if (require.main === module) {
  const cli = require('./cli');
  cli.run(process.argv.slice(2)).catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
  });
}