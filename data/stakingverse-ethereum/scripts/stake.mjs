import { ethers } from 'ethers';
import https from 'https';

// Configuration
const PRIVATE_KEY = process.env.ETH_PRIVATE_KEY || 'YOUR_PRIVATE_KEY';
const MY_ADDRESS = process.env.MY_ADDRESS || 'YOUR_ADDRESS';
const STAKEWISE_VAULT = '0x8A93A876912c9F03F88Bc9114847cf5b63c89f56';
const KEEPER = '0x6B5815467da09DaA7DC83Db21c9239d98Bb487b5';
const RPC_URL = 'https://ethereum-rpc.publicnode.com';

// Subgraph query
const SUBGRAPH_URL = 'https://graphs.stakewise.io/mainnet-a/subgraphs/name/stakewise/prod';

const VAULT_ABI = [
  'function updateStateAndDeposit(address receiver, uint256 deadline, (bytes32 rewardsRoot, uint256 reward, uint256 unlockedMevReward, bytes32[] proof) harvestParams) external payable returns (uint256)',
  'function balanceOf(address account) external view returns (uint256)',
  'function convertToAssets(uint256 shares) external view returns (uint256)',
  'function isStateUpdateRequired() external view returns (bool)'
];

async function fetchHarvestParams(vaultAddress) {
  return new Promise((resolve, reject) => {
    const query = JSON.stringify({
      query: `
        query HarvestData($vault: String!) {
          vaultHarvestDatas(where: { vault: $vault }) {
            rewardsRoot
            reward
            unlockedMevReward
            proof
          }
        }
      `,
      variables: { vault: vaultAddress.toLowerCase() }
    });

    const options = {
      hostname: 'graphs.stakewise.io',
      path: '/mainnet-a/subgraphs/name/stakewise/prod',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': query.length
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const json = JSON.parse(data);
          resolve(json.data?.vaultHarvestDatas?.[0]);
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(query);
    req.end();
  });
}

async function stakeETH(amountETH) {
  console.log(`🎯 STAKING ${amountETH} ETH ON STAKEWISE`);
  console.log('=================================\n');
  
  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  const vault = new ethers.Contract(STAKEWISE_VAULT, VAULT_ABI, wallet);
  
  // Check if state update required
  const needsUpdate = await vault.isStateUpdateRequired();
  console.log('State update required:', needsUpdate);
  
  if (needsUpdate) {
    console.log('\nFetching harvest params from subgraph...');
    const harvestData = await fetchHarvestParams(STAKEWISE_VAULT);
    
    if (!harvestData) {
      throw new Error('No harvest data available');
    }
    
    console.log('Rewards root:', harvestData.rewardsRoot.slice(0, 20) + '...');
    console.log('Reward:', harvestData.reward);
    
    const harvestParams = {
      rewardsRoot: harvestData.rewardsRoot,
      reward: harvestData.reward,
      unlockedMevReward: harvestData.unlockedMevReward,
      proof: harvestData.proof
    };
    
    const amountWei = ethers.parseEther(amountETH.toString());
    const deadline = Math.floor(Date.now() / 1000) + 3600; // 1 hour
    
    console.log('\nCalling updateStateAndDeposit...');
    const tx = await vault.updateStateAndDeposit(
      MY_ADDRESS,
      deadline,
      harvestParams,
      { value: amountWei }
    );
    
    console.log('Transaction sent:', tx.hash);
    const receipt = await tx.wait();
    
    console.log('\n✅ Staked successfully!');
    console.log('Transaction:', receipt.hash);
    console.log('Block:', receipt.blockNumber);
    
    return receipt.hash;
  } else {
    // Simple deposit if no state update needed
    const amountWei = ethers.parseEther(amountETH.toString());
    console.log('\nNo state update needed, using simple deposit...');
    
    // Would need to implement simple deposit flow here
    // Most likely still need harvest params
    throw new Error('State update always required for StakeWise V3');
  }
}

// CLI usage
const args = process.argv.slice(2);
if (args.length < 1) {
  console.log('Usage: node stake.mjs <AMOUNT_ETH>');
  console.log('Example: node stake.mjs 0.1');
  process.exit(1);
}

stakeETH(args[0]).catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
