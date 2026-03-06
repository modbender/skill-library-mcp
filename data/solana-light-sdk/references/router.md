# Router Integration

Your existing quoting, routing, and swap-building logic stays the same.
The only addition: when a market has cold accounts, detect them, and prepend load instructions before the swap.

## What changes

| | Hot market (99%+) | Cold market |
|---|---|---|
| Quoting | No change | No change |
| Swap instruction | No change | No change |
| Transaction | No change | Prepend `create_load_instructions` |

## Detecting cold accounts

Track cold accounts using a `cold_cache: HashMap<[u8; 32], AccountInterface>`.

Two concurrent gRPC subscriptions detect lifecycle transitions: an account subscription (owner filter) catches cold-to-hot, a transaction subscription (account_include filter) catches hot-to-cold via the balance heuristic (`pre > 0, post == 0`). For the full streaming implementation with `find_closed_accounts`, cache handlers, and connection setup, see the `data-streaming` skill.

If you don't stream, call `get_multiple_account_interfaces` at swap time and check `is_cold()`.

## Building swap transactions with cold accounts

```rust
use light_client::interface::{create_load_instructions, LightProgramInterface};

// 1. Identify which accounts the swap touches
let pubkeys = sdk.instruction_accounts(&AmmInstruction::Swap);

// 2. Check which are cold (from your streaming cache, or fetch)
let cold_pubkeys: Vec<_> = pubkeys.iter().filter(|p| cold_set.contains(p)).collect();

// 3. If any are cold, fetch their ColdContext and build load instructions
let mut ixs = vec![];
if !cold_pubkeys.is_empty() {
    let interfaces = rpc
        .get_multiple_account_interfaces(cold_pubkeys, None)
        .await?
        .value;
    let cold: Vec<_> = interfaces.into_iter().flatten().collect();
    let specs = sdk.load_specs(&cold)?;
    ixs.extend(create_load_instructions(&specs, payer, config_pda, &rpc).await?);
}

// 4. Swap instruction is unchanged
ixs.push(sdk.swap_ix(&swap_params)?);
```

## The LightProgramInterface trait

Each rent-free AMM SDK exposes this trait. It returns which accounts an instruction reads/writes and builds load specs for cold ones. For framework-specific implementations, see [client-sdk.md](./client-sdk.md).

```rust
pub trait LightProgramInterface {
    type Variant: Pack<AccountMeta> + Clone + Debug;
    type Instruction;

    fn program_id() -> Pubkey;
    fn instruction_accounts(&self, ix: &Self::Instruction) -> Vec<Pubkey>;
    fn load_specs(
        &self,
        cold_accounts: &[AccountInterface],
    ) -> Result<Vec<AccountSpec<Self::Variant>>, Box<dyn Error>>;
}
```

- `instruction_accounts` -- returns the pubkeys the instruction reads/writes.
- `load_specs` -- given cold `AccountInterface`s (with `ColdContext`), returns the `AccountSpec`s that `create_load_instructions` needs to bring them back on-chain.

## Full example

### Dependencies

```toml
[dependencies]
light-client = { version = "0.19.0", features = ["v2"] }

# AMM SDK that implements LightProgramInterface (provided by the AMM team)
example-amm-sdk = "0.1"
```

### Code

```rust
use light_client::interface::{create_load_instructions, LightProgramInterface};
use example_amm_sdk::{ExampleAmmSdk, AmmInstruction};

// Construct SDK from pool data (same as before -- pool data is always available,
// hot or cold, via get_account_interface or your cache).
let sdk = ExampleAmmSdk::new(pool_address, pool_data)?;

// Quote works the same regardless of hot/cold.
let quote = sdk.quote(amount_in, min_out)?;

// Build transaction.
let mut ixs = vec![];

// Check if any swap accounts are cold.
let pubkeys = sdk.instruction_accounts(&AmmInstruction::Swap);
let cold_pubkeys: Vec<_> = pubkeys.iter().filter(|p| cold_set.contains(p)).collect();

if !cold_pubkeys.is_empty() {
    // Fetch ColdContext for cold accounts.
    let interfaces = rpc
        .get_multiple_account_interfaces(cold_pubkeys, None)
        .await?
        .value;
    let cold: Vec<_> = interfaces.into_iter().flatten().collect();
    let specs = sdk.load_specs(&cold)?;
    ixs.extend(create_load_instructions(&specs, payer.pubkey(), config_pda, &rpc).await?);
}

// Swap instruction is the same as without rent-free accounts.
ixs.push(sdk.swap_ix(&swap_params)?);

rpc.send_transaction(&ixs, &payer).await?;
```

## Key types

