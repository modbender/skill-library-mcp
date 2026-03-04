const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Parse arguments manually
const args = process.argv.slice(2);
const params = {};
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    const key = args[i].substring(2);
    const value = args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : true;
    params[key] = value;
  }
}

const { query, sources, max_results } = params;
let sourceList = ['tavily', 'web-search-plus', 'local']; // Default
if (sources) {
  try {
    sourceList = JSON.parse(sources);
  } catch (e) {
    console.error('Invalid JSON for sources, using defaults');
  }
}
const maxResults = parseInt(max_results) || 5;

// SECURITY: Sanitize search query to prevent command injection
function sanitizeQuery(q) {
  if (!q || typeof q !== 'string') throw new Error('Query is required');
  const trimmed = q.trim();
  if (trimmed.length === 0) throw new Error('Query cannot be empty');
  if (trimmed.length > 500) throw new Error('Query too long (max 500 characters)');
  // Block shell metacharacters
  const dangerousChars = /[;&|`$(){}[\]<>\\!#*?~]/g;
  if (dangerousChars.test(trimmed)) {
    throw new Error('Query contains disallowed characters');
  }
  return trimmed;
}

// Call external skill/tool via OpenClaw's callSkill mechanism
// In production, this would be replaced with actual API calls
async function callSkill(skillName, action, params) {
  const sanitizedQuery = sanitizeQuery(params.q);
  
  if (skillName === 'tavily-search' && action === 'search') {
    // Call tavily-search script directly
    const scriptPath = path.join(__dirname, '../tavily-search/scripts/search.mjs');
    const apiKey = process.env.TAVILY_API_KEY || '';
    
    if (!apiKey) {
      throw new Error('TAVILY_API_KEY not set');
    }
    
    try {
      // Build command with proper escaping
      const cmd = `node "${scriptPath}" "${sanitizedQuery}" -n ${params.limit || 5}`;
      const output = execSync(cmd, {
        env: { ...process.env, TAVILY_API_KEY: apiKey },
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'pipe']
      });
      
      // Parse the markdown output to extract results
      const results = [];
      const lines = output.split('\n');
      let currentResult = null;
      
      for (const line of lines) {
        if (line.startsWith('- **')) {
          if (currentResult) results.push(currentResult);
          const titleMatch = line.match(/\*\*(.+?)\*\*/);
          const urlMatch = line.match(/\((relevance: .+?)\)/);
          currentResult = {
            title: titleMatch ? titleMatch[1] : 'Unknown',
            score: urlMatch ? parseFloat(urlMatch[1]) / 100 : 0.5,
            url: '',
            content: ''
          };
        } else if (line.trim().startsWith('http') && currentResult) {
          currentResult.url = line.trim();
        } else if (line.trim() && !line.startsWith('#') && !line.startsWith('---') && currentResult) {
          currentResult.content = (currentResult.content + ' ' + line.trim()).trim();
        }
      }
      if (currentResult) results.push(currentResult);
      
      return { items: results.slice(0, params.limit || 5) };
    } catch (e) {
      console.warn('Tavily search error:', e.message);
      return { items: [] };
    }
  }
  
  if (skillName === 'web-search-plus' && action === 'search') {
    // Placeholder for web-search-plus integration
    // In production, this would call the actual API
    console.warn('web-search-plus not configured');
    return { items: [] };
  }
  
  return { items: [] };
}

// Simple local file search with proper sanitization
function searchLocalFiles(query, maxResults) {
  const sanitizedQuery = sanitizeQuery(query);
  const results = [];
  const workspaceDir = process.env.HOME ? path.join(process.env.HOME, '.openclaw', 'workspace') : './';
  
  try {
    // SECURITY: Only search in allowed directories
    const allowedDirs = ['memory', 'skills', '.'];
    
    for (const dir of allowedDirs) {
      const searchPath = path.join(workspaceDir, dir);
      if (!fs.existsSync(searchPath)) continue;
      
      const files = fs.readdirSync(searchPath, { withFileTypes: true });
      for (const file of files) {
        if (file.isFile() && file.name.toLowerCase().includes(sanitizedQuery.toLowerCase())) {
          const fullPath = path.join(searchPath, file.name);
          // SECURITY: Verify the path is still within workspace
          const resolvedPath = path.resolve(fullPath);
          if (!resolvedPath.startsWith(path.resolve(workspaceDir))) {
            continue; // Path traversal attempt, skip
          }
          
          results.push({
            path: fullPath,
            snippet: `Found query "${sanitizedQuery}" in filename: ${file.name}`,
            score: 0.5
          });
        }
      }
    }
  } catch (e) {
    console.warn('Could not search local files:', e.message);
  }
  return results.slice(0, maxResults);
}

async function doTool() {
  if (!query) {
    console.error('Error: --query is required');
    process.exit(1);
  }

  // SECURITY: Validate query before processing
  let safeQuery;
  try {
    safeQuery = sanitizeQuery(query);
  } catch (e) {
    console.error('Invalid query:', e.message);
    process.exit(1);
  }

  const results = [];

  if (sourceList.includes('tavily')) {
    try {
      const r = await callSkill('tavily-search', 'search', { q: safeQuery, limit: maxResults });
      results.push(...r.items.map(i => ({ 
        source: 'tavily', 
        title: i.title, 
        url: i.url, 
        score: i.score || 0.5,
        content: i.content 
      })));
    } catch (e) {
      console.warn('Tavily search failed:', e.message);
    }
  }

  if (sourceList.includes('web-search-plus')) {
    try {
      const r = await callSkill('web-search-plus', 'search', { q: safeQuery, limit: maxResults });
      results.push(...r.items.map(i => ({ 
        source: 'web-search-plus', 
        title: i.title, 
        url: i.url, 
        score: i.score || 0.5 
      })));
    } catch (e) {
      console.warn('Web Search Plus failed:', e.message);
    }
  }

  if (sourceList.includes('local')) {
    const local = searchLocalFiles(safeQuery, maxResults);
    results.push(...local.map(l => ({ 
      source: 'local', 
      title: l.path, 
      snippet: l.snippet, 
      score: l.score 
    })));
  }

  // Sort by score and return top N
  results.sort((a, b) => (b.score || 0) - (a.score || 0));
  const topResults = results.slice(0, maxResults);

  console.log(JSON.stringify(topResults, null, 2));
}

doTool();
