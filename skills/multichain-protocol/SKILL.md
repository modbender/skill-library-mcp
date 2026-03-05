---
name: multichain-protocol
description: Turn any AI agent into a 19-chain crypto wallet via MeneseSDK on ICP. Send tokens, swap on DEXes (Raydium, Uniswap, ICPSwap, KongSwap, Cetus, Minswap), bridge cross-chain, manage DeFi positions (Aave, Lido, LP), automate trading (DCA, stop-loss, rebalancing), and process payments — all from a single ICP canister.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🌐"
    requires:
      bins:
        - name: dfx
          install: "sh -ci \"$(curl -fsSL https://internetcomputer.org/install.sh)\""
          check: "dfx --version"
        - name: python3
          install: "apt install -y python3 || brew install python3"
          check: "python3 --version"
    author: Menese Protocol Team
    license: MIT
    tags:
      - crypto
      - wallet
      - defi
      - multi-chain
      - icp
      - payments
---

# Multichain Protocol — MeneseSDK Wallet Skill

Operate across **19 blockchains** from a single ICP canister or CLI: Solana, Ethereum, Bitcoin, Arbitrum, Base, Polygon, BSC, Optimism, ICP, XRP, SUI, TON, Cardano, Aptos, NEAR, Tron, Litecoin, CloakCoin, THORChain.

**Powered by Menese Protocol** | **Canister ID (mainnet):** `urs2a-ziaaa-aaaad-aembq-cai`

---

## Pricing

**First 5 transactions are FREE** — no signup, no credit card, just install and go.

After the free tier, transaction signing is charged per action via your DeveloperKey (`msk_*`). Read-only operations (balances, addresses, pool queries) are always free.

---

## Quickstart (2 minutes)

### Step 1: Install dfx (ICP SDK)

If you don't have `dfx` installed, run this single command:

```bash
sh -ci "$(curl -fsSL https://internetcomputer.org/install.sh)"
```

Verify it works:
```bash
dfx --version
```

That's it. No accounts needed, no wallets to set up — dfx handles everything.

### Step 2: Install the skill

```bash
clawhub install multichain-protocol
```

Or manually: copy `SKILL.md` + `wallet_commands.py` to your workspace.

### Step 3: Create an ICP identity (if you don't have one)

```bash
dfx identity new my-wallet
dfx identity use my-wallet
```

### Step 4: Try it — your first 5 sends are free

Ask your bot:
```
"show my wallet addresses"
"what's my SOL balance?"
"send 0.1 ETH to 0xABC..."
"swap 100 USDC to SOL on Raydium"
"set up a DCA: buy $50 of BTC every day"
```

### Step 5 (optional): Deploy your own canister for production

For multi-user, automation, and timers — deploy `WalletBot.mo` as your own ICP canister.

---

## Two Integration Approaches

| | Canister (Recommended) | CLI (Quick) |
|---|---|---|
| **Flow** | User → ClawdBot → Your Canister → MeneseSDK | User → ClawdBot → `dfx canister call` → MeneseSDK |
| **Setup** | Deploy `WalletBot.mo`, register with SDK | Copy `scripts/wallet_commands.py`, done |
| **Best for** | Multi-user, automation, timers, production | Single-user, prototyping, testing |
| **Automation** | ICP timers for DCA/rebalance/bots | None (manual only) |

---

## Best Practice: Cache Addresses

Addresses are **deterministic** — the same principal always gets the same addresses on every chain. Fetch once, cache forever.

```motoko
// Canister pattern — cache in stable var
stable var cachedAddresses : ?AddressBook = null;

public shared func getAddresses() : async AddressBook {
  switch (cachedAddresses) {
    case (?addrs) { addrs };  // Return cached — no inter-canister call
    case null {
      let sol = await menese.getMySolanaAddress();
      let evm = await menese.getMyEvmAddress();
      // ... fetch all chains once ...
      let addrs = { solana = sol.address; evm = evm.evmAddress; /* ... */ };
      cachedAddresses := ?addrs;
      addrs;
    };
  };
};
```

```python
# CLI pattern — fetch once, store in file
import json, os
CACHE_FILE = "addresses_cache.json"

def get_addresses():
    if os.path.exists(CACHE_FILE):
        return json.load(open(CACHE_FILE))
    addrs = fetch_all_addresses()  # dfx calls
    json.dump(addrs, open(CACHE_FILE, "w"))
    return addrs
```

**Why**: Saves inter-canister call latency + cycles. Addresses never change for a given principal.

---

## EVM Chains — Bring Your Own RPC

All EVM operations (ETH, Arbitrum, Base, Polygon, BSC, Optimism) require **your own RPC endpoint**. MeneseSDK does not manage EVM RPCs.

| Chain | Chain ID | Free Public RPC |
|-------|----------|----------------|
| Ethereum | 1 | `https://eth.llamarpc.com` |
| Arbitrum | 42161 | `https://arb1.arbitrum.io/rpc` |
| Base | 8453 | `https://mainnet.base.org` |
| Polygon | 137 | `https://polygon-rpc.com` |
| BSC | 56 | `https://bsc-dataseed1.binance.org` |
| Optimism | 10 | `https://mainnet.optimism.io` |

Use Alchemy/Infura for production reliability.

---

## Complete Tool Reference

Every operation available, organized by category. Each tool shows the function, parameters, return type, cost, and a usage example.

### Tool 1: Get Addresses (FREE)

Deterministic per-principal. **Cache after first call.**

