#!/usr/bin/env node
/**
 * BrainDB Memory Migration v2
 * 
 * Imports existing OpenClaw workspace files into BrainDB.
 * Smart local extraction — no external API required.
 *
 * Usage:
 *   node migrate.cjs [workspace_path]          # Migrate workspace
 *   node migrate.cjs --scan [workspace_path]   # Preview what would be migrated
 *   node migrate.cjs --file path/to/file.md    # Migrate a single file
 *
 * Options:
 *   --braindb URL    BrainDB gateway URL (default: http://localhost:3333)
 *   --dry-run        Extract facts but don't encode
 *   --scan           Just list files that would be migrated
 *   --verbose        Show each extracted fact
 *   --swarm          Use Gemini Flash for extraction (sends data to Google API)
 *   --no-swarm       Force local extraction (default)
 */

const fs = require('fs');
const path = require('path');
const http = require('http');

// ─── Config ──────────────────────────────────────────────
const args = process.argv.slice(2);
const flags = new Set(args.filter(a => a.startsWith('--')));
const positional = [];
for (let i = 0; i < args.length; i++) {
  if (args[i].startsWith('--')) {
    if (['--braindb', '--swarm', '--file'].includes(args[i])) i++;
    continue;
  }
  positional.push(args[i]);
}

function getArg(name, fallback) {
  const idx = args.indexOf(`--${name}`);
  return idx !== -1 && args[idx + 1] ? args[idx + 1] : fallback;
}

const WORKSPACE = positional[0] || process.cwd();
const BRAINDB_URL = getArg('braindb', 'http://localhost:3333');
const DRY_RUN = flags.has('--dry-run');
const SCAN_ONLY = flags.has('--scan');
const VERBOSE = flags.has('--verbose');
const USE_SWARM = flags.has('--swarm');
const SINGLE_FILE = getArg('file', null);

// ─── File Discovery ──────────────────────────────────────

const KNOWN_FILES = [
  { pattern: 'MEMORY.md', shard: 'mixed', priority: 1, desc: 'Long-term memory' },
  { pattern: 'USER.md', shard: 'semantic', priority: 1, desc: 'User profile' },
  { pattern: 'IDENTITY.md', shard: 'semantic', priority: 1, desc: 'Agent identity' },
  { pattern: 'SOUL.md', shard: 'semantic', priority: 1, desc: 'Personality & behavior' },
  { pattern: 'AGENTS.md', shard: 'procedural', priority: 2, desc: 'Agent instructions' },
  { pattern: 'TOOLS.md', shard: 'procedural', priority: 2, desc: 'Tool configuration' },
  { pattern: 'HEARTBEAT.md', shard: 'procedural', priority: 3, desc: 'Heartbeat config' },
];

function discoverFiles(workspacePath) {
  const files = [];
  const seen = new Set();

  for (const known of KNOWN_FILES) {
    const fullPath = path.join(workspacePath, known.pattern);
    if (fs.existsSync(fullPath)) {
      files.push({ path: fullPath, relative: known.pattern, shard: known.shard, priority: known.priority, desc: known.desc, type: 'workspace' });
      seen.add(fullPath);
    }
  }

  // Daily notes
  const memoryDir = path.join(workspacePath, 'memory');
  if (fs.existsSync(memoryDir)) {
    for (const entry of fs.readdirSync(memoryDir, { withFileTypes: true })) {
      if (entry.isFile() && /^\d{4}-\d{2}-\d{2}\.md$/.test(entry.name)) {
        const fullPath = path.join(memoryDir, entry.name);
        if (!seen.has(fullPath)) {
          files.push({ path: fullPath, relative: `memory/${entry.name}`, shard: 'episodic', priority: 2, desc: `Daily note`, type: 'daily' });
          seen.add(fullPath);
        }
      }
    }
  }

  // Other markdown in known dirs
  for (const dir of ['memory/topics', 'research', 'docs', 'notes']) {
    const dirPath = path.join(workspacePath, dir);
    if (!fs.existsSync(dirPath)) continue;
    walkDir(dirPath, (fullPath, relPath) => {
      if (!seen.has(fullPath) && fullPath.endsWith('.md')) {
        files.push({ path: fullPath, relative: path.join(dir, relPath), shard: 'semantic', priority: 3, desc: dir, type: 'extra' });
        seen.add(fullPath);
      }
    });
  }

  files.sort((a, b) => a.priority - b.priority || a.relative.localeCompare(b.relative));
  return files;
}

