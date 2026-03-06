#!/usr/bin/env node
/**
 * Memory Access Tracker
 * 
 * Scans session transcripts for memory file reads (read tool, memory_search, memory_get)
 * and logs which files/sections were accessed, when, and how often.
 * 
 * Usage: node track.js [--since <hours>] [--sessions-dir <path>]
 */

const fs = require('fs');
const path = require('path');
const readline = require('readline');

const DEFAULT_SESSIONS_DIR = path.join(process.env.HOME, '.openclaw/agents/main/sessions');
const STATE_DIR = path.join(__dirname, '..', 'state');
const ACCESS_LOG = path.join(STATE_DIR, 'access-log.json');

// Memory file patterns we care about
const MEMORY_FILES = [
  'MEMORY.md',
  'memory/tier2-recent.md',
  'memory/tier3-archive.md',
];
const MEMORY_FILE_PATTERN = /(?:MEMORY\.md|memory\/tier[23]-\w+\.md|memory\/\d{4}-\d{2}-\d{2}\.md)/;
const DAILY_LOG_PATTERN = /memory\/(\d{4}-\d{2}-\d{2})\.md/;

function loadAccessLog() {
  try {
    return JSON.parse(fs.readFileSync(ACCESS_LOG, 'utf8'));
  } catch {
    return {
      lastScanTime: null,
      lastScanSession: null,
      sections: {},
      files: {},
    };
  }
}

function saveAccessLog(log) {
  fs.mkdirSync(STATE_DIR, { recursive: true });
  fs.writeFileSync(ACCESS_LOG, JSON.stringify(log, null, 2));
}

/**
 * Parse a JSONL session transcript for memory access patterns
 */
async function parseTranscript(filePath) {
  const accesses = [];
  
  const stream = fs.createReadStream(filePath);
  const rl = readline.createInterface({ input: stream, crlfDelay: Infinity });
  
  for await (const line of rl) {
    if (!line.trim()) continue;
    
    let entry;
    try {
      entry = JSON.parse(line);
    } catch {
      continue;
    }
    
    const timestamp = entry.timestamp || entry.ts || null;
    const message = entry.message || entry;
    const role = message.role || entry.role || '';
    const contentArr = Array.isArray(message.content) ? message.content : [];
    
    // Check for tool calls — OpenClaw format: message.content[].type === "toolCall"
    const toolCalls = contentArr.filter(c => c.type === 'toolCall');
    // Also support standard OpenAI format
    if (message.tool_calls) {
      for (const tc of message.tool_calls) {
        toolCalls.push({
          name: tc.function?.name || tc.name,
          arguments: tc.function?.arguments || tc.arguments,
        });
      }
    }
    
    if (role === 'assistant' && toolCalls.length > 0) {
      for (const call of toolCalls) {
        const fn = call.name || '';
        const args = call.arguments || '';
        let parsedArgs;
        try {
          parsedArgs = typeof args === 'string' ? JSON.parse(args) : args;
        } catch {
          parsedArgs = {};
        }
        
        // read tool on memory files
        if (fn === 'read') {
          const filePath = parsedArgs.file_path || parsedArgs.path || '';
          const match = filePath.match(MEMORY_FILE_PATTERN);
          if (match) {
            accesses.push({
              type: 'read',
              file: match[0],
              timestamp,
              offset: parsedArgs.offset || null,
              limit: parsedArgs.limit || null,
            });
          }
        }
        
        // memory_search
        if (fn === 'memory_search') {
          accesses.push({
            type: 'search',
            query: parsedArgs.query || '',
            timestamp,
          });
        }
        
        // memory_get
        if (fn === 'memory_get') {
          const memPath = parsedArgs.path || '';
          accesses.push({
            type: 'get',
            file: memPath,
            from: parsedArgs.from || null,
            lines: parsedArgs.lines || null,
            timestamp,
          });
        }
        
        // edit/write to memory files
        if (fn === 'edit' || fn === 'write') {
          const filePath = parsedArgs.file_path || parsedArgs.path || '';
          const match = filePath.match(MEMORY_FILE_PATTERN);
          if (match) {
            accesses.push({
              type: 'write',
              file: match[0],
              timestamp,
            });
          }
        }
      }
    }
    
    // Also check tool results that contain memory file content
    if ((role === 'tool' || role === 'toolResult') && (message.content || entry.content)) {
      const rawContent = message.content || entry.content;
      const content = typeof rawContent === 'string' ? rawContent : JSON.stringify(rawContent);
      // Check if search results reference memory files
      const matches = content.match(/(?:MEMORY\.md|tier[23]-\w+\.md|\d{4}-\d{2}-\d{2}\.md)/g);
      if (matches) {
        for (const m of [...new Set(matches)]) {
          accesses.push({
            type: 'search_result',
            file: m.includes('/') ? m : `memory/${m}`,
            timestamp,
          });
        }
      }
    }
  }
  
  return accesses;
}

