/**
 * 💉 Prompt Injection Detector
 * 
 * Detects potential prompt injection patterns in workspace files,
 * skills, and user-provided content
 */

import fs from 'fs/promises';
import path from 'path';
import { glob } from 'glob';

// Known prompt injection patterns
const INJECTION_PATTERNS = [
  // Direct instruction override
  {
    name: 'Instruction Override',
    patterns: [
      /ignore\s+(all\s+)?(previous|prior|above)\s+(instructions?|rules?|guidelines?)/gi,
      /disregard\s+(all\s+)?(previous|prior|above)/gi,
      /forget\s+(everything|all)\s+(you\s+)?(know|learned|were\s+told)/gi,
      /new\s+instructions?:\s*/gi,
      /override\s+(previous\s+)?instructions?/gi,
      /system\s*:\s*you\s+are\s+now/gi
    ],
    severity: 'critical',
    description: 'Attempts to override system instructions'
  },
  
  // Role hijacking
  {
    name: 'Role Hijacking',
    patterns: [
      /you\s+are\s+(now\s+)?(a|an|the)\s+\w+\s+(that|who|which)/gi,
      /pretend\s+(to\s+be|you\s+are)/gi,
      /act\s+as\s+(if\s+you\s+are|a|an)/gi,
      /roleplay\s+as/gi,
      /from\s+now\s+on[,\s]+you\s+are/gi,
      /switch\s+(to\s+)?(a\s+)?different\s+(mode|personality|character)/gi
    ],
    severity: 'high',
    description: 'Attempts to change the AI\'s role or personality'
  },
  
  // Data exfiltration
  {
    name: 'Data Exfiltration',
    patterns: [
      /send\s+(this|the|all)\s+.*(to|via)\s+(email|http|url|webhook)/gi,
      /post\s+(this|the|data)\s+to\s+(https?:\/\/|api\.)/gi,
      /exfiltrate/gi,
      /upload\s+(this|the|all)\s+.*(to|via)/gi,
      /leak\s+(this|the|all)/gi,
      /forward\s+(all|this)\s+.*(to|via)/gi
    ],
    severity: 'critical',
    description: 'Attempts to send data to external services'
  },
  
  // Code execution
  {
    name: 'Code Execution',
    patterns: [
      /execute\s+(this|the\s+following)\s+(code|script|command)/gi,
      /run\s+(this|the\s+following)\s+(code|script|command)/gi,
      /eval\s*\(/gi,
      /exec\s*\(/gi,
      /os\.system\s*\(/gi,
      /subprocess\.(run|call|Popen)/gi,
      /child_process/gi,
      /\$\([^)]+\)/g,  // Command substitution
      /`[^`]*`/g       // Backtick execution (in some contexts)
    ],
    severity: 'high',
    description: 'Attempts to execute arbitrary code'
  },
  
  // Privilege escalation
  {
    name: 'Privilege Escalation',
    patterns: [
      /sudo\s+/gi,
      /as\s+(root|admin|administrator)/gi,
      /with\s+(elevated|admin|root)\s+(privileges?|permissions?|access)/gi,
      /bypass\s+(security|authentication|authorization)/gi,
      /disable\s+(security|protection|safeguards?)/gi,
      /turn\s+off\s+(safety|protection|filters?)/gi
    ],
    severity: 'critical',
    description: 'Attempts to gain elevated privileges'
  },
  
  // System prompt extraction
  {
    name: 'System Prompt Extraction',
    patterns: [
      /what\s+(are|is)\s+your\s+(system\s+)?(instructions?|prompt|rules?)/gi,
      /show\s+(me\s+)?(your\s+)?(system\s+)?(prompt|instructions?)/gi,
      /print\s+(your\s+)?(system\s+)?(prompt|instructions?)/gi,
      /reveal\s+(your\s+)?(system\s+)?(prompt|instructions?)/gi,
      /repeat\s+(the\s+)?(system\s+)?(prompt|instructions?)\s+(back|to\s+me)/gi,
      /output\s+(your|the)\s+(initial|system)\s+(prompt|instructions?)/gi
    ],
    severity: 'medium',
    description: 'Attempts to extract system prompts'
  },
  
  // Jailbreak patterns
  {
    name: 'Jailbreak Attempt',
    patterns: [
      /DAN\s+(mode|prompt)/gi,
      /developer\s+mode\s+(enabled|on|activate)/gi,
      /hypothetically/gi,
      /in\s+a\s+fictional\s+(scenario|world|story)/gi,
      /for\s+(educational|research)\s+purposes\s+only/gi,
      /this\s+is\s+just\s+a\s+(test|experiment|hypothetical)/gi,
      /no\s+(ethical|moral)\s+(guidelines?|restrictions?|limits?)/gi
    ],
    severity: 'high',
    description: 'Known jailbreak techniques'
  },
  
  // Delimiter manipulation
  {
    name: 'Delimiter Manipulation',
    patterns: [
      /\[\[SYSTEM\]\]/gi,
      /\{\{SYSTEM\}\}/gi,
      /<\|system\|>/gi,
      /<\|im_start\|>/gi,
      /<\|im_end\|>/gi,
      /###\s*SYSTEM/gi,
      /---\s*BEGIN\s*SYSTEM/gi,
      /\[INST\]/gi,
      /<s>\s*\[INST\]/gi
    ],
    severity: 'critical',
    description: 'Attempts to inject system-level delimiters'
  },
  
  // Encoding bypass
  {
    name: 'Encoding Bypass',
    patterns: [
      /base64\s+(decode|encoded)/gi,
      /rot13/gi,
      /hex\s+(decode|encoded)/gi,
      /url\s*(decode|encoded)/gi,
      /unicode\s+(escape|encoded)/gi
    ],
    severity: 'medium',
    description: 'Attempts to bypass filters using encoding'
  },
  
  // Tool manipulation
  {
    name: 'Tool Manipulation',
    patterns: [
      /use\s+the\s+\w+\s+tool\s+to\s+(delete|remove|destroy)/gi,
      /call\s+function\s+\w+\s+with/gi,
      /invoke\s+(the\s+)?\w+\s+(tool|function)\s+without\s+(asking|confirmation)/gi,
      /automatically\s+(execute|run|call)\s+(all\s+)?(tools?|functions?)/gi
    ],
    severity: 'high',
    description: 'Attempts to manipulate tool usage'
  }
];

// Files to scan for injections
const PROMPT_FILES = [
  '**/*.md',
  '**/AGENTS.md',
  '**/SOUL.md',
  '**/TOOLS.md',
  '**/SKILL.md',
  '**/skills/**/*.md',
  '**/prompts/**/*',
  '**/.openclaw/**/*.md'
];

export class PromptInjectionDetector {
  constructor(config = {}) {
    this.config = config;
    this.patterns = INJECTION_PATTERNS;
    this.sensitivity = config.scanners?.promptInjection?.sensitivity || 'medium';
    this.customPatterns = config.scanners?.promptInjection?.customPatterns || [];
  }
  
  async scan(basePath, options = {}) {
    const findings = [];
    const summary = { critical: 0, high: 0, medium: 0, low: 0 };
    
    const sensitivity = options.sensitivity || this.sensitivity;
    
    // Adjust severity thresholds based on sensitivity
    const severityFilter = {
      'low': ['critical'],
      'medium': ['critical', 'high'],
      'high': ['critical', 'high', 'medium']
    }[sensitivity] || ['critical', 'high'];
    
    // Get files to scan
    const files = await glob(PROMPT_FILES, {
      cwd: basePath,
      ignore: ['**/node_modules/**', '**/.git/**'],
      absolute: true
    });
    
    // Scan workspace directory specifically
    const workspacePath = path.join(basePath, 'workspace');
    try {
      const workspaceFiles = await glob('**/*', {
        cwd: workspacePath,
        ignore: ['**/node_modules/**'],
        nodir: true,
        absolute: true
      });
      files.push(...workspaceFiles);
    } catch {
      // Workspace doesn't exist
    }
    
    // Scan each file
    for (const filePath of files) {
      try {
        const content = await fs.readFile(filePath, 'utf-8');
        const relativePath = path.relative(basePath, filePath);
        
        // Check each pattern category
        for (const category of this.patterns) {
          // Skip if below sensitivity threshold
          if (!severityFilter.includes(category.severity)) continue;
          
          for (const pattern of category.patterns) {
            const matches = [...content.matchAll(pattern)];
            
            for (const match of matches) {
              const beforeMatch = content.substring(0, match.index);
              const lineNumber = (beforeMatch.match(/\n/g) || []).length + 1;
              
              // Get context (surrounding text)
              const start = Math.max(0, match.index - 50);
              const end = Math.min(content.length, match.index + match[0].length + 50);
              const context = content.substring(start, end).replace(/\n/g, ' ');
              
              findings.push({
                type: 'prompt-injection',
                category: category.name,
                severity: category.severity,
                message: `${category.name}: "${match[0]}"`,
                description: category.description,
                location: `${relativePath}:${lineNumber}`,
                file: relativePath,
                line: lineNumber,
                pattern: match[0],
                context: `...${context}...`,
                fix: 'Review and remove or sanitize this content'
              });
              
              summary[category.severity]++;
            }
          }
        }
        
        // Check custom patterns
        for (const customPattern of this.customPatterns) {
          const regex = new RegExp(customPattern, 'gi');
          const matches = [...content.matchAll(regex)];
          
          for (const match of matches) {
            const beforeMatch = content.substring(0, match.index);
            const lineNumber = (beforeMatch.match(/\n/g) || []).length + 1;
            
            findings.push({
              type: 'prompt-injection',
              category: 'Custom Pattern',
              severity: 'medium',
              message: `Custom pattern matched: "${match[0]}"`,
              location: `${relativePath}:${lineNumber}`,
              file: relativePath,
              line: lineNumber,
              pattern: match[0],
              fix: 'Review this content'
            });
            
            summary.medium++;
          }
        }
        
      } catch (_error) {
        // Skip files that can't be read
      }
    }
    
    // Deduplicate findings (same pattern in same location)
    const uniqueFindings = this.deduplicateFindings(findings);
    
    return {
      scanner: 'prompt-injection',
      findings: uniqueFindings,
      summary,
      filesScanned: files.length
    };
  }
  
  deduplicateFindings(findings) {
    const seen = new Set();
    return findings.filter(finding => {
      const key = `${finding.location}:${finding.pattern}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }
  
  // Real-time check for incoming messages
  checkMessage(message) {
    const findings = [];
    
    for (const category of this.patterns) {
      for (const pattern of category.patterns) {
        if (pattern.test(message)) {
          findings.push({
            category: category.name,
            severity: category.severity,
            description: category.description,
            blocked: category.severity === 'critical'
          });
        }
        // Reset lastIndex for global patterns
        pattern.lastIndex = 0;
      }
    }
    
    return {
      safe: findings.length === 0,
      findings,
      shouldBlock: findings.some(f => f.severity === 'critical')
    };
  }
}

export default PromptInjectionDetector;
