/**
 * 🔍 Secrets Scanner
 * 
 * Detects exposed secrets like API keys, tokens, passwords
 * Inspired by detect-secrets, truffleHog, gitleaks
 */

import fs from 'fs/promises';
import path from 'path';
import { glob } from 'glob';

// Secret patterns with high/medium confidence
const SECRET_PATTERNS = [
  // API Keys
  {
    name: 'OpenAI API Key',
    pattern: /sk-[a-zA-Z0-9]{20,}T3BlbkFJ[a-zA-Z0-9]{20,}/g,
    severity: 'critical'
  },
  {
    name: 'Anthropic API Key',
    pattern: /sk-ant-[a-zA-Z0-9\-_]{80,}/g,
    severity: 'critical'
  },
  {
    name: 'Generic API Key',
    pattern: /(?:api[_-]?key|apikey)['":\s]*['"]?([a-zA-Z0-9\-_]{20,})['"]?/gi,
    severity: 'high'
  },
  
  // Tokens
  {
    name: 'Bearer Token',
    pattern: /bearer\s+[a-zA-Z0-9\-_\.]+/gi,
    severity: 'high'
  },
  {
    name: 'JWT Token',
    pattern: /eyJ[a-zA-Z0-9\-_]+\.eyJ[a-zA-Z0-9\-_]+\.[a-zA-Z0-9\-_]+/g,
    severity: 'high'
  },
  {
    name: 'Discord Bot Token',
    pattern: /[MN][A-Za-z\d]{23,}\.[\w-]{6}\.[\w-]{27}/g,
    severity: 'critical'
  },
  {
    name: 'Telegram Bot Token',
    pattern: /\d{9,10}:[a-zA-Z0-9_-]{35}/g,
    severity: 'critical'
  },
  {
    name: 'Slack Token',
    pattern: /xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}/g,
    severity: 'critical'
  },
  
  // Cloud Providers
  {
    name: 'AWS Access Key',
    pattern: /AKIA[0-9A-Z]{16}/g,
    severity: 'critical'
  },
  {
    name: 'AWS Secret Key',
    pattern: /(?:aws)?[_-]?secret[_-]?(?:access)?[_-]?key['":\s]*['"]?([a-zA-Z0-9\/\+]{40})['"]?/gi,
    severity: 'critical'
  },
  {
    name: 'Google API Key',
    pattern: /AIza[0-9A-Za-z\-_]{35}/g,
    severity: 'high'
  },
  {
    name: 'Azure Connection String',
    pattern: /DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[^;]+;/g,
    severity: 'critical'
  },
  
  // Passwords
  {
    name: 'Password in config',
    pattern: /(?:password|passwd|pwd)['":\s]*['"]?([^'"\s]{8,})['"]?/gi,
    severity: 'high'
  },
  {
    name: 'Database URL with credentials',
    pattern: /(?:postgres|mysql|mongodb|redis):\/\/[^:]+:[^@]+@/g,
    severity: 'critical'
  },
  
  // Private Keys
  {
    name: 'RSA Private Key',
    pattern: /-----BEGIN RSA PRIVATE KEY-----/g,
    severity: 'critical'
  },
  {
    name: 'SSH Private Key',
    pattern: /-----BEGIN (?:OPENSSH|DSA|EC|PGP) PRIVATE KEY-----/g,
    severity: 'critical'
  },
  
  // Webhooks
  {
    name: 'Webhook URL',
    pattern: /https:\/\/(?:hooks\.slack\.com|discord(?:app)?\.com\/api\/webhooks|api\.telegram\.org\/bot)[^\s'"]+/g,
    severity: 'high'
  },
  
  // Generic secrets
  {
    name: 'Generic Secret',
    pattern: /(?:secret|token|key|credential)['":\s]*['"]?([a-zA-Z0-9\-_]{20,})['"]?/gi,
    severity: 'medium'
  }
];

// Files to exclude
const DEFAULT_EXCLUDES = [
  '**/node_modules/**',
  '**/.git/**',
  '**/dist/**',
  '**/build/**',
  '**/*.min.js',
  '**/*.map',
  '**/package-lock.json',
  '**/pnpm-lock.yaml',
  '**/yarn.lock',
  '**/*.test.js',
  '**/*.spec.js',
  '**/test/**',
  '**/tests/**',
  '**/__tests__/**'
];

// Files that commonly contain example secrets (lower severity)
const EXAMPLE_FILES = [
  '.env.example',
  '.env.sample',
  '.env.template',
  'config.example.json',
  'config.sample.json'
];

export class SecretsScanner {
  constructor(config = {}) {
    this.config = config;
    this.patterns = SECRET_PATTERNS;
    this.excludes = [...DEFAULT_EXCLUDES, ...(config.scanners?.secrets?.exclude || [])];
    this.customPatterns = config.scanners?.secrets?.patterns || [];
  }
  
