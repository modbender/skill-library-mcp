/**
 * Simple OpenClaw Client
 * Uses system messages to inject into the main session
 */

const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

class SimpleClient {
    constructor() {
        this.connected = true; // Always "connected" since we use CLI
    }

    async sendMessage(message, model = null) {
        try {
            // Use OpenClaw CLI to send message to main session
            let cmd = `openclaw sessions send --sessionKey agent:main:main --message ${this.escapeShellArg(message)}`;
            
            if (model) {
                cmd += ` --model ${model}`;
            }

            // Add timeout
            cmd += ' --timeoutSeconds 120';

            console.log('Executing:', cmd);

            const { stdout, stderr } = await execPromise(cmd, {
                timeout: 125000, // 2 minute + 5s buffer
                maxBuffer: 10 * 1024 * 1024 // 10MB buffer
            });

            if (stderr && !stderr.includes('warning') && !stderr.includes('Successfully')) {
                console.error('stderr:', stderr);
            }

            // Parse response (the actual AI response is in stdout)
            const response = stdout.trim();
            
            // Extract just the response part (after any status messages)
            const lines = response.split('\n');
            const responseText = lines[lines.length - 1] || 'Message sent';
            
            return {
                response: responseText,
                message: responseText
            };

        } catch (error) {
            throw new Error(`Failed to send message: ${error.message}`);
        }
    }

    escapeShellArg(arg) {
        // Escape for shell safety
        return `'${arg.replace(/'/g, "'\\''")}'`;
    }

    disconnect() {
        // No-op for CLI-based client
    }
}

module.exports = SimpleClient;
