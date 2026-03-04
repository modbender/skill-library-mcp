import { ethers } from 'hardhat';
import * as fs from 'fs';
import * as path from 'path';

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log(`Deploying contracts with account: ${deployer.address}`);
  console.log(`Balance: ${ethers.formatEther(await deployer.provider.getBalance(deployer.address))} ETH`);

  // Deploy NFTArt
  console.log('\nDeploying NFTArt...');
  const NFTArt = await ethers.getContractFactory('NFTArt');
  const nftArt = await NFTArt.deploy(deployer.address);
  await nftArt.waitForDeployment();
  const nftAddress = await nftArt.getAddress();
  console.log(`NFTArt deployed to: ${nftAddress}`);

  // Deploy NFTMarketplace
  console.log('\nDeploying NFTMarketplace...');
  const NFTMarketplace = await ethers.getContractFactory('NFTMarketplace');
  const marketplace = await NFTMarketplace.deploy();
  await marketplace.waitForDeployment();
  const marketplaceAddress = await marketplace.getAddress();
  console.log(`NFTMarketplace deployed to: ${marketplaceAddress}`);

  // Write addresses to .env (append/update)
  const envPath = path.join(__dirname, '../.env');
  let envContent = fs.existsSync(envPath) ? fs.readFileSync(envPath, 'utf8') : '';

  const updates: Record<string, string> = {
    NFT_CONTRACT_ADDRESS: nftAddress,
    MARKETPLACE_ADDRESS: marketplaceAddress
  };

  for (const [key, value] of Object.entries(updates)) {
    const regex = new RegExp(`^${key}=.*$`, 'm');
    if (regex.test(envContent)) {
      envContent = envContent.replace(regex, `${key}=${value}`);
    } else {
      envContent += `\n${key}=${value}`;
    }
  }

  fs.writeFileSync(envPath, envContent.trim() + '\n');
  console.log('\n.env updated with contract addresses.');

  console.log('\n=== Deployment Summary ===');
  console.log(`NFT_CONTRACT_ADDRESS=${nftAddress}`);
  console.log(`MARKETPLACE_ADDRESS=${marketplaceAddress}`);
  console.log('\nNext steps:');
  console.log('1. Verify contracts on Basescan (optional):');
  console.log(`   npx hardhat verify --network base-mainnet ${nftAddress} ${deployer.address}`);
  console.log(`   npx hardhat verify --network base-mainnet ${marketplaceAddress}`);
  console.log('2. Run the agent: npm run cli -- generate --generation 1 --theme "your theme"');
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
