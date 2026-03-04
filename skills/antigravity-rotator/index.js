#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const Rotator = require('./scripts/rotator');
const Dashboard = require('./scripts/dashboard');

// 1. Load Config
const configPath = path.resolve(__dirname, 'config.json');
const exampleConfigPath = path.resolve(__dirname, 'assets/config.example.json');

if (!fs.existsSync(configPath)) {
    if (fs.existsSync(exampleConfigPath)) {
        console.log("ℹ️ Config file not found. Creating default config from example...");
        fs.copyFileSync(exampleConfigPath, configPath);
    } else {
        console.error("❌ config.json not found and no example available.");
        process.exit(1);
    }
}

const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));

// 2. Parse Args
const args = process.argv.slice(2);
let action = 'rotate'; // default

args.forEach(arg => {
    if (arg.startsWith('--action=')) {
        action = arg.split('=')[1];
    }
});

// 3. Execute
(async () => {
    if (action === 'setup') {
        console.log("🛠️ Antigravity Rotator Setup Helper");
        const { execSync } = require('child_process');
        try {
            const openclawPath = execSync('which openclaw', { encoding: 'utf8' }).trim();
            const nodePath = process.execPath;
            console.log(`\nFound openclaw at: ${openclawPath}`);
            console.log(`Found node at: ${nodePath}`);
            
            config.openclawBin = openclawPath;
            fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
            
            console.log("\n✅ config.json has been updated with your local paths.");
            console.log("\nNext steps:");
            console.log(`1. Run dashboard: node ${path.relative(process.cwd(), __filename)} --action=dashboard`);
            console.log(`2. Setup cron (recommended):`);
            console.log(`   */10 * * * * ${nodePath} ${path.resolve(__filename)} --action=rotate >> /tmp/antigravity-rotate.log 2>&1`);
        } catch (e) {
            console.error("\n❌ Could not automatically find openclaw. Please set 'openclawBin' in config.json manually.");
        }
        return;
    }
    
    if (action === 'rotate') {
        const rotator = new Rotator(config);
        await rotator.run();
    } else if (action === 'dashboard') {
        const dashboard = new Dashboard(config);
        dashboard.start();
    } else {
        console.error(`Unknown action: ${action}`);
        console.log("Available actions: --action=rotate, --action=dashboard");
    }
})();