| Type | Source | Purpose |
|------|--------|---------|
| `AccountInterface` | `light-client` | Account data with optional `ColdContext` |
| `LightProgramInterface` | `light-client` | Trait that AMM SDKs implement |
| `AccountSpec` | `light-client` | Input to `create_load_instructions` |

## Hot vs Cold

| | Hot | Cold |
|---|-----|------|
| On-chain | Yes | Ledger (compressed) |
| Quote | Works | Works |
| Swap | Direct | Load first / Bundle |
| Latency | Normal | +0-200ms* |
| Tx size | Normal | +100-2400 bytes*|
| CU | Normal | +15k-400k CU*|

*Depends on the number and type of cold accounts.*

### When does a market go cold?

Accounts go cold after extended inactivity. Their virtual rent balance drops
below a threshold and miners compress them onto the Solana ledger.

They stay cold until any client loads them back in-flight via `create_load_instructions`.

**Touching cold markets is rare.** The hot path has zero overhead.

## Jito bundles

If load + swap exceed Solana's 1232-byte tx limit, send as a Jito bundle. The SDK deduplicates many account keys over the wire, so instructions that appear large in isolation will be incremental when combined with swap/deposit instructions.

```rust
use solana_sdk::{instruction::Instruction, pubkey::Pubkey, system_instruction};

const JITO_TIP_ACCOUNTS: &[&str] = &[
    "96gYZGLnJYVFmbjzopPSU6QiEV5fGqZNyN9nmNhvrZU5",
    "HFqU5x63VTqvQss8hp11i4wVV8bD44PvwucfZ2bU7gRe",
    "Cw8CFyM9FkoMi7K7Crf6HNQqf4uEMzpKw6QNghXLvLkY",
    "ADaUMid9yfUytqMBgopwjb2DTLSokTSzL1zt6iGPaS49",
    "DfXygSm4jCyNCybVYYK6DwvWqjKee8pbDmJGcLWNDXjh",
    "ADuUkR4vqLUMWXxW9gh6D6L8pMSawimctcNZ5pGwDcEt",
    "DttWaMuVvTiduZRnguLF7jNxTgiMBZ1hyAumKUiL2KRL",
    "3AVi9Tg9Uo68tJfuvoKvqKNWKkC5wPdSSdeBnizKZ6jT",
];

fn jito_tip_ix(payer: &Pubkey, tip_lamports: u64) -> Instruction {
    let tip_account = JITO_TIP_ACCOUNTS[rand::random::<usize>() % JITO_TIP_ACCOUNTS.len()]
        .parse::<Pubkey>().unwrap();
    system_instruction::transfer(payer, &tip_account, tip_lamports)
}

// Add tip to last transaction, serialize, send to Jito
let tip_ix = jito_tip_ix(&payer.pubkey(), 10_000); // 10k lamports
swap_ixs.push(tip_ix);

let bundle = vec![load_tx_base64, swap_tx_base64];
let resp = client
    .post("https://mainnet.block-engine.jito.wtf/api/v1/bundles")
    .json(&serde_json::json!({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "sendBundle",
        "params": [bundle, {"encoding": "base64"}]
    }))
    .send().await?;
```

## FAQ

**Do I need to change my swap instructions?**

No. Swap instructions are identical. If the market is hot, the transaction
is the same as today. If cold, you prepend `create_load_instructions`.

**Can I quote cold markets?**

Yes. `get_account_interface` returns full account data regardless of hot/cold.
Quoting works the same.

**Do rent-free markets increase latency?**

**Hot (common path)**: No.

**Cold**: Loading accounts adds 1-200ms depending on whether a validity proof
is needed. If load + swap exceed Solana's 1232 byte limit, use Jito bundles.

**How long do accounts stay hot after loading?**

Until they go inactive again. Each write resets the timer. The inactivity
threshold is configurable by the program owner (e.g. 24h of no writes).

**Do RPC providers support get_account_interface?**

Yes. Supported by Helius and Triton. Can also be self-hosted via the
[open-source Photon indexer](https://github.com/helius-labs/photon).

**What if the indexer is down?**

Hot markets work as long as Solana is up. Cold accounts can't be loaded until
the indexer recovers. Compression is cryptographically verifiable -- integrity
doesn't depend on the indexer.

**I don't stream. Can I still support cold markets?**

Yes. At swap time, call `get_multiple_account_interfaces` for the instruction's
accounts and check `is_cold()`. This adds a round-trip per swap but requires
no streaming setup.

## Reference

| Resource | Link |
|----------|------|
| AMM Program | [cp-swap-reference](https://github.com/Lightprotocol/cp-swap-reference) |
| LightProgramInterface Trait Impl | [CpSwapSdk](https://github.com/Lightprotocol/cp-swap-reference/blob/main/programs/cp-swap/tests/program.rs#L409) |
