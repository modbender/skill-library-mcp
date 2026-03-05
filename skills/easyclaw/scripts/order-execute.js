#!/usr/bin/env node
const {
  DISCRIMINATORS,
  SystemProgram,
  TOKEN_PROGRAM_ID,
  decodeEngineConfig,
  decodeUserMargin,
  deriveEngineConfigPda,
  deriveGlobalConfigPda,
  deriveMarketPda,
  deriveOrderPda,
  deriveUserMarginPda,
  deriveUserMarketPositionPda,
  ensureAtaExists,
  getConnection,
  instruction,
  orderData,
  parseArgs,
  programIdsFromEnv,
  readSigner,
  sendInstructions,
  usageNumberToBigInt,
  u64Le
} = require("./common");

function usage() {
  console.log(`Usage:
  node scripts/order-execute.js --market-id 1 --side buy --type market --margin 1000000
  node scripts/order-execute.js --market-id 2 --side sell --type limit --margin 2000000 --price 3000000000
  node scripts/order-execute.js --market-id 1 --side buy --type market --margin 1000000 --deposit 5000000

Options:
  --market-id <u64>          Required
  --side <buy|sell>          Default: buy
  --type <market|limit>      Default: market
  --margin <u64>             Required, collateral amount for the order
  --price <u64>              Required for limit; optional for market
  --ttl <i64>                Default: 300
  --client-order-id <u64>    Default: current unix seconds
  --reduce-only              Optional flag
  --deposit <u64>            Optional collateral deposit before placing order
  --skip-create-position     Skip auto-creation of user market position PDA
`);
}

function sideToIndex(value) {
  const normalized = String(value).toLowerCase();
  if (normalized === "buy") return 0;
  if (normalized === "sell") return 1;
  throw new Error(`Invalid --side: ${value}`);
}

function typeToIndex(value) {
  const normalized = String(value).toLowerCase();
  if (normalized === "market") return 0;
  if (normalized === "limit") return 1;
  throw new Error(`Invalid --type: ${value}`);
}

