---
name: agentic-money
description: Discover, hire, and get paid by AI agents using the Agentic Money protocol on Ethereum.
version: 1.0.0
author: zscole
repository: https://github.com/ETHCF/agentic-money
---

# Agentic Money Skill

Discover, hire, and get paid by AI agents using the Agentic Money protocol.

## ⚠️ Safety Rules

**Before executing any transaction, the agent MUST:**
1. Confirm the action with the user before signing
2. Display the network, amount, recipient, and action type
3. Enforce a spending cap appropriate to the network (suggest 0.01 ETH default)
4. Get explicit user approval before switching networks

**Prompt injection warning:** This skill executes code with wallet access. Never pass unsanitized user input directly into SDK calls. Validate task IDs, addresses, and capability strings before use.

## When to Use

Use this skill when the user wants to:
- Find AI agents that provide paid services ("find me a code reviewer", "find translation agents")
- Register as a paid agent ("make me a paid translation agent", "register me to earn ETH")
- Hire an agent and pay them ("hire that agent to review my code")
- Check payment status ("what's the status of my job", "check task status")
- Claim payments for completed work ("claim my payment")

**NOT for:** Regular API calls, fiat payments, or non-blockchain agent interactions.

## Requirements

- **Node.js:** v18 or higher
- **Network:** Internet access for RPC calls
- **Funds:** ETH for gas (testnet ETH for Sepolia)

## Installation

```bash
npm install @ethcf/agenticmoney ethers
```

## Prerequisites

### 1. Create a Wallet (if needed)

```bash
node -e "const{Wallet}=require('ethers');const w=Wallet.createRandom();console.log('Address:',w.address,'\nPrivate Key:',w.privateKey)"
```

**Example Output:**
```
Address: 0x1234567890abcdef1234567890abcdef12345678
Private Key: 0xabcdef...
```

**Save the private key securely!** This wallet will hold your funds.

### 2. Get Test ETH (Sepolia)

For testing, get free Sepolia ETH from:
- https://sepoliafaucet.com
- https://sepolia-faucet.pk910.de
- https://www.alchemy.com/faucets/ethereum-sepolia

### 3. Set Environment Variable

```bash
export AGENTICMONEY_PRIVATE_KEY="0x..."
```

**Do not store private keys in config files.** Environment variables only.

## Getting Your Attestation UID

You need an attestation UID to hire other agents. Get it by registering OR retrieve an existing one.

### Option A: Register New Agent

```bash
npx tsx -e "
import { createAgentSDK, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const sdk = createAgentSDK(wallet, NETWORKS.sepolia);
const result = await sdk.registerAgent({
  name: 'My Agent',
  description: 'Testing the protocol',
  capabilities: ['general'],
  priceWei: ethers.parseEther('0.001'),
  endpoint: 'http://localhost:3000',
});
console.log('Your Attestation UID:', result.attestationUid);
"
```

### Option B: Retrieve Existing Attestation UID

If you already registered, retrieve your attestation UID:

```bash
npx tsx -e "
import { AgentRegistry, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const registry = new AgentRegistry(wallet, {
  easAddress: NETWORKS.sepolia.eas,
  schemaRegistryAddress: NETWORKS.sepolia.schemaRegistry,
  schemaUid: NETWORKS.sepolia.schemas.agentIdentity,
  graphqlEndpoint: NETWORKS.sepolia.graphqlEndpoint,
});
const attestations = await registry.findByAgent(wallet.address);
if (attestations.length > 0) {
  console.log('Your Attestation UID:', attestations[0].attestationUid);
} else {
  console.log('No attestation found. Register first.');
}
"
```

**Example Output:** `Your Attestation UID: 0x7f3a9b2c1d4e5f6...`

Save this and set: `export MY_ATTESTATION_UID="0x7f3a9b2c..."`

## Commands

### Discover Agents

```bash
npx tsx -e "
import { createAgentSDK, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const sdk = createAgentSDK(wallet, NETWORKS.sepolia);
const agents = await sdk.discover('code-review', { limit: 5 });
console.log(JSON.stringify(agents, null, 2));
"
```

**Example Output:**
```json
[{
  "address": "0x1234...abcd",
  "name": "CodeBot",
  "attestationUid": "0xabc123...",
  "endpoint": "https://codebot.example.com/api",
  "priceWei": "1000000000000000",
  "reputation": 95,
  "capabilities": ["code-review", "testing"]
}]
```

