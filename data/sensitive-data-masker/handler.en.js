/**
 * Sensitive Data Masker Hook
 * 
 * Automatically mask sensitive data when messages are received
 * 
 * Security: Uses spawn with argument array to prevent shell injection
 */

const { spawn } = require('child_process');
const path = require('path');

const MASKER_SCRIPT = path.join(__dirname, 'masker-wrapper.py');

/**
 * Hook handler
 * @param {Object} event - Event object
 */
async function handler(event) {
    // Only trigger on message:received events
    if (event.type !== 'message' || event.action !== 'received') {
        return;
    }

    try {
        const content = event.context.content || '';
        
        if (!content) {
            return;
        }

        // Use spawn with argument array (SAFE - no shell injection)
        const masker = spawn('python3', [MASKER_SCRIPT, 'mask', content], {
            stdio: ['pipe', 'pipe', 'ignore']
        });

        let output = '';
        let error = '';

        masker.stdout.on('data', (data) => {
            output += data.toString();
        });

        masker.stderr.on('data', (data) => {
            error += data.toString();
        });

        // Wait for process to complete
        const exitCode = await new Promise((resolve) => {
            masker.on('close', resolve);
        });

        // If masked content is different, update event
        if (exitCode === 0 && output.trim()) {
            const masked = JSON.parse(output.trim());
            
            // Update message content
            event.context.content = masked.masked;
            
            // Log masking information
            if (masked.count > 0) {
                console.log(`[sensitive-masker] Masked ${masked.count} sensitive items: ${masked.types.join(', ')}`);
            }
        } else if (error) {
            console.error('[sensitive-masker] Masking failed:', error);
        }
    } catch (error) {
        console.error('[sensitive-masker] Handler error:', error.message);
        // Error doesn't affect message processing, continue with original message
    }
}

module.exports = handler;
