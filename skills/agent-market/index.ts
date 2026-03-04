import {
  createPublicClient,
  createWalletClient,
  http,
  getContract,
  parseUnits,
  formatUnits,
  formatEther
} from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { baseSepolia } from 'viem/chains';
import { MarketFactoryABI } from './abi/MarketFactory';
import { BinaryMarketABI } from './abi/BinaryMarket';
import { SimpleAMMABI } from './abi/SimpleAMM';
import { OptimisticOracleABI } from './abi/OptimisticOracle';
import { ERC20ABI } from './abi/ERC20';

// Configuration
const FACTORY_ADDRESS = process.env.AGENT_MARKET_FACTORY_ADDRESS || '0xDd553bb9dfbB3F4aa3eA9509bd58386207c98598';
const USDC_ADDRESS = process.env.USDC_ADDRESS || '0x036CbD53842c5426634e7929541eC2318f3dCF7e'; // Base Sepolia USDC
const RPC_URL = process.env.RPC_URL || 'https://sepolia.base.org';
const PRIVATE_KEY = process.env.WALLET_PRIVATE_KEY as `0x${string}`;

// Oracle state enum mapping
const ORACLE_STATES = ['Open', 'Proposed', 'Disputed', 'Resolved'] as const;

// Transaction deadline: 5 minutes from now
function txDeadline(): bigint {
  return BigInt(Math.floor(Date.now() / 1000) + 300);
}

// Initialize Clients
const account = PRIVATE_KEY ? privateKeyToAccount(PRIVATE_KEY) : undefined;

const publicClient = createPublicClient({
  chain: baseSepolia,
  transport: http(RPC_URL)
});

const walletClient = account ? createWalletClient({
  account,
  chain: baseSepolia,
  transport: http(RPC_URL)
}) : undefined;

// Helper: find AMM and oracle addresses from MarketCreated event
async function getMarketContracts(marketAddress: string) {
  const logs = await publicClient.getContractEvents({
    address: FACTORY_ADDRESS as `0x${string}`,
    abi: MarketFactoryABI,
    eventName: 'MarketCreated',
    args: { marketAddress: marketAddress as `0x${string}` },
    fromBlock: 'earliest'
  });

  if (logs.length === 0) return null;

  return {
    ammAddress: logs[0].args.ammAddress as string,
    oracleAddress: logs[0].args.oracle as string,
    deadline: logs[0].args.deadline as bigint
  };
}

// ============================================================
//                      MARKET LISTING
// ============================================================

export async function market_list({ limit = 10, offset = 0 }: { limit?: number, offset?: number }) {
  if (FACTORY_ADDRESS === '0x0000000000000000000000000000000000000000') {
    return "Error: AGENT_MARKET_FACTORY_ADDRESS not configured.";
  }

  const factory = getContract({
    address: FACTORY_ADDRESS as `0x${string}`,
    abi: MarketFactoryABI,
    client: publicClient
  });

  const count = await factory.read.getMarketCount();
  const total = Number(count);

  const markets = [];
  const start = Math.max(0, total - 1 - offset);
  const end = Math.max(0, start - limit + 1);

  for (let i = start; i >= end; i--) {
    try {
      const marketAddress = await factory.read.allMarkets([BigInt(i)]);

      const marketContract = getContract({
        address: marketAddress,
        abi: BinaryMarketABI,
        client: publicClient
      });

      const question = await marketContract.read.question();
      const resolved = await marketContract.read.resolved();
      const totalPool = await marketContract.read.totalPool();

      const contracts = await getMarketContracts(marketAddress);

      let priceYes = null;
      let priceNo = null;
      let oracleState = null;

      if (contracts?.ammAddress) {
        const ammContract = getContract({
          address: contracts.ammAddress as `0x${string}`,
          abi: SimpleAMMABI,
          client: publicClient
        });

        try {
          const pYes = await ammContract.read.priceYES();
          const pNo = await ammContract.read.priceNO();
          // Prices are in 1e18 scale (probability 0-1)
          priceYes = formatEther(pYes);
          priceNo = formatEther(pNo);
        } catch (e) {
          // AMM may have no liquidity
        }
      }

      if (contracts?.oracleAddress) {
        try {
          const oracleContract = getContract({
            address: contracts.oracleAddress as `0x${string}`,
            abi: OptimisticOracleABI,
            client: publicClient
          });
          const state = await oracleContract.read.state();
          oracleState = ORACLE_STATES[state] || 'Unknown';
        } catch (e) {}
      }

      markets.push({
        id: i,
        question,
        marketAddress,
        ammAddress: contracts?.ammAddress || null,
        oracleAddress: contracts?.oracleAddress || null,
        resolved,
        outcome: resolved ? (await marketContract.read.outcome() ? 'YES' : 'NO') : null,
        totalPool: formatUnits(totalPool, 6) + ' USDC',
        yesPrice: priceYes,
        noPrice: priceNo,
        oracleState
      });

    } catch (e) {
      console.error(`Error fetching market ${i}`, e);
    }
  }

  return JSON.stringify(markets, null, 2);
}

