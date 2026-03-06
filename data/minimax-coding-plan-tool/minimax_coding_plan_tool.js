#!/usr/bin/env node

/**
 * MiniMax Coding Plan Tool - Network Search & Image Understanding
 *
 * Provides two tools:
 * - minimax_web_search: Web search using MiniMax Coding Plan API
 * - minimax_understand_image: Image understanding using MiniMax VLM API
 *
 * ⚠️ IMPORTANT: This tool requires a special Coding Plan API Key.
 * Regular MiniMax API keys will NOT work.
 */

const https = require('https');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

// Get API key and host from environment
const API_KEY = process.env.MINIMAX_API_KEY;
const API_HOST = 'api.minimax.chat';

if (!API_KEY) {
  console.error('⚠️ Note: You need a Coding Plan API Key, not a regular MiniMax API key');
  process.exit(1);
}

/**
 * Make request to MiniMax API
 */
function makeRequest(endpoint, data) {
  return new Promise((resolve, reject) => {
    const url = new URL(endpoint, `https://${API_HOST}`);

    const options = {
      hostname: API_HOST,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`
      }
    };

    const req = https.request(options, (res) => {
      let body = '';
      res.on('data', chunk => body += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(body);
          resolve(json);
        } catch (e) {
          reject(new Error(`Failed to parse response: ${body}`));
        }
      });
    });

    req.on('error', reject);
    req.write(JSON.stringify(data));
    req.end();
  });
}

/**
 * Process image URL - convert local file to base64 if needed
 */
function processImageUrl(imageSource) {
  // If it's an HTTP URL, pass through
  if (imageSource.startsWith('http://') || imageSource.startsWith('https://')) {
    return imageSource;
  }

  // It's a local file - convert to base64
  // Strip @ prefix if present
  let filePath = imageSource.startsWith('@') ? imageSource.slice(1) : imageSource;

  if (!fs.existsSync(filePath)) {
    throw new Error(`File not found: ${filePath}`);
  }

  const ext = path.extname(filePath).toLowerCase();
  const mimeTypes = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.webp': 'image/webp'
  };
  const mimeType = mimeTypes[ext] || 'image/jpeg';
  const fileContent = fs.readFileSync(filePath);
  const base64 = fileContent.toString('base64');

  return `data:${mimeType};base64,${base64}`;
}

/**
 * Web Search Tool using Coding Plan API
 *
 * Uses MiniMax's coding plan search endpoint for real-time web search
 */
async function webSearch(query) {
  if (!query || typeof query !== 'string') {
    return { error: 'Missing required parameter: query' };
  }

  try {
    // Use MiniMax Coding Plan search API
    const response = await makeRequest('/v1/coding_plan/search', {
      q: query
    });

    // Parse response
    if (response.organic) {
      return {
        success: true,
        query: query,
        results: response.organic.map(item => ({
          title: item.title || '',
          link: item.link || item.url || '',
          snippet: item.snippet || item.content || '',
          date: item.date || ''
        })),
        related_searches: response.related_searches || []
      };
    }

    return { success: true, response };
  } catch (error) {
    return { error: error.message };
  }
}

/**
 * Understand Image Tool using Coding Plan VLM API
 *
 * Uses MiniMax's vision model to analyze images
 */
async function understandImage(imageSource, prompt) {
  if (!prompt || typeof prompt !== 'string') {
    return { error: 'Missing required parameter: prompt' };
  }

  if (!imageSource || typeof imageSource !== 'string') {
    return { error: 'Missing required parameter: image_source' };
  }

  try {
    // Process image: convert HTTP URL or local file to base64
    const processedImageUrl = processImageUrl(imageSource);

    // Use MiniMax Coding Plan VLM API
    const response = await makeRequest('/v1/coding_plan/vlm', {
      prompt: prompt,
      image_url: processedImageUrl
    });

    // Extract content from response
    const content = response.content;

    if (!content) {
      return { error: 'No content returned from VLM API' };
    }

    return {
      success: true,
      prompt: prompt,
      image_source: imageSource,
      analysis: content
    };
  } catch (error) {
    return { error: error.message };
  }
}

// CLI interface
const args = process.argv.slice(2);
const command = args[0];

async function main() {
  if (command === 'web_search') {
    const query = args[1];
    const result = await webSearch(query);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'understand_image') {
    const imageSource = args[1];
    const prompt = args.slice(2).join(' ') || 'Describe this image';
    const result = await understandImage(imageSource, prompt);
    console.log(JSON.stringify(result, null, 2));
  } else if (command === 'tools') {
    // Return available tools in OpenClaw skill format
    console.log(JSON.stringify({
      tools: [
        {
          name: 'minimax_web_search',
          description: 'Web search using MiniMax Coding Plan API - search real-time or external information',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Search query. 3-5 keywords work best'
              }
            },
            required: ['query']
          }
        },
        {
          name: 'minimax_understand_image',
          description: 'Image understanding using MiniMax Coding Plan VLM API',
          inputSchema: {
            type: 'object',
            properties: {
              image_source: {
                type: 'string',
                description: 'Image source - supports HTTP/HTTPS URL or local file path (strip @ prefix)'
              },
              prompt: {
                type: 'string',
                description: 'Question or analysis request for the image'
              }
            },
            required: ['image_source', 'prompt']
          }
        }
      ]
    }, null, 2));
  } else {
    console.error('Usage:');
    console.error('  minimax-coding-plan-mcp web_search <query>');
    console.error('  minimax-coding-plan-mcp understand_image <image_source> <prompt>');
    console.error('  minimax-coding-plan-mcp tools');
    process.exit(1);
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});