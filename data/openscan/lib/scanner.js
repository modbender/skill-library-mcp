/**
 * Main Scanner - orchestrates all detection modules
 * Provides unified interface for scanning binaries and scripts
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { execSync } = require('child_process');

const { calculateEntropy, detectPacking } = require('./entropy');
const { parseMachO, isMachO, calculateThreatScore: machoThreatScore } = require('./macho');
const { parseELF, isELF, calculateThreatScore: elfThreatScore } = require('./elf');
const { scanPatterns, calculatePatternScore } = require('./patterns');

// Threat level thresholds
const THREAT_LEVELS = {
  CLEAN: { max: 20, label: 'CLEAN', color: '\x1b[32m' },
  LOW: { max: 40, label: 'LOW', color: '\x1b[33m' },
  MEDIUM: { max: 60, label: 'MEDIUM', color: '\x1b[38;5;208m' },
  HIGH: { max: 80, label: 'HIGH', color: '\x1b[31m' },
  CRITICAL: { max: 100, label: 'CRITICAL', color: '\x1b[35m' }
};

/**
 * Scan a single file
 * @param {string} filePath - Path to file
 * @param {object} options - Scan options
 * @returns {object} Scan result
 */
async function scanFile(filePath, options = {}) {
  const result = {
    path: filePath,
    name: path.basename(filePath),
    exists: false,
    size: 0,
    type: 'unknown',
    hashes: {},
    threatScore: 0,
    threatLevel: 'CLEAN',
    findings: [],
    details: {}
  };

  // Check file exists
  if (!fs.existsSync(filePath)) {
    result.findings.push('File not found');
    return result;
  }

  result.exists = true;
  const stats = fs.statSync(filePath);
  result.size = stats.size;

  // Skip very large files unless forced
  const maxSize = options.maxSize || 50 * 1024 * 1024; // 50MB default
  if (result.size > maxSize) {
    result.findings.push(`File too large (${(result.size / 1024 / 1024).toFixed(1)}MB), skipped`);
    return result;
  }

  // Read file
  const buffer = fs.readFileSync(filePath);

  // Calculate hashes
  result.hashes = {
    md5: crypto.createHash('md5').update(buffer).digest('hex'),
    sha256: crypto.createHash('sha256').update(buffer).digest('hex')
  };

  // Determine file type and parse accordingly
  if (isMachO(buffer)) {
    result.type = 'macho';
    result.details.binary = parseMachO(buffer);
    if (result.details.binary) {
      result.findings.push(...(result.details.binary.suspiciousFindings || []));
    }
  } else if (isELF(buffer)) {
    result.type = 'elf';
    result.details.binary = parseELF(buffer);
    if (result.details.binary) {
      result.findings.push(...(result.details.binary.suspiciousFindings || []));
    }
  } else if (isScript(buffer, filePath)) {
    result.type = 'script';
    result.details.script = analyzeScript(buffer, filePath);
    result.findings.push(...(result.details.script.findings || []));
  } else {
    result.type = 'data';
  }

  // Pattern scanning
  result.details.patterns = scanPatterns(buffer);
  result.findings.push(...result.details.patterns.findings);

  // Entropy analysis
  result.details.packing = detectPacking(buffer);
  if (result.details.packing.isPacked) {
    result.findings.push(`Possibly packed (entropy: ${result.details.packing.entropy.toFixed(2)})`);
  }

  // Calculate threat score
  result.threatScore = calculateOverallScore(result);
  result.threatLevel = getThreatLevel(result.threatScore);

  // macOS: Check code signature if available
  if (process.platform === 'darwin' && (result.type === 'macho' || isExecutable(filePath))) {
    result.details.codesign = checkCodeSignature(filePath);
    if (!result.details.codesign.valid) {
      result.findings.push('Invalid or missing code signature');
      result.threatScore = Math.min(result.threatScore + 15, 100);
      result.threatLevel = getThreatLevel(result.threatScore);
    }
  }

  return result;
}

/**
 * Check if buffer/path indicates a script
 */
function isScript(buffer, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const scriptExts = ['.sh', '.bash', '.zsh', '.py', '.rb', '.pl', '.js', '.php'];
  
  if (scriptExts.includes(ext)) return true;

  // Check for shebang
  if (buffer.length >= 2 && buffer[0] === 0x23 && buffer[1] === 0x21) {
    return true;
  }

  return false;
}

/**
 * Analyze a script file
 */
