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
  let trimmed = q.trim();
  if (trimmed.length === 0) throw new Error('Query cannot be empty');
  if (trimmed.length > 500) throw new Error('Query too long (max 500 characters)');
  
  // SECURITY: Remove quotes (single/double) to prevent shell argument breakout
  trimmed = trimmed.replace(/['"]/g, '');
  
  // Block shell metacharacters
  const dangerousChars = /[;&|`$(){}[\]<>\!#*?~]/g;
  if (dangerousChars.test(trimmed)) {
    throw new Error('Query contains disallowed characters');
  }
  return trimmed;
}

async function callSkill(skillName, action, params) {
  const sanitizedQuery = sanitizeQuery(params.q);
  
  if (skillName === 'tavily-search' && action === 'search') {
    const scriptPath = path.join(__dirname, '../tavily-search/scripts/search.mjs');
    const apiKey = process.env.TAVILY_API_KEY || '';
    
    if (!apiKey) throw new Error('TAVILY_API_KEY not set');
    
    try {
      // safeQuery has quotes stripped, so wrapping in "" is safe
      const cmd = `node "${scriptPath}" "${sanitizedQuery}" -n ${params.limit || 5}`;
      const output = execSync(cmd, {
        env: { ...process.env, TAVILY_API_KEY: apiKey },
        encoding: 'utf8',
        stdio: ['ignore', 'pipe', 'pipe'] // Ignore stdin
      });
      
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
      console.warn('Tavily search failed:', e.message);
      return { items: [] };
    }
  }
  return { items: [] };
}

function searchLocalFiles(query, maxResults) {
  const sanitizedQuery = sanitizeQuery(query);
  const results = [];
  
  // SECURITY: Enforce strict workspace root
  const workspaceRoot = process.env.HOME ? path.resolve(process.env.HOME, '.openclaw', 'workspace') : path.resolve(process.cwd());
  
  try {
    const allowedSubdirs = ['memory', 'skills']; // Do not include '.' to prevent scanning root if it has sensitive files
    
    for (const subdir of allowedSubdirs) {
      const searchPath = path.join(workspaceRoot, subdir);
      if (!fs.existsSync(searchPath)) continue;
      
      // Additional safety check: ensure searchPath is actually inside workspaceRoot
      if (!path.resolve(searchPath).startsWith(workspaceRoot)) continue;

      const files = fs.readdirSync(searchPath, { withFileTypes: true });
      for (const file of files) {
        if (file.isFile() && file.name.toLowerCase().includes(sanitizedQuery.toLowerCase())) {
          const fullPath = path.join(searchPath, file.name);
          results.push({
            path: fullPath,
            snippet: `Found query "${sanitizedQuery}" in filename: ${file.name}`,
            score: 0.5
          });
        }
      }
    }
  } catch (e) {
    console.warn('Local search error:', e.message);
  }
  return results.slice(0, maxResults);
}

async function doTool() {
  if (!query) {
    console.error('Error: --query is required');
    process.exit(1);
  }

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
    } catch (e) {}
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

  results.sort((a, b) => (b.score || 0) - (a.score || 0));
  console.log(JSON.stringify(results.slice(0, maxResults), null, 2));
}

doTool();
