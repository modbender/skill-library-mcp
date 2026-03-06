#!/usr/bin/env node
/**
 * Manual Memory Promotion/Demotion
 * 
 * Move a section between tiers manually.
 * 
 * Usage:
 *   node promote.js --section "TextWeb" --from 2 --to 1
 *   node promote.js --section "LARC Framework" --from 1 --to 3
 *   node promote.js --list                  # list all sections by tier
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(process.env.HOME, '.openclaw/workspace');
const TIER_FILES = {
  1: path.join(WORKSPACE, 'MEMORY.md'),
  2: path.join(WORKSPACE, 'memory/tier2-recent.md'),
  3: path.join(WORKSPACE, 'memory/tier3-archive.md'),
};

function parseSections(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const sections = [];
    let current = null;
    
    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(/^(#{2,3})\s+(.+)/);
      if (match) {
        if (current) {
          current.endLine = i;
          current.content = lines.slice(current.startLine, i).join('\n').trimEnd();
          sections.push(current);
        }
        current = { title: match[2].trim(), level: match[1].length, startLine: i, endLine: null, content: '' };
      }
    }
    if (current) {
      current.endLine = lines.length;
      current.content = lines.slice(current.startLine).join('\n').trimEnd();
      sections.push(current);
    }
    return { content, lines, sections };
  } catch {
    return { content: '', lines: [], sections: [] };
  }
}

function listSections() {
  console.log('📋 All Memory Sections\n');
  for (const [tier, file] of Object.entries(TIER_FILES)) {
    const { sections } = parseSections(file);
    const tierName = tier === '1' ? 'Tier 1 (Hot)' : tier === '2' ? 'Tier 2 (Warm)' : 'Tier 3 (Cold)';
    console.log(`${tierName}:`);
    if (sections.length === 0) {
      console.log('  (empty)');
    } else {
      for (const s of sections) {
        console.log(`  • ${s.title}`);
      }
    }
    console.log();
  }
}

function moveSection(sectionTitle, fromTier, toTier) {
  const from = parseSections(TIER_FILES[fromTier]);
  const section = from.sections.find(s => 
    s.title.toLowerCase().includes(sectionTitle.toLowerCase())
  );
  
  if (!section) {
    console.error(`❌ Section "${sectionTitle}" not found in Tier ${fromTier}`);
    console.error('Available sections:');
    for (const s of from.sections) {
      console.error(`  • ${s.title}`);
    }
    process.exit(1);
  }
  
  // Remove from source
  const sourceLines = from.lines.slice();
  sourceLines.splice(section.startLine, section.endLine - section.startLine);
  const cleanedSource = sourceLines.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  
  // Add to destination
  const dest = fs.readFileSync(TIER_FILES[toTier], 'utf8');
  const destLines = dest.split('\n');
  
  // Insert before Index section (Tier 1) or at end
  let insertIdx = destLines.length;
  for (let i = destLines.length - 1; i >= 0; i--) {
    if (destLines[i].match(/^## Index/)) {
      insertIdx = i;
      break;
    }
  }
  
  destLines.splice(insertIdx, 0, '', section.content, '');
  const cleanedDest = destLines.join('\n').replace(/\n{3,}/g, '\n\n').trim() + '\n';
  
  fs.writeFileSync(TIER_FILES[fromTier], cleanedSource);
  fs.writeFileSync(TIER_FILES[toTier], cleanedDest);
  
  const action = toTier < fromTier ? '📈 Promoted' : '📉 Demoted';
  console.log(`${action} "${section.title}" from Tier ${fromTier} → Tier ${toTier}`);
}

function main() {
  const args = process.argv.slice(2);
  
  if (args.includes('--list') || args.length === 0) {
    listSections();
    return;
  }
  
  let section = null, from = null, to = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--section') section = args[++i];
    if (args[i] === '--from') from = parseInt(args[++i]);
    if (args[i] === '--to') to = parseInt(args[++i]);
  }
  
  if (!section || !from || !to) {
    console.error('Usage: node promote.js --section "Title" --from <tier> --to <tier>');
    console.error('       node promote.js --list');
    process.exit(1);
  }
  
  if (![1, 2, 3].includes(from) || ![1, 2, 3].includes(to)) {
    console.error('Tiers must be 1, 2, or 3');
    process.exit(1);
  }
  
  moveSection(section, from, to);
}

main();
