#!/usr/bin/env node

const fs = require('fs').promises;

/**
 * Best practices database
 */
const BEST_PRACTICES = {
  wallet: {
    'seed phrase': {
      name: 'Seed Phrase',
      category: 'wallet',
      description: 'Store your 12-24 word seed phrase securely offline. Never share it digitally or store in cloud services. Use a hardware wallet for maximum security.',
      tips: ['Write on paper', 'Use metal backup', 'Store in multiple secure locations']
    },
    'account recovery': {
      name: 'Account Recovery',
      category: 'wallet',
      description: 'Set up account recovery methods including email and phone. Consider multi-signature recovery for high-value accounts.',
      tips: ['Enable 2FA', 'Set trusted contacts', 'Keep contact info updated']
    },
    'hardware wallet': {
      name: 'Hardware Wallet',
      category: 'wallet',
      description: 'Use hardware wallets (Ledger, Trezor) for storing significant amounts. Hardware wallets keep private keys offline and require physical confirmation for transactions.',
      tips: ['Verify device authenticity', 'Keep firmware updated', 'Use direct connection only']
    },
    'multi-sig': {
      name: 'Multi-Signature Wallet',
      category: 'wallet',
      description: 'Multi-sig requires multiple signatures to approve transactions. Provides additional security for teams, DAOs, and high-value accounts.',
      tips: ['Choose appropriate threshold', 'Distribute signers', 'Test with small amounts first']
    }
  },
  contracts: {
    'nep-171': {
      name: 'NEP-171 (NFT Standard)',
      category: 'contracts',
      description: 'Standard interface for Non-Fungible Tokens on NEAR. Implement for compatibility with marketplaces and wallets.',
      tips: ['Follow spec exactly', 'Include metadata', 'Handle royalties']
    },
    'nep-141': {
      name: 'NEP-141 (Fungible Token Standard)',
      category: 'contracts',
      description: 'Standard interface for fungible tokens. Similar to ERC-20 but optimized for NEAR.',
      tips: ['Implement proper metadata', 'Handle decimals correctly', 'Include pause functionality']
    },
    'access control': {
      name: 'Access Control',
      category: 'contracts',
      description: 'Implement proper access control patterns using own_only, owner_id, or role-based permissions. Never grant unlimited access.',
      tips: ['Use own_only for user data', 'Implement role-based access', 'Audit permissions']
    },
    'upgradeable contracts': {
      name: 'Upgradeable Contracts',
      category: 'contracts',
      description: 'Design contracts with upgradeability in mind. Use versioning and migration strategies. Consider upgrade delay periods.',
      tips: ['Version your contracts', 'Plan migrations', 'Notify users ahead of upgrades']
    },
    'gas optimization': {
      name: 'Gas Optimization',
      category: 'contracts',
      description: 'Minimize gas usage by avoiding unnecessary storage operations, batching calls, and optimizing data structures. Gas fees are paid in NEAR.',
      tips: ['Batch operations', 'Cache frequently accessed data', 'Use efficient data structures']
    }
  },
  defi: {
    'slippage': {
      name: 'Slippage Protection',
      category: 'defi',
      description: 'Set appropriate slippage tolerance to protect against price movement during transaction execution. Higher slippage = faster fills, more potential loss.',
      tips: ['Use 0.5-1% for stable pairs', 'Use 1-3% for volatile pairs', 'Consider market conditions']
    },
    'impermanent loss': {
      name: 'Impermanent Loss',
      category: 'defi',
      description: 'Temporary loss experienced when providing liquidity. Occurs when the price of deposited assets diverges. Can become permanent if not managed.',
      tips: ['Understand before providing liquidity', 'Diversify pools', 'Monitor regularly']
    },
    'liquidity provision': {
      name: 'Liquidity Provision',
      category: 'defi',
      description: 'Providing liquidity to DEX pools earns fees but carries risks. Start with small amounts and understand the pool dynamics.',
      tips: ['Start small', 'Research pool statistics', 'Consider impermanent loss']
    },
    'audits': {
      name: 'Smart Contract Audits',
      category: 'defi',
      description: 'Always verify that DeFi protocols have been audited by reputable firms. Audit reports should be publicly available and recent.',
      tips: ['Check audit dates', 'Verify auditor reputation', 'Review audit findings']
    }
  },
  keys: {
    'access keys': {
      name: 'Access Keys',
      category: 'keys',
      description: 'NEAR uses access keys instead of private keys for signing transactions. Limited to specific contracts or full access. Rotate keys regularly.',
      tips: ['Use function call keys when possible', 'Rotate keys periodically', 'Revoke unused keys']
    },
    'full access key': {
      name: 'Full Access Key',
      category: 'keys',
      description: 'A key with unlimited access to the account. Keep these secure and use only from trusted devices. Consider using hardware wallet for full access.',
      tips: ['Store offline', 'Use hardware wallet', 'Limit number of full access keys']
    },
    'key rotation': {
      name: 'Key Rotation',
      category: 'keys',
      description: 'Regularly rotate your access keys as a security practice. Remove old keys and add new ones with proper permissions.',
      tips: ['Rotate every 3-6 months', 'Remove unused keys', 'Use different keys for different purposes']
    }
  },
  gas: {
    'gas calculation': {
      name: 'Gas Calculation',
      category: 'gas',
      description: 'Gas = gas_price * gas_used. Monitor gas costs before transactions. Gas is paid in yoctoNEAR (1e-24 NEAR).',
      tips: ['Estimate before transactions', 'Check gas prices', 'Use batch operations']
    },
    'gas units': {
      name: 'Gas Units',
      category: 'gas',
      description: 'Gas is measured in units. Different operations consume different amounts. Storage operations are expensive, calculations are cheap.',
      tips: ['Minimize storage writes', 'Batch view calls', 'Cache results when possible']
    }
  },
  testing: {
    'unit testing': {
      name: 'Unit Testing',
      category: 'testing',
      description: 'Test individual functions in isolation. Use near-sdk-sim for local testing without blockchain. Aim for high coverage.',
      tips: ['Test edge cases', 'Mock external dependencies', 'Test error conditions']
    },
    'integration testing': {
      name: 'Integration Testing',
      category: 'testing',
      description: 'Test contract interactions on testnet before deploying to mainnet. Testnet is free and mirrors mainnet functionality.',
      tips: ['Test on testnet first', 'Use realistic scenarios', 'Test failure modes']
    },
    'testnet': {
      name: 'NEAR Testnet',
      category: 'testing',
      description: 'Free testing environment identical to mainnet. Get testnet tokens from faucets. Reset or redeploy contracts freely.',
      tips: ['Get tokens from faucet', 'Test thoroughly', 'Use testnet for experiments']
    }
  }
};

