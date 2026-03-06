#!/usr/bin/env node
/**
 * 🔍 Skill Audit - Security scanner for OpenClaw skills
 * 
 * Detects suspicious patterns that may indicate malicious code.
 */

const fs = require('fs');
const path = require('path');

// ============================================
// Detection Patterns
// ============================================

const PATTERNS = {
  critical: [
    {
      name: 'credential_read',
      pattern: /(?:credentials|\.ssh|\.env|\.npmrc|\.aws|auth|secret|token).*(?:read|open|access|load)/gi,
      description: 'Reads credential files',
    },
    {
      name: 'credential_path',
      pattern: /['"`](?:~\/\.ssh|~\/\.env|\.\.\/\.\.\/|\/etc\/passwd|credentials\.json|auth.*\.json)['"`]/gi,
      description: 'References sensitive file paths',
    },
    {
      name: 'data_exfil',
      pattern: /(?:fetch|axios|http|request)\s*\(\s*['"`]https?:\/\/(?!(?:api\.github|api\.openai|api\.anthropic|www\.moltbook))[^'"`]+['"`]/gi,
      description: 'Sends data to unknown external URL',
    },
    {
      name: 'webhook',
      pattern: /webhook\.site|requestbin|pipedream|hookbin|beeceptor/gi,
      description: 'Uses known data exfiltration services',
    },
    {
      name: 'env_secrets',
      pattern: /process\.env\.(API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIAL|PRIVATE)/gi,
      description: 'Accesses secret environment variables',
    },
  ],

  warning: [
    {
      name: 'eval_exec',
      pattern: /\b(?:eval|exec|execSync|spawn|fork)\s*\(/gi,
      description: 'Uses dynamic code execution',
    },
    {
      name: 'child_process',
      pattern: /require\s*\(\s*['"`]child_process['"`]\s*\)/gi,
      description: 'Imports child_process module',
    },
    {
      name: 'dynamic_require',
      pattern: /require\s*\(\s*[^'"`]/gi,
      description: 'Uses dynamic require',
    },
    {
      name: 'base64_string',
      pattern: /['"`][A-Za-z0-9+\/]{50,}={0,2}['"`]/g,
      description: 'Contains long base64 string (possible obfuscation)',
    },
    {
      name: 'fs_traversal',
      pattern: /fs\.(readdir|readdirSync|readFile|readFileSync)\s*\(\s*['"`](?:\/|~|\.\.)/gi,
      description: 'Reads files outside skill directory',
    },
    {
      name: 'network_unknown',
      pattern: /(?:fetch|axios|http\.get|https\.get)\s*\(/gi,
      description: 'Makes network requests',
    },
  ],

  info: [
    {
      name: 'shell_command',
      pattern: /\$\(.*\)|\.sh['"`]\s*\)|(?:^|\s)(?:bash|zsh)\s+-c/gi,
      description: 'Uses shell commands',
    },
    {
      name: 'file_write',
      pattern: /fs\.(?:writeFile|writeFileSync|appendFile)/gi,
      description: 'Writes to filesystem',
    },
    {
      name: 'many_deps',
      pattern: /"dependencies"\s*:\s*\{[^}]{500,}\}/g,
      description: 'Has many dependencies',
    },
  ],
};

// Known safe domains
const SAFE_DOMAINS = [
  'api.github.com',
  'api.openai.com',
  'api.anthropic.com',
  'www.moltbook.com',
  'clawhub.com',
  'registry.npmjs.org',
];

// ============================================
// Scanner
// ============================================

function scanFile(filePath, content) {
  const findings = [];
  const lines = content.split('\n');

  for (const [severity, patterns] of Object.entries(PATTERNS)) {
    for (const { name, pattern, description } of patterns) {
      // Reset regex state
      pattern.lastIndex = 0;
      
      let match;
      while ((match = pattern.exec(content)) !== null) {
        // Find line number
        const beforeMatch = content.substring(0, match.index);
        const lineNumber = beforeMatch.split('\n').length;
        const lineContent = lines[lineNumber - 1]?.trim() || '';

        findings.push({
          file: path.basename(filePath),
          severity: severity.toUpperCase(),
          name,
          description,
          line: lineNumber,
          context: lineContent.substring(0, 60) + (lineContent.length > 60 ? '...' : ''),
        });
      }
    }
  }

  return findings;
}

function scanDirectory(dir) {
  const findings = [];
  const extensions = ['.js', '.ts', '.mjs', '.cjs', '.json', '.md'];

  function walk(currentPath) {
    if (!fs.existsSync(currentPath)) return;
    
    const stat = fs.statSync(currentPath);
    
    if (stat.isDirectory()) {
      // Skip node_modules and .git
      if (path.basename(currentPath) === 'node_modules') return;
      if (path.basename(currentPath) === '.git') return;
      
      const files = fs.readdirSync(currentPath);
      for (const file of files) {
        walk(path.join(currentPath, file));
      }
    } else if (stat.isFile()) {
      const ext = path.extname(currentPath).toLowerCase();
      if (extensions.includes(ext)) {
        const content = fs.readFileSync(currentPath, 'utf-8');
        const fileFindings = scanFile(currentPath, content);
        findings.push(...fileFindings);
      }
    }
  }

  walk(dir);
  return findings;
}

function calculateRiskScore(findings) {
  let score = 0;
  for (const f of findings) {
    if (f.severity === 'CRITICAL') score += 30;
    else if (f.severity === 'WARNING') score += 10;
    else if (f.severity === 'INFO') score += 2;
  }
  return Math.min(100, score);
}

function formatReport(skillName, findings, riskScore) {
  const riskLevel = riskScore >= 70 ? '🔴 HIGH RISK' : riskScore >= 30 ? '🟠 MEDIUM' : '🟢 LOW';
  
  let report = `
🔍 Skill Audit Report: ${skillName}
${'━'.repeat(50)}

Risk Score: ${riskScore}/100 ${riskLevel}

`;

  if (findings.length === 0) {
    report += '✅ No suspicious patterns detected.\n';
  } else {
    // Group by severity
    const critical = findings.filter(f => f.severity === 'CRITICAL');
    const warning = findings.filter(f => f.severity === 'WARNING');
    const info = findings.filter(f => f.severity === 'INFO');

    if (critical.length > 0) {
      report += '🔴 CRITICAL:\n';
      for (const f of critical) {
        report += `  • ${f.file}:${f.line} - ${f.description}\n`;
        report += `    └─ ${f.context}\n`;
      }
      report += '\n';
    }

    if (warning.length > 0) {
      report += '🟠 WARNING:\n';
      for (const f of warning) {
        report += `  • ${f.file}:${f.line} - ${f.description}\n`;
      }
      report += '\n';
    }

    if (info.length > 0) {
      report += '🟡 INFO:\n';
      for (const f of info) {
        report += `  • ${f.file}:${f.line} - ${f.description}\n`;
      }
      report += '\n';
    }
  }

  // Recommendation
  if (riskScore >= 70) {
    report += '⚠️  RECOMMENDATION: DO NOT INSTALL - Review code manually before use!\n';
  } else if (riskScore >= 30) {
    report += '⚠️  RECOMMENDATION: Review flagged items before installing.\n';
  } else {
    report += '✅ RECOMMENDATION: Skill appears safe to use.\n';
  }

  return report;
}

// ============================================
// CLI
// ============================================

function main() {
  const args = process.argv.slice(2);
  const command = args[0];

  if (!command || command === '--help') {
    console.log(`
🔍 Skill Audit - Security scanner for OpenClaw skills

Usage:
  skill-audit scan <path>     Scan a skill directory
  skill-audit scan --all      Scan all installed skills

Examples:
  node audit.js scan ~/.openclaw/workspace/skills/moltdash
  node audit.js scan --all
`);
    return;
  }

  if (command === 'scan') {
    const target = args[1];

    if (target === '--all') {
      // Scan all skills in workspace
      const skillsDir = path.join(process.env.HOME, '.openclaw/workspace/skills');
      if (!fs.existsSync(skillsDir)) {
        console.log('No skills directory found.');
        return;
      }

      const skills = fs.readdirSync(skillsDir).filter(f => 
        fs.statSync(path.join(skillsDir, f)).isDirectory() && !f.startsWith('.')
      );

      console.log(`Scanning ${skills.length} skills...\n`);

      for (const skill of skills) {
        const skillPath = path.join(skillsDir, skill);
        const findings = scanDirectory(skillPath);
        const riskScore = calculateRiskScore(findings);
        
        const icon = riskScore >= 70 ? '🔴' : riskScore >= 30 ? '🟠' : '🟢';
        console.log(`${icon} ${skill}: ${riskScore}/100 (${findings.length} findings)`);
      }
    } else if (target) {
      // Scan specific skill
      const skillPath = path.resolve(target);
      if (!fs.existsSync(skillPath)) {
        console.error(`Path not found: ${skillPath}`);
        process.exit(1);
      }

      const skillName = path.basename(skillPath);
      const findings = scanDirectory(skillPath);
      const riskScore = calculateRiskScore(findings);
      
      console.log(formatReport(skillName, findings, riskScore));
    } else {
      console.error('Please specify a skill path or use --all');
      process.exit(1);
    }
  }
}

main();