| Chain | Function | Field to Extract |
|-------|----------|-----------------|
| Solana | `getMySolanaAddress` | `.address` |
| EVM (all 6) | `getMyEvmAddress` | `.evmAddress` (NOT `.address`) |
| Bitcoin | `getMyBitcoinAddress` | `.bech32Address` |
| Litecoin | `getMyLitecoinAddress` | `.bech32Address` |
| SUI | `getMySuiAddress` | `.suiAddress` (NOT `.address`) |
| XRP | `getMyXrpAddress` | `.classicAddress` |
| TON | `getMyTonAddress` | `.nonBounceable` (NOT `.address`) |
| Cardano | `getMyCardanoAddress` | `.bech32Address` |
| Aptos | `getMyAptosAddress` | `.address` |
| NEAR | `getMyNearAddress` | `.implicitAccountId` (NOT `.accountId`) |
| Tron | `getTronAddress` | `.base58Address` (NOT `.base58`) |
| CloakCoin | `getMyCloakAddress` | `.base58Address` |
| THORChain | `getMyThorAddress` | `.bech32Address` |

**Batch**: `getAllAddresses()` — all chains in one call.
**Solana ATA**: `getMySolanaAta(mintBase58)` — get associated token account for an SPL token.

```motoko
// Example: get SOL address
let info = await menese.getMySolanaAddress();
let myAddress = info.address;  // "5xK2abc..."
```

```bash
# CLI
dfx canister call urs2a-ziaaa-aaaad-aembq-cai getMySolanaAddress --network ic --query
```

### Tool 2: Check Balances (FREE)

| Chain | Function | Returns | Unit |
|-------|----------|---------|------|
| Solana | `getMySolanaBalance` | `Result<Nat64, Text>` | lamports (÷10^9) |
| ICP | `getICPBalance` | `Result<Nat64, Text>` | e8s (÷10^8) |
| ICP (for addr) | `getICPBalanceFor(principal)` | `Result<Nat64, Text>` | e8s (÷10^8) |
| Bitcoin | `getBitcoinBalance` | `Nat64` | satoshis (÷10^8) |
| Litecoin | `getLitecoinBalance` | `Nat64` | litoshis (÷10^8) |
| EVM | `getMyEvmBalance(rpcUrl)` | `Result<Nat, Text>` | wei (÷10^18) |
| XRP | `getMyXrpBalance` | `Result<Text, Text>` | drops as text |
| SUI | `getMySuiBalance` | `Nat64` | mist (÷10^9) |
| TON | `getMyTonBalance` | `Result<Nat64, Text>` | nanotons (÷10^9) |
| Cardano | `getCardanoBalance` | `Result<Nat64, Text>` | lovelace (÷10^6) |
| Aptos | `getAptosBalance` | `Result<Nat64, Text>` | octas (÷10^8) |
| NEAR | `getMyNearBalance` | `Nat` | yoctoNEAR (÷10^24) |
| THORChain | `getThorBalance` | `[{amount, denom}]` | units (÷10^8) |
| CloakCoin | `getCloakBalance` | `Result<{address, balance, utxoCount}, Text>` | units (÷10^6) |
| Tron | `getTrxBalance(address)` | `Result<Nat64, Text>` | sun (÷10^6) |
| ICRC-1 tokens | `getICRC1Balance(ledgerId)` | `Result<Nat, Text>` | smallest unit |
| ICRC-1 (for addr) | `getICRC1BalanceFor(principal, ledgerId)` | `Result<Nat, Text>` | smallest unit |
| ICRC-1 info | `getICRC1TokenInfo(ledgerId)` | `Result<TokenInfo, Text>` | name, symbol, decimals |
| ICP tokens list | `getSupportedICPTokens()` | `[{name,symbol,canisterId,type_,category}]` | query |
| TRC-20 tokens | `getMyTrc20Balance(contract)` | `Result<Nat, Text>` | smallest unit |

**Batch**: `getAllBalances()` — parallel fetch across all chains.

**Performance tip**: For high-frequency reads, query chain RPCs directly using cached addresses. MeneseSDK is best for signing; your own RPC is faster for reads.

```motoko
// Example: check SOL balance, convert to human-readable
switch (await menese.getMySolanaBalance()) {
  case (#ok(lamports)) { /* lamports / 1_000_000_000 = SOL */ };
  case (#err(e)) { /* handle error */ };
};
```

### Tool 3: Send Tokens ($0.05 client / $0.10 agent)

**Return types differ by chain** — getting this wrong causes runtime errors.

