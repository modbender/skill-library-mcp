#!/usr/bin/env node
/**
 * OpenClaw Daily Podcast Generator v2
 * 
 * Generates personalized podcast briefings from OpenClaw workspace memory.
 * Supports 8 built-in styles + custom user-defined styles.
 * 
 * Usage:
 *   node generate-episode.js
 *   node generate-episode.js --style "The Advisor" --time-of-day morning
 *   node generate-episode.js --style "10X Thinking" --dry-run
 *   node generate-episode.js --custom "My Custom Style"
 *   node generate-episode.js --date 2026-02-11 --style "Week in Review"
 */

const fs = require('fs');
const path = require('path');
const https = require('https');

// --- Config ---
const DEFAULT_STYLE = 'The Briefing';
const DEFAULT_TIME = 'evening';
// Official Superlore API — hosted on Render (superlore.ai domain proxies here)
const DEFAULT_API = 'https://superlore-api.onrender.com';
const DEFAULT_DEVICE_ID = 'openclaw-daily-podcast-v1';
const DEFAULT_API_KEY = process.env.SUPERLORE_API_KEY || '';

// Try to find workspace - check cwd first, then parent directories
function findWorkspace() {
  let dir = process.cwd();
  for (let i = 0; i < 5; i++) {
    if (fs.existsSync(path.join(dir, 'memory'))) return dir;
    const parent = path.dirname(dir);
    if (parent === dir) break;
    dir = parent;
  }
  return process.cwd();
}

const WORKSPACE = findWorkspace();
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const JOBS_FILE = path.join(WORKSPACE, 'JOBS.md');
const HEARTBEAT_FILE = path.join(WORKSPACE, 'HEARTBEAT.md');
const MEMORY_FILE = path.join(WORKSPACE, 'MEMORY.md');
const CUSTOM_STYLES_DIR = path.join(WORKSPACE, 'podcast-styles');

// --- Helpers ---
function formatDate(d) {
  return d.toISOString().split('T')[0];
}

function readFileSafe(filepath) {
  try { return fs.readFileSync(filepath, 'utf-8'); } catch { return null; }
}

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    dryRun: false,
    date: null,
    style: DEFAULT_STYLE,
    custom: null,
    timeOfDay: DEFAULT_TIME,
    apiUrl: DEFAULT_API,
    deviceId: DEFAULT_DEVICE_ID,
    apiKey: DEFAULT_API_KEY,
    poll: true,
    noMemory: false,
    channel: null,
  };
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--dry-run') opts.dryRun = true;
    else if (args[i] === '--no-memory') opts.noMemory = true;
    else if (args[i] === '--no-poll') opts.poll = false;
    else if (args[i] === '--date' && args[i + 1]) opts.date = args[++i];
    else if (args[i] === '--style' && args[i + 1]) opts.style = args[++i];
    else if (args[i] === '--custom' && args[i + 1]) opts.custom = args[++i];
    else if (args[i] === '--time-of-day' && args[i + 1]) opts.timeOfDay = args[++i];
    else if (args[i] === '--api-url' && args[i + 1]) opts.apiUrl = args[++i];
    else if (args[i] === '--device-id' && args[i + 1]) opts.deviceId = args[++i];
    else if (args[i] === '--api-key' && args[i + 1]) opts.apiKey = args[++i];
    else if (args[i] === '--channel' && args[i + 1]) opts.channel = args[++i];
    else if (args[i] === '--list-styles') { listStyles(); process.exit(0); }
    else if (args[i] === '--help' || args[i] === '-h') { showHelp(); process.exit(0); }
  }
  
  return opts;
}

function listStyles() {
  console.log('\n📻 Available Podcast Styles\n');
  console.log('Built-in:');
  const builtIn = Object.keys(getBuiltInStyles());
  builtIn.forEach(s => console.log(`  • ${s}`));
  
  const custom = loadCustomStyles();
  if (Object.keys(custom).length > 0) {
    console.log('\nCustom (from podcast-styles/):');
    Object.keys(custom).forEach(s => {
      const desc = custom[s].description || '';
      console.log(`  • ${s}${desc ? ' — ' + desc : ''}`);
    });
  }
  
  console.log('\nCreate custom styles in: podcast-styles/<name>.json');
  console.log('See --help for custom style format.\n');
}

function showHelp() {
  console.log(`
OpenClaw Daily Podcast Generator v2

Usage:
  node generate-episode.js [options]

Options:
  --style <name>              Built-in or custom style (default: "The Briefing")
  --custom <name>             Explicitly use a custom style from podcast-styles/
  --time-of-day <morning|midday|evening>  Time context (default: "evening")
  --date YYYY-MM-DD          Generate for specific date (default: today)
  --dry-run                  Preview prompt without creating episode
  --no-poll                  Don't poll for episode completion
  --list-styles              List all available styles (built-in + custom)
  --api-url <url>            Override Superlore API URL
  --device-id <id>           Device identifier for tracking
  --api-key <key>            Superlore API key
  --channel <channel>        Deliver episode link to a channel when ready (e.g., telegram, discord)
  --help, -h                 Show this help message

Built-in Styles:
  "The Briefing"             Documentary narrator — accomplishments, metrics, blockers
  "Opportunities & Tactics"  Growth opportunities and tactical moves
  "10X Thinking"             Moonshot perspective, challenge assumptions
  "The Advisor"              Honest mentor feedback and pattern recognition
  "Focus & Priorities"       Ruthless prioritization, the ONE thing
  "Growth & Scale"           Revenue, users, funnels, conversion strategy
  "Week in Review"           Weekly summary with trends (best Friday/Sunday)
  "The Futurist"             3/6/12-month trajectory and vision

Custom Styles:
  Create a JSON file in your workspace's podcast-styles/ directory:
  
  podcast-styles/my-style.json:
  {
    "name": "My Custom Style",
    "description": "Brief description of the style",
    "voice": "af_heart",
    "speed": 0.95,
    "targetMinutes": 6,
    "instructions": "Your detailed instructions for the AI narrator..."
  }

  Then use: --style "My Custom Style" or --custom "my-style"

Examples:
  node generate-episode.js
  node generate-episode.js --style "The Advisor" --time-of-day morning
  node generate-episode.js --custom "founder-debrief" --dry-run
  node generate-episode.js --list-styles
`);
}

