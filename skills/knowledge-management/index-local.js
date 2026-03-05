#!/usr/bin/env node
/**
 * Knowledge Management Skill — Local Storage Mode
 * Parses memory files, classifies entries, and stores them as .md files in type folders.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ============ CONFIGURATION ============
function resolveWorkspace() {
  // Priority 1: CLI argument (explicit override)
  const workspaceArgIdx = process.argv.indexOf('--workspace');
  if (workspaceArgIdx !== -1 && workspaceArgIdx + 1 < process.argv.length) {
    return path.resolve(process.argv[workspaceArgIdx + 1]);
  }

  // Priority 2: Environment variable
  if (process.env.OPENCLAW_WORKSPACE) {
    return path.resolve(process.env.OPENCLAW_WORKSPACE);
  }

  // Priority 3: Current directory IF it looks like a workspace (contains MEMORY.md or memory/)
  const cwd = process.cwd();
  if (cwd) {
    try {
      if (fs.existsSync(path.join(cwd, 'MEMORY.md')) || fs.existsSync(path.join(cwd, 'memory'))) {
        return cwd;
      }
    } catch (e) {
      // ignore and fall through
    }
  }

  // Priority 4: Hardcoded default (maintains backward compatibility for cron)
  return path.resolve('/home/ubuntu/.openclaw/workspace');
}

const WORKSPACE = resolveWorkspace();
const MEMORY_DIR = path.join(WORKSPACE, 'memory');
const MEMORY_FILE = path.join(WORKSPACE, 'MEMORY.md');

// Determine output directory for organized KM files (default: workspace/memory/KM)
function resolveOutputDir() {
  // CLI override: --output-dir <path>
  const outArgIdx = process.argv.indexOf('--output-dir');
  if (outArgIdx !== -1 && outArgIdx + 1 < process.argv.length) {
    const outPath = process.argv[outArgIdx + 1];
    return path.isAbsolute(outPath) ? outPath : path.resolve(WORKSPACE, outPath);
  }
  // Default: memory/KM inside workspace
  return path.join(WORKSPACE, 'memory', 'KM');
}

const OUTPUT_DIR = resolveOutputDir();
const STATE_FILE = path.join(OUTPUT_DIR, 'local-sync-state.json');
const SYNC_LOG = path.join(OUTPUT_DIR, 'local-sync-log.md');

// Content type folders (relative to workspace)
const CONTENT_TYPES = ['Research', 'Decision', 'Insight', 'Lesson', 'Pattern', 'Project', 'Reference', 'Tutorial'];

// ============ LOGGING ============
function log(level, message) {
  const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
  console.log(`[${level}] ${timestamp} - ${message}`);
}

function info(msg) { log('INFO', msg); }
function error(msg) { log('ERROR', msg); }
function warning(msg) { log('WARN', msg); }
function debug(msg) { if (process.argv.includes('--verbose')) log('DEBUG', msg); }

// ============ MEMORY PARSER (unchanged) ============
class MemoryParser {
  constructor(workspace) {
    this.workspace = workspace;
    this.memoryDir = path.join(workspace, 'memory');
  }

  parseMemoryFile() {
    const entries = [];
    if (!fs.existsSync(MEMORY_FILE)) {
      warning(`MEMORY.md not found`);
      return entries;
    }

    const content = fs.readFileSync(MEMORY_FILE, 'utf-8');
    const lines = content.split('\n');

    let currentSection = null;
    let currentEntry = null;
    let entryBuffer = [];

    for (const line of lines) {
      if (line.startsWith('## ')) {
        if (currentEntry && entryBuffer.length) {
          currentEntry.body = entryBuffer.join('\n').trim();
          entries.push(currentEntry);
          entryBuffer = [];
        }

        const sectionTitle = line.slice(3).trim();
        if (['Standard', 'Protocol', 'Lesson', 'Framework', 'Decision', 'Insight', 'Pattern', 'Research'].some(kw => sectionTitle.includes(kw))) {
          currentSection = sectionTitle;
        } else {
          currentSection = null;
        }
        continue;
      }

      if (line.startsWith('### ') && currentSection) {
        if (currentEntry && entryBuffer.length) {
          currentEntry.body = entryBuffer.join('\n').trim();
          entries.push(currentEntry);
          entryBuffer = [];
        }

        const entryTitle = line.slice(4).trim();
        currentEntry = {
          title: entryTitle,
          source: 'MEMORY.md',
          section: currentSection,
          file: 'MEMORY.md'
        };
        continue;
      }

      if (currentEntry !== null) {
        entryBuffer.push(line);
      }
    }

    if (currentEntry && entryBuffer.length) {
      currentEntry.body = entryBuffer.join('\n').trim();
      entries.push(currentEntry);
    }

    info(`Parsed ${entries.length} entries from MEMORY.md`);
    return entries;
  }

  parseDailyFiles(daysBack = 7) {
    const entries = [];
    const today = new Date().toDateString();

    for (let i = 0; i < daysBack; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const filePath = path.join(this.memoryDir, `${dateStr}.md`);

      if (!fs.existsSync(filePath)) continue;

      const content = fs.readFileSync(filePath, 'utf-8');
      const lines = content.split('\n');

      let currentSection = null;
      let currentEntry = null;
      let entryBuffer = [];

      for (const line of lines) {
        if (line.startsWith('## ')) {
          if (currentEntry && entryBuffer.length) {
            currentEntry.body = entryBuffer.join('\n').trim();
            entries.push(currentEntry);
            entryBuffer = [];
          }

          const sectionTitle = line.slice(3).trim();
          if (['research', 'finding', 'lesson', 'decision', 'insight', 'pattern', 'key takeaway', 'benchmark'].some(kw => sectionTitle.toLowerCase().includes(kw))) {
            currentSection = sectionTitle;
          } else {
            currentSection = null;
          }
          continue;
        }

        if (line.startsWith('### ') && currentSection) {
          if (currentEntry && entryBuffer.length) {
            currentEntry.body = entryBuffer.join('\n').trim();
            entries.push(currentEntry);
            entryBuffer = [];
          }

          const entryTitle = line.slice(4).trim();
          currentEntry = {
            title: entryTitle,
            source: 'daily',
            file: `${dateStr}.md`,
            date: dateStr,
            section: currentSection
          };
          continue;
        }

        if (currentEntry !== null) {
          entryBuffer.push(line);
        }
      }

      if (currentEntry && entryBuffer.length) {
        currentEntry.body = entryBuffer.join('\n').trim();
        entries.push(currentEntry);
      }
    }

    info(`Parsed ${entries.length} entries from daily files (last ${daysBack} days)`);
    return entries;
  }

  extractAllEntries(daysBack = 7) {
    const allEntries = [...this.parseMemoryFile(), ...this.parseDailyFiles(daysBack)];

    // Deduplicate by content hash
    const seen = new Set();
    const uniqueEntries = [];
    for (const entry of allEntries) {
      const contentHash = crypto.createHash('md5').update(`${entry.title}|${entry.date || ''}|${(entry.body || '').slice(0, 200)}`).digest('hex').slice(0, 16);
      if (!seen.has(contentHash)) {
        seen.add(contentHash);
        entry.content_hash = contentHash;
        uniqueEntries.push(entry);
      }
    }

    info(`Total unique knowledge entries: ${uniqueEntries.length}`);
    return uniqueEntries;
  }
}

// ============ CLASSIFIER (unchanged) ============
class EntryClassifier {
  constructor() {
    this.TYPE_KEYWORDS = {
      'Research': ['research', 'benchmark', 'analysis', 'comparison', 'technical deep dive', 'performance', 'detailed breakdown'],
      'Lesson': ['lesson', 'learned', 'mistake', 'error', 'issue', 'problem', 'fixed', 'resolved', 'blocker'],
      'Decision': ['decision', 'choose', 'selected', 'opted', 'concluded', 'determined', 'agreed', 'strategy'],
      'Pattern': ['pattern', 'trend', 'recurring', 'common', 'usually', 'typically', 'observation'],
      'Tutorial': ['how to', 'tutorial', 'guide', 'step', 'instruction', 'walkthrough', 'setup', 'configure'],
      'Reference': ['reference', 'cheatsheet', 'spec', 'specification', 'documentation', 'api', 'quick reference'],
      'Insight': ['insight', 'realized', 'noticed', 'observed', 'thought', 'idea', 'aha', 'epiphany']
    };

    this.DOMAIN_KEYWORDS = {
      'AI Models': ['model', 'llm', 'gpt', 'claude', 'gemini', 'stepflash', 'deepseek', 'mimo', 'devstral', 'openrouter', 'free tier', 'notion'],
      'OpenClaw': ['openclaw', 'agent', 'workflow', 'skill', 'tool', 'automation', 'sync', 'database'],
      'Cost Optimization': ['cost', 'price', '$', 'budget', 'free', 'tier', 'routing', 'saving', 'optimization', 'value'],
      'Trading': ['trading', 'invest', 'stock', 'crypto', 'nft', 'web3', 'defi', 'bitcoin', 'ethereum'],
      'Learning': ['learn', 'study', 'japanese', 'language', 'course', 'tutorial', 'duolingo'],
      'Process': ['process', 'workflow', 'method', 'procedure', 'system', 'framework']
    };

    this.CERTAINTY_PHRASES = {
      'Verified': ['proven', 'confirmed', 'tested', 'verified', 'measured', 'data shows', 'benchmark result'],
      'Likely': ['likely', 'probably', 'most likely', 'seems', 'appears', 'suggest'],
      'Speculative': ['maybe', 'might', 'could', 'possibly', 'hypothesis', 'guess', 'uncertain'],
      'Opinion': ['i think', 'believe', 'feel', 'in my view', 'personally', 'prefer']
    };

    this.IMPACT_INDICATORS = {
      'High': ['critical', 'important', 'must', 'essential', 'key', 'major', 'significant', 'game changer'],
      'Medium': ['relevant', 'useful', 'helpful', 'worth', 'good', 'beneficial'],
      'Low': ['minor', 'small', 'slight', 'marginal', 'nice to have'],
      'Negligible': ['negligible', 'tiny', 'minimal', 'barely', 'insignificant']
    };
  }

  classifyType(title, body) {
    const text = (title + ' ' + body).toLowerCase();
    for (const [ctype, keywords] of Object.entries(this.TYPE_KEYWORDS)) {
      if (keywords.some(kw => text.includes(kw))) return ctype;
    }
    return 'Insight';
  }

  classifyDomain(title, body) {
    const text = (title + ' ' + body).toLowerCase();
    for (const [domain, keywords] of Object.entries(this.DOMAIN_KEYWORDS)) {
      if (keywords.some(kw => text.includes(kw))) return domain;
    }
    return 'General';
  }

  classifyCertainty(body) {
    const text = body.toLowerCase();
    for (const [certainty, phrases] of Object.entries(this.CERTAINTY_PHRASES)) {
      if (phrases.some(phrase => text.includes(phrase))) return certainty;
    }
    return 'Verified';
  }

  classifyImpact(title, body) {
    const text = (title + ' ' + body).toLowerCase();
    for (const [impact, indicators] of Object.entries(this.IMPACT_INDICATORS)) {
      if (indicators.some(ind => text.includes(ind))) return impact;
    }
    return 'Medium';
  }

  extractTags(title, body, section) {
    const tags = [];
    const text = (title + ' ' + body + ' ' + section).toLowerCase();

    const keywordMap = {
      'AI': ['ai', 'artificial intelligence', 'ml', 'machine learning', 'model'],
      'OpenRouter': ['openrouter', 'router', 'provider', 'stepfun', 'moonshot', 'xiaomi', 'mistral'],
      'FreeTier': ['free', 'free tier', 'no cost'],
      'Benchmark': ['benchmark', 'test', 'score', 'performance', 'swe-bench', 'aime'],
      'Cost': ['cost', 'price', '$', 'pricing', 'budget', 'optimization'],
      'Automation': ['automation', 'auto', 'script', 'workflow', 'agent', 'tool'],
      'Coding': ['code', 'programming', 'development', 'swe', 'coding'],
      'Notion': ['notion', 'database', 'knowledge base', 'sync'],
      'Decision': ['decision', 'choose', 'selected', 'strategy']
    };

    for (const [tag, words] of Object.entries(keywordMap)) {
      if (words.some(w => text.includes(w))) tags.push(tag);
    }

    return [...new Set(tags)].slice(0, 7);
  }

  estimateConfidence(title, body, source) {
    let score = 7;
    if (source === 'MEMORY.md') score += 1;
    if ((body || '').length > 500) score += 1;
    if (['data', 'benchmark', 'measured', 'tested'].some(w => (body || '').toLowerCase().includes(w))) score += 1;
    return Math.min(10, Math.max(1, score));
  }

  classify(entry) {
    const { title, body } = entry;
    const meta = {
      content_type: this.classifyType(title, body),
      domain: this.classifyDomain(title, body),
      certainty: this.classifyCertainty(body),
      impact: this.classifyImpact(title, body),
      confidence_score: this.estimateConfidence(title, body, entry.source),
      tags: this.extractTags(title, body, entry.section || ''),
      source: entry.source || 'Manual'
    };
    entry.metadata = meta;
    return entry;
  }
}

// ============ LOCAL STORAGE MANAGER ============
class LocalStorageManager {
  constructor(workspace) {
    this.workspace = workspace;
    this.state = this.loadState();
  }

  loadState() {
    try {
      if (fs.existsSync(STATE_FILE)) {
        return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
      }
    } catch (e) {
      warning(`Failed to load state: ${e.message}`);
    }
    return {};
  }

  saveState() {
    try {
      fs.mkdirSync(MEMORY_DIR, { recursive: true });
      fs.writeFileSync(STATE_FILE, JSON.stringify(this.state, null, 2));
    } catch (e) {
      error(`Failed to save state: ${e.message}`);
    }
  }

  logAction(action, details) {
    const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19) + ' UTC';
    const logEntry = `- ${timestamp}: ${action} - ${details}\n`;
    fs.mkdirSync(MEMORY_DIR, { recursive: true });
    fs.appendFileSync(SYNC_LOG, logEntry);
    info(`${action}: ${details}`);
  }

  // Sanitize filename: remove invalid chars, limit length, replace spaces
  sanitizeFilename(name) {
    return name
      .replace(/[<>:"/\\|?*\x00-\x1F]/g, '_')  // Replace invalid filesystem chars
      .replace(/\s+/g, '_')                     // Replace spaces with underscores
      .substring(0, 100);                       // Limit length
  }

  // Create timestamp prefix: YYYYMMDDTHHMM
  timestampPrefix() {
    const now = new Date();
    return now.toISOString().slice(0, 16).replace(/[-:T]/g, '');
  }

  // Build markdown file content
  buildMarkdown(entry) {
    const { title, body, source, file, date, section, content_hash, metadata } = entry;
    const { content_type, domain, certainty, impact, confidence_score, tags, source: meta_source } = metadata;

    // YAML frontmatter style metadata block
    const metaBlock = `---
title: "${title}"
content_type: "${content_type}"
domain: "${domain}"
certainty: "${certainty}"
impact: "${impact}"
confidence_score: ${confidence_score}
tags: [${tags.map(t => `"${t}"`).join(', ')}]
source: "${meta_source}"
source_file: "${file || 'unknown'}"
date: "${date || new Date().toISOString().split('T')[0]}"
content_hash: "${content_hash}"
---

`;

    return metaBlock + body;
  }

  storeEntry(entry, dryRun = false) {
    // Classify entry if not already classified
    const processedEntry = entry.metadata ? entry : this.ensureMetadata(entry);
    const meta = processedEntry.metadata;
    const content_hash = processedEntry.content_hash;

    // Check if already synced
    if (this.state[content_hash]) {
      const existingPath = this.state[content_hash];
      info(`SKIP (already synced): ${processedEntry.title} -> ${existingPath}`);
      return existingPath;
    }

    // Determine target folder (create if missing)
    const folderName = meta.content_type;
    const folderPath = path.join(this.workspace, folderName);
    if (!fs.existsSync(folderPath)) {
      fs.mkdirSync(folderPath, { recursive: true });
      info(`Created folder: ${folderPath}`);
    }

    // Build filename: timestamp + title + content_hash prefix to avoid collisions
    const ts = this.timestampPrefix();
    const safeTitle = this.sanitizeFilename(processedEntry.title);
    const hashPrefix = processedEntry.content_hash.slice(0, 8); // first 8 chars of hash
    const filename = `${ts}_${safeTitle}_${hashPrefix}.md`;
    const filepath = path.join(folderPath, filename);

    if (dryRun) {
      this.logAction('DRY-RUN', `Would create: ${filename} (${meta.content_type})`);
      info(`  Title: ${processedEntry.title}`);
      info(`  Domain: ${meta.domain}, Confidence: ${meta.confidence_score}, Impact: ${meta.impact}`);
      info(`  Tags: ${meta.tags.join(', ')}`);
      info(`  Body length: ${(processedEntry.body || '').length}`);
      return null;
    }

    // Write file
    const content = this.buildMarkdown(processedEntry);
    fs.writeFileSync(filepath, content, 'utf-8');
    this.logAction('CREATED', `${filename} (${meta.content_type})`);

    // Update state
    this.state[content_hash] = filepath;
    this.saveState();

    return filepath;
  }

  ensureMetadata(entry) {
    if (!entry.metadata) {
      // Should have been classified already, but safeguard
      const classifier = new EntryClassifier();
      entry = classifier.classify(entry);
    }
    return entry;
  }

  cleanupOrphans(dryRun = false) {
    info('Scanning for orphan files...');

    // Build set of all files under content type folders
    const allFiles = new Set();
    for (const ct of CONTENT_TYPES) {
      const folder = path.join(this.workspace, ct);
      if (fs.existsSync(folder)) {
        const files = fs.readdirSync(folder).filter(f => f.endsWith('.md'));
        for (const f of files) {
          allFiles.add(path.join(folder, f));
        }
      }
    }

    // Files tracked in state
    const trackedFiles = new Set(Object.values(this.state));

    // Orphans = files on disk not in state
    const orphanFiles = [...allFiles].filter(f => !trackedFiles.has(f));

    info(`Found ${allFiles.size} knowledge files on disk`);
    info(`State tracks ${trackedFiles.size} files`);
    info(`Found ${orphanFiles.length} orphan files to archive`);

    if (dryRun) {
      info('DRY-RUN: would delete these files:');
      for (const f of orphanFiles) info(`  - ${f}`);
      return;
    }

    for (const f of orphanFiles) {
      try {
        fs.unlinkSync(f);
        this.logAction('ARCHIVED_ORPHAN', `deleted ${f}`);
      } catch (e) {
        error(`Error deleting ${f}: ${e}`);
        this.logAction('ARCHIVE_ERROR', `file ${f}: ${e.message}`);
      }
    }
  }

  /**
   * Generate index files for each content type folder.
   * Each index lists all entry files with metadata and links.
   */
  generateIndex(outputDir = null) {
    const targetDir = outputDir || this.workspace;
    info(`Generating index files in ${targetDir}`);

    // Ensure target directory exists
    fs.mkdirSync(targetDir, { recursive: true });

    // For each content type, create an index
    for (const ct of CONTENT_TYPES) {
      const folderPath = path.join(this.workspace, ct);
      if (!fs.existsSync(folderPath)) {
        debug(`Skipping ${ct}: folder not found`);
        continue;
      }

      const files = fs.readdirSync(folderPath)
        .filter(f => f.endsWith('.md'))
        .sort((a, b) => {
          // Sort by timestamp prefix (filename starts with YYYYMMDDTHHMM)
          return a.localeCompare(b);
        });

      if (files.length === 0) {
        debug(`Skipping ${ct}: no markdown files`);
        continue;
      }

      // Build index content
      let content = `# ${ct} Knowledge Index\n\n`;
      content += `**Generated:** ${new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC\n`;
      content += `**Total Entries:** ${files.length}\n\n`;
      content += `---\n\n`;
      content += `## Entries\n\n`;
      content += `| File | Title | Domain | Confidence | Impact | Tags |\n`;
      content += `|------|-------|--------|------------|--------|------|\n`;

      for (const file of files) {
        const filepath = path.join(folderPath, file);
        let entryData = { title: file, domain: '-', confidence: '-', impact: '-', tags: '-' };

        try {
          const contentText = fs.readFileSync(filepath, 'utf-8');
          // Parse YAML frontmatter
          const frontmatterMatch = contentText.match(/^---\n([\s\S]*?)\n---/);
          if (frontmatterMatch) {
            const fm = frontmatterMatch[1];
            const titleMatch = fm.match(/^title:\s*"([^"]+)"/m);
            const domainMatch = fm.match(/^domain:\s*"([^"]+)"/m);
            const confidenceMatch = fm.match(/^confidence_score:\s*(\d+)/m);
            const impactMatch = fm.match(/^impact:\s*"([^"]+)"/m);
            const tagsMatch = fm.match(/^tags:\s*\[([\s\S]*?)\]/m);

            if (titleMatch) entryData.title = titleMatch[1];
            if (domainMatch) entryData.domain = domainMatch[1];
            if (confidenceMatch) entryData.confidence = confidenceMatch[1];
            if (impactMatch) entryData.impact = impactMatch[1];
            if (tagsMatch) {
              try {
                const tagsArray = eval(`[${tagsMatch[1]}]`); // Safe since we control the format
                entryData.tags = tagsArray.join(', ');
              } catch (e) {
                entryData.tags = tagsMatch[1];
              }
            }
          }
        } catch (e) {
          // Use filename if can't parse
        }

        // Create relative link from workspace
        const relPath = path.relative(this.workspace, filepath);
        content += `| [${file}](${relPath}) | ${entryData.title} | ${entryData.domain} | ${entryData.confidence} | ${entryData.impact} | ${entryData.tags} |\n`;
      }

      content += `\n---\n\n*Last updated: ${new Date().toISOString().replace('T', ' ').substring(0, 19)} UTC*\n`;

      // Write index file
      const indexFilename = `${ct}_Index.md`;
      const indexPath = path.join(targetDir, indexFilename);
      fs.writeFileSync(indexPath, content, 'utf-8');
      info(`Created index: ${indexFilename} (${files.length} entries)`);
    }

    info('Index generation complete!');
  }
}

