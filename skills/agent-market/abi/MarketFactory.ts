export const MarketFactoryABI = [
  {
    "anonymous": false,
    "inputs": [
      { "indexed": true, "internalType": "uint256", "name": "marketId", "type": "uint256" },
      { "indexed": false, "internalType": "string", "name": "question", "type": "string" },
      { "indexed": true, "internalType": "address", "name": "marketAddress", "type": "address" },
      { "indexed": false, "internalType": "address", "name": "ammAddress", "type": "address" },
      { "indexed": false, "internalType": "address", "name": "oracle", "type": "address" },
      { "indexed": false, "internalType": "uint256", "name": "deadline", "type": "uint256" }
    ],
    "name": "MarketCreated",
    "type": "event"
  },
  {
    "inputs": [],
    "name": "CREATION_FEE",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "INITIAL_LIQUIDITY",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_BOND_AMOUNT",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "MAX_DISPUTE_WINDOW",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "name": "allMarkets",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "name": "ammForMarket",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "name": "oracleForMarket",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [
      { "internalType": "string", "name": "_question", "type": "string" },
      { "internalType": "address", "name": "_arbitrator", "type": "address" },
      { "internalType": "uint256", "name": "_deadline", "type": "uint256" }
    ],
    "name": "createMarket",
    "outputs": [
      { "internalType": "address", "name": "marketAddr", "type": "address" },
      { "internalType": "address", "name": "amm", "type": "address" },
      { "internalType": "address", "name": "oracleContract", "type": "address" }
    ],
    "stateMutability": "nonpayable",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "defaultBondAmount",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "defaultDisputeWindow",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "feeRecipient",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "getMarketCount",
    "outputs": [{ "internalType": "uint256", "name": "", "type": "uint256" }],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "inputs": [],
    "name": "usdc",
    "outputs": [{ "internalType": "address", "name": "", "type": "address" }],
    "stateMutability": "view",
    "type": "function"
  }
] as const;
