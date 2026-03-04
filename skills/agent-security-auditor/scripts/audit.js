#!/usr/bin/env node

/**
 * ERC-8004 Agent Security Auditor
 * Scans agents registered on the Identity Registry for security vulnerabilities
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const IDENTITY_REGISTRY_ADDRESS = '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432';
const DEFAULT_RPC = 'https://eth.llamarpc.com';
const DEFAULT_CHAIN_ID = 1;

// ABI fragments for Identity Registry
const IDENTITY_REGISTRY_ABI = [
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function tokenURI(uint256 tokenId) view returns (string)',
  'function getMetadata(uint256 agentId, string memory metadataKey) view returns (bytes memory)',
  'function getAgentWallet(uint256 agentId) view returns (address)',
  'function getMetadata(uint256 agentId, string metadataKey) external view returns (bytes memory)',
  'function getAgentWallet(uint256 agentId) external view returns (address)',
  'function ownerOf(uint256 agentId) external view returns (address)',
  'function tokenURI(uint256 agentId) external view returns (string)',
  'function balanceOf(address owner) external view returns (uint256)',
  'function tokenOfOwnerByIndex(address owner, uint256 index) external view returns (uint256)',
  'function totalSupply() external view returns (uint256)',
  'function tokenByIndex(uint256 index) external view returns (uint256)'
];

// ABI for Reputation Registry (optional - deployed separately)
const REPUTATION_REGISTRY_ABI = [
  'function getIdentityRegistry() view returns (address)',
  'function getSummary(uint256 agentId, address[] calldata clientAddresses, string tag1, string tag2) view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals)',
  'function getClients(uint256 agentId) view returns (address[] memory)'
];

// Severity levels
const SEVERITY = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  INFO: 'INFO'
};

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  green: '\x1b[32m',
  dim: '\x1b[2m'
};

/**
 * Parse command line arguments
 */
function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    rpc: DEFAULT_RPC,
    chainId: DEFAULT_CHAIN_ID,
    output: null,
    verbose: false
  };

  let agentAddress = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--rpc' && args[i + 1]) {
      options.rpc = args[i + 1];
      i++;
    } else if (args[i] === '--chain' && args[i + 1]) {
      options.chainId = parseInt(args[i + 1], 10);
      i++;
    } else if (args[i] === '--output' && args[i + 1]) {
      options.output = args[i + 1];
      i++;
    } else if (args[i] === '--verbose') {
      options.verbose = true;
    } else if (!args[i].startsWith('--')) {
      agentAddress = args[i];
    }
  }

  return { agentAddress, options };
}

/**
 * Validate Ethereum address
 */
function isValidAddress(address) {
  try {
    return ethers.isAddress(address);
  } catch {
    return false;
  }
}

/**
 * Check if a string is a valid URL
 */
function isValidUrl(string) {
  try {
    new URL(string);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if endpoint is suspicious
 */
function isSuspiciousEndpoint(endpoint) {
  try {
    const url = new URL(endpoint);
    
    // Check for localhost
    if (url.hostname === 'localhost' || url.hostname === '127.0.0.1' || url.hostname === '::1') {
      return { suspicious: true, reason: 'Localhost endpoint - not accessible externally' };
    }
    
    // Check for private IP ranges
    const privateRanges = ['10.', '172.16.', '172.17.', '172.18.', '172.19.', '172.2', '172.30.', '172.31.', '192.168.'];
    if (privateRanges.some(range => url.hostname.startsWith(range))) {
      return { suspicious: true, reason: 'Private IP address endpoint' };
    }
    
    // Check for unusual ports
    const unusualPorts = [22, 23, 25, 3389, 4444, 5555, 6666, 6667, 7777, 8888, 9000, 9001];
    const port = parseInt(url.port, 10);
    if (port && unusualPorts.includes(port)) {
      return { suspicious: true, reason: `Unusual port ${port} detected` };
    }
    
    // Check for HTTP instead of HTTPS (warning)
    if (url.protocol === 'http:') {
      return { suspicious: true, reason: 'HTTP endpoint without encryption', severity: 'warning' };
    }
    
    return { suspicious: false };
  } catch {
    return { suspicious: true, reason: 'Invalid endpoint URL format' };
  }
}

/**
 * Fetch JSON from URL with timeout
 */
async function fetchJson(url, timeout = 10000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, { signal: controller.signal });
    clearTimeout(timeoutId);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    throw error;
  }
}

/**
 * Query Reputation Registry for agent feedback
 */
