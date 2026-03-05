#!/usr/bin/env node

/**
 * Ghost Snippet Extractor
 * 
 * Extracts Ghost snippets from a specially-formatted draft post.
 * 
 * WORKFLOW:
 * 1. In Ghost, create a new draft post
 * 2. For each snippet, insert:
 *    - A paragraph: "SNIPPET: snippet-name-here"
 *    - The snippet content
 * 3. Get the post URL or ID
 * 4. Run: node snippet-extractor.js <post-id-or-slug>
 * 5. Script extracts each snippet and saves to library/
 * 
 * EXAMPLE POST STRUCTURE:
 * 
 * SNIPPET: signature
 * [horizontal rule]
 * — Chris Giddings
 * Software Developer | Writer
 * 
 * SNIPPET: newsletter-footer
 * [callout: Subscribe to newsletter!]
 * [button: Subscribe Now]
 * 
 * SNIPPET: book-review-header
 * [your book review template content]
 */

import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import fs from 'fs';
import { getLibraryPath, ensureConfigured } from '../snippets/snippet-config.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Get library path (will be initialized in main function)
let LIBRARY_DIR = getLibraryPath();

/**
 * Sanitize snippet name for safe filesystem usage
 * Prevents path traversal and dangerous characters
 * @param {string} name - Raw snippet name from marker
 * @returns {string} Safe filename
 */
