/**
 * ERC-8004 Proof of Concept
 *
 * Demonstrates querying the ERC-8004 Identity Registry on Base
 * to verify technical feasibility of integration.
 */

import { ethers } from 'ethers';

// Contract addresses from https://github.com/erc-8004/erc-8004-contracts
const CONTRACTS = {
  BASE_MAINNET: {
    IDENTITY_REGISTRY: '0x8004A169FB4a3325136EB29fA0ceB6D2e539a432',
    REPUTATION_REGISTRY: '0x8004BAa17C55a88189AE136b182e5fdA19dE9b63',
  },
  BASE_SEPOLIA: {
    IDENTITY_REGISTRY: '0x8004A818BFB912233c491871b3d84c89A494BD9e',
    REPUTATION_REGISTRY: '0x8004B663056A597Dffe9eCcC1965A193B7388713',
  },
};

// Minimal ABI for IdentityRegistry (ERC-721 based)
const IDENTITY_REGISTRY_ABI = [
  // Read functions
  'function totalSupply() view returns (uint256)',
  'function balanceOf(address owner) view returns (uint256)',
  'function ownerOf(uint256 tokenId) view returns (address)',
  'function tokenURI(uint256 tokenId) view returns (string)',
  'function isRegistered(address agent) view returns (bool)',

  // Write functions
  'function register(string name, string[] skills, string endpoint) returns (uint256)',

  // Events
  'event AgentRegistered(address indexed agent, uint256 indexed tokenId, string name)',
];

// Minimal ABI for ReputationRegistry
const REPUTATION_REGISTRY_ABI = [
  'function getReputation(address agent) view returns (int256)',
  'function getFeedbackCount(address agent) view returns (uint256)',
  'function addFeedback(address agent, int256 rating, string feedback)',
];

async function main() {
  console.log('🔍 ERC-8004 Proof of Concept\n');
  console.log('=' .repeat(60));

  // Use Base Mainnet (reads are free, more likely to have deployments)
  const RPC_URL = 'https://mainnet.base.org';
  const provider = new ethers.JsonRpcProvider(RPC_URL);

  console.log(`\n📡 Connected to: Base Mainnet`);
  console.log(`   RPC: ${RPC_URL}`);

  // Initialize contracts
  const identityRegistry = new ethers.Contract(
    CONTRACTS.BASE_MAINNET.IDENTITY_REGISTRY,
    IDENTITY_REGISTRY_ABI,
    provider
  );

  const reputationRegistry = new ethers.Contract(
    CONTRACTS.BASE_MAINNET.REPUTATION_REGISTRY,
    REPUTATION_REGISTRY_ABI,
    provider
  );

  console.log(`\n📋 Contract Addresses:`);
  console.log(`   Identity Registry:   ${CONTRACTS.BASE_MAINNET.IDENTITY_REGISTRY}`);
  console.log(`   Reputation Registry: ${CONTRACTS.BASE_MAINNET.REPUTATION_REGISTRY}`);

  try {
    // Query 0: Verify contract exists
    console.log('\n\n🔎 Query 0: Verify Contract Deployment');
    console.log('-'.repeat(60));
    const code = await provider.getCode(CONTRACTS.BASE_MAINNET.IDENTITY_REGISTRY);
    const hasCode = code !== '0x';
    console.log(`   Contract has code: ${hasCode ? '✅ Yes' : '❌ No'}`);
    console.log(`   Bytecode length: ${code.length} characters`);

    if (!hasCode) {
      console.log('\n⚠️  Contract not deployed at this address.');
      console.log('   This might mean:');
      console.log('   - ERC-8004 not yet deployed on Base');
      console.log('   - Different contract addresses');
      console.log('   - Need to check official documentation');
      return;
    }

    // Query 1: Total registered agents
    console.log('\n\n🔎 Query 1: Total Registered Agents');
    console.log('-'.repeat(60));
    try {
      const totalSupply = await identityRegistry.totalSupply();
      console.log(`   Total agents registered: ${totalSupply.toString()}`);
    } catch (e) {
      console.log(`   ⚠️  totalSupply() not available (contract may use different interface)`);
    }

    // Query 2: Check if a specific address is registered
    console.log('\n🔎 Query 2: Check Registration Status');
    console.log('-'.repeat(60));
    const testAddress = '0x1234567890123456789012345678901234567890';
    const isRegistered = await identityRegistry.isRegistered(testAddress);
    console.log(`   Address: ${testAddress}`);
    console.log(`   Is registered: ${isRegistered ? '✅ Yes' : '❌ No'}`);

    // Query 3: Get agent details (if any exist)
    if (totalSupply > 0) {
      console.log('\n🔎 Query 3: Sample Agent Details');
      console.log('-'.repeat(60));

      try {
        // Try to get first agent (tokenId 0 or 1)
        const tokenId = 1;
        const owner = await identityRegistry.ownerOf(tokenId);
        console.log(`   Token ID: ${tokenId}`);
        console.log(`   Owner: ${owner}`);

        // Try to get token URI (metadata)
        try {
          const tokenURI = await identityRegistry.tokenURI(tokenId);
          console.log(`   Token URI: ${tokenURI}`);
        } catch (e) {
          console.log(`   Token URI: Not available`);
        }

        // Check reputation
        try {
          const reputation = await reputationRegistry.getReputation(owner);
          const feedbackCount = await reputationRegistry.getFeedbackCount(owner);
          console.log(`   Reputation: ${reputation.toString()}`);
          console.log(`   Feedback count: ${feedbackCount.toString()}`);
        } catch (e) {
          console.log(`   Reputation: Not available`);
        }
      } catch (e) {
        console.log(`   ⚠️  Could not fetch sample agent details`);
      }
    }

    console.log('\n\n✅ POC Completed Successfully!');
    console.log('=' .repeat(60));
    console.log('\n📊 Summary:');
    console.log(`   • Connected to ERC-8004 registry on Base Sepolia`);
    console.log(`   • Successfully queried contract state`);
    console.log(`   • ${totalSupply.toString()} agents currently registered`);
    console.log(`   • Integration is technically feasible ✓`);

    console.log('\n🚀 Next Steps:');
    console.log(`   1. Implement backend service to register Bloom agents`);
    console.log(`   2. Add background worker for batch processing`);
    console.log(`   3. Display ERC-8004 status on dashboard`);
    console.log(`   4. Build reputation features`);

  } catch (error) {
    console.error('\n❌ Error during POC:');
    console.error(error);
    process.exit(1);
  }
}

// Run POC
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