function defaultMarketPrice(sideIndex) {
  if (sideIndex === 0) {
    return 100_000_000_000n;
  }
  return 1n;
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return;
  }

  if (!args["market-id"]) {
    throw new Error("--market-id is required");
  }
  if (!args.margin) {
    throw new Error("--margin is required");
  }

  const marketId = usageNumberToBigInt("market-id", args["market-id"]);
  const side = sideToIndex(args.side || "buy");
  const orderType = typeToIndex(args.type || "market");
  const margin = usageNumberToBigInt("margin", args.margin);
  const ttlSecs = args.ttl ? BigInt(args.ttl) : 300n;
  const clientOrderId = args["client-order-id"]
    ? usageNumberToBigInt("client-order-id", args["client-order-id"])
    : BigInt(Math.floor(Date.now() / 1000));
  const reduceOnly = Boolean(args["reduce-only"]);
  const depositAmount = args.deposit
    ? usageNumberToBigInt("deposit", args.deposit)
    : 0n;
  const skipCreatePosition = Boolean(args["skip-create-position"]);

  const price = args.price
    ? usageNumberToBigInt("price", args.price)
    : defaultMarketPrice(side);

  if (orderType === 1 && price <= 0n) {
    throw new Error("--price must be > 0 for limit orders");
  }

  const { signer, keypairPath } = readSigner();
  const { connection, rpc } = getConnection();
  const { orderEngine, marketRegistry } = programIdsFromEnv();

  const engineConfigPda = deriveEngineConfigPda(orderEngine);
  const globalConfigPda = deriveGlobalConfigPda(marketRegistry);
  const marketPda = deriveMarketPda(marketId, marketRegistry);
  const userMarginPda = deriveUserMarginPda(signer.publicKey, orderEngine);
  const userMarketPositionPda = deriveUserMarketPositionPda(
    userMarginPda,
    marketId,
    orderEngine
  );

  const engineConfigInfo = await connection.getAccountInfo(engineConfigPda);
  if (!engineConfigInfo) {
    throw new Error(`Engine config not found: ${engineConfigPda.toBase58()}`);
  }
  const engineConfig = decodeEngineConfig(engineConfigInfo.data);

  const setupInstructions = [];

  const userMarginInfo = await connection.getAccountInfo(userMarginPda);
  if (!userMarginInfo) {
    setupInstructions.push(
      instruction(
        orderEngine,
        [
          { pubkey: signer.publicKey, isSigner: true, isWritable: true },
          { pubkey: engineConfigPda, isSigner: false, isWritable: false },
          { pubkey: userMarginPda, isSigner: false, isWritable: true },
          { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }
        ],
        DISCRIMINATORS.CREATE_MARGIN_ACCOUNT
      )
    );
  }

  if (!skipCreatePosition) {
    const userMarketPositionInfo = await connection.getAccountInfo(
      userMarketPositionPda
    );
    if (!userMarketPositionInfo) {
      setupInstructions.push(
        instruction(
          orderEngine,
          [
            { pubkey: signer.publicKey, isSigner: true, isWritable: true },
            { pubkey: engineConfigPda, isSigner: false, isWritable: false },
            { pubkey: userMarginPda, isSigner: false, isWritable: true },
            { pubkey: userMarketPositionPda, isSigner: false, isWritable: true },
            { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }
          ],
          Buffer.concat([
            DISCRIMINATORS.CREATE_USER_MARKET_POSITION,
            u64Le(marketId)
          ])
        )
      );
    }
  }

  const { ata: userUsdcAta, createInstruction: createAtaIx } =
    await ensureAtaExists(connection, signer, signer.publicKey, engineConfig.usdcMint);
  if (createAtaIx) {
    setupInstructions.push(createAtaIx);
  }

  if (depositAmount > 0n) {
    setupInstructions.push(
      instruction(
        orderEngine,
        [
          { pubkey: signer.publicKey, isSigner: true, isWritable: true },
          { pubkey: engineConfigPda, isSigner: false, isWritable: false },
          { pubkey: userMarginPda, isSigner: false, isWritable: true },
          { pubkey: userUsdcAta, isSigner: false, isWritable: true },
          { pubkey: engineConfig.collateralVault, isSigner: false, isWritable: true },
          { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false }
        ],
        Buffer.concat([DISCRIMINATORS.DEPOSIT_COLLATERAL, u64Le(depositAmount)])
      )
    );
  }

  const setupSig = await sendInstructions(connection, signer, setupInstructions);
  if (setupSig) {
    console.log(`[ok] setup_tx: ${setupSig}`);
  }

  const refreshedUserMarginInfo = await connection.getAccountInfo(userMarginPda);
  if (!refreshedUserMarginInfo) {
    throw new Error("User margin account is still missing after setup");
  }
  const userMargin = decodeUserMargin(refreshedUserMarginInfo.data);
  const orderPda = deriveOrderPda(userMarginPda, userMargin.nextOrderNonce, orderEngine);

  const placeIx = instruction(
    orderEngine,
    [
      { pubkey: signer.publicKey, isSigner: true, isWritable: true },
      { pubkey: engineConfigPda, isSigner: false, isWritable: false },
      { pubkey: marketRegistry, isSigner: false, isWritable: false },
      { pubkey: globalConfigPda, isSigner: false, isWritable: false },
      { pubkey: marketPda, isSigner: false, isWritable: false },
      { pubkey: userMarginPda, isSigner: false, isWritable: true },
      { pubkey: orderPda, isSigner: false, isWritable: true },
      { pubkey: SystemProgram.programId, isSigner: false, isWritable: false }
    ],
    orderData({
      marketId,
      side,
      orderType,
      reduceOnly,
      margin,
      price,
      ttlSecs,
      clientOrderId
    })
  );

  const placeSig = await sendInstructions(connection, signer, [placeIx]);
  console.log(`[ok] place_order: ${placeSig}`);
  console.log(`rpc: ${rpc}`);
  console.log(`keypair: ${keypairPath}`);
  console.log(`wallet: ${signer.publicKey.toBase58()}`);
  console.log(`market_id: ${marketId.toString()}`);
  console.log(`order_pda: ${orderPda.toBase58()}`);
  console.log(`order_nonce: ${userMargin.nextOrderNonce.toString()}`);
  console.log(`side: ${side === 0 ? "buy" : "sell"}`);
  console.log(`type: ${orderType === 0 ? "market" : "limit"}`);
  console.log(`margin: ${margin.toString()}`);
  console.log(`price: ${price.toString()}`);
}

main().catch((error) => {
  const message = error instanceof Error ? error.message : String(error);
  if (message.includes("fetch failed")) {
    console.error(`[error] RPC connection failed: ${message}`);
    console.error(
      "[hint] Set SOLANA_RPC_URL (or ANCHOR_PROVIDER_URL) to a reachable Solana RPC endpoint."
    );
  } else {
    console.error(error);
  }
  process.exit(1);
});
