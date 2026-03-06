#!/usr/bin/env node
/**
 * DailyTempMarket - Node.js helper library for AI agents
 *
 * Usage:
 *   const TempMarket = require('./tempmarket.js');
 *   const market = new TempMarket();
 *
 *   // Read market state
 *   const state = await market.getMarketState();
 *   console.log('Baseline:', state.baseline, '°C');
 *   console.log('Betting open:', state.isBettingOpen);
 *
 *   // Build bet transaction for Bankr
 *   const tx = market.buildBetHigher('0.01');
 *   // Submit tx via Bankr API
 *
 * CLI:
 *   node tempmarket.js              # Show market status
 *   node tempmarket.js bet higher   # Show HIGHER bet transaction
 *   node tempmarket.js bet lower    # Show LOWER bet transaction
 *
 * Built by potdealer x Ollie for Netclawd's SensorNet
 */

const { ethers } = require('ethers');

const CONTRACT_ADDRESS = '0xA3F09E6792351e95d1fd9d966447504B5668daF6';
const RPC_URL = 'https://mainnet.base.org';
const CHAIN_ID = 8453;

// Minimal ABI for the functions we need
const ABI = [
  'function betHigher() payable',
  'function betLower() payable',
  'function getMarketState() view returns (uint256 round, int256 baseline, uint256 higherTotal, uint256 lowerTotal, uint256 rollover, bool isBettingOpen, uint256 secondsUntilClose, uint256 secondsUntilSettle)',
  'function getMyBet(address user) view returns (uint256 higherAmt, uint256 lowerAmt)',
  'function getBetCounts() view returns (uint256 higherCount, uint256 lowerCount)',
  'function yesterdayTemp() view returns (int256)',
  'function bettingOpen() view returns (bool)',
  'function higherPool() view returns (uint256)',
  'function lowerPool() view returns (uint256)',
  'function rolloverPool() view returns (uint256)',
  'function currentRound() view returns (uint256)',
  'function minBet() view returns (uint256)',
  'function timeUntilBettingCloses() view returns (uint256)',
  'function timeUntilSettlement() view returns (uint256)'
];

class TempMarket {
  constructor(rpcUrl = RPC_URL) {
    this.provider = new ethers.JsonRpcProvider(rpcUrl);
    this.contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, this.provider);
    this.address = CONTRACT_ADDRESS;
  }

  // ============ Read Functions ============

  /**
   * Get full market state
   * @returns {Object} Market state with human-readable values
   */
  async getMarketState() {
    const state = await this.contract.getMarketState();
    return {
      round: Number(state.round),
      baseline: Number(state.baseline) / 100, // Convert to °C
      baselineRaw: Number(state.baseline),
      higherPool: ethers.formatEther(state.higherTotal),
      lowerPool: ethers.formatEther(state.lowerTotal),
      rollover: ethers.formatEther(state.rollover),
      totalPot: ethers.formatEther(state.higherTotal + state.lowerTotal + state.rollover),
      isBettingOpen: state.isBettingOpen,
      secondsUntilClose: Number(state.secondsUntilClose),
      secondsUntilSettle: Number(state.secondsUntilSettle),
      timeUntilClose: this._formatTime(Number(state.secondsUntilClose)),
      timeUntilSettle: this._formatTime(Number(state.secondsUntilSettle))
    };
  }

  /**
   * Get yesterday's baseline temperature
   * @returns {number} Temperature in °C
   */
  async getBaseline() {
    const temp = await this.contract.yesterdayTemp();
    return Number(temp) / 100;
  }

  /**
   * Check if betting is currently open
   * @returns {boolean}
   */
  async isBettingOpen() {
    return await this.contract.bettingOpen();
  }

  /**
   * Get pool sizes
   * @returns {Object} Pool sizes in ETH
   */
  async getPools() {
    const [higher, lower, rollover] = await Promise.all([
      this.contract.higherPool(),
      this.contract.lowerPool(),
      this.contract.rolloverPool()
    ]);
    return {
      higher: ethers.formatEther(higher),
      lower: ethers.formatEther(lower),
      rollover: ethers.formatEther(rollover),
      total: ethers.formatEther(higher + lower + rollover)
    };
  }

  /**
   * Get bet counts
   * @returns {Object} Number of bettors on each side
   */
  async getBetCounts() {
    const counts = await this.contract.getBetCounts();
    return {
      higher: Number(counts.higherCount),
      lower: Number(counts.lowerCount)
    };
  }

  /**
   * Get a user's bet for current round
   * @param {string} address - User address
   * @returns {Object} Bet amounts in ETH
   */
  async getMyBet(address) {
    const bet = await this.contract.getMyBet(address);
    return {
      higher: ethers.formatEther(bet.higherAmt),
      lower: ethers.formatEther(bet.lowerAmt),
      hasBet: bet.higherAmt > 0 || bet.lowerAmt > 0
    };
  }

  /**
   * Get minimum bet amount
   * @returns {string} Minimum bet in ETH
   */
  async getMinBet() {
    const minBet = await this.contract.minBet();
    return ethers.formatEther(minBet);
  }

  // ============ Build Transactions for Bankr ============

  /**
   * Build a HIGHER bet transaction
   * @param {string} amountEth - Amount in ETH (e.g., "0.01")
   * @returns {Object} Transaction JSON for Bankr
   */
  buildBetHigher(amountEth = '0.01') {
    const iface = new ethers.Interface(ABI);
    const data = iface.encodeFunctionData('betHigher', []);
    const valueWei = ethers.parseEther(amountEth).toString();

    return {
      to: CONTRACT_ADDRESS,
      data: data,
      value: valueWei,
      chainId: CHAIN_ID
    };
  }

  /**
   * Build a LOWER bet transaction
   * @param {string} amountEth - Amount in ETH (e.g., "0.01")
   * @returns {Object} Transaction JSON for Bankr
   */
  buildBetLower(amountEth = '0.01') {
    const iface = new ethers.Interface(ABI);
    const data = iface.encodeFunctionData('betLower', []);
    const valueWei = ethers.parseEther(amountEth).toString();

    return {
      to: CONTRACT_ADDRESS,
      data: data,
      value: valueWei,
      chainId: CHAIN_ID
    };
  }

  // ============ Helpers ============

  _formatTime(seconds) {
    if (seconds <= 0) return 'now';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    }
    return `${minutes}m`;
  }

  /**
   * Calculate potential payout
   * @param {string} side - 'higher' or 'lower'
   * @param {string} betAmount - Bet amount in ETH
   * @param {Object} pools - Pool sizes (from getPools())
   * @returns {Object} Potential payout info
   */
  calculatePotentialPayout(side, betAmount, pools) {
    const bet = parseFloat(betAmount);
    const higher = parseFloat(pools.higher);
    const lower = parseFloat(pools.lower);
    const rollover = parseFloat(pools.rollover);
    const total = higher + lower + rollover;

    const myPool = side === 'higher' ? higher + bet : lower + bet;
    const newTotal = total + bet;
    const houseFee = (higher + lower + bet) * 0.02; // 2% on new bets only
    const winnerPool = newTotal - houseFee;

    const myShare = bet / myPool;
    const payout = myShare * winnerPool;
    const profit = payout - bet;
    const roi = (profit / bet) * 100;

    return {
      potentialPayout: payout.toFixed(4),
      potentialProfit: profit.toFixed(4),
      roi: roi.toFixed(1) + '%',
      myShare: (myShare * 100).toFixed(1) + '%'
    };
  }
}