// ============================================================
//                      MARKET DETAILS
// ============================================================

export async function market_get({ marketAddress }: { marketAddress: string }) {
  if (FACTORY_ADDRESS === '0x0000000000000000000000000000000000000000') {
    return "Error: AGENT_MARKET_FACTORY_ADDRESS not configured.";
  }

  try {
    const marketContract = getContract({
      address: marketAddress as `0x${string}`,
      abi: BinaryMarketABI,
      client: publicClient
    });

    const question = await marketContract.read.question();
    const resolved = await marketContract.read.resolved();
    const totalPool = await marketContract.read.totalPool();
    const deadline = await marketContract.read.deadline();
    const totalYes = await marketContract.read.totalYesSupply();
    const totalNo = await marketContract.read.totalNoSupply();

    const contracts = await getMarketContracts(marketAddress);

    let ammDetails = null;
    if (contracts?.ammAddress) {
      const ammContract = getContract({
        address: contracts.ammAddress as `0x${string}`,
        abi: SimpleAMMABI,
        client: publicClient
      });

      try {
        const reserveYES = await ammContract.read.reserveYES();
        const reserveNO = await ammContract.read.reserveNO();
        const pYes = await ammContract.read.priceYES();
        const pNo = await ammContract.read.priceNO();

        ammDetails = {
          address: contracts.ammAddress,
          reserveYES: formatUnits(reserveYES, 6),
          reserveNO: formatUnits(reserveNO, 6),
          priceYES: formatEther(pYes),
          priceNO: formatEther(pNo)
        };
      } catch (e) {}
    }

    let oracleDetails = null;
    if (contracts?.oracleAddress) {
      try {
        const oracleContract = getContract({
          address: contracts.oracleAddress as `0x${string}`,
          abi: OptimisticOracleABI,
          client: publicClient
        });

        const state = await oracleContract.read.state();
        const arbitrator = await oracleContract.read.arbitrator();
        const currentBond = await oracleContract.read.currentBond();
        const disputeWindow = await oracleContract.read.disputeWindow();
        const resetCount = await oracleContract.read.resetCount();

        const oracleInfo: Record<string, any> = {
          address: contracts.oracleAddress,
          state: ORACLE_STATES[state] || 'Unknown',
          arbitrator,
          currentBond: formatUnits(currentBond, 6) + ' USDC',
          disputeWindow: Number(disputeWindow) + 's',
          resetCount: Number(resetCount)
        };

        // Add proposal details if applicable
        if (state >= 1) {
          oracleInfo.proposer = await oracleContract.read.proposer();
          oracleInfo.proposedOutcome = (await oracleContract.read.proposedOutcome()) ? 'YES' : 'NO';
          oracleInfo.disputeDeadline = new Date(Number(await oracleContract.read.disputeDeadline()) * 1000).toISOString();
        }
        if (state === 1) {
          const remaining = await oracleContract.read.disputeTimeRemaining();
          oracleInfo.disputeTimeRemaining = Number(remaining) + 's';
          oracleInfo.canDispute = await oracleContract.read.canDispute();
          oracleInfo.canFinalize = await oracleContract.read.canFinalize();
          oracleInfo.canResetProposal = await oracleContract.read.canResetProposal();
        }
        if (state === 2) {
          oracleInfo.challenger = await oracleContract.read.challenger();
        }

        oracleDetails = oracleInfo;
      } catch (e) {}
    }

    // Preview claim for current wallet if resolved
    let claimPreview = null;
    if (resolved && account) {
      try {
        const preview = await marketContract.read.previewClaim([account.address]);
        claimPreview = formatUnits(preview, 6) + ' USDC';
      } catch (e) {}
    }

    return JSON.stringify({
      question,
      resolved,
      outcome: resolved ? (await marketContract.read.outcome() ? 'YES' : 'NO') : null,
      totalPool: formatUnits(totalPool, 6) + ' USDC',
      totalYesTokens: formatUnits(totalYes, 6),
      totalNoTokens: formatUnits(totalNo, 6),
      deadline: new Date(Number(deadline) * 1000).toISOString(),
      amm: ammDetails,
      oracle: oracleDetails,
      claimPreview
    }, null, 2);

  } catch (e) {
    return `Error fetching market: ${e}`;
  }
}

