---
name: openburn
description: Automates collecting Pump.fun creator fees, buying tokens with collected SOL, and burning those tokens (buyback and burn). Use this skill when the user wants to set up a regular buyback and burn schedule for their Pump.fun tokens.
metadata:
  {
    "openclaw":
      {
        "emoji": "🔥",
        "requires":
          {
            "modules":
              ["@solana/web3.js", "@solana/spl-token", "tsx", "dotenv"],
            "binaries": ["node", "pnpm"],
            "env":
              [
                "CREATOR_WALLET_PRIVATE_KEY",
                "PUMP_FUN_TOKEN_ADDRESS",
                "JUPITER_API_KEY",
                "BURN_PERCENTAGE",
                "MIN_FEE_TO_BURN",
              ],
          },
        "install":
          [
            {
              "id": "pnpm-solana",
              "kind": "npm",
              "module": "@solana/web3.js",
              "cmd": "pnpm add @solana/web3.js @solana/spl-token @pump-fun/pump-sdk tsx dotenv -w",
              "label": "Install dependencies",
            },
          ],
      },
  }
---

# Openburn

This skill helps users automate the buyback and burn mechanism for Pump.fun tokens.

## How It Works

1. **Collect Creator Fees**: The script collects trading fees (in SOL) from both the bonding curve and AMM pools
2. **Buy Tokens**: Uses the collected SOL to purchase tokens from the bonding curve
3. **Burn Tokens**: Burns the purchased tokens by sending them to Solana's incinerator address, creating buying pressure and driving the token price up

## Setup Instructions

1.  **Request Credentials**:
    Ask the user for the following information:
    - `PUMP_FUN_TOKEN_ADDRESS` (The token address on Pump.fun)
    - `CREATOR_WALLET_PRIVATE_KEY` (The private key of the wallet to burn from)
    - `JUPITER_API_KEY` (Get from [Jupiter Portal](https://portal.jup.ag/api-keys) - **Only needed if token is graduated/off-curve**)
    - `BURN_PERCENTAGE` (Percentage of collected SOL to use for buying tokens, default: 80)
    - `MIN_FEE_TO_BURN` (Minimum SOL fees required to proceed with burn, default: 0.1)

    > [!IMPORTANT]
    > Remind the user that their keys will be stored locally in the `.env` file.

2.  **Store Credentials**:
    Check if the `.env` file exists in the root directory.
    - If it exists, append the keys.
    - If not, create it.

    Format:

    ```env
    PUMP_FUN_TOKEN_ADDRESS=...
    CREATOR_WALLET_PRIVATE_KEY=...
    JUPITER_API_KEY=...
    BURN_PERCENTAGE=80
    MIN_FEE_TO_BURN=0.1
    ```

3.  **Register Token**:
    Once the `PUMP_FUN_TOKEN_ADDRESS` is received and stored, register the token with the API.

    **Endpoint**: `POST https://api.openburn.fun/api/burn/register`
    **Body**:

    ```json
    {
      "tokenAddress": "<PUMP_FUN_TOKEN_ADDRESS>"
    }
    ```

    This registration step is required before scheduling the burn job.

4.  **Schedule Job**:
    Ask the user for the scheduling interval (default: every 2 hours).

    Use the `cron` tool to register a new job:
    - **Name**: `openburn-job`
    - **Schedule**: `{ "kind": "every", "everyMs": 7200000 }` (replace 7200000 with user's interval in ms)
    - **Session Target**: `isolated`
    - **Payload**:
      ```json
      {
        "kind": "agentTurn",
        "message": "Execute the openburn script to burn SOL tokens.",
        "deliver": true
      }
      ```

5.  **Report Schedule**:
    Make a POST request to report the scheduled job.

    **Endpoint**: `POST https://api.openburn.fun/api/burn/schedule`
    **Body**:

    ```json
    {
      "jobId": "openburn-job",
      "intervalMs": 7200000
    }
    ```

## Execution Instructions

When the cron job triggers (receiving the message "Execute the openburn script..."):

1.  **Execute the Script**:
    Run the burn script located at `skills/openburn/scripts/burn.ts`.

    ```bash
    node --import tsx skills/openburn/scripts/burn.ts
    ```

2.  **Report Results**:
    The script will automatically report transaction success/failure to `https://api.openburn.fun/api/burn/transaction`.
    You should also report the output (transaction signature) to the user in the chat.

    > [!IMPORTANT]
    > **Token Decimals**: The script logs raw token amounts (integer values).
    >
    > - For a token with 6 decimals (like USDC), `1000000` = 1 token.
    > - For a token with 9 decimals (like SOL), `1000000000` = 1 token.
    > - Always format the token amount based on its decimals before reporting it to the user. Do NOT report "1 trillion tokens burned" if the raw value is `1000000000000` but the token has 18 decimals (which is just ~0.000001 tokens).
    > - The script will now log `tokensBurnedFloat` which is the human-readable amount. **Use `tokensBurnedFloat` for reporting.**

3.  **Burn Only (Manual)**:
    If the user wants to manually burn tokens already in the wallet without buying more:

    ```bash
    node --import tsx skills/burn-only.ts
    ```

    **Note**: You can configure the percentage of tokens to burn by setting the `BURN_PERCENTAGE` environment variable in `.env`. Default is 100%.
    Example: `BURN_PERCENTAGE=50` to burn 50% of the tokens in the wallet.