// ============ MAIN ORCHESTRATOR ============
class LocalOrchestrator {
  constructor(parser, classifier, storage) {
    this.parser = parser;
    this.classifier = classifier;
    this.storage = storage;
  }

  sync(daysBack = 7, dryRun = false, limit = null, cleanup = false) {
    info('='.repeat(60));
    info(`Starting local sync: days_back=${daysBack}, dry_run=${dryRun}, limit=${limit || 'none'}, cleanup=${cleanup}`);
    info('='.repeat(60));

    const entries = this.parser.extractAllEntries(daysBack);
    const entriesToProcess = limit ? entries.slice(0, limit) : entries;

    info(`Processing ${entriesToProcess.length} entries...`);

    const stats = { created: 0, updated: 0, failed: 0 };
    for (let i = 0; i < entriesToProcess.length; i++) {
      const entry = entriesToProcess[i];
      info(`[${i + 1}/${entriesToProcess.length}] Processing: ${entry.title || 'Unknown'}`);
      try {
        // Classify if not yet
        const processedEntry = entry.metadata ? entry : this.classifier.classify(entry);
        const filepath = this.storage.storeEntry(processedEntry, dryRun);
        if (filepath) {
          stats.created++;
        } else {
          stats.failed++;
        }
      } catch (e) {
        error(`Error processing entry: ${e.message}`);
        stats.failed++;
      }
    }

    if (cleanup && !dryRun) {
      this.storage.cleanupOrphans(false);
    } else if (cleanup && dryRun) {
      this.storage.cleanupOrphans(true);
    }

    info('='.repeat(60));
    info('Sync completed!');
    info(`  Created: ${stats.created}`);
    info(`  Updated: ${stats.updated}`);
    info(`  Failed:  ${stats.failed}`);
    info('='.repeat(60));
  }
}

