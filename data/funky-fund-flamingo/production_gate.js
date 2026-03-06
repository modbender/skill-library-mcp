'use strict';

const fs = require('fs');
const path = require('path');
const vm = require('vm');

const ROOT = __dirname;
const JS_EXT = '.js';
const JSON_EXT = '.json';

const IGNORE_DIRS = new Set([
    '.git',
    'node_modules',
    '.memory'
]);

const IGNORE_FILES = new Set([
    'production_gate.js'
]);

const bannedTerms = [
    'to' + 'do',
    'fix' + 'me',
    't' + 'bd',
    'st' + 'ub',
    'st' + 'ubs',
    'mo' + 'ck',
    'mo' + 'cks',
    'de' + 'mo',
    'place' + 'holder'
];
const bannedPattern = new RegExp(`\\b(${bannedTerms.join('|')})\\b`, 'i');

function collectFiles(dir) {
    const out = [];
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
        const full = path.join(dir, entry.name);
        const rel = path.relative(ROOT, full);

        if (entry.isDirectory()) {
            if (IGNORE_DIRS.has(entry.name)) continue;
            out.push(...collectFiles(full));
            continue;
        }

        if (IGNORE_FILES.has(entry.name)) continue;
        out.push(rel);
    }

    return out.sort((a, b) => a.localeCompare(b));
}

function runNodeCheck(file, code) {
    new vm.Script(code, { filename: file });
}

function main() {
    const files = collectFiles(ROOT);
    const errors = [];

    for (const rel of files) {
        const full = path.join(ROOT, rel);
        let content = '';
        try {
            content = fs.readFileSync(full, 'utf8');
        } catch (err) {
            errors.push(`Read failed: ${rel}: ${err.message}`);
            continue;
        }

        const lines = content.split('\n');
        for (let i = 0; i < lines.length; i++) {
            if (bannedPattern.test(lines[i])) {
                errors.push(`Banned token in ${rel}:${i + 1}`);
            }
        }

        if (rel.endsWith(JS_EXT)) {
            try {
                runNodeCheck(rel, content);
            } catch (err) {
                errors.push(`JS syntax failed: ${rel}: ${String(err.message || err)}`);
            }
        }

        if (rel.endsWith(JSON_EXT)) {
            try {
                JSON.parse(content);
            } catch (err) {
                errors.push(`JSON parse failed: ${rel}: ${err.message}`);
            }
        }
    }

    if (errors.length) {
        console.error('Production gate failed.');
        for (const err of errors) console.error(`- ${err}`);
        process.exit(1);
    }

    console.log('Production gate passed.');
}

main();