| Chain | Function | Params | Return |
|-------|----------|--------|--------|
| Solana | `sendSolTransaction` | `(to, lamports:Nat64)` | `Result<Text, Text>` |
| ICP | `sendICP` | `(to:Principal, e8s:Nat64)` | `Result<SendICPResult, Text>` |
| ICRC-1 | `sendICRC1` | `(to:Principal, amount:Nat, ledger:Text)` | `Result<SendICRC1Result, Text>` |
| Bitcoin | `sendBitcoin` | `(to, sats:Nat64)` | `Result<SendResultBtcLtc, Text>` |
| Litecoin | `sendLitecoin` | `(to, litoshis:Nat64)` | `Result<SendResult, Text>` (NOT BtcLtc!) |
| EVM | `sendEvmNativeTokenAutonomous` | `(to, wei:Nat, rpc, chainId:Nat, ?quoteId)` | `Result<SendResultEvm, Text>` |
| XRP | `sendXrpAutonomous` | `(to, amountXrp:Text, ?destTag:Nat32)` | **FLAT** `SendResultXrp` |
| SUI | `sendSui` | `(to, mist:Nat64)` | `Result<SendResult, Text>` |
| TON | `sendTonSimple` | `(to, nanotons:Nat64)` | **FLAT** `SendResultTon` |
| Aptos | `sendAptos` | `(to, octas:Nat64)` | `Result<SendResult, Text>` |
| NEAR | `sendNearTransfer` | `(to, yocto:Nat)` | `Result<Text, Text>` |
| Tron | `sendTrx` | `(to, sun:Nat64)` | `Result<Text, Text>` |
| Cardano | `sendCardanoTransaction` | `(to, lovelace:Nat64)` | `Result<Text, Text>` |
| CloakCoin | `sendCloak` | `(to, amount:Nat64)` | `Result<SendResultCloak, Text>` |
| THORChain | `sendThor` | `(to, amount:Nat64, memo:Text)` | `Result<Text, Text>` |
| SPL Token | `transferSplToken` | `(amount:Nat64, srcAta, dstAta)` | `TransferAndSendResult` |
| XRP IOU | `sendXrpIOU` | `(dest, currency, issuer, amount, ?tag)` | `SendResultXrp` |
| TRC-20 | `sendTrc20` | `(contract, to, amount:Nat, feeLimit:Nat64)` | `Result<Text, Text>` |

**Variant extras**: `sendBitcoinDynamicFee`, `sendBitcoinWithFee`, `sendLitecoinWithFee`, `sendSuiMax`, `sendTon` (with bounce/comment), `sendTonWithComment`.

```motoko
// Example: send 0.5 SOL
switch (await menese.sendSolTransaction("5xK2abc...", 500_000_000)) {
  case (#ok(txHash)) { /* success — txHash is the Solana TX signature */ };
  case (#err(e)) { /* handle error */ };
};

// Example: send XRP (FLAT return — check .success, not #ok)
let r = await menese.sendXrpAutonomous("rDestAddr...", "10.5", null);
if (r.success) { /* r.txHash, r.explorerUrl */ }
else { /* r.message has error */ };
```

### Tool 3b: ICRC-2 Approve & TransferFrom ($0.05 client / $0.10 agent)

ICRC-2 adds ERC-20-style `approve` + `transferFrom` to ICP tokens. Use when building escrow, payment splitters, or any pattern where a canister needs to spend tokens on behalf of users.

| Operation | Function | Params | Return |
|-----------|----------|--------|--------|
| Approve spender | `approveICRC2` | `(spender:Principal, amount:Nat, expiresAt:?Nat64, ledgerId:Text)` | `Result<ApproveResult, Text>` |
| Check allowance | `getICRC2Allowance` | `(owner:Principal, spender:Principal, ledgerId:Text)` | `Result<Allowance, Text>` — FREE |
| TransferFrom | `transferFromICRC2` | `(from:Principal, to:Principal, amount:Nat, ledgerId:Text)` | `Result<TransferFromResult, Text>` |

```motoko
// Approve MeneseSDK canister to spend 100 ckUSDC on your behalf
let ckUSDC = "xevnm-gaaaa-aaaar-qafnq-cai";
let sdk = Principal.fromText("urs2a-ziaaa-aaaad-aembq-cai");
let r = await menese.approveICRC2(sdk, 100_000_000, null, ckUSDC);  // 100 ckUSDC (6 dec)

// Check remaining allowance (FREE)
let allowance = await menese.getICRC2Allowance(myPrincipal, sdk, ckUSDC);

// Transfer from (requires prior approval)
let t = await menese.transferFromICRC2(userPrincipal, treasuryPrincipal, 50_000_000, ckUSDC);
```

### Tool 4: Swap on DEXes ($0.075 client / $0.15 agent)

| DEX | Chain | Function | Key Details |
|-----|-------|----------|-------------|
| Raydium | Solana | `swapRaydiumApiUser` | 8 params, FLAT return |
| Uniswap V3 | EVM | `swapTokens`, `swapTokensMultiHop` | Pass quoteId or rpc+chainId |
| Uniswap shortcuts | EVM | `swapETHForUSDC`, `swapUSDCForETH` | Quick ETH↔USDC |
| ICPSwap/KongSwap | ICP | `executeICPDexSwap(SwapRequest)` | Auto-routes best price |
| Cetus | SUI | `executeSuiSwap(network, from, to, amountIn, minOut)` | Network: `#mainnet` |
| Minswap | Cardano | `executeMinswapSwap(tokenIn, tokenOut, amount, slippage)` | Float slippage % |
| XRP DEX | XRP | `xrpSwap(destAmount, sendMax, paths, slipBps)` | Use xrpFindPaths first |

**Always get a quote first (FREE)**:
- Raydium: `getRaydiumQuote(inputMint, outputMint, amount, slipBps)`
- Uniswap: `getTokenQuote(from, to, amountIn, rpc)`
- ICP: `getICPDexQuote(tokenIn, tokenOut, amountIn, slipPct)` → `AggregatedQuote` (compares ICPSwap vs KongSwap)
- SUI: `getSuiSwapQuote(network, from, to, amountIn, slipBps)`
- Cardano: `getMinswapQuote(tokenIn, tokenOut, amountIn, slipPct)`
- XRP: `xrpFindPaths(destAmount, sourceCurrencies)`