  async scan(basePath, options = {}) {
    const findings = [];
    const summary = { critical: 0, high: 0, medium: 0, low: 0 };
    
    // Get all files to scan
    const files = await glob('**/*', {
      cwd: basePath,
      ignore: this.excludes,
      nodir: true,
      absolute: true
    });
    
    // Filter to only scan text files
    const textExtensions = [
      '.js', '.ts', '.jsx', '.tsx', '.mjs', '.cjs',
      '.json', '.yaml', '.yml', '.toml',
      '.env', '.sh', '.bash', '.zsh',
      '.md', '.txt', '.cfg', '.conf', '.ini',
      '.py', '.rb', '.go', '.rs', '.java',
      '.xml', '.html', '.css', '.scss'
    ];
    
    const textFiles = files.filter(f => {
      const ext = path.extname(f).toLowerCase();
      const basename = path.basename(f);
      return textExtensions.includes(ext) || 
             basename.startsWith('.env') ||
             basename.endsWith('rc') ||
             !ext; // Files without extension (like 'Dockerfile')
    });
    
    // Scan each file
    for (const filePath of textFiles) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const relativePath = path.relative(basePath, filePath);
        const isExampleFile = EXAMPLE_FILES.some(ex => relativePath.endsWith(ex));
        
        // Check each pattern
        for (const { name, pattern, severity } of this.patterns) {
          const matches = content.matchAll(pattern);
          
          for (const match of matches) {
            // Find line number
            const beforeMatch = content.substring(0, match.index);
            const lineNumber = (beforeMatch.match(/\n/g) || []).length + 1;
            
            // Adjust severity for example files
            const actualSeverity = isExampleFile ? 'low' : severity;
            
            // Mask the secret for display
            const secretValue = match[1] || match[0];
            const maskedSecret = this.maskSecret(secretValue);
            
            findings.push({
              type: 'secret',
              name,
              severity: actualSeverity,
              message: `${name} found${isExampleFile ? ' (in example file)' : ''}`,
              location: `${relativePath}:${lineNumber}`,
              file: relativePath,
              line: lineNumber,
              secret: maskedSecret,
              fix: isExampleFile 
                ? 'Example file - ensure this is not used in production'
                : 'Remove secret from code and use environment variables or a secrets manager'
            });
            
            summary[actualSeverity]++;
          }
        }
        
        // Check for high entropy strings (potential secrets)
        if (!options.quick) {
          const highEntropyFindings = this.findHighEntropyStrings(content, relativePath);
          for (const finding of highEntropyFindings) {
            if (!isExampleFile) {
              findings.push(finding);
              summary[finding.severity]++;
            }
          }
        }
        
      } catch (error) {
        // Skip files that can't be read
        if (error.code !== 'EISDIR') {
          console.warn(`Warning: Could not read ${filePath}: ${error.message}`);
        }
      }
    }
    
    // Check .env files specifically
    const envFindings = await this.scanEnvFiles(basePath);
    for (const finding of envFindings) {
      findings.push(finding);
      summary[finding.severity]++;
    }
    
    return {
      scanner: 'secrets',
      findings,
      summary,
      filesScanned: textFiles.length
    };
  }
  
  maskSecret(secret) {
    if (!secret || secret.length < 8) return '***';
    return secret.substring(0, 4) + '*'.repeat(Math.min(secret.length - 8, 20)) + secret.substring(secret.length - 4);
  }
  
  findHighEntropyStrings(content, filePath) {
    const findings = [];
    
    // Look for quoted strings that might be secrets
    const stringPattern = /['"]([a-zA-Z0-9\-_\/\+]{32,})['"]|:\s*([a-zA-Z0-9\-_\/\+]{32,})/g;
    const matches = content.matchAll(stringPattern);
    
    for (const match of matches) {
      const str = match[1] || match[2];
      const entropy = this.calculateEntropy(str);
      
      // High entropy strings are likely secrets
      if (entropy > 4.5 && str.length >= 32) {
        const beforeMatch = content.substring(0, match.index);
        const lineNumber = (beforeMatch.match(/\n/g) || []).length + 1;
        
        // Check if it's likely a hash or encoded data (less likely to be a secret)
        const looksLikeHash = /^[a-f0-9]{32,}$/i.test(str);
        const _looksLikeBase64 = /^[A-Za-z0-9+\/]+=*$/.test(str) && str.length % 4 === 0;

        if (!looksLikeHash) {
          findings.push({
            type: 'high-entropy',
            name: 'High Entropy String',
            severity: 'medium',
            message: 'High entropy string detected (possible secret)',
            location: `${filePath}:${lineNumber}`,
            file: filePath,
            line: lineNumber,
            entropy: entropy.toFixed(2),
            fix: 'Review this string - if it\'s a secret, move it to environment variables'
          });
        }
      }
    }
    
    return findings;
  }
  
  calculateEntropy(str) {
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
  
  async scanEnvFiles(basePath) {
    const findings = [];
    
    // Find all .env files
    const envFiles = await glob('**/.env*', {
      cwd: basePath,
      ignore: ['**/node_modules/**'],
      absolute: true,
      dot: true
    });
    
    for (const envFile of envFiles) {
      const relativePath = path.relative(basePath, envFile);
      const basename = path.basename(envFile);
      
      // Check if .env file is in .gitignore
      if (basename === '.env' || basename.match(/^\.env\.(local|development|production)$/)) {
        const gitignorePath = path.join(path.dirname(envFile), '.gitignore');
        
        try {
          const gitignore = await fs.readFile(gitignorePath, 'utf-8');
          const isIgnored = gitignore.split('\n').some(line => 
            line.trim() === '.env' || 
            line.trim() === '.env*' || 
            line.trim() === '*.env'
          );
          
          if (!isIgnored) {
            findings.push({
              type: 'env-file',
              name: 'Unignored .env file',
              severity: 'high',
              message: '.env file not in .gitignore - may be committed to repository',
              location: relativePath,
              file: relativePath,
              fix: `Add "${basename}" to .gitignore`
            });
          }
        } catch {
          // No .gitignore found
          findings.push({
            type: 'env-file',
            name: 'Missing .gitignore',
            severity: 'medium',
            message: 'No .gitignore found - .env files may be committed',
            location: path.dirname(relativePath),
            fix: 'Create a .gitignore file and add .env to it'
          });
        }
      }
    }
    
    return findings;
  }
}

export default SecretsScanner;
