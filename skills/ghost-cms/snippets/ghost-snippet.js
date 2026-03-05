#!/usr/bin/env node

/**
 * Ghost Snippet Manager
 * 
 * Manage local snippet library for Ghost CMS.
 * Workaround for Ghost Admin API snippet limitation (403 for integration tokens).
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { getLibraryPath, getExamplesPath, ensureConfigured } from './snippet-config.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// Get library path (external location for security)
let LIBRARY_DIR = getLibraryPath();
const EXAMPLES_DIR = getExamplesPath();

/**
 * Validate snippet name to prevent path traversal attacks
 * CRITICAL: This function prevents arbitrary file write/delete vulnerabilities
 */
function validateSnippetName(name) {
  if (!name || typeof name !== 'string') {
    throw new Error('Snippet name is required and must be a string');
  }
  
  // Prevent path traversal sequences
  if (name.includes('..') || name.includes('/') || name.includes('\\')) {
    throw new Error('Invalid snippet name: path traversal not allowed');
  }
  
  // Prevent absolute paths
  if (path.isAbsolute(name)) {
    throw new Error('Invalid snippet name: absolute paths not allowed');
  }
  
  // Only allow alphanumeric, hyphens, underscores
  const validNameRegex = /^[\w\-]+$/;
  if (!validNameRegex.test(name)) {
    throw new Error('Invalid snippet name: only alphanumeric, hyphens, and underscores allowed');
  }
  
  // Prevent empty name after validation
  if (name.length === 0 || name.length > 100) {
    throw new Error('Invalid snippet name: must be 1-100 characters');
  }
  
  return name;
}

/**
 * Load a snippet from library or examples
 */
export function loadSnippet(name, useExample = false) {
  // CRITICAL: Validate name to prevent path traversal
  const validatedName = validateSnippetName(name);
  
  const dir = useExample ? EXAMPLES_DIR : LIBRARY_DIR;
  const snippetPath = path.join(dir, `${validatedName}.json`);
  
  if (!fs.existsSync(snippetPath)) {
    throw new Error(`Snippet not found: ${name}`);
  }
  
  const content = fs.readFileSync(snippetPath, 'utf8');
  return JSON.parse(content);
}

/**
 * Save a snippet to library
 */
export function saveSnippet(name, cards) {
  // CRITICAL: Validate name to prevent arbitrary file write
  const validatedName = validateSnippetName(name);
  
  if (!fs.existsSync(LIBRARY_DIR)) {
    fs.mkdirSync(LIBRARY_DIR, { recursive: true });
  }
  
  const snippetPath = path.join(LIBRARY_DIR, `${validatedName}.json`);
  fs.writeFileSync(snippetPath, JSON.stringify(cards, null, 2));
  return snippetPath;
}

/**
 * List available snippets
 */
export function listSnippets(includeExamples = false) {
  const library = fs.existsSync(LIBRARY_DIR) 
    ? fs.readdirSync(LIBRARY_DIR).filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''))
    : [];
  
  const examples = includeExamples && fs.existsSync(EXAMPLES_DIR)
    ? fs.readdirSync(EXAMPLES_DIR).filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''))
    : [];
  
  return { library, examples };
}

/**
 * Delete a snippet from library
 */
export function deleteSnippet(name) {
  // CRITICAL: Validate name to prevent arbitrary file deletion
  const validatedName = validateSnippetName(name);
  
  const snippetPath = path.join(LIBRARY_DIR, `${validatedName}.json`);
  
  if (!fs.existsSync(snippetPath)) {
    throw new Error(`Snippet not found: ${name}`);
  }
  
  fs.unlinkSync(snippetPath);
}

/**
 * Inject snippet into Lexical content
 * @param {Array} snippet - Snippet cards array
 * @param {Object} lexicalContent - Existing Lexical document
 * @param {string} position - 'start', 'end', or index number
 */
export function injectSnippet(snippet, lexicalContent, position = 'end') {
  const children = lexicalContent.root.children;
  
  if (position === 'end') {
    children.push(...snippet);
  } else if (position === 'start') {
    children.unshift(...snippet);
  } else if (typeof position === 'number') {
    children.splice(position, 0, ...snippet);
  } else {
    throw new Error(`Invalid position: ${position}. Use 'start', 'end', or number.`);
  }
  
  return lexicalContent;
}

