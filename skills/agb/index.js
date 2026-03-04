#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

const AGB_BIN = '/root/.local/bin/agent-browser';

// 执行 agb 命令
function runAgb(args) {
    return new Promise((resolve, reject) => {
        const proc = spawn(AGB_BIN, args, {
            cwd: process.cwd(),
            stdio: ['pipe', 'pipe', 'pipe']
        });

        let stdout = '';
        let stderr = '';

        proc.stdout.on('data', (data) => {
            stdout += data.toString();
        });

        proc.stderr.on('data', (data) => {
            stderr += data.toString();
        });

        proc.on('close', (code) => {
            if (code === 0) {
                resolve({ output: stdout.trim(), stderr: stderr.trim() });
            } else {
                reject(new Error(`agb exited with code ${code}: ${stderr}`));
            }
        });
    });
}

module.exports = {
    async open({ url }) {
        if (!url) throw new Error('URL is required');
        return runAgb(['open', url]);
    },

    async close() {
        return runAgb(['close']);
    },

    async click({ selector }) {
        if (!selector) throw new Error('Selector is required');
        return runAgb(['click', selector]);
    },

    async dblclick({ selector }) {
        if (!selector) throw new Error('Selector is required');
        return runAgb(['dblclick', selector]);
    },

    async fill({ selector, text }) {
        if (!selector || !text) throw new Error('Selector and text are required');
        return runAgb(['fill', selector, text]);
    },

    async type({ selector, text }) {
        if (!selector || !text) throw new Error('Selector and text are required');
        return runAgb(['type', selector, text]);
    },

    async press({ key }) {
        if (!key) throw new Error('Key is required');
        return runAgb(['press', key]);
    },

    async scroll({ direction, pixels = '500' }) {
        if (!direction) throw new Error('Direction is required');
        return runAgb(['scroll', direction, pixels]);
    },

    async screenshot({ path: filePath }) {
        const args = filePath ? ['screenshot', filePath] : ['screenshot'];
        return runAgb(args);
    },

    async snapshot() {
        return runAgb(['snapshot']);
    },

    async get({ property, selector }) {
        if (!property) throw new Error('Property is required');
        const args = property === 'text' && selector 
            ? ['get', 'text', selector] 
            : ['get', property];
        return runAgb(args);
    },

    async find({ type, value, action, name }) {
        if (!type || !action) throw new Error('Type and action are required');
        const args = ['find', type];
        
        if (type === 'role' && name) {
            args.push('--name', name);
        }
        args.push(action);
        
        if (value) args.push(value);
        
        return runAgb(args);
    },

    async wait({ selector, ms, text, url, load }) {
        if (ms) return runAgb(['wait', ms.toString()]);
        if (text) return runAgb(['wait', '--text', text]);
        if (url) return runAgb(['wait', '--url', url]);
        if (load) return runAgb(['wait', '--load', load]);
        if (selector) return runAgb(['wait', selector]);
        throw new Error('Wait condition is required');
    },

    async eval({ code }) {
        if (!code) throw new Error('JavaScript code is required');
        return runAgb(['eval', code]);
    },

    async title() {
        return runAgb(['get', 'title']);
    },

    async currentUrl() {
        return runAgb(['get', 'url']);
    }
};
