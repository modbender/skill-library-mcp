/**
 * Network Switcher
 * Toggle between BNB Testnet and Mainnet
 * Handles RPC endpoints, contract addresses, gas prices
 */

const fs = require('fs');

const NETWORKS = {
  testnet: {
    chainId: 97,
    name: 'BNB Testnet',
    rpc: 'https://bsc-testnet.publicnode.com',
    scanner: 'https://testnet.bscscan.com',
    nativeToken: 'tBNB',
    contracts: {
      vault_eth_staking_001: '0x588eD88A145144F1E368D624EeFC336577a4276b',
      vault_high_risk_001: '0x6E05a63550200e20c9C4F112E337913c32FEBdf0',
      vault_link_oracle_001: '0x0C035842471340599966AA5A3573AC7dB34D14E4',
    },
    gasSettings: {
      minGasPrice: '1000000000', // 1 gwei
      maxGasPrice: '10000000000', // 10 gwei
      gasMultiplier: 1.2,
    },
    tokenPrices: {
      BNB: 600, // USD
      LINK: 28,
      ETH: 3500,
      '1INCH': 1.5,
    },
    harvestThreshold: 25, // USD
  },
  
  mainnet: {
    chainId: 56,
    name: 'BNB Mainnet',
    rpc: 'https://bsc-dataseed1.defibit.io',
    scanner: 'https://bscscan.com',
    nativeToken: 'BNB',
    contracts: {
      // Would be real mainnet contract addresses
      vault_eth_staking_001: '0xMAINNET_ADDRESS_1',
      vault_high_risk_001: '0xMAINNET_ADDRESS_2',
      vault_link_oracle_001: '0xMAINNET_ADDRESS_3',
    },
    gasSettings: {
      minGasPrice: '1000000000', // 1 gwei
      maxGasPrice: '50000000000', // 50 gwei
      gasMultiplier: 1.5, // More conservative on mainnet
    },
    tokenPrices: {
      BNB: 600,
      LINK: 28,
      ETH: 3500,
      '1INCH': 1.5,
    },
    harvestThreshold: 100, // USD (higher threshold on mainnet)
  },
};

class NetworkSwitcher {
  constructor(initialNetwork = 'testnet') {
    this.currentNetwork = initialNetwork;
    this.config = NETWORKS[initialNetwork];
    this.configFile = '.network.json';
    this.loadSavedNetwork();
  }

  loadSavedNetwork() {
    if (fs.existsSync(this.configFile)) {
      try {
        const saved = JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
        if (NETWORKS[saved.network]) {
          this.currentNetwork = saved.network;
          this.config = NETWORKS[this.currentNetwork];
          console.log(`✓ Loaded network from config: ${this.currentNetwork}`);
        }
      } catch (error) {
        console.warn('Could not load saved network:', error.message);
      }
    }
  }

  switchNetwork(networkName) {
    if (!NETWORKS[networkName]) {
      throw new Error(`Unknown network: ${networkName}. Available: ${Object.keys(NETWORKS).join(', ')}`);
    }

    const oldNetwork = this.currentNetwork;
    this.currentNetwork = networkName;
    this.config = NETWORKS[networkName];

    // Save preference
    fs.writeFileSync(this.configFile, JSON.stringify({
      network: networkName,
      timestamp: new Date().toISOString(),
      previousNetwork: oldNetwork,
    }, null, 2));

    console.log(`\n🔄 Network Switch: ${oldNetwork} → ${networkName}`);
    console.log(`  RPC: ${this.config.rpc}`);
    console.log(`  Scanner: ${this.config.scanner}`);
    console.log(`  Chain ID: ${this.config.chainId}`);

    return this.getNetworkInfo();
  }

  getNetworkInfo() {
    return {
      name: this.currentNetwork,
      ...this.config,
    };
  }

  getContractAddress(vaultId) {
    const address = this.config.contracts[vaultId];
    if (!address) {
      throw new Error(`Unknown vault: ${vaultId}`);
    }
    return address;
  }

  getAllContractAddresses() {
    return this.config.contracts;
  }

  getTxLink(txHash) {
    return `${this.config.scanner}/tx/${this.config.scanner}${txHash}`;
  }

  getAddressLink(address) {
    return `${this.config.scanner}/address/${address}`;
  }

  getTokenPrice(symbol) {
    return this.config.tokenPrices[symbol] || 0;
  }

  estimateGasCost(gasLimit) {
    const gasPriceGwei = 2; // Reasonable estimate
    const gasPrice = gasPriceGwei * 1e9; // Convert to wei
    const cost = (gasLimit * gasPrice) / 1e18; // Cost in BNB
    const costUSD = cost * this.config.tokenPrices.BNB;
    return { bnb: cost, usd: costUSD };
  }

  getHarvestThreshold() {
    return this.config.harvestThreshold;
  }

  isMainnet() {
    return this.currentNetwork === 'mainnet';
  }

  isTestnet() {
    return this.currentNetwork === 'testnet';
  }

  printNetworkStatus() {
    console.log(`
╔════════════════════════════════════════════════════════╗
║         Network Configuration Status                    ║
╠════════════════════════════════════════════════════════╣
║ Network:        ${this.config.name.padEnd(42)}║
║ Chain ID:       ${this.config.chainId.toString().padEnd(42)}║
║ RPC:            ${this.config.rpc.slice(0, 40).padEnd(42)}║
║ Scanner:        ${this.config.scanner.slice(0, 40).padEnd(42)}║
║ Native Token:   ${this.config.nativeToken.padEnd(42)}║
║ Harvest Min:    $${this.config.harvestThreshold.toString().padEnd(40)}║
║ Gas Multiplier: ${this.config.gasSettings.gasMultiplier.toString().padEnd(42)}║
╚════════════════════════════════════════════════════════╝
    `);
  }
}

module.exports = NetworkSwitcher;
