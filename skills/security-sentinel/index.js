const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

/**
 * Security Sentinel - Unified Scanner
 * Checks for:
 * 1. Dependency vulnerabilities (npm audit)
 * 2. Exposed secrets (API keys, Tokens)
 * 3. File permission risks (world-writable)
 */

const SECRET_PATTERNS = [
  { name: 'Generic API Key', regex: /api[_-]?key['"]?\s*[:=]\s*['"]?[\w\-]{20,}['"]?/i },
  { name: 'Password', regex: /password['"]?\s*[:=]\s*['"]?[\w\-!@#$%^&*()]{8,}['"]?/i },
  { name: 'Private Key', regex: /-----BEGIN PRIVATE KEY-----/ },
  { name: 'Feishu App Secret', regex: /app_secret['"]?\s*[:=]\s*['"]?[\w\-]{20,}['"]?/i }
];

const IGNORED_PATHS = [
  'node_modules',
  '.git',
  'logs',
  'temp',
  '.openclaw/cache',
  'memory' // Add memory to ignored paths to reduce noise
];

async function scan(options = {}) {
  const report = {
    timestamp: new Date().toISOString(),
    vulnerabilities: {},
    secrets: [],
    permissions: [],
    status: 'clean'
  };

  console.log('[Sentinel] Starting security scan...');

  // 1. Dependency Scan (npm audit)
  // Skip if --skip-audit
  if (!options.skipAudit) {
    try {
      console.log('[Sentinel] Running npm audit...');
      const auditOutput = execSync('npm audit --json', { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] });
      const audit = JSON.parse(auditOutput);
      report.vulnerabilities = {
        total: audit.metadata?.vulnerabilities?.total || 0,
        severity: audit.metadata?.vulnerabilities || {},
        details: audit.advisories || {}
      };
    } catch (err) {
      // npm audit returns non-zero exit code if vulns found, but stdout is valid JSON
      if (err.stdout) {
        try {
          const audit = JSON.parse(err.stdout);
          report.vulnerabilities = {
            total: audit.metadata?.vulnerabilities?.total || 0,
            severity: audit.metadata?.vulnerabilities || {},
            details: audit.advisories || {}
          };
        } catch (parseErr) {
          report.vulnerabilities = { error: 'Failed to parse npm audit output' };
        }
      } else {
        report.vulnerabilities = { error: 'npm audit failed: ' + err.message };
      }
    }
  }

  // 2. Secret Scan (Recursive)
  console.log('[Sentinel] Scanning for secrets...');
  const files = getAllFiles(process.cwd());
  for (const file of files) {
    try {
      const content = fs.readFileSync(file, 'utf8');
      for (const pattern of SECRET_PATTERNS) {
        if (pattern.regex.test(content)) {
          // Verify false positives (e.g., example values)
          if (!content.includes('EXAMPLE') && !content.includes('YOUR_API_KEY') && !file.includes('security-sentinel/index.js')) {
             report.secrets.push({
               file: path.relative(process.cwd(), file),
               type: pattern.name
             });
          }
        }
      }
    } catch (readErr) {
      // Ignore binary or unreadable
    }
  }

  // 3. Permission Scan
  console.log('[Sentinel] Checking permissions...');
  const CRITICAL_FILES = ['package.json', '.env', 'openclaw.json'];
  for (const crit of CRITICAL_FILES) {
    if (fs.existsSync(crit)) {
      const stats = fs.statSync(crit);
      const mode = stats.mode & 0o777; // Octal
      // Check if world writable (xx2 or xx6 or xx7)
      if ((mode & 0o002) !== 0) {
        report.permissions.push({
          file: crit,
          mode: mode.toString(8),
          issue: 'World Writable'
        });
      }
    }
  }

  // Summary Status
  if (
    (report.vulnerabilities.total > 0 && (report.vulnerabilities.severity.high > 0 || report.vulnerabilities.severity.critical > 0)) ||
    report.secrets.length > 0 ||
    report.permissions.length > 0
  ) {
    report.status = 'risk_detected';
  }

  return report;
}

function getAllFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const filePath = path.join(dir, file);
    if (IGNORED_PATHS.some(ignored => filePath.includes(ignored))) continue;

    if (fs.existsSync(filePath)) {
      const stat = fs.statSync(filePath);
      if (stat.isDirectory()) {
        getAllFiles(filePath, fileList);
      } else {
        if (/\.(js|json|md|txt|sh|yml|yaml|env)$/.test(file)) {
          fileList.push(filePath);
        }
      }
    }
  }
  return fileList;
}

// CLI Support
if (require.main === module) {
  const args = process.argv.slice(2);
  const options = {
    skipAudit: args.includes('--skip-audit')
  };
  
  scan(options).then(report => {
    console.log(JSON.stringify(report, null, 2));
    // If risks are detected, default to exit 1 for CI/CD unless --no-fail is passed
    if (report.status === 'risk_detected' && !args.includes('--no-fail')) {
      process.exit(1); 
    }
  }).catch(err => {
    console.error(err);
    process.exit(1);
  });
}

module.exports = { scan };