function walkDir(dir, callback, base) {
  base = base || dir;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walkDir(full, callback, base);
    else callback(full, path.relative(base, full));
  }
}

// ─── File-Level Summary Facts ────────────────────────────
// Consolidated facts that answer common queries (who, what, etc.)
// These bridge the gap between granular KV facts and vague queries.

function generateSummaryFacts(content, fileName) {
  const summaries = [];
  const lower = content.toLowerCase();
  
  // USER.md / identity files: generate "who is [name]" summary
  if (/user\.md|identity\.md/i.test(fileName)) {
    // Extract name
    const nameMatch = content.match(/\*?\*?Name\*?\*?\s*[:—]\s*(\w+)/i);
    const name = nameMatch ? nameMatch[1] : null;
    
    // Collect key identity facts
    const identityParts = [];
    const patterns = [
      { re: /\*?\*?(?:Name|Full Name)\*?\*?\s*[:—]\s*(.{2,80})/i, label: 'name' },
      { re: /\*?\*?(?:Current Role|Role|Title|Rank)\*?\*?\s*[:—]\s*(.{2,120})/i, label: 'role' },
      { re: /\*?\*?(?:Location|City|Based in)\*?\*?\s*[:—]\s*(.{2,80})/i, label: 'location' },
      { re: /\*?\*?(?:Timezone|TZ)\*?\*?\s*[:—]\s*(.{2,80})/i, label: 'timezone' },
      { re: /\*?\*?(?:Side Business|Business|Company)\*?\*?\s*[:—]\s*(.{2,120})/i, label: 'business' },
      { re: /\*?\*?(?:Pronouns)\*?\*?\s*[:—]\s*(.{2,40})/i, label: 'pronouns' },
    ];
    
    for (const { re, label } of patterns) {
      const m = content.match(re);
      if (m) identityParts.push(`${label}: ${m[1].trim().replace(/\*+/g, '')}`);
    }
    
    if (identityParts.length >= 2) {
      const summary = identityParts.join('. ');
      summaries.push({
        trigger: name ? `Who is ${name} — identity and background` : 'User identity and background',
        content: summary,
        shard: 'semantic',
      });
    }
    
    // Family summary
    const familyLines = [];
    const wifeMatch = content.match(/\*?\*?(?:Wife|Spouse|Partner)\*?\*?\s*[:—]?\s*\n?(?:.*?\*?\*?)?(\w+)/i) ||
                       content.match(/\*?\*?Wife:?\*?\*?\s*\n\s*[-*]\s*\*?\*?(\w+)/i);
    if (wifeMatch) familyLines.push(`Wife: ${wifeMatch[1]}`);
    
    const kidMatches = content.match(/(?:Kids?|Children)\s*(?:\([^)]*\))?\s*[:—]?\s*\n((?:\s*[-*]\s*.+\n?)+)/i);
    if (kidMatches) {
      const kids = kidMatches[1].match(/[-*]\s*(\w+)/g);
      if (kids) familyLines.push(`Kids: ${kids.map(k => k.replace(/[-*]\s*/, '')).join(', ')}`);
    }
    // Also catch inline kid listings
    const kidLines = content.match(/(\w+)\s*(?:—|[-–])\s*(?:\w+ (?:Elementary|Middle|High|School))/gi);
    if (kidLines && kidLines.length > 0) {
      const kidNames = kidLines.map(l => l.match(/^(\w+)/)[1]);
      if (!familyLines.some(f => f.startsWith('Kids'))) {
        familyLines.push(`Kids: ${kidNames.join(', ')}`);
      }
      familyLines.push(...kidLines.map(l => l.trim()));
    }
    
    if (familyLines.length > 0) {
      summaries.push({
        trigger: name ? `${name}'s family — wife and kids` : 'Family members',
        content: familyLines.join('. '),
        shard: 'semantic',
      });
    }
    
    // Technical skills summary
    const skillsSection = content.match(/(?:Technical Skills|Skills|Tech Stack)[\s\S]{0,20}?\n((?:\s*[-*]\s*.+\n?){2,})/i);
    if (skillsSection) {
      summaries.push({
        trigger: name ? `${name}'s technical skills and expertise` : 'Technical skills',
        content: skillsSection[1].replace(/\s*[-*]\s*/g, ', ').trim().replace(/^,\s*/, ''),
        shard: 'semantic',
      });
    }
  }
  
  // IDENTITY.md: agent self-identity summary
  if (/identity\.md/i.test(fileName)) {
    const parts = [];
    const nameMatch = content.match(/\*?\*?Name\*?\*?\s*[:—]\s*(.+)/i);
    const roleMatch = content.match(/\*?\*?Role\*?\*?\s*[:—]\s*(.+)/i);
    const hardwareMatch = content.match(/\*?\*?Hardware\*?\*?\s*[:—]\s*(.+)/i);
    const vibeMatch = content.match(/\*?\*?Vibe\*?\*?\s*[:—]\s*(.+)/i);
    
    if (nameMatch) parts.push(`Name: ${nameMatch[1].trim().replace(/\*+/g, '')}`);
    if (roleMatch) parts.push(`Role: ${roleMatch[1].trim().replace(/\*+/g, '')}`);
    if (hardwareMatch) parts.push(`Hardware: ${hardwareMatch[1].trim().replace(/\*+/g, '')}`);
    if (vibeMatch) parts.push(`Vibe: ${vibeMatch[1].trim().replace(/\*+/g, '')}`);
    
    if (parts.length >= 2) {
      summaries.push({
        trigger: 'My identity — who I am, my name, my role',
        content: parts.join('. '),
        shard: 'semantic',
      });
    }
  }
  
  // SOUL.md: personality summary
  if (/soul\.md/i.test(fileName)) {
    const personalityTraits = [];
    // Extract key behavioral rules
    const noOpeners = content.match(/No hollow openers|Never start with/i);
    const brevity = content.match(/Brevity wins/i);
    const opinions = content.match(/I have opinions/i);
    const humor = content.match(/Dry wit|sardonic|humor/i);
    
    if (brevity) personalityTraits.push('Brevity wins — one sentence if possible');
    if (noOpeners) personalityTraits.push('No hollow openers — never "Great question" or "I\'d be happy to help"');
    if (opinions) personalityTraits.push('Strong opinions — commit to a take rather than hedge');
    if (humor) personalityTraits.push('Dry wit, sardonic when appropriate');
    
    if (personalityTraits.length >= 2) {
      summaries.push({
        trigger: 'My personality — how I communicate and behave',
        content: personalityTraits.join('. '),
        shard: 'semantic',
      });
    }
  }
  
  // MEMORY.md: business/revenue summary
  if (/memory\.md/i.test(fileName)) {
    const revParts = [];
    const revenueMatch = content.match(/Revenue\*?\*?\s*[:—]\s*(.+)/i);
    const clientMatch = content.match(/Primary Client\*?\*?\s*[:—]\s*(.+)/i);
    const targetMatch = content.match(/6-month target\*?\*?\s*[:—]\s*(.+)/i);
    const monthlyMatch = content.match(/Monthly recurring\*?\*?\s*[:—]\s*(.+)/i);
    
    if (revenueMatch) revParts.push(`Revenue: ${revenueMatch[1].trim().replace(/\*+/g, '')}`);
    if (clientMatch) revParts.push(`Primary client: ${clientMatch[1].trim().replace(/\*+/g, '')}`);
    if (monthlyMatch) revParts.push(`Monthly recurring: ${monthlyMatch[1].trim().replace(/\*+/g, '')}`);
    if (targetMatch) revParts.push(`Target: ${targetMatch[1].trim().replace(/\*+/g, '')}`);
    
    if (revParts.length >= 2) {
      summaries.push({
        trigger: 'Business revenue — how we make money, clients, income',
        content: revParts.join('. '),
        shard: 'semantic',
      });
    }
    
    // Projects summary
    const projectNames = [];
    const projectMatches = content.matchAll(/###\s+(.+?)\s*(?:\(|$)/gm);
    for (const pm of projectMatches) {
      const pname = pm[1].trim().replace(/\*+/g, '');
      if (pname.length > 3 && pname.length < 60) projectNames.push(pname);
    }
    if (projectNames.length >= 2) {
      summaries.push({
        trigger: 'Active projects and products we are building',
        content: `Projects: ${projectNames.join(', ')}`,
        shard: 'semantic',
      });
    }
  }
  
  return summaries;
}

