# Load associated token account

Reinstates a compressed (cold) token account back to active on-chain state. TypeScript only.

`loadAta` unifies tokens from multiple sources: compressed tokens → decompresses → Light associated token account; SPL balance (if `wrap=true`) → wraps → Light associated token account; T22 balance (if `wrap=true`) → wraps → Light associated token account. Creates the associated token account if it doesn't exist. Returns `null` if nothing to load (idempotent).

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    mintToCompressed,
    loadAta,
    getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";
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
    // Setup: Get compressed tokens (cold storage)
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);
    await mintToCompressed(rpc, payer, mint, payer, [
        { recipient: payer.publicKey, amount: 1000n },
    ]);

    // Load compressed tokens to hot balance
    const lightTokenAta = getAssociatedTokenAddressInterface(mint, payer.publicKey);
    const tx = await loadAta(rpc, lightTokenAta, payer, mint, payer);

    console.log("Tx:", tx);
})();
```

### Instruction

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import {
    createRpc,
    buildAndSignTx,
    sendAndConfirmTx,
} from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    mintToCompressed,
    createLoadAtaInstructions,
    getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token/unified";
import { homedir } from "os";
import { readFileSync } from "fs";

// devnet:
// const RPC_URL = `https://devnet.helius-rpc.com?api-key=${process.env.API_KEY!}`;
// const rpc = createRpc(RPC_URL);
// localnet:
const rpc = createRpc();

const payer = Keypair.fromSecretKey(
    new Uint8Array(
        JSON.parse(readFileSync(`${homedir()}/.config/solana/id.json`, "utf8")),
    ),
);

(async function () {
    // Inactive Light Tokens are cryptographically preserved on the Solana ledger
    // as compressed tokens (cold storage)
    // Setup: Get compressed tokens in light-token associated token account
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);
    await mintToCompressed(rpc, payer, mint, payer, [{ recipient: payer.publicKey, amount: 1000n }]);

    const lightTokenAta = getAssociatedTokenAddressInterface(
        mint,
        payer.publicKey,
    );

    // Load compressed tokens to light associated token account (hot balance). Usually one tx. Empty = noop.
    const instructions = await createLoadAtaInstructions(
        rpc,
        lightTokenAta,
        payer.publicKey,
        mint,
        payer.publicKey,
    );

    if (instructions.length === 0) return console.log("Nothing to load");

    for (const ixs of instructions) {
        const { blockhash } = await rpc.getLatestBlockhash();
        const tx = buildAndSignTx(ixs, payer, blockhash);
        const sig = await sendAndConfirmTx(rpc, tx);
        console.log("Tx:", sig);
    }
})();
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/load-ata)
- [Action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/load-ata.ts)
- [Instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/load-ata.ts)
