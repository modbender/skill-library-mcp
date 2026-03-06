#!/usr/bin/env node

/**
 * Security Skill Scanner v2.0.0
 * Analyzes OpenClaw skill markdown files for suspicious instruction patterns
 * 
 * Note: This scans SKILL.md files (markdown documentation).
 * It looks for suspicious INSTRUCTIONS that tell agents to do unsafe things,
 * not for executable malware (since skills are just text instructions).
 * 
 * Author: Md Anik Rahman
 * License: MIT
 */

const fs = require('fs');
const path = require('path');

// Risk levels
const RISK_LEVELS = {
  CRITICAL: { score: 100, emoji: '🔴', label: 'CRITICAL' },
  HIGH: { score: 75, emoji: '🟠', label: 'HIGH' },
  MEDIUM: { score: 50, emoji: '🟡', label: 'MEDIUM' },
  LOW: { score: 25, emoji: '🟢', label: 'LOW' },
  INFO: { score: 0, emoji: 'ℹ️', label: 'INFO' }
};

// Security patterns to detect
const SECURITY_PATTERNS = {
  // CRITICAL patterns
  SHELL_INJECTION: {
    level: 'CRITICAL',
    patterns: [
      /eval\s*\(/gi,
      /exec\s*\(/gi,
      /execSync\s*\(/gi,
      /spawn\s*\(/gi,
      /child_process/gi,
      /\$\{.*?\}/g, // Command substitution
      /`.*?`/g, // Backtick execution
    ],
    description: 'Shell command execution detected',
    recommendation: 'Review command execution carefully - potential for arbitrary code execution'
  },
  
  EXTERNAL_DOWNLOAD: {
    level: 'CRITICAL',
    patterns: [
      /curl\s+.*?\s+-o\s+/gi,
      /wget\s+.*?\s+-O\s+/gi,
      /download.*?\.exe/gi,
      /download.*?\.sh/gi,
      /download.*?\.bin/gi,
      /fetch.*?binary/gi,
    ],
    description: 'External binary download detected',
    recommendation: 'DO NOT INSTALL - Downloading external executables is extremely dangerous'
  },

  CREDENTIAL_HARVESTING: {
    level: 'CRITICAL',
    patterns: [
      /password\s*[:=]\s*.*?input/gi,
      /api[_-]?key\s*[:=]\s*.*?input/gi,
      /token\s*[:=]\s*.*?input/gi,
      /\.env.*?upload/gi,
      /credentials.*?send/gi,
      /auth.*?post.*?http[^s]/gi,
    ],
    description: 'Potential credential harvesting detected',
    recommendation: 'This may attempt to steal credentials - DO NOT INSTALL'
  },

  KNOWN_MALWARE_DOMAINS: {
    level: 'CRITICAL',
    patterns: [
      /data-collector\.xyz/gi,
      /analytics-tracker\.site/gi,
      /log-service\.info/gi,
      /stat-collector\.net/gi,
      // Add known malicious domains here
    ],
    description: 'Known malicious domain detected',
    recommendation: 'DO NOT INSTALL - This domain is associated with malware'
  },

  // HIGH risk patterns
  SUSPICIOUS_API_CALLS: {
    level: 'HIGH',
    patterns: [
      /https?:\/\/[a-z0-9-]+\.(xyz|tk|ml|ga|cf|gq)/gi, // Suspicious TLDs
      /post.*?http:\/\//gi, // Unencrypted POST
      /fetch\(['"](http:\/\/|\/\/)/gi,
      /XMLHttpRequest.*?http:\/\//gi,
    ],
    description: 'Suspicious API endpoint or unencrypted connection',
    recommendation: 'Review what data is being sent and to where'
  },

  SENSITIVE_FILE_ACCESS: {
    level: 'HIGH',
    patterns: [
      /\.ssh\/|\.aws\/|\.config\//gi,
      /\/etc\/passwd|\/etc\/shadow/gi,
      /\.npmrc|\.pypirc/gi,
      /id_rsa|id_dsa/gi,
      /\.pgpass|\.netrc/gi,
      /writeFile.*?\/etc\//gi,
    ],
    description: 'Access to sensitive system files or directories',
    recommendation: 'This skill requests access to sensitive files - verify necessity'
  },

  BASE64_ENCODING: {
    level: 'HIGH',
    patterns: [
      /atob\(/gi,
      /btoa\(/gi,
      /Buffer\.from\(.*?['"]base64['"]\)/gi,
      /base64.*?decode/gi,
      /fromBase64/gi,
      /[A-Za-z0-9+\/]{40,}={0,2}/, // Long base64 strings
    ],
    description: 'Base64 encoding/decoding detected',
    recommendation: 'May be obfuscating malicious code - inspect carefully'
  },

  // MEDIUM risk patterns
  BROAD_FILE_ACCESS: {
    level: 'MEDIUM',
    patterns: [
      /fs\.readdir.*?['"]\//gi,
      /glob\(['"]\*\*/gi,
      /recursive.*?true/gi,
      /readFile.*?\/home\//gi,
    ],
    description: 'Broad file system access detected',
    recommendation: 'Review what files this skill needs to access'
  },

  UNENCRYPTED_NETWORK: {
    level: 'MEDIUM',
    patterns: [
      /http:\/\/(?!localhost|127\.0\.0\.1)/gi,
      /ws:\/\//gi, // Unencrypted websocket
    ],
    description: 'Unencrypted network connection',
    recommendation: 'Data transmitted without encryption - request HTTPS version'
  },

  DYNAMIC_IMPORTS: {
    level: 'MEDIUM',
    patterns: [
      /require\(.*?\+.*?\)/gi,
      /import\(.*?\+.*?\)/gi,
      /eval.*?require/gi,
    ],
    description: 'Dynamic code loading detected',
    recommendation: 'Could load arbitrary code - verify what is being imported'
  },

  // LOW risk patterns
  MISSING_ERROR_HANDLING: {
    level: 'LOW',
    patterns: [
      /(?<!try\s*\{[\s\S]{0,200})await\s+(?!.*catch)/gi,
    ],
    description: 'Potential missing error handling',
    recommendation: 'Code quality issue - may cause crashes'
  },
};

// Whitelisted patterns (legitimate uses)
const WHITELIST = {
  domains: [
    'github.com',
    'raw.githubusercontent.com',
    'api.openai.com',
    'api.anthropic.com',
    'api.weatherapi.com',
    'api.github.com',
    'npmjs.com',
    'pypi.org',
  ],
  commands: [
    'npm install',
    'pip install',
    'yarn add',
  ],
};

class SecurityScanner {
  constructor(config = {}) {
    this.config = {
      whitelistedDomains: [...WHITELIST.domains, ...(config.whitelistedDomains || [])],
      whitelistedCommands: [...WHITELIST.commands, ...(config.whitelistedCommands || [])],
      strictMode: config.strictMode || false,
    };
    this.findings = [];
  }

  /**
   * Scan a skill file or directory
   */
  scanSkill(filePath) {
    this.findings = [];
    
    let content;
    try {
      const stats = fs.statSync(filePath);
      
      if (stats.isDirectory()) {
        return this.scanDirectory(filePath);
      } else {
        content = fs.readFileSync(filePath, 'utf8');
        return this.scanContent(content, filePath);
      }
    } catch (error) {
      return {
        success: false,
        error: `Failed to scan file: ${error.message}`,
      };
    }
  }

  /**
   * Scan a directory for all skill files
   */
  scanDirectory(dirPath) {
    const results = {
      scannedFiles: [],
      totalFindings: 0,
      highestRisk: 'INFO',
    };

    try {
      const files = this.getAllFiles(dirPath);
      
      for (const file of files) {
        if (file.endsWith('.md') || file.endsWith('.js') || file.endsWith('.ts')) {
          const content = fs.readFileSync(file, 'utf8');
          const scanResult = this.scanContent(content, file);
          results.scannedFiles.push({
            file: path.relative(dirPath, file),
            ...scanResult,
          });
          results.totalFindings += scanResult.findings.length;
          
          if (this.compareRiskLevels(scanResult.overallRisk, results.highestRisk) > 0) {
            results.highestRisk = scanResult.overallRisk;
          }
        }
      }

      return {
        success: true,
        ...results,
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }

  /**
   * Get all files in directory recursively
   */
  getAllFiles(dirPath, arrayOfFiles = []) {
    const files = fs.readdirSync(dirPath);

    files.forEach(file => {
      const filePath = path.join(dirPath, file);
      if (fs.statSync(filePath).isDirectory()) {
        arrayOfFiles = this.getAllFiles(filePath, arrayOfFiles);
      } else {
        arrayOfFiles.push(filePath);
      }
    });

    return arrayOfFiles;
  }

  /**
   * Scan content for security issues
   */
  scanContent(content, fileName = 'unknown') {
    this.findings = [];
    const lines = content.split('\n');

    // Check each security pattern
    for (const [patternName, patternDef] of Object.entries(SECURITY_PATTERNS)) {
      for (const regex of patternDef.patterns) {
        const matches = content.match(regex);
        
        if (matches && matches.length > 0) {
          // Check if it's whitelisted
          if (!this.isWhitelisted(matches[0])) {
            const lineNumbers = this.findLineNumbers(content, regex);
            
            this.findings.push({
              pattern: patternName,
              level: patternDef.level,
              description: patternDef.description,
              recommendation: patternDef.recommendation,
              matches: matches.slice(0, 3), // Limit to first 3 matches
              lineNumbers: lineNumbers.slice(0, 3),
              count: matches.length,
            });
          }
        }
      }
    }

    // Calculate overall risk
    const overallRisk = this.calculateOverallRisk();

    return {
      success: true,
      fileName,
      scanTime: new Date().toISOString(),
      overallRisk,
      riskScore: RISK_LEVELS[overallRisk].score,
      findings: this.findings,
      summary: this.generateSummary(),
      recommendation: this.generateRecommendation(overallRisk),
    };
  }

  /**
   * Find line numbers where pattern matches
   */
  findLineNumbers(content, regex) {
    const lines = content.split('\n');
    const lineNumbers = [];

    lines.forEach((line, index) => {
      if (regex.test(line)) {
        lineNumbers.push(index + 1);
      }
    });

    return lineNumbers;
  }

  /**
   * Check if a match is whitelisted
   */
  isWhitelisted(match) {
    // Check whitelisted domains
    for (const domain of this.config.whitelistedDomains) {
      if (match.includes(domain)) {
        return true;
      }
    }

    // Check whitelisted commands
    for (const cmd of this.config.whitelistedCommands) {
      if (match.includes(cmd)) {
        return true;
      }
    }

    return false;
  }

  /**
   * Calculate overall risk level
   */
  calculateOverallRisk() {
    if (this.findings.length === 0) {
      return 'INFO';
    }

    const levels = this.findings.map(f => f.level);

    if (levels.includes('CRITICAL')) return 'CRITICAL';
    if (levels.includes('HIGH')) return 'HIGH';
    if (levels.includes('MEDIUM')) return 'MEDIUM';
    if (levels.includes('LOW')) return 'LOW';
    return 'INFO';
  }

  /**
   * Compare risk levels
   */
  compareRiskLevels(level1, level2) {
    return RISK_LEVELS[level1].score - RISK_LEVELS[level2].score;
  }

  /**
   * Generate summary statistics
   */
  generateSummary() {
    const summary = {
      total: this.findings.length,
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
    };

    this.findings.forEach(finding => {
      summary[finding.level.toLowerCase()]++;
    });

    return summary;
  }

  /**
   * Generate installation recommendation
   */
  generateRecommendation(riskLevel) {
    const recommendations = {
      CRITICAL: '❌ DO NOT INSTALL - This skill has critical security issues that pose significant risk to your system.',
      HIGH: '⚠️ NOT RECOMMENDED - This skill has serious security concerns. Only install if you fully trust the author and have reviewed the code.',
      MEDIUM: '⚠️ CAUTION - This skill has some security concerns. Review the findings and consider contacting the author for improvements.',
      LOW: '✅ LIKELY SAFE - Minor issues detected. Review findings but generally safe to install from trusted sources.',
      INFO: '✅ SAFE - No security issues detected. This skill appears safe to install.',
    };

    return recommendations[riskLevel];
  }

  /**
   * Generate formatted report
   */
  generateReport(scanResult) {
    const risk = RISK_LEVELS[scanResult.overallRisk];
    
    let report = '\n';
    report += '═══════════════════════════════════════════════════\n';
    report += '           SECURITY SCAN REPORT\n';
    report += '═══════════════════════════════════════════════════\n\n';
    report += `Skill: ${scanResult.fileName}\n`;
    report += `Scanned: ${scanResult.scanTime}\n`;
    report += `Overall Risk: ${risk.emoji} ${risk.label}\n`;
    report += `Risk Score: ${risk.score}/100\n\n`;

    if (scanResult.findings.length > 0) {
      report += '─────────────── FINDINGS ───────────────\n\n';

      scanResult.findings.forEach((finding, index) => {
        const level = RISK_LEVELS[finding.level];
        report += `${index + 1}. [${level.emoji} ${level.label}] ${finding.description}\n`;
        report += `   Pattern: ${finding.pattern}\n`;
        
        if (finding.lineNumbers && finding.lineNumbers.length > 0) {
          report += `   Line(s): ${finding.lineNumbers.join(', ')}`;
          if (finding.count > finding.lineNumbers.length) {
            report += ` (and ${finding.count - finding.lineNumbers.length} more)`;
          }
          report += '\n';
        }
        
        if (finding.matches && finding.matches.length > 0) {
          report += `   Example: ${finding.matches[0].substring(0, 60)}${finding.matches[0].length > 60 ? '...' : ''}\n`;
        }
        
        report += `   ⚠️  ${finding.recommendation}\n\n`;
      });

      report += '─────────────── SUMMARY ─────────────────\n\n';
      report += `Total Issues: ${scanResult.summary.total}\n`;
      report += `  ${RISK_LEVELS.CRITICAL.emoji} Critical: ${scanResult.summary.critical}\n`;
      report += `  ${RISK_LEVELS.HIGH.emoji} High: ${scanResult.summary.high}\n`;
      report += `  ${RISK_LEVELS.MEDIUM.emoji} Medium: ${scanResult.summary.medium}\n`;
      report += `  ${RISK_LEVELS.LOW.emoji} Low: ${scanResult.summary.low}\n\n`;
    } else {
      report += '✅ No security issues detected!\n\n';
    }

    report += '─────────────── RECOMMENDATION ──────────────\n\n';
    report += scanResult.recommendation + '\n\n';
    report += '═══════════════════════════════════════════════════\n';

    return report;
  }
}

// Export for use as module
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { SecurityScanner, RISK_LEVELS, SECURITY_PATTERNS };
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node scanner.js <path-to-skill-file-or-directory>');
    console.log('Example: node scanner.js ./SKILL.md');
    console.log('Example: node scanner.js ~/.openclaw/skills/');
    process.exit(1);
  }

  const scanner = new SecurityScanner();
  const result = scanner.scanSkill(args[0]);

  if (!result.success) {
    console.error('Error:', result.error);
    process.exit(1);
  }

  if (result.scannedFiles) {
    // Directory scan
    console.log(`\nScanned ${result.scannedFiles.length} files`);
    console.log(`Total findings: ${result.totalFindings}`);
    console.log(`Highest risk: ${RISK_LEVELS[result.highestRisk].emoji} ${result.highestRisk}`);
    
    result.scannedFiles.forEach(fileResult => {
      if (fileResult.findings.length > 0) {
        console.log(scanner.generateReport(fileResult));
      }
    });
  } else {
    // Single file scan
    console.log(scanner.generateReport(result));
  }
}
