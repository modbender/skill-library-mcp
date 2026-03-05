# Agent Security Auditor

Scans ERC-8004 agents for security vulnerabilities and generates comprehensive security reports.

## Overview

This skill audits ERC-8004 Trustless Agents by querying the Identity Registry and analyzing agent metadata for common security issues. It helps identify potentially malicious or misconfigured agents before interacting with them.

## Features

- **Identity Registry Query**: Fetches agent metadata from the ERC-8004 Identity Registry
- **Metadata Validation**: Checks for missing, empty, or suspicious metadata
- **Endpoint Security**: Analyzes service endpoints for red flags
- **x402 Payment Analysis**: Validates payment configuration
- **Reputation Check**: Queries the Reputation Registry for feedback signals
- **Verification Status**: Checks if endpoints are verified via domain control

## Usage

```bash
# Run the audit script directly with Node.js
node scripts/audit.js <agent-address> [options]

# Options:
#   --rpc <url>        RPC endpoint URL (default: https://eth.llamarpc.com)
#   --chain <id>       Chain ID (default: 1)
#   --output <file>    Output file for JSON report
#   --verbose          Enable verbose logging
```

## Example

```bash
# Audit an agent on Ethereum mainnet
node scripts/audit.js 0x742d35Cc6634C0532925a3b844Bc9e7595f8bE21

# Audit with custom RPC
node scripts/audit.js 0x742d35Cc6634C0532925a3b844Bc9e7595f8bE21 --rpc https://mainnet.infura.io/v3/YOUR_KEY

# Save report to file
node scripts/audit.js 0x742d35Cc6634C0532925a3b844Bc9e7595f8bE21 --output report.json
```

## What Gets Scanned

### Critical Issues
- Missing or empty metadata (no name, description)
- No registered services/endpoints
- Invalid or unreachable agent URI
- No agent wallet configured

### High Severity Issues
- Unverified endpoints (no domain control proof)
- Suspicious endpoint patterns (localhost, IP addresses, unusual ports)
- No x402 payment support warning
- No reputation signals

### Medium Severity Issues
- No validation registrations
- Missing supportedTrust indicators
- Inactive agent status

### Info
- Reputation score summary
- Validation count
- Service endpoint count

## Architecture

```
agent-security-auditor/
├── SKILL.md           # This file
├── scripts/
│   └── audit.js       # Main audit logic
└── references/
    └── ERC-8004.md    # ERC-8004 specification reference
```

## Dependencies

- ethers.js ^6.x - Ethereum blockchain interaction
- node-fetch or built-in fetch - HTTP requests for off-chain metadata

## Exit Codes

- `0` - Audit completed successfully
- `1` - Invalid agent address
- `2` - Blockchain connection error
- `3` - Critical error during audit

## Notes

- Requires internet connection for RPC calls and metadata fetching
- Some checks require off-chain metadata fetching which may be slow
- Reputation and validation registries are optional deployments