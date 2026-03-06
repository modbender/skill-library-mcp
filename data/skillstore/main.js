#!/usr/bin/env node

/**
 * SkillStore - OpenClaw Skill Manager
 * Intelligent search with semantic matching and threshold filtering
 */

const fs = require('fs');
const path = require('path');
const { exec } = require('child_process');
const https = require('https');

const C = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  mag: '\x1b[35m'
};

const log = (msg, color = 'reset') => console.log(`${C[color]}${msg}${C.reset}`);
const err = (msg) => console.error(`${C.red}Error:${C.reset} ${msg}`);

const CONFIG_FILE = path.join(__dirname, 'config.json');
const MATCH_THRESHOLD = 0.3; // 30% similarity threshold

// Known skills with detailed descriptions
const SKILL_DATABASE = [
  { name: 'homeassistant', desc: 'Control smart home devices like lights switches thermostats via Home Assistant API', keywords: ['home', 'assistant', 'smart', 'homeassistant', 'ha', 'light', 'switch', 'thermostat', 'iot', 'automation'] },
  { name: 'skillstore', desc: 'Search install and create OpenClaw skills with intelligent matching semantic search threshold filtering', keywords: ['skill', 'store', 'openclaw', 'install', 'search', 'create', 'template', 'manager'] },
  { name: 'openclaw-migrate', desc: 'Migrate OpenClaw from one host to another via SSH sync config skills memory tokens', keywords: ['migrate', 'openclaw', 'ssh', 'sync', 'migration', 'transfer', 'backup'] },
  { name: 'openhue', desc: 'Control Philips Hue lights and scenes', keywords: ['hue', 'philips', 'light', 'bulb', 'scene'] },
  { name: 'blucli', desc: 'Control BluOS speakers and streaming devices', keywords: ['bluos', 'speaker', 'audio', 'music', 'streaming', 'bluetooth'] },
  { name: 'sonoscli', desc: 'Control Sonos speakers and groups', keywords: ['sonos', 'speaker', 'audio', 'music', 'streaming'] },
  { name: 'eightctl', desc: 'Control Eight Sleep pods temperature and alarms', keywords: ['eight', 'sleep', 'pod', 'temperature', 'mattress', 'bed'] },
  { name: 'gog', desc: 'Google Workspace CLI for Gmail Calendar Drive Contacts Sheets Docs', keywords: ['google', 'gmail', 'calendar', 'drive', 'workspace', 'email', 'document'] },
  { name: 'himalaya', desc: 'Email client via IMAP SMTP terminal', keywords: ['email', 'imap', 'smtp', 'mail', 'terminal'] },
  { name: 'obsidian', desc: 'Obsidian vault integration and automation', keywords: ['obsidian', 'note', 'markdown', 'vault', 'knowledge'] },
  { name: 'ordercli', desc: 'Food delivery order management Foodora Deliveroo', keywords: ['food', 'order', 'delivery', 'foodora', 'deliveroo', 'eat'] },
  { name: 'weather', desc: 'Weather forecasts current temperature conditions', keywords: ['weather', 'forecast', 'temperature', 'rain', 'sun', 'climate'] },
  { name: 'github', desc: 'GitHub CLI issues pull requests workflows', keywords: ['github', 'git', 'issue', 'pr', 'pull', 'request', 'repo', 'repository'] },
  { name: 'blogwatcher', desc: 'Monitor RSS Atom feeds for blog updates', keywords: ['blog', 'rss', 'feed', 'monitor', 'watch', 'atom', 'news'] },
  { name: 'gifgrep', desc: 'Search and download GIFs from providers', keywords: ['gif', 'image', 'search', 'meme', 'animation'] },
  { name: 'video-frames', desc: 'Extract frames and clips from video files', keywords: ['video', 'frame', 'clip', 'extract', 'ffmpeg'] },
  { name: 'youtube-summarizer', desc: 'Summarize YouTube video transcripts', keywords: ['youtube', 'video', 'transcript', 'summarize', 'summary'] },
  { name: 'ga4', desc: 'Google Analytics 4 query and reporting', keywords: ['analytics', 'ga4', 'google', 'traffic', 'pageview', 'metric'] },
  { name: 'gsc', desc: 'Google Search Console SEO query data', keywords: ['seo', 'search', 'google', 'console', 'ranking', 'clicks'] },
  { name: 'wacli', desc: 'WhatsApp messaging via CLI send messages', keywords: ['whatsapp', 'wa', 'message', 'send', 'chat'] },
  { name: 'browser', desc: 'Automate web browser interactions', keywords: ['browser', 'automation', 'web', 'scraping', 'selenium', 'playwright'] },
  { name: 'healthcheck', desc: 'Security hardening and system monitoring', keywords: ['security', 'hardening', 'monitor', 'health', 'firewall', 'audit'] },
];

