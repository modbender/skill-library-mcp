#!/usr/bin/env node
/**
 * Skill Auditor Report Formatter — Human-friendly, visual, fast to read
 * Usage: node format-report.js <json-file>
 */

const fs = require('fs');

const RISK_HEADER = {
  CLEAN:    '🟢 SAFE',
  LOW:      '🟢 LOW RISK',
  MEDIUM:   '⚠️ SOME RISK',
  HIGH:     '🔴 RISKY',
  CRITICAL: '🚫 DANGEROUS'
};

// Short, punchy capability descriptions
const CAP_SHORT = {
  'Makes network requests': '🌐 Connects to internet',
  'Accesses files outside skill directory': '📂 Reads your files',
  'Potential data exfiltration': '📤 Sends data out',
  'Executes shell commands': '⚙️ Runs system commands',
  'Uses obfuscation techniques': '🕵️ Hides its behavior',
  'Contains prompt injection attempts': '🧠 Hijacks your AI',
  'Attempts persistence mechanisms': '📌 Installs permanently',
  'Attempts privilege escalation': '🔓 Grabs extra access'
};

// Softer labels when behavior is disclosed/intent-matched
const CAP_SHORT_DISCLOSED = {
  'Makes network requests': '🌐 Connects to internet (disclosed)',
  'Accesses files outside skill directory': '📂 Reads your files (disclosed)',
  'Potential data exfiltration': '📤 Sends data out (disclosed)',
  'Executes shell commands': '⚙️ Runs system commands (disclosed)',
  'Uses obfuscation techniques': '🕵️ Uses encoding (disclosed)',
  'Contains prompt injection attempts': '🧠 Modifies AI behavior (disclosed)',
  'Attempts persistence mechanisms': '📌 Persistent changes (disclosed)',
  'Attempts privilege escalation': '🔓 Extra access (disclosed)'
};

// Check if a file is a license file
function isLicenseFile(filename) {
  const baseName = filename.toLowerCase();
  const licensePatterns = [
    /^license(\.txt|\.md)?$/,
    /.*-ofl\.txt$/,
    /^ofl\.txt$/,
    /^copying$/,
    /^notice$/
  ];
  return licensePatterns.some(pattern => pattern.test(baseName));
}

// Danger meter visual gauge
function dangerMeter(riskLevel, findingCount) {
  const levels = {
    CLEAN:    { fill: 0,  label: 'No Threat' },
    LOW:      { fill: 2,  label: 'Minimal' },
    MEDIUM:   { fill: 4,  label: 'Moderate' },
    HIGH:     { fill: 7,  label: 'High' },
    CRITICAL: { fill: 10, label: 'Severe' }
  };
  const l = levels[riskLevel] || levels.CLEAN;
  let fill = Math.min(10, l.fill + Math.floor(findingCount / 10));

  const colors = ['🟩','🟩','🟨','🟨','🟧','🟧','🟧','🔴','🔴','🔴'];
  const empty = '⬜';

  let bar = '';
  for (let i = 0; i < 10; i++) {
    bar += i < fill ? colors[i] : empty;
  }
  return `${bar} ${l.label}`;
}