function sanitizeSnippetName(name) {
  if (!name || typeof name !== 'string') {
    throw new Error('Snippet name cannot be empty');
  }
  
  // Remove path separators (prevent path traversal)
  name = name.replace(/[/\\]/g, '-');
  
  // Remove dangerous characters and control codes
  name = name.replace(/[<>:"|?*\x00-\x1F\x7F]/g, '');
  
  // Remove leading/trailing dots and whitespace
  name = name.trim().replace(/^\.+|\.+$/g, '');
  
  // Replace multiple spaces/dashes with single dash
  name = name.replace(/[\s-]+/g, '-');
  
  // Limit length (filesystem compatibility)
  name = name.substring(0, 100);
  
  // Prevent directory traversal attempts
  if (name === '.' || name === '..' || name.includes('..')) {
    throw new Error(`Invalid snippet name (path traversal attempt): "${name}"`);
  }
  
  // Prevent hidden files
  if (name.startsWith('.')) {
    throw new Error(`Invalid snippet name (hidden file): "${name}"`);
  }
  
  // Ensure not empty after sanitization
  if (!name || name.length === 0) {
    throw new Error('Snippet name invalid after sanitization');
  }
  
  return name;
}

/**
 * Sanitize marker prefix for safe regex usage
 * Prevents regex injection
 * @param {string} marker - Raw marker prefix
 * @returns {string} Safe marker
 */
function sanitizeMarker(marker) {
  if (!marker || typeof marker !== 'string') {
    return 'SNIPPET:';
  }
  
  // Limit length
  marker = marker.substring(0, 50);
  
  // Remove characters that could cause regex issues
  marker = marker.replace(/[^\w\s:.-]/g, '');
  
  // Trim
  marker = marker.trim();
  
  // Fallback if empty
  if (!marker) {
    return 'SNIPPET:';
  }
  
  return marker;
}

/**
 * Validate snippet size
 * @param {string} snippetName - Name of snippet
 * @param {Array} cards - Snippet cards
 */
function validateSnippetSize(snippetName, cards) {
  // Check card count
  if (cards.length > 100) {
    console.warn(`⚠️  Warning: Snippet "${snippetName}" has ${cards.length} cards (unusually large)`);
  }
  
  // Check total size
  const snippetJson = JSON.stringify(cards);
  const sizeMB = snippetJson.length / (1024 * 1024);
  
  if (snippetJson.length > 1024 * 1024) { // 1MB limit
    throw new Error(`Snippet "${snippetName}" is too large (${sizeMB.toFixed(2)}MB). Maximum 1MB allowed.`);
  }
  
  return true;
}

/**
 * Extract snippets from a Ghost post
 * @param {string} postIdOrSlug - Post ID or slug
 * @param {Object} options - Extraction options
 */
async function extractSnippets(postIdOrSlug, options = {}) {
  // Try to load from config files if not in env vars
  let apiUrl = options.apiUrl || process.env.GHOST_API_URL;
  let apiKey = options.apiKey || process.env.GHOST_ADMIN_KEY;

  if (!apiUrl || !apiKey) {
    try {
      const configDir = join(process.env.HOME, '.config', 'ghost');
      const apiUrlPath = join(configDir, 'api_url');
      const apiKeyPath = join(configDir, 'api_key');

      if (fs.existsSync(apiUrlPath) && fs.existsSync(apiKeyPath)) {
        apiUrl = fs.readFileSync(apiUrlPath, 'utf8').trim();
        apiKey = fs.readFileSync(apiKeyPath, 'utf8').trim();
      }
    } catch (err) {
      // Ignore errors, will fail below with better message
    }
  }

  if (!apiUrl || !apiKey) {
    throw new Error('Ghost credentials required. Set environment variables GHOST_API_URL and GHOST_ADMIN_KEY, or create config files in ~/.config/ghost/');
  }

  let {
    markerPrefix = 'SNIPPET:',
    dryRun = false,
    verbose = false
  } = options;
  
  // Sanitize marker prefix for security
  markerPrefix = sanitizeMarker(markerPrefix);

  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║         Ghost Snippet Extractor                        ║');
  console.log('╚════════════════════════════════════════════════════════╝\n');
  
  if (markerPrefix !== 'SNIPPET:') {
    console.log(`🔍 Using custom marker: "${markerPrefix}"\n`);
  }

  // Create ghostApi function with credentials
  const jwt = await import('jsonwebtoken');
  const https = await import('https');
  
  const [keyId, keySecret] = apiKey.split(':');
  
  function generateToken() {
    const payload = {
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + 300,
      aud: '/admin/'
    };
    return jwt.default.sign(payload, Buffer.from(keySecret, 'hex'), {
      algorithm: 'HS256',
      keyid: keyId
    });
  }
  
  function ghostApiRequest(endpoint, method = 'GET') {
    const token = generateToken();
    const url = new URL(`${apiUrl}/ghost/api/admin${endpoint}`);
    
    return new Promise((resolve, reject) => {
      const req = https.default.request(url, {
        method,
        headers: {
          'Authorization': `Ghost ${token}`,
          'Content-Type': 'application/json',
          'Accept-Version': 'v5.0'
        }
      }, (res) => {
        let body = '';
        res.on('data', chunk => body += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            reject(new Error(`Invalid JSON: ${body}`));
          }
        });
      });
      req.on('error', reject);
      req.end();
    });
  }

  console.log(`📖 Fetching post: ${postIdOrSlug}`);
  
  // Fetch post with lexical format
  const response = await ghostApiRequest(`/posts/${postIdOrSlug}/?formats=lexical`, 'GET');
  
  if (!response.posts || response.posts.length === 0) {
    throw new Error(`Post not found: ${postIdOrSlug}`);
  }

  const post = response.posts[0];
  console.log(`✅ Found: "${post.title}"`);
  console.log(`   Status: ${post.status}`);
  console.log(`   Updated: ${new Date(post.updated_at).toLocaleDateString()}\n`);

  // Parse Lexical JSON
  const lexical = typeof post.lexical === 'string' 
    ? JSON.parse(post.lexical) 
    : post.lexical;

  const cards = lexical.root.children;
  console.log(`📦 Total cards in post: ${cards.length}\n`);

  // Find snippet markers and extract snippets
  const snippets = [];
  let currentSnippet = null;

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];

    // Check if this card is a snippet marker
    if (card.type === 'paragraph' && card.children) {
      const text = card.children.map(c => c.text || '').join('').trim();
      
      if (text.startsWith(markerPrefix)) {
        // Save previous snippet if exists
        if (currentSnippet) {
          snippets.push(currentSnippet);
        }

        // Start new snippet
        const snippetName = text.substring(markerPrefix.length).trim();
        currentSnippet = {
          name: snippetName,
          cards: [],
          startIndex: i
        };

        if (verbose) {
          console.log(`🔍 Found marker: "${text}" → snippet name: "${snippetName}"`);
        }
      } else if (currentSnippet) {
        // Add card to current snippet
        currentSnippet.cards.push(card);
      }
    } else if (currentSnippet) {
      // Add non-paragraph card to current snippet
      currentSnippet.cards.push(card);
    }
  }

  // Save last snippet
  if (currentSnippet) {
    snippets.push(currentSnippet);
  }

  console.log(`✨ Found ${snippets.length} snippets:\n`);

  // Display and save snippets
  for (const snippet of snippets) {
    console.log(`📌 Snippet: ${snippet.name}`);
    console.log(`   Cards: ${snippet.cards.length}`);
    console.log(`   Types: ${snippet.cards.map(c => c.type).join(', ')}`);

    try {
      // Sanitize filename for security
      const safeName = sanitizeSnippetName(snippet.name);
      
      // Validate size
      validateSnippetSize(safeName, snippet.cards);

      if (dryRun) {
        console.log(`   [DRY RUN] Would save to: library/${safeName}.json`);
      } else {
        // Save snippet to library
        const filename = `${safeName}.json`;
        const filepath = join(LIBRARY_DIR, filename);
        
        fs.writeFileSync(filepath, JSON.stringify(snippet.cards, null, 2));
        console.log(`   ✅ Saved: ${filepath}`);
      }

      if (verbose) {
        console.warn(`   ⚠️  Verbose mode: previews may contain sensitive data`);
        console.log(`   Preview: ${JSON.stringify(snippet.cards[0], null, 2).substring(0, 100)}...`);
      }
    } catch (error) {
      console.error(`   ❌ Error saving snippet: ${error.message}`);
      continue;
    }

    console.log('');
  }

  // Summary
  console.log('╔════════════════════════════════════════════════════════╗');
  console.log('║                    EXTRACTION COMPLETE                 ║');
  console.log('╚════════════════════════════════════════════════════════╝\n');

  console.log(`📊 Summary:`);
  console.log(`   Total snippets extracted: ${snippets.length}`);
  console.log(`   Saved to: ${LIBRARY_DIR}`);
  
  if (dryRun) {
    console.log(`\n⚠️  DRY RUN MODE - No files were saved`);
    console.log(`   Remove --dry-run to save snippets\n`);
  } else {
    console.log(`\n✅ Snippets ready to use!`);
    console.log(`   List: node snippets/ghost-snippet.js list`);
    console.log(`   Preview: node snippets/ghost-snippet.js preview ${snippets[0]?.name || 'snippet-name'}\n`);
  }

  return snippets;
}

