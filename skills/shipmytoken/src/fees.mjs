import {
  Connection,
  Keypair,
  PublicKey,
  TransactionMessage,
  VersionedTransaction,
  ComputeBudgetProgram,
} from "@solana/web3.js";
import bs58 from "bs58";
import { readTokenHistory, writeTokenHistory, getKey } from "./config.mjs";

const SHIPMYTOKEN_WALLET = new PublicKey("7Z9vCDFzwe2DsTq4zvmrurScehUYAgUifiycgD6ZYa6T");
const RPC_URL = process.env.SOLANA_RPC_URL || "https://api.mainnet-beta.solana.com";

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith("--")) {
      const key = argv[i].slice(2);
      const next = argv[i + 1];
      if (next && !next.startsWith("--")) {
        args[key] = next;
        i++;
      } else {
        args[key] = true;
      }
    }
  }
  return args;
}

async function claimFees(wallet, connection) {
  const { OnlinePumpSdk } = await import("@pump-fun/pump-sdk");
  const sdk = new OnlinePumpSdk(connection);

  const history = await readTokenHistory();
  if (history.tokens.length === 0) {
    console.log(JSON.stringify({ success: true, action: "claim", claimed: [], message: "No tokens found." }));
    return;
  }

  const results = [];

  for (const token of history.tokens) {
    if (!token.feeSharingConfigured) {
      results.push({
        name: token.name,
        symbol: token.symbol,
        mint: token.mint,
        skipped: true,
        reason: "Fee sharing not configured. 100% of creator fees go directly to the creator wallet.",
      });
      continue;
    }

    const mint = new PublicKey(token.mint);

    try {
      const feeResult = await sdk.getMinimumDistributableFee(mint);

      if (!feeResult.canDistribute) {
        results.push({
          name: token.name,
          symbol: token.symbol,
          mint: token.mint,
          skipped: true,
          reason: `Below minimum distributable fee (need ${feeResult.minimumRequired.toNumber() / 1e9} SOL, have ${feeResult.distributableFees.toNumber() / 1e9} SOL)`,
        });
        continue;
      }

      const { instructions, isGraduated } = await sdk.buildDistributeCreatorFeesInstructions(mint);

      const allInstructions = [
        ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
        ...(Array.isArray(instructions) ? instructions : [instructions]),
      ];

      const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("confirmed");
      const message = new TransactionMessage({
        payerKey: wallet.publicKey,
        recentBlockhash: blockhash,
        instructions: allInstructions,
      }).compileToV0Message();

      const tx = new VersionedTransaction(message);
      tx.sign([wallet]);

      const signature = await connection.sendTransaction(tx, { skipPreflight: false });
      await connection.confirmTransaction(
        { signature, blockhash, lastValidBlockHeight },
        "confirmed"
      );

      results.push({
        name: token.name,
        symbol: token.symbol,
        mint: token.mint,
        claimed: true,
        isGraduated,
        signature,
      });
    } catch (err) {
      results.push({
        name: token.name,
        symbol: token.symbol,
        mint: token.mint,
        claimed: false,
        error: err.message,
      });
    }
  }

  console.log(JSON.stringify({ success: true, action: "claim", results }));
}

async function updateShares(wallet, connection, args) {
  const mintAddress = args.mint;
  const sharesStr = args.shares;

  if (!mintAddress || !sharesStr) {
    console.log(JSON.stringify({
      success: false,
      error: "Usage: --update --mint <mint_address> --shares \"creator:6000,ABC:3000\""
    }));
    process.exit(1);
  }

  // Parse shares
  const entries = sharesStr.split(",").map((s) => {
    const [address, bps] = s.trim().split(":");
    return { address: address.trim(), shareBps: parseInt(bps, 10) };
  });

  // Add SHIP MY TOKEN's 10% if not already included
  const smtEntry = entries.find((e) => e.address === SHIPMYTOKEN_WALLET.toBase58());
  if (!smtEntry) {
    entries.push({ address: SHIPMYTOKEN_WALLET.toBase58(), shareBps: 1000 });
  } else if (smtEntry.shareBps < 1000) {
    console.log(JSON.stringify({
      success: false,
      error: "SHIP MY TOKEN must retain at least 10% (1000 bps)."
    }));
    process.exit(1);
  }

  // Validate
  const total = entries.reduce((sum, e) => sum + e.shareBps, 0);
  if (total !== 10000) {
    console.log(JSON.stringify({
      success: false,
      error: `Shares must sum to 10000 bps. Current total: ${total}`
    }));
    process.exit(1);
  }

  if (entries.length > 10) {
    console.log(JSON.stringify({
      success: false,
      error: `Maximum 10 shareholders allowed. Got ${entries.length}.`
    }));
    process.exit(1);
  }

  const history = await readTokenHistory();
  const token = history.tokens.find((t) => t.mint === mintAddress);
  if (!token) {
    console.log(JSON.stringify({ success: false, error: `Token ${mintAddress} not found in history.` }));
    process.exit(1);
  }

  const { PumpSdk } = await import("@pump-fun/pump-sdk");
  const sdk = new PumpSdk();

  const currentShareholders = (token.shareholders || []).map((s) => new PublicKey(s.address));
  const newShareholders = entries.map((e) => ({
    address: new PublicKey(e.address),
    shareBps: e.shareBps,
  }));

  const ix = await sdk.updateFeeShares({
    authority: wallet.publicKey,
    mint: new PublicKey(mintAddress),
    currentShareholders,
    newShareholders,
  });

  const instructions = [
    ComputeBudgetProgram.setComputeUnitPrice({ microLamports: 100_000 }),
    ...(Array.isArray(ix) ? ix : [ix]),
  ];

  const { blockhash, lastValidBlockHeight } = await connection.getLatestBlockhash("confirmed");
  const message = new TransactionMessage({
    payerKey: wallet.publicKey,
    recentBlockhash: blockhash,
    instructions,
  }).compileToV0Message();

  const tx = new VersionedTransaction(message);
  tx.sign([wallet]);

  const signature = await connection.sendTransaction(tx, { skipPreflight: false });
  await connection.confirmTransaction(
    { signature, blockhash, lastValidBlockHeight },
    "confirmed"
  );

  // Update history
  token.shareholders = entries.map((e) => ({
    address: e.address,
    shareBps: e.shareBps,
    label: e.address === SHIPMYTOKEN_WALLET.toBase58() ? "shipmytoken" : undefined,
  }));
  await writeTokenHistory(history);

  console.log(JSON.stringify({
    success: true,
    action: "update_shares",
    mint: mintAddress,
    shareholders: token.shareholders,
    signature,
  }));
}

async function main() {
  const args = parseArgs(process.argv.slice(2));

  const privateKey = await getKey("SOLANA_PRIVATE_KEY");
  if (!privateKey) {
    console.log(JSON.stringify({ success: false, error: "SOLANA_PRIVATE_KEY not set. Run setup first." }));
    process.exit(1);
  }

  const wallet = Keypair.fromSecretKey(bs58.decode(privateKey));
  const connection = new Connection(RPC_URL, "confirmed");

  if (args.claim) {
    await claimFees(wallet, connection);
  } else if (args.update) {
    await updateShares(wallet, connection, args);
  } else {
    console.log(JSON.stringify({
      success: false,
      error: "Usage: --claim | --update --mint <mint> --shares \"addr:bps,...\""
    }));
    process.exit(1);
  }
}

main().catch((err) => {
  console.log(JSON.stringify({ success: false, error: err.message }));
  process.exit(1);
});
