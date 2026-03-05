/**
 * Pattern Detection - ported from Harkonnen static-analysis.h
 * Detects suspicious strings, shellcode patterns, and API references
 */

// Shellcode patterns (byte sequences commonly found in exploits)
const SHELLCODE_PATTERNS = [
  { pattern: Buffer.from([0x31, 0xc0, 0x50, 0x68]), name: 'x86 shellcode prologue (xor eax; push)' },
  { pattern: Buffer.from([0xeb, 0xfe]), name: 'Infinite loop (jmp $-2)' },
  { pattern: Buffer.from([0xcc, 0xcc, 0xcc, 0xcc]), name: 'INT3 breakpoint sled' },
  { pattern: Buffer.from([0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90, 0x90]), name: 'NOP sled' },
  { pattern: Buffer.from([0x31, 0xc9, 0xf7, 0xe1]), name: 'x86 register clearing' },
  { pattern: Buffer.from([0x48, 0x31, 0xc0]), name: 'x64 xor rax, rax' },
  { pattern: Buffer.from([0x48, 0x31, 0xff]), name: 'x64 xor rdi, rdi' },
];

// Suspicious API references (Linux/macOS only)
const SUSPICIOUS_APIS = [
  // Process manipulation (Unix)
  'ptrace',           // Debugger/injection
  'process_vm_readv', // Read another process memory (Linux)
  'process_vm_writev',// Write another process memory (Linux)
  'task_for_pid',     // Get task port for another process (macOS)
  'mach_vm_read',     // Read VM of another task (macOS)
  'mach_vm_write',    // Write VM of another task (macOS)
  
  // Code injection / dynamic loading
  'dlopen',           // Load shared library
  'dlsym',            // Get symbol from library
  'NSCreateObjectFileImageFromMemory', // macOS in-memory loading
  
  // Memory manipulation
  'mmap',             // Map memory (can create executable regions)
  'mprotect',         // Change memory protection
  'memfd_create',     // Create anonymous file in memory (Linux)
  'fexecve',          // Execute from fd
  
  // Execution
  'execve',           // Execute program
  'execl',
  'execlp',
  'execle',
  'execv',
  'execvp',
  'posix_spawn',      // Spawn process
  'posix_spawnp',
  'system',           // Shell command
  'popen',            // Shell command with pipe
  
  // Network (suspicious in non-network tools)
  'socket',
  'connect',
  'bind',
  'listen',
  'accept',
  
  // Keylogging (macOS)
  'CGEventTapCreate',         // Event tap for key capture
  'CGEventTapEnable',
  'IOHIDManagerCreate',       // HID device access
  
  // Anti-debugging
  'PT_DENY_ATTACH',   // macOS anti-debug
  'P_TRACED',         // Check if being traced
  'sysctl',           // Can check for debugger
  
  // Privilege escalation
  'setuid',           // Set user ID
  'setgid',           // Set group ID
  'seteuid',          // Set effective UID
  'setegid',          // Set effective GID
  'AuthorizationExecuteWithPrivileges', // macOS priv escalation (deprecated but still used)
  
  // Persistence (macOS)
  'SMJobBless',       // Install privileged helper
  'LSRegisterURL',    // Register app
  
  // Environment manipulation
  'DYLD_INSERT_LIBRARIES', // macOS dylib injection
  'LD_PRELOAD'             // Linux shared library injection
];

// Suspicious strings
const SUSPICIOUS_STRINGS = [
  // Command execution
  '/bin/sh',
  '/bin/bash',
  'cmd.exe',
  'powershell',
  'cmd /c',
  
  // Reverse shells
  '/dev/tcp/',
  'bash -i',
  'nc -e',
  'ncat',
  
  // Persistence
  '/etc/cron',
  'launchd',
  'LaunchAgents',
  'LaunchDaemons',
  
  // Data exfiltration
  'pastebin.com',
  'transfer.sh',
  'file.io',
  
  // C2 indicators
  'beacon',
  'payload',
  'shellcode',
  'backdoor',
  'rootkit',
  'keylog',
  'ransom'
];

