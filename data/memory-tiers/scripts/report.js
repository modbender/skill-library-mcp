#!/usr/bin/env node
/**
 * Memory Tier Health Report
 * 
 * Shows current state of all tiers: sizes, section counts, staleness,
 * access frequency, and recommendations.
 * 
 * Usage: node report.js [--json]
 */

const fs = require('fs');
const path = require('path');

const WORKSPACE = path.join(process.env.HOME, '.openclaw/workspace');
const STATE_DIR = path.join(__dirname, '..', 'state');
const ACCESS_LOG = path.join(STATE_DIR, 'access-log.json');

const TIER_FILES = {
  1: { path: path.join(WORKSPACE, 'MEMORY.md'), name: 'Tier 1 (Hot)', maxLines: 100 },
  2: { path: path.join(WORKSPACE, 'memory/tier2-recent.md'), name: 'Tier 2 (Warm)', maxLines: 150 },
  3: { path: path.join(WORKSPACE, 'memory/tier3-archive.md'), name: 'Tier 3 (Cold)', maxLines: null },
};

function loadAccessLog() {
  try {
    return JSON.parse(fs.readFileSync(ACCESS_LOG, 'utf8'));
  } catch {
    return { files: {}, sections: {}, lastScanTime: null };
  }
}

function getFileStats(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const sections = lines.filter(l => l.match(/^#{2,3}\s/));
    const bytes = Buffer.byteLength(content);
    return { lines: lines.length, sections: sections.length, bytes, exists: true };
  } catch {
    return { lines: 0, sections: 0, bytes: 0, exists: false };
  }
}

function getSectionDetails(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    const sections = [];
    
    for (let i = 0; i < lines.length; i++) {
      const match = lines[i].match(/^(#{2,3})\s+(.+)/);
      if (match) {
        sections.push({
          title: match[2].trim(),
          level: match[1].length,
          line: i + 1,
        });
      }
    }
    return sections;
  } catch {
    return [];
  }
}

function getDailyLogStats() {
  const memDir = path.join(WORKSPACE, 'memory');
  try {
    const files = fs.readdirSync(memDir)
      .filter(f => f.match(/^\d{4}-\d{2}-\d{2}\.md$/))
      .sort();
    
    let totalLines = 0;
    for (const f of files) {
      const content = fs.readFileSync(path.join(memDir, f), 'utf8');
      totalLines += content.split('\n').length;
    }
    
    return {
      count: files.length,
      totalLines,
      oldest: files[0] || null,
      newest: files[files.length - 1] || null,
    };
  } catch {
    return { count: 0, totalLines: 0, oldest: null, newest: null };
  }
}

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes}B`;
  return `${(bytes / 1024).toFixed(1)}KB`;
}

function main() {
  const jsonMode = process.argv.includes('--json');
  const accessLog = loadAccessLog();
  const now = Date.now();
  
  const report = {
    timestamp: new Date().toISOString(),
    lastTrackingScan: accessLog.lastScanTime,
    tiers: {},
    dailyLogs: getDailyLogStats(),
    recommendations: [],
  };
  
  for (const [tier, info] of Object.entries(TIER_FILES)) {
    const stats = getFileStats(info.path);
    const sections = getSectionDetails(info.path);
    const normPath = info.path.replace(WORKSPACE + '/', '');
    const fileAccess = accessLog.files[normPath];
    
    // Find stalest section
    let stalestSection = null;
    let stalestDays = 0;
    
    for (const section of sections) {
      const key = `${normPath}#${section.title}`;
      const sectionAccess = accessLog.sections[key];
      if (sectionAccess) {
        const days = Math.round((now - new Date(sectionAccess.lastAccessed).getTime()) / (24 * 60 * 60 * 1000));
        if (days > stalestDays) {
          stalestDays = days;
          stalestSection = section.title;
        }
      }
    }
    
    report.tiers[tier] = {
      name: info.name,
      file: normPath,
      lines: stats.lines,
      maxLines: info.maxLines,
      overLimit: info.maxLines ? stats.lines > info.maxLines : false,
      sections: stats.sections,
      size: formatBytes(stats.bytes),
      lastAccessed: fileAccess?.lastAccessed || 'never',
      totalAccesses: fileAccess?.accessCount || 0,
      stalestSection,
      stalestDays,
      sectionList: sections.map(s => s.title),
    };
    
    // Generate recommendations
    if (info.maxLines && stats.lines > info.maxLines) {
      report.recommendations.push(
        `⚠️ ${info.name} is ${stats.lines} lines (limit ${info.maxLines}). Demote stale sections.`
      );
    }
    if (stalestDays > 7 && parseInt(tier) === 1) {
      report.recommendations.push(
        `📉 "${stalestSection}" in Tier 1 hasn't been accessed in ${stalestDays} days. Consider demoting.`
      );
    }
    if (stalestDays > 30 && parseInt(tier) === 2) {
      report.recommendations.push(
        `📉 "${stalestSection}" in Tier 2 hasn't been accessed in ${stalestDays} days. Consider archiving.`
      );
    }
  }
  
  if (!accessLog.lastScanTime) {
    report.recommendations.push(
      '🔍 No tracking data yet. Run `node track.js` to scan session transcripts.'
    );
  }
  
  if (jsonMode) {
    console.log(JSON.stringify(report, null, 2));
    return;
  }
  
  // Pretty print
  console.log('🧠 Memory Tier Health Report');
  console.log(`${'═'.repeat(60)}`);
  console.log(`Generated: ${report.timestamp}`);
  console.log(`Last tracking scan: ${report.lastTrackingScan || 'never'}`);
  console.log();
  
  for (const [tier, data] of Object.entries(report.tiers)) {
    const limitStr = data.maxLines ? ` / ${data.maxLines} max` : '';
    const overStr = data.overLimit ? ' ⚠️ OVER LIMIT' : '';
    console.log(`${'─'.repeat(60)}`);
    console.log(`${data.name}`);
    console.log(`  File: ${data.file}`);
    console.log(`  Size: ${data.lines} lines${limitStr}${overStr} (${data.size})`);
    console.log(`  Sections: ${data.sections}`);
    console.log(`  Accesses: ${data.totalAccesses} total`);
    console.log(`  Last accessed: ${data.lastAccessed}`);
    if (data.stalestSection) {
      console.log(`  Stalest: "${data.stalestSection}" (${data.stalestDays} days)`);
    }
    if (data.sectionList.length > 0) {
      console.log(`  Contents:`);
      for (const s of data.sectionList) {
        console.log(`    • ${s}`);
      }
    }
  }
  
  console.log(`\n${'─'.repeat(60)}`);
  console.log(`📝 Daily Logs: ${report.dailyLogs.count} files, ${report.dailyLogs.totalLines} lines`);
  if (report.dailyLogs.oldest) {
    console.log(`   Range: ${report.dailyLogs.oldest} → ${report.dailyLogs.newest}`);
  }
  
  if (report.recommendations.length > 0) {
    console.log(`\n${'─'.repeat(60)}`);
    console.log('💡 Recommendations:');
    for (const rec of report.recommendations) {
      console.log(`  ${rec}`);
    }
  }
  
  console.log();
}

main();
