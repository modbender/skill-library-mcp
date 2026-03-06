// lib/jsonl-parser.js – Robust OpenClaw JSONL parser
// Handles multiple formats:
//   Format A (actual OpenClaw): {type: "message", message: {role: "user", content: [...]}}
//   Format B (simple/legacy):   {role: "user", content: "..."}
//   Format C (timestamped):     {type: "message", timestamp: ..., message: {role, content}}
// Also handles session metadata lines: {type: "session", ...}, {type: "tool_use", ...} etc.

/**
 * Parse a single JSONL line and extract role + text content.
 * Returns {role, content} or null if not a user/assistant message.
 */
function parseLine(line) {
  if (!line || !line.trim()) return null;

  let parsed;
  try {
    parsed = JSON.parse(line);
  } catch {
    return null;
  }

  // Extract the actual message object (could be nested or flat)
  const msg = parsed.message || parsed;

  // Only care about user and assistant messages
  const role = msg.role;
  if (role !== 'user' && role !== 'assistant') return null;

  // Extract text content (handles string, array of objects, array of strings)
  const content = extractText(msg.content);
  if (!content || content.length < 10) return null;

  return { role, content };
}

/**
 * Extract text from various content formats:
 *   - String: "hello"
 *   - Array of objects: [{type: "text", text: "hello"}, {type: "image", ...}]
 *   - Array of strings: ["hello", "world"]
 *   - Object with text: {type: "text", text: "hello"}
 */
function extractText(content) {
  if (!content) return '';

  if (typeof content === 'string') return content.trim();

  if (Array.isArray(content)) {
    return content
      .map(item => {
        if (typeof item === 'string') return item;
        if (typeof item === 'object' && item) {
          // Skip non-text content (images, tool_use, tool_result etc.)
          if (item.type && item.type !== 'text') return '';
          return item.text || item.content || '';
        }
        return '';
      })
      .filter(t => t.length > 0)
      .join(' ')
      .trim();
  }

  if (typeof content === 'object') {
    return content.text || content.content || '';
  }

  return String(content);
}

/**
 * Parse entire JSONL content (string with newlines) into formatted messages.
 * Returns array of "[role]: content" strings.
 */
function parseJSONL(rawContent) {
  const lines = rawContent.split('\n').filter(l => l.trim());
  const messages = [];

  for (const line of lines) {
    const result = parseLine(line);
    if (result) {
      messages.push(`[${result.role}]: ${result.content}`);
    }
  }

  return messages;
}

module.exports = { parseLine, extractText, parseJSONL };
