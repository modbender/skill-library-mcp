#!/usr/bin/env node
/**
 * innovation-catalyst v4.0
 * Analyzes system state and proposes strategic innovations to break plateaus.
 * Now with ADVANCED automation candidates.
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = process.cwd();
const SKILLS_DIR = path.join(WORKSPACE, 'skills');

// Utility to check if a skill exists
function skillExists(name) {
  return fs.existsSync(path.join(SKILLS_DIR, name));
}

// Innovation Candidates with dependencies
const CANDIDATES = [
  // Basic Security & Ops
  {
    id: 'dependency-scanner',
    name: 'Dependency Scanner',
    type: 'security',
    description: 'Scans package.json for vulnerable dependencies using npm audit.',
    condition: () => !skillExists('dependency-scanner') && !skillExists('security-sentinel'),
    priority: 'high'
  },
  {
    id: 'permission-auditor',
    name: 'Permission Auditor',
    type: 'security',
    description: 'Audits source code for high-risk permissions and tool usage.',
    condition: () => !skillExists('permission-auditor') && !skillExists('security-sentinel'),
    priority: 'high'
  },
  // Data & Knowledge
  {
    id: 'local-vector-store',
    name: 'Local Vector Store',
    type: 'data',
    description: 'Semantic search engine for local files using TF-IDF/Cosine similarity.',
    condition: () => !skillExists('local-vector-store'),
    priority: 'medium'
  },
  // Advanced Automation (v4.0 additions)
  {
    id: 'auto-pr-merger',
    name: 'Auto PR Merger',
    type: 'dev-ops',
    description: 'Automates checking out PRs, running tests, and merging if successful.',
    condition: () => !skillExists('auto-pr-merger'),
    priority: 'high'
  },
  {
    id: 'auto-test-generator',
    name: 'Auto Test Generator',
    type: 'dev',
    description: 'Scans skills and automatically generates basic unit tests.',
    condition: () => !skillExists('auto-test-generator') && !skillExists('skill-tester'),
    priority: 'medium'
  },
  {
    id: 'log-archiver',
    name: 'Log Archiver',
    type: 'ops',
    description: 'Rotates and compresses old log files to save disk space.',
    condition: () => !skillExists('log-archiver'),
    priority: 'low'
  },
  {
    id: 'workspace-cleaner',
    name: 'Workspace Cleaner',
    type: 'ops',
    description: 'Automated cleanup of temporary files and orphaned directories.',
    condition: () => !skillExists('workspace-cleaner'),
    priority: 'low'
  },
  // New Candidates (v5.0)
  {
    id: 'github-issue-manager',
    name: 'GitHub Issue Manager',
    type: 'workflow',
    description: 'Manage GitHub Issues (create, list, comment, close) via gh CLI.',
    condition: () => !skillExists('github-issue-manager'),
    priority: 'high'
  },
  {
    id: 'video-tools',
    name: 'Video Tools',
    type: 'media',
    description: 'Advanced video manipulation (cut, merge, watermark) using FFmpeg.',
    condition: () => !skillExists('video-tools') && !skillExists('video-editor'),
    priority: 'medium'
  },
  {
    id: 'audio-transcriber',
    name: 'Audio Transcriber',
    type: 'media',
    description: 'Transcribe audio files to text using local or API-based Whisper models.',
    condition: () => !skillExists('audio-transcriber'),
    priority: 'medium'
  },
  {
    id: 'web-monitor',
    name: 'Web Monitor',
    type: 'data',
    description: 'Monitor web pages for content changes and alert on updates.',
    condition: () => !skillExists('web-monitor') && !skillExists('web-change-monitor'),
    priority: 'low'
  }
];

function analyze() {
  console.log('🔍 Innovation Catalyst v4.0 analyzing workspace...');
  
  const suggestions = CANDIDATES.filter(c => c.condition());
  
  if (suggestions.length === 0) {
    console.log('✅ All known innovation gaps filled. System is at peak capability density.');
    console.log('- Consider purely creative tasks or manual overrides.');
    return;
  }

  console.log(`💡 Found ${suggestions.length} potential innovations to break stagnation:\n`);
  
  suggestions.forEach(s => {
    console.log(`[${s.type.toUpperCase()}] ${s.name} (${s.priority})`);
    console.log(`   Description: ${s.description}`);
    console.log(`   Idea: Implement 'skills/${s.id}' to fill this gap.\n`);
  });

  // Output specifically for the Evolver to capture
  const topPick = suggestions.find(s => s.priority === 'high') || suggestions[0];
  if (topPick) {
    console.log(`RECOMMENDATION: Implement '${topPick.id}' to improve system ${topPick.type}.`);
  }
}

// CLI handler
if (require.main === module) {
  try {
    analyze();
  } catch (error) {
    console.error('Analysis failed:', error.message);
    process.exit(1);
  }
}

module.exports = { analyze };
