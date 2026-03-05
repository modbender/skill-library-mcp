#!/usr/bin/env node
/**
 * UniFuncs Web Reader
 * Reads and extracts content from webpages
 */

const API_KEY = process.env.UNIFUNCS_API_KEY;
const API_BASE = 'https://api.unifuncs.com';

if (!API_KEY) {
  console.error('Error: UNIFUNCS_API_KEY environment variable is not set');
  console.error('Please set it with: export UNIFUNCS_API_KEY=sk-xxxxxx');
  process.exit(1);
}

async function webReader(url, options = {}) {
  const payload = {
    url,
    format: options.format || 'md',
    liteMode: options.liteMode || false,
    includeImages: options.includeImages !== false,
    linkSummary: options.linkSummary || false
  };

  if (options.topic) payload.topic = options.topic;
  if (options.onlyCSSSelectors) payload.onlyCSSSelectors = options.onlyCSSSelectors;
  if (options.excludeCSSSelectors) payload.excludeCSSSelectors = options.excludeCSSSelectors;

  try {
    const response = await fetch(`${API_BASE}/api/web-reader/read`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    const content = await response.text();
    return {
      success: true,
      data: content,
      error: null
    };
  } catch (error) {
    return {
      success: false,
      data: null,
      error: error.message
    };
  }
}

// CLI handling
if (import.meta.url === `file://${process.argv[1]}`) {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args[0] === '--help') {
    console.log(`
Usage: node web-reader.js <url> [options]

Options:
  --format <format>      Output format: markdown (default), text
  --lite                 Enable lite mode
  --no-images            Exclude images
  --link-summary         Append link summary
  --topic <topic>        Extract content related to topic

Example:
  node web-reader.js "https://example.com" --format markdown --lite
`);
    process.exit(0);
  }

  const url = args[0];
  const options = {
    format: 'md',
    liteMode: false,
    includeImages: true,
    linkSummary: false
  };

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--format':
        options.format = args[++i];
        break;
      case '--lite':
        options.liteMode = true;
        break;
      case '--no-images':
        options.includeImages = false;
        break;
      case '--link-summary':
        options.linkSummary = true;
        break;
      case '--topic':
        options.topic = args[++i];
        break;
    }
  }

  const result = await webReader(url, options);
  console.log(JSON.stringify(result, null, 2));
}

export { webReader };