/**
 * Extract section headers from memory file content
 */
function extractSections(content) {
  const sections = [];
  const lines = content.split('\n');
  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^#{1,3}\s+(.+)/);
    if (match) {
      sections.push({
        title: match[1].trim(),
        line: i + 1,
      });
    }
  }
  return sections;
}

/**
 * Map a line number to a section in a memory file
 */
function lineToSection(filePath, lineNum) {
  try {
    const fullPath = filePath.startsWith('/') ? filePath : 
      path.join(process.env.HOME, '.openclaw/workspace', filePath);
    const content = fs.readFileSync(fullPath, 'utf8');
    const sections = extractSections(content);
    
    let currentSection = '(top)';
    for (const sec of sections) {
      if (sec.line <= lineNum) {
        currentSection = sec.title;
      } else {
        break;
      }
    }
    return currentSection;
  } catch {
    return null;
  }
}

async function main() {
  const args = process.argv.slice(2);
  let sinceHours = 24;
  let sessionsDir = DEFAULT_SESSIONS_DIR;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--since') sinceHours = parseInt(args[++i]) || 24;
    if (args[i] === '--sessions-dir') sessionsDir = args[++i];
  }
  
  const log = loadAccessLog();
  const since = Date.now() - (sinceHours * 60 * 60 * 1000);
  const sinceDate = new Date(since);
  
  console.error(`Scanning sessions since ${sinceDate.toISOString()} (${sinceHours}h ago)`);
  
  // Find session files
  const files = fs.readdirSync(sessionsDir)
    .filter(f => f.endsWith('.jsonl'))
    .map(f => ({
      name: f,
      path: path.join(sessionsDir, f),
      mtime: fs.statSync(path.join(sessionsDir, f)).mtimeMs,
    }))
    .filter(f => f.mtime > since)
    .sort((a, b) => a.mtime - b.mtime);
  
  console.error(`Found ${files.length} session files to scan`);
  
  let totalAccesses = 0;
  
  for (const file of files) {
    const accesses = await parseTranscript(file.path);
    
    for (const access of accesses) {
      totalAccesses++;
      const now = access.timestamp || new Date(file.mtime).toISOString();
      
      if (access.file) {
        // Normalize file path
        const normFile = access.file.replace(/^.*workspace\//, '');
        
        // Update file-level tracking
        if (!log.files[normFile]) {
          log.files[normFile] = {
            firstAccessed: now,
            lastAccessed: now,
            accessCount: 0,
            readCount: 0,
            writeCount: 0,
            searchHitCount: 0,
          };
        }
        const fileLog = log.files[normFile];
        fileLog.lastAccessed = now;
        fileLog.accessCount++;
        if (access.type === 'read' || access.type === 'get') fileLog.readCount++;
        if (access.type === 'write') fileLog.writeCount++;
        if (access.type === 'search_result') fileLog.searchHitCount++;
        
        // Track section-level access if we have line info
        if (access.from || access.offset) {
          const line = access.from || access.offset;
          const section = lineToSection(normFile, line);
          if (section) {
            const sectionKey = `${normFile}#${section}`;
            if (!log.sections[sectionKey]) {
              log.sections[sectionKey] = {
                file: normFile,
                section,
                firstAccessed: now,
                lastAccessed: now,
                accessCount: 0,
              };
            }
            log.sections[sectionKey].lastAccessed = now;
            log.sections[sectionKey].accessCount++;
          }
        }
      }
      
      // Track search queries
      if (access.type === 'search' && access.query) {
        if (!log.searches) log.searches = [];
        log.searches.push({
          query: access.query,
          timestamp: now,
        });
        // Keep only last 100 searches
        if (log.searches.length > 100) {
          log.searches = log.searches.slice(-100);
        }
      }
    }
  }
  
  log.lastScanTime = new Date().toISOString();
  log.lastScanSession = files.length > 0 ? files[files.length - 1].name : null;
  
  saveAccessLog(log);
  
  console.log(JSON.stringify({
    scanned: files.length,
    accesses: totalAccesses,
    trackedFiles: Object.keys(log.files).length,
    trackedSections: Object.keys(log.sections).length,
  }));
}

main().catch(e => {
  console.error('Error:', e.message);
  process.exit(1);
});
