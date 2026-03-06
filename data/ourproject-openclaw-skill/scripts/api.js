/**
 * OurProject API - Core helper for all scripts
 * Usage: node scripts/api.js <METHOD> <endpoint> [body_json]
 * Example: node scripts/api.js GET /projects
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

const CONFIG_FILE = path.join(__dirname, '..', '.config.json');

function loadConfig() {
    try {
        return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
    } catch {
        console.error('❌ Not configured. Run: node scripts/setup.js');
        process.exit(1);
    }
}

function makeRequest(method, endpoint, body = null) {
    const config = loadConfig();
    return new Promise((resolve, reject) => {
        const baseUrl = config.apiBaseUrl || 'https://api.ourproject.app/api';
        // Normalize: if endpoint already has /api/ prefix, strip it since baseUrl already includes /api
        const normalizedEndpoint = endpoint.startsWith('/api/') ? endpoint.slice(4) : endpoint;
        const fullEndpoint = normalizedEndpoint.startsWith('/') ? normalizedEndpoint : '/' + normalizedEndpoint;
        const url = new URL(baseUrl + fullEndpoint);
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;

        const options = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname + url.search,
            method: method.toUpperCase(),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${config.apiKey}`,
                'User-Agent': 'OurProject-OpenClaw-Skill/1.0'
            },
        };

        const req = lib.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (res.statusCode === 401) {
                        console.error('❌ Authentication failed. Run: node scripts/setup.js to reconfigure.');
                        process.exit(1);
                    }
                    resolve({ status: res.statusCode, data: json });
                } catch {
                    resolve({ status: res.statusCode, data: data });
                }
            });
        });

        req.on('error', (err) => {
            reject(new Error(`Connection failed: ${err.message}. Make sure ourproject.app is accessible.`));
        });

        if (body) req.write(typeof body === 'string' ? body : JSON.stringify(body));
        req.end();
    });
}

async function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.log('Usage: node scripts/api.js <METHOD> <endpoint> [body_json]');
        console.log('');
        console.log('Examples:');
        console.log('  node scripts/api.js GET /projects');
        console.log('  node scripts/api.js GET /tasks');
        console.log('  node scripts/api.js GET /finance/dashboard');
        console.log('  node scripts/api.js POST /notes \'{"title":"Test","content":"Hello"}\'');
        process.exit(1);
    }

    const method = args[0];
    const endpoint = args[1];
    const body = args[2] ? JSON.parse(args[2]) : null;

    try {
        const result = await makeRequest(method, endpoint, body);
        console.log(JSON.stringify(result.data, null, 2));
    } catch (err) {
        console.error('❌', err.message);
    }
}

module.exports = { makeRequest, loadConfig };

if (require.main === module) {
    main();
}
