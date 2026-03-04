#!/usr/bin/env node
import { runCli } from '../src/index.js';

const exitCode = await runCli(process.argv.slice(2));
process.exit(exitCode);
