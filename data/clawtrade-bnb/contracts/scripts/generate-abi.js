const fs = require("fs");
const path = require("path");

// Manual ABI for YieldVault (matches the Solidity contract)
const YieldVaultABI = [
  {
    inputs: [
      {
        internalType: "string",
        name: "_vaultId",
        type: "string",
      },
      {
        internalType: "address",
        name: "_underlying",
        type: "address",
      },
    ],
    stateMutability: "nonpayable",
    type: "constructor",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: false,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
    ],
    name: "FeeDeducted",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "user",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "yieldAmount",
        type: "uint256",
      },
    ],
    name: "Harvest",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "user",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
    ],
    name: "Deposit",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "address",
        name: "user",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
    ],
    name: "Withdraw",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: false,
        internalType: "uint256",
        name: "yield",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "newShares",
        type: "uint256",
      },
    ],
    name: "Compound",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "string",
        name: "vaultId",
        type: "string",
      },
      {
        indexed: false,
        internalType: "string",
        name: "action",
        type: "string",
      },
      {
        indexed: true,
        internalType: "address",
        name: "user",
        type: "address",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "uint256",
        name: "timestamp",
        type: "uint256",
      },
    ],
    name: "ExecutionRecorded",
    type: "event",
  },
  {
    anonymous: false,
    inputs: [
      {
        indexed: true,
        internalType: "string",
        name: "vaultId",
        type: "string",
      },
      {
        indexed: false,
        internalType: "string",
        name: "action",
        type: "string",
      },
      {
        indexed: true,
        internalType: "address",
        name: "user",
        type: "address",
      },
      {
        indexed: true,
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
      {
        indexed: false,
        internalType: "bool",
        name: "success",
        type: "bool",
      },
      {
        indexed: false,
        internalType: "string",
        name: "message",
        type: "string",
      },
    ],
    name: "ActionExecuted",
    type: "event",
  },
  {
    inputs: [],
    name: "compound",
    outputs: [
      {
        internalType: "uint256",
        name: "newShares",
        type: "uint256",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "amount",
        type: "uint256",
      },
    ],
    name: "deposit",
    outputs: [
      {
        internalType: "uint256",
        name: "sharesIssued",
        type: "uint256",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [],
    name: "harvest",
    outputs: [
      {
        internalType: "uint256",
        name: "yieldAmount",
        type: "uint256",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
    ],
    name: "withdraw",
    outputs: [
      {
        internalType: "uint256",
        name: "amountRedeemed",
        type: "uint256",
      },
    ],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "assets",
        type: "uint256",
      },
    ],
    name: "calculateSharesFromAssets",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
    ],
    name: "calculateAssetsFromShares",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "user",
        type: "address",
      },
    ],
    name: "calculateUserYield",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [
      {
        internalType: "address",
        name: "user",
        type: "address",
      },
    ],
    name: "getShareBalance",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "getTotalAssets",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "getTotalShares",
    outputs: [
      {
        internalType: "uint256",
        name: "",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "getVaultInfo",
    outputs: [
      {
        internalType: "string",
        name: "id",
        type: "string",
      },
      {
        internalType: "address",
        name: "tokenAddress",
        type: "address",
      },
      {
        internalType: "uint256",
        name: "total",
        type: "uint256",
      },
      {
        internalType: "uint256",
        name: "shares",
        type: "uint256",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "vaultId",
    outputs: [
      {
        internalType: "string",
        name: "",
        type: "string",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "underlying",
    outputs: [
      {
        internalType: "address",
        name: "",
        type: "address",
      },
    ],
    stateMutability: "view",
    type: "function",
  },
  {
    inputs: [],
    name: "pause",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
  {
    inputs: [],
    name: "unpause",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
];

function generateABI() {
  console.log("📄 Generating YieldVault ABI...\n");

  const outputFile = path.join(__dirname, "../abi/YieldVault.json");
  const outputDir = path.dirname(outputFile);

  // Create abi directory if it doesn't exist
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
    console.log(`📁 Created directory: ${outputDir}`);
  }

  // Write ABI to file
  fs.writeFileSync(outputFile, JSON.stringify(YieldVaultABI, null, 2));
  console.log(`✅ ABI saved to: ${outputFile}`);

  // Also create a JavaScript export
  const jsFile = path.join(__dirname, "../abi/YieldVault.js");
  const jsContent = `// Auto-generated YieldVault ABI
module.exports = ${JSON.stringify(YieldVaultABI, null, 2)};
`;
  fs.writeFileSync(jsFile, jsContent);
  console.log(`✅ JS export saved to: ${jsFile}`);

  // Create a TypeScript declaration file
  const tsFile = path.join(__dirname, "../abi/YieldVault.d.ts");
  const tsContent = `// Auto-generated YieldVault ABI TypeScript declaration
export const YieldVaultABI: any[];
export default YieldVaultABI;
`;
  fs.writeFileSync(tsFile, tsContent);
  console.log(`✅ TypeScript declaration saved to: ${tsFile}`);

  // Create integration guide
  const integrationFile = path.join(__dirname, "../ABI_USAGE.md");
  const integrationContent = `# YieldVault ABI Usage

## Import ABI

### JavaScript
\`\`\`javascript
const YieldVaultABI = require('./abi/YieldVault.json');
// or
const { YieldVaultABI } = require('./abi/YieldVault.js');
\`\`\`

### TypeScript
\`\`\`typescript
import YieldVaultABI from './abi/YieldVault.json';
\`\`\`

## Contract Events

### ExecutionRecorded
Emitted on every action (deposit, withdraw, harvest, compound)
\`\`\`solidity
event ExecutionRecorded(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 amount,
    uint256 shares,
    uint256 timestamp
);
\`\`\`

### ActionExecuted
Emitted with success/failure status
\`\`\`solidity
event ActionExecuted(
    string indexed vaultId,
    string action,
    address indexed user,
    uint256 indexed amount,
    bool success,
    string message
);
\`\`\`

## Contract Functions

| Function | Input | Output | Action |
|----------|-------|--------|--------|
| deposit() | uint256 amount | uint256 shares | Deposit tokens and receive shares |
| withdraw() | uint256 shares | uint256 amount | Burn shares and receive tokens |
| harvest() | - | uint256 yield | Claim yield without reinvesting |
| compound() | - | uint256 newShares | Reinvest yield as new shares |
| getShareBalance() | address user | uint256 | Get user's share balance |
| getTotalAssets() | - | uint256 | Get total vault assets |
| getTotalShares() | - | uint256 | Get total shares issued |
| getVaultInfo() | - | (id, token, assets, shares) | Get vault metadata (compatible with mockdata.json) |

## Agent Integration

Use events to track vault activity:

\`\`\`javascript
contract.on('ExecutionRecorded', (vaultId, action, user, amount, shares) => {
  console.log(\`[\${vaultId}] \${action} by \${user}: \${amount} amount, \${shares} shares\`);
});

contract.on('ActionExecuted', (vaultId, action, user, amount, success, message) => {
  console.log(\`Action \${action} - Success: \${success}, Message: \${message}\`);
});
\`\`\`

## Data Compatibility

The contract is compatible with mockdata.json structure:

\`\`\`json
{
  "vault_id": "vault_bnb_lp_001",
  "token": "0xB4FBF271143F901BF5EE8b0E99033aBEA4912312",
  "shares": 1000000000000000000,
  "amount": 500000000000000000
}
\`\`\`

Generated: $(date)
`;
  fs.writeFileSync(integrationFile, integrationContent);
  console.log(`✅ Integration guide saved to: ${integrationFile}`);

  console.log("\n✨ ABI generation complete!");
  console.log("\nUse these files for agent integration:");
  console.log(`  • ${outputFile}`);
  console.log(`  • ${jsFile}`);
  console.log(`  • ${tsFile}`);
}

// Run if called directly
if (require.main === module) {
  try {
    generateABI();
  } catch (error) {
    console.error("❌ Error:", error.message);
    process.exit(1);
  }
}

module.exports = { YieldVaultABI, generateABI };