function analyzeScript(buffer, filePath) {
  const content = buffer.toString('utf8');
  const findings = [];
  const ext = path.extname(filePath).toLowerCase();

  // Dangerous patterns in shell scripts
  const dangerousPatterns = [
    { pattern: /curl\s+[^|]*\|\s*(ba)?sh/gi, name: 'curl pipe to shell' },
    { pattern: /wget\s+[^|]*\|\s*(ba)?sh/gi, name: 'wget pipe to shell' },
    { pattern: /eval\s*\(/gi, name: 'eval usage' },
    { pattern: /base64\s+-d/gi, name: 'base64 decode' },
    { pattern: /\$\(.*base64.*\)/gi, name: 'base64 in command substitution' },
    { pattern: /nc\s+-[el]/gi, name: 'netcat listener/exec' },
    { pattern: /\/dev\/tcp\//gi, name: 'bash /dev/tcp network' },
    { pattern: /rm\s+-rf\s+[\/~]/gi, name: 'dangerous rm -rf' },
    { pattern: /chmod\s+[0-7]*777/gi, name: 'chmod 777' },
    { pattern: />\s*\/etc\//gi, name: 'writing to /etc' },
    { pattern: /crontab/gi, name: 'crontab modification' },
    { pattern: /launchctl/gi, name: 'launchctl usage' },
    { pattern: /DYLD_INSERT_LIBRARIES/gi, name: 'DYLD injection' },
    { pattern: /LD_PRELOAD/gi, name: 'LD_PRELOAD injection' }
  ];

  for (const { pattern, name } of dangerousPatterns) {
    if (pattern.test(content)) {
      findings.push(`Dangerous pattern: ${name}`);
    }
  }

  // Check for obfuscation indicators
  const obfuscationIndicators = [
    { check: () => (content.match(/\\x[0-9a-f]{2}/gi) || []).length > 20, name: 'Heavy hex escaping' },
    { check: () => (content.match(/\$'\\/g) || []).length > 10, name: 'ANSI-C quoting abuse' },
    { check: () => content.split('\n').some(l => l.length > 1000), name: 'Very long lines' }
  ];

  for (const { check, name } of obfuscationIndicators) {
    if (check()) {
      findings.push(`Obfuscation indicator: ${name}`);
    }
  }

  return {
    type: ext || 'shell',
    lines: content.split('\n').length,
    findings
  };
}

/**
 * Check if file is executable
 */
function isExecutable(filePath) {
  try {
    const stats = fs.statSync(filePath);
    return !!(stats.mode & fs.constants.S_IXUSR);
  } catch {
    return false;
  }
}

/**
 * Check code signature on macOS
 */
function checkCodeSignature(filePath) {
  try {
    execSync(`codesign --verify --deep --strict "${filePath}" 2>&1`, {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return { valid: true, signed: true };
  } catch (err) {
    const output = err.stdout || err.stderr || '';
    if (output.includes('not signed')) {
      return { valid: false, signed: false, error: 'Not signed' };
    }
    return { valid: false, signed: true, error: output.trim() };
  }
}

/**
 * Calculate overall threat score
 */
function calculateOverallScore(result) {
  let score = 0;

  // Binary analysis score
  if (result.type === 'macho' && result.details.binary) {
    score += machoThreatScore(result.details.binary) * 0.4;
  } else if (result.type === 'elf' && result.details.binary) {
    score += elfThreatScore(result.details.binary) * 0.4;
  } else if (result.type === 'script' && result.details.script) {
    score += result.details.script.findings.length * 10;
  }

  // Pattern score
  if (result.details.patterns) {
    score += calculatePatternScore(result.details.patterns) * 0.4;
  }

  // Packing score
  if (result.details.packing && result.details.packing.isPacked) {
    score += 20;
  }

  return Math.min(Math.round(score), 100);
}

/**
 * Get threat level from score
 */
function getThreatLevel(score) {
  for (const [level, config] of Object.entries(THREAT_LEVELS)) {
    if (score <= config.max) {
      return level;
    }
  }
  return 'CRITICAL';
}

/**
 * Scan a directory recursively
 */
async function scanDirectory(dirPath, options = {}) {
  const results = [];
  const maxDepth = options.maxDepth || 10;

  async function walk(dir, depth) {
    if (depth > maxDepth) return;

    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      // Skip hidden files/dirs unless requested
      if (!options.includeHidden && entry.name.startsWith('.')) {
        continue;
      }

      if (entry.isDirectory()) {
        // Skip node_modules, .git, etc.
        if (['node_modules', '.git', '__pycache__', 'venv'].includes(entry.name)) {
          continue;
        }
        await walk(fullPath, depth + 1);
      } else if (entry.isFile()) {
        const result = await scanFile(fullPath, options);
        results.push(result);
      }
    }
  }

  await walk(dirPath, 0);
  return results;
}

/**
 * Format scan result for display
 */
function formatResult(result, options = {}) {
  const reset = '\x1b[0m';
  const levelConfig = THREAT_LEVELS[result.threatLevel] || THREAT_LEVELS.CLEAN;
  const color = options.noColor ? '' : levelConfig.color;
  const colorReset = options.noColor ? '' : reset;

  let output = '';
  output += `\n${color}[${levelConfig.label}]${colorReset} ${result.name}\n`;
  output += `  Path: ${result.path}\n`;
  output += `  Type: ${result.type} | Size: ${(result.size / 1024).toFixed(1)}KB\n`;
  output += `  Score: ${result.threatScore}/100\n`;

  if (result.hashes.sha256) {
    output += `  SHA256: ${result.hashes.sha256}\n`;
  }

  if (result.findings.length > 0) {
    output += `  Findings:\n`;
    for (const finding of result.findings.slice(0, 10)) {
      output += `    - ${finding}\n`;
    }
    if (result.findings.length > 10) {
      output += `    ... and ${result.findings.length - 10} more\n`;
    }
  }

  return output;
}

module.exports = {
  scanFile,
  scanDirectory,
  formatResult,
  THREAT_LEVELS,
  getThreatLevel
};