function formatReport(report) {
  const lines = [];

  // ── Header ──
  const header = RISK_HEADER[report.riskLevel] || '❓ UNKNOWN';
  lines.push(`${header} — "${report.skill.name}"`);
  lines.push('');

  // ── Danger Meter ──
  lines.push(`Threat: ${dangerMeter(report.riskLevel, report.findingCount)}`);

  // ── Publisher ──
  if (report.reputation) {
    const r = report.reputation;
    const badge = r.tier === 'known' ? '✓' : '?';
    lines.push(`Publisher: [${badge}] ${r.publisher} — ${r.note}`);
    // Add GitHub profile link if source is from GitHub
    if (report.skill.source && report.skill.source.includes('github.com')) {
      try {
        const match = report.skill.source.match(/github\.com\/([^\/]+)/);
        if (match) {
          lines.push(`Profile: https://github.com/${match[1]}`);
        }
      } catch {}
    }
  }

  // ── Accuracy bar ──
  if (report.accuracyScore) {
    const s = report.accuracyScore;
    const filled = '●'.repeat(s.score);
    const empty = '○'.repeat(10 - s.score);
    let label;
    if (s.score >= 8) label = 'Honest';
    else if (s.score >= 5) label = 'Partly honest';
    else if (s.score >= 3) label = 'Misleading';
    else label = 'Deceptive';
    lines.push(`Accuracy: ${filled}${empty} ${s.score}/10 — ${label}`);
  }

  // ── Quick stats line ──
  lines.push(`Files: ${report.scan.fileCount} | Findings: ${report.findingCount}`);
  lines.push('');

  // ── Clean? Short exit ──
  if (report.riskLevel === 'CLEAN') {
    lines.push('✅ Does what it says, nothing suspicious.');
    return lines.join('\n');
  }

  // ── What it does (icons only, one line each) ──
  if (report.summary.actualCapabilities.length > 0) {
    // Determine which capabilities are fully intent-matched
    const capToCategories = {
      'Makes network requests': ['Network'],
      'Accesses files outside skill directory': ['File Access', 'Sensitive File Access'],
      'Potential data exfiltration': ['Data Exfiltration'],
      'Executes shell commands': ['Shell Execution'],
      'Uses obfuscation techniques': ['Obfuscation'],
      'Contains prompt injection attempts': ['Prompt Injection'],
      'Attempts persistence mechanisms': ['Persistence'],
      'Attempts privilege escalation': ['Privilege Escalation']
    };
    for (const cap of report.summary.actualCapabilities) {
      const cats = capToCategories[cap] || [];
      const catFindings = (report.findings || []).filter(f => cats.includes(f.category));
      const allMatched = catFindings.length > 0 && catFindings.every(f => f.intentMatch);
      if (allMatched) {
        lines.push(CAP_SHORT_DISCLOSED[cap] || `✓ ${cap} (disclosed)`);
      } else {
        lines.push(CAP_SHORT[cap] || `❓ ${cap}`);
      }
    }
    lines.push('');
  }

  // ── Where it connects ──
  if (report.summary.externalUrls.length > 0) {
    const domains = new Set();
    for (const url of report.summary.externalUrls) {
      try { domains.add(new URL(url).hostname); } catch { domains.add(url.substring(0, 50)); }
    }
    lines.push(`Connects to: ${[...domains].slice(0, 5).join(', ')}`);
    lines.push('');
  }

  // ── Group license file URL findings ──
  const licenseUrlFindings = [];
  const nonLicenseFindings = [];
  
  for (const finding of report.findings) {
    const fileName = finding.file.split('/').pop() || finding.file;
    if (finding.id === 'http-url' && isLicenseFile(fileName)) {
      licenseUrlFindings.push(finding);
    } else {
      nonLicenseFindings.push(finding);
    }
  }

  // ── Show license URL summary if any found ──
  if (licenseUrlFindings.length > 0) {
    const licenseUrls = licenseUrlFindings.map(f => f.snippet || '').filter(s => s);
    const domains = new Set();
    for (const url of licenseUrls) {
      try { 
        const domain = new URL(url.trim()).hostname;
        domains.add(domain);
      } catch { 
        // If not a valid URL, extract domain-like text
        const match = url.match(/([a-zA-Z0-9-]+\.[a-zA-Z]{2,})/);
        if (match) domains.add(match[1]);
      }
    }
    const domainList = [...domains].slice(0, 5).join(', ');
    lines.push(`🌐 ${licenseUrlFindings.length} URLs found in license/font files (${domainList})`);
    lines.push('⚠️ Documentation only — no executable network calls');
    lines.push('');
  }

  // ── Top 3 evidence snippets (most severe) from non-license findings ──
  const sorted = [...nonLicenseFindings].sort((a, b) => {
    const ord = { critical: 0, high: 1, medium: 2, low: 3 };
    return (ord[a.severity] ?? 99) - (ord[b.severity] ?? 99);
  });

  // Dedupe by category, pick worst from each
  const seenCats = new Set();
  const topFindings = [];
  for (const f of sorted) {
    if (seenCats.has(f.category)) continue;
    seenCats.add(f.category);
    topFindings.push(f);
    if (topFindings.length >= 3) break;
  }

  if (topFindings.length > 0) {
    lines.push('Evidence:');
    for (const f of topFindings) {
      const snip = f.snippet ? (f.snippet.length > 80 ? f.snippet.substring(0, 77) + '...' : f.snippet) : '';
      lines.push(`→ ${f.file}:${f.line}`);
      lines.push(`  ${snip}`);
    }
    lines.push('');
  }

  // ── Undisclosed capabilities ──
  if (report.accuracyScore && report.accuracyScore.undisclosed && report.accuracyScore.undisclosed.length > 0) {
    lines.push('⚠️ Not mentioned in description:');
    for (const u of report.accuracyScore.undisclosed) {
      lines.push(`  ${CAP_SHORT[u] || u}`);
    }
    lines.push('');
  }

  // ── Verdict ──
  switch (report.riskLevel) {
    case 'LOW':
      lines.push('→ Minor stuff. Probably fine.');
      break;
    case 'MEDIUM':
      lines.push('→ Check if the above makes sense for this skill.');
      break;
    case 'HIGH':
      lines.push('→ This does more than expected. Trust the source?');
      break;
    case 'CRITICAL':
      lines.push('→ This looks malicious. Don\'t install.');
      break;
  }

  // Reputation reminder
  if (report.reputation && report.reputation.tier === 'known' && report.riskLevel !== 'CLEAN') {
    lines.push('');
    lines.push(`ℹ️ ${report.reputation.publisher} is a known publisher, but known ≠ safe. Review findings above.`);
  } else if (report.reputation && report.reputation.tier === 'unknown') {
    lines.push('');
    lines.push('⚠️ Unknown publisher — extra caution recommended.');
  }

  return lines.join('\n');
}

function main() {
  const jsonFile = process.argv[2];
  if (!jsonFile) {
    console.error('Usage: node format-report.js <json-file>');
    process.exit(2);
  }
  const report = JSON.parse(fs.readFileSync(jsonFile, 'utf-8'));
  console.log(formatReport(report));
}

main();