```motoko
// Example: swap 1 SOL → USDC on Raydium
let SOL = "So11111111111111111111111111111111111111112";
let USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";

let result = await menese.swapRaydiumApiUser(
  SOL, USDC,
  1_000_000_000,  // 1 SOL in lamports
  150,            // 1.5% slippage
  true,           // wrapSol: input is native SOL
  false,          // unwrapSol: output is USDC not SOL
  null, null      // auto-detect ATAs
);
// FLAT record — access directly:
// result.txSignature, result.outputAmount, result.priceImpactPct
```

```motoko
// Example: swap on ICP DEX (auto-routes to ICPSwap or KongSwap)
let swapReq : Menese.SwapRequest = {
  tokenIn = "ryjl3-tyaaa-aaaaa-aaaba-cai";  // ICP ledger
  tokenOut = "mxzaz-hqaaa-aaaar-qaada-cai";  // ckUSDC
  amountIn = 100_000_000;  // 1 ICP
  minAmountOut = 0;
  slippagePct = 1.0;
  preferredDex = null;  // auto-pick best price
};
let result = await menese.executeICPDexSwap(swapReq);
```

### Tool 5: Bridge ETH↔SOL ($0.10 client / $0.20 agent)

| Direction | Function | Params |
|-----------|----------|--------|
| ETH→SOL | `quickUltrafastEthToSol` | `(ethWei:Nat)` |
| USDC→SOL | `quickUltrafastUsdcToSol` | `(usdc:Nat)` |
| ETH→Token | `quickUltrafastEthToToken` | `(ethWei:Nat, outputMint, slipBps:Nat)` |
| SOL→ETH | `quickSolToEth` | `(solLamports:Nat64, slipBps:Nat)` |
| USDC SOL→ETH | `quickUsdcBridgeSolToEth` | `(usdc:Nat64)` |
| CCTP (any) | `quickCctpBridge` | `(srcChainId, usdc, outputToken, fast, slipBps, ethRpc)` |

```motoko
// Example: bridge 0.1 ETH to Solana
let result = await menese.quickUltrafastEthToSol(100_000_000_000_000_000);  // 0.1 ETH in wei
// Result<Text, Text> — ok = status text
```

### Tool 6: DeFi — Aave V3 ($0.10 agent)

| Operation | Function | Params |
|-----------|----------|--------|
| Supply ETH | `aaveSupplyEth` | `(wei:Nat, rpc, ?quoteId)` → `Result<SupplyEthResult, Text>` |
| Withdraw ETH | `aaveWithdrawEth` | `(wei:Nat, rpc, ?quoteId)` → `Result<WithdrawEthResult, Text>` |
| Supply ERC-20 | `aaveSupplyToken` | `(tokenAddr, amount:Nat, rpc, ?quoteId)` |
| Withdraw ERC-20 | `aaveWithdrawToken` | `(tokenAddr, amount:Nat, rpc, ?quoteId)` |
| Read aWETH bal | `getAWethBalance` | `(user, rpc)` → FREE |
| Read aToken bal | `getATokenBalance` | `(aTokenAddr, user, rpc)` → FREE |

```motoko
// Supply 0.5 ETH to Aave → receive aWETH (~2-3% APY)
let r = await menese.aaveSupplyEth(500_000_000_000_000_000, ethRpc, null);
switch (r) {
  case (#ok(res)) { /* res.txHash, res.aTokenAddress */ };
  case (#err(e)) { /* error */ };
};
```

### Tool 7: DeFi — Lido Staking ($0.10 agent)

| Operation | Function | Return |
|-----------|----------|--------|
| Stake ETH→stETH | `stakeEthForStEth(wei, rpc, ?quoteId)` | `Result<StakeResult, Text>` |
| Wrap stETH→wstETH | `wrapStEth(amount, rpc, ?quoteId)` | `Result<WrapResult, Text>` |
| Unwrap wstETH→stETH | `unwrapWstEth(amount, rpc, ?quoteId)` | `Result<UnwrapResult, Text>` |
| Read stETH bal | `getStEthBalance(user, rpc)` | FREE |
| Read wstETH bal | `getWstEthBalance(user, rpc)` | FREE |

```motoko
// Stake 1 ETH with Lido (~3-4% APY), then wrap for DeFi composability
ignore await menese.stakeEthForStEth(1_000_000_000_000_000_000, ethRpc, null);
ignore await menese.wrapStEth(1_000_000_000_000_000_000, ethRpc, null);
```

### Tool 8: DeFi — Uniswap V3 Liquidity ($0.10 agent)

| Operation | Function |
|-----------|----------|
| Add ETH+Token LP | `addLiquidityETH(tokenSymbol, tokenAmt, ethAmt, slipBps, rpc, ?quoteId)` |
| Add Token+Token LP | `addLiquidity(tokenA, tokenB, amtA, amtB, slipBps, rpc, ?quoteId)` |
| Remove ETH LP | `removeLiquidityETH(tokenSymbol, lpAmt, slipBps, feeOnTransfer, rpc, ?quoteId)` |
| Remove Token LP | `removeLiquidity(tokenA, tokenB, lpAmt, slipBps, rpc, ?quoteId)` |
| Read reserves | `getPoolReserves(tokenA, tokenB, rpc)` — FREE |
| Get pair addr | `getPairAddress(tokenA, tokenB, rpc)` — FREE |

### Tool 9: Custom EVM Contract Calls

| Operation | Function | Cost |
|-----------|----------|------|
| Read (view) | `callEvmContractRead(contract, selector4byte, argsHexes, rpc)` | FREE |
| Write (tx) | `callEvmContractWrite(contract, selector, args, rpc, chainId, value, ?quoteId)` | $0.10 |

