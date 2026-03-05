/**
 * On-chain Transaction Analysis Module
 * 
 * Queries blockchain explorers for wallet transaction history
 * and derives trust signals from on-chain behavior.
 * 
 * Signals:
 * - Transaction count and frequency
 * - Unique counterparties (diversity)
 * - Total volume (logarithmic weighting)
 * - Contract interactions (capability signal)
 * - Recency weighting (exponential decay)
 * 
 * Supports: Base Sepolia (testnet), Base Mainnet, Ethereum Mainnet
 */

const https = require('https');

class OnchainAnalyzer {
  constructor(opts = {}) {
    // Base Sepolia explorer API (free, no key needed for basic queries)
    this.explorers = {
      'base-sepolia': {
        url: 'https://api-sepolia.basescan.org/api',
        key: opts.basescanKey || '',
      },
      'base': {
        url: 'https://api.basescan.org/api',
        key: opts.basescanKey || '',
      },
      'ethereum': {
        url: 'https://api.etherscan.io/api',
        key: opts.etherscanKey || '',
      }
    };

    // USDC contract addresses
    this.usdc = {
      'base-sepolia': '0x036CbD53842c5426634e7929541eC2318f3dCF7e',
      'base': '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
      'ethereum': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    };
  }

  /**
   * Fetch and analyze on-chain history for a wallet
   * @param {string} address - Wallet address
   * @param {string} chain - 'base-sepolia' | 'base' | 'ethereum'
   * @returns {Object} - On-chain trust signals
   */
  async analyze(address, chain = 'base-sepolia') {
    if (!address || !address.match(/^0x[a-fA-F0-9]{40}$/)) {
      return this._emptyResult('Invalid address');
    }

    const explorer = this.explorers[chain];
    if (!explorer) {
      return this._emptyResult(`Unsupported chain: ${chain}`);
    }

    try {
      // Fetch normal transactions + token transfers in parallel
      const [txs, tokenTxs, balance] = await Promise.all([
        this._fetchTxList(address, explorer),
        this._fetchTokenTxs(address, explorer, this.usdc[chain]),
        this._fetchBalance(address, explorer),
      ]);

      return this._score(address, txs, tokenTxs, balance, chain);
    } catch (err) {
      return this._emptyResult(`Fetch error: ${err.message}`);
    }
  }

  _score(address, txs, tokenTxs, balance, chain) {
    const addrLower = address.toLowerCase();
    const now = Date.now() / 1000;

    // --- Normal transactions ---
    const txCount = txs.length;
    const uniqueCounterparties = new Set();
    let contractInteractions = 0;
    let totalValueWei = 0;
    const txTimestamps = [];

    for (const tx of txs) {
      const other = tx.from.toLowerCase() === addrLower ? tx.to : tx.from;
      if (other) uniqueCounterparties.add(other.toLowerCase());
      if (tx.input && tx.input !== '0x') contractInteractions++;
      totalValueWei += parseFloat(tx.value || 0);
      txTimestamps.push(parseInt(tx.timeStamp));
    }

    // --- USDC token transfers ---
    const usdcTxCount = tokenTxs.length;
    let usdcVolume = 0;
    let usdcSent = 0;
    let usdcReceived = 0;
    const usdcCounterparties = new Set();

    for (const tx of tokenTxs) {
      const value = parseFloat(tx.value || 0) / 1e6; // USDC has 6 decimals
      usdcVolume += value;
      const other = tx.from.toLowerCase() === addrLower ? tx.to : tx.from;
      if (other) usdcCounterparties.add(other.toLowerCase());
      if (tx.from.toLowerCase() === addrLower) usdcSent += value;
      else usdcReceived += value;
    }

    // --- Recency ---
    let lastActivityDays = null;
    if (txTimestamps.length > 0) {
      const latest = Math.max(...txTimestamps);
      lastActivityDays = Math.round((now - latest) / 86400);
    }

    // --- Scoring ---
    // Transaction frequency score (log scale)
    const txFreqScore = Math.min(100, Math.round(Math.log10(txCount + 1) * 50));

    // Counterparty diversity score
    const diversityScore = Math.min(100, Math.round(
      Math.log10(uniqueCounterparties.size + 1) * 60
    ));

    // Volume score (log scale, weighted)
    // 50 small txs > 2 large ones (per research)
    const volumeScore = Math.min(100, Math.round(
      Math.log10(usdcVolume + 1) * 30 +
      Math.log10(usdcTxCount + 1) * 20
    ));

    // Contract interaction score (capability signal)
    const contractScore = Math.min(100, Math.round(
      contractInteractions > 0
        ? Math.log10(contractInteractions + 1) * 60
        : 0
    ));

    // Recency score (exponential decay, lambda=0.02, ~35 day half-life)
    const recencyScore = lastActivityDays !== null
      ? Math.round(Math.exp(-0.02 * lastActivityDays) * 100)
      : 0;

    // Composite on-chain score
    const composite = Math.round(
      txFreqScore * 0.25 +
      diversityScore * 0.20 +
      volumeScore * 0.25 +
      contractScore * 0.15 +
      recencyScore * 0.15
    );

    return {
      score: composite,
      address,
      chain,
      details: {
        txCount,
        uniqueCounterparties: uniqueCounterparties.size,
        contractInteractions,
        totalValueETH: Math.round(totalValueWei / 1e18 * 10000) / 10000,
        usdcTxCount,
        usdcVolume: Math.round(usdcVolume * 100) / 100,
        usdcSent: Math.round(usdcSent * 100) / 100,
        usdcReceived: Math.round(usdcReceived * 100) / 100,
        usdcCounterparties: usdcCounterparties.size,
        lastActivityDays,
        balanceWei: balance,
      },
      subscores: {
        txFrequency: txFreqScore,
        diversity: diversityScore,
        volume: volumeScore,
        contractActivity: contractScore,
        recency: recencyScore,
      },
      hasActivity: txCount > 0,
    };
  }

  _emptyResult(reason) {
    return {
      score: 0,
      address: null,
      chain: null,
      details: {},
      subscores: {},
      hasActivity: false,
      error: reason,
    };
  }

  // --- API helpers ---

  _fetch(url) {
    return new Promise((resolve, reject) => {
      const req = https.get(url, { timeout: 10000 }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error('JSON parse error'));
          }
        });
      });
      req.on('error', reject);
      req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
    });
  }

  async _fetchTxList(address, explorer) {
    const url = `${explorer.url}?module=account&action=txlist&address=${address}&startblock=0&endblock=99999999&sort=desc&apikey=${explorer.key}`;
    const data = await this._fetch(url);
    if (data.status === '1' && Array.isArray(data.result)) {
      return data.result.slice(0, 200); // Cap at 200
    }
    return [];
  }

  async _fetchTokenTxs(address, explorer, tokenAddress) {
    if (!tokenAddress) return [];
    const url = `${explorer.url}?module=account&action=tokentx&address=${address}&contractaddress=${tokenAddress}&startblock=0&endblock=99999999&sort=desc&apikey=${explorer.key}`;
    const data = await this._fetch(url);
    if (data.status === '1' && Array.isArray(data.result)) {
      return data.result.slice(0, 200);
    }
    return [];
  }

  async _fetchBalance(address, explorer) {
    const url = `${explorer.url}?module=account&action=balance&address=${address}&apikey=${explorer.key}`;
    const data = await this._fetch(url);
    return data.result || '0';
  }
}

module.exports = { OnchainAnalyzer };
