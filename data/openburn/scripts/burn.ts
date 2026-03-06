import {
  Connection,
  Keypair,
  PublicKey,
  Transaction,
  VersionedTransaction,
  sendAndConfirmTransaction,
  LAMPORTS_PER_SOL,
} from "@solana/web3.js";
import {
  getAssociatedTokenAddress,
  createBurnInstruction,
  getAccount,
  getMint,
  TOKEN_PROGRAM_ID,
  TOKEN_2022_PROGRAM_ID,
} from "@solana/spl-token";
import PumpSdk from "@pump-fun/pump-sdk";
import dotenv from "dotenv";
import BN from "bn.js";

const { OnlinePumpSdk, PUMP_SDK } = PumpSdk;
import path from "path";
import bs58 from "bs58";

// Load environment variables from the root .env file
dotenv.config({ path: path.resolve(process.cwd(), ".env") });

// API URL for reporting burn transactions
const API_URL = "https://api.openburn.fun";

// Jupiter API endpoint
const JUPITER_API_URL = "https://lite-api.jup.ag/swap/v1";

// Solana native mint (SOL)
const SOL_MINT = new PublicKey("So11111111111111111111111111111111111111112");

// Solana burn address (incinerator)
const BURN_ADDRESS = new PublicKey("1nc1nerator11111111111111111111111111111111");

// Get quote from Jupiter
async function getJupiterQuote(
  inputMint: string,
  outputMint: string,
  amount: number,
  slippageBps: number = 100 // 1% slippage
) {
  const params = new URLSearchParams({
    inputMint,
    outputMint,
    amount: amount.toString(),
    slippageBps: slippageBps.toString(),
  });

  const response = await fetch(`${JUPITER_API_URL}/quote?${params}`, {
    headers: {
      "x-api-key": process.env.JUPITER_API_KEY || "",
    },
  });
  if (!response.ok) {
    throw new Error(`Jupiter quote failed: ${response.status} ${response.statusText} - Ensure JUPITER_API_KEY is set`);
  }

  return await response.json();
}

// Get swap transaction from Jupiter
async function getJupiterSwapTransaction(
  quoteResponse: any,
  userPublicKey: string,
  wrapUnwrapSOL: boolean = true
) {
  const response = await fetch(`${JUPITER_API_URL}/swap`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": process.env.JUPITER_API_KEY || "",
    },
    body: JSON.stringify({
      quoteResponse,
      userPublicKey,
      wrapAndUnwrapSol: wrapUnwrapSOL,
      dynamicComputeUnitLimit: true,
      prioritizationFeeLamports: "auto",
    }),
  });

  if (!response.ok) {
    throw new Error(`Jupiter swap transaction failed: ${response.status} ${response.statusText} - Ensure JUPITER_API_KEY is set`);
  }

  return await response.json();
}

// Helper to post data to API
async function postToApi(endpoint: string, data: any) {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
        console.error(`Failed to post to API: ${response.status} ${response.statusText}`);
    } else {
        console.log(`Successfully reported to API: ${endpoint}`);
    }
  } catch (error) {
    console.error("Error posting to API:", error);
  }
}

