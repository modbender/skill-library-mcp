#!/usr/bin/env node

/**
 * InfoQuest Extract CLI
 * Extract webpage content using BytePlus InfoQuest API
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
  console.error(`Usage: extract.mjs "url"
  
Examples:
  node extract.mjs "https://github.com/openclaw/openclaw"
`);
  process.exit(2);
}

// Parse command line arguments
const args = process.argv.slice(2);
if (args.length === 0 || args[0] === "-h" || args[0] === "--help") usage();

if (args.length > 1) {
  console.error("Error: Only one URL is supported");
  usage();
}

const url = args[0];

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

// Prepare crawl request data
function prepareCrawlRequestData(url) {
  return {
    url,
    format: 'HTML'
  };
}

// Format extracted content
function formatContent(content, url) {
  if (!content || content.startsWith('Error:')) {
    return `# Failed to extract content from: ${url}\nError: ${content}\n`;
  }
  
  return `# Content from: ${url}\n\n${content}\n`;
}

// Fetch webpage content
async function fetchContent(url, returnFormat = 'html') {
  const headers = prepareHeaders();
  const data = prepareCrawlRequestData(url, returnFormat);

  try {
    const response = await fetch('https://reader.infoquest.bytepluses.com', {
      method: 'POST',
      headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const errorText = await response.text();
      return `Error: fetch API returned status ${response.status}: ${errorText}`;
    }

    const text = await response.text();
    
    if (!text || !text.trim()) {
      return 'Error: no result found';
    }

    // Try to parse as JSON and extract reader_result
    try {
      const jsonData = JSON.parse(text);
      if (jsonData.reader_result) {
        return jsonData.reader_result;
      } else if (jsonData.content) {
        return 'Error: fetch API return wrong format';
      }
    } catch {
      // Not JSON, return as-is
    }

    return text;
  } catch (error) {
    return `Error: fetch API failed: ${error.message}`;
  }
}

// Process single URL
async function main() {
  try {
    const content = await fetchContent(url);
    
    if (content.startsWith('Error:')) {
      console.error(`Error: ${content}`);
      process.exit(1);
    }
    
    console.log(formatContent(content, url));
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();