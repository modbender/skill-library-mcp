# Create interface PDA for existing mints

Register an interface PDA on an existing SPL or Token-2022 mint for interoperability with Light Token. The interface PDA holds SPL/T22 tokens when wrapped to Light Token. No mint authority required.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair, PublicKey } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import { createSplInterface } from "@lightprotocol/compressed-token";
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
    const existingMint = new PublicKey("YOUR_EXISTING_MINT_ADDRESS");

    const tx = await createSplInterface(rpc, payer, existingMint);

    console.log("Mint:", existingMint.toBase58());
    console.log("Tx:", tx);
})();
```

### Instruction

```typescript
import "dotenv/config";
import {
    Keypair,
    PublicKey,
    Transaction,
    sendAndConfirmTransaction,
} from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import { LightTokenProgram } from "@lightprotocol/compressed-token";
import { TOKEN_PROGRAM_ID } from "@solana/spl-token";
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
    const existingMint = new PublicKey("YOUR_EXISTING_MINT_ADDRESS");

    const ix = await LightTokenProgram.createSplInterface({
        feePayer: payer.publicKey,
        mint: existingMint,
        tokenProgramId: TOKEN_PROGRAM_ID,
    });

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(rpc, tx, [payer]);

    console.log("Mint:", existingMint.toBase58());
    console.log("Tx:", signature);
})();
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/create-mint)
