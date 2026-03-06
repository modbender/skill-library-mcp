#!/usr/bin/env node

/**
 * OpenClaw MoreLogin skill entrypoint.
 *
 * Direct mode: execute bin/morelogin.js in-process.
 * This makes `openclaw morelogin ...` equivalent to:
 * `node bin/morelogin.js ...`
 */

const { main } = require('./bin/morelogin');

main(process.argv.slice(2));
