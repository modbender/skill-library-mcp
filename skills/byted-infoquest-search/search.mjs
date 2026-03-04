#!/usr/bin/env node

/**
 * InfoQuest Search CLI
 * AI-optimized web search using BytePlus InfoQuest API
 */

// Use global fetch if available (Node.js 18+), otherwise use dynamic import
let fetchImplementation;

if (typeof globalThis.fetch === 'function') {
  // Node.js 18+ has built-in fetch
  fetchImplementation = globalThis.fetch;
} else {
  // For older Node.js versions, use dynamic import
  fetchImplementation = async (...args) => {
    try {
      const { default: fetch } = await import('node-fetch');
      return fetch(...args);
    } catch (error) {
      throw new Error(
        'Fetch API not available. Node.js 18+ includes fetch natively. ' +
        'For older versions, install node-fetch: npm install node-fetch'
      );
    }
  };
}

const fetch = fetchImplementation;

function usage() {
  console.error(`Usage: search.mjs "query" [options]
  
Options:
  -s, --site <domain>     Search within specific site (e.g., github.com)
  -d, --days <number>     Search within last N days
  -h, --help              Show this help message

Examples:
  node search.mjs "OpenClaw AI framework"
  node search.mjs "machine learning" -d 7
  node search.mjs "Python tutorials" -s github.com
  node search.mjs "latest news" -d 1
`);
  process.exit(2);
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

const query = args[0];
let site = "";
let days = -1;

for (let i = 1; i < args.length; i++) {
  const arg = args[i];
  
  if (arg === "-s" || arg === "--site") {
    site = args[i + 1] || "";
    i++;
    continue;
  }
  
  if (arg === "-d" || arg === "--days") {
    days = parseInt(args[i + 1] || "7", 10);
    i++;
    continue;
  }
  
  console.error(`Unknown argument: ${arg}`);
  usage();
}

// Check API key
const apiKey = (process.env.INFOQUEST_API_KEY || "").trim();
if (!apiKey) {
  console.error("Error: INFOQUEST_API_KEY environment variable is not set");
  console.error("Set it using: export INFOQUEST_API_KEY='your-api-key-here'");
  console.error("Get your API key from: https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest");
  process.exit(1);
}

// Prepare request headers
function prepareHeaders() {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  return headers;
}

// Clean search results
function cleanResults(rawResults) {
  const seenUrls = new Set();
  const cleanResults = [];

  for (const contentList of rawResults) {
    const content = contentList.content;
    const results = content.results;

    // Process organic results
    if (results.organic) {
      for (const result of results.organic) {
        const cleanResult = { type: 'page' };
        if (result.title) cleanResult.title = result.title;
        if (result.desc) cleanResult.desc = result.desc;
        if (result.url) cleanResult.url = result.url;
        
        const url = cleanResult.url;
        if (url && !seenUrls.has(url)) {
          seenUrls.add(url);
          cleanResults.push(cleanResult);
        }
      }
    }

    // Process news results
    if (results.top_stories) {
      const news = results.top_stories;
      for (const item of news.items) {
        const cleanResult = { type: 'news' };
        if (item.time_frame) cleanResult.time_frame = item.time_frame;
        if (item.source) cleanResult.source = item.source;
        if (item.url) cleanResult.url = item.url;
        if (item.title) cleanResult.title = item.title;
        
        const url = cleanResult.url;
        if (url && !seenUrls.has(url)) {
          seenUrls.add(url);
          cleanResults.push(cleanResult);
        }
      }
    }
  }

  return cleanResults;
}

// Perform web search
async function performSearch(query, site = '', days = -1) {
  const headers = prepareHeaders();
  const params = {
    format: 'JSON',
    query
  };

  if (days > 0) {
    params.time_range = days;
  }

  if (site) {
    params.site = site;
  }

  try {
    const response = await fetch('https://search.infoquest.bytepluses.com', {
      method: 'POST',
      headers,
      body: JSON.stringify(params)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Search API returned status ${response.status}: ${errorText}`);
    }

    const data = await response.json();
    
    if (data.search_result) {
      const results = data.search_result.results;
      return cleanResults(results);
    } else if (data.content) {
      throw new Error('web search API return wrong format');
    } else {
      return data;
    }
  } catch (error) {
    throw new Error(`Search failed: ${error.message}`);
  }
}

// Main function
async function main() {
  try {
    const results = await performSearch(query, site, days > 0 ? days : -1);
    
    console.log(JSON.stringify({
      query,
      count: results.length,
      results
    }, null, 2));
    
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();