Selector = first 4 bytes of `keccak256("functionName(type1,type2)")`, hex-encoded, no `0x` prefix.

```motoko
// Read Chainlink ETH/USD price (FREE)
let result = await menese.callEvmContractRead(
  "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  // ETH/USD feed
  "feaf968c",  // latestRoundData()
  [], ethRpc
);
```

### Tool 10: Strategy Engine (rule creation FREE, execution per-action pricing)

| Operation | Function | Cost |
|-----------|----------|------|
| Create rule | `addStrategyRule(Rule)` | FREE |
| List rules | `getMyStrategyRules()` | FREE |
| Update status | `updateStrategyRuleStatus(ruleId, status)` | FREE |
| Delete rule | `deleteStrategyRule(ruleId)` | FREE |
| View logs | `getStrategyLogs()` | FREE |
| Init automation | `initAutomation()` | FREE |

Rule types: `#DCA`, `#StopLoss`, `#TakeProfit`, `#Rebalance`, `#Scheduled`, `#APYMigration`, `#LiquidityProvision`, `#VolatilityTrigger`.

Rule statuses: `#Active`, `#Paused`, `#Cancelled`, `#Executed`, `#Executing`, `#Failed`, `#Draft`, `#Confirmed`, `#Ready`.

### Tool 11: Solana ATA / XRP Trustlines (setup)

| Operation | Function | Cost |
|-----------|----------|------|
| Create Solana ATA | `createMySolanaAtaForMint(mint, ata)` | Send pricing |
| Create ATA (custom program) | `createMySolanaAtaForMintWithProgram(mint, ata, programId)` | Send pricing |
| Set XRP trustline | `xrpSetTrustline(currency, issuer, limit)` | Send pricing |
| Read XRP trustlines | `xrpGetAccountLines()` | FREE |
| Get Solana ATA | `getMySolanaAta(mint)` | FREE |

### Tool 12: Developer/Billing

| Operation | Function | Cost |
|-----------|----------|------|
| Register canister | `registerDeveloperCanister(Principal, appName)` | FREE |
| Get dev key | `getMyDeveloperKey()` | FREE |
| Regenerate key | `regenerateDeveloperKey()` | FREE |
| Validate key | `validateDeveloperKey(key)` | FREE |
| Check account | `getMyGatewayAccount()` → `UserAccount` | FREE |
| Check dev account | `getMyDeveloperAccount()` → `?DeveloperAccountV3` | FREE |
| Deposit credits | `depositGatewayCredits(currency, amount)` | ICP cost |

### Tool 13: Utility

| Operation | Function | Cost |
|-----------|----------|------|
| BTC max send | `getBitcoinMaxSendAmount(?feeRate)` → `{maxAmount, fee, utxoCount}` | FREE |
| LTC max send | `getLitecoinMaxSendAmount(?feeRate)` → `{maxAmount, fee, utxoCount}` | FREE |
| Health check | `health()` | FREE |
| Version | `version()` | FREE |

### Tool 14: ICP DEX LP Management ($0.10 agent)

Manage liquidity positions on ICPSwap and KongSwap. The SDK aggregates both DEXes.

| Operation | Function | Cost |
|-----------|----------|------|
| List pools | `getICPDexPools()` → `[PoolInfo]` | FREE |
| List tokens | `getICPDexTokens()` → `[DexToken]` | FREE |
| View positions | `getICPLPPositions()` → `[LPPosition]` | FREE |
| Add liquidity | `addICPLiquidity(AddLiquidityRequest)` → `Result<AddLiquidityResult, Text>` | $0.10 |
| Remove liquidity | `removeICPLiquidity(RemoveLiquidityRequest)` → `Result<RemoveLiquidityResult, Text>` | $0.10 |

**Types:**

```
AddLiquidityRequest = { poolId:Text, dex:{#ICPSwap|#KongSwap}, token0:Text, token1:Text, token0Amount:Nat, token1Amount:Nat, slippagePct:Float }
RemoveLiquidityRequest = { poolId:Text, dex:{#ICPSwap|#KongSwap}, lpTokens:Nat, slippagePct:Float }
LPPosition = { poolId, dex, token0, token1, token0Symbol, token1Symbol, liquidity:Nat, token0Amount, token1Amount, unclaimedFees:?(Nat,Nat), valueUsd:?Nat }
PoolInfo = { poolId, dex, token0, token1, token0Symbol, token1Symbol, reserve0, reserve1, fee, tvl:?Nat, apr:?Float, volume24h:?Nat }
DexToken = { canisterId, symbol, name, decimals:Nat8, fee:Nat, standard:{#ICRC1|#ICRC2|#DIP20}, logo:?Text, category:?Text, availableOn:[DexId] }
```

**Well-known pools:** ICP/ckUSDC, ckBTC/ICP, ICP/ckETH, ckUSDT/ckUSDC, CHAT/ICP (on both ICPSwap and KongSwap).

