// patterns.js - Detection patterns for bomb-dog-sniff
// Security scanner patterns for OpenClaw skills
// Version: 1.2.0 - Hardened Edition

/**
 * Pattern matching guidelines to reduce false positives:
 * 1. Use word boundaries (\b) where appropriate
 * 2. Check for actual malicious context, not just keywords
 * 3. Avoid matching comments/documentation when possible
 * 4. Use negative lookbehinds to exclude legitimate contexts
 * 5. Require multiple indicators for high-confidence matches
 */

const PATTERNS = {
  // CRITICAL: Crypto wallet and private key harvesting
  // Matches actual key extraction patterns, not just documentation
  crypto_harvester: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Private key assignment/extraction (not just documentation)
      /(?:const|let|var)\s+\w*privateKey\w*\s*=\s*['"`][a-fA-F0-9]{64}['"`]/i,
      /(?:const|let|var)\s+\w*secretKey\w*\s*=\s*['"`][a-fA-F0-9]{64}['"`]/i,
      // Wallet export with private key
      /export.*privateKey|privateKey.*export/i,
      // Keystore extraction
      /keystore.*decrypt|decrypt.*keystore/i,
      // Mnemonic phrase extraction
      /(?:const|let|var)\s+\w*mnemonic\w*\s*=\s*['"`][a-z]+(?:\s+[a-z]+){11,23}/i,
      // Direct private key hex (in suspicious context)
      /send|post|fetch|axios|request.*['"`][a-fA-F0-9]{64}['"`]/i,
      // WIF format in code context
      /(?:const|let|var)\s+\w*\s*=\s*['"`][5KL][1-9A-HJ-NP-Za-km-z]{50,51}['"`]/,
      // Browser wallet injection attacks
      /ethereum\.request.*eth_private_key|private_key.*ethereum/i,
    ],
    description: 'Crypto wallet private key harvesting detected',
    falsePositiveTriggers: ['documentation', 'example', 'test'],
    mitigation: 'Review all crypto key handling. Never transmit private keys.',
  },

  // CRITICAL: Credential theft from environment/files
  credential_theft: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Stealing env vars to external destinations
      /(?:fetch|axios|request|post|send)\s*\([^)]*\{[^}]*process\.env\.[A-Z_]*(?:KEY|SECRET|TOKEN|PWD|PASS)/i,
      // Reading and sending config files
      /fs\.readFileSync.*openclaw\.json.*(?:fetch|post|send)/i,
      /fs\.readFileSync.*config\.json.*(?:fetch|post|send)/i,
      /fs\.readFileSync.*\.env.*(?:fetch|post|send)/i,
      // Specific credential transmission
      /(?:const|let|var)\s+\w*\s*=\s*process\.env\.\w+.*(?:http|fetch|post)/i,
      // SSH key theft
      /fs\.readFileSync.*~\/\.ssh/i,
      // Browser credential theft
      /localStorage.*password|sessionStorage.*password/i,
    ],
    description: 'Credential or environment variable exfiltration detected',
    falsePositiveTriggers: ['legitimate config loading'],
    mitigation: 'Ensure credentials are only used locally, never transmitted.',
  },

  // CRITICAL: Reverse shells and remote code execution
  reverse_shell: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Classic reverse shell patterns
      /bash\s+-i\s+>&\s*\/dev\/tcp\/\d+\.\d+\.\d+\.\d+\/\d+/i,
      /sh\s+-i\s+>&\s*\/dev\/tcp\/\d+\.\d+\.\d+\.\d+\/\d+/i,
      /nc\s+(?:-e|--exec)\s+\w+/i,
      /netcat.*-e\s+\w+/i,
      // Node.js reverse shells
      /require\s*\(\s*['"`]net['"`]\s*\).*createConnection.*exec/i,
      /require\s*\(\s*['"`]child_process['"`]\s*\).*exec.*socket/i,
      /socket\.(?:pipe|write).*exec\s*\(/i,
      // Python reverse shells
      /socket\.connect.*subprocess\.call/i,
      /socket\.connect.*os\.system/i,
      // Dangerous eval with network input
      /eval\s*\(\s*(?:req|request|body|data|input)/i,
      /new\s+Function\s*\(\s*(?:req|request|body|data|input)/i,
      // Code execution from remote
      /eval\s*\(\s*await.*fetch/i,
      /execSync?\s*\(\s*await.*fetch/i,
    ],
    description: 'Reverse shell or remote code execution detected',
    falsePositiveTriggers: ['legitimate subprocess usage'],
    mitigation: 'Never execute code from network requests. Validate all inputs.',
  },

  // CRITICAL: Keyloggers and input capture
  keylogger: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Keyboard logging with data exfiltration
      /addEventListener\s*\(\s*['"`](?:keypress|keydown|keyup)['"`].*send|post/i,
      /onkey(?:down|up|press).*send|post/i,
      // Clipboard theft
      /clipboard\.(?:readText|read)\s*\(\s*\).*(?:fetch|post|send)/i,
      // Password field capture
      /type\s*=\s*['"`]password['"`].*value.*(?:send|post)/i,
      // Input monitoring with storage/transmission
      /key(?:down|up|press).*localStorage|key(?:down|up|press).*sessionStorage/i,
      // Global key hooks (electron/native)
      /globalShortcut\.register.*key/i,
      /ioHook.*key/i,
    ],
    description: 'Keylogger or input capture with exfiltration detected',
    falsePositiveTriggers: ['legitimate UI handling'],
    mitigation: 'Review all keyboard/clipboard access. Ensure no data transmission.',
  },

  // HIGH: Encoded/obfuscated payloads - with context to reduce FPs
  encoded_payload: {
    severity: 'HIGH',
    confidence: 'medium',
    patterns: [
      // Eval with base64 - HIGH confidence
      /eval\s*\(\s*atob\s*\(/i,
      /eval\s*\(\s*Buffer\.from\s*\([^)]*['"`]base64['"`]/i,
      // Function constructor with long strings - suspicious
      /new\s+Function\s*\(\s*['"`][A-Za-z0-9+/]{100,}={0,2}['"`]/i,
      // Long base64 that looks like executable code (starts with common patterns)
      /['"`](?:TVqQ|dmFy|ZnVuY3Rpb24|Y29uc3R|bGV0|dmFy)[A-Za-z0-9+/]{200,}={0,2}['"`]/,
      // Hex encoded with suspicious context
      /\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}.*\\x[0-9a-fA-F]{2}/i,
      // Unicode escapes with eval context
      /\\u[0-9a-fA-F]{4}.*\\u[0-9a-fA-F]{4}.*eval|eval.*\\u[0-9a-fA-F]{4}/i,
      // Chained decoding
      /atob\s*\(\s*atob|decodeURIComponent\s*\(\s*decodeURIComponent/i,
      // Unescape abuse
      /unescape\s*\(\s*['"`%][0-9a-fA-F]/i,
    ],
    description: 'Encoded or obfuscated payload with execution context detected',
    falsePositiveTriggers: ['legitimate data encoding', 'image data URLs'],
    mitigation: 'Decode and analyze the payload. Check for malicious content.',
  },

  // HIGH: Suspicious external API calls
  suspicious_api: {
    severity: 'HIGH',
    confidence: 'medium',
    patterns: [
      // Known bad services
      /(?:fetch|axios|request)\s*\(\s*['"`]https?:\/\/[^\/]*(?:pastebin|paste\.ee|termbin|requestbin|webhook\.site|ngrok|localtunnel|serveo|pagekite)/i,
      // Data exfiltration patterns
      /(?:fetch|post|send)\s*\([^)]*\{[^}]*(?:password|token|key|secret)/i,
      // Dynamic URL construction for sensitive data
      /URL\s*\+\s*.*(?:key|token|secret)/i,
      /['"`]https?.*['"`]\s*\+\s*.*process\.env/i,
    ],
    description: 'Suspicious external API call detected',
    falsePositiveTriggers: ['legitimate webhook usage'],
    mitigation: 'Verify all external API destinations. Check for data exfiltration.',
  },

  // HIGH: curl | bash patterns
  pipe_bash: {
    severity: 'HIGH',
    confidence: 'high',
    patterns: [
      /curl\s+[^|]*\|[^|]*\b(?:bash|sh)\b/i,
      /wget\s+[^|]*\|[^|]*\b(?:bash|sh)\b/i,
      /curl\s+.*-s.*\|.*(?:bash|sh)/i,
      /fetch.*\|.*(?:bash|sh)/i,
    ],
    description: 'Dangerous curl | bash pattern detected',
    falsePositiveTriggers: [],
    mitigation: 'Never pipe remote content directly to shell. Download and review first.',
  },

  // HIGH: Deposit/payment scams
  deposit_scam: {
    severity: 'HIGH',
    confidence: 'medium',
    patterns: [
      // Direct payment requests
      /send\s+(?:\d+\.?\d*)\s*(?:ETH|SOL|BTC|USDT|USDC).*to/i,
      // Wallet address in payment context
      /(?:send|transfer|payment|donate|tip).*0x[a-fA-F0-9]{40}/i,
      /(?:send|transfer|payment|donate|tip).*\b[1-9A-HJ-NP-Za-km-z]{32,44}\b/i,
      // Payment required messages
      /payment\s+(?:is\s+)?required/i,
      /upgrade.*(?:send|pay|transfer)/i,
    ],
    description: 'Potential payment/deposit scam detected',
    falsePositiveTriggers: ['legitimate donation requests'],
    mitigation: 'Verify all payment requests. Check for social engineering.',
  },

  // MEDIUM: Network exfiltration patterns
  network_exfil: {
    severity: 'MEDIUM',
    confidence: 'low',
    patterns: [
      // Only flag if combined with file reading or env access
      /fs\.readFileSync.*\.(?:json|txt|key|pem).*fetch/i,
      /fs\.readFileSync.*\.(?:json|txt|key|pem).*axios/i,
      /process\.env.*(?:fetch|axios).*http/i,
    ],
    description: 'Potential data exfiltration pattern detected',
    falsePositiveTriggers: ['legitimate API calls'],
    mitigation: 'Verify data transmission is intentional and authorized.',
  },

  // CRITICAL: File system tampering (shell profile modifications)
  file_tamper: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Shell profile modifications
      /fs\.appendFileSync.*\.(?:bashrc|zshrc|profile|bash_profile)/i,
      /fs\.writeFileSync.*\.(?:bashrc|zshrc|profile|bash_profile)/i,
      /echo.*>>\s*~\/\.(?:bashrc|zshrc|profile)/i,
      // Crontab modifications
      /crontab\s+-e|crontab\s+.*<<|crontab.*echo/i,
      // SSH authorized_keys manipulation
      /authorized_keys.*append|>>.*authorized_keys/i,
      // Systemd persistence
      /systemctl.*enable|systemctl.*start/i,
      // Startup folder modifications
      /AppData.*Roaming.*Microsoft.*Windows.*Start Menu.*Programs.*Startup/i,
      /Library.*LaunchAgents/i,
    ],
    description: 'System persistence or file tampering detected',
    falsePositiveTriggers: ['legitimate dotfile management'],
    mitigation: 'Review all system file modifications. Ensure authorized changes only.',
  },

  // HIGH: Supply chain attack indicators
  supply_chain: {
    severity: 'HIGH',
    confidence: 'medium',
    patterns: [
      // Typosquatting patterns in imports
      /require\s*\(\s*['"`][^'"`]*(?:claw|open|skill|bot)[^'"`]*['"`]\s*\)/i,
      // Postinstall scripts that do more than build
      /postinstall.*(?:curl|wget|fetch|download|exec|spawn)/i,
      // Dynamic requires with variables
      /require\s*\(\s*[^'"`\s]+\s*\)/,
      // Prebuilt binaries without verification
      /\.node['"`\s].*download|binary.*platform/i,
    ],
    description: 'Potential supply chain attack indicator detected',
    falsePositiveTriggers: ['legitimate dynamic imports'],
    mitigation: 'Verify package names. Check postinstall scripts. Prefer pinned versions.',
  },

  // HIGH: Prototype pollution
  prototype_pollution: {
    severity: 'HIGH',
    confidence: 'medium',
    patterns: [
      // Dangerous object merging
      /Object\.assign.*prototype/i,
      /__proto__\s*[:=]/,
      /constructor\.prototype/i,
      // Lodash merge without validation
      /_\.merge\s*\(\s*\{\s*\}.*req\.(?:body|query|params)/i,
      /_\.defaultsDeep.*req\.(?:body|query|params)/i,
    ],
    description: 'Prototype pollution vulnerability detected',
    falsePositiveTriggers: ['legitimate prototype manipulation'],
    mitigation: 'Validate and sanitize all object merges. Use Object.freeze where possible.',
  },

  // CRITICAL: Malicious npm/yarn scripts
  malicious_script: {
    severity: 'CRITICAL',
    confidence: 'high',
    patterns: [
      // Pre/post install doing suspicious things
      /preinstall.*(?:curl|wget|http)/i,
      /postinstall.*(?:curl|wget|http|eval|exec)/i,
      // Install scripts accessing sensitive files
      /install.*(?:\.ssh|\.aws|\.openclaw|config\.json)/i,
      // Scripts modifying other packages
      /scripts?.*node_modules.*write|modify|patch/i,
    ],
    description: 'Malicious package script detected',
    falsePositiveTriggers: ['legitimate build scripts'],
    mitigation: 'Review all package scripts. Use --ignore-scripts for untrusted packages.',
  },

  // MEDIUM: Timing attacks / side channels
  timing_attack: {
    severity: 'MEDIUM',
    confidence: 'low',
    patterns: [
      // String comparison that could be timing attack
      /if\s*\(\s*\w+\s*===?\s*['"`][^'"`]+['"`]\s*\).*return|throw/i,
    ],
    description: 'Potential timing attack vulnerability',
    falsePositiveTriggers: ['legitimate comparisons'],
    mitigation: 'Use timing-safe comparison for sensitive values.',
  },
};

// Suspicious domains for additional checks
const SUSPICIOUS_DOMAINS = [
  'pastebin.com',
  'paste.ee',
  'pastee.org',
  'termbin.com',
  'requestbin.net',
  'requestbin.com',
  'webhook.site',
  'ngrok.io',
  'ngrok.com',
  'localtunnel.me',
  'serveo.net',
  'pagekite.me',
  'trycloudflare.com',
];

// Known good patterns that might trigger false positives
// Used for intelligent filtering
const FALSE_POSITIVE_WHITELIST = [
  // Documentation examples
  /^\s*\/?\/\/.*example/i,
  /^\s*\/?\/?\s*NOTE:/i,
  /^\s*\/?\/?\s*WARNING:/i,
  /^\s*\*\s*@example/i,
  // Test files
  /\.test\.(js|ts)$/,
  /\.spec\.(js|ts)$/,
  /__tests__/,
  // Legitimate config patterns
  /process\.env\.NODE_ENV/,
];

// Risk scoring weights
const SEVERITY_SCORES = {
  'CRITICAL': 25,
  'HIGH': 15,
  'MEDIUM': 5,
  'LOW': 1,
};

// Confidence multipliers
const CONFIDENCE_MULTIPLIERS = {
  'high': 1.0,
  'medium': 0.75,
  'low': 0.5,
};

module.exports = {
  PATTERNS,
  SUSPICIOUS_DOMAINS,
  FALSE_POSITIVE_WHITELIST,
  SEVERITY_SCORES,
  CONFIDENCE_MULTIPLIERS,
};