// ============================================================
//                      CREATE MARKET
// ============================================================

export async function market_create({ question, arbitrator, deadlineDays = 7 }: { question: string, arbitrator: string, deadlineDays?: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    // Read actual costs from factory
    const creationFee = await publicClient.readContract({
      address: FACTORY_ADDRESS as `0x${string}`,
      abi: MarketFactoryABI,
      functionName: 'CREATION_FEE'
    });
    const initialLiquidity = await publicClient.readContract({
      address: FACTORY_ADDRESS as `0x${string}`,
      abi: MarketFactoryABI,
      functionName: 'INITIAL_LIQUIDITY'
    });
    const totalCost = creationFee + initialLiquidity;

    // Calculate deadline
    const now = Math.floor(Date.now() / 1000);
    const deadline = BigInt(now + deadlineDays * 86400);

    // Approve USDC
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([FACTORY_ADDRESS as `0x${string}`, totalCost]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Create Market
    const factory = getContract({
      address: FACTORY_ADDRESS as `0x${string}`,
      abi: MarketFactoryABI,
      client: walletClient
    });

    const hash = await factory.write.createMarket([question, arbitrator as `0x${string}`, deadline]);
    const receipt = await publicClient.waitForTransactionReceipt({ hash });

    return `Market created! Transaction: ${hash}\nCost: ${formatUnits(totalCost, 6)} USDC (${formatUnits(creationFee, 6)} fee + ${formatUnits(initialLiquidity, 6)} liquidity)\nDeadline: ${new Date(Number(deadline) * 1000).toISOString()}`;

  } catch (e) {
    return `Error creating market: ${e}`;
  }
}

// ============================================================
//                      BUY YES / NO
// ============================================================

export async function market_buy_yes({ marketAddress, amount }: { marketAddress: string, amount: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amountBig = parseUnits(amount.toString(), 6);

    // Approve USDC to AMM
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([contracts.ammAddress as `0x${string}`, amountBig]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Buy YES
    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.buyYES([amountBig, 0n, txDeadline()]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Bought YES shares for ${amount} USDC! Transaction: ${hash}`;

  } catch (e) {
    return `Error buying YES: ${e}`;
  }
}

export async function market_buy_no({ marketAddress, amount }: { marketAddress: string, amount: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amountBig = parseUnits(amount.toString(), 6);

    // Approve USDC to AMM
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([contracts.ammAddress as `0x${string}`, amountBig]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Buy NO
    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.buyNO([amountBig, 0n, txDeadline()]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Bought NO shares for ${amount} USDC! Transaction: ${hash}`;

  } catch (e) {
    return `Error buying NO: ${e}`;
  }
}

// ============================================================
//                      SELL YES / NO
// ============================================================

export async function market_sell_yes({ marketAddress, amount }: { marketAddress: string, amount: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amountBig = parseUnits(amount.toString(), 6);

    // Get YES token address from AMM
    const ammContract = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: publicClient
    });
    const yesTokenAddr = await ammContract.read.yesToken();

    // Approve YES token to AMM
    const yesToken = getContract({
      address: yesTokenAddr as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await yesToken.write.approve([contracts.ammAddress as `0x${string}`, amountBig]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Sell YES
    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.sellYES([amountBig, 0n, txDeadline()]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Sold ${amount} YES shares for USDC! Transaction: ${hash}`;

  } catch (e) {
    return `Error selling YES: ${e}`;
  }
}

export async function market_sell_no({ marketAddress, amount }: { marketAddress: string, amount: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amountBig = parseUnits(amount.toString(), 6);

    // Get NO token address from AMM
    const ammContract = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: publicClient
    });
    const noTokenAddr = await ammContract.read.noToken();

    // Approve NO token to AMM
    const noToken = getContract({
      address: noTokenAddr as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await noToken.write.approve([contracts.ammAddress as `0x${string}`, amountBig]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Sell NO
    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.sellNO([amountBig, 0n, txDeadline()]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Sold ${amount} NO shares for USDC! Transaction: ${hash}`;

  } catch (e) {
    return `Error selling NO: ${e}`;
  }
}

// ============================================================
//                      LIQUIDITY
// ============================================================

export async function market_add_liquidity({ marketAddress, amount }: { marketAddress: string, amount: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amountBig = parseUnits(amount.toString(), 6);

    // Approve USDC to AMM
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([contracts.ammAddress as `0x${string}`, amountBig]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Add liquidity
    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.addLiquidity([amountBig, 0n, txDeadline()]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Added ${amount} USDC liquidity! You received LP tokens. Transaction: ${hash}`;

  } catch (e) {
    return `Error adding liquidity: ${e}`;
  }
}

export async function market_remove_liquidity({ marketAddress, shares }: { marketAddress: string, shares: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const sharesBig = parseUnits(shares.toString(), 6);

    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.removeLiquidity([sharesBig]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Removed liquidity (burned ${shares} LP shares). You received YES + NO tokens. Transaction: ${hash}`;

  } catch (e) {
    return `Error removing liquidity: ${e}`;
  }
}

// ============================================================
//                      LP POST-RESOLUTION
// ============================================================

export async function market_lp_claim_winnings({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.claimWinnings();
    await publicClient.waitForTransactionReceipt({ hash });

    // Read claimed amount
    const ammRead = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: publicClient
    });
    const claimed = await ammRead.read.claimedUSDC();

    return `AMM claimed winnings from resolved market: ${formatUnits(claimed, 6)} USDC. LPs can now call market_lp_withdraw.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error claiming AMM winnings: ${e}`;
  }
}

export async function market_lp_withdraw({ marketAddress, shares }: { marketAddress: string, shares: number }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.ammAddress) return "Error: Could not find AMM for this market.";

    const sharesBig = parseUnits(shares.toString(), 6);

    const amm = getContract({
      address: contracts.ammAddress as `0x${string}`,
      abi: SimpleAMMABI,
      client: walletClient
    });

    const hash = await amm.write.withdrawAfterResolution([sharesBig]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Withdrew USDC for ${shares} LP shares after resolution. Transaction: ${hash}`;

  } catch (e) {
    return `Error withdrawing after resolution: ${e}`;
  }
}

// ============================================================
//                      CLAIM WINNINGS
// ============================================================

export async function market_claim({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const marketContract = getContract({
      address: marketAddress as `0x${string}`,
      abi: BinaryMarketABI,
      client: publicClient
    });

    // Check claimable amount first
    const preview = await marketContract.read.previewClaim([account.address]);
    if (preview === 0n) return "Nothing to claim (no winning tokens, already claimed, or market not resolved).";

    const market = getContract({
      address: marketAddress as `0x${string}`,
      abi: BinaryMarketABI,
      client: walletClient
    });

    const hash = await market.write.claim();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Claimed ${formatUnits(preview, 6)} USDC! Transaction: ${hash}`;

  } catch (e) {
    return `Error claiming: ${e}`;
  }
}

// ============================================================
//                      EMERGENCY WITHDRAW
// ============================================================

export async function market_emergency_withdraw({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const market = getContract({
      address: marketAddress as `0x${string}`,
      abi: BinaryMarketABI,
      client: walletClient
    });

    const hash = await market.write.emergencyWithdraw();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Emergency withdrawal complete. Transaction: ${hash}`;

  } catch (e) {
    return `Error in emergency withdrawal: ${e}`;
  }
}

// ============================================================
//                   ORACLE: PROPOSE OUTCOME
// ============================================================

export async function market_propose_outcome({ marketAddress, outcome }: { marketAddress: string, outcome: boolean }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracleContract = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: publicClient
    });

    const canPropose = await oracleContract.read.canPropose();
    if (!canPropose) return "Error: Cannot propose right now (oracle not in Open state or market already resolved).";

    const currentBond = await oracleContract.read.currentBond();

    // Approve bond
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([contracts.oracleAddress as `0x${string}`, currentBond]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Propose
    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.proposeOutcome([outcome]);
    await publicClient.waitForTransactionReceipt({ hash });

    const disputeWindow = await oracleContract.read.disputeWindow();

    return `Proposed outcome: ${outcome ? 'YES' : 'NO'}! Bond: ${formatUnits(currentBond, 6)} USDC.\nDispute window: ${Number(disputeWindow)}s. If unchallenged, call market_finalize to resolve.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error proposing outcome: ${e}`;
  }
}

// ============================================================
//                   ORACLE: DISPUTE
// ============================================================

export async function market_dispute({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracleContract = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: publicClient
    });

    const canDispute = await oracleContract.read.canDispute();
    if (!canDispute) return "Error: Cannot dispute (no active proposal or dispute window closed).";

    const proposedOutcome = await oracleContract.read.proposedOutcome();
    const currentBond = await oracleContract.read.currentBond();

    // Approve counter-bond
    const usdc = getContract({
      address: USDC_ADDRESS as `0x${string}`,
      abi: ERC20ABI,
      client: walletClient
    });

    const approveTx = await usdc.write.approve([contracts.oracleAddress as `0x${string}`, currentBond]);
    await publicClient.waitForTransactionReceipt({ hash: approveTx });

    // Dispute
    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.disputeProposal();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Disputed proposed outcome (${proposedOutcome ? 'YES' : 'NO'})! Counter-bond: ${formatUnits(currentBond, 6)} USDC.\nThe arbitrator will now make the final call.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error disputing: ${e}`;
  }
}

// ============================================================
//                   ORACLE: FINALIZE
// ============================================================

export async function market_finalize({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracleContract = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: publicClient
    });

    const canFinalize = await oracleContract.read.canFinalize();
    if (!canFinalize) {
      const state = await oracleContract.read.state();
      if (state === 1) {
        const remaining = await oracleContract.read.disputeTimeRemaining();
        return `Error: Dispute window still open (${Number(remaining)}s remaining). Wait for it to close.`;
      }
      return `Error: Cannot finalize (oracle state: ${ORACLE_STATES[state] || 'Unknown'}).`;
    }

    const proposedOutcome = await oracleContract.read.proposedOutcome();

    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.finalize();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Market finalized! Outcome: ${proposedOutcome ? 'YES' : 'NO'}. Proposer bond refunded.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error finalizing: ${e}`;
  }
}

// ============================================================
//                   ORACLE: ARBITRATE (arbitrator only)
// ============================================================

export async function market_arbitrate({ marketAddress, outcome }: { marketAddress: string, outcome: boolean }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracleContract = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: publicClient
    });

    const state = await oracleContract.read.state();
    if (state !== 2) return `Error: Cannot arbitrate (oracle state: ${ORACLE_STATES[state] || 'Unknown'}, must be Disputed).`;

    const arbitrator = await oracleContract.read.arbitrator();
    if (arbitrator.toLowerCase() !== account.address.toLowerCase()) {
      return `Error: You are not the arbitrator for this oracle. Arbitrator: ${arbitrator}`;
    }

    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.arbitrate([outcome]);
    await publicClient.waitForTransactionReceipt({ hash });

    return `Arbitrated! Final outcome: ${outcome ? 'YES' : 'NO'}. Winner gets both bonds.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error arbitrating: ${e}`;
  }
}

// ============================================================
//                   ORACLE: RESET DISPUTE
// ============================================================

export async function market_reset_dispute({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.resetDispute();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Dispute reset! Both bonds returned. Oracle is back to Open state — a new proposal can be made.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error resetting dispute: ${e}`;
  }
}

// ============================================================
//                   ORACLE: RESET PROPOSAL
// ============================================================

export async function market_reset_proposal({ marketAddress }: { marketAddress: string }) {
  if (!walletClient || !account) return "Error: No wallet configured.";

  try {
    const contracts = await getMarketContracts(marketAddress);
    if (!contracts?.oracleAddress) return "Error: Could not find oracle for this market.";

    const oracle = getContract({
      address: contracts.oracleAddress as `0x${string}`,
      abi: OptimisticOracleABI,
      client: walletClient
    });

    const hash = await oracle.write.resetProposal();
    await publicClient.waitForTransactionReceipt({ hash });

    return `Proposal reset! Proposer bond returned. Oracle is back to Open state.\nTransaction: ${hash}`;

  } catch (e) {
    return `Error resetting proposal: ${e}`;
  }
}

// ============================================================
//                   ARBITRATOR CHECK
// ============================================================

export async function market_arbitrator_check() {
  if (FACTORY_ADDRESS === '0x0000000000000000000000000000000000000000') {
    return "Error: AGENT_MARKET_FACTORY_ADDRESS not configured.";
  }
  if (!account) {
    return "Error: No wallet configured (needed to identify self as arbitrator).";
  }

  const factory = getContract({
    address: FACTORY_ADDRESS as `0x${string}`,
    abi: MarketFactoryABI,
    client: publicClient
  });

  const count = await factory.read.getMarketCount();
  const total = Number(count);

  const myAddress = account.address.toLowerCase();
  const pendingActions = [];

  for (let i = 0; i < total; i++) {
    try {
      const marketAddress = await factory.read.allMarkets([BigInt(i)]);

      const marketContract = getContract({
        address: marketAddress,
        abi: BinaryMarketABI,
        client: publicClient
      });

      const resolved = await marketContract.read.resolved();
      if (resolved) continue;

      // Get oracle contract address
      const oracleAddress = await marketContract.read.oracle();

      const oracleContract = getContract({
        address: oracleAddress,
        abi: OptimisticOracleABI,
        client: publicClient
      });

      const arbitrator = await oracleContract.read.arbitrator();

      if (arbitrator.toLowerCase() === myAddress) {
        const state = await oracleContract.read.state();
        const question = await marketContract.read.question();

        const info: Record<string, any> = {
          marketAddress,
          oracleAddress,
          question,
          oracleState: ORACLE_STATES[state] || 'Unknown'
        };

        if (state === 1) {
          // Proposed — check if we can finalize or if dispute window is still open
          const canFinalize = await oracleContract.read.canFinalize();
          const canResetProposal = await oracleContract.read.canResetProposal();
          const proposedOutcome = await oracleContract.read.proposedOutcome();
          info.proposedOutcome = proposedOutcome ? 'YES' : 'NO';
          info.canFinalize = canFinalize;
          if (!canFinalize) {
            const remaining = await oracleContract.read.disputeTimeRemaining();
            info.disputeTimeRemaining = Number(remaining) + 's';
          }
          if (canResetProposal) {
            info.action = 'STUCK PROPOSAL — can call market_reset_proposal';
          } else {
            info.action = canFinalize ? 'READY TO FINALIZE' : 'WAITING (dispute window open)';
          }
        } else if (state === 2) {
          // Disputed — needs arbitration
          const proposedOutcome = await oracleContract.read.proposedOutcome();
          info.proposedOutcome = proposedOutcome ? 'YES' : 'NO';
          info.action = 'NEEDS ARBITRATION — call market_arbitrate';
        } else if (state === 0) {
          info.action = 'AWAITING PROPOSAL — no action needed yet';
        }

        pendingActions.push(info);
      }

    } catch (e) {
      console.error(`Error checking market ${i}`, e);
    }
  }

  if (pendingActions.length === 0) {
    return "No pending markets found where you are the arbitrator.";
  }

  return JSON.stringify({
    message: "Found markets where you are the arbitrator.",
    markets: pendingActions
  }, null, 2);
}
