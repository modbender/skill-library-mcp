/**
 * List NFT Skill
 * Handles listing NFTs on the marketplace
 */
import { ethers } from 'ethers';
import * as fs from 'fs';

function getPrivateKey(): string {
  if (process.env.PRIVATE_KEY_FILE) {
    return fs.readFileSync(process.env.PRIVATE_KEY_FILE, 'utf8').trim();
  }
  return process.env.BASE_PRIVATE_KEY!;
}

const MARKETPLACE_ABI = [
  'function listItem(address nftAddress, uint256 tokenId, uint256 price) external',
  'function getListing(address nftAddress, uint256 tokenId) external view returns (tuple(address seller, uint256 price, bool active))'
];

const NFT_ABI = [
  'function approve(address to, uint256 tokenId) external',
  'function setApprovalForAll(address operator, bool approved) external',
  'function isApprovedForAll(address owner, address operator) external view returns (bool)',
  'function ownerOf(uint256 tokenId) external view returns (address)'
];

interface ListResult {
  success: boolean;
  price: string;
  txHash?: string;
  error?: string;
}

export async function listNFT(tokenId: string, priceInEth: string): Promise<ListResult> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  const wallet = new ethers.Wallet(getPrivateKey(), provider);

  const nftContract = new ethers.Contract(
    process.env.NFT_CONTRACT_ADDRESS!,
    NFT_ABI,
    wallet
  );

  const marketplaceContract = new ethers.Contract(
    process.env.MARKETPLACE_ADDRESS!,
    MARKETPLACE_ABI,
    wallet
  );

  const priceWei = ethers.parseEther(priceInEth);

  console.log(`[List] Listing Token #${tokenId} for ${priceInEth} ETH`);

  try {
    // Check ownership
    const owner = await nftContract.ownerOf(tokenId);
    if (owner.toLowerCase() !== wallet.address.toLowerCase()) {
      return { success: false, price: priceInEth, error: 'Not the owner' };
    }

    // Check if marketplace is approved
    const isApproved = await nftContract.isApprovedForAll(wallet.address, process.env.MARKETPLACE_ADDRESS!);
    
    if (!isApproved) {
      console.log('[List] Approving marketplace...');
      const approveTx = await nftContract.setApprovalForAll(process.env.MARKETPLACE_ADDRESS!, true);
      await approveTx.wait();
      console.log('[List] Marketplace approved');
    }

    // List the item
    const listTx = await marketplaceContract.listItem(
      process.env.NFT_CONTRACT_ADDRESS!,
      tokenId,
      priceWei
    );

    console.log(`[List] Listing transaction: ${listTx.hash}`);
    const receipt = await listTx.wait();

    console.log(`[List] ✅ Listed successfully in block ${receipt.blockNumber}`);

    return {
      success: true,
      price: priceInEth,
      txHash: listTx.hash
    };

  } catch (error: any) {
    console.error('[List] Error listing NFT:', error.message);
    return { success: false, price: priceInEth, error: error.message };
  }
}

export async function checkListing(tokenId: string): Promise<{ listed: boolean; price: string; seller: string }> {
  const provider = new ethers.JsonRpcProvider(process.env.BASE_RPC_URL);
  
  const marketplaceContract = new ethers.Contract(
    process.env.MARKETPLACE_ADDRESS!,
    MARKETPLACE_ABI,
    provider
  );

  try {
    const listing = await marketplaceContract.getListing(
      process.env.NFT_CONTRACT_ADDRESS!,
      tokenId
    );

    return {
      listed: listing.active,
      price: listing.active ? ethers.formatEther(listing.price) : '0',
      seller: listing.seller
    };
  } catch (error) {
    return { listed: false, price: '0', seller: '' };
  }
}