/**
 * Flatten all terms for search
 */
function getAllTerms() {
  const terms = [];
  for (const category of Object.keys(BEST_PRACTICES)) {
    for (const key of Object.keys(BEST_PRACTICES[category])) {
      terms.push({ ...BEST_PRACTICES[category][key], key });
    }
  }
  return terms;
}

/**
 * Browse by category
 */
function browseCategory(category) {
  if (category) {
    const cat = BEST_PRACTICES[category];
    if (!cat) {
      console.log(`Category "${category}" not found`);
      console.log('Available categories:', Object.keys(BEST_PRACTICES).join(', '));
      return;
    }
    console.log(`${category.toUpperCase()}:`);
    console.log('');
    for (const [key, item] of Object.entries(cat)) {
      console.log(`  ${item.name} (${key})`);
      console.log(`  ${item.description.substring(0, 80)}...`);
      console.log('');
    }
  } else {
    console.log('Available Categories:');
    console.log('');
    for (const [cat, items] of Object.entries(BEST_PRACTICES)) {
      console.log(`  ${cat} (${Object.keys(items).length} terms)`);
    }
  }
}

/**
 * Search for term
 */
function searchTerm(query) {
  const terms = getAllTerms();
  const lowerQuery = query.toLowerCase();
  const results = terms.filter(t =>
    t.name.toLowerCase().includes(lowerQuery) ||
    t.key.includes(lowerQuery) ||
    t.description.toLowerCase().includes(lowerQuery)
  );

  if (results.length === 0) {
    console.log(`No results found for "${query}"`);
    return;
  }

  console.log(`Results for "${query}":`);
  console.log('');
  results.forEach(r => {
    console.log(`  ${r.name} (${r.key}) [${r.category}]`);
  });
}

/**
 * Get term details
 */
function getTerm(key) {
  for (const category of Object.values(BEST_PRACTICES)) {
    if (category[key]) {
      const term = category[key];
      console.log(`${term.name}`);
      console.log(`Category: ${term.category}`);
      console.log(`\n${term.description}`);
      if (term.tips && term.tips.length > 0) {
        console.log(`\nTips:`);
        term.tips.forEach(tip => console.log(`  • ${tip}`));
      }
      return;
    }
  }
  console.log(`Term "${key}" not found`);
}

/**
 * List all terms
 */
function listTerms() {
  const terms = getAllTerms();
  console.log(`All Terms (${terms.length}):`);
  console.log('');
  terms.forEach(t => {
    console.log(`  ${t.name} (${t.key}) [${t.category}]`);
  });
}

/**
 * Random tip
 */
function randomTip() {
  const terms = getAllTerms();
  const random = terms[Math.floor(Math.random() * terms.length)];
  console.log(`💡 Random Tip: ${random.name}`);
  console.log(`\n${random.description}`);
  if (random.tips && random.tips.length > 0) {
    console.log(`\nTip: ${random.tips[0]}`);
  }
}

// CLI interface
const command = process.argv[2];
const arg = process.argv[3];

function main() {
  try {
    switch (command) {
      case 'browse':
        browseCategory(arg);
        break;

      case 'search':
        if (!arg) {
          console.error('Error: Search term required');
          console.error('Usage: near-best search <term>');
          process.exit(1);
        }
        searchTerm(arg);
        break;

      case 'get':
        if (!arg) {
          console.error('Error: Term key required');
          console.error('Usage: near-best get <term>');
          process.exit(1);
        }
        getTerm(arg);
        break;

      case 'list':
        listTerms();
        break;

      case 'random':
        randomTip();
        break;

      default:
        console.log('NEAR Best Practices Guide');
        console.log('');
        console.log('Commands:');
        console.log('  browse [category]    Browse best practices by category');
        console.log('  search <term>       Search for a term');
        console.log('  get <term>          Get detailed explanation');
        console.log('  list                List all terms');
        console.log('  random              Get a random tip');
        console.log('');
        console.log(`Total terms: ${getAllTerms().length}`);
    }
  } catch (error) {
    console.error(`Error: ${error.message}`);
    process.exit(1);
  }
}

main();
