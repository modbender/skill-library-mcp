#!/usr/bin/env node
/**
 * Solidity Guardian - Smart Contract Security Analyzer
 * Detects vulnerabilities, suggests fixes, generates reports.
 */

const fs = require('fs');
const path = require('path');

// Vulnerability patterns with detection regex and fix suggestions
const VULNERABILITY_PATTERNS = {
  // Critical
  'SG-001': {
    id: 'SG-001',
    title: 'Reentrancy Vulnerability',
    severity: 'critical',
    pattern: /\.call\{.*value.*\}|\.transfer\(|\.send\(/,
    antiPattern: /ReentrancyGuard|nonReentrant|_status\s*=/,
    contextCheck: (lines, lineNum, content) => {
      // Check if state is modified AFTER external call
      const beforeCall = lines.slice(Math.max(0, lineNum - 5), lineNum).join('\n');
      const afterCall = lines.slice(lineNum, Math.min(lines.length, lineNum + 5)).join('\n');
      const stateModAfter = /\w+\s*[+\-*/]?=\s*[^=]/.test(afterCall) && 
                           !afterCall.includes('bool success');
      return stateModAfter;
    },
    description: 'External call found before state update. Attacker can re-enter.',
    suggestion: 'Use ReentrancyGuard and follow checks-effects-interactions pattern. Update state BEFORE external calls.',
    references: ['https://swcregistry.io/docs/SWC-107']
  },
  'SG-002': {
    id: 'SG-002',
    title: 'Unprotected Selfdestruct',
    severity: 'critical',
    pattern: /selfdestruct\s*\(/,
    antiPattern: /onlyOwner|require\s*\(\s*msg\.sender\s*==|onlyRole/,
    description: 'selfdestruct without access control can destroy the contract.',
    suggestion: 'Add onlyOwner modifier or access control. Consider removing selfdestruct entirely.',
    references: ['https://swcregistry.io/docs/SWC-106']
  },
  'SG-003': {
    id: 'SG-003',
    title: 'Delegatecall to Untrusted Contract',
    severity: 'critical',
    pattern: /\.delegatecall\s*\(/,
    contextCheck: (lines, lineNum, content) => {
      const line = lines[lineNum];
      // Check if target is from user input or storage that could be manipulated
      return /delegatecall\([^)]*\(/.test(line) || 
             lines.slice(Math.max(0, lineNum - 3), lineNum).some(l => 
               /address.*=.*_|address.*=.*param|address.*=.*arg/.test(l));
    },
    description: 'Delegatecall with potentially untrusted target allows code execution in contract context.',
    suggestion: 'Only delegatecall to trusted, immutable implementation addresses. Use OpenZeppelin proxy patterns.',
    references: ['https://swcregistry.io/docs/SWC-112']
  },

  // High
  'SG-010': {
    id: 'SG-010',
    title: 'Missing Access Control',
    severity: 'high',
    pattern: /function\s+\w+.*public|function\s+\w+.*external/,
    contextCheck: (lines, lineNum, content) => {
      const funcLine = lines[lineNum];
      const funcBody = lines.slice(lineNum, Math.min(lines.length, lineNum + 10)).join('\n');
      // Sensitive operations without access control
      const sensitiveOps = /\.transfer\(|\.call\{|selfdestruct|suicide|delegatecall|_mint\(|_burn\(|withdraw/;
      const hasAccessControl = /onlyOwner|onlyRole|require\s*\(\s*msg\.sender\s*==|_checkRole|hasRole/;
      return sensitiveOps.test(funcBody) && !hasAccessControl.test(funcBody) && 
             !funcLine.includes('view') && !funcLine.includes('pure');
    },
    description: 'Sensitive function lacks access control.',
    suggestion: 'Add onlyOwner, onlyRole, or custom access control modifier.',
    references: ['https://swcregistry.io/docs/SWC-105']
  },
  'SG-011': {
    id: 'SG-011',
    title: 'Unchecked ERC20 Transfer',
    severity: 'high',
    pattern: /\.transfer\s*\(|\.transferFrom\s*\(/,
    antiPattern: /SafeERC20|safeTransfer|require\s*\([^)]*transfer/,
    contextCheck: (lines, lineNum, content) => {
      const line = lines[lineNum];
      // Skip ETH transfers (address.transfer)
      if (/payable\s*\(/.test(line)) return false;
      // Check if it's likely an ERC20 call
      return /\w+\.transfer\s*\(/.test(line) && !/msg\.sender\.transfer|payable\(/.test(line);
    },
    description: 'ERC20 transfer without checking return value. Some tokens return false instead of reverting.',
    suggestion: 'Use SafeERC20.safeTransfer() from OpenZeppelin.',
    references: ['https://swcregistry.io/docs/SWC-104']
  },
  'SG-012': {
    id: 'SG-012',
    title: 'Integer Overflow/Underflow',
    severity: 'high',
    pattern: /\+\+|\-\-|\+\s*=|\-\s*=|\*\s*=|\/\s*=/,
    contextCheck: (lines, lineNum, content) => {
      // Only flag for Solidity < 0.8.0
      const pragmaMatch = content.match(/pragma\s+solidity\s+[\^~]?(0\.\d+)/);
      if (pragmaMatch) {
        const version = parseFloat(pragmaMatch[1]);
        return version < 0.8;
      }
      return false;
    },
    antiPattern: /SafeMath|using\s+SafeMath/,
    description: 'Arithmetic operation in Solidity < 0.8 without SafeMath.',
    suggestion: 'Upgrade to Solidity 0.8+ or use SafeMath library.',
    references: ['https://swcregistry.io/docs/SWC-101']
  },
  'SG-013': {
    id: 'SG-013',
    title: 'tx.origin Authentication',
    severity: 'high',
    pattern: /tx\.origin/,
    contextCheck: (lines, lineNum, content) => {
      const line = lines[lineNum];
      // Flag if used for authentication
      return /require.*tx\.origin|tx\.origin\s*==|==\s*tx\.origin/.test(line);
    },
    description: 'Using tx.origin for authentication is vulnerable to phishing attacks.',
    suggestion: 'Use msg.sender instead of tx.origin for authentication.',
    references: ['https://swcregistry.io/docs/SWC-115']
  },
  'SG-014': {
    id: 'SG-014',
    title: 'Weak Randomness',
    severity: 'high',
    pattern: /block\.timestamp|block\.number|blockhash/,
    contextCheck: (lines, lineNum, content) => {
      const context = lines.slice(Math.max(0, lineNum - 2), lineNum + 3).join('\n');
      // Flag if used for randomness
      return /random|rand|lottery|winner|select|pick|shuffle|keccak256.*block\./i.test(context);
    },
    description: 'Block variables are predictable. Miners can manipulate them.',
    suggestion: 'Use Chainlink VRF or commit-reveal scheme for secure randomness.',
    references: ['https://swcregistry.io/docs/SWC-120']
  },

  // Medium
  'SG-020': {
    id: 'SG-020',
    title: 'Floating Pragma',
    severity: 'medium',
    pattern: /pragma\s+solidity\s+[\^~]/,
    description: 'Floating pragma allows compilation with different compiler versions.',
    suggestion: 'Pin to a specific version: pragma solidity 0.8.20;',
    references: ['https://swcregistry.io/docs/SWC-103']
  },
  'SG-021': {
    id: 'SG-021',
    title: 'Missing Zero Address Check',
    severity: 'medium',
    pattern: /function\s+\w+.*address\s+\w+/,
    contextCheck: (lines, lineNum, content) => {
      const funcBody = lines.slice(lineNum, Math.min(lines.length, lineNum + 15)).join('\n');
      const hasAddressParam = /address\s+_?\w+/.test(lines[lineNum]);
      const checksZero = /require.*!=\s*address\s*\(\s*0\s*\)|require.*!=\s*0x0|_require.*Zero/.test(funcBody);
      return hasAddressParam && !checksZero && /=\s*_?\w+;/.test(funcBody);
    },
    description: 'Address parameter assigned without zero address validation.',
    suggestion: 'Add: require(_addr != address(0), "Zero address");',
    references: []
  },
  'SG-022': {
    id: 'SG-022',
    title: 'Timestamp Dependence',
    severity: 'medium',
    pattern: /block\.timestamp/,
    contextCheck: (lines, lineNum, content) => {
      const context = lines.slice(lineNum, lineNum + 3).join('\n');
      // Flag if used in conditions
      return /if\s*\(.*block\.timestamp|require.*block\.timestamp|block\.timestamp\s*[<>=]/.test(context);
    },
    description: 'Logic depends on block.timestamp which can be manipulated by miners.',
    suggestion: 'Use block.number for time-based logic or accept ~15 second variance.',
    references: ['https://swcregistry.io/docs/SWC-116']
  },
  'SG-023': {
    id: 'SG-023',
    title: 'DoS with Revert in Loop',
    severity: 'medium',
    pattern: /for\s*\(|while\s*\(/,
    contextCheck: (lines, lineNum, content) => {
      const loopBody = lines.slice(lineNum, Math.min(lines.length, lineNum + 15)).join('\n');
      // Check for external calls or transfers in loop
      return /\.transfer\(|\.call\{|\.send\(|require\s*\(/.test(loopBody);
    },
    description: 'External call in loop can cause DoS if one call reverts.',
    suggestion: 'Use pull-over-push pattern. Let users withdraw individually.',
    references: ['https://swcregistry.io/docs/SWC-113']
  },

  // Low
  'SG-030': {
    id: 'SG-030',
    title: 'Missing Event Emission',
    severity: 'low',
    pattern: /function\s+\w+.*public|function\s+\w+.*external/,
    contextCheck: (lines, lineNum, content) => {
      const funcLine = lines[lineNum];
      if (funcLine.includes('view') || funcLine.includes('pure')) return false;
      
      // Find function body
      let braceCount = 0;
      let started = false;
      let funcBody = '';
      for (let i = lineNum; i < Math.min(lines.length, lineNum + 30); i++) {
        funcBody += lines[i] + '\n';
        braceCount += (lines[i].match(/\{/g) || []).length;
        braceCount -= (lines[i].match(/\}/g) || []).length;
        if (braceCount > 0) started = true;
        if (started && braceCount === 0) break;
      }
      
      // Check if function modifies state but has no emit
      const modifiesState = /\w+\s*=\s*[^=]/.test(funcBody) && !/bool\s+success/.test(funcBody);
      const hasEmit = /emit\s+\w+/.test(funcBody);
      return modifiesState && !hasEmit;
    },
    description: 'State-changing function without event emission.',
    suggestion: 'Emit events for all state changes to enable off-chain tracking.',
    references: []
  },
  'SG-031': {
    id: 'SG-031',
    title: 'Magic Numbers',
    severity: 'low',
    pattern: /[=<>]\s*\d{3,}|\/\s*\d{2,}|\*\s*\d{2,}/,
    antiPattern: /constant|immutable|10\*\*|1e\d/,
    description: 'Hardcoded numeric values reduce readability.',
    suggestion: 'Use named constants: uint256 constant FEE_DENOMINATOR = 10000;',
    references: []
  },
  'SG-032': {
    id: 'SG-032',
    title: 'Implicit Visibility',
    severity: 'low',
    pattern: /^\s*function\s+\w+\s*\([^)]*\)\s*(?!public|private|internal|external)/m,
    description: 'Function without explicit visibility specifier.',
    suggestion: 'Always specify visibility: public, private, internal, or external.',
    references: ['https://swcregistry.io/docs/SWC-100']
  },

  // Additional Critical Patterns
  'SG-004': {
    id: 'SG-004',
    title: 'Uninitialized Storage Pointer',
    severity: 'critical',
    pattern: /\w+\s+storage\s+\w+\s*;/,
    description: 'Uninitialized storage pointer can overwrite arbitrary storage slots.',
    suggestion: 'Always initialize storage pointers or use memory keyword.',
    references: ['https://swcregistry.io/docs/SWC-109']
  },
  'SG-005': {
    id: 'SG-005',
    title: 'Signature Replay',
    severity: 'critical',
    pattern: /ecrecover\s*\(/,
    antiPattern: /nonce|deadline|block\.chainid|_useNonce/,
    description: 'Signature verification without replay protection.',
    suggestion: 'Include nonce, deadline, and chainId in signed message. Use EIP-712.',
    references: ['https://swcregistry.io/docs/SWC-121']
  },
  'SG-006': {
    id: 'SG-006',
    title: 'Arbitrary Jump with Function Type',
    severity: 'critical',
    pattern: /function\s*\([^)]*\)\s*(internal|external|public|private)?\s*\w*\s*;/,
    contextCheck: (lines, lineNum, content) => {
      const context = lines.slice(lineNum, lineNum + 5).join('\n');
      return /=\s*\w+\[/.test(context); // Assignment from array
    },
    description: 'Function type variable assigned from user input can lead to arbitrary code execution.',
    suggestion: 'Validate function selector or use fixed function references.',
    references: ['https://swcregistry.io/docs/SWC-127']
  },

  // Additional High Patterns  
  'SG-015': {
    id: 'SG-015',
    title: 'Unprotected Ether Withdrawal',
    severity: 'high',
    pattern: /\.transfer\s*\(|\.send\s*\(|\.call\{.*value/,
    contextCheck: (lines, lineNum, content) => {
      const funcStart = lines.slice(Math.max(0, lineNum - 15), lineNum).join('\n');
      const hasAccessControl = /onlyOwner|onlyRole|require\s*\(\s*msg\.sender|_checkRole/.test(funcStart);
      const isWithdraw = /withdraw|claim|redeem/i.test(funcStart);
      return isWithdraw && !hasAccessControl;
    },
    description: 'Withdrawal function without access control or ownership check.',
    suggestion: 'Add access control or ensure only rightful owner can withdraw.',
    references: ['https://swcregistry.io/docs/SWC-105']
  },
  'SG-016': {
    id: 'SG-016',
    title: 'Unchecked Low-Level Call',
    severity: 'high',
    pattern: /\.call\s*\(|\.delegatecall\s*\(|\.staticcall\s*\(/,
    antiPattern: /require\s*\(\s*success|if\s*\(\s*!?\s*success/,
    contextCheck: (lines, lineNum, content) => {
      const context = lines.slice(lineNum, lineNum + 3).join('\n');
      return !/(bool\s+)?success.*=/.test(lines[lineNum]) || 
             !/require\s*\(\s*success|if\s*\(\s*!?\s*success/.test(context);
    },
    description: 'Low-level call without checking return value.',
    suggestion: 'Always check the success return value: (bool success, ) = addr.call(...); require(success);',
    references: ['https://swcregistry.io/docs/SWC-104']
  },
  'SG-017': {
    id: 'SG-017',
    title: 'Dangerous Strict Equality',
    severity: 'high',
    pattern: /==\s*(address\s*\(\s*this\s*\)\s*\.)?balance|balance\s*==/,
    description: 'Strict equality check on contract balance can be manipulated via selfdestruct.',
    suggestion: 'Use >= or <= instead of == for balance checks.',
    references: ['https://swcregistry.io/docs/SWC-132']
  },
  'SG-018': {
    id: 'SG-018',
    title: 'Use of Deprecated Functions',
    severity: 'high',
    pattern: /suicide\s*\(|block\.blockhash\s*\(|sha3\s*\(|callcode\s*\(|throw\s*;/,
    description: 'Deprecated Solidity function used.',
    suggestion: 'Replace: suicide→selfdestruct, block.blockhash→blockhash, sha3→keccak256, throw→revert().',
    references: ['https://swcregistry.io/docs/SWC-111']
  },
  'SG-019': {
    id: 'SG-019',
    title: 'Incorrect Constructor Name',
    severity: 'high',
    pattern: /function\s+\w+\s*\([^)]*\)\s*(public|external)?\s*\{/,
    contextCheck: (lines, lineNum, content) => {
      // Check if function name matches contract name (old constructor style)
      const contractMatch = content.match(/contract\s+(\w+)/);
      if (!contractMatch) return false;
      const contractName = contractMatch[1];
      const funcMatch = lines[lineNum].match(/function\s+(\w+)/);
      return funcMatch && funcMatch[1] === contractName;
    },
    description: 'Function has same name as contract (pre-0.4.22 constructor pattern).',
    suggestion: 'Use constructor() instead of function ContractName().',
    references: ['https://swcregistry.io/docs/SWC-118']
  },

  // Additional Medium Patterns
  'SG-025': {
    id: 'SG-025',
    title: 'Shadowing State Variables',
    severity: 'medium',
    pattern: /function\s+\w+[^{]*\{/,
    contextCheck: (lines, lineNum, content) => {
      // Find state variables
      const stateVars = content.match(/^\s*(uint|int|address|bool|bytes|string|mapping)\d*\s+(?:public|private|internal)?\s*(\w+)/gm);
      if (!stateVars) return false;
      const stateVarNames = stateVars.map(v => v.match(/(\w+)\s*[;=]/)?.[1]).filter(Boolean);
      
      // Check function params
      const funcLine = lines[lineNum];
      const params = funcLine.match(/\(([^)]+)\)/)?.[1] || '';
      return stateVarNames.some(name => params.includes(name));
    },
    description: 'Function parameter shadows state variable.',
    suggestion: 'Use different names for parameters and state variables (prefix with _).',
    references: ['https://swcregistry.io/docs/SWC-119']
  },
  'SG-026': {
    id: 'SG-026',
    title: 'Unbounded Loop',
    severity: 'medium',
    pattern: /for\s*\([^;]*;\s*\w+\s*<\s*\w+\.length/,
    description: 'Loop iterates over dynamic array. Can exceed gas limit.',
    suggestion: 'Limit iterations or use pagination. Consider pull-over-push pattern.',
    references: ['https://swcregistry.io/docs/SWC-128']
  },
  'SG-027': {
    id: 'SG-027',
    title: 'Block Gas Limit DoS',
    severity: 'medium',
    pattern: /\.push\s*\(/,
    contextCheck: (lines, lineNum, content) => {
      // Check if pushing to array that's iterated
      const context = lines.slice(Math.max(0, lineNum - 5), lineNum + 10).join('\n');
      return /for\s*\([^)]*\.length/.test(context);
    },
    description: 'Array grows unbounded and is iterated. May exceed block gas limit.',
    suggestion: 'Implement array size limits or pagination.',
    references: ['https://swcregistry.io/docs/SWC-128']
  },
  'SG-028': {
    id: 'SG-028',
    title: 'State Change After External Call',
    severity: 'medium',
    pattern: /\.call\{|\.transfer\(|\.send\(/,
    contextCheck: (lines, lineNum, content) => {
      const afterCall = lines.slice(lineNum + 1, lineNum + 5).join('\n');
      // Check for state changes (assignments to storage)
      return /\w+\s*=\s*[^=]/.test(afterCall) && !/bool\s+success|success\s*=/.test(afterCall);
    },
    description: 'State modified after external call (potential reentrancy).',
    suggestion: 'Move state changes before external calls (checks-effects-interactions).',
    references: ['https://swcregistry.io/docs/SWC-107']
  },
  'SG-029': {
    id: 'SG-029',
    title: 'Assert Instead of Require',
    severity: 'medium',
    pattern: /assert\s*\(/,
    contextCheck: (lines, lineNum, content) => {
      const line = lines[lineNum];
      // Assert should only be used for invariants, not input validation
      return /assert\s*\(\s*\w+\s*[<>=!]/.test(line);
    },
    description: 'assert() used for input validation. Consumes all gas on failure.',
    suggestion: 'Use require() for input validation, assert() only for invariants.',
    references: ['https://swcregistry.io/docs/SWC-110']
  },

  // Additional Low Patterns
  'SG-033': {
    id: 'SG-033',
    title: 'Missing Indexed Event Parameters',
    severity: 'low',
    pattern: /event\s+\w+\s*\([^)]*address[^)]*\)/,
    antiPattern: /indexed\s+address|address\s+indexed/,
    description: 'Address parameters in events should be indexed for efficient filtering.',
    suggestion: 'Add indexed keyword: event Transfer(address indexed from, address indexed to, uint256 value);',
    references: []
  },
  'SG-034': {
    id: 'SG-034',
    title: 'Public Function Could Be External',
    severity: 'low',
    pattern: /function\s+\w+[^{]*public[^{]*\{/,
    contextCheck: (lines, lineNum, content) => {
      const funcMatch = lines[lineNum].match(/function\s+(\w+)/);
      if (!funcMatch) return false;
      const funcName = funcMatch[1];
      // Check if function is called internally
      const internalCalls = content.match(new RegExp(`\\b${funcName}\\s*\\(`, 'g')) || [];
      return internalCalls.length <= 1; // Only the definition
    },
    description: 'Public function not called internally could be external (saves gas).',
    suggestion: 'Change public to external if function is only called externally.',
    references: []
  },
  'SG-035': {
    id: 'SG-035',
    title: 'Unused Return Value',
    severity: 'low',
    pattern: /\w+\.\w+\s*\([^)]*\)\s*;/,
    contextCheck: (lines, lineNum, content) => {
      const line = lines[lineNum];
      // Check for common functions that return values
      return /\.add\(|\.sub\(|\.mul\(|\.div\(|\.allowance\(|\.balanceOf\(/.test(line);
    },
    description: 'Return value of function call not used.',
    suggestion: 'Check return value or explicitly ignore: (, ) = func();',
    references: []
  },
  'SG-036': {
    id: 'SG-036',
    title: 'Use of Assembly',
    severity: 'low',
    pattern: /assembly\s*\{/,
    description: 'Inline assembly bypasses Solidity safety checks.',
    suggestion: 'Ensure assembly is thoroughly reviewed. Document why it is necessary.',
    references: []
  },
  'SG-037': {
    id: 'SG-037',
    title: 'Gas-Inefficient Storage Reads',
    severity: 'low',
    pattern: /for\s*\([^{]*\{/,
    contextCheck: (lines, lineNum, content) => {
      const loopBody = lines.slice(lineNum, lineNum + 10).join('\n');
      // Check for repeated storage access in loop
      const storageAccess = loopBody.match(/\b(balances|allowances|_balances|_allowances|mapping)\b/g);
      return storageAccess && storageAccess.length > 2;
    },
    description: 'Repeated storage reads in loop. Cache in memory for gas savings.',
    suggestion: 'Cache storage values in memory variables before loop.',
    references: []
  },
  'SG-038': {
    id: 'SG-038',
    title: 'Missing Error Messages',
    severity: 'low',
    pattern: /require\s*\([^,)]+\)\s*;/,
    description: 'require() without error message makes debugging difficult.',
    suggestion: 'Add error message: require(condition, "Descriptive error");',
    references: []
  },
  'SG-039': {
    id: 'SG-039',
    title: 'Use Custom Errors',
    severity: 'low',
    pattern: /require\s*\([^)]+,\s*"[^"]+"\s*\)/,
    contextCheck: (lines, lineNum, content) => {
      // Only flag for Solidity >= 0.8.4
      const pragmaMatch = content.match(/pragma\s+solidity\s+[\^~]?(0\.8\.(\d+))/);
      if (pragmaMatch && parseInt(pragmaMatch[2]) >= 4) return true;
      return false;
    },
    description: 'String error messages cost more gas than custom errors (Solidity 0.8.4+).',
    suggestion: 'Use custom errors: error Unauthorized(); ... revert Unauthorized();',
    references: []
  },
  'SG-040': {
    id: 'SG-040',
    title: 'Hardcoded Gas Amount',
    severity: 'low',
    pattern: /\.call\{[^}]*gas\s*:\s*\d+/,
    description: 'Hardcoded gas values may break with EVM updates.',
    suggestion: 'Avoid hardcoding gas. Let EVM determine gas or use gasleft().',
    references: ['https://swcregistry.io/docs/SWC-134']
  }
};

// Analyze a single Solidity file
function analyzeFile(filePath, options = {}) {
  const content = fs.readFileSync(filePath, 'utf8');
  const lines = content.split('\n');
  const findings = [];
  
  for (const [id, vuln] of Object.entries(VULNERABILITY_PATTERNS)) {
    // Skip if severity filter doesn't match
    if (options.severity && !options.severity.includes(vuln.severity)) continue;
    
    // Check anti-pattern first (if file has protection, skip)
    if (vuln.antiPattern && vuln.antiPattern.test(content)) continue;
    
    // Find pattern matches
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Skip comments
      if (line.trim().startsWith('//') || line.trim().startsWith('*')) continue;
      
      if (vuln.pattern.test(line)) {
        // Run context check if defined
        if (vuln.contextCheck && !vuln.contextCheck(lines, i, content)) continue;
        
        findings.push({
          id: vuln.id,
          title: vuln.title,
          severity: vuln.severity,
          file: filePath,
          line: i + 1,
          code: line.trim(),
          description: vuln.description,
          suggestion: vuln.suggestion,
          references: vuln.references || []
        });
      }
    }
  }
  
  return findings;
}

// Analyze a directory recursively
function analyzeDirectory(dirPath, options = {}) {
  const findings = [];
  
  function walk(dir) {
    const files = fs.readdirSync(dir);
    for (const file of files) {
      const fullPath = path.join(dir, file);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        // Skip node_modules and common non-source directories
        if (!['node_modules', '.git', 'artifacts', 'cache', 'out'].includes(file)) {
          walk(fullPath);
        }
      } else if (file.endsWith('.sol')) {
        findings.push(...analyzeFile(fullPath, options));
      }
    }
  }
  
  walk(dirPath);
  return findings;
}

// Generate markdown report
function generateMarkdownReport(findings, projectPath) {
  const now = new Date().toISOString().split('T')[0];
  
  const bySeverity = {
    critical: findings.filter(f => f.severity === 'critical'),
    high: findings.filter(f => f.severity === 'high'),
    medium: findings.filter(f => f.severity === 'medium'),
    low: findings.filter(f => f.severity === 'low')
  };
  
  let report = `# Security Audit Report

**Project:** ${projectPath}
**Date:** ${now}
**Tool:** Solidity Guardian

## Summary

| Severity | Count |
|----------|-------|
| 🔴 Critical | ${bySeverity.critical.length} |
| 🟠 High | ${bySeverity.high.length} |
| 🟡 Medium | ${bySeverity.medium.length} |
| 🔵 Low | ${bySeverity.low.length} |
| **Total** | **${findings.length}** |

`;

  for (const [severity, items] of Object.entries(bySeverity)) {
    if (items.length === 0) continue;
    
    const emoji = { critical: '🔴', high: '🟠', medium: '🟡', low: '🔵' }[severity];
    report += `## ${emoji} ${severity.charAt(0).toUpperCase() + severity.slice(1)} Findings

`;
    
    for (const finding of items) {
      report += `### ${finding.id}: ${finding.title}

**File:** \`${finding.file}\`
**Line:** ${finding.line}

\`\`\`solidity
${finding.code}
\`\`\`

**Issue:** ${finding.description}

**Recommendation:** ${finding.suggestion}

${finding.references.length > 0 ? `**References:** ${finding.references.join(', ')}` : ''}

---

`;
    }
  }
  
  return report;
}

// CLI
if (require.main === module) {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node analyze.js <path> [--format json|markdown] [--severity critical,high,medium,low]');
    process.exit(1);
  }
  
  const targetPath = args[0];
  const formatIdx = args.indexOf('--format');
  const format = formatIdx !== -1 ? args[formatIdx + 1] : 'table';
  const sevIdx = args.indexOf('--severity');
  const severity = sevIdx !== -1 ? args[sevIdx + 1].split(',') : null;
  
  const options = { severity };
  
  let findings;
  const stat = fs.statSync(targetPath);
  if (stat.isDirectory()) {
    findings = analyzeDirectory(targetPath, options);
  } else {
    findings = analyzeFile(targetPath, options);
  }
  
  if (format === 'json') {
    console.log(JSON.stringify(findings, null, 2));
  } else if (format === 'markdown') {
    console.log(generateMarkdownReport(findings, targetPath));
  } else {
    // Table format
    const colors = { critical: '\x1b[31m', high: '\x1b[33m', medium: '\x1b[36m', low: '\x1b[37m' };
    const reset = '\x1b[0m';
    
    console.log(`\nSolidity Guardian Analysis: ${targetPath}\n`);
    console.log('='.repeat(80));
    
    if (findings.length === 0) {
      console.log('\n✅ No issues found!\n');
    } else {
      for (const f of findings) {
        console.log(`${colors[f.severity]}[${f.severity.toUpperCase()}]${reset} ${f.id}: ${f.title}`);
        console.log(`  📁 ${f.file}:${f.line}`);
        console.log(`  💡 ${f.suggestion}`);
        console.log();
      }
      
      console.log('='.repeat(80));
      console.log(`Total: ${findings.length} issues found`);
      console.log(`  Critical: ${findings.filter(f => f.severity === 'critical').length}`);
      console.log(`  High: ${findings.filter(f => f.severity === 'high').length}`);
      console.log(`  Medium: ${findings.filter(f => f.severity === 'medium').length}`);
      console.log(`  Low: ${findings.filter(f => f.severity === 'low').length}`);
    }
  }
}

module.exports = { analyzeFile, analyzeDirectory, generateMarkdownReport, VULNERABILITY_PATTERNS };