function httpRequest(url, options, body) {
  return new Promise((resolve, reject) => {
    const parsedUrl = new URL(url);
    const req = https.request({
      hostname: parsedUrl.hostname,
      port: parsedUrl.port || 443,
      path: parsedUrl.pathname + parsedUrl.search,
      method: options.method || 'GET',
      headers: options.headers || {},
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(data) }); }
        catch { resolve({ status: res.statusCode, data }); }
      });
    });
    req.on('error', (err) => {
      if (err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT' || err.code === 'ENOTFOUND') {
        err.isNetworkError = true;
      }
      reject(err);
    });
    if (body) req.write(body);
    req.end();
  });
}

function handleApiError(status, data) {
  if (status === 401) {
    console.error('❌ Invalid or missing API key. Get yours at https://superlore.ai → Account → API Keys');
  } else if (status === 402) {
    console.error("❌ You've used all your free hours! Upgrade at https://superlore.ai/pricing for more.");
  } else if (status === 429) {
    console.error('❌ Rate limited. Please wait a moment and try again.');
  } else if (status >= 500) {
    console.error('❌ Superlore API error. The service may be temporarily unavailable. Try again in a few minutes.');
    if (data && data.error) console.error('   Details:', data.error);
  } else {
    console.error(`❌ API error (${status}):`, data);
  }
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function getUserName() {
  const userFile = readFileSafe(path.join(WORKSPACE, 'USER.md'));
  if (userFile) {
    const callMatch = userFile.match(/what to call them[:\s*]+(\w+)/i);
    if (callMatch) return callMatch[1];
    const nameMatch = userFile.match(/\*\*Name:\*\*\s*(\w+)/i);
    if (nameMatch) return nameMatch[1];
  }
  return 'there';
}

// --- Custom Styles ---
function loadCustomStyles() {
  const styles = {};
  
  // Check workspace/podcast-styles/
  if (fs.existsSync(CUSTOM_STYLES_DIR)) {
    const files = fs.readdirSync(CUSTOM_STYLES_DIR).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const content = JSON.parse(fs.readFileSync(path.join(CUSTOM_STYLES_DIR, file), 'utf-8'));
        const name = content.name || file.replace('.json', '');
        styles[name] = {
          voice: content.voice || 'af_heart',
          speed: content.speed || 0.90,
          targetMinutes: content.targetMinutes || 6,
          instructions: content.instructions || '',
          description: content.description || '',
          dataSources: content.dataSources || null, // optional custom data sources
        };
      } catch (e) {
        console.warn(`⚠️  Failed to load custom style ${file}: ${e.message}`);
      }
    }
  }
  
  // Also check ~/.openclaw/podcast-styles/ for global custom styles
  const globalDir = path.join(process.env.HOME || '', '.openclaw', 'podcast-styles');
  if (fs.existsSync(globalDir)) {
    const files = fs.readdirSync(globalDir).filter(f => f.endsWith('.json'));
    for (const file of files) {
      try {
        const content = JSON.parse(fs.readFileSync(path.join(globalDir, file), 'utf-8'));
        const name = content.name || file.replace('.json', '');
        if (!styles[name]) { // workspace styles take priority
          styles[name] = {
            voice: content.voice || 'af_heart',
            speed: content.speed || 0.90,
            targetMinutes: content.targetMinutes || 6,
            instructions: content.instructions || '',
            description: content.description || '',
            dataSources: content.dataSources || null,
          };
        }
      } catch (e) {
        console.warn(`⚠️  Failed to load global custom style ${file}: ${e.message}`);
      }
    }
  }
  
  return styles;
}

