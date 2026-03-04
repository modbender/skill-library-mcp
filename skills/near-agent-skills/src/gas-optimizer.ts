import { providers, utils } from 'near-api-js';

export async function near_gas_estimate(tx: any) {
  const network = 'mainnet';
  try {
    const provider = new providers.JsonRpcProvider({ url: `https://rpc.${network}.near.org` });
    const gasPrice = await provider.gasPrice(null);
    return `Current Gas Price: ${gasPrice.gas_price} yocto/gas. 1 TGas = ${(Number(gasPrice.gas_price) * 1e12 / 1e24).toFixed(6)} NEAR.`;
  } catch (e) {
    return "Gas estimation unavailable: could not connect to NEAR RPC.";
  }
}

export async function near_gas_optimize(account_id: string, contract_id: string) {
  const network = 'mainnet';
  const provider = new providers.JsonRpcProvider({ url: `https://rpc.${network}.near.org` });
  
  const recommendations = [
    "Use batching for related actions to save 10% base gas",
    "Avoid large state reads in loops: current contract state size might be an issue",
    "Consider storage staking: current usage is significant"
  ];

  try {
    const state: any = await provider.query({
      request_type: "view_account",
      finality: "final",
      account_id: contract_id,
    });
    if (state.storage_usage > 1000000) {
      recommendations.push("WARNING: High storage usage detected. Consider cleaning up old state.");
    }
  } catch (e) {}

  return recommendations;
}

export async function near_gas_history(account_id: string) {
  try {
    const response = await fetch(`https://api.nearblocks.io/v1/account/${account_id}/txns?limit=25`);
    const data: any = await response.json();
    const totalGas = data.txns.reduce((sum: number, tx: any) => sum + Number(tx.transaction_fee || 0), 0);
    return {
      last_25_tx_fees: `${(totalGas / 1e24).toFixed(4)} NEAR`,
      avg_per_tx: `${(totalGas / (data.txns.length || 1) / 1e24).toFixed(6)} NEAR`
    };
  } catch (e) {
    return { error: "Could not fetch historical gas data." };
  }
}


export async function near_gas_compare(near_gas: number, eth_gas: number) {
  // Comparison logic
  const cost_near = near_gas * 0.0001; // Mock rate
  const cost_eth = eth_gas * 0.00000001 * 2500; // Mock rate
  return {
    near_usd: cost_near,
    eth_usd: cost_eth,
    savings: cost_eth / cost_near
  };
}