// ============ MAIN ============
function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.verbose) {
    // verbose logging enabled via log function check
  }

  // Initialize components
  const parser = new MemoryParser(WORKSPACE);
  const classifier = new EntryClassifier();
  const storage = new LocalStorageManager(OUTPUT_DIR);
  const orchestrator = new LocalOrchestrator(parser, classifier, storage);

  switch (args.tool) {
    case 'sync':
      orchestrator.sync(
        args.days_back || 7,
        args.dry_run || false,
        args.limit || null,
        args.cleanup || false
      );
      return { success: true };

    case 'classify':
      const entries = parser.extractAllEntries(args.days_back || 0);
      const classified = entries.map(e => classifier.classify(e));
      console.log(JSON.stringify(classified, null, 2));
      return { success: true, count: classified.length };

    case 'list_types':
      console.log(`Available content types: ${CONTENT_TYPES.join(', ')}`);
      return { success: true };

    case 'cleanup':
      const dryRunCleanup = args.dry_run || false;
      storage.cleanupOrphans(dryRunCleanup);
      return { success: true };

    case 'summarize':
      const outputDir = args.output_dir || OUTPUT_DIR;
      storage.generateIndex(outputDir);
      return { success: true };

    case 'query':
      return { success: true, message: 'Query not yet implemented' };

    default:
      // If no tool specified or unknown, show help
      if (!args.tool) {
        console.log(`
Knowledge Management Skill (Local Storage)
Usage: km <tool> [options]

Input Workspace (where MEMORY.md and memory/ live) - detected automatically:
  1. OPENCLAWORKSPACE environment variable
  2. --workspace <path> CLI argument
  3. Current working directory (pwd) - 'cd /path/to/workspace && km ...'
  4. Default: ~/.openclaw/workspace

Output Directory (where Research/, Decision/, etc. are stored):
  --output-dir <path>  - Override default output location
                       - Default: <workspace>/memory/KM
                       - Can be absolute or relative to workspace

Tools:
  sync       - Sync memory entries to output directory
  classify   - Parse and classify without storing (JSON output)
  summarize  - Generate index files in output directory
  cleanup    - Remove orphaned files from output directory
  list_types - List all available content types

Global Options:
  --workspace <path>   - Input workspace (where source files are)
  --output-dir <path>  - Output directory for organized files (default: memory/KM)

Options (sync):
  --days_back <num>  - How many days of daily files to include (default: 7)
  --dry_run          - Preview without creating files
  --limit <num>      - Max entries to process
  --cleanup          - Archive orphan files after sync

Options (classify):
  --days_back <num>  - 0 = only MEMORY.md, otherwise include daily files

Options (summarize):
  --output_dir <path> - Override where to write index files (default: output dir)

Options (cleanup):
  --dry_run          - Preview what would be deleted

Examples:
  # Use default locations (input at workspace root, output in memory/KM)
  km sync --days_back 7 --cleanup

  # Custom input and output
  km sync --workspace /custom/input --output-dir /custom/output

  # Dry run
  km sync --dry_run --days_back 1

  # Classify entries
  km classify --days_back 3 > entries.json

  # Generate indexes
  km summarize

  # Cleanup orphans
  km cleanup --dry_run

  # List content types
  km list_types
`);
        return { success: true };
      }
      error(`Unknown tool: ${args.tool}`);
      return { error: `Unknown tool: ${args.tool}` };
  }
}

// ============ HELPERS ============
function parseArgs(argv) {
  const args = { tool: null };
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg.startsWith('--')) {
      const key = arg.slice(2).replace(/-/g, '_');
      if (argv[i + 1] && !argv[i + 1].startsWith('--')) {
        args[key] = isNaN(argv[i + 1]) ? argv[i + 1] : parseInt(argv[i + 1], 10);
        i++;
      } else {
        args[key] = true;
      }
    } else if (!args.tool) {
      args.tool = arg;
    }
  }
  return args;
}

// ============ ENTRY POINT ============
if (require.main === module) {
  const result = main();
  if (result?.error) process.exit(1);
  if (result?.success) process.exit(0);
}

module.exports = { MemoryParser, EntryClassifier, LocalStorageManager, LocalOrchestrator };