async function main() {
  const privateKeyString = process.env.CREATOR_WALLET_PRIVATE_KEY;
  const tokenAddressString = process.env.PUMP_FUN_TOKEN_ADDRESS;
  const burnPercentageStr = process.env.BURN_PERCENTAGE || "80";
  const minFeeToBurnStr = process.env.MIN_FEE_TO_BURN || "0.1";

  if (!privateKeyString) {
    console.error("Error: CREATOR_WALLET_PRIVATE_KEY is not set in .env");
    process.exit(1);
  }

  if (!tokenAddressString) {
    console.error("Error: PUMP_FUN_TOKEN_ADDRESS is not set in .env");
    process.exit(1);
  }

  const burnPercentage = parseFloat(burnPercentageStr);
  if (isNaN(burnPercentage) || burnPercentage <= 0 || burnPercentage > 100) {
      console.error(`Error: Invalid BURN_PERCENTAGE: ${burnPercentageStr}. Must be between 0 and 100.`);
      process.exit(1);
  }

  const minFeeToBurn = parseFloat(minFeeToBurnStr);
  if (isNaN(minFeeToBurn) || minFeeToBurn < 0) {
      console.error(`Error: Invalid MIN_FEE_TO_BURN: ${minFeeToBurnStr}. Must be a positive number.`);
      process.exit(1);
  }

  let tokenMint: PublicKey;
  let tokenProgramId: PublicKey;
  try {
    tokenMint = new PublicKey(tokenAddressString);
  } catch (e) {
      console.error("Invalid PUMP_FUN_TOKEN_ADDRESS");
      process.exit(1);
  }

  const connection = new Connection("https://api.mainnet-beta.solana.com", "confirmed");

  // Detect Token Program ID
  try {
    const mintInfo = await connection.getAccountInfo(tokenMint);
    if (!mintInfo) {
      console.error("Error: Could not fetch token mint info. Check if the address is correct.");
      process.exit(1);
    }
    tokenProgramId = mintInfo.owner;
    console.log(`Detected Token Program: ${tokenProgramId.toBase58()}`);
    
    // Verify it's a known token program
    if (!tokenProgramId.equals(TOKEN_PROGRAM_ID) && !tokenProgramId.equals(TOKEN_2022_PROGRAM_ID)) {
        console.warn("Warning: Token mint owner is not a known Token Program (Standard or Token-2022).");
    }
  } catch (e) {
      console.error("Error detecting token program:", e);
      process.exit(1);
  }

  // Fetch Token Decimals
  let tokenDecimals = 6; // Default to 6
  try {
      const mintData = await getMint(connection, tokenMint, "confirmed", tokenProgramId);
      tokenDecimals = mintData.decimals;
      console.log(`Token Decimals: ${tokenDecimals}`);
  } catch (e) {
      console.warn(`Could not fetch mint data for decimals, defaulting to 6. Error: ${e}`);
  }

  // Decode private key
  let secretKey: Uint8Array;
  try {
    if (privateKeyString.startsWith("[") && privateKeyString.endsWith("]")) {
      secretKey = Uint8Array.from(JSON.parse(privateKeyString));
    } else {
      // Try Base58 decoding
      secretKey = bs58.decode(privateKeyString);
    }
  } catch (e) {
    const errorMsg = "Error parsing private key. Ensure it is a JSON array of numbers.";
    console.error(errorMsg);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: errorMsg,
        tokenAddress: tokenAddressString
    });
    process.exit(1);
  }

  const payer = Keypair.fromSecretKey(secretKey);

  


  console.log(`Wallet Public Key: ${payer.publicKey.toBase58()}`);
  console.log(`Token Mint: ${tokenMint.toBase58()}`);
  console.log(`Burn Percentage: ${burnPercentage}%`);
  console.log(`Minimum Fee to Burn: ${minFeeToBurn} SOL`);

  // --- Step 1: Collect Creator Fees (Bonding Curve & Swap/AMM) ---
  let feeSignature: string | undefined;
  let solBalanceBeforeFees = 0;
  let solBalanceAfterFees = 0;
  let feesCollectedSol = 0;

  try {
    // Check SOL balance before fee collection
    solBalanceBeforeFees = await connection.getBalance(payer.publicKey);
    console.log(`SOL Balance Before Fee Collection: ${(solBalanceBeforeFees / LAMPORTS_PER_SOL).toFixed(6)} SOL`);

    console.log("\nInitializing Pump SDK and collecting creator fees (Bonding Curve + Swap/AMM)...");
    const sdk = new OnlinePumpSdk(connection);
    
    // collectCoinCreatorFeeInstructions aggregates instructions for both:
    // 1. Bonding Curve fee collection (Pump Program)
    // 2. AMM fee collection (Raydium/PumpSwap depending on SDK version)
    const feeInstructions = await sdk.collectCoinCreatorFeeInstructions(payer.publicKey, payer.publicKey);

    if (feeInstructions.length > 0) {
        console.log(`Generated ${feeInstructions.length} fee collection instructions.`);
        
        const feeTx = new Transaction().add(...feeInstructions);
        const feeSig = await sendAndConfirmTransaction(connection, feeTx, [payer]);
        console.log(`Fees collected successfully! Transaction: ${feeSig}`);
        feeSignature = feeSig;

        // Check balance after fee collection
        solBalanceAfterFees = await connection.getBalance(payer.publicKey);
        const feesCollected = solBalanceAfterFees - solBalanceBeforeFees;
        feesCollectedSol = feesCollected / LAMPORTS_PER_SOL;
        console.log(`SOL Balance After Fee Collection: ${(solBalanceAfterFees / LAMPORTS_PER_SOL).toFixed(6)} SOL`);
        console.log(`Fees Collected: ${feesCollectedSol.toFixed(6)} SOL`);

        // Check if fees meet minimum threshold
        if (feesCollectedSol < minFeeToBurn) {
            const msg = `Fees collected (${feesCollectedSol.toFixed(6)} SOL) are below minimum threshold (${minFeeToBurn} SOL). Skipping burn.`;
            console.log(msg);
            await postToApi("/api/burn/transaction", {
                status: "skipped",
                reason: "below_minimum_threshold",
                feesCollected: feesCollectedSol.toFixed(6),
                minFeeToBurn: minFeeToBurn.toString(),
                tokenAddress: tokenAddressString,
                wallet: payer.publicKey.toBase58()
            });
            return;
        }

        // Log claim to API
        await postToApi("/api/burn/claims", {
            signature: feeSig,
            feesCollected: feesCollectedSol.toFixed(6),
            feesCollectedLamports: feesCollected.toString(),
            tokenAddress: tokenAddressString,
            wallet: payer.publicKey.toBase58()
        });
    } else {
        console.log("No fee collection instructions generated (no unclaimed fees found).");
        solBalanceAfterFees = solBalanceBeforeFees;
    }
  } catch (feeError: any) {
    console.warn("Warning: Fee collection failed or no fees to collect.", feeError.message);
    
    await postToApi("/api/burn/transaction", {
        status: "warning",
        error: `Fee collection warning: ${feeError.message}`,
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58()
    });
    
    // Use current balance if fee collection failed
    solBalanceAfterFees = await connection.getBalance(payer.publicKey);
  }

  // --- Step 2: Buy Tokens with Collected SOL ---
  let buySignature: string | undefined;
  let tokensBought = BigInt(0);

  try {
    console.log("\n--- Buying Tokens ---");
    
    // Calculate SOL amount to use for buying (percentage of collected fees)
    // We assume the wallet is funded with enough SOL for gas, so we use all collected fees
    const availableForBuySol = feesCollectedSol;

    if (availableForBuySol <= 0) {
        const msg = "No SOL available to buy tokens (insufficient balance after reserving for fees).";
        console.log(msg);
        await postToApi("/api/burn/transaction", {
            status: "success",
            signature: feeSignature || "no-fees-collected",
            feeCollectionSignature: feeSignature,
            tokensBought: 0,
            tokensBurned: 0,
            tokenAddress: tokenAddressString,
            wallet: payer.publicKey.toBase58()
        });
        return;
    }

    // Apply burn percentage to determine how much SOL to use for buying
    const solAmountToBuySol = availableForBuySol * (burnPercentage / 100);
    const solAmountToBuyLamports = Math.floor(solAmountToBuySol * LAMPORTS_PER_SOL);
    console.log(`Using ${solAmountToBuySol.toFixed(6)} SOL (${burnPercentage}% of available) to buy tokens...`);

    // Initialize SDK and check token state
    const sdk = new OnlinePumpSdk(connection);
    const globalAccount = await sdk.fetchGlobal();
    
    // Get user's token account address
    const userTokenAccount = await getAssociatedTokenAddress(
      tokenMint, 
      payer.publicKey,
      false, 
      tokenProgramId
    );
    
    // Check token balance before buy
    let tokenBalanceBefore = BigInt(0);
    try {
      const accountBefore = await getAccount(connection, userTokenAccount, "confirmed", tokenProgramId);
      tokenBalanceBefore = accountBefore.amount;
    } catch (e) {
      // Token account doesn't exist yet, balance is 0
      console.log("Token account doesn't exist yet, will be created during buy");
    }

    // Fetch buy state (includes bonding curve and user token account info)
    const { bondingCurveAccountInfo, bondingCurve, associatedUserAccountInfo } = 
        await sdk.fetchBuyState(tokenMint, payer.publicKey, tokenProgramId);
    
    // Check if bonding curve is complete (token graduated to Raydium)
    if (bondingCurve.complete) {
        console.log("Token has graduated to Raydium. Using Jupiter DEX for swap...");
        
        // Get user's token account address
        const userTokenAccountT22 = await getAssociatedTokenAddress(
          tokenMint,
          payer.publicKey,
          false,
          tokenProgramId
        );

        // Check token balance before buy
        let tokenBalanceBeforeJupiter = BigInt(0);
        try {
          const accountBefore = await getAccount(connection, userTokenAccountT22, "confirmed", tokenProgramId);
          tokenBalanceBeforeJupiter = accountBefore.amount;
        } catch (e) {
          // Token account doesn't exist yet, balance is 0
          console.log("Token account doesn't exist yet, will be created during swap");
        }

        // Get quote from Jupiter
        console.log("Fetching quote from Jupiter...");
        const quoteResponse = await getJupiterQuote(
          SOL_MINT.toBase58(),
          tokenMint.toBase58(),
          solAmountToBuyLamports,
          100 // 1% slippage
        );

        console.log(`Quote received: ${quoteResponse.outAmount} tokens for ${solAmountToBuySol.toFixed(6)} SOL`);
        console.log(`Price impact: ${quoteResponse.priceImpactPct}%`);

        // Get swap transaction
        console.log("Getting swap transaction from Jupiter...");
        const swapResponse = await getJupiterSwapTransaction(quoteResponse, payer.publicKey.toBase58());

        // Deserialize and sign the transaction
        const swapTransactionBuf = Buffer.from(swapResponse.swapTransaction, "base64");
        const transaction = VersionedTransaction.deserialize(swapTransactionBuf);
        transaction.sign([payer]);

        // Send transaction
        console.log("Sending swap transaction...");
        const rawTransaction = transaction.serialize();
        const txid = await connection.sendRawTransaction(rawTransaction, {
          skipPreflight: true,
          maxRetries: 2,
        });

        // Confirm transaction
        console.log("Confirming transaction...");
        const confirmation = await connection.confirmTransaction(txid, "confirmed");

        if (confirmation.value.err) {
          throw new Error(`Transaction failed: ${JSON.stringify(confirmation.value.err)}`);
        }

        console.log(`Tokens bought successfully via Jupiter! Transaction: ${txid}`);
        buySignature = txid;

        // Get token balance after buy
        const tokenAccountAfter = await getAccount(connection, userTokenAccountT22, "confirmed", tokenProgramId);
        tokensBought = tokenAccountAfter.amount - tokenBalanceBeforeJupiter;
        console.log(`Tokens Bought: ${tokensBought.toString()}`);

    } else {
        // Token is still on bonding curve, use Pump.fun SDK
        console.log("Token is on bonding curve. Using Pump.fun SDK...");
        
        // Use SDK's buy method which handles bonded tokens
        const solAmountBN = new BN(solAmountToBuyLamports);
        
        // Calculate token amount based on bonding curve formula
        // k = virtualSolReserves * virtualTokenReserves
        // newSolReserves = virtualSolReserves + solAmount
        // newTokenReserves = k / newSolReserves
        // tokensToBuy = virtualTokenReserves - newTokenReserves
        
        const virtualSolReserves = new BN(bondingCurve.virtualSolReserves);
        const virtualTokenReserves = new BN(bondingCurve.virtualTokenReserves);
        
        const k = virtualSolReserves.mul(virtualTokenReserves);
        const newSolReserves = virtualSolReserves.add(solAmountBN);
        const newTokenReserves = k.div(newSolReserves);
        let tokensToBuy = virtualTokenReserves.sub(newTokenReserves);
        
        // Use 99% of the calculated tokens to allow for slippage/price movement
        // This ensures solAmountBN covers the cost even if price moves slightly up
        tokensToBuy = tokensToBuy.mul(new BN(99)).div(new BN(100));
        
        console.log(`Calculating tokens for ${solAmountToBuySol} SOL input...`);
        console.log(`Virtual SOL Reserves: ${virtualSolReserves.toString()}`);
        console.log(`Virtual Token Reserves: ${virtualTokenReserves.toString()}`);
        console.log(`Expected Tokens (with 1% slippage buffer): ${tokensToBuy.toString()}`);

        const tokenAmountBN = tokensToBuy;

        // Get buy instructions from PUMP_SDK singleton
        const buyInstructions = await PUMP_SDK.buyInstructions({
          global: globalAccount,
          bondingCurveAccountInfo,
          bondingCurve,
          associatedUserAccountInfo,
          mint: tokenMint,
          user: payer.publicKey,
          amount: tokenAmountBN,
          solAmount: solAmountBN,
          slippage: 10, // 10% slippage tolerance
          tokenProgram: tokenProgramId
        });

        console.log(`Generated ${buyInstructions.length} buy instructions`);

        const buyTx = new Transaction().add(...buyInstructions);
        const buySig = await sendAndConfirmTransaction(connection, buyTx, [payer]);
        console.log(`Tokens bought successfully! Transaction: ${buySig}`);
        buySignature = buySig;

        // Get token balance after buy
        const tokenAccountAfter = await getAccount(connection, userTokenAccount, "confirmed", tokenProgramId);
        tokensBought = tokenAccountAfter.amount - tokenBalanceBefore;
        console.log(`Tokens Bought: ${tokensBought.toString()}`);
    }

  } catch (buyError: any) {
    console.error("Error buying tokens:", buyError);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: `Token purchase failed: ${buyError.message}`,
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58(),
        feeCollectionSignature: feeSignature
    });
    process.exit(1);
  }

  // --- Step 3: Burn Purchased Tokens ---
  try {
    console.log("\n--- Burning Tokens ---");

    if (tokensBought === BigInt(0)) {
        console.log("No tokens to burn.");
        return;
    }

    const userTokenAccount = await getAssociatedTokenAddress(
      tokenMint,
      payer.publicKey,
      false,
      tokenProgramId
    );

    // Burn all purchased tokens
    const burnTx = new Transaction().add(
      createBurnInstruction(
        userTokenAccount,
        tokenMint,
        payer.publicKey,
        tokensBought,
        [],
        tokenProgramId
      )
    );

    console.log(`Burning ${tokensBought.toString()} tokens...`);

    const burnSig = await sendAndConfirmTransaction(connection, burnTx, [payer]);
    console.log(`Burn successful! Transaction signature: ${burnSig}`);

    // Calculate metrics
    const tokensBurnedFloat = Number(tokensBought) / Math.pow(10, tokenDecimals);
    console.log(`Burned ${tokensBought.toString()} raw units (${tokensBurnedFloat.toFixed(tokenDecimals)} tokens)`);
    
    const solSpent = (solBalanceAfterFees - await connection.getBalance(payer.publicKey)) / LAMPORTS_PER_SOL;
    const buyPricePerToken = tokensBurnedFloat > 0 ? solSpent / tokensBurnedFloat : 0;

    await postToApi("/api/burn/transaction", {
        status: "success",
        feeCollectionSignature: feeSignature,
        buySignature: buySignature,
        burnSignature: burnSig,
        tokensBought: tokensBought.toString(),
        tokensBurned: tokensBought.toString(),
        tokensBurnedFloat: tokensBurnedFloat.toFixed(tokenDecimals),
        solSpent: solSpent.toFixed(6),
        buyPricePerToken: buyPricePerToken.toFixed(10),
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58(),
        burnAddress: BURN_ADDRESS.toBase58()
    });

  } catch (error: any) {
    console.error("Error burning tokens:", error);
    await postToApi("/api/burn/transaction", {
        status: "failed",
        error: error.message || String(error),
        tokenAddress: tokenAddressString,
        wallet: payer.publicKey.toBase58(),
        feeCollectionSignature: feeSignature,
        buySignature: buySignature
    });
    process.exit(1);
  }
}

main().catch((err) => {
  console.error("Unexpected error:", err);
  process.exit(1);
});