// ─── Smart Local Extraction ──────────────────────────────
// This is the core innovation. Instead of dumb chunking, we parse
// markdown structure and extract facts using pattern recognition.

function extractFacts(content, fileName, defaultShard) {
  const facts = [];
  const lines = content.split('\n');
  
  // Parse sections (## headers create sections)
  const sections = [];
  let currentSection = { header: fileName, lines: [], level: 0 };
  
  for (const line of lines) {
    const headerMatch = line.match(/^(#{1,4})\s+(.+)/);
    if (headerMatch) {
      if (currentSection.lines.length > 0) sections.push(currentSection);
      currentSection = { header: headerMatch[2].trim(), lines: [], level: headerMatch[1].length };
    } else {
      currentSection.lines.push(line);
    }
  }
  if (currentSection.lines.length > 0) sections.push(currentSection);

  for (const section of sections) {
    const text = section.lines.join('\n').trim();
    if (text.length < 30) continue;
    
    // Strategy 1: Key-value facts (Name: Value, **Key:** Value)
    const kvFacts = extractKeyValueFacts(text, section.header);
    facts.push(...kvFacts);
    
    // Strategy 2: List items with substance
    const listFacts = extractListFacts(text, section.header);
    facts.push(...listFacts);
    
    // Strategy 3: Paragraph facts (sentences with specific details)
    const paraFacts = extractParagraphFacts(text, section.header);
    facts.push(...paraFacts);
    
    // Strategy 4: Code blocks / commands (procedural)
    const codeFacts = extractCodeFacts(text, section.header);
    facts.push(...codeFacts);
  }
  
  // Deduplicate by trigger similarity
  const unique = deduplicateLocal(facts);
  
  // Assign shards
  for (const fact of unique) {
    if (!fact.shard) {
      fact.shard = classifyShard(fact.trigger, fact.content, defaultShard);
    }
  }
  
  return unique;
}

function extractKeyValueFacts(text, sectionHeader) {
  const facts = [];
  // Match patterns like "**Name:** Value" or "- **Role:** Value"
  const kvPattern = /(?:^|\n)\s*[-*]*\s*\*?\*?([A-Z][^:*\n]{1,40})\*?\*?\s*[:—]\s*(.{10,300})/g;
  let match;
  while ((match = kvPattern.exec(text)) !== null) {
    const key = match[1].trim().replace(/\*+/g, '');
    const value = match[2].trim().replace(/\*+/g, '');
    // Skip meta/structure keys and short values
    if (/^(note|example|todo|fixme|hack|warning|tip)/i.test(key)) continue;
    if (value.length < 10) continue;
    // Use the actual key-value as trigger, not section header
    facts.push({
      trigger: `${key}: ${value.substring(0, 80)}`,
      content: `${key}: ${value}`,
    });
  }
  return facts;
}

function extractListFacts(text, sectionHeader) {
  const facts = [];
  // Match substantive list items with key-value or enough detail
  const listPattern = /(?:^|\n)\s*[-*]\s+\*?\*?(.{20,400})/g;
  let match;
  while ((match = listPattern.exec(text)) !== null) {
    let item = match[1].trim().replace(/\*+/g, '');
    if (/^\[[ x]\]/.test(item)) item = item.replace(/^\[[ x]\]\s*/, '');
    
    // Must have specific content (names, numbers, paths, technical terms)
    if (!/[A-Z][a-z]{2,}|[0-9]|\$|\/|http|@/.test(item)) continue;
    // Skip very short items
    if (item.length < 20) continue;
    
    // Use the item itself as trigger (not just section header)
    const trigger = item.substring(0, 80);
    facts.push({ trigger, content: item });
  }
  return facts;
}

function extractParagraphFacts(text, sectionHeader) {
  const facts = [];
  // Only extract paragraphs that are NOT already captured by KV or list patterns
  // This catches narrative text, descriptions, and context
  const paragraphs = text.split(/\n\n+/).filter(p => {
    const trimmed = p.trim();
    // Skip short, code blocks, tables, and pure list blocks
    if (trimmed.length < 60) return false;
    if (trimmed.startsWith('```') || trimmed.startsWith('|')) return false;
    // Skip if it's just a list (all lines start with - or *)
    const lines = trimmed.split('\n');
    if (lines.every(l => /^\s*[-*]/.test(l) || l.trim() === '')) return false;
    return true;
  });
  
  for (const para of paragraphs) {
    const cleaned = para.trim().replace(/\s+/g, ' ');
    if (!/[A-Z][a-z]{2,}|[0-9]/.test(cleaned)) continue;
    
    // First meaningful sentence as trigger
    const firstSentence = cleaned.match(/^.{20,150}?[.!?](?:\s|$)/) || [cleaned.substring(0, 100)];
    const trigger = `${sectionHeader}: ${firstSentence[0].trim().substring(0, 80)}`;
    
    facts.push({ trigger, content: cleaned.substring(0, 500) });
  }
  return facts;
}

function extractCodeFacts(text, sectionHeader) {
  const facts = [];
  // Extract code blocks with their context
  const codePattern = /```(\w*)\n([\s\S]*?)```/g;
  let match;
  while ((match = codePattern.exec(text)) !== null) {
    const lang = match[1] || 'code';
    const code = match[2].trim();
    if (code.length < 10 || code.length > 500) continue;
    
    // Look for preceding description
    const before = text.substring(Math.max(0, match.index - 100), match.index).trim();
    const lastLine = before.split('\n').pop() || '';
    
    facts.push({
      trigger: `${sectionHeader}: ${lastLine.substring(0, 60) || lang + ' snippet'}`,
      content: `${lastLine}\n\`\`\`${lang}\n${code}\n\`\`\``,
      shard: 'procedural',
    });
  }
  return facts;
}

function deduplicateLocal(facts) {
  const unique = [];
  const seen = new Set();
  
  for (const fact of facts) {
    // Simple dedup by normalized content
    const key = (fact.trigger + fact.content).toLowerCase().replace(/\s+/g, ' ').substring(0, 100);
    if (seen.has(key)) continue;
    
    // Also check for very similar triggers or content
    let isDupe = false;
    for (const existing of unique) {
      if (triggerSimilarity(fact.trigger, existing.trigger) > 0.6 ||
          triggerSimilarity(fact.content, existing.content) > 0.7) {
        // Keep the one with more content
        if (fact.content.length > existing.content.length) {
          unique[unique.indexOf(existing)] = fact;
        }
        isDupe = true;
        break;
      }
    }
    
    if (!isDupe) {
      seen.add(key);
      unique.push(fact);
    }
  }
  return unique;
}

function triggerSimilarity(a, b) {
  const setA = new Set(a.toLowerCase().split(/\s+/));
  const setB = new Set(b.toLowerCase().split(/\s+/));
  const intersection = [...setA].filter(x => setB.has(x)).length;
  const union = new Set([...setA, ...setB]).size;
  return union > 0 ? intersection / union : 0;
}

function classifyShard(trigger, content, defaultShard) {
  if (defaultShard && defaultShard !== 'mixed') return defaultShard;
  
  const text = `${trigger} ${content}`.toLowerCase();
  
  // Procedural indicators
  if (/\b(how to|workflow|rule|process|step|command|script|when to|always|never|pattern)\b/.test(text)) return 'procedural';
  if (/```/.test(text)) return 'procedural';
  
  // Episodic indicators  
  if (/\b(happened|decided|on \d{4}|january|february|march|april|may|june|july|august|september|october|november|december|yesterday|today|last week)\b/.test(text)) return 'episodic';
  if (/\d{4}-\d{2}-\d{2}/.test(text)) return 'episodic';
  
  // Default: semantic (facts, knowledge, preferences)
  return 'semantic';
}

// ─── HTTP Helpers ────────────────────────────────────────

function httpPost(url, body, timeoutMs = 120000) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify(body);
    const parsed = new URL(url);
    const req = http.request({
      hostname: parsed.hostname, port: parsed.port, path: parsed.pathname,
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(data) },
      timeout: timeoutMs,
    }, (res) => {
      let buf = '';
      res.on('data', chunk => buf += chunk);
      res.on('end', () => {
        const lines = buf.trim().split('\n');
        try { resolve(JSON.parse(lines[lines.length - 1])); } catch { resolve(null); }
      });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.write(data);
    req.end();
  });
}

function httpGet(url, timeoutMs = 5000) {
  return new Promise((resolve, reject) => {
    const parsed = new URL(url);
    const req = http.request({
      hostname: parsed.hostname, port: parsed.port, path: parsed.pathname,
      method: 'GET', timeout: timeoutMs,
    }, (res) => {
      let buf = '';
      res.on('data', chunk => buf += chunk);
      res.on('end', () => { try { resolve(JSON.parse(buf)); } catch { resolve(null); } });
    });
    req.on('error', reject);
    req.on('timeout', () => { req.destroy(); reject(new Error('timeout')); });
    req.end();
  });
}

// ─── Swarm Extraction (optional) ─────────────────────────

function buildExtractionPrompt(fileContent, fileName, shard) {
  const shardGuidance = {
    episodic: 'Focus on events, decisions, conversations, milestones.',
    semantic: 'Focus on facts, identities, preferences, relationships, knowledge.',
    procedural: 'Focus on rules, workflows, processes, lessons learned.',
    mixed: 'Classify each fact as episodic, semantic, or procedural.',
  };

  return `Extract the most important, durable facts from this file. Each fact should be a standalone memory useful in future conversations.

Guidelines:
- ${shardGuidance[shard] || shardGuidance.semantic}
- Be specific: include names, numbers, dates, IPs, paths when present
- Each fact must stand alone without the source document
- Skip temporary info and meta-commentary
- Include ALL important facts — err on the side of more, not fewer

Format as JSON array:
[{"trigger": "Short searchable title", "content": "Complete fact with specifics", "shard": "${shard === 'mixed' ? 'semantic|episodic|procedural' : shard}"}]

Source: ${fileName}
---
${fileContent.substring(0, 6000)}`;
}

// ─── Encoding ────────────────────────────────────────────

async function encodeFact(fact, source) {
  return httpPost(`${BRAINDB_URL}/memory/encode`, {
    event: fact.trigger,
    content: fact.content,
    shard: fact.shard || 'semantic',
    context: { source, migrated: new Date().toISOString() },
    motivationDelta: { serve: 0.3 },
    dedupThreshold: 0.88,
  });
}

// ─── Main ────────────────────────────────────────────────

async function main() {
  console.log('🧠 BrainDB Memory Migration v2');
  console.log('═'.repeat(50));

  if (SINGLE_FILE) {
    if (!fs.existsSync(SINGLE_FILE)) {
      console.error(`❌ File not found: ${SINGLE_FILE}`);
      process.exit(1);
    }
    const files = [{ path: path.resolve(SINGLE_FILE), relative: path.basename(SINGLE_FILE), shard: 'mixed', priority: 1, desc: path.basename(SINGLE_FILE), type: 'single' }];
    return await migrateFiles(files);
  }

  const wsPath = path.resolve(WORKSPACE);
  console.log(`📂 Workspace: ${wsPath}`);
  
  const files = discoverFiles(wsPath);
  if (files.length === 0) {
    console.log('\n⚠️  No files found to migrate.');
    process.exit(0);
  }

  if (SCAN_ONLY) {
    console.log(`\n📋 Found ${files.length} files to migrate:\n`);
    for (const f of files) {
      const size = fs.statSync(f.path).size;
      const kb = (size / 1024).toFixed(1);
      console.log(`  ${f.shard.padEnd(11)} ${kb.padStart(6)}KB  ${f.relative}  (${f.desc})`);
    }
    console.log(`\nRun without --scan to migrate.`);
    return;
  }

  await migrateFiles(files);
}

async function migrateFiles(files) {
  try {
    const health = await httpGet(`${BRAINDB_URL}/health`);
    if (!health?.status) throw new Error('no response');
    console.log(`✅ BrainDB: ${health.status} (${health.totalMemories || 0} existing memories)`);
  } catch (e) {
    console.error(`❌ Can't reach BrainDB at ${BRAINDB_URL}`);
    process.exit(1);
  }

  const useSwarm = USE_SWARM;
  if (useSwarm) {
    console.log('🐝 Using Gemini Flash extraction (⚠️ sends data to Google API)');
  } else {
    console.log('📦 Using smart local extraction (fully local, no external API)');
  }
  
  console.log(`📋 Files: ${files.length}`);
  if (DRY_RUN) console.log('   (DRY RUN)');
  console.log('');

  let totalFacts = 0, totalEncoded = 0, totalDedup = 0, errors = 0;

  for (const file of files) {
    const content = fs.readFileSync(file.path, 'utf8');
    if (content.trim().length < 20) {
      if (VERBOSE) console.log(`   ⏭️  ${file.relative}: too short`);
      continue;
    }

    let facts;
    
    if (useSwarm) {
      // Swarm extraction
      try {
        const prompt = buildExtractionPrompt(content, file.relative, file.shard);
        const result = await httpPost('http://localhost:9999/parallel', { prompts: [prompt] });
        const raw = result?.results?.[0];
        const jsonMatch = raw?.match(/\[[\s\S]*?\]/);
        facts = jsonMatch ? JSON.parse(jsonMatch[0]) : null;
      } catch {
        facts = null;
      }
      if (!facts) {
        // Fallback to local
        facts = extractFacts(content, file.relative, file.shard);
      }
    } else {
      facts = extractFacts(content, file.relative, file.shard);
    }

    // Add consolidated summary facts for key files
    const summaryFacts = generateSummaryFacts(content, file.relative);
    if (summaryFacts.length > 0) {
      facts.push(...summaryFacts);
      if (VERBOSE) console.log(`      📋 +${summaryFacts.length} summary facts`);
    }

    console.log(`   📄 ${file.relative}: ${facts.length} facts`);
    totalFacts += facts.length;

    if (DRY_RUN) {
      if (VERBOSE) {
        for (const f of facts) console.log(`      [${f.shard}] ${f.trigger}`);
      }
      continue;
    }

    for (const fact of facts) {
      try {
        const result = await encodeFact(fact, file.relative);
        if (result?.ok) {
          if (result.deduplicated) totalDedup++;
          else totalEncoded++;
          if (VERBOSE) console.log(`      ✅ ${fact.trigger.substring(0, 50)}`);
        } else {
          errors++;
        }
      } catch {
        errors++;
      }
    }
  }

  console.log('');
  console.log('═'.repeat(50));
  console.log('📊 Migration Complete');
  console.log(`   Files: ${files.length} | Facts: ${totalFacts} | Encoded: ${totalEncoded} | Dedup: ${totalDedup} | Errors: ${errors}`);
  console.log('═'.repeat(50));

  if (totalEncoded > 0) {
    console.log('\n✅ Your memories are loaded! Test with:');
    console.log(`   curl -s -X POST ${BRAINDB_URL}/memory/recall \\`);
    console.log(`     -H "Content-Type: application/json" \\`);
    console.log(`     -d '{"query":"who am I","limit":3}'`);
  }
}

main().catch(e => {
  console.error('Fatal:', e.message);
  process.exit(1);
});
