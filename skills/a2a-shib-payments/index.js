#!/usr/bin/env node

/**
 * SHIB Payments Skill for OpenClaw
 * Send/receive SHIB on Polygon with A2A protocol support
 */

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Load config from ~/.env.local or process.env
function loadConfig() {
  const envPath = path.join(process.env.HOME, '.env.local');
  if (fs.existsSync(envPath)) {
    const envContent = fs.readFileSync(envPath, 'utf8');
    envContent.split('\n').forEach(line => {
      const [key, ...valueParts] = line.split('=');
      if (key && valueParts.length) {
        process.env[key.trim()] = valueParts.join('=').trim();
      }
    });
  }

  return {
    rpc: process.env.POLYGON_RPC || 'https://polygon-rpc.com',
    privateKey: process.env.POLYGON_PRIVATE_KEY,
    walletAddress: process.env.POLYGON_WALLET_ADDRESS,
    shibContract: '0x6f8a06447ff6fcf75d803135a7de15ce88c1d4ec',
    network: 'eip155:137' // Polygon mainnet
  };
}

class ShibPaymentAgent {
  constructor(config) {
    this.config = config;
    this.provider = new ethers.JsonRpcProvider(config.rpc);
    
    if (config.privateKey) {
      this.wallet = new ethers.Wallet(config.privateKey, this.provider);
    }

    // SHIB token ABI (minimal)
    this.shibAbi = [
      'function balanceOf(address owner) view returns (uint256)',
      'function transfer(address to, uint256 amount) returns (bool)',
      'function decimals() view returns (uint8)',
      'function symbol() view returns (string)',
      'function name() view returns (string)'
    ];

    this.shibToken = new ethers.Contract(
      config.shibContract,
      this.shibAbi,
      this.wallet || this.provider
    );
  }

  async getBalance(address = null) {
    const target = address || this.config.walletAddress || this.wallet?.address;
    
    if (!target) {
      throw new Error('No address provided and no wallet configured');
    }

    const balance = await this.shibToken.balanceOf(target);
    const decimals = await this.shibToken.decimals();
    const formatted = ethers.formatUnits(balance, decimals);

    return {
      address: target,
      balanceRaw: balance.toString(),
      balance: formatted,
      token: 'SHIB',
      network: 'Polygon'
    };
  }

  async sendPayment(recipient, amountShib) {
    if (!this.wallet) {
      throw new Error('No wallet configured. Set POLYGON_PRIVATE_KEY in ~/.env.local');
    }

    // Validate recipient
    if (!ethers.isAddress(recipient)) {
      throw new Error(`Invalid recipient address: ${recipient}`);
    }

    // Get decimals and convert amount
    const decimals = await this.shibToken.decimals();
    const amount = ethers.parseUnits(amountShib.toString(), decimals);

    console.log(`Sending ${amountShib} SHIB to ${recipient}...`);

    // Check balance
    const balance = await this.shibToken.balanceOf(this.wallet.address);
    if (balance < amount) {
      throw new Error(`Insufficient SHIB balance. Have: ${ethers.formatUnits(balance, decimals)}, Need: ${amountShib}`);
    }

    // Execute transfer with gas limit
    const tx = await this.shibToken.transfer(recipient, amount, {
      gasLimit: 100000 // Safety limit
    });

    console.log(`Transaction submitted: ${tx.hash}`);
    console.log('Waiting for confirmation...');

    const receipt = await tx.wait();

    const gasCost = receipt.gasUsed * receipt.gasPrice;
    const gasCostUSD = await this.estimateGasCostUSD(gasCost);

    return {
      success: true,
      txHash: receipt.hash,
      blockNumber: receipt.blockNumber,
      from: this.wallet.address,
      to: recipient,
      amountShib,
      gasUsed: receipt.gasUsed.toString(),
      gasCostPOL: ethers.formatEther(gasCost),
      gasCostUSD: gasCostUSD,
      explorerUrl: `https://polygonscan.com/tx/${receipt.hash}`
    };
  }

  async estimateGasCostUSD(gasCostWei) {
    // Rough estimate: 1 POL = $0.09 (adjust as needed)
    const polPrice = 0.09;
    const gasCostPOL = parseFloat(ethers.formatEther(gasCostWei));
    return (gasCostPOL * polPrice).toFixed(4);
  }

  async getTokenInfo() {
    const [name, symbol, decimals] = await Promise.all([
      this.shibToken.name(),
      this.shibToken.symbol(),
      this.shibToken.decimals()
    ]);

    return {
      name,
      symbol,
      decimals,
      contract: this.config.shibContract,
      network: 'Polygon (PoS)',
      networkId: this.config.network
    };
  }

  async getTransactionHistory(address, limit = 10) {
    // Note: This requires an API key for PolygonScan
    // For POC, we'll just return a placeholder
    return {
      address,
      message: 'Transaction history requires PolygonScan API integration',
      explorerUrl: `https://polygonscan.com/address/${address}#tokentxns`
    };
  }
}

// CLI Interface
async function main() {
  const config = loadConfig();
  const agent = new ShibPaymentAgent(config);

  const command = process.argv[2];
  const args = process.argv.slice(3);

  try {
    let result;

    switch(command) {
      case 'balance':
        const address = args[0];
        result = await agent.getBalance(address);
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'send':
        if (args.length < 2) {
          console.error('Usage: node index.js send <recipient> <amount>');
          process.exit(1);
        }
        const [recipient, amount] = args;
        result = await agent.sendPayment(recipient, parseFloat(amount));
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'info':
        result = await agent.getTokenInfo();
        console.log(JSON.stringify(result, null, 2));
        break;

      case 'history':
        const historyAddress = args[0] || config.walletAddress;
        result = await agent.getTransactionHistory(historyAddress);
        console.log(JSON.stringify(result, null, 2));
        break;

      default:
        console.log(`
SHIB Payments Skill - Usage:

  node index.js balance [address]       - Check SHIB balance
  node index.js send <to> <amount>      - Send SHIB to address
  node index.js info                    - Get token information
  node index.js history [address]       - View transaction history

Examples:
  node index.js balance
  node index.js send 0x1234...5678 1000
  node index.js info

Configuration:
  Set POLYGON_RPC and POLYGON_PRIVATE_KEY in ~/.env.local
  See SKILL.md for setup guide
        `);
        process.exit(0);
    }

  } catch (error) {
    console.error('Error:', error.message);
    process.exit(1);
  }
}

// Run CLI if called directly
if (require.main === module) {
  main();
}

// Export for use as module
module.exports = { ShibPaymentAgent, loadConfig };