// Load config
function loadConfig() {
  if (fs.existsSync(CONFIG_FILE)) {
    return JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
  }
  return { installed: [], searchHistory: [] };
}

function saveConfig(config) {
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}

// Prompt user
function prompt(question) {
  return new Promise(resolve => {
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout
    });
    readline.question(question, answer => {
      readline.close();
      resolve(answer);
    });
  });
}

// HTTP request helper
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers: { 'User-Agent': 'OpenClaw-SkillStore/1.0' } }, (res) => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => {
        try { resolve(JSON.parse(data)); }
        catch (e) { resolve({}); }
      });
    });
    req.on('error', reject);
    req.setTimeout(5000, () => { req.destroy(); reject(new Error('timeout')); });
  });
}

// Tokenize text into words
function tokenize(text) {
  return text.toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2);
}

// Calculate similarity between query and skill
function calculateSimilarity(query, skill) {
  const queryWords = new Set(tokenize(query));
  const skillWords = new Set([
    ...tokenize(skill.name),
    ...tokenize(skill.desc),
    ...skill.keywords
  ]);
  
  // Jaccard similarity
  const intersection = [...queryWords].filter(w => skillWords.has(w));
  const union = new Set([...queryWords, ...skillWords]);
  
  let score = intersection.length / union.size;
  
  // Boost for exact keyword matches
  for (const word of queryWords) {
    if (skill.keywords.includes(word)) score += 0.1;
    if (skill.name.toLowerCase().includes(word)) score += 0.15;
  }
  
  // Boost for name match
  const queryLower = query.toLowerCase();
  if (skill.name.toLowerCase().includes(queryLower.split(' ')[0])) {
    score += 0.1;
  }
  
  return Math.min(score, 1); // Cap at 1.0
}

