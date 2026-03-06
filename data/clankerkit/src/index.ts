import type { Address } from 'viem';
import { parseUnits } from 'viem';
import {
  ClankerKit,
  TOKEN_ADDRESSES,
  TOKEN_DECIMALS,
  deployAgentWallet,
  deployPolicyEngine,
} from 'clankerkit';
import type {
  CrossChainSwapParams,
  PolicyConfig,
  TradeStrategy,
  TradeStrategyType,
} from 'clankerkit';

let clankerKit: ClankerKit | null = null;

function getClankerKit(): ClankerKit {
  if (!clankerKit) {
    const walletAddress = process.env.AGENT_WALLET_ADDRESS as Address;
    const owner = process.env.OWNER_ADDRESS as Address;
    const agentKey = (`0x${process.env.AGENT_PRIVATE_KEY?.replace(/^0x/, '')}`) as Address;
    const policyEngine = process.env.POLICY_ENGINE_ADDRESS as Address;
    const rpcUrl = process.env.MONAD_RPC_URL || 'https://testnet-rpc.monad.xyz';
    const testnet = process.env.MONAD_NETWORK !== 'mainnet';

    if (!walletAddress || !owner || !agentKey) {
      throw new Error('Missing required environment variables: AGENT_WALLET_ADDRESS, OWNER_ADDRESS, AGENT_PRIVATE_KEY');
    }

    clankerKit = new ClankerKit({
      walletAddress,
      owner,
      agentKey,
      policyEngine,
      rpcUrl,
      testnet,
    });
  }
  return clankerKit;
}

function formatAmount(amount: bigint, token: string): string {
  const decimals = TOKEN_DECIMALS[token.toUpperCase()] ?? 18;
  const divisor = BigInt(10 ** decimals);
  const whole = amount / divisor;
  const fraction = amount % divisor;
  const fractionStr = fraction.toString().padStart(decimals, '0').slice(0, 4);
  return `${whole}.${fractionStr}`;
}

/**
 * Convert a human-readable amount string to wei (bigint).
 * Handles both:
 *   - Human-readable: "0.01" → parsed with token decimals
 *   - Already wei: "10000000000000000" → passed through as-is
 *
 * Heuristic: if the string contains a decimal point, treat it as human-readable.
 * Otherwise, if it's a pure integer with >10 digits, treat it as raw wei.
 * For short integers like "1" or "100", treat as human-readable.
 *
 * For unknown token addresses, queries decimals on-chain via the SDK.
 */
async function parseHumanAmount(amount: string, token: string, kit?: ClankerKit): Promise<bigint> {
  let decimals = TOKEN_DECIMALS[token.toUpperCase()];

  // For contract addresses not in TOKEN_DECIMALS, try on-chain lookup
  if (decimals === undefined && kit && token.startsWith('0x') && token.length === 42) {
    decimals = await kit.fetchTokenDecimals(token);
  }
  decimals = decimals ?? 18;

  // Contains a decimal point => definitely human-readable
  if (amount.includes('.')) {
    return parseUnits(amount, decimals);
  }

  // Pure integer: if it's very large (>10 digits), assume it's already in wei.
  // This handles backward compatibility for callers passing raw wei.
  if (/^\d+$/.test(amount) && amount.length > 10) {
    return BigInt(amount);
  }

  // Short integer like "1", "100" => treat as human-readable
  return parseUnits(amount, decimals);
}