async function queryReputationRegistry(agentId, provider) {
  // Try common Reputation Registry addresses (per ERC-8004, it's a singleton per chain)
  const reputationAddresses = [
    '0x8bFvCL6dG1yyF4p9AC59e8C1aA4eB5e7F3dA123', // Common pattern, may need to be discovered
  ];
  
  // For now, we'll note that reputation registry query requires knowing the deployed address
  // The Identity Registry could have a reference to the reputation registry
  
  return {
    available: false,
    message: 'Reputation Registry address not configured - reputation check skipped'
  };
}

/**
 * Main audit function
 */
async function auditAgent(agentAddress, options) {
  console.log(`${colors.blue}=== ERC-8004 Agent Security Auditor ===${colors.reset}\n`);
  console.log(`Agent Address: ${agentAddress}`);
  console.log(`RPC Endpoint: ${options.rpc}`);
  console.log(`Chain ID: ${options.chainId}\n`);

  const findings = [];
  const report = {
    agentAddress,
    timestamp: new Date().toISOString(),
    chainId: options.chainId,
    identityRegistry: IDENTITY_REGISTRY_ADDRESS,
    metadata: {},
    findings: [],
    summary: {
      critical: 0,
      high: 0,
      medium: 0,
      low: 0,
      info: 0
    }
  };

  try {
    // Connect to blockchain
    const provider = new ethers.JsonRpcProvider(options.rpc);
    
    // Verify network
    const network = await provider.getNetwork();
    console.log(`Connected to network: ${network.name} (chainId: ${network.chainId})\n`);

    // Create Identity Registry contract
    const identityRegistry = new ethers.Contract(
      IDENTITY_REGISTRY_ADDRESS,
      IDENTITY_REGISTRY_ABI,
      provider
    );

    // Step 1: Check if agent exists (try to get owner)
    console.log(`${colors.dim}[1/6] Verifying agent registration...${colors.reset}`);
    
    let agentId;
    try {
      // Try to find the agentId by checking if address owns any tokens
      // First, try if it's already a tokenId (many implementations use address as ID)
      const addressAsUint = BigInt(agentAddress);
      
      try {
        const owner = await identityRegistry.ownerOf(addressAsUint);
        agentId = addressAsUint;
        console.log(`  Found agent with ID: ${agentId}`);
      } catch {
        // Try to find by owner address
        const balance = await identityRegistry.balanceOf(agentAddress);
        if (balance > 0n) {
          agentId = await identityRegistry.tokenOfOwnerByIndex(agentAddress, 0);
          console.log(`  Found agent with ID: ${agentId}`);
        } else {
          // Try sequential IDs
          agentId = null;
          const totalSupply = await identityRegistry.totalSupply();
          for (let i = 0n; i < totalSupply; i++) {
            try {
              const owner = await identityRegistry.ownerOf(i);
              if (owner.toLowerCase() === agentAddress.toLowerCase()) {
                agentId = i;
                break;
              }
            } catch {
              continue;
            }
          }
        }
      }
      
      if (!agentId) {
        findings.push({
          severity: SEVERITY.CRITICAL,
          title: 'Agent Not Registered',
          description: 'No agent found with the provided address',
          recommendation: 'Verify the agent address is correct'
        });
        report.summary.critical++;
        console.log(`  ${colors.red}✗ Agent not found${colors.reset}`);
        return report;
      }
      
      const owner = await identityRegistry.ownerOf(agentId);
      report.metadata.owner = owner;
      console.log(`  ${colors.green}✓ Agent registered, owner: ${owner}${colors.reset}`);
      
    } catch (error) {
      findings.push({
        severity: SEVERITY.CRITICAL,
        title: 'Agent Not Found',
        description: `Could not find agent: ${error.message}`,
        recommendation: 'Verify the agent address is correct'
      });
      report.summary.critical++;
      console.log(`  ${colors.red}✗ Error: ${error.message}${colors.reset}`);
      return report;
    }

    // Step 2: Fetch agent URI
    console.log(`${colors.dim}[2/6] Fetching agent metadata URI...${colors.reset}`);
    
    let agentURI;
    try {
      agentURI = await identityRegistry.tokenURI(agentId);
      report.metadata.agentURI = agentURI;
      console.log(`  Agent URI: ${agentURI}`);
    } catch (error) {
      findings.push({
        severity: SEVERITY.CRITICAL,
        title: 'Missing Agent URI',
        description: 'Could not retrieve agent URI from registry',
        recommendation: 'Contact agent owner to set agentURI'
      });
      report.summary.critical++;
      console.log(`  ${colors.red}✗ Error: ${error.message}${colors.reset}`);
      return report;
    }

    // Step 3: Fetch and parse registration file
    console.log(`${colors.dim}[3/6] Fetching registration file...${colors.reset}`);
    
    let registration;
    try {
      if (agentURI.startsWith('data:')) {
        // Handle base64 encoded data URI
        const base64Data = agentURI.replace('data:application/json;base64,', '');
        const jsonStr = Buffer.from(base64Data, 'base64').toString('utf-8');
        registration = JSON.parse(jsonStr);
      } else {
        registration = await fetchJson(agentURI);
      }
      
      report.metadata.registration = registration;
      console.log(`  ${colors.green}✓ Registration file fetched${colors.reset}`);
      
      // Validate required fields
      if (!registration.name || registration.name.trim() === '') {
        findings.push({
          severity: SEVERITY.CRITICAL,
          title: 'Missing Agent Name',
          description: 'Registration file has empty or missing name field',
          recommendation: 'Add a valid name to the registration file'
        });
        report.summary.critical++;
      }
      
      if (!registration.description || registration.description.trim() === '') {
        findings.push({
          severity: SEVERITY.HIGH,
          title: 'Missing Description',
          description: 'Registration file has empty or missing description',
          recommendation: 'Add a description to the registration file'
        });
        report.summary.high++;
      }
      
      if (!registration.services || registration.services.length === 0) {
        findings.push({
          severity: SEVERITY.CRITICAL,
          title: 'No Service Endpoints',
          description: 'Agent has no registered services/endpoints',
          recommendation: 'Add at least one service endpoint to the registration'
        });
        report.summary.critical++;
      }
      
      // Check if agent is active
      if (registration.active === false) {
        findings.push({
          severity: SEVERITY.MEDIUM,
          title: 'Inactive Agent',
          description: 'Agent is marked as inactive in registration',
          recommendation: 'Only interact with active agents'
        });
        report.summary.medium++;
      }
      
      // Check supportedTrust
      if (!registration.supportedTrust || registration.supportedTrust.length === 0) {
        findings.push({
          severity: SEVERITY.LOW,
          title: 'No Trust Indicators',
          description: 'No trust models specified in registration',
          recommendation: 'Consider using reputation, validation, or TEE attestation'
        });
        report.summary.low++;
      }
      
    } catch (error) {
      findings.push({
        severity: SEVERITY.CRITICAL,
        title: 'Cannot Fetch Registration',
        description: `Failed to fetch registration file: ${error.message}`,
        recommendation: 'Verify the agentURI is accessible and returns valid JSON'
      });
      report.summary.critical++;
      console.log(`  ${colors.red}✗ Error: ${error.message}${colors.reset}`);
      return report;
    }

    // Step 4: Analyze endpoints
    console.log(`${colors.dim}[4/6] Analyzing service endpoints...${colors.reset}`);
    
    if (registration.services && registration.services.length > 0) {
      let verifiedEndpoints = 0;
      let unverifiedEndpoints = 0;
      
      for (const service of registration.services) {
        if (!service.endpoint) continue;
        
        // Check for suspicious endpoints
        const suspicious = isSuspiciousEndpoint(service.endpoint);
        if (suspicious.suspicious) {
          findings.push({
            severity: suspicious.severity === 'warning' ? SEVERITY.LOW : SEVERITY.HIGH,
            title: `Suspicious Endpoint: ${service.name}`,
            description: suspicious.reason,
            recommendation: 'Review endpoint for security concerns'
          });
          if (suspicious.severity === 'warning') {
            report.summary.low++;
          } else {
            report.summary.high++;
          }
        }
        
        // Check if endpoint uses HTTPS
        try {
          const url = new URL(service.endpoint);
          if (url.protocol !== 'https:' && url.protocol !== 'ipfs:' && url.protocol !== 'data:') {
            findings.push({
              severity: SEVERITY.MEDIUM,
              title: `Insecure Endpoint: ${service.name}`,
              description: `Endpoint uses ${url.protocol} instead of HTTPS`,
              recommendation: 'Use HTTPS for secure communication'
            });
            report.summary.medium++;
          }
        } catch {
          // Invalid URL already caught above
        }
        
        // Check for domain verification
        if (service.endpoint.startsWith('https://')) {
          const hostname = new URL(service.endpoint).hostname;
          if (registration.registrations) {
            // Check if endpoint domain matches any verified registration
            // This is a simplified check - real verification would fetch .well-known/agent-registration.json
            unverifiedEndpoints++;
          }
        }
      }
      
      console.log(`  Analyzed ${registration.services.length} service(s)`);
    }

    // Step 5: Check agent wallet
    console.log(`${colors.dim}[5/6] Checking payment configuration...${colors.reset}`);
    
    try {
      const agentWallet = await identityRegistry.getAgentWallet(agentId);
      report.metadata.agentWallet = agentWallet;
      
      if (!agentWallet || agentWallet === ethers.ZeroAddress) {
        findings.push({
          severity: SEVERITY.HIGH,
          title: 'No Agent Wallet',
          description: 'Agent has not configured a payment wallet',
          recommendation: 'Agent should set agentWallet for receiving payments'
        });
        report.summary.high++;
        console.log(`  ${colors.yellow}⚠ No agent wallet configured${colors.reset}`);
      } else {
        console.log(`  ${colors.green}✓ Agent wallet: ${agentWallet}${colors.reset}`);
      }
    } catch (error) {
      console.log(`  ${colors.dim}Could not check agent wallet: ${error.message}${colors.reset}`);
    }

    // Check x402 support
    if (registration.x402Support === true) {
      console.log(`  ${colors.green}✓ x402 payment support enabled${colors.reset}`);
    } else if (registration.x402Support === false) {
      findings.push({
        severity: SEVERITY.LOW,
        title: 'No x402 Payment Support',
        description: 'Agent does not advertise x402 payment support',
        recommendation: 'Consider enabling x402 for standardized payments'
      });
      report.summary.low++;
    }

    // Step 6: Reputation and validation check
    console.log(`${colors.dim}[6/6] Checking reputation signals...${colors.reset}`);
    
    // Note: Reputation Registry is a separate deployment
    // In production, you'd need to discover its address
    report.metadata.reputation = {
      note: 'Reputation Registry check requires separate deployment address'
    };
    
    console.log(`  ${colors.dim}Reputation check requires Reputation Registry deployment${colors.reset}`);

    // Add findings to report
    report.findings = findings;
    
    // Print summary
    console.log(`\n${colors.blue}=== Audit Summary ===${colors.reset}`);
    console.log(`Critical: ${report.summary.critical}`);
    console.log(`High: ${report.summary.high}`);
    console.log(`Medium: ${report.summary.medium}`);
    console.log(`Low: ${report.summary.low}`);
    console.log(`Info: ${report.summary.info}`);
    
    // Print findings
    if (findings.length > 0) {
      console.log(`\n${colors.blue}=== Findings ===${colors.reset}`);
      for (const finding of findings) {
        const color = finding.severity === SEVERITY.CRITICAL ? colors.red :
                      finding.severity === SEVERITY.HIGH ? colors.yellow :
                      finding.severity === SEVERITY.MEDIUM ? colors.blue :
                      colors.dim;
        console.log(`\n${color}[${finding.severity}]${colors.reset} ${finding.title}`);
        console.log(`  ${finding.description}`);
        console.log(`  → ${finding.recommendation}`);
      }
    }

    return report;

  } catch (error) {
    console.error(`\n${colors.red}Error during audit: ${error.message}${colors.reset}`);
    if (options.verbose) {
      console.error(error.stack);
    }
    
    findings.push({
      severity: SEVERITY.CRITICAL,
      title: 'Audit Failed',
      description: error.message,
      recommendation: 'Check RPC endpoint and try again'
    });
    report.findings = findings;
    report.summary.critical++;
    
    return report;
  }
}

/**
 * Main entry point
 */
async function main() {
  const { agentAddress, options } = parseArgs();
  
  if (!agentAddress) {
    console.log('Usage: node audit.js <agent-address> [options]');
    console.log('');
    console.log('Options:');
    console.log('  --rpc <url>        RPC endpoint URL (default: https://eth.llamarpc.com)');
    console.log('  --chain <id>       Chain ID (default: 1)');
    console.log('  --output <file>    Output file for JSON report');
    console.log('  --verbose          Enable verbose logging');
    console.log('');
    console.log('Example:');
    console.log('  node audit.js 0x742d35Cc6634C0532925a3b844Bc9e7595f8bE21');
    process.exit(1);
  }
  
  if (!isValidAddress(agentAddress)) {
    console.error('Invalid Ethereum address');
    process.exit(1);
  }
  
  const report = await auditAgent(agentAddress, options);
  
  // Save to file if requested
  if (options.output) {
    fs.writeFileSync(options.output, JSON.stringify(report, null, 2));
    console.log(`\n${colors.green}Report saved to: ${options.output}${colors.reset}`);
  }
  
  // Exit with error if critical issues found
  if (report.summary.critical > 0) {
    process.exit(3);
  }
  
  process.exit(0);
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(3);
});
