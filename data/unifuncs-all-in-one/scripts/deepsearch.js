#!/usr/bin/env node
/**
 * UniFuncs Deep Research
 * Conduct comprehensive research on topics
 */

const API_KEY = process.env.UNIFUNCS_API_KEY;
const API_BASE = 'https://api.unifuncs.com';

if (!API_KEY) {
  console.error('Error: UNIFUNCS_API_KEY environment variable is not set');
  console.error('Please set it with: export UNIFUNCS_API_KEY=sk-xxxxxx');
  process.exit(1);
}

async function deepSearch(query, options = {}) {
  const payload = {
    model: options.model || 's2',
    messages: [
      {
        role: 'user',
        content: query
      }
    ],
    stream: false
  };

  try {
    const response = await fetch(`${API_BASE}/deepsearch/v1/chat/completions`, {
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
      data: data.choices?.[0]?.message?.content || data,
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
Usage: node deepsearch.js "<research question>" [options]

Options:
  --model <model>    Model to use: s2 (default), s1

Example:
  node deepsearch.js "What are the latest developments in AI agents?"
`);
    process.exit(0);
  }

  const query = args[0];
  const options = {
    model: 's2'
  };

  for (let i = 1; i < args.length; i++) {
    switch (args[i]) {
      case '--model':
        options.model = args[++i];
        break;
    }
  }

  const result = await deepSearch(query, options);
  console.log(JSON.stringify(result, null, 2));
}

export { deepSearch };
