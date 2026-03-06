///////////////////////////////////////////////////////////////////////////////
// ABIs for Circle Gateway contracts
// Only includes functions needed for deposit, balance check, and mint operations.
// Full ABI reference: https://developers.circle.com/gateway/references/contract-interfaces-and-events

export const gatewayWalletAbi = [
  {
    type: "function",
    name: "deposit",
    inputs: [
      { name: "token", type: "address", internalType: "address" },
      { name: "value", type: "uint256", internalType: "uint256" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
];

export const gatewayMinterAbi = [
  {
    type: "function",
    name: "gatewayMint",
    inputs: [
      { name: "attestationPayload", type: "bytes", internalType: "bytes" },
      { name: "signature", type: "bytes", internalType: "bytes" },
    ],
    outputs: [],
    stateMutability: "nonpayable",
  },
];
