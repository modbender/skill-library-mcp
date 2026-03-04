/**
 * USDC integration for Scout
 * Trust-gated payments on Base Sepolia testnet
 */

const { ethers } = require('ethers');

// Base Sepolia testnet config
const BASE_SEPOLIA_RPC = 'https://sepolia.base.org';
const USDC_ADDRESS = '0x036CbD53842c5426634e7929541eC2318f3dCF7e'; // Circle's testnet USDC on Base Sepolia

// Minimal ERC-20 ABI for transfers and balance checks
const ERC20_ABI = [
  'function transfer(address to, uint256 amount) returns (bool)',
  'function approve(address spender, uint256 amount) returns (bool)',
  'function balanceOf(address account) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function allowance(address owner, address spender) view returns (uint256)'
];

class USDCClient {
  constructor(privateKey) {
    this.provider = new ethers.JsonRpcProvider(BASE_SEPOLIA_RPC);
    this.wallet = privateKey
      ? new ethers.Wallet(privateKey, this.provider)
      : null;
    this.usdc = new ethers.Contract(USDC_ADDRESS, ERC20_ABI, this.wallet || this.provider);
  }

  /**
   * Get USDC balance for an address
   */
  async getBalance(address) {
    const balance = await this.usdc.balanceOf(address);
    const decimals = await this.usdc.decimals();
    return parseFloat(ethers.formatUnits(balance, decimals));
  }

  /**
   * Get wallet address
   */
  getAddress() {
    if (!this.wallet) throw new Error('No wallet configured');
    return this.wallet.address;
  }

  /**
   * Send USDC (simple transfer)
   */
  async transfer(toAddress, amount) {
    if (!this.wallet) throw new Error('No wallet configured - set SCOUT_PRIVATE_KEY');
    const decimals = await this.usdc.decimals();
    const amountWei = ethers.parseUnits(amount.toString(), decimals);

    const tx = await this.usdc.transfer(toAddress, amountWei);
    const receipt = await tx.wait();

    return {
      txHash: receipt.hash,
      from: this.wallet.address,
      to: toAddress,
      amount,
      blockNumber: receipt.blockNumber,
      explorerUrl: `https://sepolia.basescan.org/tx/${receipt.hash}`
    };
  }

  /**
   * Trust-gated payment: check trust score, then pay with appropriate safeguards
   */
  async safePay(trustResult, toAddress, requestedAmount, taskDescription) {
    const rec = trustResult.recommendation;

    // Check if transaction is recommended
    if (rec.level === 'VERY_LOW') {
      return {
        status: 'BLOCKED',
        reason: `Agent ${trustResult.agentName} trust score too low (${trustResult.score}/100). Transaction not recommended.`,
        trustScore: trustResult.score,
        recommendation: rec
      };
    }

    // Check amount against recommended max
    if (requestedAmount > rec.maxTransaction) {
      return {
        status: 'OVER_LIMIT',
        reason: `Requested ${requestedAmount} USDC exceeds recommended max of ${rec.maxTransaction} USDC for trust level ${rec.level}.`,
        trustScore: trustResult.score,
        recommendation: rec,
        suggestion: `Consider splitting into ${Math.ceil(requestedAmount / rec.maxTransaction)} smaller transactions.`
      };
    }

    // Determine upfront amount based on trust level
    let upfrontPct;
    if (rec.level === 'HIGH') upfrontPct = 1.0;
    else if (rec.level === 'MEDIUM') upfrontPct = 0.5;
    else upfrontPct = 0.0; // LOW = full escrow

    const upfrontAmount = requestedAmount * upfrontPct;
    const escrowAmount = requestedAmount - upfrontAmount;

    const result = {
      status: 'APPROVED',
      trustScore: trustResult.score,
      trustLevel: rec.level,
      agentName: trustResult.agentName,
      requestedAmount,
      taskDescription,
      upfrontAmount,
      escrowAmount,
      toAddress,
      terms: rec.escrowTerms,
      flags: trustResult.flags,
      transactions: []
    };

    // Execute upfront payment if any
    if (upfrontAmount > 0 && this.wallet) {
      try {
        const balance = await this.getBalance(this.wallet.address);
        if (balance < upfrontAmount) {
          result.status = 'INSUFFICIENT_FUNDS';
          result.reason = `Need ${upfrontAmount} USDC but only have ${balance} USDC`;
          return result;
        }

        const tx = await this.transfer(toAddress, upfrontAmount);
        result.transactions.push({
          type: 'upfront',
          ...tx
        });
      } catch (err) {
        result.status = 'TX_FAILED';
        result.reason = err.message;
        return result;
      }
    }

    if (escrowAmount > 0) {
      result.escrowNote = `${escrowAmount} USDC held in escrow. Release with: scout release --to ${toAddress} --amount ${escrowAmount}`;
    }

    return result;
  }

  /**
   * Check on-chain USDC activity for an address
   * (Basic: just checks current balance as a signal)
   */
  async checkActivity(address) {
    try {
      const balance = await this.getBalance(address);
      const ethBalance = parseFloat(
        ethers.formatEther(await this.provider.getBalance(address))
      );

      return {
        address,
        usdcBalance: balance,
        ethBalance: Math.round(ethBalance * 10000) / 10000,
        hasUSDC: balance > 0,
        hasGas: ethBalance > 0,
        chain: 'Base Sepolia'
      };
    } catch (err) {
      return {
        address,
        error: err.message,
        hasUSDC: false,
        hasGas: false
      };
    }
  }
}

module.exports = { USDCClient, USDC_ADDRESS, BASE_SEPOLIA_RPC };
