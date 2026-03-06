/**
 * Zeta Markets Funding Rate Aggregator
 * Uses @zetamarkets/sdk to read on-chain data
 */

import { Connection, PublicKey } from '@solana/web3.js';
import { Exchange, Network, utils, assets, constants } from '@zetamarkets/sdk';

const RPC_URL = process.env.SOLANA_RPC_URL || 'https://api.mainnet-beta.solana.com';

interface ZetaFundingRate {
  symbol: string;
  fundingRate: number;
  fundingRateApy: number;
  markPrice: number;
  indexPrice: number;
}

async function getZetaFundingRates(): Promise<ZetaFundingRate[]> {
  console.log('Connecting to Solana mainnet...');
  
  const connection = new Connection(RPC_URL, 'confirmed');
  
  console.log('Loading Zeta Exchange...');
  
  // Load exchange without wallet (read-only)
  await Exchange.load(
    [],  // no assets filter, load all
    undefined,  // no throttle
    connection,
    Network.MAINNET,
    undefined,  // wallet (not needed for reading)
    undefined,  // commitment
    undefined,  // callback
    undefined,  // throttle
  );
  
  console.log('Exchange loaded. Fetching funding rates...');
  
  const rates: ZetaFundingRate[] = [];
  
  // Get all available assets
  const allAssets = [
    constants.Asset.SOL,
    constants.Asset.BTC,
    constants.Asset.ETH,
    constants.Asset.APT,
    constants.Asset.ARB,
    constants.Asset.BNB,
    constants.Asset.JTO,
    constants.Asset.ONEMBONK,
    constants.Asset.PYTH,
    constants.Asset.TIA,
    constants.Asset.JUP,
    constants.Asset.DYM,
    constants.Asset.STRK,
    constants.Asset.WIF,
    constants.Asset.RNDR,
    constants.Asset.TNSR,
    constants.Asset.W,
  ];
  
  for (const asset of allAssets) {
    try {
      const assetName = assets.assetToName(asset);
      
      // Get pricing info
      const pricing = Exchange.getPricing(asset);
      if (!pricing) continue;
      
      // Funding rate from the Pricing account
      // Zeta uses 1-hour funding intervals
      const fundingRate = pricing.fundingRate || 0;
      const markPrice = pricing.markPrice || 0;
      const indexPrice = Exchange.getOraclePrice(asset) || 0;
      
      // Convert to APY (hourly rate * 24 * 365 * 100)
      const fundingRateApy = fundingRate * 24 * 365 * 100;
      
      rates.push({
        symbol: assetName,
        fundingRate,
        fundingRateApy,
        markPrice,
        indexPrice,
      });
      
      console.log(`${assetName}: Funding=${(fundingRate * 100).toFixed(4)}%, APY=${fundingRateApy.toFixed(2)}%`);
    } catch (e) {
      // Skip failed assets
    }
  }
  
  return rates;
}

// Main
async function main() {
  console.log('═'.repeat(60));
  console.log('⚡ ZETA MARKETS FUNDING RATE SCANNER');
  console.log('═'.repeat(60));
  
  try {
    const rates = await getZetaFundingRates();
    
    console.log('\n📊 SUMMARY:');
    console.log(`Loaded ${rates.length} markets`);
    
    // Sort by absolute APY
    rates.sort((a, b) => Math.abs(b.fundingRateApy) - Math.abs(a.fundingRateApy));
    
    console.log('\n🎯 TOP FUNDING OPPORTUNITIES:');
    for (const r of rates.slice(0, 10)) {
      const direction = r.fundingRateApy > 0 ? '🔴 Short pays Long' : '🟢 Long pays Short';
      console.log(`  ${r.symbol}: ${r.fundingRateApy.toFixed(2)}% APY ${direction}`);
    }
    
  } catch (error) {
    console.error('Error:', error);
  }
  
  process.exit(0);
}

main();
