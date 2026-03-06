#!/usr/bin/env node

/**
 * OpenRouter CLI Wrapper for OpenClaw
 * 
 * Provides connectivity precheck via --test and delegates 
 * image generation requests to the core generate.js script.
 * 
 * @module openrouter-wrapper
 */

const { spawn } = require('child_process');
const path = require('path');
const adapter = require('../adapters/openrouter');

const args = process.argv.slice(2);

/**
 * Fetches and displays available image models from OpenRouter
 */
async function listModels() {
    try {
        const apiKey = process.env.OPENROUTER_API_KEY;
        const defaultModel = process.env.IMAGE_GEN_TEXT_TO_IMAGE_MODEL || 'bytedance-seed/seedream-4.5';
        
        if (!apiKey) {
            console.error('Error: OPENROUTER_API_KEY not set');
            process.exit(1);
        }
        
        const response = await fetch('https://openrouter.ai/api/v1/models', {
            headers: { 'Authorization': `Bearer ${apiKey}` }
        });
        
        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`HTTP error! status: ${response.status}. Body: ${errorBody}`);
        }
        
        const data = await response.json();

        // Validate response format
        if (!data || !data.data || !Array.isArray(data.data)) {
            console.error('Error: Unexpected response format from OpenRouter API');
            process.exit(1);
        }
        
        // Filter for image models
        const imageModels = data.data.filter(m => 
            m.id.includes('image') || 
            m.architecture?.modality === 'image' ||
            m.id.includes('seedream') ||
            m.id.includes('dall-e') ||
            m.id.includes('imagen')
        );
        
        if (imageModels.length === 0) {
            console.log('No image models found on OpenRouter.');
            process.exit(0);
        }

        // Sort by model ID
        imageModels.sort((a, b) => a.id.localeCompare(b.id));
        
        console.log('Available Image Models:\n');
        imageModels.forEach(model => {
            const isDefault = model.id === defaultModel;
            const prefix = isDefault ? ' [DEFAULT] ' : '  ';
            console.log(`${prefix}${model.id}`);
            console.log(`    Name: ${model.name || 'N/A'}`);
            console.log(`    Description: ${model.description || 'N/A'}\n`);
        });
        process.exit(0);
    } catch (error) {
        console.error('Failed to fetch models:', error.message);
        process.exit(1);
    }
}
/**
 * Handles the --test flag to validate environment and connectivity
 */
async function handleTest() {
    try {
        const result = await adapter.test();
        if (result.success) {
            console.log(JSON.stringify(result, null, 2));
            process.exit(0);
        } else {
            console.error(JSON.stringify(result.error || result, null, 2));
            process.exit(1);
        }
    } catch (error) {
        console.error(JSON.stringify(adapter.createError(
            adapter.ErrorCodes.API_ERROR,
            `Precheck failed: ${error.message}`,
            500
        ), null, 2));
        process.exit(1);
    }
}

/**
 * Delegates CLI arguments to the core generate.js script
 * 
 * @param {string[]} cliArgs - Arguments to delegate
 */
function delegateToCore(cliArgs) {
    const coreScript = path.resolve(__dirname, '../generate.js');
    
    // Check if core script exists
    const fs = require('fs');
    if (!fs.existsSync(coreScript)) {
        console.error(JSON.stringify(adapter.createError(
            adapter.ErrorCodes.CONFIG_ERROR,
            'Core generation script not found. Ensure Task 7 is complete.',
            500
        ), null, 2));
        process.exit(1);
    }

    const child = spawn('node', [coreScript, ...cliArgs], {
        stdio: 'inherit',
        env: process.env
    });

    child.on('close', (code) => {
        process.exit(code || 0);
    });

    child.on('error', (err) => {
        console.error(JSON.stringify(adapter.createError(
            adapter.ErrorCodes.API_ERROR,
            `Failed to delegate to core script: ${err.message}`,
            500
        ), null, 2));
        process.exit(1);
    });
}

// Main CLI logic
if (args.includes('--list-models')) {
    listModels();
} else if (args.includes('--test') || args.includes('-t')) {
    handleTest();
} else if (args.length > 0 && args.some(arg => arg.startsWith('--'))) {
    delegateToCore(args);
} else {
    // Show usage
    console.log('OpenRouter Image Generation Wrapper for OpenClaw');
    console.log('');
    console.log('Usage:');
    console.log('  node openrouter.js --test               Precheck connectivity and configuration');
    console.log('  node openrouter.js --list-models         List available image models from OpenRouter');
    console.log('  node openrouter.js --prompt <text>      Generate image (delegates to generate.js)');
    console.log('  node openrouter.js [options]            Additional flags: --model, --i2i-model, --input-image, --size, --output');
    console.log('');
    console.log('Environment:');
    console.log('  OPENROUTER_API_KEY                      Required for authentication');
    console.log('');
    process.exit(0);
}
