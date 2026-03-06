#!/usr/bin/env node
// scan.js - Main scanner for bomb-dog-sniff
// Security scanner for OpenClaw skills
// Version: 1.2.0 - Hardened Edition

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { PATTERNS, SEVERITY_SCORES, FALSE_POSITIVE_WHITELIST } = require('./patterns');

// Security constants
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB max file size
const MAX_LINE_LENGTH = 10000; // 10KB max line length (prevent ReDoS)
const MAX_FILES_PER_SCAN = 10000; // Prevent resource exhaustion
const MAX_FINDINGS_PER_FILE = 100; // Prevent output flooding
const MAX_TOTAL_FINDINGS = 500;

// File extensions to scan
const SCAN_EXTENSIONS = new Set([
  '.js', '.ts', '.mjs', '.cjs', '.jsx', '.tsx',
  '.json', '.jsonc',
  '.md', '.mdx',
  '.sh', '.bash', '.zsh',
  '.py', '.rb', '.pl', '.php',
  '.yml', '.yaml',
  '.Dockerfile', '.dockerfile',
  '.txt', // README, LICENSE, etc
]);

// Binary file signatures to skip
const BINARY_SIGNATURES = [
  Buffer.from([0x7F, 0x45, 0x4C, 0x46]), // ELF
  Buffer.from([0x4D, 0x5A]), // DOS/Windows executable
  Buffer.from([0xCA, 0xFE, 0xBA, 0xBE]), // Java class
  Buffer.from([0x50, 0x4B, 0x03, 0x04]), // ZIP (includes docx, jar, etc)
  Buffer.from([0x1F, 0x8B]), // GZIP
  Buffer.from([0xFF, 0xD8, 0xFF]), // JPEG
  Buffer.from([0x89, 0x50, 0x4E, 0x47]), // PNG
  Buffer.from([0x25, 0x50, 0x44, 0x46]), // PDF
];

// Generate unique scan ID with entropy
function generateScanId() {
  const date = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const random = crypto.randomBytes(4).toString('hex');
  return `bds-${date}-${random}`;
}

// Check if buffer looks like binary
function isBinaryFile(buffer) {
  if (!buffer || buffer.length === 0) return false;
  
  // Check file signatures
  for (const sig of BINARY_SIGNATURES) {
    if (buffer.slice(0, sig.length).equals(sig)) {
      return true;
    }
  }
  
  // Check for high ratio of null bytes
  let nullBytes = 0;
  const sampleSize = Math.min(buffer.length, 8192);
  for (let i = 0; i < sampleSize; i++) {
    if (buffer[i] === 0) nullBytes++;
  }
  
  // If more than 10% null bytes, likely binary
  return (nullBytes / sampleSize) > 0.1;
}

// Check if file is likely a test file
function isTestFile(filePath) {
  const basename = path.basename(filePath);
  const dir = path.dirname(filePath);
  return (
    basename.includes('.test.') ||
    basename.includes('.spec.') ||
    basename.includes('_test.') ||
    basename.includes('_spec.') ||
    dir.includes('__tests__') ||
    dir.includes('/test/') ||
    dir.includes('/tests/')
  );
}

