#!/usr/bin/env node
const {
  PublicKey,
  decodeEngineConfig,
  decodeOrder,
  decodeUserMargin,
  deriveEngineConfigPda,
  deriveUserMarginPda,
  getConnection,
  orderStatusName,
  orderTypeName,
  parseArgs,
  programIdsFromEnv,
  readSigner,
  sideName
} = require("./common");
const { getAssociatedTokenAddressSync, TOKEN_PROGRAM_ID } = require("@solana/spl-token");

function usage() {
  console.log(`Usage:
  node scripts/balance.js
  node scripts/balance.js --json

Optional env:
  SOLANA_RPC_URL or ANCHOR_PROVIDER_URL
  KEYPAIR_PATH or ANCHOR_WALLET
  ORDER_ENGINE_PROGRAM_ID
  MARKET_REGISTRY_PROGRAM_ID
`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  if (args.help) {
    usage();
    return;
  }

  const { signer, keypairPath } = readSigner();
  const { connection, rpc } = getConnection();
  const { orderEngine } = programIdsFromEnv();

  const engineConfigPda = deriveEngineConfigPda(orderEngine);
  const userMarginPda = deriveUserMarginPda(signer.publicKey, orderEngine);

  const engineConfigInfo = await connection.getAccountInfo(engineConfigPda);
  if (!engineConfigInfo) {
    throw new Error(`Engine config not found: ${engineConfigPda.toBase58()}`);
  }
  const engineConfig = decodeEngineConfig(engineConfigInfo.data);

  const userMarginInfo = await connection.getAccountInfo(userMarginPda);
  const userMargin = userMarginInfo ? decodeUserMargin(userMarginInfo.data) : null;

  const usdcAta = getAssociatedTokenAddressSync(
    engineConfig.usdcMint,
    signer.publicKey,
    false,
    TOKEN_PROGRAM_ID
  );
  const usdcAtaInfo = await connection.getAccountInfo(usdcAta);
  const usdcBalance = usdcAtaInfo
    ? await connection.getTokenAccountBalance(usdcAta)
    : null;

  const solLamports = await connection.getBalance(signer.publicKey, "confirmed");

  const orderAccounts = await connection.getProgramAccounts(orderEngine, {
    filters: [
      {
        memcmp: {
          offset: 16,
          bytes: userMarginPda.toBase58()
        }
      }
    ]
  });

  const decodedOrders = [];
  for (const account of orderAccounts) {
    try {
      decodedOrders.push(decodeOrder(account.account.data, account.pubkey));
    } catch (_ignored) {
    }
  }

  decodedOrders.sort((a, b) => (a.id > b.id ? -1 : 1));

  const openOrders = decodedOrders.filter((order) => order.status === 0);

  if (args.json) {
    const payload = {
      rpc,
      keypairPath,
      wallet: signer.publicKey.toBase58(),
      engineConfig: engineConfigPda.toBase58(),
      userMargin: userMarginPda.toBase58(),
      usdcMint: engineConfig.usdcMint.toBase58(),
      usdcAta: usdcAta.toBase58(),
      balances: {
        solLamports: solLamports.toString(),
        usdcRawAmount: usdcBalance ? usdcBalance.value.amount : "0",
        usdcUiAmount: usdcBalance ? usdcBalance.value.uiAmountString : "0",
        collateralRawAmount: userMargin ? userMargin.collateralBalance.toString() : "0"
      },
      orders: {
        total: decodedOrders.length,
        open: openOrders.length,
        items: decodedOrders.map((order) => ({
          pubkey: order.pubkey.toBase58(),
          id: order.id.toString(),
          marketId: order.marketId.toString(),
          side: sideName(order.side),
          orderType: orderTypeName(order.orderType),
          reduceOnly: order.reduceOnly,
          margin: order.margin.toString(),
          price: order.price.toString(),
          status: orderStatusName(order.status),
          clientOrderId: order.clientOrderId.toString()
        }))
      }
    };
    console.log(JSON.stringify(payload, null, 2));
    return;
  }

  console.log(`rpc: ${rpc}`);
  console.log(`signer: ${signer.publicKey.toBase58()}`);
  console.log(`keypair: ${keypairPath}`);
  console.log(`engine_config: ${engineConfigPda.toBase58()}`);
  console.log(`user_margin: ${userMarginPda.toBase58()}`);
  console.log(`usdc_mint: ${engineConfig.usdcMint.toBase58()}`);
  console.log(`usdc_ata: ${usdcAta.toBase58()}`);
  console.log(`sol: ${solLamports} lamports`);
  console.log(
    `usdc: ${usdcBalance ? usdcBalance.value.amount : "0"} raw (${usdcBalance ? usdcBalance.value.uiAmountString : "0"} UI)`
  );

  if (!userMargin) {
    console.log("margin_account: not initialized");
  } else {
    console.log(`collateral_balance: ${userMargin.collateralBalance.toString()}`);
    console.log(`next_order_nonce: ${userMargin.nextOrderNonce.toString()}`);
    console.log(`total_notional: ${userMargin.totalNotional.toString()}`);
  }

  console.log(`orders: total=${decodedOrders.length}, open=${openOrders.length}`);
  for (const order of openOrders.slice(0, 20)) {
    console.log(
      `- id=${order.id.toString()} market=${order.marketId.toString()} side=${sideName(order.side)} type=${orderTypeName(order.orderType)} margin=${order.margin.toString()} price=${order.price.toString()} status=${orderStatusName(order.status)} pubkey=${order.pubkey.toBase58()}`
    );
  }
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