export const tools = {
  async get_wallet_info() {
    const kit = getClankerKit();
    const info = await kit.getInfo();
    return {
      address: info.address,
      owner: info.owner,
      agent: info.agent,
      balance: formatAmount(info.balance, 'MON'),
      balanceWei: info.balance.toString(),
      policies: info.policies ? {
        isActive: info.policies.isActive,
        dailyLimit: info.policies.dailyLimit.toString(),
        dailySpent: info.policies.dailySpent.toString(),
        weeklyLimit: info.policies.weeklyLimit.toString(),
        weeklySpent: info.policies.weeklySpent.toString(),
      } : null,
    };
  },

  async get_token_balance({ token }: { token: string }) {
    const kit = getClankerKit();
    const network = process.env.MONAD_NETWORK !== 'mainnet' ? 'testnet' : 'mainnet';
    const tokens = TOKEN_ADDRESSES[network] as Record<string, Address>;
    let tokenAddress: Address;
    if (token.startsWith('0x') && token.length === 42) {
      tokenAddress = token as Address;
    } else {
      tokenAddress = tokens[token.toUpperCase()];
      if (!tokenAddress) {
        throw new Error(`Unknown token: ${token}. Available: ${Object.keys(tokens).join(', ')}`);
      }
    }
    const balance = await kit.getTokenBalance(tokenAddress);
    const symbol = kit.resolveTokenSymbol(token);
    return {
      token: symbol,
      tokenAddress,
      balance: formatAmount(balance, symbol),
      balanceWei: balance.toString(),
    };
  },

  async send_tokens({ to, amount }: { to: string; amount: string }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, 'MON', kit);
    const result = await kit.send(to as Address, amountWei);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      amountSent: amount,
      amountWei: amountWei.toString(),
    };
  },

  async send_token({ token, to, amount }: { token: string; to: string; amount: string }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, token, kit);
    const result = await kit.sendToken(token as Address, to as Address, amountWei);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      token,
      amountSent: amount,
      amountWei: amountWei.toString(),
    };
  },

  async execute_transaction({ target, value = '0', data }: { target: string; value?: string; data: string }) {
    const kit = getClankerKit();
    const result = await kit.execute(target as Address, BigInt(value), data as `0x${string}`);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
    };
  },

  async swap_tokens({ tokenIn, tokenOut, amount, slippage = 50 }: {
    tokenIn: string;
    tokenOut: string;
    amount: string;
    slippage?: number;
  }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, tokenIn, kit);

    // Resolve human-readable symbols for output
    const tokenInSymbol = kit.resolveTokenSymbol(tokenIn);
    const tokenOutSymbol = kit.resolveTokenSymbol(tokenOut);

    const quote = await kit.getSwapQuote({
      tokenIn,
      tokenOut,
      amount: amountWei,
      slippage,
    });

    const result = await kit.swap({
      tokenIn,
      tokenOut,
      amount: amountWei,
      slippage,
    });

    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      tokenIn: tokenInSymbol,
      tokenOut: tokenOutSymbol,
      tokenInAddress: tokenIn,
      tokenOutAddress: tokenOut,
      amountIn: amount,
      amountInWei: amountWei.toString(),
      expectedAmountOut: quote.amountOut.toString(),
      minAmountOut: quote.minAmountOut.toString(),
    };
  },

  async get_swap_quote({ tokenIn, tokenOut, amount }: {
    tokenIn: string;
    tokenOut: string;
    amount: string;
  }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, tokenIn, kit);

    // Resolve human-readable symbols for output
    const tokenInSymbol = kit.resolveTokenSymbol(tokenIn);
    const tokenOutSymbol = kit.resolveTokenSymbol(tokenOut);

    const quote = await kit.getSwapQuote({
      tokenIn,
      tokenOut,
      amount: amountWei,
    });

    return {
      tokenIn: tokenInSymbol,
      tokenOut: tokenOutSymbol,
      tokenInAddress: tokenIn,
      tokenOutAddress: tokenOut,
      amountIn: amount,
      amountInWei: amountWei.toString(),
      expectedAmountOut: quote.amountOut.toString(),
      minAmountOut: quote.minAmountOut.toString(),
    };
  },

  async stake_mon({ amount, validatorId }: { amount: string; validatorId?: number }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, 'MON', kit);
    const result = await kit.stake(
      validatorId !== undefined ? BigInt(validatorId) : undefined,
      amountWei
    );
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      amountStaked: amount,
      amountWei: amountWei.toString(),
      validatorId: validatorId ?? 1,
    };
  },

  async unstake_mon({ amount, validatorId, withdrawId = 0 }: {
    amount: string;
    validatorId?: number;
    withdrawId?: number;
  }) {
    const kit = getClankerKit();
    const amountWei = await parseHumanAmount(amount, 'MON', kit);
    const result = await kit.unstake(
      validatorId !== undefined ? BigInt(validatorId) : undefined,
      amountWei,
      withdrawId
    );
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      amountUnstaked: amount,
      amountWei: amountWei.toString(),
      validatorId: validatorId ?? 1,
      withdrawId,
      note: 'Withdrawal will be available after 1 epoch delay. Call withdraw_stake to claim.',
    };
  },

  async withdraw_stake({ validatorId, withdrawId = 0 }: {
    validatorId?: number;
    withdrawId?: number;
  }) {
    const kit = getClankerKit();
    const result = await kit.withdrawStake(
      validatorId !== undefined ? BigInt(validatorId) : undefined,
      withdrawId
    );
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      validatorId: validatorId ?? 1,
      withdrawId,
    };
  },

  async claim_staking_rewards({ validatorId }: { validatorId?: number }) {
    const kit = getClankerKit();
    const result = await kit.claimStakingRewards(
      validatorId !== undefined ? BigInt(validatorId) : undefined
    );
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      validatorId: validatorId ?? 1,
    };
  },

  async compound_rewards({ validatorId }: { validatorId?: number }) {
    const kit = getClankerKit();
    const result = await kit.compoundRewards(
      validatorId !== undefined ? BigInt(validatorId) : undefined
    );
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      validatorId: validatorId ?? 1,
    };
  },

  async get_staking_info({ validatorId }: { validatorId?: number }) {
    const kit = getClankerKit();
    const info = await kit.getDelegationInfo(
      validatorId !== undefined ? BigInt(validatorId) : undefined
    );
    return {
      validatorId: validatorId ?? 1,
      stake: info.stake.toString(),
      stakeFormatted: formatAmount(info.stake, 'MON'),
      unclaimedRewards: info.unclaimedRewards.toString(),
      unclaimedRewardsFormatted: formatAmount(info.unclaimedRewards, 'MON'),
      pendingStake: info.deltaStake.toString(),
      activationEpoch: info.deltaEpoch.toString(),
    };
  },

  async get_policy() {
    const kit = getClankerKit();
    const state = await kit.getPolicyState();
    return {
      isActive: state.isActive,
      dailyLimit: state.dailyLimit.toString(),
      dailySpent: state.dailySpent.toString(),
      dailyRemaining: (state.dailyLimit - state.dailySpent).toString(),
      weeklyLimit: state.weeklyLimit.toString(),
      weeklySpent: state.weeklySpent.toString(),
      weeklyRemaining: (state.weeklyLimit - state.weeklySpent).toString(),
      requireApprovalAbove: state.requireApprovalAbove.toString(),
    };
  },

  async create_policy({
    dailyLimit,
    weeklyLimit,
    allowedTokens = [],
    allowedContracts = [],
    requireApprovalAbove,
  }: {
    dailyLimit: string;
    weeklyLimit?: string;
    allowedTokens?: string[];
    allowedContracts?: string[];
    requireApprovalAbove?: string;
  }) {
    const kit = getClankerKit();
    const config: PolicyConfig = {
      dailyLimit: await parseHumanAmount(dailyLimit, 'MON', kit),
      weeklyLimit: weeklyLimit
        ? await parseHumanAmount(weeklyLimit, 'MON', kit)
        : undefined,
      allowedTokens: allowedTokens.length > 0
        ? (allowedTokens as Address[])
        : undefined,
      allowedContracts: allowedContracts.length > 0
        ? (allowedContracts as Address[])
        : undefined,
      requireApprovalAbove: requireApprovalAbove
        ? await parseHumanAmount(requireApprovalAbove, 'MON', kit)
        : undefined,
    };
    const result = await kit.createPolicy(config);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      dailyLimit,
      weeklyLimit: weeklyLimit ?? 'not set',
    };
  },

  async update_daily_limit({ newLimit }: { newLimit: string }) {
    const kit = getClankerKit();
    const limitWei = await parseHumanAmount(newLimit, 'MON', kit);
    const result = await kit.updateDailyLimit(limitWei);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      newLimit,
      newLimitWei: limitWei.toString(),
    };
  },

  async pay_for_service({ endpoint, amount }: { endpoint: string; amount: number }) {
    const kit = getClankerKit();
    const result = await kit.pay(endpoint, amount);
    return {
      success: result.success,
      transactionHash: result.transactionHash,
      error: result.error,
    };
  },

  async register_agent({ name, description }: { name: string; description: string }) {
    const kit = getClankerKit();
    const result = await kit.registerAsAgent(name, description);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      name,
    };
  },

  // ─── Kuru CLOB tools ──────────────────────────────────────────────────────

  async get_kuru_markets() {
    const kit = getClankerKit();
    return { markets: kit.getKuruMarkets() };
  },

  async get_order_book({ marketAddress }: { marketAddress: string }) {
    const kit = getClankerKit();
    const book = await kit.getOrderBook(marketAddress);
    return {
      marketAddress,
      bestBid: book.bestBid,
      bestAsk: book.bestAsk,
      midPrice: book.midPrice,
      bids: book.bids.slice(0, 10),   // top 10 levels
      asks: book.asks.slice(0, 10),
      blockNumber: book.blockNumber,
    };
  },

  async get_market_price({ marketAddress }: { marketAddress: string }) {
    const kit = getClankerKit();
    const price = await kit.getMarketPrice(marketAddress);
    return { marketAddress, ...price };
  },

  async kuru_market_order({
    marketAddress,
    amount,
    isBuy,
    minAmountOut = 0,
    slippageBps = 100,
  }: {
    marketAddress: string;
    amount: number;
    isBuy: boolean;
    minAmountOut?: number;
    slippageBps?: number;
  }) {
    const kit = getClankerKit();
    const result = await kit.kuruMarketOrder({ marketAddress, amount, isBuy, minAmountOut, slippageBps });
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      orderId: result.orderId,
      status: result.status,
    };
  },

  async kuru_limit_order({
    marketAddress,
    price,
    size,
    isBuy,
    postOnly = false,
  }: {
    marketAddress: string;
    price: number;
    size: number;
    isBuy: boolean;
    postOnly?: boolean;
  }) {
    const kit = getClankerKit();
    const result = await kit.kuruLimitOrder({ marketAddress, price, size, isBuy, postOnly });
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      orderId: result.orderId,
      status: result.status,
    };
  },

  async cancel_kuru_orders({
    marketAddress,
    orderIds,
  }: {
    marketAddress: string;
    orderIds: string[];
  }) {
    const kit = getClankerKit();
    const result = await kit.cancelKuruOrders(marketAddress, orderIds);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      cancelledCount: orderIds.length,
    };
  },

  // ─── Cross-chain swap tools ───────────────────────────────────────────────

  async kyber_swap({
    chain,
    tokenIn,
    tokenOut,
    amountIn,
    slippageBps = 50,
    recipient,
  }: {
    chain: string;
    tokenIn: string;
    tokenOut: string;
    amountIn: string;
    slippageBps?: number;
    recipient?: string;
  }) {
    const kit = getClankerKit();
    const params: CrossChainSwapParams = {
      chain: chain as CrossChainSwapParams['chain'],
      tokenIn,
      tokenOut,
      amountIn,
      slippageBps,
      recipient,
    };
    const result = await kit.kyberSwap(params);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      chain: result.chain,
      amountIn: result.amountIn,
      amountOut: result.amountOut,
    };
  },

  async zerox_swap({
    chain,
    tokenIn,
    tokenOut,
    amountIn,
    slippageBps = 50,
  }: {
    chain: string;
    tokenIn: string;
    tokenOut: string;
    amountIn: string;
    slippageBps?: number;
  }) {
    const kit = getClankerKit();
    const params: CrossChainSwapParams = {
      chain: chain as CrossChainSwapParams['chain'],
      tokenIn,
      tokenOut,
      amountIn,
      slippageBps,
    };
    const result = await kit.zeroExSwap(params);
    return {
      success: result.status === 'success',
      transactionHash: result.hash,
      status: result.status,
      chain: result.chain,
      amountIn: result.amountIn,
      amountOut: result.amountOut,
    };
  },

  // ─── Memecoin / strategy tools ────────────────────────────────────────────

  async get_meme_tokens() {
    const kit = getClankerKit();
    const tokens = await kit.getMemeTokens();
    return {
      tokens: tokens.map((t) => ({
        symbol: t.symbol,
        address: t.address,
        price: t.price,
        priceChange24h: `${(t.priceChange24h * 100).toFixed(2)}%`,
        bid: t.bid,
        ask: t.ask,
        timestamp: new Date(t.timestamp).toISOString(),
      })),
    };
  },

  async get_token_price({ token }: { token: string }) {
    const kit = getClankerKit();
    const metrics = await kit.getTokenPrice(token);
    return {
      symbol: metrics.symbol,
      address: metrics.address,
      price: metrics.price,
      priceChange24h: `${(metrics.priceChange24h * 100).toFixed(2)}%`,
      bid: metrics.bid,
      ask: metrics.ask,
      volume24h: metrics.volume24h,
      timestamp: new Date(metrics.timestamp).toISOString(),
    };
  },

  async smart_trade({
    token,
    strategyType,
    budgetMon,
    stopLoss = 0.1,
    takeProfit = 0.3,
    dcaIntervals = 5,
    momentumThreshold = 0.05,
    autoExecute = false,
  }: {
    token: string;
    strategyType: string;
    budgetMon: number;
    stopLoss?: number;
    takeProfit?: number;
    dcaIntervals?: number;
    momentumThreshold?: number;
    autoExecute?: boolean;
  }) {
    const kit = getClankerKit();
    const strategy: TradeStrategy = {
      type: strategyType as TradeStrategyType,
      budgetMon,
      stopLoss,
      takeProfit,
      dcaIntervals,
      momentumThreshold,
    };
    const result = await kit.smartTrade(token, strategy, autoExecute);
    return {
      strategy: result.strategy,
      token: result.token,
      action: result.action,
      amount: result.amount,
      price: result.price,
      transactionHash: result.hash,
      status: result.status,
      reason: result.reason,
    };
  },

  // ─── Deployment tools ─────────────────────────────────────────────────────

  async ensure_gas({ minBalance, topUpAmount }: {
    minBalance?: string;
    topUpAmount?: string;
  } = {}) {
    const kit = getClankerKit();
    const min = minBalance ? parseUnits(minBalance, 18) : undefined;
    const top = topUpAmount ? parseUnits(topUpAmount, 18) : undefined;
    const result = await kit.ensureGas(min, top);
    const format = (v: bigint) => {
      const d = 18;
      const divisor = BigInt(10 ** d);
      const whole = v / divisor;
      const frac = (v % divisor).toString().padStart(d, '0').slice(0, 6);
      return `${whole}.${frac}`;
    };
    return {
      funded: result.funded,
      transactionHash: result.hash ?? null,
      eoaBalance: format(result.eoaBalance) + ' MON',
      walletBalance: format(result.walletBalance) + ' MON',
      message: result.funded
        ? `Topped up EOA with gas from wallet. TX: ${result.hash}`
        : 'EOA already has sufficient gas balance.',
    };
  },

  async deploy_policy_engine() {
    const privateKey = (`0x${process.env.AGENT_PRIVATE_KEY?.replace(/^0x/, '')}`) as `0x${string}`;
    const rpcUrl = process.env.MONAD_RPC_URL;
    const testnet = process.env.MONAD_NETWORK !== 'mainnet';
    const result = await deployPolicyEngine(privateKey, { rpcUrl, testnet });
    return {
      success: true,
      policyEngineAddress: result.address,
      transactionHash: result.hash,
      network: testnet ? 'testnet' : 'mainnet',
    };
  },

  async deploy_agent_wallet({
    owner,
    agent,
    policyEngine,
  }: {
    owner: string;
    agent: string;
    policyEngine?: string;
  }) {
    const privateKey = (`0x${process.env.AGENT_PRIVATE_KEY?.replace(/^0x/, '')}`) as `0x${string}`;
    const rpcUrl = process.env.MONAD_RPC_URL;
    const testnet = process.env.MONAD_NETWORK !== 'mainnet';
    const result = await deployAgentWallet(
      privateKey,
      owner as Address,
      agent as Address,
      { policyEngine: policyEngine as Address | undefined, rpcUrl, testnet }
    );
    return {
      success: true,
      walletAddress: result.walletAddress,
      policyEngineAddress: result.policyEngineAddress,
      transactionHash: result.hash,
      network: testnet ? 'testnet' : 'mainnet',
    };
  },
};

export default tools;