// ============ CLI Mode ============

async function main() {
  const args = process.argv.slice(2);
  const market = new TempMarket();

  if (args[0] === 'bet') {
    const side = args[1]?.toLowerCase();
    const amount = args[2] || '0.01';

    if (side === 'higher') {
      console.log('\n=== Bet HIGHER Transaction ===\n');
      console.log('Submit this to Bankr:\n');
      console.log(JSON.stringify(market.buildBetHigher(amount), null, 2));
    } else if (side === 'lower') {
      console.log('\n=== Bet LOWER Transaction ===\n');
      console.log('Submit this to Bankr:\n');
      console.log(JSON.stringify(market.buildBetLower(amount), null, 2));
    } else {
      console.log('Usage: node tempmarket.js bet <higher|lower> [amount]');
      console.log('Example: node tempmarket.js bet higher 0.01');
    }
    return;
  }

  // Default: show market status
  console.log('\n=== DailyTempMarket Status ===\n');
  console.log('Contract:', CONTRACT_ADDRESS);
  console.log('');

  try {
    const state = await market.getMarketState();
    const counts = await market.getBetCounts();

    console.log(`Round: ${state.round}`);
    console.log(`Baseline: ${state.baseline}°C (beat this to win HIGHER)`);
    console.log('');
    console.log(`HIGHER pool: ${state.higherPool} ETH (${counts.higher} bettors)`);
    console.log(`LOWER pool:  ${state.lowerPool} ETH (${counts.lower} bettors)`);
    console.log(`Rollover:    ${state.rollover} ETH`);
    console.log(`Total pot:   ${state.totalPot} ETH`);
    console.log('');
    console.log(`Betting open: ${state.isBettingOpen ? 'YES' : 'NO'}`);
    if (state.isBettingOpen) {
      console.log(`Closes in: ${state.timeUntilClose}`);
    }
    console.log(`Settlement in: ${state.timeUntilSettle}`);
    console.log('');
    console.log('To bet, run:');
    console.log('  node tempmarket.js bet higher 0.01');
    console.log('  node tempmarket.js bet lower 0.01');
  } catch (err) {
    console.error('Error reading market state:', err.message);
  }
}

// Run CLI if executed directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = TempMarket;