// --- Data Extraction ---
function extractAccomplishments(memo) {
  if (!memo) return [];
  const items = [];
  const lines = memo.split('\n');
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Broader matching — catch more work items
    if (/✅|done|completed|shipped|deployed|fixed|built|created|launched|implemented|published|added|updated|improved|resolved|merged|refactored|configured|migrated|optimized|wrote|designed/i.test(line)) {
      let text = line.replace(/^[#\-*\s>]+/, '').replace(/✅/g, '').trim();
      if (text.length > 10 && text.length < 300) {
        items.push(text);
      }
    }
  }
  return items;
}

function extractMetrics(memo) {
  if (!memo) return [];
  const metrics = [];
  const patterns = [
    /(\d+)\s*(articles?|posts?|pages?|blogs?)\s*(published|written|created|pushed)/i,
    /(\d+)\s*(tests?|specs?)\s*(passing|added|fixed)/i,
    /(\d+)\s*(keywords?|backlinks?|domains?)/i,
    /(\d+)\s*(episodes?|podcasts?)\s*(created|generated)/i,
    /(\d+)\s*(bugs?|issues?|errors?)\s*(fixed|resolved)/i,
    /(\d+)\s*(commands?|features?)\s*(added|built|shipped)/i,
    /DR\s*[:\s]*(\d+\.?\d*)/i,
    /traffic[:\s]*~?(\d[\d,]*)\s*(visits?|views?)/i,
    /(\d+)\s*(personas?|competitors?|strategies?|tactics?)/i,
    /(\d[\d,]*)\s*(chars?|lines?|words?)\s/i,
    /(\d+)\s*(users?|signups?|subscribers?)/i,
    /\$[\d,.]+/i,
    /(\d+)%/i,
  ];
  
  const lines = memo.split('\n');
  for (const line of lines) {
    for (const pat of patterns) {
      const match = line.match(pat);
      if (match) {
        let text = line.replace(/^[#\-*\s>]+/, '').trim();
        if (text.length > 5 && text.length < 200) {
          metrics.push(text);
          break;
        }
      }
    }
  }
  return [...new Set(metrics)].slice(0, 10);
}

function extractBlockers(memo, heartbeat) {
  const blockers = [];
  const sources = [memo, heartbeat].filter(Boolean);
  
  for (const src of sources) {
    const lines = src.split('\n');
    for (const line of lines) {
      if (/⏸️|blocked|blocker|❌|failed|error|broken|urgent|need[s]?\s+(to|access|info|help)/i.test(line)) {
        let text = line.replace(/^[#\-*\s>\[\]]+/, '').replace(/⏸️|❌/g, '').trim();
        if (text.length > 10 && text.length < 200 && !/not found|no memory/i.test(text)) {
          blockers.push(text);
        }
      }
    }
  }
  return [...new Set(blockers)].slice(0, 5);
}

function extractUpcoming(heartbeat, jobs) {
  const upcoming = [];
  
  if (heartbeat) {
    // Look for unchecked task items
    for (const line of heartbeat.split('\n')) {
      if (/^\s*-\s*\[\s\]/.test(line)) {
        let text = line.replace(/^\s*-\s*\[\s\]\s*/, '').trim();
        text = text.replace(/\(#\d+[^)]*\)/g, '').trim();
        if (text.length > 5 && text.length < 200) upcoming.push(text);
      }
    }
  }
  
  if (jobs && upcoming.length < 5) {
    const lines = jobs.split('\n');
    for (const line of lines) {
      if (/🟡/.test(line)) {
        const match = line.match(/\*\*(.+?)\*\*/);
        if (match) {
          const name = match[1].split('—')[0].trim();
          if (!upcoming.some(u => u.toLowerCase().includes(name.toLowerCase()))) {
            upcoming.push(name);
          }
        }
      }
    }
  }
  
  return upcoming.slice(0, 7);
}

function extractSections(memo) {
  if (!memo) return [];
  return memo.split('\n')
    .filter(l => /^##\s/.test(l))
    .map(l => l.replace(/^#+\s*/, '').replace(/✅.*$/, '').replace(/\(.*?\)/, '').trim())
    .filter(s => s.length > 3 && s.length < 100);
}

function countJobs(jobs) {
  if (!jobs) return { done: 0, inProgress: 0, notStarted: 0, blocked: 0, total: 0 };
  const lines = jobs.split('\n');
  return {
    done: lines.filter(l => /🟢/.test(l)).length,
    inProgress: lines.filter(l => /🟡/.test(l)).length,
    notStarted: lines.filter(l => /🔴/.test(l)).length,
    blocked: lines.filter(l => /⏸️/.test(l)).length,
    total: lines.filter(l => /🟢|🟡|🔴|⏸️/.test(l)).length,
  };
}

function rankByImpact(items) {
  const highImpact = /security|deploy|launch|ship|revenue|user|customer|fix.*critical|production|SEO|blog|article|growth|pipeline|API|auth/i;
  const medImpact = /built|created|implemented|test|optimize|improve|strategy|research|analysis|design|refactor/i;
  
  return items
    .map(item => ({
      text: item,
      score: highImpact.test(item) ? 3 : medImpact.test(item) ? 2 : 1,
    }))
    .sort((a, b) => b.score - a.score)
    .map(x => x.text);
}

// =============================================================================
// PRIVACY & SANITIZATION
// =============================================================================
// These functions ensure sensitive data never leaves the user's machine.
// The agent reads workspace files locally; only the sanitized briefing text
// is sent to Superlore's API. Raw files are NEVER transmitted.
// =============================================================================

/**
 * Strip secrets, tokens, keys, and credentials from any text.
 * This runs on ALL data before it's included in the briefing prompt.
 * 
 * What gets stripped:
 * - API keys, tokens, passwords (pattern-matched)
 * - Email addresses (except bare first names)
 * - IP addresses and internal hostnames
 * - SSH credentials and connection strings
 * - Database URLs and connection strings
 * - File paths that reveal system structure
 * - Base64-encoded blobs (likely secrets)
 */
function stripSecrets(text) {
  if (!text) return text;
  
  return text
    // API keys & tokens: long alphanumeric strings near sensitive keywords
    .replace(/(?:api[_-]?key|token|secret|password|credential|auth)[:\s=]*[`"']?[A-Za-z0-9_\-./]{16,}[`"']?/gi, '[REDACTED]')
    // Standalone long tokens (sk_, rpa_, ghp_, etc.)
    .replace(/\b(?:sk|rpa|ghp|gho|Bearer|xox[bpas]|AKIA)[_\-]?[A-Za-z0-9_\-]{16,}\b/g, '[REDACTED]')
    // Database connection strings
    .replace(/(?:postgres|mysql|mongodb|redis):\/\/[^\s"'`)\]]+/gi, '[REDACTED_DB_URL]')
    // Generic URLs with credentials (user:pass@host)
    .replace(/\b\w+:\/\/[^@\s]+@[^\s"'`)\]]+/g, '[REDACTED_URL]')
    // Email addresses
    .replace(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g, '[email]')
    // IP addresses (v4)
    .replace(/\b(?:10|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b/g, '[internal-ip]')
    // SSH-style credentials
    .replace(/ssh\s+\S+@\S+/gi, '[SSH_REDACTED]')
    // Absolute file paths (home directories)
    .replace(/(?:\/Users\/|\/home\/|C:\\Users\\)\S+/g, '[path]')
    // Base64 blobs (40+ chars, likely encoded secrets)
    .replace(/\b[A-Za-z0-9+/]{40,}={0,3}\b/g, '[REDACTED_BASE64]')
    // Hex strings that look like hashes/keys (32+ chars)
    .replace(/\b[0-9a-f]{32,}\b/gi, '[REDACTED_HEX]');
}

/**
 * Sanitize MEMORY.md — strip internal agent instructions, secrets, and operational details.
 * Only keep product context, metrics, and project info useful for a podcast script.
 */
function sanitizeMemory(memory) {
  if (!memory) return null;
  
  const lines = memory.split('\n');
  const filtered = [];
  let skipSection = false;
  
  // Sections that contain agent internals, not useful for podcasts
  const skipPatterns = [
    /^## HARD RULES/i,
    /^## Model Routing/i,
    /^## OpenClaw Operations/i,
    /^## Active Crons/i,
    /^## Render Credentials/i,
    /^## Tailscale/i,
    /^## Anti-Token/i,
    /^## Lessons Learned/i,
    /^## Tools & Access/i,
    /^## Google Sheets/i,
    /^## API Keys/i,
  ];
  
  // Individual lines that are sensitive regardless of section
  const skipLinePatterns = [
    /off limits/i,
    /do not read inbox/i,
    /email.*can use/i,
    /api[._-]?key/i,
    /password/i,
    /credential/i,
    /service.account/i,
    /session.*target/i,
    /subagent/i,
    /heartbeat.*fire/i,
    /cron.*job/i,
    /sonnet|opus|claude|anthropic/i,
    /token.*budget/i,
    /launchd/i,
    /sentry\.io/i,
    /\.env\b/i,
    /DATABASE_URL/i,
    /SUPABASE/i,
    /OPENAI/i,
    /service.?id/i,
  ];
  
  for (const line of lines) {
    if (skipPatterns.some(p => p.test(line))) {
      skipSection = true;
      continue;
    }
    
    if (skipSection && /^## /.test(line) && !skipPatterns.some(p => p.test(line))) {
      skipSection = false;
    }
    
    if (skipSection) continue;
    if (skipLinePatterns.some(p => p.test(line))) continue;
    
    filtered.push(line);
  }
  
  // Apply secret stripping as a final pass
  const result = stripSecrets(filtered.join('\n').trim());
  // Limit to 1200 chars of useful context
  return result.slice(0, 1200);
}

/**
 * Sanitize daily memory files — strip secrets while preserving work narrative.
 * Less aggressive than MEMORY.md sanitization since daily files are primarily
 * work logs, but still removes any embedded secrets.
 */
function sanitizeDailyMemo(memo) {
  if (!memo) return memo;
  return stripSecrets(memo);
}

// --- Build Briefing Data ---
function buildBriefingData(date, memoryFiles, jobs, heartbeat, memory, isWeekly) {
  const userName = getUserName();
  const dateStr = new Date(date + 'T12:00:00').toLocaleDateString('en-US', {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });

  // Combine all available memory files — sanitize each one
  const allMemos = memoryFiles.filter(Boolean).map(sanitizeDailyMemo);
  const todayMemo = allMemos[0];
  const yesterdayMemo = allMemos[1];

  const accomplishments = rankByImpact(extractAccomplishments(todayMemo));
  const metrics = extractMetrics(todayMemo);
  const blockers = extractBlockers(todayMemo, heartbeat);
  const upcoming = extractUpcoming(heartbeat, jobs);
  const sections = extractSections(todayMemo);
  const jobCounts = countJobs(jobs);

  // For weekly, aggregate across all days
  let weeklyAccomplishments = [];
  let weeklyMetrics = [];
  let weeklySections = [];
  if (isWeekly && allMemos.length > 1) {
    for (const memo of allMemos) {
      weeklyAccomplishments.push(...extractAccomplishments(memo));
      weeklyMetrics.push(...extractMetrics(memo));
      weeklySections.push(...extractSections(memo));
    }
    weeklyAccomplishments = rankByImpact([...new Set(weeklyAccomplishments)]);
    weeklyMetrics = [...new Set(weeklyMetrics)];
    weeklySections = [...new Set(weeklySections)];
  }

  const topAccomplishments = isWeekly ? weeklyAccomplishments.slice(0, 10) : accomplishments.slice(0, 5);
  const displayMetrics = isWeekly ? weeklyMetrics.slice(0, 15) : metrics;
  const displaySections = isWeekly ? weeklySections : sections;
  
  let briefing = '';
  briefing += `# ${isWeekly ? 'Weekly' : 'Daily'} Briefing: ${dateStr}\n\n`;
  
  briefing += `## Context\n`;
  briefing += `This is a ${isWeekly ? 'weekly' : 'daily'} briefing for ${userName}.\n\n`;

  if (topAccomplishments.length > 0) {
    briefing += `## Top Accomplishments${isWeekly ? ' This Week' : ' Today'}\n`;
    topAccomplishments.forEach((a, i) => {
      briefing += `${i + 1}. ${a}\n`;
    });
    briefing += '\n';
  }

  if (displayMetrics.length > 0) {
    briefing += `## Key Metrics & Numbers\n`;
    displayMetrics.forEach(m => briefing += `- ${m}\n`);
    briefing += '\n';
  }

  if (displaySections.length > 0) {
    briefing += `## Areas of Work${isWeekly ? ' This Week' : ' Today'}\n`;
    displaySections.forEach(s => briefing += `- ${s}\n`);
    briefing += '\n';
  }

  if (jobCounts.total > 0) {
    briefing += `## Job Board Status\n`;
    briefing += `- ${jobCounts.total} total jobs tracked\n`;
    briefing += `- ${jobCounts.done} completed, ${jobCounts.inProgress} in progress, ${jobCounts.notStarted} not started`;
    if (jobCounts.blocked > 0) briefing += `, ${jobCounts.blocked} blocked`;
    briefing += '\n\n';
  }

  if (blockers.length > 0) {
    briefing += `## Blockers & Issues\n`;
    blockers.forEach(b => briefing += `- ⚠️ ${b}\n`);
    briefing += '\n';
  }

  if (upcoming.length > 0) {
    briefing += `## Coming Up Next\n`;
    upcoming.forEach(u => briefing += `- ${u}\n`);
    briefing += '\n';
  }

  if (!isWeekly && yesterdayMemo) {
    const yesterdaySections = extractSections(yesterdayMemo);
    if (yesterdaySections.length > 0) {
      briefing += `## Yesterday's Context\n`;
      briefing += `Yesterday focused on: ${yesterdaySections.slice(0, 4).join(', ')}.\n\n`;
    }
  }

  // Add sanitized memory context (no secrets, no agent instructions)
  const cleanMemory = sanitizeMemory(memory);
  if (cleanMemory) {
    briefing += `## Project Context\n`;
    briefing += cleanMemory + '\n\n';
  }

  return { briefing, userName, dateStr };
}

// --- Style Configurations ---
function getBuiltInStyles() {
  return {
    'The Briefing': {
      voice: 'af_heart-80_af_sarah-15_af_nicole-5', // Luna — warm, professional narrator
      speed: 0.90,
      targetMinutes: 6,
      instructions: `
1. Open with a warm, professional greeting and the full date.
2. Lead with the BIGGEST accomplishment or most exciting development — make it a headline.
3. Cover the top 3-5 accomplishments as a narrative, not a list. Weave them into a story of progress.
4. Include specific numbers and metrics where available — they make the briefing credible and concrete.
5. If there are blockers, present them as "challenges on the radar" — honest but not doom-and-gloom.
6. End with a "looking ahead" preview of what's planned next, building anticipation.
7. Close with an encouraging, forward-looking sign-off.

STYLE RULES:
- Sound like a professional documentary narrator, NOT a robot reading a log file.
- Use transitions between topics ("Meanwhile...", "On the growth front...", "Shifting to engineering...").
- Keep energy up — this is a briefing someone should look forward to hearing.
- Reference the user by name. This is THEIR project, make it personal.
- Aim for 5-7 minutes of engaging content.
- Do NOT list items with bullet points — narrate them naturally.
- Include a brief "by the numbers" segment summarizing key metrics.
`,
    },
    
    'Opportunities & Tactics': {
      voice: 'am_michael-60_am_eric-40', // Michael — strategic, authoritative
      speed: 0.90,
      targetMinutes: 7,
      instructions: `
1. Open with a warm greeting and date, positioning this as a strategic opportunities review.
2. Acknowledge what was accomplished, but quickly pivot to "Here's what this unlocks..."
3. Identify 3-5 growth opportunities or tactical moves based on today's work:
   - What could be amplified or scaled?
   - What competitive gaps exist that could be filled?
   - What's being overlooked or underutilized?
   - What quick wins are available?
4. For each opportunity, explain:
   - Why it matters (the leverage point)
   - What it would take to execute (realistic assessment)
   - What the upside could be
5. Reference industry trends, competitive landscape, or market positioning where relevant.
6. End with "If I had to pick ONE tactical move for tomorrow, it would be..." — force prioritization.
7. Close with an encouraging nudge toward action.

STYLE RULES:
- Think like a growth strategist, not a task manager
- Use questions: "Have you considered...?" "What if...?" "Why not...?"
- Be specific about tactics, not vague inspirational fluff
- Acknowledge constraints but focus on possibilities
- Reference concrete examples from today's work
- Sound excited about potential, not preachy
`,
    },
    
    '10X Thinking': {
      voice: 'am_michael-60_am_eric-40', // Michael — bold, confident
      speed: 0.95,
      targetMinutes: 5,
      instructions: `
1. Open with energy and the full date, then: "this is your ten-X thinking session. Let's challenge some assumptions."
2. Acknowledge today's work briefly, then immediately ask: "But what if we're thinking too small?"
3. Explore 10x questions:
   - What would 10x users/revenue/impact look like?
   - What assumptions would need to be FALSE for that to happen?
   - What are we doing that's incremental vs. transformational?
   - Where could we create a monopoly or unfair advantage?
4. Challenge conventional wisdom: "Everyone does X. What if we did Y instead?"
5. Identify one "crazy" idea that might not be crazy
6. Ask: "What's the ONE thing that, if solved, would make everything else easier or irrelevant?"
7. Close with a bold challenge: "Tomorrow, what if you focused on THIS instead?"

STYLE RULES:
- Be provocative but not obnoxious
- Use Peter Thiel's framework: "What important truth do very few people agree with you on?"
- Challenge incrementalism — 10% improvement vs. 10x transformation
- Sound like a brilliant contrarian, not a motivational speaker
- Keep it grounded in today's actual work — this isn't abstract philosophy
`,
    },
    
    'The Advisor': {
      voice: 'af_heart-80_af_sarah-15_af_nicole-5', // Luna — thoughtful mentor
      speed: 0.92,
      targetMinutes: 7,
      instructions: `
1. Open warmly with the full date: "Let's review your day."
2. Acknowledge the wins genuinely: "Here's what I'm seeing that's working well..."
3. Identify patterns — both positive and concerning:
   - "I notice you're consistently..."
   - "There's a pattern emerging around..."
4. Ask honest questions:
   - "Is this really the highest leverage use of time?"
   - "Have you considered why X keeps coming up?"
   - "What would happen if you said no to Y?"
5. Offer experience-based perspective: "In my experience, when founders face this, they usually..."
6. Give 1-2 specific recommendations, not vague advice
7. End with accountability: "Next time we talk, I'll ask you about [specific thing]. Deal?"
8. Close with warmth and confidence in them.

STYLE RULES:
- Balance praise and constructive feedback (not just cheerleading)
- Use "I notice..." and "Have you considered..." framing
- Be specific, not generic ("work smarter" is useless; "delegate X so you can focus on Y" is helpful)
- Show you've been paying attention (reference previous work/patterns)
- Sound like someone who's been through this before
- Be warm but don't avoid hard truths
`,
    },
    
    'Focus & Priorities': {
      voice: 'af_heart', // Heart — intimate, direct
      speed: 0.95,
      targetMinutes: 5,
      instructions: `
1. Open decisively with the full date: "Let's cut through the noise and find what matters."
2. Acknowledge the volume of work in one sentence, then pivot: "But here's the question: what's actually moving the needle?"
3. Categorize today's work:
   - HIGH LEVERAGE: Things that compound or unlock future opportunities
   - NECESSARY: Things that maintain momentum but don't create leverage
   - BUSY WORK: Things that feel productive but don't drive outcomes
4. Identify the ONE thing: "If you could only accomplish one thing tomorrow, it should be..."
5. Name 1-2 things to STOP doing or delegate
6. Reference the 80/20 rule: "20% of today's work will drive 80% of results. That 20% is..."
7. Close with a challenge: "Tomorrow, protect time for [the ONE thing]. Everything else is secondary."

STYLE RULES:
- Be brutally honest about busy work vs. real work
- No fluff, no rambling — every sentence should deliver value
- Keep the whole episode under 5 minutes
- End with clarity, not more options
`,
    },
    
    'Growth & Scale': {
      voice: 'am_michael-60_am_eric-40', // Michael — data-driven authority
      speed: 0.92,
      targetMinutes: 6,
      instructions: `
1. Open with focus on metrics and the full date: "Let's look at the numbers."
2. Present key growth metrics from today's work:
   - Users, traffic, signups, conversions
   - Revenue, MRR, growth rate
   - Engagement metrics (retention, activation, referral)
3. Identify what's working: "The growth lever that's showing traction is..."
4. Identify what's NOT working: "The bottleneck in the funnel appears to be..."
5. Analyze today's work through a growth lens:
   - What activities directly impact acquisition, activation, retention, revenue, or referral?
   - What experiments were run or could be run?
6. Recommend 1-2 growth experiments for tomorrow:
   - Hypothesis: "If we do X, we expect Y to improve by Z%"
   - How to measure it
7. Reference growth frameworks: pirate metrics (AARRR), growth loops, compounding tactics
8. Close with focus on one growth metric to move tomorrow.

STYLE RULES:
- Lead with numbers and data, not feelings
- Use growth terminology: CAC, LTV, activation rate, viral coefficient
- Think in systems and loops, not one-off tactics
- Be honest about what's NOT working
- End with a clear hypothesis to test
`,
    },
    
    'Week in Review': {
      voice: 'af_heart-80_af_sarah-15_af_nicole-5', // Luna — reflective storytelling
      speed: 0.88,
      targetMinutes: 10,
      instructions: `
1. Open reflectively with the full date: "this is your week in review. Let's zoom out."
2. Frame the week: "This week, the story was really about..."
3. Highlight weekly wins (cumulative accomplishments across all days):
   - What shipped or got completed?
   - What major milestones were hit?
   - What surprised you (good or bad)?
4. Identify trends and patterns across the week:
   - "Early in the week you were focused on X, by the end you'd shifted to Y..."
   - "You're building momentum around..."
5. Present a "by the numbers" weekly summary (cumulative metrics)
6. Name 1-2 lessons learned this week
7. Look ahead: "Next week, the priorities should be..."
8. Set 1-3 weekly goals for the coming week
9. Close with encouragement and a reset for the new week.

STYLE RULES:
- This is a reflection, not a race — slow down
- Celebrate the cumulative wins (it's easy to forget progress)
- Identify momentum and trends (what's building over time?)
- Use "the story of this week" framing — create narrative coherence
- Reference specific days when available
- This episode should feel like closure and a fresh start
`,
    },
    
    'The Futurist': {
      voice: 'af_heart', // Heart — intimate visionary
      speed: 0.95,
      targetMinutes: 7,
      instructions: `
1. Open with future focus and the full date: "Let's talk about where this is heading."
2. Briefly acknowledge today's work, then ask: "But what is this building toward?"
3. Project forward in three horizons:
   - **3 months from now**: If this trajectory continues, what will exist that doesn't today?
   - **6 months from now**: What major milestones or capabilities will be reached?
   - **12 months from now**: What does success look like?
4. Connect today's specific work to future outcomes:
   - "Today's work on X is actually laying groundwork for..."
   - "This seems small now, but in 6 months it could enable..."
5. Identify inflection points: "The thing that will change the trajectory is..."
6. Ask strategic questions:
   - "Are we building toward the right future?"
   - "What would need to be true for this to 10x in a year?"
7. End with a north-star reminder: "The vision is... and today moved us closer."

STYLE RULES:
- Be speculative but grounded in real progress (not fantasy)
- Use timelines: "In 3 months... In 6 months... In 12 months..."
- Connect tactical work to strategic outcomes
- Sound like a visionary founder, not a fortune teller
- Balance ambition with realism
`,
    },
  };
}

function getStyleConfig(styleName, customStyleName) {
  // If explicit custom style requested, load from file
  if (customStyleName) {
    const custom = loadCustomStyles();
    // Try exact name match first, then filename match
    if (custom[customStyleName]) return custom[customStyleName];
    // Try case-insensitive
    const key = Object.keys(custom).find(k => k.toLowerCase() === customStyleName.toLowerCase());
    if (key) return custom[key];
    console.error(`❌ Custom style "${customStyleName}" not found. Use --list-styles to see available styles.`);
    process.exit(1);
  }
  
  // Check built-in styles
  const builtIn = getBuiltInStyles();
  if (builtIn[styleName]) return builtIn[styleName];
  
  // Check custom styles as fallback
  const custom = loadCustomStyles();
  if (custom[styleName]) return custom[styleName];
  const key = Object.keys(custom).find(k => k.toLowerCase() === styleName.toLowerCase());
  if (key) return custom[key];
  
  console.warn(`⚠️  Style "${styleName}" not found, falling back to "The Briefing"`);
  return builtIn['The Briefing'];
}

function formatDateForAudio(dateStr) {
  const parts = dateStr.split(' ');
  if (parts.length < 4) return dateStr;
  
  const day = parts[2].replace(',', '');
  const year = parts[3];
  
  const dayNum = parseInt(day);
  const dayWords = ['', 'first', 'second', 'third', 'fourth', 'fifth', 'sixth', 'seventh', 'eighth', 'ninth', 'tenth',
    'eleventh', 'twelfth', 'thirteenth', 'fourteenth', 'fifteenth', 'sixteenth', 'seventeenth', 'eighteenth', 'nineteenth', 'twentieth',
    'twenty-first', 'twenty-second', 'twenty-third', 'twenty-fourth', 'twenty-fifth', 'twenty-sixth', 'twenty-seventh', 'twenty-eighth', 'twenty-ninth', 'thirtieth', 'thirty-first'];
  
  const dayText = dayWords[dayNum] || day;
  
  const yearNum = parseInt(year);
  let yearText = year;
  if (yearNum >= 2000 && yearNum < 2100) {
    const remainder = yearNum % 100;
    const centuryWord = 'twenty';
    const remainderWord = remainder < 10 ? 'oh-' + ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][remainder] :
      remainder < 20 ? ['ten', 'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen'][remainder - 10] :
      ['twenty', 'thirty', 'forty', 'fifty', 'sixty', 'seventy', 'eighty', 'ninety'][Math.floor(remainder / 10) - 2] + (remainder % 10 > 0 ? '-' + ['', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'][remainder % 10] : '');
    yearText = centuryWord + ' ' + remainderWord;
  }
  
  return `${parts[0]} ${parts[1]} ${dayText}, ${yearText}`;
}

// --- Build Episode Prompt ---
/**
 * Generate a personalized cover image prompt that blends:
 * 1. The user's project/product context (from IDENTITY.md or SOUL.md)
 * 2. The episode style's theme
 * 3. Time-of-day atmosphere
 * 
 * Simple formula: [project elements] + [style mood] + [lighting]
 */
function generateCoverImagePrompt(styleName, timeOfDay, config) {
  // Extract project context from workspace files
  let projectKeywords = [];
  try {
    const workspace = process.env.HOME + '/.openclaw/workspace';
    const fs = require('fs');
    
    // Try IDENTITY.md first, then USER.md
    for (const file of ['IDENTITY.md', 'USER.md', 'SOUL.md']) {
      try {
        const content = fs.readFileSync(`${workspace}/${file}`, 'utf8').toLowerCase();
        // Extract product/project descriptors
        const productPatterns = [
          /(?:builds?|creates?|makes?|platform for|app for|tool for)\s+([a-z\s,]+)/g,
          /(?:podcast|audio|music|video|code|design|art|writing|content|saas|api)/g,
        ];
        for (const p of productPatterns) {
          const matches = content.match(p) || [];
          projectKeywords.push(...matches.slice(0, 3));
        }
        if (projectKeywords.length > 0) break;
      } catch {}
    }
  } catch {}

  // Distill to a short project flavor (max 30 chars)
  const projectFlavor = projectKeywords.length > 0
    ? projectKeywords.slice(0, 2).join(', ').substring(0, 60)
    : '';

  const lighting = {
    morning: 'warm golden sunrise light',
    midday: 'bright natural daylight',
    evening: 'warm amber evening glow',
  }[timeOfDay] || 'cinematic dramatic lighting';

  // Style themes — simple, evocative concepts
  const styleThemes = {
    'The Briefing': ['mission control dashboard', 'strategic overview map', 'data streams flowing'],
    'Opportunities & Tactics': ['chess pieces and strategy', 'compass pointing to opportunity', 'doors opening to light'],
    '10X Thinking': ['rocket launching upward', 'exponential growth chart', 'lightning bolt of innovation'],
    'The Advisor': ['wise mentor\'s bookshelf', 'handwritten notes by firelight', 'two chairs in conversation'],
    'Focus & Priorities': ['single arrow hitting bullseye', 'one spotlight in darkness', 'clear path through chaos'],
    'Growth & Scale': ['seedling becoming giant tree', 'ascending staircase of progress', 'rising graph with momentum'],
    'Week in Review': ['mountain trail looking back at journey', 'mosaic of the week\'s moments', 'sunset reflection on calm water'],
    'The Futurist': ['telescope pointed at stars', 'road stretching to horizon', 'blueprint of tomorrow'],
  };

  const themes = styleThemes[styleName] || styleThemes['The Briefing'];
  const dateHash = new Date().getDate() + new Date().getHours();
  const theme = themes[dateHash % themes.length];

  // Build prompt: project context + style theme + lighting
  const projectContext = projectFlavor
    ? `Incorporate subtle elements of ${projectFlavor}. `
    : '';
  
  return `${theme}. ${projectContext}${lighting}. Cinematic photograph, abstract and evocative. No people, no faces, no microphones, no text.`;
}

function buildEpisodePrompt(styleName, timeOfDay, briefingData, dateStr, config) {
  const { briefing, userName } = briefingData;
  
  const greeting = timeOfDay === 'morning' ? 'Good morning' : timeOfDay === 'midday' ? 'Good afternoon' : 'Good evening';
  const audioDate = formatDateForAudio(dateStr);
  
  // PRIVACY: Final pass — strip any secrets that survived earlier sanitization
  // This is a defense-in-depth measure; earlier stages should have caught most
  const strippedBriefing = stripSecrets(briefing);
  
  // Clean special chars and trim to stay under API limits
  let safeBriefing = strippedBriefing
    .replace(/—/g, '-')
    .replace(/→/g, '->')
    .replace(/[\u2600-\u27BF\uFE0F]/gu, '')  // misc symbols
    .replace(/[\u{1F300}-\u{1FAFF}]/gu, '');  // emoji
  
  // Hard limit: keep briefing under ~3000 chars so total topic (briefing + instructions) stays under ~4400 chars
  // The Superlore API returns 500 when body exceeds ~4870 bytes
  if (safeBriefing.length > 3000) {
    safeBriefing = safeBriefing.substring(0, 3000) + '\n\n[briefing truncated for length]';
  }

  let topic = `You are producing a professional podcast briefing episode. Here is today's structured briefing data:

${safeBriefing}

---

INSTRUCTIONS FOR THE EPISODE:

**CRITICAL: Start directly with "${greeting}, ${userName}. It is ${audioDate}..." then introduce the style naturally.**

DO NOT include flowery preambles like "The code that ships..." or "This is a story about..." — get straight to the briefing.

${config.instructions}

WRITING STYLE (applies to ALL styles):
- Keep sentences SHORT — aim for 10-18 words per sentence. Break up long compound sentences.
- Use natural pauses: end paragraphs with a clear thought. Let ideas breathe.
- Vary rhythm: mix short punchy sentences with occasional longer ones. Don't be monotone.
- Write for the EAR, not the eye. If a sentence needs re-reading, it's too complex for audio.
`;

  // Hard limit: Superlore API returns 500 when JSON body exceeds ~4870 bytes
  // Keep topic under 4200 chars to stay safe with UTF-8 expansion
  if (topic.length > 4200) {
    // Trim the briefing section, keep instructions intact
    const overhead = topic.length - safeBriefing.length;
    const maxBriefing = 4200 - overhead - 50; // 50 char buffer
    safeBriefing = safeBriefing.substring(0, maxBriefing) + '\n[truncated]';
    topic = `You are producing a professional podcast briefing episode. Here is today's structured briefing data:

${safeBriefing}

---

INSTRUCTIONS FOR THE EPISODE:

**CRITICAL: Start directly with "${greeting}, ${userName}. It is ${audioDate}..." then introduce the style naturally.**

DO NOT include flowery preambles like "The code that ships..." or "This is a story about..." — get straight to the briefing.

${config.instructions}
`;
  }

  const dateFormatted = new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  const title = `${styleName} — ${dateFormatted}`;

  return { topic, title };
}

// --- Main ---
async function main() {
  const opts = parseArgs();
  
  const today = opts.date || formatDate(new Date());
  const isWeekly = (opts.custom || opts.style).toLowerCase().includes('week');
  
  // Read memory files — 7 days for weekly, 2 for daily
  const daysToRead = isWeekly ? 7 : 2;
  const memoryFiles = [];
  for (let i = 0; i < daysToRead; i++) {
    const d = formatDate(new Date(new Date(today + 'T12:00:00').getTime() - i * 86400000));
    memoryFiles.push(readFileSafe(path.join(MEMORY_DIR, `${d}.md`)));
  }

  const styleName = opts.custom || opts.style;
  const config = getStyleConfig(opts.style, opts.custom);

  console.log(`📻 OpenClaw Daily Podcast Generator v2`);
  console.log(`   Style: ${styleName}${opts.custom ? ' (custom)' : ''}`);
  console.log(`   Voice: ${config.voice} @ ${config.speed}x`);
  console.log(`   Time: ${opts.timeOfDay}`);
  console.log(`   Date: ${today}`);
  console.log(`   Workspace: ${WORKSPACE}`);

  const jobs = readFileSafe(JOBS_FILE);
  const heartbeat = readFileSafe(HEARTBEAT_FILE);
  const memory = opts.noMemory ? null : readFileSafe(MEMORY_FILE);

  const foundMemos = memoryFiles.filter(Boolean).length;
  if (foundMemos === 0) {
    console.error('❌ No memory files found. Nothing to summarize.');
    process.exit(1);
  }

  console.log(`   Memory files found: ${foundMemos}/${daysToRead}`);
  console.log(`   JOBS.md: ${jobs ? jobs.length + ' chars' : 'not found'}`);
  console.log(`   HEARTBEAT.md: ${heartbeat ? heartbeat.length + ' chars' : 'not found'}`);
  console.log(`   MEMORY.md: ${memory ? 'loaded (sanitized)' : 'not found'}`);

  // Build briefing data
  const briefingData = buildBriefingData(today, memoryFiles, jobs, heartbeat, memory, isWeekly);
  const { topic, title } = buildEpisodePrompt(styleName, opts.timeOfDay, briefingData, briefingData.dateStr, config);

  if (opts.dryRun) {
    console.log('\n' + '='.repeat(70));
    console.log('📝 DRY RUN — This is EXACTLY what would be sent to Superlore\'s API');
    console.log('   Your raw workspace files are NEVER sent. Only this processed text.');
    console.log('='.repeat(70) + '\n');
    console.log(topic);
    console.log('\n' + '-'.repeat(70));
    console.log(`   Title: ${title}`);
    console.log(`   Prompt length: ${topic.length} chars`);
    console.log(`   Voice: ${config.voice}`);
    console.log(`   Speed: ${config.speed}`);
    console.log(`   Target: ${config.targetMinutes} minutes`);
    console.log(`   Visibility: private (hardcoded — cannot be overridden)`);
    console.log(`   Secrets stripped: API keys, tokens, emails, IPs, paths, DB URLs`);
    console.log(`\n💡 Tip: Review the text above. If you see anything sensitive,`);
    console.log(`   report it so we can improve the sanitization rules.`);
    return;
  }

  // Create episode via Superlore API
  console.log('\n🎙️  Creating Superlore episode...');

  // Generate creative cover image prompt based on style
  const coverImagePrompt = generateCoverImagePrompt(styleName, opts.timeOfDay, config);

  const body = JSON.stringify({
    topic,
    title,
    style: 'documentary',
    tone: 'documentary',
    voice: config.voice,
    voiceProvider: 'local',
    voiceSpeed: config.speed,
    ttsModel: 'kokoro',
    targetMinutes: config.targetMinutes,
    language: 'en',
    visibility: 'private', // HARDCODED — briefings contain personal workspace data. NEVER public.
    webSearch: false,
    altScript: false,
    coverImagePrompt,
  });

  let res;
  try {
    res = await httpRequest(`${opts.apiUrl}/episodes`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(opts.apiKey ? { 'x-api-key': opts.apiKey } : { 'X-Device-ID': opts.deviceId }),
      },
    }, body);
  } catch (err) {
    if (err.isNetworkError) {
      console.error('❌ Could not reach Superlore API. Check your internet connection.');
    } else {
      console.error('❌ Network error:', err.message);
    }
    process.exit(1);
  }

  if (res.status >= 400) {
    handleApiError(res.status, res.data);
    process.exit(1);
  }

  const episode = res.data?.episode || res.data;
  const slug = episode.slug || episode.id;
  const url = `https://superlore.ai/episode/${slug}`;

  console.log(`\n✅ Episode created!`);
  console.log(`   ID: ${episode.id}`);
  console.log(`   Title: ${title}`);
  console.log(`   Slug: ${slug}`);
  console.log(`   Status: ${episode.status}`);
  console.log(`   URL: ${url}`);

  // Poll for completion
  if (opts.poll && opts.apiKey) {
    console.log(`\n⏳ Polling for completion (checking every 5s, up to 5 minutes)...`);
    const maxAttempts = 60; // 60 attempts × 5s = 5 minutes
    for (let i = 0; i < maxAttempts; i++) {
      await sleep(5000);
      try {
        const check = await httpRequest(`${opts.apiUrl}/episodes/${episode.id}`, {
          method: 'GET',
          headers: {
            ...(opts.apiKey ? { 'x-api-key': opts.apiKey } : { 'X-Device-ID': opts.deviceId }),
          },
        });
        const ep = check.data?.episode || check.data;
        const status = ep?.status || 'unknown';
        if (status === 'ready' || status === 'completed') {
          console.log(`\n🎉 Episode ready! Listen: ${url}`);
          if (opts.channel) {
            console.log(`[EPISODE_READY] url=${url} channel=${opts.channel}`);
          }
          return;
        } else if (status === 'failed') {
          console.error(`\n❌ Episode generation failed.`);
          process.exit(1);
        }
        // Print a dot every 5 attempts (~25s) to show progress without flooding
        if (i % 5 === 4) process.stdout.write(`.`);
      } catch (err) {
        if (err.isNetworkError) {
          console.error('\n❌ Could not reach Superlore API. Check your internet connection.');
          process.exit(1);
        }
        process.stdout.write(`?`);
      }
    }
    console.log(`\n⏳ Still processing after 5 minutes. Check: ${url}`);
  } else {
    console.log(`\n   ⏳ Episode is generating. Check the URL in ~2-5 minutes.`);
    if (opts.channel) {
      console.log(`[EPISODE_READY] url=${url} channel=${opts.channel}`);
    }
  }
}

main().catch(err => {
  if (err.isNetworkError || err.code === 'ECONNREFUSED' || err.code === 'ETIMEDOUT' || err.code === 'ENOTFOUND') {
    console.error('❌ Could not reach Superlore API. Check your internet connection.');
  } else {
    console.error('❌ Fatal error:', err.message);
  }
  process.exit(1);
});
