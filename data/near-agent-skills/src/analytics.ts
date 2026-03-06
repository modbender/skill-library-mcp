import fetch from 'node-fetch';

export async function near_analytics_network() {
  const res = await fetch('https://rpc.mainnet.near.org', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      jsonrpc: '2.0',
      id: 'analytics',
      method: 'status',
      params: []
    })
  });
  const data = await res.json();
  return {
    version: data.result.version,
    protocol_version: data.result.protocol_version,
    latest_block_height: data.result.sync_info.latest_block_height
  };
}

export async function near_analytics_whales() {
  try {
    const response = await fetch('https://api.nearblocks.io/v1/txns?limit=5&sort=amount&order=desc');
    const data: any = await response.json();
    return data.txns.map((tx: any) => ({
      account: tx.signer_id,
      amount: `${(Number(tx.amount || 0) / 1e24).toLocaleString()} NEAR`,
      type: "High Value Transfer",
      hash: tx.transaction_hash
    }));
  } catch (e) {
    return [{ error: "Whale data unavailable." }];
  }
}

export async function near_analytics_trending() {
  try {
    const response = await fetch('https://api.nearblocks.io/v1/contracts?limit=5&sort=txns&order=desc');
    const data: any = await response.json();
    return data.contracts.map((c: any) => ({
      contract: c.contract_id,
      transactions_24h: c.txns_24h,
      growth: c.txns_growth_24h ? `${c.txns_growth_24h}%` : "Stable"
    }));
  } catch (e) {
    return [{ error: "Trending data unavailable." }];
  }
}

export async function near_analytics_defi() {
  try {
    // Aggregated stats from multiple sources (simplified for real data)
    const response = await fetch('https://api.nearblocks.io/v1/stats');
    const data: any = await response.json();
    return {
      near_price_usd: data.stats[0].near_price,
      market_cap_usd: data.stats[0].market_cap,
      total_transactions: data.stats[0].total_txns,
      daily_active_accounts: data.stats[0].active_accounts_24h
    };
  } catch (e) {
    return { error: "DeFi/Network stats unavailable." };
  }
}

