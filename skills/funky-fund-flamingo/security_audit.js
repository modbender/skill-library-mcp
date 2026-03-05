'use strict';

const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const FILES = fs.readdirSync(ROOT).filter(f =>
    /\.(js|md|ya?ml|json)$/.test(f) && f !== 'security_audit.js'
);

const bannedPatterns = [
    { name: 'child process execSync', re: /\bexecSync\s*\(/ },
    { name: 'child process spawn', re: /\bspawn\s*\(/ },
    { name: 'child process fork', re: /\bfork\s*\(/ },
    { name: 'external tool spawning directive', re: /sessions_spawn/i },
    { name: 'network request primitive', re: /\bhttps?\.(request|get)\s*\(/ },
    { name: 'fetch api', re: /\bfetch\s*\(/ },
    { name: 'axios usage', re: /\baxios\b/ },
    { name: 'curl command string', re: /\bcurl\s+/i },
    { name: 'wget command string', re: /\bwget\s+/i },
];

const allowList = [
    { file: 'generate_history.js', re: /\bexecFileSync\s*\(/ },
];

function isAllowed(file, line) {
    return allowList.some(rule => rule.file === file && rule.re.test(line));
}

function main() {
    const violations = [];

    for (const file of FILES) {
        const full = path.join(ROOT, file);
        const content = fs.readFileSync(full, 'utf8');
        const lines = content.split('\n');

        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (isAllowed(file, line)) continue;
            for (const pattern of bannedPatterns) {
                if (pattern.re.test(line)) {
                    violations.push(`${file}:${i + 1} ${pattern.name}: ${line.trim()}`);
                }
            }
        }
    }

    if (violations.length) {
        console.error('Security audit failed.');
        for (const item of violations) console.error(`- ${item}`);
        process.exit(1);
    }

    console.log('Security audit passed.');
}

main();
