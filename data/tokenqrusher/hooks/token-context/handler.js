/**
 * Token Context Hook
 *
 * SECURITY MANIFEST:
 *   Environment variables: none
 *   External endpoints: none
 *   Local files read: ~/.openclaw/hooks/token-context/config.json
 *   Local files written: none
 */
'use strict';

const shared = require('../token-shared/shared');

/**
 * Main handler function
 * @param {Object} event
 * @returns {Promise<void>}
 */
async function handler(event) {
    // Entry log
    console.log('[token-context] Entry: handler');

    // Guard: Only handle agent:bootstrap
    if (event.type !== 'agent' || event.action !== 'bootstrap') {
        return;
    }

    // Load config with caching
    const config = shared.loadConfigCached((msg) => console.log(msg));
    
    // Guard: Hook disabled
    if (config.enabled === false) {
        console.log('[token-context] Exit: disabled');
        return;
    }

    // Guard: No context
    const context = event.context;
    if (!context) {
        console.log('[token-context] Exit: no context');
        return;
    }

    // Extract message using shared pure function
    const messageResult = shared.extractUserMessage(context);
    if (!messageResult.isJust) {
        console.log('[token-context] Exit: no message');
        return;
    }

    const message = messageResult.value;

    // Classify using shared pure function
    const classification = shared.classifyComplexity(message);
    const allowedFiles = shared.getAllowedFiles(classification.level, config);
    
    // Filter files
    const currentFiles = context.bootstrapFiles || [];
    const currentFileNames = currentFiles.map(f => f.name);

    const filteredFiles = currentFiles.filter(f => 
        shared.isValidFileName(f.name) && allowedFiles.includes(f.name)
    );

    const removed = currentFileNames.filter(f => !allowedFiles.includes(f));

    // Log results
    if (removed.length > 0) {
        console.log(`[token-context] 📉 ${currentFileNames.length} → ${filteredFiles.length} files`);
        console.log(`[token-context]    Removed: ${removed.join(', ')}`);
    } else {
        console.log(`[token-context] ✓ ${filteredFiles.length} files (${classification.level})`);
    }

    // Apply filter
    if (!config.dryRun) {
        context.bootstrapFiles = filteredFiles;
    }

    console.log('[token-context] Exit: success');
}

/**
 * Export for OpenClaw
 */
module.exports = handler;
module.exports.default = handler;
