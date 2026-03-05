#!/usr/bin/env node
/**
 * Memory Mode Toggle
 * 
 * Toggle between fast (standard) and focus (curated) retrieval modes
 * 
 * Usage:
 *   node memory_mode.js focus      # Enable focus mode
 *   node memory_mode.js unfocus    # Disable focus mode
 *   node memory_mode.js status     # Check current mode
 */

import path from 'path';
import { fileURLToPath } from 'url';
import { initDatabase, getMeta, setMeta } from './db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const DB_PATH = process.env.MEMORY_DB_PATH || path.join(__dirname, 'vector-memory.db');
const MODE_KEY = 'search_mode';

/**
 * Get current search mode
 * @returns {string} 'fast' or 'focus'
 */
export function getSearchMode() {
    const db = initDatabase(DB_PATH);
    const mode = getMeta(db, MODE_KEY) || 'fast';
    db.close();
    return mode;
}

/**
 * Set search mode
 * @param {string} mode - 'fast' or 'focus'
 */
export function setSearchMode(mode) {
    if (!['fast', 'focus'].includes(mode)) {
        throw new Error(`Invalid mode: ${mode}. Use 'fast' or 'focus'.`);
    }
    
    const db = initDatabase(DB_PATH);
    setMeta(db, MODE_KEY, mode);
    db.close();
    
    return mode;
}

/**
 * Toggle focus mode on
 */
export function enableFocus() {
    setSearchMode('focus');
    return {
        mode: 'focus',
        description: 'Curated retrieval via Focus Agent',
        behavior: 'Searches will use multi-pass curation (retrieve → rank → synthesize)'
    };
}

/**
 * Toggle focus mode off (back to fast)
 */
export function disableFocus() {
    setSearchMode('fast');
    return {
        mode: 'fast',
        description: 'Standard retrieval',
        behavior: 'Searches use direct vector similarity'
    };
}

/**
 * Get mode status
 */
export function getModeStatus() {
    const mode = getSearchMode();
    
    if (mode === 'focus') {
        return {
            mode: 'focus',
            active: true,
            description: 'Curated retrieval via Focus Agent',
            behavior: 'Searches use multi-pass curation (retrieve → rank → synthesize)',
            toggle: 'Run "node memory_mode.js unfocus" to switch to fast mode'
        };
    }
    
    return {
        mode: 'fast',
        active: false,
        description: 'Standard retrieval',
        behavior: 'Searches use direct vector similarity',
        toggle: 'Run "node memory_mode.js focus" to enable focus mode'
    };
}

/**
 * CLI handler
 */
async function main() {
    const args = process.argv.slice(2);
    const command = args[0];
    
    switch (command) {
        case 'focus':
            const focusResult = enableFocus();
            console.log(JSON.stringify(focusResult, null, 2));
            break;
            
        case 'unfocus':
        case 'fast':
            const fastResult = disableFocus();
            console.log(JSON.stringify(fastResult, null, 2));
            break;
            
        case 'status':
            const status = getModeStatus();
            console.log(JSON.stringify(status, null, 2));
            break;
            
        default:
            console.log(`
Memory Mode Toggle

Toggle between fast (standard) and focus (curated) retrieval modes.

Usage:
  node memory_mode.js focus      # Enable focus mode (curated retrieval)
  node memory_mode.js unfocus    # Disable focus mode (standard retrieval)
  node memory_mode.js status     # Check current mode

Modes:
  fast   - Direct vector similarity search (quick, cheap)
  focus  - Multi-pass curation via Focus Agent (deeper, higher quality)

When in focus mode:
  1. Search retrieves broad set (20+ chunks)
  2. Focus Agent ranks and selects most relevant
  3. Synthesis produces coherent context narrative
  4. Main agent receives curated, focused context

Environment:
  MEMORY_DB_PATH  - Path to SQLite database (default: ./vector-memory.db)
`);
    }
}

// Only run main if this file is executed directly (not imported)
if (import.meta.url === `file://${process.argv[1]}`) {
    main().catch(err => {
        console.error('Error:', err.message);
        process.exit(1);
    });
}
