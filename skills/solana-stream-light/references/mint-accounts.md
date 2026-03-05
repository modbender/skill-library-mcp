# Streaming Mint Accounts

Stream light-mint accounts and metadata via Laserstream gRPC. Mint accounts are borsh-deserialized `Mint` structs containing base mint data, metadata, and optional extensions (including `TokenMetadata` for name/symbol/URI).

Events: new mints (raw data), mint updates (supply/authority changes), `TokenMetadata` (name, symbol, URI, additional_metadata), cold/hot transitions.

For simple lookups, use `get_account_interface` instead of streaming (see `shared.md`).

## Subscribe filters

Constants:

```rust
const LIGHT_TOKEN_PROGRAM_ID: &str = "cTokenmWW8bLPjZEBAUgYy3zKxQZW6VKi7bqNFEVv3m";
const ACCOUNT_TYPE_OFFSET: u64 = 165;
const ACCOUNT_TYPE_MINT: u8 = 1;
```

Additional imports beyond base streaming imports (see `shared.md`):

```rust
use borsh::BorshDeserialize;
use helius_laserstream::grpc::subscribe_request_filter_accounts_filter::Filter;
use helius_laserstream::grpc::subscribe_request_filter_accounts_filter_memcmp::Data;
use helius_laserstream::grpc::{
    SubscribeRequestFilterAccountsFilter,
    SubscribeRequestFilterAccountsFilterMemcmp,
};
use light_token_interface::state::{ExtensionStruct, Mint};
```

| Subscription | Detects | How |
|:-------------|:--------|:----|
| Account sub (`owner: cToken...`, `account_type == 1`) | Hot state + cold-to-hot | Pubkey cache lookup |
| Transaction sub (`account_include: cToken...`) | Hot-to-cold | Balance heuristic (`pre > 0, post == 0`) |

```rust
let mut request = helius_laserstream::grpc::SubscribeRequest::default();

// 1. Account sub: mint state tracking + cold-to-hot detection.
//    account_type == 1 (Mint) at byte offset 165.
request.accounts.insert(
    "light_mints".to_string(),
    SubscribeRequestFilterAccounts {
        owner: vec![LIGHT_TOKEN_PROGRAM_ID.to_string()],
        filters: vec![SubscribeRequestFilterAccountsFilter {
            filter: Some(Filter::Memcmp(SubscribeRequestFilterAccountsFilterMemcmp {
                offset: ACCOUNT_TYPE_OFFSET,
                data: Some(Data::Bytes(vec![ACCOUNT_TYPE_MINT])),
            })),
        }],
        nonempty_txn_signature: Some(true),
        ..Default::default()
    },
);

// 2. Transaction sub: hot-to-cold detection.
request.transactions.insert(
    "light_token_txns".to_string(),
    SubscribeRequestFilterTransactions {
        vote: Some(false),
        failed: Some(false),
        account_include: vec![LIGHT_TOKEN_PROGRAM_ID.to_string()],
        ..Default::default()
    },
);

let (stream, _handle) = subscribe(config, request);
tokio::pin!(stream);
```

Connection setup (`LaserstreamConfig`, mainnet/devnet URLs) is in `shared.md`.

## Deserialize mint accounts

Match on `UpdateOneof::Account`, borsh-deserialize as `Mint`, update cache, remove from `cold_cache`:

```rust
use helius_laserstream::grpc::subscribe_update::UpdateOneof;

Some(UpdateOneof::Account(account_update)) => {
    if let Some(account_info) = account_update.account {
        let pubkey: [u8; 32] = account_info.pubkey.as_slice().try_into().unwrap();

        match Mint::deserialize(&mut account_info.data.as_slice()) {
            Ok(mint) => {
                cold_cache.remove(&pubkey); // no longer cold
                cache.insert(pubkey, mint);
            }
            Err(e) => {
                eprintln!(
                    "Failed to deserialize mint {}: {}",
                    bs58::encode(&pubkey).into_string(),
                    e
                );
            }
        }
    }
}
```

## Hot-to-cold

Uses the shared `find_closed_accounts` function directly. No discriminator check is needed for mints -- `CompressAndCloseMint` always drains lamports to zero, and `cache.remove` filters unrelated closures. See `shared.md` for the full `find_closed_accounts` implementation and transaction handler pattern.

## TokenMetadata extraction

Iterate mint extensions and match `ExtensionStruct::TokenMetadata`:

```rust
fn extract_metadata(mint: &Mint) -> Option<(String, String, String)> {
    let extensions = mint.extensions.as_ref()?;

    for ext in extensions {
        if let ExtensionStruct::TokenMetadata(m) = ext {
            let name = String::from_utf8_lossy(&m.name).to_string();
            let symbol = String::from_utf8_lossy(&m.symbol).to_string();
            let uri = String::from_utf8_lossy(&m.uri).to_string();
            return Some((name, symbol, uri));
        }
    }
    None
}
```

## Data layouts

### Mint

```rust
#[repr(C)]
pub struct Mint {
    pub base: BaseMint,
    pub metadata: MintMetadata,
    pub reserved: [u8; 16],
    pub account_type: u8,
    pub compression: CompressionInfo,
    pub extensions: Option<Vec<ExtensionStruct>>,
}

#[repr(C)]
pub struct BaseMint {
    pub mint_authority: Option<Pubkey>,
    pub supply: u64,
    pub decimals: u8,
    pub is_initialized: bool,
    pub freeze_authority: Option<Pubkey>,
}

#[repr(C)]
pub struct MintMetadata {
    pub version: u8,
    pub mint_decompressed: bool,
    pub mint: Pubkey,
    pub mint_signer: [u8; 32],
    pub bump: u8,
}
```

### TokenMetadata

```rust
#[repr(C)]
pub struct TokenMetadata {
    pub update_authority: Pubkey,  // [0u8; 32] = immutable
    pub mint: Pubkey,
    pub name: Vec<u8>,
    pub symbol: Vec<u8>,
    pub uri: Vec<u8>,
    pub additional_metadata: Vec<AdditionalMetadata>,
}

pub struct AdditionalMetadata {
    pub key: Vec<u8>,
    pub value: Vec<u8>,
}
```

## Additional dependencies

Add to `Cargo.toml` alongside the shared streaming dependencies (see `shared.md`):

```toml
[dependencies]
borsh = "0.10"
light-token-interface = "0.3.0"
```
