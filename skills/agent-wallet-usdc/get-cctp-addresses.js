import { BridgeKit } from "@circle-fin/bridge-kit";

const kit = new BridgeKit();

kit.getSupportedChains().then(chains => {
  for (const chain of chains) {
    if (chain.chain === 'Base_Sepolia' || chain.chain === 'Ethereum_Sepolia') {
      console.log(`\n${chain.chain}:`);
      console.log('  USDC:', chain.usdcAddress);
      console.log('  CCTP:', JSON.stringify(chain.cctp, null, 4));
      console.log('  Kit:', JSON.stringify(chain.kitContracts, null, 4));
    }
  }
});
