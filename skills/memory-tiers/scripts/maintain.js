#!/usr/bin/env node
/**
 * Memory Tier Maintenance
 * 
 * Runs promotion/demotion logic based on access patterns:
 * - Tier 1 items not accessed in 7 days → demote to Tier 2
 * - Tier 2 items not accessed in 30 days → demote to Tier 3
 * - Tier 2/3 items accessed recently → promote up
 * 
 * Usage: node maintain.js [--dry-run] [--demote-days-t1 <7>] [--demote-days-t2 <30>]
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(process.env.HOME, '.openclaw/workspace');
const STATE_DIR = path.join(__dirname, '..', 'state');
const ACCESS_LOG = path.join(STATE_DIR, 'access-log.json');

const TIER_FILES = {
  1: path.join(WORKSPACE, 'MEMORY.md'),
  2: path.join(WORKSPACE, 'memory/tier2-recent.md'),
  3: path.join(WORKSPACE, 'memory/tier3-archive.md'),
};

function loadAccessLog() {
  try {
    return JSON.parse(fs.readFileSync(ACCESS_LOG, 'utf8'));
  } catch {
    return { files: {}, sections: {} };
  }
}

/**
 * Parse a tier file into sections
 * Returns array of { title, tier, content, startLine, endLine }
 */
function parseSections(filePath, tier) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const sections = [];
    let currentSection = null;
    let headerLines = []; // lines before first section
    
    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(/^(#{2,3})\s+(.+)/);
      if (match) {
        if (currentSection) {
          currentSection.endLine = i - 1;
          currentSection.content = lines.slice(currentSection.startLine, i).join('\n');
          sections.push(currentSection);
        } else {
          headerLines = lines.slice(0, i);
        }
        currentSection = {
          title: match[2].trim(),
          level: match[1].length,
          tier,
          startLine: i,
          endLine: null,
        };
      }
    }
    
    if (currentSection) {
      currentSection.endLine = lines.length - 1;
      currentSection.content = lines.slice(currentSection.startLine).join('\n');
      sections.push(currentSection);
    }
    
    return { header: headerLines.join('\n'), sections };
  } catch {
    return { header: '', sections: [] };
  }
}

/**
 * Get the last access time for a section
 */
function getLastAccess(accessLog, filePath, sectionTitle) {
  const normFile = filePath.replace(WORKSPACE + '/', '');
  
  // Check section-level access
  const sectionKey = `${normFile}#${sectionTitle}`;
  if (accessLog.sections[sectionKey]) {
    return new Date(accessLog.sections[sectionKey].lastAccessed).getTime();
  }
  
  // Fall back to file-level access
  if (accessLog.files[normFile]) {
    return new Date(accessLog.files[normFile].lastAccessed).getTime();
  }
  
  return 0; // never accessed
}

/**
 * Check if a section was recently promoted (accessed from a lower tier)
 */
function wasRecentlyAccessed(accessLog, sectionTitle, withinDays) {
  const cutoff = Date.now() - (withinDays * 24 * 60 * 60 * 1000);
  
  for (const [key, data] of Object.entries(accessLog.sections)) {
    if (key.includes(sectionTitle) && new Date(data.lastAccessed).getTime() > cutoff) {
      return true;
    }
  }
  return false;
}

