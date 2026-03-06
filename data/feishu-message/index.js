#!/usr/bin/env node
const { program } = require('commander');
const fs = require('fs');
const path = require('path');
const { spawn } = require('child_process');

require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

function runScript(scriptName, args) {
    const scriptPath = path.resolve(__dirname, scriptName);
    if (!fs.existsSync(scriptPath)) {
        console.error(`Error: Script ${scriptName} not found at ${scriptPath}`);
        process.exit(1);
    }
    
    // Pass stdio: 'inherit' to preserve colors and output
    const child = spawn(process.execPath, [scriptPath, ...args], {
        stdio: 'inherit',
        env: process.env
    });
    
    child.on('close', (code) => process.exit(code));
    child.on('error', (err) => {
        console.error(`Error spawning ${scriptName}:`, err);
        process.exit(1);
    });
}

program
    .name('feishu-message')
    .description('Unified Feishu Toolkit for messaging, groups, and files')
    .version('1.1.0');

// Subcommand: get (calls get.js)
program
    .command('get')
    .description('Get a message by ID')
    .argument('<message_id>', 'Message ID')
    .option('-r, --raw', 'Output raw JSON')
    .option('-R, --recursive', 'Recursively fetch merged messages')
    .action((id, options) => {
        const args = [id];
        if (options.raw) args.push('--raw');
        if (options.recursive) args.push('--recursive');
        runScript('get.js', args);
    });

// Subcommand: send (proxies to feishu-post)
program
    .command('send')
    .description('Send a rich text message (via feishu-post)')
    .requiredOption('-t, --target <id>', 'Target ID')
    .option('-c, --content <text>', 'Content')
    .option('-x, --text <text>', 'Text')
    .option('--title <text>', 'Title')
    .action((options) => {
        const scriptPath = path.resolve(__dirname, '../feishu-post/send.js');
        const args = ['--target', options.target];
        if (options.content) args.push('--content', options.content);
        if (options.text) args.push('--text', options.text);
        if (options.title) args.push('--title', options.title);
        
        const child = spawn(process.execPath, [scriptPath, ...args], {
            stdio: 'inherit',
            env: process.env
        });
        child.on('close', (code) => process.exit(code));
    });

// Subcommand: send-audio (calls send-audio.js)
program
    .command('send-audio')
    .description('Send an audio file')
    .requiredOption('-t, --target <id>', 'Target ID (user/chat)')
    .requiredOption('-f, --file <path>', 'Audio file path')
    .option('-d, --duration <ms>', 'Duration in ms')
    .action((options) => {
        const args = ['--target', options.target, '--file', options.file];
        if (options.duration) args.push('--duration', options.duration);
        runScript('send-audio.js', args);
    });

// Subcommand: create-chat (calls create_chat.js)
program
    .command('create-chat')
    .description('Create a group chat')
    .requiredOption('-n, --name <name>', 'Chat name')
    .requiredOption('-u, --users <ids...>', 'User IDs')
    .option('--desc <text>', 'Description')
    .option('--content <text>', 'Description (alias)')
    .action((options) => {
        const args = ['--name', options.name, '--users', ...options.users];
        const desc = options.desc || options.content;
        if (desc) args.push('--desc', desc);
        runScript('create_chat.js', args);
    });

// Subcommand: list-pins (calls list_pins_v2.js)
program
    .command('list-pins')
    .description('List pinned messages in a chat')
    .argument('<chat_id>', 'Chat ID')
    .action((chatId) => {
        runScript('list_pins_v2.js', [chatId]);
    });

program.parse();
