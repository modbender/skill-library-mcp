#!/usr/bin/env node
/**
 * Skill Guardian - Security Scanner for OpenClaw Skills
 * 
 * Scans skill directories for malicious patterns including:
 * - Crypto harvesting, reverse shells, credential theft
 * - Encoded payloads, suspicious API calls
 * - Dangerous execution patterns
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Pattern definitions for malicious code detection
const PATTERNS = {
  // Critical severity patterns
  CRITICAL: [
    {
      name: 'private_key_harvest',
      pattern: /(?:private[_-]?key|privkey|secret[_-]?key)\s*[=:]\s*["'][^"']{32,}["']/i,
      description: 'Hardcoded private key detected',
      mitigation: 'Never hardcode private keys in source code'
    },
    {
      name: 'wallet_file_access',
      pattern: /(?:fs\.read|readFile|cat)\s*\(?\s*["'].*(?:keystore|wallet|metamask|ethereum|bitcoin|solana).*["']/i,
      description: 'Attempts to access cryptocurrency wallet files',
      mitigation: 'Remove code that accesses cryptocurrency wallets'
    },
    {
      name: 'reverse_shell_bash',
      pattern: /bash\s+-i\s+>&\s*\/dev\/tcp\/[0-9.]+\/\d+/i,
      description: 'Bash reverse shell detected',
      mitigation: 'Remove reverse shell code immediately'
    },
    {
      name: 'reverse_shell_nc',
      pattern: /(?:nc|netcat).*-[el].*\d+.*(?:sh|bash|zsh)/i,
      description: 'Netcat reverse shell detected',
      mitigation: 'Remove reverse shell code immediately'
    },
    {
      name: 'reverse_shell_socket',
      pattern: /socket\..*connect.*(?:exec|spawn|child_process)/i,
      description: 'Socket-based reverse shell pattern',
      mitigation: 'Review socket connections for malicious intent'
    },
    {
      name: 'openclaw_config_access',
      pattern: /(?:\.openclaw|openclaw\.json|config\.json).*read|fs\.read.*openclaw/i,
      description: 'Attempts to read OpenClaw configuration files',
      mitigation: 'Skills should not access OpenClaw configuration'
    }
  ],

  // High severity patterns
  HIGH: [
    {
      name: 'mnemonic_phrase',
      pattern: /(?:mnemonic|seed[_-]?phrase|recovery[_-]?phrase).*[=:].*["'][a-z]+(?:\s+[a-z]+){11,23}["']/i,
      description: 'Cryptocurrency mnemonic seed phrase handling',
      mitigation: 'Never handle mnemonic phrases in skill code'
    },
    {
      name: 'crypto_address_pattern',
      pattern: /(?:0x[a-f0-9]{40}|[13][a-zA-Z0-9]{26,33}|bc1[a-z0-9]{39,59})/i,
      description: 'Cryptocurrency address pattern found',
      mitigation: 'Verify all crypto addresses are legitimate'
    },
    {
      name: 'curl_pipe_bash',
      pattern: /(?:curl|wget).*\|.*(?:bash|sh|zsh)/i,
      description: 'Dangerous curl | bash pattern detected',
      mitigation: 'Avoid piping curl directly to shell'
    },
    {
      name: 'eval_execution',
      pattern: /eval\s*\(\s*(?:atob|Buffer\.from|decode)/i,
      description: 'Eval with decoded payload execution',
      mitigation: 'Remove eval() with decoded content'
    },
    {
      name: 'base64_obfuscation',
      pattern: /(?:atob|btoa|Buffer\.from|base64).*\n.*(?:eval|exec|Function)/is,
      description: 'Base64 encoded payload with execution',
      mitigation: 'Do not execute base64 decoded content'
    },
    {
      name: 'suspicious_domain',
      pattern: /https?:\/\/(?:[a-z0-9-]+\.)?(?:pastebin|ghostbin|termbin|requestbin|hookbin|webhook\.site)\./i,
      description: 'External request to suspicious paste/dump service',
      mitigation: 'Avoid external services for data exfiltration'
    },
    {
      name: 'dynamic_import_suspicious',
      pattern: /import\s*\(\s*(?:atob|decode|Buffer|__encode)/i,
      description: 'Dynamic import with potentially obfuscated URL',
      mitigation: 'Use static imports with verified sources'
    }
  ],

  // Medium severity patterns
  MEDIUM: [
    {
      name: 'env_var_access',
      pattern: /process\.env\.(?:OPENCLAW_|API_KEY|SECRET|PASSWORD|PRIVATE|TOKEN)/i,
      description: 'Accessing sensitive environment variables',
      mitigation: 'Limit access to sensitive environment variables'
    },
    {
      name: 'home_directory_access',
      pattern: /(?:~\/|\$HOME|\${HOME}|os\.homedir).*\.(?:env|config|key|secret)/i,
      description: 'Accessing sensitive files in home directory',
      mitigation: 'Skills should not access user home directory files'
    },
    {
      name: 'payment_prompt',
      pattern: /(?:send|deposit|transfer|pay).*\$?\d+.*(?:to|address|wallet)/i,
      description: 'Payment or deposit request pattern',
      mitigation: 'Verify all payment requests are legitimate'
    },
    {
      name: 'clipboard_access',
      pattern: /clipboard.*(?:read|write)|readText|writeText.*clipboard/i,
      description: 'Clipboard access detected',
      mitigation: 'Clipboard access may steal sensitive data'
    },
    {
      name: 'keylogger_pattern',
      pattern: /(?:keydown|keyup|keypress).*send|emit.*(?:key|input|stroke)/i,
      description: 'Potential keylogger pattern',
      mitigation: 'Review keyboard event handling for malicious intent'
    },
    {
      name: 'suspicious_fetch',
      pattern: /fetch\s*\(\s*["']https?:\/\/(?:\d{1,3}\.){3}\d{1,3}/i,
      description: 'HTTP request to IP address (suspicious)',
      mitigation: 'Use domain names instead of IP addresses'
    }
  ],

  // Low severity patterns
  LOW: [
    {
      name: 'hex_encoded',
      pattern: /["']\\x[0-9a-f]{2}(?:\\x[0-9a-f]{2}){7,}["']/i,
      description: 'Hex encoded string detected',
      mitigation: 'Avoid hex encoding in source code'
    },
    {
      name: 'unicode_escape',
      pattern: /\\u[0-9a-f]{4}(?:\\u[0-9a-f]{4}){3,}/i,
      description: 'Unicode escape sequence obfuscation',
      mitigation: 'Avoid unicode escape sequences'
    },
    {
      name: 'child_process_spawn',
      pattern: /child_process\.(?:spawn|exec|execSync)\s*\(\s*["']curl|wget|nc|netcat/i,
      description: 'Spawning external network process',
      mitigation: 'Review all external process spawning'
    },
    {
      name: 'network_interface_enum',
      pattern: /os\.networkInterfaces|ifconfig|ipconfig|ip\s+addr/i,
      description: 'Network interface enumeration',
      mitigation: 'Skills typically do not need network info'
    }
  ]
};

// Suspicious file names and extensions
const SUSPICIOUS_FILES = [
  /\.exe$/i,
  /\.dll$/i,
  /\.so$/i,
  /\.dylib$/i,
  /\.bin$/i,
  /keylogger/i,
  /stealer/i,
  /exploit/i,
  /payload/i,
  /backdoor/i,
  /trojan/i
];

// Files to skip during scanning
const SKIP_PATTERNS = [
  /node_modules/i,
  /\.git/i,
  /package-lock\.json$/,
  /yarn\.lock$/,
  /\.min\.js$/,
  /dist\//,
  /build\//,
  /coverage\//
];

/**
 * Calculate SHA256 hash of file content
 */
