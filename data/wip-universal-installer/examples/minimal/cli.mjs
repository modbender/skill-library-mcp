#!/usr/bin/env node
import { hello } from './core.mjs';
const name = process.argv[2];
console.log(hello({ name }));