```motoko
// Discover pools, then add liquidity
let pools = await menese.getICPDexPools();
// Find ICP/ckUSDC pool
let pool = Array.find<DexTypes.PoolInfo>(pools, func(p) { p.token0Symbol == "ICP" and p.token1Symbol == "ckUSDC" });

switch (pool) {
  case (?p) {
    let req : DexTypes.AddLiquidityRequest = {
      poolId = p.poolId;
      dex = p.dex;
      token0 = "ryjl3-tyaaa-aaaaa-aaaba-cai";  // ICP ledger
      token1 = "xevnm-gaaaa-aaaar-qafnq-cai";  // ckUSDC
      token0Amount = 100_000_000;  // 1 ICP
      token1Amount = 10_000_000;   // 10 ckUSDC
      slippagePct = 1.0;
    };
    let result = await menese.addICPLiquidity(req);
  };
  case null { /* pool not found */ };
};

// View positions
let positions = await menese.getICPLPPositions();
// Remove liquidity
let removeReq : DexTypes.RemoveLiquidityRequest = {
  poolId = positions[0].poolId;
  dex = positions[0].dex;
  lpTokens = positions[0].liquidity;  // Remove all
  slippagePct = 1.0;
};
let removed = await menese.removeICPLiquidity(removeReq);
```

### Tool 15: ICP AI Rebalancer (FREE)

AI-powered portfolio rebalancing recommendations using Herfindahl-Hirschman Index diversification scoring, impermanent loss estimation, and risk-adjusted APY analysis.

| Operation | Function | Cost |
|-----------|----------|------|
| Get recommendations | `getICPRebalanceRecommendations(preferences, tokenBalances, pools?)` → `[RebalanceRecommendation]` | FREE |

**Types:**

```
RebalancePreferences = { targetCategories:[Text], riskTolerance:Text, minApy:?Float, maxImpermanentLoss:?Float, autoCompound:Bool }
  targetCategories: ["stablecoin", "defi", "lst", "yield", "wrapped", "meme", "ecosystem"]
  riskTolerance: "conservative" | "moderate" | "aggressive"

RebalanceRecommendation = { id, action:{#Swap|#AddLiquidity|#RemoveLiquidity|#Compound}, fromToken, toToken, fromSymbol, toSymbol, amount:Nat, reason:Text, estimatedApy:?Float, currentApy:?Float, impermanentLossRisk:{#Low|#Medium|#High}, confidence:Float, estimatedGasUsd:?Float }
```

```motoko
// Get rebalancing recommendations for your ICP portfolio
let prefs : DexTypes.RebalancePreferences = {
  targetCategories = ["stablecoin", "defi", "lst"];
  riskTolerance = "moderate";
  minApy = ?5.0;        // Only suggest >5% APY
  maxImpermanentLoss = ?10.0;  // Max 10% IL risk
  autoCompound = true;
};

// Pass current balances: [(canisterId, amount)]
let balances = [
  ("ryjl3-tyaaa-aaaaa-aaaba-cai", 500_000_000),  // 5 ICP
  ("xevnm-gaaaa-aaaar-qafnq-cai", 100_000_000),  // 100 ckUSDC
  ("mxzaz-hqaaa-aaaar-qaada-cai", 50_000),        // 0.0005 ckBTC
];

let recommendations = await menese.getICPRebalanceRecommendations(prefs, balances, null);
for (rec in recommendations.vals()) {
  Debug.print(rec.reason # " | Confidence: " # Float.toText(rec.confidence));
  // e.g., "Swap 2 ICP → ckUSDC and add to ICP/ckUSDC pool for 12.5% APY | Confidence: 0.85"
};
```

---

## Combining Tools — Practical Automation Examples

The real power is combining these tools. Below are complete patterns showing how tools work together.

### Example 1: DCA Bot (Timer + Balance + Swap)

Buy USDC with SOL every hour if balance exceeds threshold.

```motoko
// Tools used: getMySolanaBalance (FREE) + swapRaydiumApiUser ($0.075)
func dcaCycle() : async () {
  let balance = switch (await menese.getMySolanaBalance()) {
    case (#ok(v)) v; case (#err(_)) return;
  };
  if (balance < 500_000_000) return;  // < 0.5 SOL, skip

  let swapAmt = balance - 50_000_000;  // Keep 0.05 SOL for rent
  let _ = await menese.swapRaydiumApiUser(
    "So11111111111111111111111111111111111111112",  // SOL
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",  // USDC
    swapAmt, 150, true, false, null, null
  );
};

// Run every hour
let timerId = Timer.recurringTimer<system>(#seconds(3600), dcaCycle);
```

### Example 2: Stop-Loss via Strategy Engine

Set a stop-loss rule that auto-sells when price drops. No timer needed — MeneseSDK evaluates.

```motoko
// Tool used: addStrategyRule (FREE to create, execution costs per action)
let rule : Menese.Rule = {
  id = 0;
  ruleType = #StopLoss;
  status = #Active;
  chainType = #Solana;
  triggerPrice = 120_000_000;  // Trigger at this price level
  sizePct = 100;  // Sell 100% of position
  positionId = 0;
  createdAt = Time.now();
  dcaConfig = null; lpConfig = null; scheduledConfig = null;
  apyMigrationConfig = null; volatilityConfig = null;
  swapAmountLamports = ?1_000_000_000;  // 1 SOL
  swapAmountWei = null;
};
let ruleId = await menese.addStrategyRule(rule);
```

### Example 3: Take-Profit + Stop-Loss Combo

Set both on the same position — whichever triggers first wins.

```motoko
// Tools: addStrategyRule × 2
// Take-profit at 200
let tp : Menese.Rule = { /* ... */ ruleType = #TakeProfit; triggerPrice = 200_000_000; sizePct = 50; /* sell half */ /* ... */ };
let tpId = await menese.addStrategyRule(tp);

// Stop-loss at 100
let sl : Menese.Rule = { /* ... */ ruleType = #StopLoss; triggerPrice = 100_000_000; sizePct = 100; /* sell all */ /* ... */ };
let slId = await menese.addStrategyRule(sl);

// When one triggers, cancel the other
// Check via getMyStrategyRules() or getStrategyLogs() in your timer
```

