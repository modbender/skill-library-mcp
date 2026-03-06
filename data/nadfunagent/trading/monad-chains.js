const monadMainnet = {
  id: 143,
  name: 'Monad Mainnet',
  network: 'monad',
  nativeCurrency: { name: 'MON', symbol: 'MON', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://monad-mainnet.drpc.org'] },
    public: { http: ['https://monad-mainnet.drpc.org'] }
  },
  blockExplorers: {
    default: { name: 'Monad Explorer', url: 'https://explorer.monad.xyz' }
  }
};

const monadTestnet = {
  id: 10143,
  name: 'Monad Testnet',
  network: 'monad-testnet',
  nativeCurrency: { name: 'MON', symbol: 'MON', decimals: 18 },
  rpcUrls: {
    default: { http: ['https://monad-testnet.drpc.org'] },
    public: { http: ['https://monad-testnet.drpc.org'] }
  },
  blockExplorers: {
    default: { name: 'Monad Testnet Explorer', url: 'https://testnet.monad.xyz' }
  }
};

module.exports = { monadMainnet, monadTestnet };
