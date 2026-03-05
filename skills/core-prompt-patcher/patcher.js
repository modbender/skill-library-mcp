#!/usr/bin/env node

/**
 * Core Prompt Patcher v2.1 - Dynamic SOUL.md-Based Injector
 * 
 * Automatically syncs your workspace SOUL.md persona into OpenClaw's core system prompt
 * after updates. Detects OpenClaw version changes and adapts to new file structures.
 * 
 * General-purpose tool - works with any SOUL.md content.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const OPENCLAW_PACKAGE_ROOT = '/home/oki/.npm-global/lib/node_modules/openclaw';
const DIST_PLUGIN_SDK_DIR = path.join(OPENCLAW_PACKAGE_ROOT, 'dist', 'plugin-sdk');
const WORKSPACE_DIR = path.join(process.env.HOME || '/home/oki', '.openclaw', 'workspace');
const SOUL_FILE = path.join(WORKSPACE_DIR, 'SOUL.md');
const BACKUP_SUFFIX = '.soul-patcher-backup';
const STATE_FILE = path.join(__dirname, '.patcher-state.json');

// Patterns to match in the compiled JS (may vary by version)
const PROMPT_PATTERNS = [
  /"You are a personal assistant running inside OpenClaw\."/,
  /"You are an AI assistant\."/,
  /"You are a helpful assistant\."/,
  /"You are a [^"]*assistant[^"]*"\./
];

const TOOLING_SECTION_PATTERNS = [
  /"## Tooling",\s*"Tool availability/,
  /"## Tools",\s*"Tool availability/,
  /"## Capabilities",\s*"Tool/,
  /"## Available Tools"/
];

function log(msg, type = 'info') {
  const prefix = {
    info: 'ℹ',
    success: '✓',
    warning: '⚠',
    error: '✗'
  }[type] || '•';
  
  const colors = {
    info: '\x1b[36m',
    success: '\x1b[32m',
    warning: '\x1b[33m',
    error: '\x1b[31m',
    reset: '\x1b[0m'
  };
  
  console.log(`${colors[type]}${prefix} ${msg}${colors.reset}`);
}

function getOpenClawVersion() {
  try {
    const packageJson = path.join(OPENCLAW_PACKAGE_ROOT, 'package.json');
    const pkg = JSON.parse(fs.readFileSync(packageJson, 'utf-8'));
    return pkg.version || 'unknown';
  } catch (err) {
    return 'unknown';
  }
}

function loadState() {
  try {
    if (fs.existsSync(STATE_FILE)) {
      return JSON.parse(fs.readFileSync(STATE_FILE, 'utf-8'));
    }
  } catch (err) {
    log(`Failed to load state: ${err.message}`, 'warning');
  }
  return { lastOpenClawVersion: null, lastPatched: null, lastSoulHash: null };
}

function saveState(state) {
  try {
    fs.writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
  } catch (err) {
    log(`Failed to save state: ${err.message}`, 'warning');
  }
}

function hashContent(content) {
  // Simple hash function
  let hash = 0;
  for (let i = 0; i < content.length; i++) {
    const char = content.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return hash.toString(36);
}

function loadSoulPersona() {
  if (!fs.existsSync(SOUL_FILE)) {
    log('SOUL.md not found in workspace. Cannot patch without SOUL.md file.', 'error');
    log(`Expected location: ${SOUL_FILE}`, 'warning');
    return null;
  }
  
  try {
    const soulContent = fs.readFileSync(SOUL_FILE, 'utf-8');
    
    if (!soulContent || typeof soulContent !== 'string' || soulContent.trim().length === 0) {
      log('SOUL.md is empty. Please add your persona definition.', 'error');
      return null;
    }
    
    // Extract key sections from SOUL.md to convert into system prompt format
    const sections = extractPersonaSections(soulContent);
    
    if (!sections || sections.length === 0) {
      log('Could not extract persona sections from SOUL.md. Using full content.', 'warning');
      return formatFullSoulForInjection(soulContent);
    }
    
    return formatPersonaForInjection(sections);
  } catch (err) {
    log(`Failed to load SOUL.md: ${err.message}`, 'error');
    log(`Stack: ${err.stack}`, 'debug');
    return null;
  }
}

function extractPersonaSections(content) {
  if (!content || typeof content !== 'string') {
    return [];
  }
  
  const sections = [];
  
  // Extract headers and their content
  const headerRegex = /^##+\s+(.+)$/gm;
  const lines = content.split('\n');
  
  let currentSection = null;
  let currentContent = [];
  
  for (const line of lines) {
    const headerMatch = line.match(headerRegex);
    if (headerMatch && headerMatch[1]) {
      if (currentSection && currentContent.length > 0) {
        sections.push({
          title: currentSection,
          content: currentContent.join('\n').trim()
        });
      }
      currentSection = headerMatch[1].trim();
      currentContent = [];
    } else if (currentSection && line && line.trim()) {
      currentContent.push(line);
    }
  }
  
  // Push last section
  if (currentSection && currentContent.length > 0) {
    sections.push({
      title: currentSection,
      content: currentContent.join('\n').trim()
    });
  }
  
  // Filter to persona-relevant sections
  const personaKeywords = ['identity', 'personality', 'vibe', 'tone', 'directive', 'principle', 'behavior', 'response', 'language', 'core', 'who', 'what', 'how', 'guide', 'rule', 'trait', 'character', 'nature'];
  return sections.filter(s => {
    if (!s || !s.title || !s.content) return false;
    const titleLower = s.title.toLowerCase();
    const contentLower = s.content.toLowerCase();
    return personaKeywords.some(kw => titleLower.includes(kw)) ||
           personaKeywords.some(kw => contentLower.includes(kw));
  });
}

function formatFullSoulForInjection(content) {
  // Convert entire SOUL.md content to system prompt format
  const lines = [''];
  const contentLines = content.split('\n');
  
  for (const line of contentLines) {
    if (line.trim()) {
      lines.push(line.trim());
    }
  }
  lines.push('');
  
  // Convert to JavaScript string array format
  return lines.map(line => `"${line.replace(/"/g, '\\"')}"`).join(',\n') + ',\n';
}

function formatPersonaForInjection(sections) {
  if (!sections || sections.length === 0) {
    return null;
  }
  
  const lines = [''];
  
  for (const section of sections) {
    if (!section || !section.title) continue;
    
    lines.push(`## ${section.title.toUpperCase()}`);
    
    // Split content into lines and format each
    const contentStr = section.content || '';
    const contentLines = contentStr.split('\n');
    for (const line of contentLines) {
      if (line && line.trim()) {
        lines.push(line.trim());
      }
    }
    lines.push('');
  }
  
  // Convert to JavaScript string array format
  return lines.map(line => `"${line.replace(/"/g, '\\"')}"`).join(',\n') + ',\n';
}

function findReplyFile() {
  try {
    const files = fs.readdirSync(DIST_PLUGIN_SDK_DIR);
    const replyFile = files.find(f => f.startsWith('reply-') && f.endsWith('.js'));
    return replyFile ? path.join(DIST_PLUGIN_SDK_DIR, replyFile) : null;
  } catch (err) {
    return null;
  }
}

function backupFile(filePath) {
  const backupPath = filePath + BACKUP_SUFFIX;
  try {
    fs.copyFileSync(filePath, backupPath);
    log(`Backup created: ${backupPath}`, 'success');
    return true;
  } catch (err) {
    log(`Failed to create backup: ${err.message}`, 'error');
    return false;
  }
}

function checkPersonaExists(content, personaHash) {
  const state = loadState();
  return state.lastSoulHash === personaHash && 
         (content.includes('## CORE IDENTITY') || content.includes('## PERSONALITY') || content.includes('SOUL.md'));
}

function findInsertionPoint(content) {
  // Try each pattern
  for (const promptPattern of PROMPT_PATTERNS) {
    const match = content.match(new RegExp(`(${promptPattern.source})\\s*,\\s*""`));
    if (match) {
      // Verify tooling section exists nearby
      for (const toolPattern of TOOLING_SECTION_PATTERNS) {
        const toolMatch = content.match(toolPattern);
        if (toolMatch && toolMatch.index > match.index) {
          return match.index + match[0].length;
        }
      }
      // Return even without tooling verification
      return match.index + match[0].length;
    }
  }
  
  return null;
}

function injectPersona(content, personaInjection) {
  const insertionPoint = findInsertionPoint(content);
  
  if (!insertionPoint) {
    log('Could not find insertion point in core prompt', 'error');
    log('OpenClaw may have changed its prompt structure.', 'warning');
    return { modified: false, content: null };
  }

  // Inject persona
  const before = content.slice(0, insertionPoint);
  const after = content.slice(insertionPoint);
  
  const newContent = before + personaInjection + after;
  
  // Verify injection worked
  if (!newContent.includes('##') && !newContent.includes('SOUL.md')) {
    log('Persona injection verification failed', 'error');
    return { modified: false, content: null };
  }

  log('Persona successfully injected', 'success');
  return { modified: true, content: newContent };
}

function detectChanges() {
  const state = loadState();
  const currentVersion = getOpenClawVersion();
  const changes = {
    versionChanged: state.lastOpenClawVersion !== currentVersion,
    soulChanged: false,
    needsPatch: false
  };
  
  // Check if SOUL.md exists and changed
  if (fs.existsSync(SOUL_FILE)) {
    try {
      const soulContent = fs.readFileSync(SOUL_FILE, 'utf-8');
      const currentHash = hashContent(soulContent);
      changes.soulChanged = state.lastSoulHash !== currentHash;
    } catch (err) {
      log(`Failed to check SOUL.md: ${err.message}`, 'warning');
    }
  }
  
  // Determine if patch is needed
  changes.needsPatch = changes.versionChanged || changes.soulChanged;
  
  if (changes.versionChanged) {
    log(`OpenClaw version changed: ${state.lastOpenClawVersion || 'unknown'} → ${currentVersion}`, 'info');
  }
  
  if (changes.soulChanged) {
    log('SOUL.md content has changed', 'info');
  }
  
  return changes;
}

function patchCorePrompt(force = false) {
  log('Starting SOUL-based Core Prompt Patcher...', 'info');
  
  const state = loadState();
  const currentVersion = getOpenClawVersion();
  log(`Current OpenClaw version: ${currentVersion}`, 'info');
  
  // Detect changes
  const changes = detectChanges();
  
  if (!changes.needsPatch && !force) {
    log('No changes detected. Core prompt is up-to-date with SOUL.md', 'success');
    return true;
  }
  
  // Find the reply file
  const replyFile = findReplyFile();
  if (!replyFile) {
    log('Could not find reply-*.js file in dist/plugin-sdk', 'error');
    log(`Searched in: ${DIST_PLUGIN_SDK_DIR}`, 'warning');
    return false;
  }
  
  log(`Found core prompt file: ${path.basename(replyFile)}`, 'success');
  
  // Load persona from SOUL.md
  const personaInjection = loadSoulPersona();
  
  if (!personaInjection) {
    log('Failed to load persona from SOUL.md. Aborting patch.', 'error');
    return false;
  }
  
  const soulContent = fs.existsSync(SOUL_FILE) ? fs.readFileSync(SOUL_FILE, 'utf-8') : '';
  const personaHash = hashContent(soulContent);
  
  // Read the file
  let content;
  try {
    content = fs.readFileSync(replyFile, 'utf-8');
  } catch (err) {
    log(`Failed to read file: ${err.message}`, 'error');
    return false;
  }
  
  // Check if already patched with current persona
  if (checkPersonaExists(content, personaHash) && !force) {
    log('Core prompt already matches current SOUL.md', 'success');
    return true;
  }
  
  // Create backup
  if (!backupFile(replyFile)) {
    return false;
  }
  
  // Remove old persona if exists (for updates)
  if (content.includes('## CORE IDENTITY') || content.includes('## PERSONALITY') || content.includes('## SOUL')) {
    log('Removing old persona injection...', 'info');
    // Simple removal: find and remove between first persona section and ## Tooling
    const toolingMatch = content.match(/,\s*"## Tooling"/);
    if (toolingMatch) {
      const personaStart = content.indexOf('"## CORE IDENTITY"') || 
                          content.indexOf('"## PERSONALITY"') || 
                          content.indexOf('"## SOUL');
      if (personaStart > 0 && personaStart < toolingMatch.index) {
        content = content.slice(0, personaStart) + content.slice(toolingMatch.index + 1);
      }
    }
  }
  
  // Inject new persona
  const result = injectPersona(content, personaInjection);
  
  if (!result.modified || !result.content) {
    log('Persona injection failed', 'error');
    return false;
  }
  
  // Write the modified content
  try {
    fs.writeFileSync(replyFile, result.content, 'utf-8');
    log(`Core prompt patched with SOUL.md persona`, 'success');
    
    // Update state
    state.lastOpenClawVersion = currentVersion;
    state.lastPatched = new Date().toISOString();
    state.lastSoulHash = personaHash;
    saveState(state);
    
    return true;
  } catch (err) {
    log(`Failed to write patched file: ${err.message}`, 'error');
    // Try to restore backup
    try {
      fs.copyFileSync(replyFile + BACKUP_SUFFIX, replyFile);
      log('Restored backup', 'warning');
    } catch (restoreErr) {
      log(`Failed to restore backup: ${restoreErr.message}`, 'error');
    }
    return false;
  }
}

// Main execution
const args = process.argv.slice(2);
const force = args.includes('--force') || args.includes('-f');
const verbose = args.includes('--verbose') || args.includes('-v');

if (verbose) {
  const state = loadState();
  log(`State: ${JSON.stringify(state, null, 2)}`, 'info');
}

const success = patchCorePrompt(force);
process.exit(success ? 0 : 1);
