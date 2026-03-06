/**
 * OurProject Setup - Configure API key for OpenClaw skill
 * Usage: node scripts/setup.js
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');
const http = require('http');
const https = require('https');

const CONFIG_FILE = path.join(__dirname, '..', '.config.json');
const DEFAULT_API_URL = 'https://api.ourproject.app/api';

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
const ask = (q) => new Promise(resolve => rl.question(q, resolve));

function testApiKey(apiUrl, apiKey) {
    return new Promise((resolve, reject) => {
        const url = new URL(apiUrl + '/integrations/me');
        const isHttps = url.protocol === 'https:';
        const lib = isHttps ? https : http;

        const options = {
            hostname: url.hostname,
            port: url.port || (isHttps ? 443 : 80),
            path: url.pathname,
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'User-Agent': 'OurProject-OpenClaw-Skill/1.0'
            },
        };

        const req = lib.request(options, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try {
                    const json = JSON.parse(data);
                    if (res.statusCode === 200) {
                        resolve(json);
                    } else {
                        reject(new Error(json.message || `HTTP ${res.statusCode}`));
                    }
                } catch (e) {
                    reject(new Error('Invalid response'));
                }
            });
        });

        req.on('error', reject);
        req.end();
    });
}

async function setup() {
    console.log('');
    console.log('🦞 OurProject × OpenClaw Setup');
    console.log('================================');
    console.log('');
    console.log('Get your API key from: https://ourproject.app');
    console.log('Go to Integrations → API Keys → Generate');
    console.log('');

    // Check existing config
    let existingConfig = null;
    try {
        existingConfig = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf-8'));
        console.log(`Current config: API URL = ${existingConfig.apiBaseUrl}`);
        console.log(`                User = ${existingConfig.userName || 'Unknown'}`);
        console.log('');
    } catch { /* no existing config */ }

    // API URL
    const apiUrl = await ask(`API URL [${DEFAULT_API_URL}]: `);
    const finalApiUrl = apiUrl.trim() || (existingConfig?.apiBaseUrl || DEFAULT_API_URL);

    // API Key
    const apiKey = await ask('API Key (starts with op_): ');

    if (!apiKey.trim()) {
        console.error('❌ API key is required. Get one from Integrations → API Keys.');
        rl.close();
        process.exit(1);
    }

    if (!apiKey.trim().startsWith('op_')) {
        console.error('❌ Invalid API key format. Must start with "op_"');
        rl.close();
        process.exit(1);
    }

    // Test connection
    console.log('\n🔍 Testing connection...');

    try {
        const result = await testApiKey(finalApiUrl, apiKey.trim());
        const user = result.user;

        console.log(`\n✅ Connection successful!`);
        console.log(`   User: ${user.name}`);
        console.log(`   Email: ${user.email}`);
        console.log(`   Role: ${user.role}`);

        // Save config
        const config = {
            apiBaseUrl: finalApiUrl,
            apiKey: apiKey.trim(),
            userName: user.name,
            userEmail: user.email,
            configuredAt: new Date().toISOString()
        };

        fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
        console.log(`\n💾 Config saved to .config.json`);
        console.log('\n🎉 Setup complete! You can now use OurProject commands.');
        console.log('   Try: node scripts/summary.js');

    } catch (err) {
        console.error(`\n❌ Connection failed: ${err.message}`);
        console.error('   Check your API key and URL, then try again.');
    }

    rl.close();
}

setup();
