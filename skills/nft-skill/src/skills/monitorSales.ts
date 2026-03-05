/**
 * Sales Monitoring Skill
 * Watches for NFT sales on the marketplace
 */
import { ethers } from 'ethers';

const MARKETPLACE_ABI = [
  'event ItemSold(address indexed buyer, address indexed nftAddress, uint256 indexed tokenId, uint256 price)'
];

interface SaleEvent {
  buyer: string;
  tokenId: string;
  price: string;
  txHash: string;
  blockNumber: number;
}

type SaleCallback = (sale: SaleEvent) => void | Promise<void>;

/**
 * Start monitoring for sales of our NFTs
 * Returns a cleanup function to stop monitoring
 */
export function startSalesMonitor(onSale: SaleCallback): () => void {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const marketplaceContract = new ethers.Contract(
    process.env.MARKETPLACE_ADDRESS!,
    MARKETPLACE_ABI,
    provider
  );

  // Filter for sales of our NFT contract
  const filter = marketplaceContract.filters.ItemSold(
    null, // any buyer
    process.env.NFT_CONTRACT_ADDRESS! // our NFT contract
  );

  const listener = async (
    buyer: string,
    nftAddress: string,
    tokenId: bigint,
    price: bigint,
    event: any
  ) => {
    console.log('[Monitor] 🎉 SALE DETECTED!');
    console.log(`[Monitor] Token #${tokenId} sold for ${ethers.formatEther(price)} ETH`);
    console.log(`[Monitor] Buyer: ${buyer}`);
    console.log(`[Monitor] TX: ${event.transactionHash}`);

    try {
      await onSale({
        buyer,
        tokenId: tokenId.toString(),
        price: ethers.formatEther(price),
        txHash: event.transactionHash,
        blockNumber: event.blockNumber
      });
    } catch (error) {
      console.error('[Monitor] Error in sale callback:', error);
    }
  };

  marketplaceContract.on(filter, listener);
  console.log('[Monitor] Sales monitor started, watching for purchases...');

  // Return cleanup function
  return () => {
    marketplaceContract.off(filter, listener);
    console.log('[Monitor] Sales monitor stopped');
  };
}

/**
 * Check for any sales we might have missed (useful on restart)
 */
export async function checkRecentSales(
  fromBlock: number,
  onSale: SaleCallback
): Promise<number> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const marketplaceContract = new ethers.Contract(
    process.env.MARKETPLACE_ADDRESS!,
    MARKETPLACE_ABI,
    provider
  );

  const currentBlock = await provider.getBlockNumber();

  console.log(`[Monitor] Checking for sales from block ${fromBlock} to ${currentBlock}...`);

  const filter = marketplaceContract.filters.ItemSold(
    null,
    process.env.NFT_CONTRACT_ADDRESS!
  );

  const events = await marketplaceContract.queryFilter(filter, fromBlock, currentBlock);

  console.log(`[Monitor] Found ${events.length} sales since block ${fromBlock}`);

  for (const event of events) {
    if (!('args' in event)) continue;
    
    const [buyer, nftAddress, tokenId, price] = event.args;

    await onSale({
      buyer,
      tokenId: tokenId.toString(),
      price: ethers.formatEther(price),
      txHash: event.transactionHash,
      blockNumber: event.blockNumber
    });
  }

  return currentBlock;
}
