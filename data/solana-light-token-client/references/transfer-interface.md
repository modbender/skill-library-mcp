# Transfer interface

Routes through SPL, Token-2022, or Light Token depending on source/destination types.

**Transfer paths**: Light→Light: direct transfer. SPL→Light: SPL tokens locked in interface PDA, balance credited to Light account. Light→SPL: burns Light balance, releases SPL from interface PDA.

## TypeScript

### Action

```typescript
import "dotenv/config";
import { Keypair } from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterface,
    mintToInterface,
    transferInterface,
    getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token";
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
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);

    const sender = Keypair.generate();
    await createAtaInterface(rpc, payer, mint, sender.publicKey);
    const senderAta = getAssociatedTokenAddressInterface(mint, sender.publicKey);
    await mintToInterface(rpc, payer, mint, senderAta, payer, 1_000_000_000);

    const recipient = Keypair.generate();

    // destination is a wallet pubkey; the action creates the recipient associated token account.
    const tx = await transferInterface(rpc, payer, senderAta, mint, recipient.publicKey, sender, 500_000_000);

    console.log("Tx:", tx);
})();
```

### Instruction

```typescript
import "dotenv/config";
import {
    Keypair,
    ComputeBudgetProgram,
    Transaction,
    sendAndConfirmTransaction,
} from "@solana/web3.js";
import { createRpc } from "@lightprotocol/stateless.js";
import {
    createMintInterface,
    createAtaInterface,
    mintToInterface,
    createLightTokenTransferInstruction,
    getAssociatedTokenAddressInterface,
} from "@lightprotocol/compressed-token";
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
    const { mint } = await createMintInterface(rpc, payer, payer, null, 9);

    const sender = Keypair.generate();
    await createAtaInterface(rpc, payer, mint, sender.publicKey);
    const senderAta = getAssociatedTokenAddressInterface(
        mint,
        sender.publicKey,
    );
    await mintToInterface(rpc, payer, mint, senderAta, payer, 1_000_000_000);

    const recipient = Keypair.generate();
    await createAtaInterface(rpc, payer, mint, recipient.publicKey);
    const recipientAta = getAssociatedTokenAddressInterface(
        mint,
        recipient.publicKey,
    );

    // Transfer tokens between light-token associated token accounts
    const ix = createLightTokenTransferInstruction(
        senderAta,
        recipientAta,
        sender.publicKey,
        500_000_000,
    );

    const tx = new Transaction().add(ix);
    const signature = await sendAndConfirmTransaction(rpc, tx, [payer, sender]);

    console.log("Tx:", signature);
})();
```

## Rust

### Action

```rust
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_token_client::actions::{CreateAta, TransferInterface};
use rust_client::{setup, SetupContext};
use solana_sdk::{signature::Keypair, signer::Signer};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let SetupContext {
        mut rpc,
        payer,
        mint,
        associated_token_account,
        decimals,
        ..
    } = setup().await;

    // Create recipient associated token account
    let recipient = Keypair::new();
    let (_signature, recipient_associated_token_account) = CreateAta {
        mint,
        owner: recipient.pubkey(),
        idempotent: true,
    }
    .execute(&mut rpc, &payer)
    .await?;

    // Transfers tokens between token accounts (SPL, Token-2022, or Light) in a single call.
    let sig = TransferInterface {
        source: associated_token_account,
        mint,
        destination: recipient_associated_token_account,
        amount: 1000,
        decimals,
        ..Default::default()
    }
    .execute(&mut rpc, &payer, &payer)
    .await?;

    let data = rpc
        .get_account(recipient_associated_token_account)
        .await?
        .ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

### Instruction

```rust
use anchor_spl::token::spl_token;
use borsh::BorshDeserialize;
use light_client::rpc::Rpc;
use light_program_test::{LightProgramTest, ProgramTestConfig};
use light_token::{
    instruction::{
        get_associated_token_address, CreateAssociatedTokenAccount, SplInterface,
        TransferInterface, LIGHT_TOKEN_PROGRAM_ID,
    },
    spl_interface::find_spl_interface_pda_with_index,
};
use rust_client::{setup_spl_associated_token_account, setup_spl_mint};
use solana_sdk::signer::Signer;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut rpc = LightProgramTest::new(ProgramTestConfig::new_v2(true, None)).await?;

    let payer = rpc.get_payer().insecure_clone();
    let decimals = 2u8;
    let amount = 10_000u64;

    // Setup creates mint, mints tokens and creates SPL associated token account
    let mint = setup_spl_mint(&mut rpc, &payer, decimals).await;
    let spl_associated_token_account = setup_spl_associated_token_account(&mut rpc, &payer, &mint, &payer.pubkey(), amount).await;
    let (interface_pda, interface_bump) = find_spl_interface_pda_with_index(&mint, 0, false);

    // Create Light associated token account
    let light_associated_token_account = get_associated_token_address(&payer.pubkey(), &mint);

    let create_associated_token_account_instruction =
        CreateAssociatedTokenAccount::new(payer.pubkey(), payer.pubkey(), mint).instruction()?;

    rpc.create_and_send_transaction(&[create_associated_token_account_instruction], &payer.pubkey(), &[&payer])
        .await?;

    // SPL interface PDA for Mint (holds SPL tokens when transferred to Light Token)
    let spl_interface = SplInterface {
        mint,
        spl_token_program: spl_token::ID,
        spl_interface_pda: interface_pda,
        spl_interface_pda_bump: interface_bump,
    };

    // Transfers tokens between token accounts (SPL, Token-2022, or Light) in a single call.
    let transfer_instruction = TransferInterface {
        source: spl_associated_token_account,
        destination: light_associated_token_account,
        amount,
        decimals,
        authority: payer.pubkey(),
        payer: payer.pubkey(),
        spl_interface: Some(spl_interface),
        max_top_up: None,
        source_owner: spl_token::ID,
        destination_owner: LIGHT_TOKEN_PROGRAM_ID,
    }
    .instruction()?;

    let sig = rpc
        .create_and_send_transaction(&[transfer_instruction], &payer.pubkey(), &[&payer])
        .await?;

    let data = rpc
        .get_account(light_associated_token_account)
        .await?
        .ok_or("Account not found")?;
    let token = light_token_interface::state::Token::deserialize(&mut &data.data[..])?;
    println!("Balance: {} Tx: {sig}", token.amount);

    Ok(())
}
```

## Links

- [Docs](https://zkcompression.com/light-token/cookbook/transfer-interface)
- [TS action example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/transfer-interface.ts)
- [TS instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/transfer-interface.ts)
- [Rust action example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/transfer_interface.rs)
- [Rust instruction example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/transfer_interface.rs)