// URL/IP patterns (regexes)
const URL_PATTERN = /https?:\/\/[^\s<>"{}|\\^`[\]]+/gi;
const IP_PATTERN = /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g;
const BASE64_PATTERN = /[A-Za-z0-9+/]{40,}={0,2}/g;

/**
 * Find a pattern in a buffer
 * @param {Buffer} buffer 
 * @param {Buffer} pattern 
 * @returns {number[]} Array of offsets where pattern was found
 */
function findPattern(buffer, pattern) {
  const offsets = [];
  let pos = 0;

  while (pos <= buffer.length - pattern.length) {
    const idx = buffer.indexOf(pattern, pos);
    if (idx === -1) break;
    offsets.push(idx);
    pos = idx + 1;
  }

  return offsets;
}

/**
 * Find a string in a buffer (case insensitive)
 * @param {Buffer} buffer 
 * @param {string} str 
 * @returns {number[]} Array of offsets
 */
function findString(buffer, str) {
  const offsets = [];
  const strLower = str.toLowerCase();
  const strUpper = str.toUpperCase();
  const strBuffer = Buffer.from(str);
  const strBufferLower = Buffer.from(strLower);
  const strBufferUpper = Buffer.from(strUpper);

  // Try exact match first
  let pos = 0;
  while (pos <= buffer.length - strBuffer.length) {
    let idx = buffer.indexOf(strBuffer, pos);
    if (idx === -1) {
      idx = buffer.indexOf(strBufferLower, pos);
    }
    if (idx === -1) {
      idx = buffer.indexOf(strBufferUpper, pos);
    }
    if (idx === -1) break;
    offsets.push(idx);
    pos = idx + 1;
  }

  return offsets;
}

/**
 * Scan buffer for all suspicious patterns
 * @param {Buffer} buffer 
 * @returns {object} Scan results
 */
function scanPatterns(buffer) {
  const results = {
    shellcodePatterns: [],
    suspiciousAPIs: [],
    suspiciousStrings: [],
    urls: [],
    ips: [],
    base64Blobs: [],
    findings: []
  };

  // Scan for shellcode patterns
  for (const { pattern, name } of SHELLCODE_PATTERNS) {
    const offsets = findPattern(buffer, pattern);
    if (offsets.length > 0) {
      results.shellcodePatterns.push({ name, count: offsets.length, offsets: offsets.slice(0, 5) });
      results.findings.push(`Shellcode pattern: ${name}`);
    }
  }

  // Convert buffer to string for text pattern matching
  // Use latin1 to preserve all bytes
  const text = buffer.toString('latin1');

  // Scan for suspicious APIs
  for (const api of SUSPICIOUS_APIS) {
    const offsets = findString(buffer, api);
    if (offsets.length > 0) {
      results.suspiciousAPIs.push({ api, count: offsets.length });
      results.findings.push(`Suspicious API: ${api}`);
    }
  }

  // Scan for suspicious strings
  for (const str of SUSPICIOUS_STRINGS) {
    const offsets = findString(buffer, str);
    if (offsets.length > 0) {
      results.suspiciousStrings.push({ string: str, count: offsets.length });
      results.findings.push(`Suspicious string: ${str}`);
    }
  }

  // Extract URLs
  const urls = text.match(URL_PATTERN) || [];
  results.urls = [...new Set(urls)].slice(0, 10);
  if (results.urls.length > 0) {
    results.findings.push(`Found ${results.urls.length} URL(s)`);
  }

  // Extract IPs
  const ips = text.match(IP_PATTERN) || [];
  // Filter out common safe IPs
  const filteredIPs = ips.filter(ip => 
    !ip.startsWith('127.') && 
    !ip.startsWith('0.') &&
    ip !== '255.255.255.255'
  );
  results.ips = [...new Set(filteredIPs)].slice(0, 10);
  if (results.ips.length > 0) {
    results.findings.push(`Found ${results.ips.length} IP address(es)`);
  }

  // Look for large base64 blobs (potential encoded payloads)
  const base64 = text.match(BASE64_PATTERN) || [];
  const largeBase64 = base64.filter(b => b.length > 100);
  results.base64Blobs = largeBase64.length;
  if (largeBase64.length > 0) {
    results.findings.push(`Found ${largeBase64.length} large base64 blob(s) - potential encoded payload`);
  }

  return results;
}

/**
 * Calculate threat score based on patterns
 * @param {object} patternResults 
 * @returns {number} Score 0-100
 */
function calculatePatternScore(patternResults) {
  let score = 0;

  // Shellcode patterns are very suspicious
  score += patternResults.shellcodePatterns.length * 20;

  // Suspicious APIs
  score += Math.min(patternResults.suspiciousAPIs.length * 5, 30);

  // Suspicious strings
  score += Math.min(patternResults.suspiciousStrings.length * 3, 20);

  // Network indicators
  if (patternResults.urls.length > 0) score += 10;
  if (patternResults.ips.length > 0) score += 10;

  // Base64 blobs
  score += Math.min(patternResults.base64Blobs * 5, 15);

  return Math.min(score, 100);
}

module.exports = {
  scanPatterns,
  calculatePatternScore,
  findPattern,
  findString,
  SUSPICIOUS_APIS,
  SUSPICIOUS_STRINGS,
  SHELLCODE_PATTERNS
};