/**
 * Validate snippet extraction post
 * Checks if post follows the correct format
 */
async function validatePost(postIdOrSlug, options = {}) {
  console.log('🔍 Validating snippet extraction post format...\n');

  const snippets = await extractSnippets(postIdOrSlug, {
    ...options,
    dryRun: true,
    verbose: true
  });

  console.log('\n📋 Validation Results:\n');

  if (snippets.length === 0) {
    console.log('❌ No snippets found!');
    console.log('\nExpected format:');
    console.log('   SNIPPET: snippet-name');
    console.log('   [snippet content cards]');
    console.log('   SNIPPET: another-snippet');
    console.log('   [snippet content cards]\n');
    return false;
  }

  console.log('✅ Format looks good!');
  console.log(`   Found ${snippets.length} snippets`);
  console.log(`\n💡 Run without --validate to extract snippets\n`);
  return true;
}

// CLI Usage
if (import.meta.url === `file://${process.argv[1]}`) {
  // Async wrapper for configuration
  (async () => {
    // Ensure library is configured before extraction
    LIBRARY_DIR = await ensureConfigured(process.stdout.isTTY);
    
    const args = process.argv.slice(2);
    
    if (args.includes('--help') || args.length === 0) {
    console.log(`
Ghost Snippet Extractor

USAGE:
  snippet-extractor.js <post-id-or-slug> [options]

OPTIONS:
  --dry-run          Preview extraction without saving files
  --validate         Validate post format without extracting
  --verbose          Show detailed extraction info
  --marker <prefix>  Custom marker prefix (default: "SNIPPET:")
  --help             Show this help

WORKFLOW:

1. CREATE SNIPPET EXTRACTION POST IN GHOST:
   
   Create a new draft post with this structure:
   
   SNIPPET: signature
   [Insert your "signature" snippet here]
   
   SNIPPET: newsletter-footer
   [Insert your "newsletter-footer" snippet here]
   
   SNIPPET: book-review-header
   [Insert your "book-review-header" snippet here]

2. GET POST ID OR SLUG:
   
   From Ghost Admin URL:
   https://your-blog.ghost.io/ghost/#/editor/post/65f1234abcd567890
                                                  ^^^^^^^^^^^^^^^^
                                                  This is the post ID
   
   Or use the post slug (URL-friendly title)

3. EXTRACT SNIPPETS:
   
   # Validate format first (dry run)
   node snippet-extractor.js my-snippets --validate
   
   # Extract and save
   export GHOST_API_URL="https://your-blog.ghost.io"
   export GHOST_ADMIN_KEY="your_admin_key"
   node snippet-extractor.js my-snippets

4. USE EXTRACTED SNIPPETS:
   
   node ghost-snippet.js list
   node ghost-snippet.js preview signature

EXAMPLES:

  # Extract from post with ID
  node snippet-extractor.js 65f1234abcd567890

  # Extract from post by slug
  node snippet-extractor.js my-snippets-post

  # Dry run (preview only)
  node snippet-extractor.js my-snippets --dry-run

  # Validate post format
  node snippet-extractor.js my-snippets --validate

  # Custom marker prefix
  node snippet-extractor.js my-snippets --marker "--- SNIPPET:"

  # Verbose output
  node snippet-extractor.js my-snippets --verbose

TIPS:

- Use paragraph text "SNIPPET: name-here" as markers
- Snippet names become filenames (use kebab-case)
- Everything between markers becomes the snippet
- Markers are NOT included in saved snippets
- Original Ghost snippets remain unchanged
- Safe to delete extraction post after running

REQUIREMENTS:

- GHOST_API_URL environment variable
- GHOST_ADMIN_KEY environment variable
- Draft post in Ghost with snippets
`);
    process.exit(0);
  }

  const postIdOrSlug = args[0];
  const options = {
    dryRun: args.includes('--dry-run'),
    verbose: args.includes('--verbose'),
    markerPrefix: args.includes('--marker') 
      ? args[args.indexOf('--marker') + 1]
      : 'SNIPPET:'
  };

  try {
    if (args.includes('--validate')) {
      await validatePost(postIdOrSlug, options);
    } else {
      await extractSnippets(postIdOrSlug, options);
    }
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}\n`);
    process.exit(1);
  }
  })(); // End async wrapper
}

export { extractSnippets, validatePost };
