#!/usr/bin/env node

/**
 * Continuous Learning Analysis Script
 * Analyzes session patterns and generates optimization suggestions
 * 
 * Usage:
 *   node analyze.mjs         # Run analysis
 *   node analyze.mjs list    # Show optimizations
 *   node analyze.mjs instincts # Show instincts
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Determine workspace from script location
const SKILL_DIR = join(__dirname, '..');
const WORKSPACE = join(SKILL_DIR, '..', '..', 'workspace');
const MEMORY_DIR = join(WORKSPACE, 'memory', 'learning');
const INSTINCTS_FILE = join(MEMORY_DIR, 'instincts.jsonl');
const PATTERNS_FILE = join(MEMORY_DIR, 'patterns.json');
const OPTIMIZATIONS_FILE = join(MEMORY_DIR, 'optimizations.json');

// Ensure directory exists
if (!existsSync(MEMORY_DIR)) {
  mkdirSync(MEMORY_DIR, { recursive: true });
}

// Initialize files if not exist
if (!existsSync(INSTINCTS_FILE)) {
  writeFileSync(INSTINCTS_FILE, '');
}
if (!existsSync(PATTERNS_FILE)) {
  writeFileSync(PATTERNS_FILE, JSON.stringify({ patterns: [] }, null, 2));
}
if (!existsSync(OPTIMIZATIONS_FILE)) {
  writeFileSync(OPTIMIZATIONS_FILE, JSON.stringify({ optimizations: [] }, null, 2));
}

// Pattern categories
const CATEGORIES = ['code_style', 'testing', 'git', 'debugging', 'workflow', 'communication'];

// Simple pattern detectors (can be expanded)
const PATTERN_DETECTORS = [
  { 
    id: 'prefer-typescript-strict',
    domain: 'code_style',
    trigger: 'when writing typescript',
    detection: ['strict', 'any type', 'unknown type']
  },
  {
    id: 'prefer-functional-components',
    domain: 'code_style',
    trigger: 'when writing react',
    detection: ['functional', 'useState', 'useEffect']
  },
  {
    id: 'use-yarn',
    domain: 'workflow',
    trigger: 'when installing packages',
    detection: ['yarn add', 'yarn install']
  },
  {
    id: 'commit-often',
    domain: 'git',
    trigger: 'when making changes',
    detection: ['git commit', 'commit -m']
  }
];

function loadPatterns() {
  try {
    return JSON.parse(readFileSync(PATTERNS_FILE, 'utf-8')).patterns || [];
  } catch {
    return [];
  }
}

function savePatterns(patterns) {
  writeFileSync(PATTERNS_FILE, JSON.stringify({ patterns }, null, 2));
}

function loadOptimizations() {
  try {
    return JSON.parse(readFileSync(OPTIMIZATIONS_FILE, 'utf-8')).optimizations || [];
  } catch {
    return [];
  }
}

function saveOptimizations(optimizations) {
  writeFileSync(OPTIMIZATIONS_FILE, JSON.stringify({ optimizations }, null, 2));
}

function addInstinct(id, domain, trigger, confidence = 0.3) {
  const instinct = {
    id,
    domain,
    trigger,
    confidence,
    source: 'session-observation',
    created: new Date().toISOString(),
    evidence: []
  };
  
  appendToFile(INSTINCTS_FILE, JSON.stringify(instinct) + '\n');
  console.log(`✓ Added instinct: ${id}`);
}

function appendToFile(file, content) {
  const existing = existsSync(file) ? readFileSync(file, 'utf-8') : '';
  writeFileSync(file, existing + content);
}

function analyzeSessions() {
  console.log('\n🧠 Continuous Learning - Session Analysis\n');
  console.log('═'.repeat(40));
  
  // Check memory files for patterns
  const memoryDir = join(WORKSPACE, 'memory');
  
  console.log('\n📊 Analyzing recent sessions...\n');
  
  // Generic optimizations based on session analysis
  // These are template suggestions - actual ones come from pattern detection
  const optimizations = [
    {
      id: 'optimize-cron-frequency',
      title: 'Review cron job frequency',
      description: 'Some cron jobs may run too frequently. Consider reducing to optimize API usage.',
      impact: 'high',
      effort: 'low',
      category: 'automation'
    },
    {
      id: 'memory-optimization',
      title: 'Enable semantic memory search',
      description: 'Use embedding models for better context recall in long sessions.',
      impact: 'high',
      effort: 'medium',
      category: 'memory'
    },
    {
      id: 'batch-operations',
      title: 'Batch similar operations',
      description: 'Group similar API calls or tasks to reduce overhead.',
      impact: 'medium',
      effort: 'low',
      category: 'performance'
    }
  ];
  
  // Save optimizations
  const existingOptimizations = loadOptimizations();
  const newOptimizations = [...existingOptimizations, ...optimizations];
  saveOptimizations(newOptimizations);
  
  console.log('\n📈 Analysis Complete\n');
  console.log('═'.repeat(40));
  console.log(`Patterns detected: ${patternsFound.length}`);
  console.log(`Optimizations generated: ${optimizations.length}`);
  console.log(`\nRun: node scripts/instincts.mjs list`);
  console.log(`Run: node scripts/optimizations.mjs list`);
  
  return { patternsFound, optimizations };
}

function listInstincts() {
  console.log('\n🧠 Learned Instincts\n');
  console.log('═'.repeat(40));
  
  try {
    const content = readFileSync(INSTINCTS_FILE, 'utf-8');
    const lines = content.trim().split('\n').filter(l => l);
    
    if (lines.length === 0) {
      console.log('No instincts learned yet.\n');
      return;
    }
    
    lines.forEach(line => {
      const instinct = JSON.parse(line);
      const conf = instinct.confidence || 0;
      const emoji = conf >= 0.7 ? '🟢' : conf >= 0.5 ? '🟡' : '🔴';
      console.log(`${emoji} ${instinct.id}`);
      console.log(`   Domain: ${instinct.domain} | Confidence: ${conf}`);
      console.log(`   Trigger: ${instinct.trigger}`);
      console.log('');
    });
    
    console.log(`Total: ${lines.length} instincts`);
  } catch (e) {
    console.log('No instincts learned yet.\n');
  }
}

function listOptimizations() {
  console.log('\n💡 Suggested Optimizations\n');
  console.log('═'.repeat(40));
  
  const optimizations = loadOptimizations();
  
  if (optimizations.length === 0) {
    console.log('No optimizations suggested yet.\n');
    return;
  }
  
  optimizations.forEach((opt, i) => {
    const impact = opt.impact === 'high' ? '🟢' : opt.impact === 'medium' ? '🟡' : '🔴';
    console.log(`${i + 1}. ${opt.title} ${impact}`);
    console.log(`   ${opt.description}`);
    console.log(`   Impact: ${opt.impact} | Effort: ${opt.effort}`);
    console.log('');
  });
  
  console.log(`Total: ${optimizations.length} optimizations`);
}

// CLI
const args = process.argv.slice(2);
const command = args[0] || 'analyze';

if (command === 'analyze') {
  analyzeSessions();
} else if (command === 'instincts') {
  listInstincts();
} else if (command === 'optimizations' || command === 'list') {
  listOptimizations();
} else if (command === 'help') {
  console.log('Usage:');
  console.log('  node analyze.mjs           # Analyze sessions');
  console.log('  node analyze.mjs instincts   # List instincts');
  console.log('  node analyze.mjs list       # List optimizations');
} else {
  console.log('Unknown command:', command);
}
