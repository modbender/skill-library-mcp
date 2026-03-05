#!/usr/bin/env node

/**
 * ClawGuard Post-Install Setup Script
 * Initializes the database with bundled blacklist data
 */

import { existsSync, mkdirSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { homedir } from 'os';

const __dirname = dirname(fileURLToPath(import.meta.url));

async function setup() {
    console.log('🔧 Setting up ClawGuard...');
    
    // Create config directory
    const configDir = join(homedir(), '.clawguard');
    if (!existsSync(configDir)) {
        mkdirSync(configDir, { recursive: true });
        console.log(`   Created ${configDir}`);
    }

    console.log('✅ Setup complete! Run "clawguard sync" to initialize the database.');
}

setup().catch(err => {
    console.error('Setup failed:', err.message);
    process.exit(1);
});