### Example 4: DCA via Strategy Engine (no custom timer)

Let MeneseSDK handle the scheduling internally.

```motoko
// Tool: addStrategyRule with DCA config
let dca : Menese.Rule = {
  id = 0;
  ruleType = #DCA;
  status = #Active;
  chainType = #Solana;
  triggerPrice = 0; sizePct = 100; positionId = 0;
  createdAt = Time.now();
  dcaConfig = ?{
    amountPerInterval = 100_000_000;  // 0.1 SOL per buy
    currentInterval = 0;
    intervalSeconds = 3600;  // Every hour
    lastExecutedAt = 0;
    maxIntervals = 168;  // Run for 1 week (168 hours)
    targetToken = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v";  // Buy USDC
    totalSpent = 0;
  };
  lpConfig = null; scheduledConfig = null;
  apyMigrationConfig = null; volatilityConfig = null;
  swapAmountLamports = ?100_000_000;
  swapAmountWei = null;
};
ignore await menese.addStrategyRule(dca);
```

### Example 5: Multi-Chain Sweep (Balance + Send across chains)

Check all balances, sweep any above threshold to treasury.

```motoko
// Tools: getAllBalances (FREE) + sendSolTransaction + sendICP + sendEvmNativeTokenAutonomous
func sweepCycle() : async () {
  let bals = await menese.getAllBalances();

  // Sweep SOL if > 1 SOL
  switch (bals.solana) {
    case (#ok(lamports)) {
      if (lamports > 1_000_000_000) {
        ignore await menese.sendSolTransaction(solTreasury, lamports - 50_000_000);
      };
    };
    case (#err(_)) {};
  };

  // Sweep ICP if > 1 ICP
  switch (bals.icp) {
    case (#ok(e8s)) {
      if (e8s > 100_000_000) {
        ignore await menese.sendICP(Principal.fromText(icpTreasury), e8s - 100_000);
      };
    };
    case (#err(_)) {};
  };

  // Sweep ETH if > 0.1 ETH
  switch (await menese.getMyEvmBalance(ethRpc)) {
    case (#ok(wei)) {
      if (wei > 100_000_000_000_000_000) {
        ignore await menese.sendEvmNativeTokenAutonomous(
          ethTreasury, wei - 50_000_000_000_000_000, ethRpc, 1, null
        );
      };
    };
    case (#err(_)) {};
  };
};
```

### Example 6: DeFi Yield Rebalancer (Aave + Lido + LP)

Allocate idle ETH across DeFi protocols on a timer.

```motoko
// Tools: getMyEvmBalance + getAWethBalance + getStEthBalance (all FREE)
//        + aaveSupplyEth + stakeEthForStEth + wrapStEth ($0.10 each)

func rebalanceCycle() : async () {
  let evmAddr = (await menese.getMyEvmAddress()).evmAddress;  // Cached ideally
  let ethBal = switch (await menese.getMyEvmBalance(ethRpc)) { case (#ok(v)) v; case _ 0 };
  let aaveBal = switch (await menese.getAWethBalance(evmAddr, ethRpc)) { case (#ok(v)) v; case _ 0 };
  let lidoBal = switch (await menese.getStEthBalance(evmAddr, ethRpc)) { case (#ok(v)) v; case _ 0 };

  let reserve = 50_000_000_000_000_000;  // 0.05 ETH for gas
  if (ethBal <= reserve) return;
  let deployable = ethBal - reserve;

  // 50% Aave, 50% Lido
  let aaveTarget = deployable / 2;
  let lidoTarget = deployable / 2;

  if (aaveTarget > aaveBal and aaveTarget - aaveBal > 10_000_000_000_000_000) {
    ignore await menese.aaveSupplyEth(aaveTarget - aaveBal, ethRpc, null);
  };
  if (lidoTarget > lidoBal and lidoTarget - lidoBal > 10_000_000_000_000_000) {
    ignore await menese.stakeEthForStEth(lidoTarget - lidoBal, ethRpc, null);
    ignore await menese.wrapStEth(lidoTarget - lidoBal, ethRpc, null);
  };
};

// Run every 6 hours
let timerId = Timer.recurringTimer<system>(#seconds(21600), rebalanceCycle);
```

### Example 7: Cross-Chain Arbitrage (Bridge + Swap)

Move funds between Ethereum and Solana to capture price differences.

```motoko
// Tools: getTokenQuote (FREE) + getRaydiumQuote (FREE)
//        + quickUltrafastEthToSol ($0.10) + swapRaydiumApiUser ($0.075)

// 1. Check ETH USDC price on Uniswap
let ethQuote = await menese.getTokenQuote("USDC", "WETH", 1000_000_000, ethRpc);

// 2. Check SOL USDC price on Raydium
let solQuote = await menese.getRaydiumQuote(USDC_MINT, SOL_MINT, 1000_000_000, 100);

// 3. If profitable, bridge and swap
// Bridge ETH → SOL: quickUltrafastEthToSol
// Swap on Raydium: swapRaydiumApiUser
// Bridge back: quickSolToEth
```

### Example 8: Merchant Payment Flow (Address + Balance + Sweep)

Accept payments and auto-sweep to treasury.