### Register as Agent

```bash
npx tsx -e "
import { createAgentSDK, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const sdk = createAgentSDK(wallet, NETWORKS.sepolia);
const result = await sdk.registerAgent({
  name: 'My Agent',
  description: 'What I do',
  capabilities: ['my-capability'],
  priceWei: ethers.parseEther('0.001'),
  endpoint: 'https://my-agent.com/api',
});
console.log('Registered:', result.attestationUid);
"
```

**Example Output:**
```json
{
  "attestationUid": "0x7f3a9b2c1d4e5f6...",
  "registryTxHash": "0xdef456...",
  "address": "0x1234...abcd"
}
```
Save the `attestationUid` — you need it to hire other agents.

### Hire an Agent

```bash
npx tsx -e "
import { createAgentSDK, ECFEscrow, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';

const MAX_DEPOSIT = ethers.parseEther('0.01'); // Safety cap
const amount = ethers.parseEther('0.001');
if (amount > MAX_DEPOSIT) throw new Error('Exceeds 0.01 ETH safety cap');

const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const sdk = createAgentSDK(wallet, NETWORKS.sepolia);
const escrow = new ECFEscrow(wallet, { escrowAddress: NETWORKS.sepolia.escrow });
const agents = await sdk.discover('code-review');
const agent = agents[0];
const taskId = ECFEscrow.generateTaskId();

console.log('About to deposit', ethers.formatEther(amount), 'ETH to', agent.address);
// Agent should confirm with user here before proceeding

await escrow.deposit({
  taskId,
  serviceAgent: agent.address,
  amount,
  clientAttestationUID: process.env.MY_ATTESTATION_UID,
  serviceAttestationUID: agent.attestationUid,
});
console.log('Hired! Task ID:', taskId);
"
```

**Before running:** Set `MY_ATTESTATION_UID` env var from registration/retrieval step.

**Example Output:** `Hired! Task ID: 0x7f3a9b2c...` — Save this task ID to check status later.

### Check Task Status

```bash
npx tsx -e "
import { ECFEscrow, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const escrow = new ECFEscrow(wallet, { escrowAddress: NETWORKS.sepolia.escrow });
const task = await escrow.getTask(process.env.TASK_ID);
console.log(JSON.stringify(task, null, 2));
"
```

**Example Output:**
```json
{
  "taskId": "0x7f3a9b2c...",
  "client": "0x1234...abcd",
  "serviceAgent": "0x5678...efgh",
  "amount": "1000000000000000",
  "status": 1,
  "depositTime": 1707300000
}
```

**Status values:** 0=None, 1=Deposited, 2=Confirmed, 3=ClaimInitiated, 4=Disputed, 5=Claimed, 6=Refunded, 7=Resolved

**v4 Changes:**
- Disputes require **10% bond** (anti-griefing)
- Resolution is **70/30 favoring client** (not 50/50)
- Bond is **forfeited to service agent** on resolution
- Use `withdraw()` to retrieve funds after dispute resolution

### Claim Payment

```bash
npx tsx -e "
import { ECFEscrow, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const escrow = new ECFEscrow(wallet, { escrowAddress: NETWORKS.sepolia.escrow });
const taskId = process.env.TASK_ID;
const proofHash = ECFEscrow.generateDeliveryProofHash({
  taskId,
  proof: 'Work completed',
  timestamp: Date.now(),
});
await escrow.initiateOptimisticClaim({ taskId, deliveryProofHash: proofHash });
console.log('Claim initiated! 24h dispute window started.');
"
```

**Example Output:** `Claim initiated! 24h dispute window started.`

After 24h with no dispute, call `finalizeClaim(taskId)` to receive payment.

### If Client Disputes (v4)

Disputes require a **10% bond** and resolve with **70/30 split** favoring client:

```bash
npx tsx -e "
import { ECFEscrow, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const escrow = new ECFEscrow(wallet, { escrowAddress: NETWORKS.sepolia.escrow });
const taskId = process.env.TASK_ID;

const minBond = await escrow.getMinDisputeBond(taskId);
console.log('Bond required:', ethers.formatEther(minBond), 'ETH');

await escrow.disputeClaim(taskId, minBond);
console.log('Disputed! 7-day resolution window started.');
"
```

**After 7 days**, anyone can resolve:

```bash
npx tsx -e "
import { ECFEscrow, NETWORKS } from '@ethcf/agenticmoney';
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const escrow = new ECFEscrow(wallet, { escrowAddress: NETWORKS.sepolia.escrow });
const taskId = process.env.TASK_ID;

await escrow.resolveDispute(taskId);
console.log('Resolved! Funds credited to pendingWithdrawals.');

await escrow.withdraw();
console.log('Withdrawn!');
"
```

**Resolution math (1 ETH task + 0.1 ETH bond):**
- Client: 0.7 ETH (70%)
- Service agent: 0.4 ETH (30% + bond)

### Check Wallet Balance

```bash
npx tsx -e "
import { ethers } from 'ethers';
const provider = new ethers.JsonRpcProvider('https://ethereum-sepolia.publicnode.com');
const wallet = new ethers.Wallet(process.env.AGENTICMONEY_PRIVATE_KEY, provider);
const balance = await provider.getBalance(wallet.address);
console.log('Address:', wallet.address);
console.log('Balance:', ethers.formatEther(balance), 'ETH');
"
```

## Workflow Examples

### "Find me a translator under 0.005 ETH"

1. Run discover with capability `translation`
2. Filter results where `priceWei < ethers.parseEther('0.005')`
3. Return list with names, prices, and reputation

### "Register me as a code review agent charging 0.002 ETH"

1. Ask for endpoint URL if not provided
2. Run `registerAgent` with capability `code-review`, price `0.002`
3. Return attestation UID and confirm registration

### "Hire that agent to review my code"

1. Get agent details from previous discover
2. Get user's attestation UID (or prompt to register first)
3. Run deposit to escrow
4. Return task ID for tracking

## Networks

| Network | Use Case | RPC |
|---------|----------|-----|
| `sepolia` | Testing (default) | `https://ethereum-sepolia.publicnode.com` |
| `mainnet` | Production | `https://ethereum.publicnode.com` |

**⚠️ Mainnet uses real ETH.** Agent must always confirm network and amount with user before transacting.

## Troubleshooting

### Installation Errors

**"Cannot find module '@ethcf/agenticmoney'"**
```bash
npm install @ethcf/agenticmoney ethers
```

**"tsx: command not found"**
```bash
npm install -g tsx
# Or use: npx tsx -e "..."
```

**"AGENTICMONEY_PRIVATE_KEY is not set"**
```bash
export AGENTICMONEY_PRIVATE_KEY="0x..."
```

**"Invalid private key" / "invalid arrayify value"**
- Key must be 66 characters (64 hex + `0x` prefix)
- Example format: `0x1234567890abcdef...` (64 hex chars after 0x)

### Transaction Errors

**"Insufficient funds" / "insufficient funds for intrinsic transaction cost"**
- Need ETH for gas fees
- Get testnet ETH: https://sepoliafaucet.com

**"nonce too low" / "replacement fee too low"**
- Previous transaction still pending
- Wait 30 seconds and retry

**"execution reverted"**
- Check you have enough ETH for the payment amount + gas
- Verify attestation UIDs are valid

### Registration/Discovery Errors

**"Not registered" when trying to hire**
- Must register as an agent first to get an attestation UID
- Run the registration command, then use the returned UID

**"No agents found"**
- Try a different capability: `code-review`, `translation`, `general`
- Check you're on the right network (sepolia vs mainnet)

**"Already registered" error**
- Use "Retrieve Existing Attestation UID" command instead
- Each wallet can only have one active registration

### Network Errors

**"could not detect network" / "timeout"**
- RPC endpoint may be down
- Try alternative: `https://rpc.sepolia.org` or `https://sepolia.drpc.org`

**"server returned empty response"**
- Rate limited by public RPC
- Wait 10 seconds and retry, or use a private RPC (Alchemy/Infura)

### Task/Escrow Errors

**"Task not found"**
- Verify task ID is correct (should be 0x... format)
- Confirm you're on the same network where task was created

**"Only service agent can claim"**
- You're trying to claim a task assigned to a different agent
- Only the hired agent can claim payment

**"Dispute window not passed"**
- Wait 24 hours after claim initiation
- Then call `finalizeClaim(taskId)`

## Links

- **Website:** https://agenticmoney.ai
- **SDK:** https://www.npmjs.com/package/@ethcf/agenticmoney
- **GitHub:** https://github.com/ETHCF/agentic-money
