#!/usr/bin/env node
/**
 * Slither Integration for Solidity Guardian
 * Runs Slither analysis and merges results with Guardian findings.
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Check if Slither is installed
function checkSlither() {
  try {
    execSync('slither --version', { stdio: 'pipe' });
    return true;
  } catch {
    return false;
  }
}

// Install Slither
async function installSlither() {
  console.log('Installing Slither...');
  
  // Try different installation methods
  const methods = [
    'pipx install slither-analyzer',
    'pip3 install slither-analyzer',
    'python3 -m pip install slither-analyzer'
  ];
  
  for (const method of methods) {
    try {
      execSync(method, { stdio: 'inherit' });
      console.log('✅ Slither installed successfully');
      return true;
    } catch {
      continue;
    }
  }
  
  console.log('⚠️  Could not install Slither. Install manually:');
  console.log('   pip3 install slither-analyzer');
  console.log('   or: pipx install slither-analyzer');
  return false;
}

// Map Slither severity to Guardian severity
function mapSeverity(slitherImpact) {
  const mapping = {
    'High': 'critical',
    'Medium': 'high', 
    'Low': 'medium',
    'Informational': 'low',
    'Optimization': 'low'
  };
  return mapping[slitherImpact] || 'medium';
}

// Run Slither and get JSON output
function runSlither(projectPath, options = {}) {
  if (!checkSlither()) {
    console.log('Slither not found.');
    if (options.autoInstall) {
      if (!installSlither()) {
        return null;
      }
    } else {
      console.log('Run with --install-slither to auto-install, or install manually.');
      return null;
    }
  }
  
  const outputFile = path.join('/tmp', `slither-${Date.now()}.json`);
  
  try {
    // Run Slither with JSON output
    const cmd = `slither ${projectPath} --json ${outputFile} 2>/dev/null`;
    execSync(cmd, { 
      stdio: 'pipe',
      timeout: 300000, // 5 minute timeout
      cwd: projectPath.includes('/') ? path.dirname(projectPath) : process.cwd()
    });
  } catch (e) {
    // Slither exits with non-zero on findings, but still writes JSON
  }
  
  if (!fs.existsSync(outputFile)) {
    console.log('Slither did not produce output. Check if project compiles.');
    return null;
  }
  
  try {
    const results = JSON.parse(fs.readFileSync(outputFile, 'utf8'));
    fs.unlinkSync(outputFile); // Clean up
    return results;
  } catch (e) {
    console.log('Failed to parse Slither output:', e.message);
    return null;
  }
}

// Convert Slither findings to Guardian format
function convertSlitherFindings(slitherResults) {
  if (!slitherResults || !slitherResults.results || !slitherResults.results.detectors) {
    return [];
  }
  
  return slitherResults.results.detectors.map((detector, index) => {
    // Get first element location
    const firstElement = detector.elements?.[0];
    const sourceMapping = firstElement?.source_mapping;
    
    return {
      id: `SLITHER-${detector.check}`,
      title: detector.check.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      severity: mapSeverity(detector.impact),
      file: sourceMapping?.filename || 'unknown',
      line: sourceMapping?.lines?.[0] || 0,
      code: detector.first_markdown_element || '',
      description: detector.description,
      suggestion: detector.markdown || 'Review and fix the identified issue.',
      references: [`https://github.com/crytic/slither/wiki/Detector-Documentation#${detector.check}`],
      source: 'slither',
      confidence: detector.confidence
    };
  });
}

// Merge Slither findings with Guardian findings
function mergeFindings(guardianFindings, slitherFindings) {
  const merged = [...guardianFindings];
  
  // Add Slither findings, avoiding duplicates
  for (const sf of slitherFindings) {
    // Check for similar finding at same location
    const isDuplicate = guardianFindings.some(gf => 
      gf.file === sf.file && 
      Math.abs(gf.line - sf.line) < 3 &&
      gf.severity === sf.severity
    );
    
    if (!isDuplicate) {
      merged.push(sf);
    }
  }
  
  // Sort by severity then line number
  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
  merged.sort((a, b) => {
    const sevDiff = severityOrder[a.severity] - severityOrder[b.severity];
    if (sevDiff !== 0) return sevDiff;
    return a.line - b.line;
  });
  
  return merged;
}

// Generate combined report
function generateCombinedReport(projectPath, guardianFindings, slitherFindings) {
  const merged = mergeFindings(guardianFindings, slitherFindings);
  const now = new Date().toISOString().split('T')[0];
  
  const guardianCount = guardianFindings.length;
  const slitherCount = slitherFindings.length;
  const uniqueSlither = merged.length - guardianCount;
  
  let report = `# Combined Security Audit Report

**Project:** ${projectPath}
**Date:** ${now}
**Tools:** Solidity Guardian + Slither

## Analysis Summary

| Source | Findings |
|--------|----------|
| Solidity Guardian | ${guardianCount} |
| Slither (unique) | ${uniqueSlither} |
| **Total** | **${merged.length}** |

## Severity Breakdown

| Severity | Count |
|----------|-------|
| 🔴 Critical | ${merged.filter(f => f.severity === 'critical').length} |
| 🟠 High | ${merged.filter(f => f.severity === 'high').length} |
| 🟡 Medium | ${merged.filter(f => f.severity === 'medium').length} |
| 🔵 Low | ${merged.filter(f => f.severity === 'low').length} |

`;

  // Group by severity
  const bySeverity = {
    critical: merged.filter(f => f.severity === 'critical'),
    high: merged.filter(f => f.severity === 'high'),
    medium: merged.filter(f => f.severity === 'medium'),
    low: merged.filter(f => f.severity === 'low')
  };

  for (const [severity, items] of Object.entries(bySeverity)) {
    if (items.length === 0) continue;
    
    const emoji = { critical: '🔴', high: '🟠', medium: '🟡', low: '🔵' }[severity];
    report += `## ${emoji} ${severity.charAt(0).toUpperCase() + severity.slice(1)} Findings\n\n`;
    
    for (const finding of items) {
      const source = finding.source === 'slither' ? ' [Slither]' : ' [Guardian]';
      report += `### ${finding.id}: ${finding.title}${source}\n\n`;
      report += `**File:** \`${finding.file}\`\n`;
      report += `**Line:** ${finding.line}\n`;
      if (finding.confidence) {
        report += `**Confidence:** ${finding.confidence}\n`;
      }
      report += `\n**Issue:** ${finding.description}\n\n`;
      report += `**Recommendation:** ${finding.suggestion}\n\n`;
      if (finding.references && finding.references.length > 0) {
        report += `**References:** ${finding.references.join(', ')}\n`;
      }
      report += '\n---\n\n';
    }
  }
  
  return report;
}

// CLI
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help')) {
    console.log(`
Slither Integration for Solidity Guardian

Usage: node slither-integration.js <path> [options]

Options:
  --install-slither    Auto-install Slither if not found
  --format <type>      Output format: json, markdown (default: markdown)
  --output <file>      Write to file instead of stdout
  --guardian-only      Run Guardian analysis only (skip Slither)
  --slither-only       Run Slither analysis only (skip Guardian)
  --help               Show this help

Examples:
  node slither-integration.js ./contracts/
  node slither-integration.js . --format markdown --output AUDIT.md
  node slither-integration.js ./src/ --install-slither
`);
    process.exit(0);
  }
  
  const projectPath = args[0];
  const autoInstall = args.includes('--install-slither');
  const formatIdx = args.indexOf('--format');
  const format = formatIdx !== -1 ? args[formatIdx + 1] : 'markdown';
  const outputIdx = args.indexOf('--output');
  const outputFile = outputIdx !== -1 ? args[outputIdx + 1] : null;
  const guardianOnly = args.includes('--guardian-only');
  const slitherOnly = args.includes('--slither-only');
  
  // Import Guardian analyzer
  const { analyzeDirectory, analyzeFile, generateMarkdownReport } = require('./analyzer');
  
  let guardianFindings = [];
  let slitherFindings = [];
  
  // Run Guardian
  if (!slitherOnly) {
    console.log('Running Solidity Guardian analysis...');
    const stat = fs.statSync(projectPath);
    if (stat.isDirectory()) {
      guardianFindings = analyzeDirectory(projectPath);
    } else {
      guardianFindings = analyzeFile(projectPath);
    }
    console.log(`Guardian found ${guardianFindings.length} issues.`);
  }
  
  // Run Slither
  if (!guardianOnly) {
    console.log('Running Slither analysis...');
    const slitherResults = runSlither(projectPath, { autoInstall });
    if (slitherResults) {
      slitherFindings = convertSlitherFindings(slitherResults);
      console.log(`Slither found ${slitherFindings.length} issues.`);
    }
  }
  
  // Generate output
  let output;
  if (format === 'json') {
    output = JSON.stringify({
      guardian: guardianFindings,
      slither: slitherFindings,
      merged: mergeFindings(guardianFindings, slitherFindings)
    }, null, 2);
  } else {
    output = generateCombinedReport(projectPath, guardianFindings, slitherFindings);
  }
  
  if (outputFile) {
    fs.writeFileSync(outputFile, output);
    console.log(`\n✅ Report written to ${outputFile}`);
  } else {
    console.log('\n' + output);
  }
}

main().catch(console.error);

module.exports = { 
  checkSlither, 
  installSlither, 
  runSlither, 
  convertSlitherFindings, 
  mergeFindings,
  generateCombinedReport 
};