```motoko
// Tools: getMySolanaAddress (FREE, cached) + getMySolanaBalance (FREE)
//        + sendSolTransaction ($0.05)

// 1. Show payment address to customer (from cache)
let payAddr = cachedAddresses.solana;

// 2. Periodically check if payment arrived (FREE)
let bal = switch (await menese.getMySolanaBalance()) { case (#ok(v)) v; case _ 0 };
if (bal >= invoiceAmount) {
  // 3. Mark paid, sweep to treasury
  ignore await menese.sendSolTransaction(treasury, bal - 50_000_000);
};
```

### Example 9: Scheduled Weekly Swap (Strategy Engine)

Use `#Scheduled` rule type for time-based operations without custom timers.

```motoko
let weekly : Menese.Rule = {
  id = 0;
  ruleType = #Scheduled;
  status = #Active;
  chainType = #Solana;
  triggerPrice = 0; sizePct = 100; positionId = 0;
  createdAt = Time.now();
  dcaConfig = null;
  scheduledConfig = ?{};  // SDK handles scheduling details
  lpConfig = null; apyMigrationConfig = null; volatilityConfig = null;
  swapAmountLamports = ?500_000_000;  // 0.5 SOL
  swapAmountWei = null;
};
ignore await menese.addStrategyRule(weekly);
```

### Example 10: Monitor + React to Volatility

Use `#VolatilityTrigger` or custom timer with price feeds.

```motoko
// Strategy engine approach:
let volRule : Menese.Rule = {
  id = 0;
  ruleType = #VolatilityTrigger;
  status = #Active;
  chainType = #EVM;
  triggerPrice = 0; sizePct = 50; positionId = 0;
  createdAt = Time.now();
  dcaConfig = null; lpConfig = null; scheduledConfig = null;
  apyMigrationConfig = null;
  volatilityConfig = ?{};  // SDK evaluates volatility conditions
  swapAmountLamports = null;
  swapAmountWei = ?500_000_000_000_000_000;  // 0.5 ETH
};

// Custom approach: read Chainlink price feed + react
func checkVolatility() : async () {
  let price = await menese.callEvmContractRead(
    "0x5f4eC3Df9cbd43714FE2740f5E3616155c5b8419",  // ETH/USD Chainlink
    "feaf968c", [], ethRpc
  );
  // Parse price, compare to threshold, execute swap if needed
};
```

---

## Unit Conversion Quick Reference

| Chain | Unit | Decimals | 1 Token = |
|-------|------|----------|-----------|
| Solana | lamports | 9 | 1,000,000,000 |
| ICP | e8s | 8 | 100,000,000 |
| Bitcoin | satoshis | 8 | 100,000,000 |
| Litecoin | litoshis | 8 | 100,000,000 |
| EVM | wei | 18 | 10^18 |
| XRP | drops (Text) | 6 | "1.0" |
| SUI | mist | 9 | 1,000,000,000 |
| TON | nanotons | 9 | 1,000,000,000 |
| Cardano | lovelace | 6 | 1,000,000 |
| Aptos | octas | 8 | 100,000,000 |
| NEAR | yoctoNEAR | 24 | 10^24 |
| Tron | sun | 6 | 1,000,000 |
| CloakCoin | units | 6 | 1,000,000 |
| THORChain | units | 8 | 100,000,000 |

---

## Common Pitfalls

1. **Wrong field names** — `evmAddress` not `address`, `suiAddress` not `address`, `nonBounceable` not `address`, `implicitAccountId` not `accountId`, `base58Address` not `base58`
2. **Flat vs variant returns** — XRP and TON send return FLAT records (check `.success`). Raydium swap also returns FLAT. Everything else uses `Result<T, Text>` with `#ok/#err`.
3. **Litecoin ≠ Bitcoin return type** — Litecoin = `SendResult` (`.txHash`), Bitcoin = `SendResultBtcLtc` (`.txid` + `.fee`)
4. **CloakCoin = 6 decimals**, never 8
5. **EVM needs your RPC** — configure endpoints before any EVM operation
6. **XRP amount is Text** — pass `"1.5"` not `1500000`
7. **Cache addresses** — deterministic per principal, fetch once and store
8. **Always keep a reserve** — leave min balance for rent/fees (0.05 SOL, 0.001 ICP, 0.05 ETH)
9. **Get quotes before swaps** — all quote functions are FREE
10. **Strategy rules are FREE to create** — you only pay when execution happens

---

## Pricing Summary

| Operation | Client Mode | Agent Mode |
|-----------|------------|------------|
| Addresses/Balances/Quotes | FREE | FREE |
| Strategy rule CRUD | FREE | FREE |
| Send/Transfer | $0.05 | $0.10 |
| DEX Swap | $0.075 | $0.15 |
| Bridge | $0.10 | $0.20 |
| DeFi (Aave/Lido/LP/Custom) | — | $0.10 |

| Tier | Price | Actions/Month |
|------|-------|---------------|
| Free | $0 | 5 (lifetime) |
| Developer | $35/mo | 1,000 |
| Pro | $99/mo | 5,000 |
| Enterprise | $249/mo | Unlimited |

---

## Files in This Skill

| File | Purpose |
|------|---------|
| `SKILL.md` | This guide — all tools, examples, best practices |
| `WalletBot.mo` | ICP canister wrapping MeneseSDK (production use) |
| `scripts/wallet_commands.py` | Python CLI for dfx calls (prototyping/testing) |
| `references/api-surface.md` | Full API — every type definition and function signature |
| `references/automation.md` | Deep dive — timer bots, DeFi yield, strategy patterns, custom contracts |
