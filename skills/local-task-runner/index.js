const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const crypto = require('crypto');

// Configuration
const TASK_DIR = path.join(__dirname, '.tasks');
if (!fs.existsSync(TASK_DIR)) {
    fs.mkdirSync(TASK_DIR, { recursive: true });
}

// Helper: Run a command
function runCommand(command, timeout = 30000) {
    return new Promise((resolve, reject) => {
        const child = exec(command, { timeout: timeout, maxBuffer: 1024 * 1024 * 5 }, (error, stdout, stderr) => {
            if (error) {
                resolve({ 
                    success: false, 
                    error: error.message, 
                    code: error.code,
                    signal: error.signal,
                    stdout: stdout, 
                    stderr: stderr 
                });
            } else {
                resolve({ 
                    success: true, 
                    stdout: stdout, 
                    stderr: stderr 
                });
            }
        });
    });
}

// Helper: Parse CLI arguments
function parseArgs() {
    const args = process.argv.slice(2);
    const options = {};
    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg.startsWith('--')) {
            const key = arg.slice(2);
            let value = true;
            if (i + 1 < args.length && !args[i + 1].startsWith('--')) {
                value = args[i + 1];
            }
            options[key] = value;
        }
    }
    return options;
}

// Main logic
async function main() {
    const options = parseArgs();
    
    // Command: run
    // Usage: node index.js run --code "console.log('hi')"
    if (process.argv[2] === 'run') {
        const code = options.code;
        if (!code) {
            console.error('Error: --code argument is required.');
            process.exit(1);
        }

        const timeout = parseInt(options.timeout || '30000', 10);
        const taskId = crypto.randomBytes(4).toString('hex');
        const fileName = `task_${taskId}.js`;
        const filePath = path.join(TASK_DIR, fileName);

        console.log(`[TASK:${taskId}] Starting... (Timeout: ${timeout}ms)`);

        let result = null;
        let duration = 0;

        try {
            // Write code to temporary file
            fs.writeFileSync(filePath, code);

            // Execute
            const startTime = Date.now();
            result = await runCommand(`node "${filePath}"`, timeout);
            duration = Date.now() - startTime;

            // Cleanup
            try {
                fs.unlinkSync(filePath);
            } catch (cleanupErr) {
                console.warn(`[TASK:${taskId}] Warning: Failed to cleanup ${fileName}: ${cleanupErr.message}`);
            }

            // Output
            if (result.success) {
                console.log(`[TASK:${taskId}] Completed in ${duration}ms`);
                if (result.stdout) console.log('--- STDOUT ---\n' + result.stdout.trim());
                if (result.stderr) console.log('--- STDERR ---\n' + result.stderr.trim());
            } else {
                console.log(`[TASK:${taskId}] Failed in ${duration}ms`);
                console.log(`Error: ${result.error}`);
                if (result.code) console.log(`Exit Code: ${result.code}`);
                if (result.signal) console.log(`Signal: ${result.signal}`);
                if (result.stdout) console.log('--- STDOUT ---\n' + result.stdout.trim());
                if (result.stderr) console.log('--- STDERR ---\n' + result.stderr.trim());
                process.exit(1);
            }

        } catch (err) {
            console.error(`[TASK:${taskId}] Internal Error: ${err.message}`);
            process.exit(1);
        }
    } else {
        console.log('Usage: node skills/local-task-runner/index.js run --code "..." [--timeout 30000]');
    }
}

main().catch(err => {
    console.error('Fatal Error:', err);
    process.exit(1);
});
