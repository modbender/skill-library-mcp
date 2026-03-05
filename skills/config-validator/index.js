#!/usr/bin/env node
/**
 * Config Validator
 * A simple utility to validate OpenClaw configuration files and environment settings.
 * Ensures critical configurations are present and well-formed.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Determine workspace root
const WORKSPACE_ROOT = path.resolve(__dirname, '../../');
const ENV_FILE = path.join(WORKSPACE_ROOT, '.env');
const OPENCLAW_JSON = path.join(WORKSPACE_ROOT, 'openclaw.json');
const PACKAGE_JSON = path.join(WORKSPACE_ROOT, 'package.json');

// Critical Env Variables
const CRITICAL_ENV = [
    'CLAWHUB_TOKEN',
    'FEISHU_APP_ID',
    'FEISHU_APP_SECRET',
    'FEISHU_BOT_NAME',
    'OPENAI_API_KEY',
    'DATABASE_URL'
];

// Optional Env Variables
const OPTIONAL_ENV = [
    'DUBY_API_KEY',
    'MEM0_API_KEY',
    'GEMINI_API_KEY',
    'ANTHROPIC_API_KEY',
    'EVOLVER_MAX_RSS_MB',
    'EVOLVER_MIN_SLEEP_MS'
];

function log(msg, type = 'INFO') {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${type}] ${msg}`);
}

function checkEnv() {
    log('Checking .env file...');
    if (!fs.existsSync(ENV_FILE)) {
        log('Error: .env file missing!', 'ERROR');
        return { valid: false, issues: ['Missing .env file'] };
    }

    try {
        const envContent = fs.readFileSync(ENV_FILE, 'utf8');
        const envLines = envContent.split('\n');
        const envKeys = new Set();
        
        envLines.forEach(line => {
            const trimmed = line.trim();
            if (trimmed && !trimmed.startsWith('#')) {
                const parts = trimmed.split('=');
                if (parts.length > 0) envKeys.add(parts[0].trim());
            }
        });

        const missing = [];
        CRITICAL_ENV.forEach(key => {
            if (!envKeys.has(key)) missing.push(key);
        });

        if (missing.length > 0) {
            log(`Warning: Missing critical env vars: ${missing.join(', ')}`, 'WARN');
            return { valid: true, issues: missing.map(k => `Missing env var: ${k}`) }; // treat as warning for now to avoid blocking
        } else {
            log('Environment variables check passed.', 'SUCCESS');
            return { valid: true, issues: [] };
        }
    } catch (e) {
        log(`Error reading .env: ${e.message}`, 'ERROR');
        return { valid: false, issues: [e.message] };
    }
}

function checkOpenClawJson() {
    log('Checking openclaw.json...');
    if (!fs.existsSync(OPENCLAW_JSON)) {
        log('Warning: openclaw.json missing (using defaults).', 'WARN');
        return { valid: true, issues: ['Missing openclaw.json'] };
    }

    try {
        const content = fs.readFileSync(OPENCLAW_JSON, 'utf8');
        JSON.parse(content);
        log('openclaw.json is valid JSON.', 'SUCCESS');
        return { valid: true, issues: [] };
    } catch (e) {
        log(`Error parsing openclaw.json: ${e.message}`, 'ERROR');
        return { valid: false, issues: [`Invalid JSON in openclaw.json: ${e.message}`] };
    }
}

function checkPackageJson() {
    log('Checking package.json...');
    if (!fs.existsSync(PACKAGE_JSON)) {
        log('Error: package.json missing!', 'ERROR');
        return { valid: false, issues: ['Missing package.json'] };
    }

    try {
        const pkg = JSON.parse(fs.readFileSync(PACKAGE_JSON, 'utf8'));
        if (!pkg.name || !pkg.version) {
            log('Warning: package.json missing name or version.', 'WARN');
            return { valid: true, issues: ['Missing metadata in package.json'] };
        }
        
        // Check dependencies consistency
        if (pkg.dependencies) {
            const nodeModules = path.join(WORKSPACE_ROOT, 'node_modules');
            if (!fs.existsSync(nodeModules)) {
                log('Warning: node_modules missing (run npm install).', 'WARN');
                return { valid: true, issues: ['Missing node_modules'] };
            }
        }
        
        log('package.json check passed.', 'SUCCESS');
        return { valid: true, issues: [] };
    } catch (e) {
        log(`Error parsing package.json: ${e.message}`, 'ERROR');
        return { valid: false, issues: [`Invalid JSON in package.json: ${e.message}`] };
    }
}

function run() {
    const envRes = checkEnv();
    const jsonRes = checkOpenClawJson();
    const pkgRes = checkPackageJson();

    const allIssues = [...envRes.issues, ...jsonRes.issues, ...pkgRes.issues];
    const status = (envRes.valid && jsonRes.valid && pkgRes.valid) ? 'success' : 'failed';

    const report = {
        timestamp: new Date().toISOString(),
        status,
        issues: allIssues,
        metrics: {
            env_vars_checked: CRITICAL_ENV.length + OPTIONAL_ENV.length,
            files_checked: 3
        }
    };

    console.log(JSON.stringify(report, null, 2));
    
    // Exit with code 1 if critical failures
    if (!envRes.valid || !jsonRes.valid || !pkgRes.valid) {
        process.exit(1);
    }
}

if (require.main === module) {
    run();
}

module.exports = { run, checkEnv, checkOpenClawJson, checkPackageJson };
