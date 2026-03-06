/**
 * Real Tools for Worker Nodes
 * These wrap actual web APIs for search and fetch
 */

const config = require('../config');

/**
 * Web Search - Uses DuckDuckGo HTML (no API key needed)
 */
async function webSearch(query, options = {}) {
  const count = options.count || 5;
  
  try {
    // Use DuckDuckGo HTML search (no API key required)
    const url = `https://html.duckduckgo.com/html/?q=${encodeURIComponent(query)}`;
    
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html',
      },
    });

    if (!response.ok) {
      throw new Error(`Search error: ${response.status}`);
    }

    const html = await response.text();
    
    // Parse results from DuckDuckGo HTML
    const results = [];
    const resultRegex = /<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)<\/a>[\s\S]*?<a[^>]+class="result__snippet"[^>]*>([\s\S]*?)<\/a>/g;
    
    let match;
    while ((match = resultRegex.exec(html)) !== null && results.length < count) {
      const [, url, title, snippet] = match;
      // Decode DuckDuckGo redirect URL
      const actualUrl = decodeURIComponent(url.replace(/.*uddg=/, '').split('&')[0]);
      results.push({
        title: title.trim(),
        url: actualUrl,
        snippet: snippet.replace(/<[^>]+>/g, '').trim(),
      });
    }
    
    // Fallback: simpler parsing if regex didn't match
    if (results.length === 0) {
      const linkRegex = /<a[^>]+class="result__url"[^>]*>([^<]+)<\/a>/g;
      const titleRegex = /<a[^>]+class="result__a"[^>]*>([^<]+)<\/a>/g;
      
      const titles = [...html.matchAll(/<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>([^<]+)<\/a>/g)];
      
      for (let i = 0; i < Math.min(titles.length, count); i++) {
        const [, href, title] = titles[i];
        const actualUrl = decodeURIComponent(href.replace(/.*uddg=/, '').split('&')[0]);
        if (actualUrl.startsWith('http')) {
          results.push({
            title: title.trim(),
            url: actualUrl,
            snippet: '',
          });
        }
      }
    }

    return { success: true, query, results, count: results.length };
  } catch (error) {
    return { success: false, query, error: error.message, results: [] };
  }
}

/**
 * Web Fetch - Extracts readable content from URLs
 */
async function webFetch(url, options = {}) {
  const maxChars = options.maxChars || 15000;
  
  try {
    // Use a readability service or direct fetch
    const response = await fetch(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (compatible; ClawdBot/1.0)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
      redirect: 'follow',
    });

    if (!response.ok) {
      throw new Error(`Fetch error: ${response.status}`);
    }

    const html = await response.text();
    
    // Basic HTML to text extraction
    const text = extractTextFromHtml(html);
    const truncated = text.substring(0, maxChars);
    
    return { 
      success: true, 
      url, 
      content: truncated,
      charCount: truncated.length,
      truncatedFrom: text.length > maxChars ? text.length : null,
    };
  } catch (error) {
    return { success: false, url, error: error.message, content: null };
  }
}

/**
 * Basic HTML text extraction (no external deps)
 */
function extractTextFromHtml(html) {
  // Remove scripts and styles
  let text = html
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<nav[^>]*>[\s\S]*?<\/nav>/gi, '')
    .replace(/<header[^>]*>[\s\S]*?<\/header>/gi, '')
    .replace(/<footer[^>]*>[\s\S]*?<\/footer>/gi, '');
  
  // Convert common elements to text
  text = text
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<\/h[1-6]>/gi, '\n\n')
    .replace(/<li[^>]*>/gi, '• ')
    .replace(/<\/li>/gi, '\n');
  
  // Strip remaining tags
  text = text.replace(/<[^>]+>/g, ' ');
  
  // Clean up whitespace
  text = text
    .replace(/&nbsp;/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, ' ')
    .replace(/\n\s*\n/g, '\n\n')
    .trim();
  
  return text;
}

/**
 * Analyze - LLM-based content analysis (uses node's Gemini)
 */
function createAnalyzeTool(llmClient) {
  return async function analyze(content, instruction = 'Summarize the key points') {
    const prompt = `Analyze the following content. ${instruction}

Content:
${content.substring(0, 10000)}

Provide a structured analysis with key points, insights, and any notable patterns.`;
    
    try {
      const result = await llmClient.complete(prompt);
      return { success: true, analysis: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
}

/**
 * Extract - Structured data extraction
 */
function createExtractTool(llmClient) {
  return async function extract(content, schema = null) {
    const schemaInstructions = schema 
      ? `Extract data matching this schema: ${JSON.stringify(schema)}`
      : 'Extract all key facts, figures, names, dates, and entities';
    
    const prompt = `Extract structured data from the following content.
${schemaInstructions}

Content:
${content.substring(0, 10000)}

Return the extracted data in a clean, structured format (JSON preferred).`;
    
    try {
      const result = await llmClient.complete(prompt);
      return { success: true, extracted: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
}

/**
 * Synthesize - Combine multiple sources
 */
function createSynthesizeTool(llmClient) {
  return async function synthesize(sources, instruction = 'Create a comprehensive summary') {
    const sourcesText = sources.map((s, i) => 
      `--- Source ${i + 1} ---\n${typeof s === 'string' ? s : JSON.stringify(s)}`
    ).join('\n\n');
    
    const prompt = `Synthesize the following sources into a coherent report.
${instruction}

${sourcesText}

Create a well-organized report that:
1. Identifies common themes and patterns
2. Notes any contradictions or unique points
3. Provides actionable insights
4. Is well-structured and easy to read`;
    
    try {
      const result = await llmClient.complete(prompt);
      return { success: true, synthesis: result };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };
}

module.exports = {
  webSearch,
  webFetch,
  createAnalyzeTool,
  createExtractTool,
  createSynthesizeTool,
};
