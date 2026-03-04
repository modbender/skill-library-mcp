#!/usr/bin/env node
/**
 * UniFuncs AI Search
 * Search the web with AI-powered results
 */

const API_KEY = process.env.UNIFUNCS_API_KEY;
const API_BASE = 'https://api.unifuncs.com';

if (!API_KEY) {
  console.error('Error: UNIFUNCS_API_KEY environment variable is not set');
  console.error('Please set it with: export UNIFUNCS_API_KEY=sk-xxxxxx');
  process.exit(1);
}

async function webSearch(query, options = {}) {
  const payload = {
    query,
    page: options.page || 1,
    count: options.count || 10,
    format: options.format || 'json'
  };

  if (options.freshness) payload.freshness = options.freshness;
  if (options.includeImages) payload.includeImages = options.includeImages;

  try {
    const response = await fetch(`${API_BASE}/api/web-search/search`, {
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

    const data = await response.json();
    return {
      success: true,
      data,
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
Usage: node web-search.js <query> [options]

Options:
  --freshness <period>   Time filter: Day, Week, Month, Year
  --count <number>      Results per page (1-50, default 10)
  --page <number>       Page number (default 1)
  --format <format>     Output format: json (default), markdown, text
  --include-images       Include image results

Example:
  node web-search.js "UniFuncs API" --freshness Week --count 20
`);
    process.exit(0);
  }

  const query = args[0];
  const options = {
    page: 1,
    count: 10,
    format: 'json'
  };

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--freshness':
        options.freshness = args[++i];
        break;
      case '--count':
        options.count = parseInt(args[++i]);
        break;
      case '--page':
        options.page = parseInt(args[++i]);
        break;
      case '--format':
        options.format = args[++i];
        break;
      case '--include-images':
        options.includeImages = true;
        break;
    }
  }

  const result = await webSearch(query, options);
  console.log(JSON.stringify(result, null, 2));
}

export { webSearch };