// Check if line might be a false positive
function isLikelyFalsePositive(line, category) {
  const trimmed = line.trim();
  
  // Skip comments
  if (trimmed.startsWith('//') || trimmed.startsWith('#') || trimmed.startsWith('*') || trimmed.startsWith('/*')) {
    // But still check if it's a very suspicious comment (documentation of malicious behavior)
    if (/TODO.*hack|FIXME.*bypass|XXX.*exploit/i.test(trimmed)) {
      return false;
    }
    return true;
  }
  
  // Skip markdown tables (documentation)
  if (/^\|.*\|$/.test(trimmed)) return true;
  
  // Skip markdown headers
  if (/^#{1,6}\s/.test(trimmed)) return true;
  
  // Skip markdown list items that are documentation
  if (/^[-*]\s+`/.test(trimmed) && !/(?:fetch|post|send|exec|eval|curl)/i.test(trimmed)) {
    return true;
  }
  
  // Skip documentation examples (but not actual code examples)
  if (/example|Example|EXAMPLE/i.test(trimmed) && !/(?:fetch|post|send|exec|eval|curl|wget)/i.test(trimmed)) {
    return true;
  }
  
  // Skip markdown code blocks with language hints
  if (/^```\w*$/.test(trimmed)) return true;
  
  // Skip lines that are clearly documentation descriptions
  if (/^[\s]*[-*]\s+[A-Za-z].*:\s+/.test(trimmed) && !/(?:privateKey|secret|password)/i.test(trimmed)) {
    return true;
  }
  
  // For crypto_harvester: skip unless there's actual key material or exfiltration
  if (category === 'crypto_harvester') {
    // Skip unless it looks like actual code with key material
    const hasKeyMaterial = /['"`][a-fA-F0-9]{32,}['"`]/.test(trimmed) || 
                           /['"`][5KL][1-9A-HJ-NP-Za-km-z]{50,51}['"`]/.test(trimmed);
    const hasExfiltration = /(?:fetch|post|send|axios|request|curl|wget)/i.test(trimmed);
    
    if (!hasKeyMaterial && !hasExfiltration) {
      return true;
    }
  }
  
  // For keylogger: skip unless there's actual event capture
  if (category === 'keylogger') {
    const hasEventCapture = /addEventListener|onkey|keypress|keydown|keyup/i.test(trimmed);
    const hasExfiltration = /(?:fetch|post|send|axios|request|localStorage|sessionStorage)/i.test(trimmed);
    
    if (!hasEventCapture || !hasExfiltration) {
      return true;
    }
  }
  
  return false;
}

// Calculate risk level from score
function getRiskLevel(score) {
  if (score >= 70) return 'MALICIOUS';
  if (score >= 40) return 'SUSPICIOUS';
  if (score >= 20) return 'LOW';
  return 'SAFE';
}

// Get emoji for risk level
function getRiskEmoji(level) {
  switch (level) {
    case 'MALICIOUS': return '☠️';
    case 'SUSPICIOUS': return '🚫';
    case 'LOW': return '⚠️';
    default: return '✅';
  }
}

// Get recommendation based on risk level
function getRecommendation(level, findings, isTestFile) {
  const testNote = isTestFile ? ' (Note: Findings in test files may be legitimate test cases)' : '';
  
  switch (level) {
    case 'MALICIOUS':
      return `MALICIOUS - Do not install. Found ${findings.length} critical security issues.${testNote}`;
    case 'SUSPICIOUS':
      return `SUSPICIOUS - Manual review required. Found ${findings.length} potential security concerns.${testNote}`;
    case 'LOW':
      return `LOW RISK - Minor concerns found. Review recommended.${testNote}`;
    default:
      return `SAFE - No malicious patterns detected.`;
  }
}

// Calculate entropy of a string (for detecting encoded payloads)
function calculateEntropy(str) {
  if (!str || str.length === 0) return 0;
  
  const freq = {};
  for (const char of str) {
    freq[char] = (freq[char] || 0) + 1;
  }
  
  let entropy = 0;
  const len = str.length;
  for (const count of Object.values(freq)) {
    const p = count / len;
    entropy -= p * Math.log2(p);
  }
  
  return entropy;
}

// Scan a single file for patterns
function scanFile(filePath, content, options = {}) {
  const findings = [];
  const lines = content.split('\n');
  const fileIsTest = isTestFile(filePath);
  
  // Early exit for empty files
  if (lines.length === 0 || (lines.length === 1 && lines[0].trim() === '')) {
    return findings;
  }
  
  // Track seen matches to avoid duplicates
  const seenMatches = new Set();
  
  for (const [category, config] of Object.entries(PATTERNS)) {
    for (const pattern of config.patterns) {
      try {
        // Reset lastIndex for regexes with global flag
        if (pattern.global) {
          pattern.lastIndex = 0;
        }
        
        // Check each line
        lines.forEach((line, index) => {
          // Skip overly long lines (ReDoS protection)
          if (line.length > MAX_LINE_LENGTH) {
            return;
          }
          
          if (pattern.test(line)) {
            // Reset lastIndex after test
            if (pattern.global) {
              pattern.lastIndex = 0;
            }
            
            // Check for false positives
            if (isLikelyFalsePositive(line, category)) {
              return;
            }
            
            // Create unique key for deduplication
            const matchKey = `${category}:${index + 1}:${pattern.toString()}`;
            if (seenMatches.has(matchKey)) {
              return;
            }
            seenMatches.add(matchKey);
            
            // Calculate contextual score adjustment
            let adjustedSeverity = config.severity;
            
            // Reduce severity for test files (often test malicious patterns)
            if (fileIsTest && config.severity !== 'CRITICAL') {
              const severityOrder = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW'];
              const currentIdx = severityOrder.indexOf(config.severity);
              if (currentIdx < severityOrder.length - 1) {
                adjustedSeverity = severityOrder[currentIdx + 1];
              }
            }
            
            // Check for high entropy strings (likely encoded payload)
            const excerpt = line.trim().slice(0, 150);
            if (excerpt.length > 50) {
              const entropy = calculateEntropy(excerpt);
              if (entropy > 4.5) { // High entropy threshold
                adjustedSeverity = 'HIGH';
              }
            }
            
            findings.push({
              severity: adjustedSeverity,
              category,
              file: path.relative(process.cwd(), filePath),
              line: index + 1,
              description: config.description,
              excerpt: excerpt,
              confidence: config.confidence || 'medium',
              mitigation: config.mitigation || 'Review and verify this code.',
              isTestFile: fileIsTest,
            });
          }
          
          // Reset lastIndex after test
          if (pattern.global) {
            pattern.lastIndex = 0;
          }
        });
        
        // Check full content for multi-line patterns (limited to prevent ReDoS)
        if (pattern.multiline || (pattern.flags && pattern.flags.includes('m'))) {
          const truncatedContent = content.slice(0, 100000); // Limit for performance
          let match;
          const patternCopy = new RegExp(pattern.source, pattern.flags);
          
          while ((match = patternCopy.exec(truncatedContent)) !== null) {
            const lineNum = truncatedContent.substring(0, match.index).split('\n').length;
            
            // Create unique key
            const matchKey = `${category}:${lineNum}:multiline`;
            if (seenMatches.has(matchKey)) {
              continue;
            }
            seenMatches.add(matchKey);
            
            findings.push({
              severity: config.severity,
              category,
              file: path.relative(process.cwd(), filePath),
              line: lineNum,
              description: config.description,
              excerpt: match[0].slice(0, 150),
              confidence: config.confidence || 'medium',
              mitigation: config.mitigation || 'Review and verify this code.',
              isTestFile: fileIsTest,
            });
            
            // Limit multi-line matches per pattern
            if (findings.length >= MAX_FINDINGS_PER_FILE) {
              break;
            }
          }
        }
      } catch (err) {
        // Log pattern errors but don't crash
        console.error(`Pattern error in ${category}: ${err.message}`);
      }
      
      // Limit total findings per file
      if (findings.length >= MAX_FINDINGS_PER_FILE) {
        findings.push({
          severity: 'INFO',
          category: 'scan_limit',
          file: path.relative(process.cwd(), filePath),
          line: 0,
          description: `Scan limit reached (${MAX_FINDINGS_PER_FILE} findings per file). File may have more issues.`,
          excerpt: '',
          confidence: 'high',
          mitigation: 'Manually review this file.',
          isTestFile: fileIsTest,
        });
        break;
      }
    }
    
    if (findings.length >= MAX_FINDINGS_PER_FILE) {
      break;
    }
  }
  
  return findings;
}

// Recursively get all files in directory
function getAllFiles(dirPath, arrayOfFiles = [], options = {}) {
  // Prevent infinite recursion via symlinks
  const { maxDepth = 20, currentDepth = 0, visitedInodes = new Set() } = options;
  
  if (currentDepth > maxDepth) {
    console.error(`Warning: Max directory depth (${maxDepth}) reached at ${dirPath}`);
    return arrayOfFiles;
  }
  
  if (arrayOfFiles.length >= MAX_FILES_PER_SCAN) {
    console.error(`Warning: Max files per scan (${MAX_FILES_PER_SCAN}) reached`);
    return arrayOfFiles;
  }
  
  let files;
  try {
    files = fs.readdirSync(dirPath, { withFileTypes: true });
  } catch (err) {
    console.error(`Warning: Could not read directory ${dirPath}: ${err.message}`);
    return arrayOfFiles;
  }
  
  for (const dirent of files) {
    const fullPath = path.join(dirPath, dirent.name);
    
    // Skip hidden files and common non-code directories
    if (dirent.name.startsWith('.') || dirent.name === 'node_modules' || 
        dirent.name === 'vendor' || dirent.name === 'dist' || dirent.name === 'build' ||
        dirent.name === 'coverage' || dirent.name === '.git') {
      continue;
    }
    
    if (dirent.isDirectory()) {
      // Check for symlink loops
      try {
        const stats = fs.statSync(fullPath);
        const inodeKey = `${stats.dev}:${stats.ino}`;
        if (visitedInodes.has(inodeKey)) {
          console.error(`Warning: Symlink loop detected at ${fullPath}`);
          continue;
        }
        visitedInodes.add(inodeKey);
        
        getAllFiles(fullPath, arrayOfFiles, {
          maxDepth,
          currentDepth: currentDepth + 1,
          visitedInodes,
        });
      } catch (err) {
        console.error(`Warning: Could not stat ${fullPath}: ${err.message}`);
      }
    } else if (dirent.isFile()) {
      // Check extension
      const ext = path.extname(dirent.name).toLowerCase();
      const basename = dirent.name.toLowerCase();
      
      // Include files with matching extensions or known names
      if (SCAN_EXTENSIONS.has(ext) || SCAN_EXTENSIONS.has(basename) ||
          basename === 'dockerfile' || basename.startsWith('dockerfile.')) {
        arrayOfFiles.push(fullPath);
      }
    }
    
    if (arrayOfFiles.length >= MAX_FILES_PER_SCAN) {
      break;
    }
  }
  
  return arrayOfFiles;
}

// Calculate file hash for integrity tracking
function calculateFileHash(filePath) {
  try {
    const content = fs.readFileSync(filePath);
    return crypto.createHash('sha256').update(content).digest('hex').slice(0, 16);
  } catch (err) {
    return null;
  }
}

// Main scan function
function scanSkill(skillPath, options = {}) {
  const scanId = generateScanId();
  const timestamp = new Date().toISOString();
  const startTime = Date.now();
  
  // Validate path
  if (!fs.existsSync(skillPath)) {
    return {
      error: `Path does not exist: ${skillPath}`,
      scanId,
      timestamp,
      duration: 0,
    };
  }
  
  const stats = fs.statSync(skillPath);
  if (!stats.isDirectory()) {
    return {
      error: `Path is not a directory: ${skillPath}`,
      scanId,
      timestamp,
      duration: 0,
    };
  }
  
  // Get all files to scan
  let filesToScan = [];
  try {
    filesToScan = getAllFiles(skillPath);
  } catch (err) {
    return {
      error: `Failed to read directory: ${err.message}`,
      scanId,
      timestamp,
      duration: Date.now() - startTime,
    };
  }
  
  // Track scan statistics
  const scanStats = {
    totalFiles: filesToScan.length,
    scannedFiles: 0,
    skippedFiles: 0,
    binaryFiles: 0,
    emptyFiles: 0,
    largeFiles: 0,
    errorFiles: 0,
  };
  
  // Scan each file
  const allFindings = [];
  const fileHashes = {};
  
  for (const file of filesToScan) {
    try {
      // Check file size first
      const fileStat = fs.statSync(file);
      
      if (fileStat.size === 0) {
        scanStats.emptyFiles++;
        scanStats.skippedFiles++;
        continue;
      }
      
      if (fileStat.size > MAX_FILE_SIZE) {
        scanStats.largeFiles++;
        scanStats.skippedFiles++;
        console.error(`Warning: Skipping large file ${file} (${(fileStat.size / 1024 / 1024).toFixed(2)}MB)`);
        continue;
      }
      
      // Read file and check if binary
      const buffer = fs.readFileSync(file);
      
      if (isBinaryFile(buffer)) {
        scanStats.binaryFiles++;
        scanStats.skippedFiles++;
        continue;
      }
      
      // Calculate hash for integrity
      const hash = crypto.createHash('sha256').update(buffer).digest('hex').slice(0, 16);
      fileHashes[path.relative(skillPath, file)] = hash;
      
      // Convert to string for scanning
      const content = buffer.toString('utf8');
      const findings = scanFile(file, content, options);
      allFindings.push(...findings);
      
      scanStats.scannedFiles++;
      
      // Check total findings limit
      if (allFindings.length >= MAX_TOTAL_FINDINGS) {
        allFindings.push({
          severity: 'INFO',
          category: 'scan_limit',
          file: 'SCAN_SUMMARY',
          line: 0,
          description: `Total scan limit reached (${MAX_TOTAL_FINDINGS} findings). Scan stopped.`,
          excerpt: '',
          confidence: 'high',
          mitigation: 'This skill has too many findings. Treat as high risk.',
          isTestFile: false,
        });
        break;
      }
    } catch (err) {
      scanStats.errorFiles++;
      console.error(`Warning: Could not read ${file}: ${err.message}`);
    }
  }
  
  // Calculate risk score
  let riskScore = 0;
  const severityCounts = {};
  const categoryCounts = {};
  
  for (const finding of allFindings) {
    if (finding.category === 'scan_limit') continue;
    
    const score = SEVERITY_SCORES[finding.severity] || 1;
    // Apply confidence multiplier
    const confidenceMultiplier = finding.confidence === 'high' ? 1.0 : 
                                  finding.confidence === 'medium' ? 0.75 : 0.5;
    riskScore += score * confidenceMultiplier;
    
    severityCounts[finding.severity] = (severityCounts[finding.severity] || 0) + 1;
    categoryCounts[finding.category] = (categoryCounts[finding.category] || 0) + 1;
  }
  
  // Cap at 100
  riskScore = Math.min(Math.round(riskScore), 100);
  
  // Determine risk level
  const riskLevel = getRiskLevel(riskScore);
  
  // Generate report
  const duration = Date.now() - startTime;
  const hasTestFiles = allFindings.some(f => f.isTestFile);
  
  const report = {
    scanId,
    timestamp,
    duration,
    targetPath: path.resolve(skillPath),
    riskScore,
    riskLevel,
    riskEmoji: getRiskEmoji(riskLevel),
    severityCounts,
    categoryCounts,
    findings: allFindings,
    stats: {
      ...scanStats,
      totalFindings: allFindings.filter(f => f.category !== 'scan_limit').length,
    },
    fileHashes,
    recommendation: getRecommendation(riskLevel, allFindings, hasTestFiles),
    scanVersion: '1.2.0',
  };
  
  return report;
}

// Format findings for terminal output
function formatFindingsForTerminal(report) {
  const lines = [];
  
  if (report.findings.length === 0) {
    return 'No findings.';
  }
  
  // Group by severity
  const bySeverity = {};
  for (const f of report.findings) {
    if (f.category === 'scan_limit') continue;
    bySeverity[f.severity] = bySeverity[f.severity] || [];
    bySeverity[f.severity].push(f);
  }
  
  const severityOrder = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'];
  
  for (const severity of severityOrder) {
    const findings = bySeverity[severity];
    if (!findings || findings.length === 0) continue;
    
    const icon = severity === 'CRITICAL' ? '🔴' : 
                 severity === 'HIGH' ? '🟠' :
                 severity === 'MEDIUM' ? '🟡' : '⚪';
    
    lines.push(`\n${icon} ${severity} (${findings.length})`);
    lines.push('─'.repeat(50));
    
    // Show first 5 of each severity
    findings.slice(0, 5).forEach(f => {
      lines.push(`  ${f.category}: ${f.file}:${f.line}`);
      lines.push(`    ${f.description}`);
      if (f.excerpt) {
        const excerpt = f.excerpt.length > 60 ? f.excerpt.slice(0, 60) + '...' : f.excerpt;
        lines.push(`    Code: ${excerpt}`);
      }
      if (f.confidence) {
        lines.push(`    Confidence: ${f.confidence}`);
      }
      lines.push('');
    });
    
    if (findings.length > 5) {
      lines.push(`  ... and ${findings.length - 5} more ${severity.toLowerCase()} issues`);
    }
  }
  
  return lines.join('\n');
}

// CLI entry point
function main() {
  const args = process.argv.slice(2);
  
  // Parse options
  const options = {
    json: false,
    threshold: 40,
    verbose: false,
  };
  
  const positional = [];
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--json' || args[i] === '-j') {
      options.json = true;
    } else if (args[i] === '--verbose' || args[i] === '-v') {
      options.verbose = true;
    } else if ((args[i] === '--threshold' || args[i] === '-t') && args[i + 1]) {
      options.threshold = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === '--help' || args[i] === '-h') {
      console.log(`
Usage: node scan.js [options] <path-to-skill>

Options:
  -j, --json          Output JSON only
  -v, --verbose       Verbose output
  -t, --threshold N   Set risk threshold (default: 40)
  -h, --help          Show this help

Examples:
  node scan.js ./skills/suspicious-skill
  node scan.js -j ./untrusted-skill > report.json
  node scan.js -v -t 20 ./skill-to-audit

Exit codes:
  0 - SAFE (risk score 0-19) or below threshold
  1 - Error or invalid arguments
  2 - Risky (risk score >= threshold, default 40)
`);
      process.exitCode = 0;
      return;
    } else if (!args[i].startsWith('-')) {
      positional.push(args[i]);
    }
  }
  
  if (positional.length === 0) {
    console.error('Error: No path specified. Use --help for usage.');
    process.exitCode = 1;
    return;
  }
  
  const skillPath = path.resolve(positional[0]);
  
  if (!options.json) {
    console.error(`🔍 Bomb-Dog-Sniff Security Scanner v1.2.0`);
    console.error(`Target: ${skillPath}`);
    console.error('');
  }
  
  const report = scanSkill(skillPath, options);
  
  if (report.error) {
    console.error(`❌ Error: ${report.error}`);
    process.exitCode = 1;
    return;
  }
  
  // Output JSON or formatted text
  if (options.json) {
    console.log(JSON.stringify(report, null, 2));
  } else {
    // Print findings
    console.error(formatFindingsForTerminal(report));
    
    // Print summary
    console.error('\n' + '═'.repeat(50));
    console.error('SCAN SUMMARY');
    console.error('═'.repeat(50));
    console.error(`${report.riskEmoji} Risk Score: ${report.riskScore}/100`);
    console.error(`   Risk Level: ${report.riskLevel}`);
    console.error(`   Duration: ${report.duration}ms`);
    console.error(`   Files Scanned: ${report.stats.scannedFiles}/${report.stats.totalFiles}`);
    if (report.stats.skippedFiles > 0) {
      console.error(`   Files Skipped: ${report.stats.skippedFiles} (binary/empty/large)`);
    }
    console.error(`   Findings: ${report.stats.totalFindings}`);
    
    if (Object.keys(report.severityCounts).length > 0) {
      console.error('\n   Severity Breakdown:');
      for (const [sev, count] of Object.entries(report.severityCounts)) {
        const icon = sev === 'CRITICAL' ? '🔴' : sev === 'HIGH' ? '🟠' : sev === 'MEDIUM' ? '🟡' : '⚪';
        console.error(`     ${icon} ${sev}: ${count}`);
      }
    }
    
    console.error('\n📋 Recommendation:');
    console.error(`   ${report.recommendation}`);
    console.error('');
    console.error(`Scan ID: ${report.scanId}`);
  }
  
  // Set exit code
  if (report.riskScore >= options.threshold) {
    process.exitCode = 2;
  } else {
    process.exitCode = 0;
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

module.exports = { 
  scanSkill, 
  scanFile,
  isBinaryFile,
  calculateEntropy,
  MAX_FILE_SIZE,
  MAX_LINE_LENGTH,
};
