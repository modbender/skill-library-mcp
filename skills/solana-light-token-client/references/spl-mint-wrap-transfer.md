# Mint SPL, wrap, and transfer

End-to-end flow: create a Token-2022 mint with interface PDA, mint SPL tokens, wrap to Light Token associated token account, and transfer.

## TypeScript

```typescript
import "dotenv/config";
import { Keypair, PublicKey } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterfaceIdempotent,
    getAssociatedTokenAddressInterface,
    wrap,
    transferInterface,
} from "@lightprotocol/compressed-token";
import {
    TOKEN_2022_PROGRAM_ID,
    createAssociatedTokenAccount,
    mintTo,
} from "@solana/spl-token";
import { homedir } from "os";
import { readFileSync } from "fs";

// devnet:
const RPC_URL = `https://devnet.helius-rpc.com?api-key=${process.env.API_KEY!}`;
const rpc = createRpc(RPC_URL);
// localnet:
// const rpc = createRpc();

const payer = Keypair.fromSecretKey(
    new Uint8Array(
        JSON.parse(readFileSync(`${homedir()}/.config/solana/id.json`, "utf8"))
    )
);

(async function () {
    const decimals = 9;
    const tokenAmount = BigInt(100 * Math.pow(10, decimals));
    const recipient = Keypair.generate();

    // Creates on-chain SPL or Token-2022 mint and registers SPL interface PDA.
    // SPL interface PDA enables wrap/unwrap between SPL/Token-2022 and Light Token.
    const mintKeypair = Keypair.generate();
    const { mint } = await createMintInterface(
        rpc,
        payer,
        payer,
        null,
        decimals,
        mintKeypair,
        undefined,
        TOKEN_2022_PROGRAM_ID,
    );

    // 1. Mint SPL tokens to payer's associated token account
    const payerSplAta = await createAssociatedTokenAccount(
        rpc,
        payer,
        mint,
        payer.publicKey,
        undefined,
        TOKEN_2022_PROGRAM_ID,
    );
    await mintTo(
        rpc,
        payer,
        mint,
        payerSplAta,
        payer,
        tokenAmount,
        [],
        undefined,
        TOKEN_2022_PROGRAM_ID,
    );

    // 2. Wrap SPL tokens into payer's light associated token account
    await createAtaInterfaceIdempotent(rpc, payer, mint, payer.publicKey);
    const payerLightAta = getAssociatedTokenAddressInterface(mint, payer.publicKey);
    await wrap(rpc, payer, payerSplAta, payerLightAta, payer, mint, tokenAmount);

    // 3. Transfer to recipient's light associated token account
    await createAtaInterfaceIdempotent(rpc, payer, mint, recipient.publicKey);
    const recipientLightAta = getAssociatedTokenAddressInterface(mint, recipient.publicKey);
    await transferInterface(
        rpc,
        payer,
        payerLightAta,
        mint,
        recipientLightAta,
        payer,
        tokenAmount,
    );

    console.log("Transferred", 100, "tokens to", recipient.publicKey.toBase58());
})();
```

## Links

- [Quickstart](https://zkcompression.com/light-token/quickstart)
- [Source](https://github.com/Lightprotocol/examples-light-token/blob/main/toolkits/sign-with-privy/scripts/src/mint-spl-and-wrap.ts)