// Search local skills with content analysis
function searchLocal(query) {
  const skillsDir = path.join(__dirname, '..');
  if (!fs.existsSync(skillsDir)) return [];
  
  const results = [];
  const items = fs.readdirSync(skillsDir);
  const q = query.toLowerCase();
  
  for (const item of items) {
    const itemPath = path.join(skillsDir, item);
    if (!fs.statSync(itemPath).isDirectory()) continue;
    
    let content = '';
    let fullDesc = '';
    
    // Read SKILL.md and README.md
    for (const file of ['SKILL.md', 'README.md']) {
      const fpath = path.join(itemPath, file);
      if (fs.existsSync(fpath)) {
        content += fs.readFileSync(fpath, 'utf8') + ' ';
      }
    }
    
    fullDesc = content;
    
    const score = calculateSimilarity(query, {
      name: item,
      desc: fullDesc.substring(0, 500), // Limit desc length
      keywords: tokenize(fullDesc)
    });
    
    if (score >= MATCH_THRESHOLD) {
      results.push({
        name: item,
        score,
        type: 'local',
        desc: fullDesc.substring(0, 200).replace(/[#*`\n]/g, ' ').trim()
      });
    }
  }
  
  return results.sort((a, b) => b.score - a.score);
}

// Search GitHub with semantic matching
async function searchGitHub(query) {
  log(`Searching GitHub for "${query}"...`, 'cyan');
  
  try {
    const results = await httpGet(
      `https://api.github.com/search/repositories?q=openclaw+${encodeURIComponent(query)}+in:name,description&per_page=15`
    );
    
    if (!results.items) return [];
    
    const scoredResults = [];
    
    for (const r of results.items) {
      const score = calculateSimilarity(query, {
        name: r.name,
        desc: r.description || '',
        keywords: tokenize(r.name + ' ' + (r.description || ''))
      });
      
      if (score >= MATCH_THRESHOLD) {
        scoredResults.push({
          name: r.name,
          fullName: r.full_name,
          desc: r.description || 'No description',
          url: r.html_url,
          stars: r.stargazers_count,
          score,
          type: 'git'
        });
      }
    }
    
    return scoredResults.sort((a, b) => b.score - a.score);
    
  } catch (e) {
    log('GitHub search unavailable', 'gray');
    return [];
  }
}

// Search known skills database
function searchKnown(query) {
  const scoredResults = [];
  
  for (const skill of SKILL_DATABASE) {
    const score = calculateSimilarity(query, skill);
    
    if (score >= MATCH_THRESHOLD) {
      scoredResults.push({
        name: skill.name,
        desc: skill.desc,
        score,
        type: 'known'
      });
    }
  }
  
  return scoredResults.sort((a, b) => b.score - a.score);
}

// Show search results with scores
function showResults(query, results) {
  const matchCount = results.filter(r => r.score >= MATCH_THRESHOLD).length;
  
  log(`\n${C.bright}Search Results for "${query}"${C.reset}`, 'cyan');
  log(`Match threshold: ${Math.round(MATCH_THRESHOLD * 100)}% | Found: ${matchCount}\n`, 'gray');
  
  if (matchCount === 0) {
    log(`No skills match your request above ${Math.round(MATCH_THRESHOLD * 100)}% threshold.`, 'yellow');
    return false;
  }
  
  results.forEach((r, i) => {
    const bar = '█'.repeat(Math.max(1, Math.floor(r.score * 10)));
    const barColor = r.score >= 0.5 ? 'green' : (r.score >= 0.3 ? 'yellow' : 'gray');
    const prefix = r.type === 'local' ? '[LOCAL]' : r.type === 'git' ? '[GIT]' : '[KNOWN]';
    const prefixColor = r.type === 'local' ? 'green' : r.type === 'git' ? 'cyan' : 'mag';
    
    log(`${i + 1}. ${C[prefixColor]}${prefix}${C.reset} ${C.bright}${r.name}${C.reset} ${C[barColor]}${bar}${C.reset} ${Math.round(r.score * 100)}%`, prefixColor);
    log(`   ${r.desc.substring(0, 80)}...`, 'gray');
  });
  
  return true;
}

// Install from GitHub
async function installFromGitHub(repo, name) {
  log(`\nInstalling ${name} from GitHub...`, 'cyan');
  
  const skillsDir = path.join(__dirname, '..');
  const targetDir = path.join(skillsDir, name);
  
  if (fs.existsSync(targetDir)) {
    log(`Skill "${name}" already exists`, 'yellow');
    return false;
  }
  
  const cmd = `git clone https://github.com/${repo}.git "${targetDir}"`;
  
  return new Promise((resolve) => {
    exec(cmd, (error) => {
      if (error) {
        err(`Failed to install: ${error.message}`);
        resolve(false);
        return;
      }
      
      log(`Installed to ${targetDir}`, 'green');
      
      const config = loadConfig();
      config.installed.push({ name, repo, installedAt: new Date().toISOString() });
      saveConfig(config);
      
      resolve(true);
    });
  });
}

// Create new skill with templates
function createNewSkill(name) {
  log(`\nCreating new skill: ${name}`, 'cyan');
  
  const skillsDir = path.join(__dirname, '..');
  const targetDir = path.join(skillsDir, name);
  
  if (fs.existsSync(targetDir)) {
    err(`Skill "${name}" already exists!`);
    return false;
  }
  
  fs.mkdirSync(targetDir, { recursive: true });
  
  const templates = {
    'SKILL.md': `# ${name}

Brief description of what this skill does.

## Setup

\\\`\\\`\\\`bash
# Installation steps
\\\`\\\`\\\`

## Usage

\\\`\\\`\\\`bash
${name} command
\\\`\\\`\\\`

## Configuration

Required environment variables or config options.

## Supported Commands

- \\\`command1\\\` - Description
- \\\`command2\\\` - Description`,
    
    'README.md': `# ${name}

Brief description.

## Features

- Feature 1
- Feature 2

## Quick Start

\\\`\\\`\\\`bash
# Setup
${name} setup

# Usage
${name} command
\\\`\\\`\\\`

## License

MIT`,
    
    'config.json': `{\n  "name": "${name}",\n  "version": "1.0.0"\n}`,
    
    '.gitignore': `config.json\n*.token\n*.key\n.env\nnode_modules/`,
    
    'main.js': `#!/usr/bin/env node

/**
 * ${name} - Skill for OpenClaw
 */

const C = {
  reset: '\\x1b[0m',
  green: '\\x1b[32m',
  yellow: '\\x1b[33m',
  cyan: '\\x1b[36m'
};

const log = (msg, color = 'reset') => console.log(\`\${C[color]}\${msg}\${C.reset}\`);

function main() {
  const args = process.argv.slice(2);
  const cmd = args[0];
  
  if (!cmd || cmd === 'help') {
    log('Usage: ' + process.argv[1] + ' <command>', 'yellow');
    return;
  }
  
  log(\`Command: \${cmd}\`, 'cyan');
}

main();
`
  };
  
  for (const [filename, content] of Object.entries(templates)) {
    fs.writeFileSync(path.join(targetDir, filename), content);
  }
  
  fs.chmodSync(path.join(targetDir, 'main.js'), '755');
  
  log(`Created at: ${targetDir}`, 'green');
  return true;
}

// List installed skills
function listInstalled() {
  const config = loadConfig();
  
  log(`\n${C.bright}Installed Skills${C.reset}\n`, 'cyan');
  
  const skillsDir = path.join(__dirname, '..');
  if (fs.existsSync(skillsDir)) {
    const items = fs.readdirSync(skillsDir).filter(i => {
      const p = path.join(skillsDir, i);
      return fs.statSync(p).isDirectory() && !i.startsWith('.');
    });
    
    if (items.length > 0) {
      items.forEach(s => log(`  - ${s}`, 'gray'));
    } else {
      log('  No skills installed', 'gray');
    }
  }
}

// Show known skills
function showKnownSkills() {
  log(`\n${C.bright}Known OpenClaw Skills (${SKILL_DATABASE.length})${C.reset}\n`, 'cyan');
  
  for (const s of SKILL_DATABASE) {
    log(`  - ${C.green}${s.name}${C.reset} - ${s.desc}`, 'gray');
  }
}

// Main workflow
async function main() {
  const args = process.argv.slice(2);
  const query = args.join(' ');
  
  if (!query || query === 'help' || query === '-h') {
    log(C.bright + '\nSkillStore - Intelligent Skill Search' + C.reset, 'cyan');
    log('\nUsage:', 'yellow');
    log('  skillstore <query>     - Search and filter skills', 'gray');
    log('  skillstore list        - List installed skills', 'gray');
    log('  skillstore known       - Show known skills', 'gray');
    log('  skillstore create <n>   - Create new skill', 'gray');
    log(`\nThreshold: ${Math.round(MATCH_THRESHOLD * 100)}% similarity required`, 'gray');
    log('\nExamples:', 'yellow');
    log('  skillstore control lights', 'gray');
    log('  skillstore email gmail', 'gray');
    log('  skillstore weather forecast', 'gray');
    return;
  }
  
  if (query === 'list' || query === 'ls') {
    listInstalled();
    return;
  }
  
  if (query === 'known') {
    showKnownSkills();
    return;
  }
  
  if (query.startsWith('create ') || query.startsWith('new ')) {
    const name = query.replace(/^(create|new)\s+/, '');
    createNewSkill(name);
    return;
  }
  
  // Intelligent search workflow
  log(C.bright + '\n=== SkillStore Search ===' + C.reset, 'cyan');
  log(`Query: "${query}" | Threshold: ${Math.round(MATCH_THRESHOLD * 100)}%+\n`, 'gray');
  
  // Step 1: Search known skills (fastest, most accurate)
  const knownResults = searchKnown(query);
  
  // Step 2: Search local skills
  const localResults = searchLocal(query);
  
  // Step 3: Search GitHub
  const gitResults = await searchGitHub(query);
  
  // Combine and deduplicate
  const allResults = [...knownResults, ...localResults, ...gitResults];
  
  // Remove duplicates by name (keep highest score)
  const seen = new Map();
  for (const r of allResults) {
    if (!seen.has(r.name) || seen.get(r.name).score < r.score) {
      seen.set(r.name, r);
    }
  }
  
  const uniqueResults = [...seen.values()].sort((a, b) => b.score - a.score);
  
  // Show results
  const hasResults = showResults(query, uniqueResults);
  
  if (!hasResults) {
    log('\nNo existing skills match your needs above threshold.', 'yellow');
    const create = await prompt(`Create new skill "${query.replace(/\s+/g, '-')}"? (y/n): `);
    
    if (create.toLowerCase() === 'y') {
      const name = query.toLowerCase()
        .replace(/[^a-z0-9]/g, '-')
        .replace(/-+/g, '-')
        .replace(/^-|-$/g, '');
      createNewSkill(name);
    }
    return;
  }
  
  // Interactive selection
  const gitOnly = gitResults.filter(r => r.type === 'git');
  if (gitOnly.length > 0) {
    log(`\n${C.yellow}Enter number (1-${gitOnly.length}) to install from GitHub${C.reset}`, 'gray');
  }
  log(`${C.gray}Or 'n' to create new, 'q' to quit${C.reset}`, 'gray');
  
  const choice = await prompt('\nYour choice: ');
  
  const num = parseInt(choice);
  if (!isNaN(num) && num >= 1 && num <= gitOnly.length) {
    const selected = gitOnly[num - 1];
    await installFromGitHub(selected.fullName, selected.name);
    return;
  }
  
  if (choice.toLowerCase() === 'n') {
    const name = query.toLowerCase()
      .replace(/[^a-z0-9]/g, '-')
      .replace(/-+/g, '-')
      .replace(/^-|-$/g, '');
    createNewSkill(name);
    return;
  }
  
  log('Cancelled', 'gray');
}

main();
