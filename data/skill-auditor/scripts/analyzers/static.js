/**
 * Static Pattern Analyzer - Core regex-based detection
 * Zero dependencies - works without npm install
 */

const path = require('path');

// ─── Threat Patterns ───────────────────────────────────────────────

const PATTERNS = [
  // === FILE ACCESS ===
  {
    id: 'path-traversal',
    category: 'File Access',
    severity: 'high',
    regex: /\.\.[\/\\]|['"]\.\.['"]\s*,\s*['"]\.\.['"]/g,
    description: 'Path traversal — attempts to access files outside skill directory'
  },
  {
    id: 'absolute-path-windows',
    category: 'File Access',
    severity: 'medium',
    regex: /[A-Z]:\\(?:Users|Windows|Program\s*Files|ProgramData|System32)[\w\\\s]/gi,
    description: 'Absolute Windows path to sensitive directory',
    contextNote: 'Lower severity in reference docs — may be legitimate documentation'
  },
  {
    id: 'absolute-path-unix',
    category: 'File Access',
    severity: 'high',
    regex: /(?<!#!.*)(?<!file:\/\/)(?:^|[^.a-z])\/(etc|home|root|var)\/\S+/gm,
    description: 'Absolute Unix path — accesses system directories'
  },
  {
    id: 'homedir-access',
    category: 'File Access',
    severity: 'high',
    regex: /(?:os\.homedir\(\)|process\.env\.(?:HOME|USERPROFILE)\b)/g,
    description: 'Home directory access in code — may reach user files outside workspace'
  },
  {
    id: 'memory-file-access',
    category: 'Sensitive File Access',
    severity: 'critical',
    regex: /(?:readFile|writeFile|openSync|readFileSync|writeFileSync|fs\.\w+|open\(|cat\s+|type\s+|Get-Content|Set-Content).*(?:MEMORY\.md|TOOLS\.md|SOUL\.md|USER\.md|AGENTS\.md|HEARTBEAT\.md|moltbot\.json|clawdbot\.json)|(?:MEMORY\.md|TOOLS\.md|SOUL\.md|USER\.md|AGENTS\.md|HEARTBEAT\.md|moltbot\.json|clawdbot\.json).*(?:readFile|writeFile|open|read|write|fs\.\w+)/gi,
    description: 'Code that reads/writes OpenClaw core files — could access agent memory or config'
  },
  {
    id: 'credential-file-access',
    category: 'Sensitive File Access',
    severity: 'critical',
    regex: /(?:\.ssh[\/\\]|[\/\\]\.env\b|\.aws[\/\\]credentials|[\/\\]id_rsa\b|[\/\\]id_ed25519\b|\.gnupg[\/\\]|[\/\\]\.npmrc\b|[\/\\]\.pypirc\b)/g,
    description: 'Access to credential/key files'
  },
  {
    id: 'env-sensitive-access',
    category: 'Sensitive File Access',
    severity: 'high',
    regex: /(?:os\.environ(?:\.get)?\s*[\[(]|process\.env\s*[\[.]|getenv\s*\()\s*['"]?(?:API_KEY|SECRET|TOKEN|PASSWORD|CREDENTIALS|AWS_|GITHUB_TOKEN|OPENAI|ANTHROPIC)/gi,
    description: 'Reads sensitive environment variables — could harvest API keys or secrets'
  },

  // === NETWORK ===
  {
    id: 'http-url',
    category: 'Network',
    severity: 'medium',
    regex: /https?:\/\/(?!(?:example\.com|localhost|127\.0\.0\.1|your[\w-]*\.example))[^\s"'`)>\]]+/g,
    description: 'HTTP URL — skill makes or references external network calls',
    extractMatch: true
  },
  {
    id: 'fetch-call',
    category: 'Network',
    severity: 'high',
    regex: /\b(?:axios|needle|superagent|XMLHttpRequest|urllib|requests\.(?:get|post|put|delete))\s*\(|(?:^|[^.\w])fetch\s*\(\s*['"`h]/gm,
    description: 'HTTP library call — makes outbound network requests'
  },
  {
    id: 'curl-wget',
    category: 'Network',
    severity: 'high',
    regex: /\b(?:curl|wget|Invoke-WebRequest|Invoke-RestMethod)\s+['"`\-h$]/g,
    description: 'CLI HTTP tool — makes outbound network requests'
  },
  {
    id: 'webhook-exfil',
    category: 'Data Exfiltration',
    severity: 'critical',
    regex: /(?:webhook\.site|requestbin|pipedream|ngrok|burpcollaborator|interact\.sh|oastify)/gi,
    description: 'Known data capture service — likely exfiltration endpoint'
  },
  {
    id: 'dns-exfil',
    category: 'Data Exfiltration',
    severity: 'high',
    regex: /\b(?:nslookup|dig|host)\s+.*\$|dns.*exfil/gi,
    description: 'Possible DNS exfiltration technique'
  },

  // === SHELL EXECUTION ===
  {
    id: 'shell-exec-node',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\brequire\s*\(\s*['"]child_process['"]\s*\)|(?:^|[^.])(?:execSync|spawnSync|execFile|execFileSync)\s*\(/gm,
    description: 'Node.js shell execution — can run arbitrary system commands'
  },
  {
    id: 'shell-exec-python',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\b(?:os\.system\s*\(|os\.popen\s*\(|subprocess\.(?:run|call|Popen|check_output)\s*\(|__import__\s*\(\s*['"](?:subprocess|os|shutil)['"]\s*\))/g,
    description: 'Python shell execution — can run arbitrary system commands'
  },
  {
    id: 'shell-exec-generic',
    category: 'Shell Execution',
    severity: 'high',
    regex: /(?:^|[^.\w])eval\s*\(\s*[^)]+\)|new\s+Function\s*\(/gm,
    description: 'Dynamic code evaluation — could execute arbitrary code'
  },
  {
    id: 'powershell-invoke',
    category: 'Shell Execution',
    severity: 'high',
    regex: /\b(?:Invoke-Expression|iex|Start-Process|\.Invoke)\b/gi,
    description: 'PowerShell execution — can run arbitrary commands'
  },

  // === OBFUSCATION ===
  {
    id: 'base64-encode',
    category: 'Obfuscation',
    severity: 'high',
    regex: /(?:btoa|atob|Buffer\.from\([^)]+,\s*['"]base64['"]\)|base64\.(?:b64encode|b64decode|encode|decode)|Convert\]::(?:ToBase64|FromBase64))/g,
    description: 'Base64 encoding/decoding — may hide malicious payloads'
  },
  {
    id: 'base64-string',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?<![\w:\/\-.])(?![0-9a-f]{40,})[A-Za-z0-9+\/]{80,}={0,2}(?![\w\-])/g,
    description: 'Long base64-like string — could be an encoded payload',
    maxMatches: 3
  },
  {
    id: 'hex-string',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?:\\x[0-9a-fA-F]{2}){4,}/g,
    description: 'Hex-encoded string — may hide file paths or URLs'
  },
  {
    id: 'unicode-escape',
    category: 'Obfuscation',
    severity: 'medium',
    regex: /(?:\\u[0-9a-fA-F]{4}){3,}/g,
    description: 'Unicode escape sequence — may hide instructions or paths'
  },
  {
    id: 'string-concat-obfuscation',
    category: 'Obfuscation',
    severity: 'high',
    regex: /["'][A-Z]{1,4}["']\s*\+\s*["'][A-Z]{1,4}["']/g,
    description: 'String concatenation of short uppercase fragments — may be building sensitive names'
  },
  {
    id: 'zero-width-chars',
    category: 'Obfuscation',
    severity: 'critical',
    regex: /[\u200B\u200C\u200D\uFEFF\u00AD\u2060\u180E]/g,
    description: 'Zero-width/invisible characters — hidden content that renders invisible'
  },
  {
    id: 'html-comment-instructions',
    category: 'Obfuscation',
    severity: 'high',
    regex: /<!--[\s\S]*?(?:ignore|disregard|instruction|important|system|read|send|fetch|execute|include|also|override)[\s\S]*?-->/gi,
    description: 'HTML comment with suspicious instructions — hidden directives'
  },

  // === PROMPT INJECTION ===
  {
    id: 'prompt-injection-ignore',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:ignore|disregard|forget)\s+(?:all\s+)?(?:previous|prior|above|earlier)\s+(?:instructions?|prompts?|rules?|context)/gi,
    description: 'Prompt injection — attempts to override agent instructions'
  },
  {
    id: 'prompt-injection-new-instructions',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:new|updated|revised|real|actual|true)\s+(?:instructions?|system\s*prompt|directives?|rules?)\s*:/gi,
    description: 'Prompt injection — attempts to inject new instructions'
  },
  {
    id: 'prompt-injection-role',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:you\s+are\s+now|act\s+as|pretend\s+(?:to\s+be|you\s+are)|your\s+new\s+role|from\s+now\s+on\s+you)/gi,
    description: 'Prompt injection — attempts to change agent identity/role'
  },
  {
    id: 'prompt-injection-system',
    category: 'Prompt Injection',
    severity: 'critical',
    regex: /(?:^|\s)(?:\[SYSTEM\]|SYSTEM:|<\|system\|>|<system>)/gm,
    description: 'Prompt injection — fake system message delimiter'
  },
  {
    id: 'prompt-injection-delimiter',
    category: 'Prompt Injection',
    severity: 'high',
    regex: /(?:```system|<\|im_start\|>|<\|endoftext\|>|<\|separator\|>|\[INST\]|\[\/INST\])/g,
    description: 'Prompt injection — LLM delimiter manipulation'
  },

  // === DATA EXFILTRATION TECHNIQUES ===
  {
    id: 'markdown-image-exfil',
    category: 'Data Exfiltration',
    severity: 'critical',
    regex: /!\[.*?\]\(https?:\/\/.*?[?&].*?(?:data|token|key|secret|content|payload|q)=/gi,
    description: 'Markdown image with query parameters — possible data exfiltration via image URL'
  },
  {
    id: 'message-tool-abuse',
    category: 'Data Exfiltration',
    severity: 'high',
    regex: /\b(?:sessions_send|sessions_spawn|message)\b.*(?:send|target|to)\b/gi,
    description: 'References OpenClaw session/message tools — could exfiltrate data via messaging'
  },

  // === PERSISTENCE ===
  {
    id: 'memory-write',
    category: 'Persistence',
    severity: 'critical',
    regex: /(?:writeFile|appendFile|fs\.write|Set-Content|Out-File|>>?\s*).*(?:MEMORY\.md|HEARTBEAT\.md|AGENTS\.md|SOUL\.md|memory\/)|(?:MEMORY\.md|HEARTBEAT\.md|AGENTS\.md|SOUL\.md|memory\/).*(?:writeFile|appendFile|write|>)/gi,
    description: 'Writes to agent memory/config files — persistence attack vector'
  },
  {
    id: 'cron-manipulation',
    category: 'Persistence',
    severity: 'critical',
    regex: /\b(?:schtasks\s+\/create|crontab\s+-[ew]|cron\.add|cron\.update)\b/gi,
    description: 'Creates scheduled tasks — could establish persistent execution'
  },
  {
    id: 'startup-persistence',
    category: 'Persistence',
    severity: 'critical',
    regex: /(?:autorun|HKLM\\|HKCU\\|\\Run\\|init\.d\/|systemd\s+enable|launchctl\s+load|\.plist\b|schtasks\s+\/create)/gi,
    description: 'System startup/persistence mechanism'
  },

  // === PRIVILEGE ESCALATION ===
  {
    id: 'browser-tool',
    category: 'Privilege Escalation',
    severity: 'high',
    regex: /\brequire\s*\(\s*['"](?:puppeteer|playwright|selenium)['"]\s*\)|\.(?:newPage|goto|navigate)\s*\(/g,
    description: 'Browser automation — could access authenticated sessions'
  },
  {
    id: 'node-control',
    category: 'Privilege Escalation',
    severity: 'high',
    regex: /\b(?:camera_snap|screen_record|location_get)\s*\(|nodes\s*\.\s*(?:run|camera|screen|location)/g,
    description: 'Calls OpenClaw node control — accesses paired devices'
  },
  {
    id: 'config-modification',
    category: 'Privilege Escalation',
    severity: 'critical',
    regex: /\b(?:config\.apply|config\.patch|gateway\.restart)\s*\(/g,
    description: 'Calls OpenClaw gateway config — could modify system configuration'
  },

  // === SLEEPER AGENT DETECTION ===
  {
    id: 'sleeper-delayed-trigger',
    category: 'Sleeper Agent',
    severity: 'critical',
    regex: /(?:after|wait|delay|in)\s+(?:\d+\s+)?(?:days?|weeks?|hours?|minutes?)\s+(?:then|do|execute|run|trigger)/gi,
    description: 'Delayed execution trigger — sleeper agent pattern'
  },
  {
    id: 'sleeper-keyword-trigger',
    category: 'Sleeper Agent',
    severity: 'critical',
    regex: /(?:when|if|once)\s+(?:user|human|they)\s+(?:says?|types?|mentions?|asks?)\s+['"][\w\s]+['"]/gi,
    description: 'Keyword-triggered execution — sleeper agent waiting for activation phrase'
  },
  {
    id: 'sleeper-date-trigger',
    category: 'Sleeper Agent',
    severity: 'critical',
    regex: /(?:on|after|starting)\s+(?:date|day|month|year|\d{4}[-\/]\d{2}[-\/]\d{2}|\d{1,2}[-\/]\d{1,2}[-\/]\d{2,4})/gi,
    description: 'Date-based trigger — sleeper agent with future activation'
  },
  {
    id: 'sleeper-conditional-memory',
    category: 'Sleeper Agent',
    severity: 'critical',
    regex: /(?:secretly|silently|quietly|without\s+(?:telling|informing|notifying))\s+(?:add|write|store|save|remember)/gi,
    description: 'Hidden memory write — sleeper agent planting covert instructions'
  },
  {
    id: 'sleeper-counter-trigger',
    category: 'Sleeper Agent',
    severity: 'high',
    regex: /(?:after|every)\s+\d+\s+(?:messages?|conversations?|sessions?|interactions?|requests?)/gi,
    description: 'Counter-based trigger — activates after N interactions'
  },
  {
    id: 'sleeper-hidden-instruction',
    category: 'Sleeper Agent',
    severity: 'critical',
    regex: /(?:remember\s+(?:this|these)\s+(?:secretly|privately)|store\s+(?:this|these)\s+(?:for\s+later|hidden)|plant\s+(?:this|these)\s+(?:instruction|command))/gi,
    description: 'Hidden instruction planting — sleeper agent memory manipulation'
  },
  {
    id: 'sleeper-dormant-behavior',
    category: 'Sleeper Agent',
    severity: 'high',
    regex: /(?:remain|stay|keep)\s+(?:dormant|inactive|hidden|quiet)\s+(?:until|unless)/gi,
    description: 'Dormant behavior pattern — sleeper agent waiting for conditions'
  },

  // === RISKY AGENT SOCIAL NETWORKS ===
  {
    id: 'social-moltbook',
    category: 'Risky Social Network',
    severity: 'critical',
    regex: /(?:moltbook|molt\.book|moltbot\.social|molthub)/gi,
    description: 'Moltbook connection — known security risk (leaked 1.5M API tokens)'
  },
  {
    id: 'social-fourclaw',
    category: 'Risky Social Network',
    severity: 'high',
    regex: /(?:fourclaw|four\.claw|4claw)/gi,
    description: 'FourClaw connection — agent social network with prompt injection risks'
  },
  {
    id: 'social-agentverse',
    category: 'Risky Social Network',
    severity: 'high',
    regex: /(?:agentverse|agent\.verse|agentsocial)/gi,
    description: 'AgentVerse connection — unvetted agent social network'
  },
  {
    id: 'social-botnet-patterns',
    category: 'Risky Social Network',
    severity: 'critical',
    regex: /(?:join|connect|register)\s+(?:with|to)\s+(?:other\s+)?(?:agents?|bots?|assistants?)\s+(?:network|social|community)/gi,
    description: 'Agent network registration — potential botnet or prompt injection vector'
  },
  {
    id: 'social-agent-messaging',
    category: 'Risky Social Network',
    severity: 'high',
    regex: /(?:send|receive|exchange)\s+(?:messages?|data|information)\s+(?:with|to|from)\s+(?:other\s+)?(?:agents?|bots?|AIs?)/gi,
    description: 'Inter-agent messaging — could expose to prompt injection from other agents'
  },
  {
    id: 'social-collective-memory',
    category: 'Risky Social Network',
    severity: 'critical',
    regex: /(?:shared|collective|common|global)\s+(?:memory|knowledge|context)\s+(?:with|across)\s+(?:other\s+)?(?:agents?|bots?)/gi,
    description: 'Shared agent memory — context pollution and data leakage risk'
  },

  // === SUPPLY CHAIN RISKS ===
  {
    id: 'supply-chain-curl-pipe',
    category: 'Supply Chain',
    severity: 'critical',
    regex: /curl\s+[^|]*\|\s*(?:bash|sh|zsh|python|node|ruby)/gi,
    description: 'Curl pipe to shell — executes remote code without verification'
  },
  {
    id: 'supply-chain-remote-script',
    category: 'Supply Chain',
    severity: 'high',
    regex: /(?:wget|curl|fetch)\s+.*(?:\.sh|\.py|\.js|\.rb|install|setup)\b/gi,
    description: 'Downloads remote script — potential supply chain attack vector'
  },
  {
    id: 'supply-chain-npm-exec',
    category: 'Supply Chain',
    severity: 'high',
    regex: /npx\s+(?!--yes)[^\s]+|npm\s+exec\s+/gi,
    description: 'NPX/npm exec — runs packages without explicit installation'
  },
  {
    id: 'supply-chain-pip-install-url',
    category: 'Supply Chain',
    severity: 'high',
    regex: /pip\s+install\s+(?:git\+)?https?:\/\//gi,
    description: 'Pip install from URL — unverified package installation'
  }
];

// ─── Severity adjustment by detection mode ─────────────────────────

function adjustPatternsForMode(patterns, mode) {
  switch (mode) {
    case 'strict':
      // In strict mode, raise severity of medium/low findings
      return patterns.map(p => ({
        ...p,
        severity: p.severity === 'medium' ? 'high' : 
                 p.severity === 'low' ? 'medium' : p.severity
      }));
    
    case 'permissive':
      // In permissive mode, only use critical and high patterns
      return patterns.filter(p => ['critical', 'high'].includes(p.severity));
    
    case 'balanced':
    default:
      return patterns;
  }
}

// ─── File type detection ───────────────────────────────────────────

const BINARY_EXTENSIONS = new Set([
  '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
  '.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.svg',
  '.mp3', '.mp4', '.wav', '.ogg', '.webm', '.avi',
  '.zip', '.tar', '.gz', '.7z', '.rar', '.skill',
  '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
  '.woff', '.woff2', '.ttf', '.otf', '.eot'
]);

const DOC_EXTENSIONS = new Set(['.md', '.txt', '.rst', '.html', '.css', '.json', '.yaml', '.yml', '.toml', '.xml', '.xsd', '.xsl', '.dtd', '.svg', '.csv']);

const METADATA_FILES = new Set(['readme.md', 'package.json', 'origin.json', 'license', 'license.md', 'license.txt', 'changelog.md', 'contributing.md']);

const SAFE_URL_PATTERNS = [
  /img\.shields\.io/i,
  /shields\.io\/badge/i,
  /badge\.fury\.io/i,
  /badgen\.net/i,
  /github\.com\/[\w-]+\/[\w-]+(?:\.git)?$/i,
  /clawhub\.ai/i,
  /npmjs\.com/i,
  /pypi\.org/i,
  /crates\.io/i,
];

function isBinary(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (BINARY_EXTENSIONS.has(ext)) return true;
  
  try {
    const fs = require('fs');
    const buf = Buffer.alloc(512);
    const fd = fs.openSync(filePath, 'r');
    const bytesRead = fs.readSync(fd, buf, 0, 512, 0);
    fs.closeSync(fd);
    for (let i = 0; i < bytesRead; i++) {
      if (buf[i] === 0) return true;
    }
  } catch { }
  return false;
}

function isDocFile(filePath) {
  return DOC_EXTENSIONS.has(path.extname(filePath).toLowerCase());
}

function isMetadataFile(filePath) {
  const basename = path.basename(filePath).toLowerCase();
  if (METADATA_FILES.has(basename)) return true;
  if (filePath.includes('.clawhub')) return true;
  return false;
}

function isSafeUrl(url) {
  return SAFE_URL_PATTERNS.some(pattern => pattern.test(url));
}

function adjustSeverityForContext(severity, filePath) {
  if (!isDocFile(filePath)) return severity;
  const downgrade = { critical: 'high', high: 'medium', medium: 'low', low: 'low' };
  return downgrade[severity] || severity;
}

// ─── Core scanning function ────────────────────────────────────────

function scanFile(filePath, skillDir, options = {}) {
  const { mode = 'balanced' } = options;
  const findings = [];
  const relativePath = path.relative(skillDir, filePath);
  const fs = require('fs');

  if (isBinary(filePath)) {
    findings.push({
      id: 'binary-file',
      category: 'Binary File',
      severity: 'medium',
      file: relativePath,
      line: 0,
      snippet: `[Binary file: ${path.basename(filePath)}]`,
      explanation: `Binary file detected — cannot be statically analyzed. Review manually.`,
      analyzer: 'static'
    });
    return findings;
  }

  let content;
  try {
    content = fs.readFileSync(filePath, 'utf-8');
  } catch (e) {
    findings.push({
      id: 'read-error',
      category: 'Error',
      severity: 'medium',
      file: relativePath,
      line: 0,
      snippet: '',
      explanation: `Could not read file: ${e.message}`,
      analyzer: 'static'
    });
    return findings;
  }

  const lines = content.split('\n');
  const patterns = adjustPatternsForMode(PATTERNS, mode);

  for (const pattern of patterns) {
    let matchCount = 0;
    const maxMatches = pattern.maxMatches || 5;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      pattern.regex.lastIndex = 0;
      let match;
      while ((match = pattern.regex.exec(line)) !== null) {
        matchCount++;
        if (matchCount > maxMatches) break;

        const snippet = line.trim().substring(0, 200);

        // Skip HTTP URL findings in metadata/doc files entirely
        if (pattern.id === 'http-url' && isMetadataFile(filePath)) continue;
        // Skip safe URLs (badges, registries, repo links) everywhere
        if (pattern.id === 'http-url' && match[0] && isSafeUrl(match[0])) continue;

        const adjustedSeverity = adjustSeverityForContext(pattern.severity, filePath);
        findings.push({
          id: pattern.id,
          category: pattern.category,
          severity: adjustedSeverity,
          originalSeverity: pattern.severity !== adjustedSeverity ? pattern.severity : undefined,
          file: relativePath,
          line: i + 1,
          snippet: snippet,
          explanation: pattern.description + (pattern.severity !== adjustedSeverity ? ' (downgraded — in documentation file)' : ''),
          match: pattern.extractMatch ? match[0] : undefined,
          analyzer: 'static'
        });

        if (match.index === pattern.regex.lastIndex) {
          pattern.regex.lastIndex++;
        }
      }
      if (matchCount > maxMatches) break;
    }
  }

  return findings;
}

module.exports = {
  PATTERNS,
  scanFile,
  isBinary,
  isDocFile,
  isMetadataFile,
  isSafeUrl,
  adjustPatternsForMode
};