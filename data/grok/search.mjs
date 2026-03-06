// search.mjs
// xAI Grok Search - Web and X search functions

/**
 * Search the web using xAI's Grok API
 * @param {Object} options - Search options
 * @param {string} options.query - Search query (required)
 * @param {string} options.model - Model to use (default: grok-4-1-fast-reasoning)
 * @param {string[]} options.allowed_domains - Restrict to these domains (max 5)
 * @param {string[]} options.excluded_domains - Exclude these domains (max 5)
 * @param {boolean} options.enable_image_understanding - Enable image analysis
 * @returns {Promise<Object>} Search results with content and citations
 */
export async function search_web(options) {
  const {
    query,
    model = 'grok-4-1-fast-reasoning',
    allowed_domains = null,
    excluded_domains = null,
    enable_image_understanding = false
  } = options;

  // Validate API key
  if (!process.env.XAI_API_KEY) {
    throw new Error('XAI_API_KEY environment variable is required');
  }

  // Validate domain filters
  if (allowed_domains && allowed_domains.length > 5) {
    throw new Error('Maximum 5 allowed_domains');
  }
  if (excluded_domains && excluded_domains.length > 5) {
    throw new Error('Maximum 5 excluded_domains');
  }
  if (allowed_domains && excluded_domains) {
    throw new Error('Cannot use both allowed_domains and excluded_domains');
  }

  // Build tool - exactly like the official curl example
  const tool = { type: 'web_search' };
  
  // Add optional parameters
  if (allowed_domains) tool.allowed_domains = allowed_domains;
  if (excluded_domains) tool.excluded_domains = excluded_domains;
  if (enable_image_understanding) tool.enable_image_understanding = true;

  // Make API request
  const response = await fetch('https://api.x.ai/v1/responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.XAI_API_KEY}`
    },
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool]
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const output = data.output || [];
  const lastMessage = output[output.length - 1] || {};

  return {
    content: lastMessage.content || '',
    citations: data.citations || [],
    usage: data.usage || {},
    server_side_tool_usage: data.server_side_tool_usage || {},
    raw_response: data
  };
}

/**
 * Search X (Twitter) using xAI's Grok API
 * @param {Object} options - Search options
 * @param {string} options.query - Search query (required)
 * @param {string} options.model - Model to use (default: grok-4-1-fast-reasoning)
 * @param {string[]} options.allowed_x_handles - Only search these handles (max 10, no @)
 * @param {string[]} options.excluded_x_handles - Exclude these handles (max 10, no @)
 * @param {string} options.from_date - Start date in ISO8601 format (YYYY-MM-DD)
 * @param {string} options.to_date - End date in ISO8601 format (YYYY-MM-DD)
 * @param {boolean} options.enable_image_understanding - Enable image analysis
 * @param {boolean} options.enable_video_understanding - Enable video analysis
 * @returns {Promise<Object>} Search results with content and citations
 */
export async function search_x(options) {
  const {
    query,
    model = 'grok-4-1-fast-reasoning',
    allowed_x_handles = null,
    excluded_x_handles = null,
    from_date = null,
    to_date = null,
    enable_image_understanding = false,
    enable_video_understanding = false
  } = options;

  // Validate API key
  if (!process.env.XAI_API_KEY) {
    throw new Error('XAI_API_KEY environment variable is required');
  }

  // Validate handle filters
  if (allowed_x_handles && allowed_x_handles.length > 10) {
    throw new Error('Maximum 10 allowed_x_handles');
  }
  if (excluded_x_handles && excluded_x_handles.length > 10) {
    throw new Error('Maximum 10 excluded_x_handles');
  }
  if (allowed_x_handles && excluded_x_handles) {
    throw new Error('Cannot use both allowed_x_handles and excluded_x_handles');
  }

  // Build tool - exactly like the official curl example
  const tool = { type: 'x_search' };
  
  // Add optional parameters
  if (allowed_x_handles) tool.allowed_x_handles = allowed_x_handles;
  if (excluded_x_handles) tool.excluded_x_handles = excluded_x_handles;
  if (from_date) tool.from_date = from_date;
  if (to_date) tool.to_date = to_date;
  if (enable_image_understanding) tool.enable_image_understanding = true;
  if (enable_video_understanding) tool.enable_video_understanding = true;

  // Make API request
  const response = await fetch('https://api.x.ai/v1/responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${process.env.XAI_API_KEY}`
    },
    body: JSON.stringify({
      model,
      input: [{ role: 'user', content: query }],
      tools: [tool]
    })
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(`API Error: ${error.error?.message || response.statusText}`);
  }

  const data = await response.json();
  const output = data.output || [];
  const lastMessage = output[output.length - 1] || {};

  return {
    content: lastMessage.content || '',
    citations: data.citations || [],
    usage: data.usage || {},
    server_side_tool_usage: data.server_side_tool_usage || {},
    raw_response: data
  };
}

// CLI usage
if (import.meta.url === `file://${process.argv[1]}`) {
  const command = process.argv[2];
  const query = process.argv[3];
  
  if (!command || !query || !['web', 'x'].includes(command)) {
    console.error('Usage:');
    console.error('  node search.mjs web "your search query"');
    console.error('  node search.mjs x "what people are saying"');
    process.exit(1);
  }

  try {
    let result;
    
    if (command === 'web') {
      result = await search_web({ query });
      console.log('\n🌐 Web Search Results:\n');
    } else {
      result = await search_x({ query });
      console.log('\n𝕏 X Search Results:\n');
    }
    
    console.log(result.content);
    
    if (result.citations && result.citations.length > 0) {
      console.log('\n' + '─'.repeat(60));
      console.log('Sources:');
      console.log('─'.repeat(60));
      result.citations.forEach((cite, i) => {
        console.log(`${i + 1}. ${cite.title || 'Untitled'}`);
        console.log(`   ${cite.url || ''}`);
        if (cite.snippet) {
          console.log(`   ${cite.snippet.substring(0, 100)}...`);
        }
        console.log();
      });
    }
  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}