function main() {
  const args = process.argv.slice(2);
  let dryRun = args.includes('--dry-run');
  let demoteDaysT1 = 7;
  let demoteDaysT2 = 30;
  
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--demote-days-t1') demoteDaysT1 = parseInt(args[++i]) || 7;
    if (args[i] === '--demote-days-t2') demoteDaysT2 = parseInt(args[++i]) || 30;
  }
  
  const accessLog = loadAccessLog();
  const now = Date.now();
  const t1Cutoff = now - (demoteDaysT1 * 24 * 60 * 60 * 1000);
  const t2Cutoff = now - (demoteDaysT2 * 24 * 60 * 60 * 1000);
  
  const actions = [];
  
  // Parse all tiers
  const tiers = {};
  for (const [tier, file] of Object.entries(TIER_FILES)) {
    tiers[tier] = parseSections(file, parseInt(tier));
  }
  
  // === DEMOTION: Tier 1 → Tier 2 (not accessed in 7 days) ===
  for (const section of tiers[1].sections) {
    // Skip structural sections (Index, metadata)
    if (section.title.includes('Index') || section.title.includes('Deeper Tiers')) continue;
    
    const lastAccess = getLastAccess(accessLog, TIER_FILES[1], section.title);
    if (lastAccess > 0 && lastAccess < t1Cutoff) {
      actions.push({
        action: 'demote',
        section: section.title,
        from: 1,
        to: 2,
        lastAccessed: new Date(lastAccess).toISOString(),
        daysSince: Math.round((now - lastAccess) / (24 * 60 * 60 * 1000)),
        content: section.content,
      });
    }
  }
  
  // === DEMOTION: Tier 2 → Tier 3 (not accessed in 30 days) ===
  for (const section of tiers[2].sections) {
    const lastAccess = getLastAccess(accessLog, TIER_FILES[2], section.title);
    if (lastAccess > 0 && lastAccess < t2Cutoff) {
      actions.push({
        action: 'demote',
        section: section.title,
        from: 2,
        to: 3,
        lastAccessed: new Date(lastAccess).toISOString(),
        daysSince: Math.round((now - lastAccess) / (24 * 60 * 60 * 1000)),
        content: section.content,
      });
    }
  }
  
  // === PROMOTION: Tier 2/3 → Tier 1 (accessed in last 24h) ===
  const promotionCutoff = now - (24 * 60 * 60 * 1000);
  
  for (const tier of [2, 3]) {
    for (const section of tiers[tier].sections) {
      const lastAccess = getLastAccess(accessLog, TIER_FILES[tier], section.title);
      if (lastAccess > promotionCutoff) {
        actions.push({
          action: 'promote',
          section: section.title,
          from: tier,
          to: 1,
          lastAccessed: new Date(lastAccess).toISOString(),
          content: section.content,
        });
      }
    }
  }
  
  // Report
  console.log(`Memory Tier Maintenance Report`);
  console.log(`${'─'.repeat(50)}`);
  console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE'}`);
  console.log(`Demote T1→T2 after: ${demoteDaysT1} days`);
  console.log(`Demote T2→T3 after: ${demoteDaysT2} days`);
  console.log(`Promote to T1 if accessed in: 24h`);
  console.log(`${'─'.repeat(50)}`);
  
  if (actions.length === 0) {
    console.log('\n✅ No actions needed — all tiers are current.');
    return;
  }
  
  const demotions = actions.filter(a => a.action === 'demote');
  const promotions = actions.filter(a => a.action === 'promote');
  
  if (demotions.length > 0) {
    console.log(`\n📉 Demotions (${demotions.length}):`);
    for (const d of demotions) {
      console.log(`  "${d.section}" T${d.from}→T${d.to} (${d.daysSince} days since access)`);
    }
  }
  
  if (promotions.length > 0) {
    console.log(`\n📈 Promotions (${promotions.length}):`);
    for (const p of promotions) {
      console.log(`  "${p.section}" T${p.from}→T${p.to} (accessed ${p.lastAccessed})`);
    }
  }
  
  if (dryRun) {
    console.log('\n🔍 Dry run — no changes made. Remove --dry-run to apply.');
    // Output JSON for programmatic use
    console.log(JSON.stringify({ actions }, null, 2));
    return;
  }
  
  // === APPLY CHANGES ===
  // Read current tier contents
  const tierContents = {};
  for (const [tier, file] of Object.entries(TIER_FILES)) {
    tierContents[tier] = fs.readFileSync(file, 'utf8');
  }
  
  for (const action of actions) {
    const content = action.content.trim();
    
    // Remove from source tier
    const sourceFile = TIER_FILES[action.from];
    tierContents[action.from] = tierContents[action.from].replace(content, '').replace(/\n{3,}/g, '\n\n');
    
    // Add to destination tier (before the last section or at end)
    const destFile = TIER_FILES[action.to];
    const destLines = tierContents[action.to].split('\n');
    
    // Find insertion point (before Index section for Tier 1, or at end)
    let insertIdx = destLines.length;
    for (let i = destLines.length - 1; i >= 0; i--) {
      if (destLines[i].match(/^## Index|^## ─/)) {
        insertIdx = i;
        break;
      }
    }
    
    destLines.splice(insertIdx, 0, '', content, '');
    tierContents[action.to] = destLines.join('\n');
  }
  
  // Write updated files
  for (const [tier, file] of Object.entries(TIER_FILES)) {
    // Clean up excessive blank lines
    const cleaned = tierContents[tier].replace(/\n{3,}/g, '\n\n').trim() + '\n';
    fs.writeFileSync(file, cleaned);
  }
  
  // Update maintenance timestamp in MEMORY.md header
  const memContent = fs.readFileSync(TIER_FILES[1], 'utf8');
  const updated = memContent.replace(
    /<!-- last_maintained: .+? -->/,
    `<!-- last_maintained: ${new Date().toISOString().split('T')[0]} -->`
  );
  fs.writeFileSync(TIER_FILES[1], updated);
  
  console.log(`\n✅ Applied ${actions.length} changes.`);
  
  // Save maintenance log
  const maintLog = path.join(STATE_DIR, 'maintenance-log.json');
  let history = [];
  try { history = JSON.parse(fs.readFileSync(maintLog, 'utf8')); } catch {}
  history.push({
    timestamp: new Date().toISOString(),
    actions: actions.map(a => ({ action: a.action, section: a.section, from: a.from, to: a.to })),
  });
  // Keep last 50 maintenance runs
  if (history.length > 50) history = history.slice(-50);
  fs.writeFileSync(maintLog, JSON.stringify(history, null, 2));
}

main();
