/**
 * File Metadata Extraction
 * Extracts searchable metadata from markdown documentation files
 */

/**
 * Extract title (first H1)
 */
function extractTitle(lines) {
  for (const line of lines) {
    const match = line.match(/^#\s+(.+)$/);
    if (match) return match[1].trim();
  }
  return null;
}

/**
 * Extract all headers (H2, H3)
 */
function extractHeaders(lines) {
  const headers = [];
  for (const line of lines) {
    const match = line.match(/^#{2,3}\s+(.+)$/);
    if (match) {
      headers.push(match[1].trim());
    }
  }
  return headers;
}

/**
 * Extract first meaningful paragraph as summary
 */
function extractSummary(lines) {
  let inParagraph = false;
  let paragraph = [];
  
  for (const line of lines) {
    // Skip frontmatter
    if (line === '---') continue;
    // Skip headers
    if (line.startsWith('#')) {
      if (paragraph.length > 0) break;
      continue;
    }
    // Skip empty lines before paragraph
    if (!line.trim() && !inParagraph) continue;
    // End of paragraph
    if (!line.trim() && inParagraph) break;
    // Skip code blocks
    if (line.startsWith('```')) continue;
    
    inParagraph = true;
    paragraph.push(line.trim());
  }
  
  return paragraph.join(' ').slice(0, 300);
}

/**
 * Extract keywords from content
 * - Config keys (camelCase in backticks or YAML)
 * - camelCase words anywhere in text
 * - YAML keys
 * - Error codes (ALLCAPS)
 * - Code terms in backticks
 */
function extractKeywords(content) {
  const keywords = new Set();
  
  // Backtick content (config keys, commands, etc.)
  const backtickMatches = content.match(/`([^`]+)`/g) || [];
  for (const match of backtickMatches) {
    const term = match.replace(/`/g, '').trim();
    // Skip long code snippets, keep short terms
    if (term.length > 0 && term.length < 40 && !term.includes('\n')) {
      // Split on common delimiters
      const parts = term.split(/[.\s/=:]+/);
      for (const part of parts) {
        if (part.length > 1 && part.length < 30) {
          keywords.add(part.toLowerCase());
        }
      }
    }
  }
  
  // camelCase words (config keys like requireMention, allowGroups)
  const camelMatches = content.match(/\b[a-z][a-z0-9]*[A-Z][a-zA-Z0-9]*\b/g) || [];
  for (const match of camelMatches) {
    keywords.add(match.toLowerCase());
  }
  
  // YAML-style keys at start of line
  const yamlMatches = content.match(/^\s{0,4}([a-zA-Z][a-zA-Z0-9_]+):/gm) || [];
  for (const match of yamlMatches) {
    const key = match.replace(':', '').trim();
    if (key.length > 1) {
      keywords.add(key.toLowerCase());
    }
  }
  
  // Error codes (ALLCAPS with underscores)
  const errorMatches = content.match(/\b[A-Z][A-Z0-9_]{2,}\b/g) || [];
  for (const match of errorMatches) {
    // Skip common non-error terms
    if (!['README', 'TODO', 'NOTE', 'API', 'URL', 'HTTP', 'JSON', 'YAML'].includes(match)) {
      keywords.add(match.toLowerCase());
    }
  }
  
  return [...keywords];
}

/**
 * Extract full metadata from a file
 */
function extractFileMetadata(content, filePath) {
  const lines = content.split('\n');
  
  const title = extractTitle(lines);
  const headers = extractHeaders(lines);
  const keywords = extractKeywords(content);
  const summary = extractSummary(lines);
  
  // Build searchable text blob for FTS
  const searchText = [
    title || '',
    headers.join(' '),
    keywords.join(' '),
    summary
  ].join(' ').toLowerCase();
  
  // Build embedding text (more context for vectors)
  const embeddingText = [
    title || '',
    headers.join('. '),
    summary,
    keywords.slice(0, 20).join(', ')
  ].join('\n');
  
  return {
    path: filePath,
    title,
    headers,
    keywords,
    summary,
    searchText,
    embeddingText
  };
}

module.exports = {
  extractTitle,
  extractHeaders,
  extractSummary,
  extractKeywords,
  extractFileMetadata
};
