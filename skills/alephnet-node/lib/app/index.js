/**
 * Application Module Index
 * 
 * Exports all application components for the Sentient Observer.
 */

// Use static imports for ES modules
import { colors, MIME_TYPES } from './constants.js';
import { parseArgs, printHelp } from './args.js';
import { 
    getSentientSystemPrompt, 
    initializeObserver, 
    truncateToolContent, 
    clearScreen, 
    Spinner 
} from './shared.js';
import { SentientCLI } from './cli.js';
import { SentientServer } from './server.js';

export {
    // Constants
    colors,
    MIME_TYPES,
    
    // Argument parsing
    parseArgs,
    printHelp,
    
    // Shared utilities
    getSentientSystemPrompt,
    initializeObserver,
    truncateToolContent,
    clearScreen,
    Spinner,
    
    // Main application classes
    SentientCLI,
    SentientServer
};

export default {
    colors,
    MIME_TYPES,
    parseArgs,
    printHelp,
    getSentientSystemPrompt,
    initializeObserver,
    truncateToolContent,
    clearScreen,
    Spinner,
    SentientCLI,
    SentientServer
};