// CLI Usage
if (import.meta.url === `file://${process.argv[1]}`) {
  // Async wrapper for configuration
  (async () => {
    // Ensure library is configured before running commands
    LIBRARY_DIR = await ensureConfigured(process.stdout.isTTY);
    
    const command = process.argv[2];
    
    if (!command || command === 'help') {
    console.log(`
Ghost Snippet Manager

Usage:
  ghost-snippet.js list [--examples]     List available snippets
  ghost-snippet.js preview <name>        Preview snippet JSON
  ghost-snippet.js save <name> <file>    Save snippet to library
  ghost-snippet.js delete <name>         Delete snippet from library
  ghost-snippet.js copy <name> <dest>    Copy example to library

Examples:
  # List library snippets
  ghost-snippet.js list
  
  # List library + examples
  ghost-snippet.js list --examples
  
  # Preview a snippet
  ghost-snippet.js preview signature
  
  # Save new snippet
  ghost-snippet.js save my-cta cta.json
  
  # Copy example to library
  ghost-snippet.js copy signature-example signature
  
  # Delete snippet
  ghost-snippet.js delete old-snippet

For programmatic usage, import functions:
  import { loadSnippet, saveSnippet, injectSnippet } from './ghost-snippet.js';
`);
    process.exit(0);
  }
  
  try {
    switch (command) {
      case 'list': {
        const includeExamples = process.argv.includes('--examples');
        const { library, examples } = listSnippets(includeExamples);
        
        console.log('\\n📚 Snippet Library:');
        if (library.length === 0) {
          console.log('  (no snippets in library)');
        } else {
          library.forEach(s => console.log(`  ✓ ${s}`));
        }
        
        if (includeExamples && examples.length > 0) {
          console.log('\\n📖 Examples:');
          examples.forEach(s => console.log(`  • ${s}`));
        }
        
        console.log('\\nHint: Use --examples to see example snippets');
        break;
      }
      
      case 'preview': {
        const name = process.argv[3];
        const useExample = process.argv.includes('--example');
        
        if (!name) {
          console.error('Error: Snippet name required');
          console.log('Usage: ghost-snippet.js preview <name> [--example]');
          process.exit(1);
        }
        
        const snippet = loadSnippet(name, useExample);
        console.log(JSON.stringify(snippet, null, 2));
        break;
      }
      
      case 'save': {
        const name = process.argv[3];
        const file = process.argv[4];
        
        if (!name || !file) {
          console.error('Error: Name and file required');
          console.log('Usage: ghost-snippet.js save <name> <file>');
          process.exit(1);
        }
        
        if (!fs.existsSync(file)) {
          console.error(`Error: File not found: ${file}`);
          process.exit(1);
        }
        
        const content = JSON.parse(fs.readFileSync(file, 'utf8'));
        const savedPath = saveSnippet(name, content);
        console.log(`✅ Saved snippet: ${name}`);
        console.log(`   Location: ${savedPath}`);
        break;
      }
      
      case 'delete': {
        const name = process.argv[3];
        
        if (!name) {
          console.error('Error: Snippet name required');
          console.log('Usage: ghost-snippet.js delete <name>');
          process.exit(1);
        }
        
        deleteSnippet(name);
        console.log(`✅ Deleted snippet: ${name}`);
        break;
      }
      
      case 'copy': {
        const sourceName = process.argv[3];
        const destName = process.argv[4];
        
        if (!sourceName || !destName) {
          console.error('Error: Source and destination names required');
          console.log('Usage: ghost-snippet.js copy <source> <destination>');
          process.exit(1);
        }
        
        // Try to load from examples first, then library
        let snippet;
        try {
          snippet = loadSnippet(sourceName, true); // Try examples
        } catch {
          snippet = loadSnippet(sourceName, false); // Try library
        }
        
        const savedPath = saveSnippet(destName, snippet);
        console.log(`✅ Copied ${sourceName} → ${destName}`);
        console.log(`   Location: ${savedPath}`);
        break;
      }
      
      default:
        console.error(`Unknown command: ${command}`);
        console.log('Run "ghost-snippet.js help" for usage');
        process.exit(1);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
  })(); // End async wrapper
}