function hashContent(content) {
  return crypto.createHash('sha256').update(content).digest('hex');
}

/**
 * Check if file should be skipped
 */
function shouldSkipFile(filePath) {
  return SKIP_PATTERNS.some(pattern => pattern.test(filePath));
}

/**
 * Check if filename is suspicious
 */
function checkSuspiciousFilename(filePath) {
  const basename = path.basename(filePath);
  return SUSPICIOUS_FILES.filter(pattern => pattern.test(basename));
}

/**
 * Scan a single file for malicious patterns
 */
function scanFile(filePath, content, options = {}) {
  const findings = [];
  const lines = content.split('\n');
  const suspiciousName = checkSuspiciousFilename(filePath);
  
  // Check for suspicious filename
  if (suspiciousName.length > 0) {
    findings.push({
      severity: 'medium',
      category: 'suspicious_filename',
      file: filePath,
      line: 0,
      match: path.basename(filePath),
      description: `Suspicious filename pattern: ${suspiciousName.map(p => p.source).join(', ')}`,
      mitigation: 'Review file purpose and naming'
    });
  }

  // Check each line against patterns
  lines.forEach((line, index) => {
    const lineNum = index + 1;
    
    // Skip comments unless they contain suspicious URLs
    const codeOnly = line.replace(/\/\/.*$|\/\*[\s\S]*?\*\//, '').trim();
    
    // Check all severity levels
    Object.entries(PATTERNS).forEach(([severity, patterns]) => {
      patterns.forEach(({ name, pattern, description, mitigation }) => {
        if (pattern.test(line) || pattern.test(codeOnly)) {
          findings.push({
            severity: severity.toLowerCase(),
            category: name,
            file: filePath,
            line: lineNum,
            match: line.trim().substring(0, 150),
            description,
            mitigation
          });
        }
      });
    });
  });

  // Check for deeply encoded content if option enabled
  if (options.checkEncoded) {
    const encodedFindings = checkEncodedPayloads(content, filePath);
    findings.push(...encodedFindings);
  }

  return findings;
}

/**
 * Check for encoded payloads (base64, hex with multiple layers)
 */
function checkEncodedPayloads(content, filePath) {
  const findings = [];
  
  // Detect multiple layers of base64
  const base64Pattern = /["']([A-Za-z0-9+/]{100,}={0,2})["']/g;
  let match;
  
  while ((match = base64Pattern.exec(content)) !== null) {
    const potentialBase64 = match[1];
    
    // Try to decode
    try {
      let decoded = Buffer.from(potentialBase64, 'base64').toString('utf-8');
      let depth = 1;
      
      // Check for nested encoding
      while (depth < 3) {
        const isBase64 = /^[A-Za-z0-9+/]+={0,2}$/.test(decoded) && decoded.length > 50;
        if (!isBase64) break;
        
        decoded = Buffer.from(decoded, 'base64').toString('utf-8');
        depth++;
      }
      
      // Check if final decoded content is suspicious
      const suspiciousDecoded = /(?:eval|exec|Function|import|require)\s*\(/i.test(decoded);
      
      if (depth > 1 || suspiciousDecoded) {
        findings.push({
          severity: depth > 2 ? 'critical' : 'high',
          category: 'encoded_payload',
          file: filePath,
          line: content.substring(0, match.index).split('\n').length,
          match: `${potentialBase64.substring(0, 50)}...`,
          description: `Multi-layer encoded payload detected (${depth} layers)`,
          mitigation: 'Do not execute encoded content',
          meta: { encodingDepth: depth }
        });
      }
    } catch (e) {
      // Not valid base64, ignore
    }
  }

  return findings;
}

/**
 * Recursively get all files in directory
 */
function getAllFiles(dirPath, arrayOfFiles = []) {
  try {
    const files = fs.readdirSync(dirPath);
    
    files.forEach(file => {
      const fullPath = path.join(dirPath, file);
      
      if (shouldSkipFile(fullPath)) {
        return;
      }
      
      if (fs.statSync(fullPath).isDirectory()) {
        arrayOfFiles = getAllFiles(fullPath, arrayOfFiles);
      } else {
        arrayOfFiles.push(fullPath);
      }
    });
  } catch (error) {
    // Directory may not exist or be accessible
  }
  
  return arrayOfFiles;
}

/**
 * Calculate risk score based on findings
 */
function calculateRiskScore(findings) {
  const weights = {
    critical: 25,
    high: 15,
    medium: 10,
    low: 5
  };

  let score = 0;
  const countedCategories = new Set();

  findings.forEach(finding => {
    // Cap score contribution per category to prevent single exploit type dominating
    if (!countedCategories.has(finding.category)) {
      score += weights[finding.severity] || 5;
      countedCategories.add(finding.category);
    } else {
      // Additional instances add smaller amounts
      score += Math.ceil((weights[finding.severity] || 5) / 4);
    }
  });

  // Cap at 100
  return Math.min(score, 100);
}

/**
 * Determine recommendation based on score
 */
function getRecommendation(score) {
  if (score >= 76) return 'MALICIOUS';
  if (score >= 51) return 'SUSPICIOUS';
  if (score >= 21) return 'LOW_RISK';
  return 'SAFE';
}

/**
 * Main scan function
 */
async function scanSkill(skillPath, options = {}) {
  const startTime = Date.now();
  
  // Validate path
  if (!fs.existsSync(skillPath)) {
    throw new Error(`Skill path does not exist: ${skillPath}`);
  }

  const resolvedPath = path.resolve(skillPath);
  const skillName = path.basename(resolvedPath);
  
  // Get all files to scan
  const files = getAllFiles(resolvedPath);
  const findings = [];
  let filesScanned = 0;
  let bytesScanned = 0;

  // Scan each file
  for (const file of files) {
    try {
      // Only scan text files
      const ext = path.extname(file).toLowerCase();
      const textExtensions = ['.js', '.ts', '.json', '.md', '.py', '.sh', '.bash', '.zsh', '.txt', '.yaml', '.yml'];
      
      if (!textExtensions.includes(ext) && ext !== '') {
        continue;
      }

      const content = fs.readFileSync(file, 'utf-8');
      bytesScanned += content.length;
      filesScanned++;

      const relativePath = path.relative(resolvedPath, file);
      const fileFindings = scanFile(relativePath, content, options);
      findings.push(...fileFindings);

      if (options.verbose && fileFindings.length > 0) {
        console.log(`⚠️  ${relativePath}: ${fileFindings.length} finding(s)`);
      }
    } catch (error) {
      if (options.verbose) {
        console.error(`Error scanning ${file}: ${error.message}`);
      }
    }
  }

  // Calculate risk metrics
  const riskScore = calculateRiskScore(findings);
  const recommendation = getRecommendation(riskScore);
  
  const summary = {
    totalFilesScanned: filesScanned,
    totalBytesScanned: bytesScanned,
    filesWithIssues: new Set(findings.map(f => f.file)).size,
    criticalFindings: findings.filter(f => f.severity === 'critical').length,
    highFindings: findings.filter(f => f.severity === 'high').length,
    mediumFindings: findings.filter(f => f.severity === 'medium').length,
    lowFindings: findings.filter(f => f.severity === 'low').length
  };

  const report = {
    skillPath: resolvedPath,
    skillName,
    scanTimestamp: new Date().toISOString(),
    scanDuration: Date.now() - startTime,
    riskScore,
    recommendation,
    summary,
    findings: findings.sort((a, b) => {
      const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
      return severityOrder[a.severity] - severityOrder[b.severity];
    })
  };

  return report;
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length < 1 || args.includes('--help') || args.includes('-h')) {
    console.log(`
Skill Guardian - Security Scanner for OpenClaw Skills

Usage:
  node scan.js <skill-path> [options]

Options:
  --verbose, -v       Show detailed scan progress
  --output, -o        Save report to JSON file
  --strict, -s        Fail on any findings (exit code 1)
  --encoded, -e       Check for deeply encoded payloads
  --help, -h          Show this help message

Examples:
  node scan.js ../some-skill
  node scan.js ../some-skill --verbose --output report.json
  node scan.js ../some-skill --strict --encoded
`);
    process.exit(0);
  }

  const skillPath = args[0];
  const options = {
    verbose: args.includes('--verbose') || args.includes('-v'),
    output: null,
    strictMode: args.includes('--strict') || args.includes('-s'),
    checkEncoded: args.includes('--encoded') || args.includes('-e')
  };

  // Parse output file
  const outputIndex = args.indexOf('--output') !== -1 ? args.indexOf('--output') : args.indexOf('-o');
  if (outputIndex !== -1 && args[outputIndex + 1]) {
    options.output = args[outputIndex + 1];
  }

  try {
    if (options.verbose) {
      console.log(`🔍 Scanning skill: ${skillPath}`);
      console.log('─'.repeat(50));
    }

    const report = await scanSkill(skillPath, options);

    // Print summary
    console.log('\n' + '═'.repeat(60));
    console.log('  SECURITY SCAN REPORT');
    console.log('═'.repeat(60));
    console.log(`  Skill:      ${report.skillName}`);
    console.log(`  Path:       ${report.skillPath}`);
    console.log(`  Scanned:    ${report.summary.totalFilesScanned} files (${(report.summary.totalBytesScanned / 1024).toFixed(1)} KB)`);
    console.log('─'.repeat(60));
    console.log(`  Risk Score: ${report.riskScore}/100`);
    
    // Color code recommendation
    const recColors = {
      SAFE: '\x1b[32m',      // Green
      LOW_RISK: '\x1b[33m',  // Yellow
      SUSPICIOUS: '\x1b[35m', // Magenta
      MALICIOUS: '\x1b[31m'   // Red
    };
    const reset = '\x1b[0m';
    const color = recColors[report.recommendation] || '';
    console.log(`  Verdict:    ${color}${report.recommendation}${reset}`);
    console.log('─'.repeat(60));

    // Print findings summary
    if (report.findings.length > 0) {
      console.log(`\n  Findings by Severity:`);
      console.log(`    🔴 Critical: ${report.summary.criticalFindings}`);
      console.log(`    🟠 High:     ${report.summary.highFindings}`);
      console.log(`    🟡 Medium:   ${report.summary.mediumFindings}`);
      console.log(`    🟢 Low:      ${report.summary.lowFindings}`);

      if (options.verbose) {
        console.log('\n  Detailed Findings:');
        report.findings.forEach((finding, i) => {
          const severityEmoji = {
            critical: '🔴',
            high: '🟠',
            medium: '🟡',
            low: '🟢'
          }[finding.severity];
          
          console.log(`\n  ${i + 1}. ${severityEmoji} [${finding.severity.toUpperCase()}] ${finding.category}`);
          console.log(`     File: ${finding.file}:${finding.line}`);
          console.log(`     ${finding.description}`);
          console.log(`     Match: ${finding.match.substring(0, 80)}...`);
          console.log(`     Mitigation: ${finding.mitigation}`);
        });
      }
    } else {
      console.log('\n  ✅ No security issues detected');
    }

    console.log('\n' + '═'.repeat(60));

    // Save report if requested
    if (options.output) {
      fs.writeFileSync(options.output, JSON.stringify(report, null, 2));
      console.log(`\n📄 Report saved to: ${options.output}`);
    }

    // Exit with appropriate code
    if (report.recommendation === 'MALICIOUS') {
      process.exit(3);
    } else if (report.findings.length > 0 && options.strictMode) {
      process.exit(1);
    } else {
      process.exit(0);
    }

  } catch (error) {
    console.error(`❌ Scan failed: ${error.message}`);
    process.exit(2);
  }
}

// Export for programmatic usage
module.exports = { scanSkill, scanFile, PATTERNS };

// Run if executed directly
if (require.main === module) {
  main();
}
