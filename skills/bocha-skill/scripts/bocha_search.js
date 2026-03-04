#!/usr/bin/env node

/**
 * Bocha AI Search Tool for OpenClaw
 * 
 * Usage:
 *   BOCHA_API_KEY=your_key node bocha_search.js '{"query": "search term", "count": 10}'
 *   echo '{"query": "search term"}' | BOCHA_API_KEY=your_key node bocha_search.js
 */

const https = require('https');
const http = require('http');
const { URL } = require('url');

// API Configuration
const BOCHA_API_ENDPOINT = 'https://api.bocha.cn/v1/web-search';

// Colors for terminal output (optional)
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

/**
 * Make HTTP request
 */
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const client = parsedUrl.protocol === 'https:' ? https : http;
    
    const requestOptions = {
      hostname: parsedUrl.hostname,
      port: parsedUrl.port,
      path: parsedUrl.pathname + parsedUrl.search,
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'OpenClaw-Bocha-Search/1.0',
        ...options.headers
      }
    };

    const req = client.request(requestOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const response = JSON.parse(data);
          resolve({ status: res.statusCode, data: response });
        } catch (e) {
          resolve({ status: res.statusCode, data: data });
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

/**
 * Search using Bocha API
 */
async function searchBocha(query, count = 10, freshness = 'noLimit', summary = true) {
  const apiKey = process.env.BOCHA_API_KEY;
  
  if (!apiKey) {
    throw new Error(
      'BOCHA_API_KEY environment variable is required.\n' +
      'Get your API key from: https://open.bocha.cn/\n' +
      'Then set it with: export BOCHA_API_KEY="your-key-here"'
    );
  }

  // Build request body according to Bocha API specification
  const requestBody = {
    query: query,
    count: Math.min(Math.max(count, 1), 50),
    freshness: freshness,
    summary: summary
  };

  try {
    const response = await makeRequest(BOCHA_API_ENDPOINT, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`
      },
      body: requestBody
    });

    if (response.status >= 200 && response.status < 300) {
      // Check Bocha API response code
      if (response.data.code === 200) {
        return response.data.data;
      } else {
        throw new Error(`API error: ${response.data.msg || 'Unknown error'} (code: ${response.data.code})`);
      }
    } else if (response.status === 401) {
      throw new Error('Invalid API KEY. Please check your BOCHA_API_KEY.');
    } else if (response.status === 403) {
      throw new Error('Insufficient balance. Please recharge at https://open.bocha.cn/');
    } else if (response.status === 429) {
      throw new Error('Rate limit exceeded. Please wait before making more requests.');
    } else {
      throw new Error(`API request failed with status ${response.status}: ${JSON.stringify(response.data)}`);
    }
  } catch (error) {
    if (error.message.includes('BOCHA_API_KEY') || 
        error.message.includes('Invalid API KEY') ||
        error.message.includes('Insufficient balance') ||
        error.message.includes('Rate limit')) {
      throw error;
    }
    throw new Error(`Search failed: ${error.message}`);
  }
}

/**
 * Format results as markdown
 */
function formatResults(data, query) {
  if (!data || !data.webPages || !data.webPages.value || data.webPages.value.length === 0) {
    return `## 🔍 博查搜索结果: "${query}"\n\n未找到相关结果。`;
  }

  let output = `## 🔍 博查搜索结果: "${query}"\n\n`;
  
  if (data.webPages.totalEstimatedMatches) {
    output += `找到约 ${data.webPages.totalEstimatedMatches.toLocaleString()} 条结果（显示前 ${data.webPages.value.length} 条）\n\n`;
  }

  data.webPages.value.forEach((result, index) => {
    const title = result.name || '无标题';
    const url = result.url || result.hostPageUrl || '#';
    const snippet = result.summary || result.snippet || '无描述';
    const source = result.siteName || new URL(url).hostname;
    const date = result.datePublished || result.dateLastCrawled || '';
    
    output += `### ${index + 1}. [${title}](${url})\n`;
    output += `**来源**: ${source}`;
    if (date) {
      // Format date if available
      try {
        const dateObj = new Date(date);
        if (!isNaN(dateObj.getTime())) {
          output += ` | **时间**: ${dateObj.toLocaleDateString('zh-CN')}`;
        }
      } catch (e) {
        output += ` | **时间**: ${date}`;
      }
    }
    output += `\n\n`;
    output += `${snippet}\n\n`;
    output += `---\n\n`;
  });

  // Add images section if available
  if (data.images && data.images.value && data.images.value.length > 0) {
    output += `### 🖼️ 相关图片\n\n`;
    data.images.value.slice(0, 6).forEach((img, index) => {
      if (img.thumbnailUrl || img.contentUrl) {
        output += `[![图片${index + 1}](${img.thumbnailUrl || img.contentUrl})](${img.hostPageUrl || img.contentUrl}) `;
      }
    });
    output += `\n\n`;
  }

  return output;
}

/**
 * Main function
 */
async function main() {
  try {
    // Get input from command line arguments or stdin
    let input = '';
    
    if (process.argv.length > 2) {
      // From command line
      input = process.argv[2];
    } else {
      // From stdin
      const chunks = [];
      for await (const chunk of process.stdin) {
        chunks.push(chunk);
      }
      input = Buffer.concat(chunks).toString('utf-8');
    }

    if (!input.trim()) {
      console.error('Usage: bocha_search \'{\"query\": \"search term\", \"count\": 10}\'');
      process.exit(1);
    }

    // Parse input
    let params;
    try {
      params = JSON.parse(input);
    } catch (e) {
      // If not valid JSON, treat as plain query string
      params = { query: input.trim() };
    }

    const { query, count = 10, freshness = 'noLimit', summary = true } = params;

    if (!query) {
      throw new Error('Query parameter is required');
    }

    // Perform search
    const results = await searchBocha(query, count, freshness, summary);
    
    // Output formatted results
    const formatted = formatResults(results, query);
    console.log(formatted);
    
    // Also output raw JSON for programmatic use
    console.log('\n<!-- RAW_JSON_START -->');
    console.log(JSON.stringify(results, null, 2));
    console.log('<!-- RAW_JSON_END -->');

  } catch (error) {
    console.error(`${colors.red}Error: ${error.message}${colors.reset}`);
    
    if (error.message.includes('BOCHA_API_KEY')) {
      console.error(`\n${colors.yellow}Setup Instructions:${colors.reset}`);
      console.error('1. Visit https://open.bocha.cn/ to get an API key');
      console.error('2. Set the environment variable:');
      console.error('   export BOCHA_API_KEY="your-api-key-here"');
      console.error('3. Or add to ~/.openclaw/openclaw.json:');
      console.error('   {"skills": {"entries": {"bocha-search": {"env": {"BOCHA_API_KEY": "your-key"}}}}}');
    } else if (error.message.includes('Insufficient balance')) {
      console.error(`\n${colors.yellow}Please recharge your account at https://open.bocha.cn/${colors.reset}`);
    }
    
    process.exit(1);
  }
}

// Run main function
main();