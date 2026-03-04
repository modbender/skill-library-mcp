#!/usr/bin/env node
/**
 * Audit All Installed Skills
 * Scans every skill in the OpenClaw skills directories
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawnSync } = require('child_process');

// ANSI colors
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m'
};

function log(msg, color = '') {
  console.log(`${color}${msg}${colors.reset}`);
}

function findSkillDirectories() {
  const skillPaths = [];
  
  // Common skill locations
  const searchPaths = [
    // User's clawd/skills folder
    path.join(process.env.HOME || process.env.USERPROFILE, 'clawd', 'skills'),
    // OpenClaw npm global skills
    path.join(process.env.APPDATA || path.join(process.env.HOME || '', '.config'), 'npm', 'node_modules', 'openclaw', 'skills'),
    // Linux/Mac global
    '/usr/local/lib/node_modules/openclaw/skills',
    path.join(process.env.HOME || '', '.npm-global', 'lib', 'node_modules', 'openclaw', 'skills'),
    // Current directory skills
    path.join(process.cwd(), 'skills'),
  ];
  
  // Also check OPENCLAW_SKILLS_PATH env var
  if (process.env.OPENCLAW_SKILLS_PATH) {
    searchPaths.unshift(...process.env.OPENCLAW_SKILLS_PATH.split(path.delimiter));
  }
  
  for (const searchPath of searchPaths) {
    if (fs.existsSync(searchPath)) {
      try {
        const entries = fs.readdirSync(searchPath, { withFileTypes: true });
        for (const entry of entries) {
          if (entry.isDirectory()) {
            const skillPath = path.join(searchPath, entry.name);
            const skillMd = path.join(skillPath, 'SKILL.md');
            if (fs.existsSync(skillMd)) {
              skillPaths.push({
                name: entry.name,
                path: skillPath,
                source: searchPath
              });
            }
          }
        }
      } catch (e) {
        // Permission denied or other error, skip
      }
    }
  }
  
  // Dedupe by path
  const seen = new Set();
  return skillPaths.filter(s => {
    if (seen.has(s.path)) return false;
    seen.add(s.path);
    return true;
  });
}

function scanSkill(skillPath, options = {}) {
  const scanScript = path.join(__dirname, 'scan-skill.js');
  const args = [scanScript, skillPath, '--json-stdout'];
  
  if (options.severity) {
    args.push('--severity', options.severity);
  }
  
  try {
    const result = spawnSync('node', args, {
      encoding: 'utf8',
      timeout: 60000,
      maxBuffer: 10 * 1024 * 1024
    });
    
    if (result.stdout) {
      try {
        return JSON.parse(result.stdout);
      } catch (e) {
        // Try to find JSON in output
        const jsonMatch = result.stdout.match(/\{[\s\S]*\}$/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
      }
    }
    
    return {
      error: result.stderr || 'Scan failed',
      riskLevel: 'UNKNOWN'
    };
  } catch (e) {
    return {
      error: e.message,
      riskLevel: 'UNKNOWN'
    };
  }
}

function getRiskColor(risk) {
  switch (risk?.toUpperCase()) {
    case 'CRITICAL': return colors.red;
    case 'HIGH': return colors.red;
    case 'ELEVATED': return colors.yellow;
    case 'MEDIUM': return colors.yellow;
    case 'LOW': return colors.cyan;
    case 'CLEAN': return colors.green;
    default: return colors.dim;
  }
}

function getRiskEmoji(risk) {
  switch (risk?.toUpperCase()) {
    case 'CRITICAL': return '🚨';
    case 'HIGH': return '⚠️';
    case 'ELEVATED': return '⚡';
    case 'MEDIUM': return '📋';
    case 'LOW': return '📝';
    case 'CLEAN': return '✅';
    default: return '❓';
  }
}

async function main() {
  const args = process.argv.slice(2);
  const severity = args.find((a, i) => args[i-1] === '--severity') || 'high';
  const jsonOutput = args.includes('--json');
  const verbose = args.includes('--verbose') || args.includes('-v');
  
  if (args.includes('--help') || args.includes('-h')) {
    log('\nAudit All Installed Skills', colors.cyan);
    log('\nUsage: node audit-installed.js [options]');
    log('\nOptions:');
    log('  --severity <level>  Minimum severity to report (critical/high/medium/low)');
    log('  --json              Output results as JSON');
    log('  --verbose, -v       Show detailed findings');
    log('  --help, -h          Show this help');
    process.exit(0);
  }
  
  log('\n╔════════════════════════════════════════════════════════════╗', colors.cyan);
  log('║              SKILL AUDITOR - FULL AUDIT                    ║', colors.cyan);
  log('╚════════════════════════════════════════════════════════════╝\n', colors.cyan);
  
  log('Searching for installed skills...', colors.dim);
  const skills = findSkillDirectories();
  
  if (skills.length === 0) {
    log('\nNo skills found!', colors.yellow);
    log('Searched in common locations. Set OPENCLAW_SKILLS_PATH to add custom paths.', colors.dim);
    process.exit(0);
  }
  
  log(`Found ${skills.length} skill(s) to audit.\n`, colors.bright);
  
  const results = [];
  const summary = {
    total: skills.length,
    clean: 0,
    low: 0,
    medium: 0,
    elevated: 0,
    high: 0,
    critical: 0,
    unknown: 0
  };
  
  for (let i = 0; i < skills.length; i++) {
    const skill = skills[i];
    process.stdout.write(`[${i + 1}/${skills.length}] Scanning ${skill.name}...`);
    
    const result = scanSkill(skill.path, { severity });
    result.skillName = skill.name;
    result.skillPath = skill.path;
    results.push(result);
    
    const risk = result.riskLevel || 'UNKNOWN';
    const riskLower = risk.toLowerCase();
    
    if (summary[riskLower] !== undefined) {
      summary[riskLower]++;
    } else {
      summary.unknown++;
    }
    
    // Clear line and show result
    process.stdout.write('\r\x1b[K');
    log(
      `${getRiskEmoji(risk)} ${skill.name.padEnd(30)} ${getRiskColor(risk)}${risk.padEnd(10)}${colors.reset} ` +
      `${colors.dim}(${result.findingCount || 0} findings)${colors.reset}`
    );
    
    if (verbose && result.findings?.length > 0) {
      const criticalFindings = result.findings.filter(f => 
        f.severity === 'critical' || f.severity === 'high'
      ).slice(0, 5);
      
      for (const finding of criticalFindings) {
        log(`   └─ ${finding.severity.toUpperCase()}: ${finding.explanation?.slice(0, 60)}...`, colors.dim);
      }
    }
  }
  
  // Summary
  log('\n' + '─'.repeat(60), colors.dim);
  log('\n📊 AUDIT SUMMARY\n', colors.bright);
  
  log(`Total skills scanned: ${summary.total}`);
  log(`${colors.green}✅ Clean:    ${summary.clean}${colors.reset}`);
  log(`${colors.cyan}📝 Low:      ${summary.low}${colors.reset}`);
  log(`${colors.yellow}📋 Medium:   ${summary.medium}${colors.reset}`);
  log(`${colors.yellow}⚡ Elevated: ${summary.elevated}${colors.reset}`);
  log(`${colors.red}⚠️  High:     ${summary.high}${colors.reset}`);
  log(`${colors.red}🚨 Critical: ${summary.critical}${colors.reset}`);
  
  if (summary.unknown > 0) {
    log(`${colors.dim}❓ Unknown:  ${summary.unknown}${colors.reset}`);
  }
  
  // High-risk skills
  const riskySkills = results.filter(r => 
    ['critical', 'high'].includes(r.riskLevel?.toLowerCase())
  );
  
  if (riskySkills.length > 0) {
    log('\n⚠️  HIGH-RISK SKILLS DETECTED:', colors.red);
    for (const skill of riskySkills) {
      log(`\n  ${skill.skillName}`, colors.bright);
      log(`  Path: ${skill.skillPath}`, colors.dim);
      if (skill.summary?.actualCapabilities) {
        log(`  Capabilities: ${skill.summary.actualCapabilities.slice(0, 3).join(', ')}`, colors.yellow);
      }
      if (skill.summary?.externalUrls?.length > 0) {
        log(`  External URLs: ${skill.summary.externalUrls.slice(0, 2).join(', ')}`, colors.yellow);
      }
    }
    log('\n  Run individual scans for details:', colors.dim);
    log('  node scripts/scan-skill.js <path>', colors.dim);
  }
  
  // JSON output
  if (jsonOutput) {
    const jsonPath = path.join(process.cwd(), 'audit-results.json');
    fs.writeFileSync(jsonPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      summary,
      results
    }, null, 2));
    log(`\n📄 Full results saved to: ${jsonPath}`, colors.cyan);
  }
  
  // Exit code based on findings
  if (summary.critical > 0) {
    process.exit(2);
  } else if (summary.high > 0) {
    process.exit(1);
  }
  process.exit(0);
}

main().catch(err => {
  console.error('Audit failed:', err);
  process.exit(1);
});
