# Streaming Token Accounts

Light token accounts share the same 165-byte base layout as SPL Token. Existing SPL Token parsers work without modification. Two gRPC subscriptions target the Light Token Program: an account subscription for hot state and cold-to-hot detection, and a transaction subscription for hot-to-cold detection.

For simple account lookups, use `get_account_interface` instead of streaming. See `shared.md` for connection setup, `find_closed_accounts`, cold-to-hot base pattern, and point queries.

## Parsing

`PodAccount` from `spl_token_2022_interface` parses SPL-token, SPL-token-2022, and Light-token accounts identically. For accounts with extensions, truncate to 165 bytes before parsing.

```rust
use spl_pod::bytemuck::pod_from_bytes;
use spl_token_2022_interface::pod::PodAccount;

let parsed: &PodAccount = pod_from_bytes(&data[..165])?;
```

## Subscribe filters

Constants:

```rust
const LIGHT_TOKEN_PROGRAM_ID: &str = "cTokenmWW8bLPjZEBAUgYy3zKxQZW6VKi7bqNFEVv3m";
const TOKEN_ACCOUNT_SIZE: u64 = 165;
const ACCOUNT_TYPE_OFFSET: u64 = 165;
const ACCOUNT_TYPE_TOKEN: u8 = 2;
```

Additional imports beyond base streaming imports (see `shared.md`):

```rust
use helius_laserstream::grpc::subscribe_request_filter_accounts_filter::Filter;
use helius_laserstream::grpc::subscribe_request_filter_accounts_filter_memcmp::Data;
use helius_laserstream::grpc::{
    SubscribeRequestFilterAccounts, SubscribeRequestFilterAccountsFilter,
    SubscribeRequestFilterAccountsFilterMemcmp, SubscribeRequestFilterTransactions,
};
```

Full `SubscribeRequest` construction:

```rust
let mut request = helius_laserstream::grpc::SubscribeRequest::default();

// 1. Account sub: hot state tracking + cold-to-hot detection.
//    Base token accounts (exactly 165 bytes, no extensions).
request.accounts.insert(
    "light_tokens".to_string(),
    SubscribeRequestFilterAccounts {
        owner: vec![LIGHT_TOKEN_PROGRAM_ID.to_string()],
        filters: vec![SubscribeRequestFilterAccountsFilter {
            filter: Some(Filter::Datasize(TOKEN_ACCOUNT_SIZE)),
        }],
        nonempty_txn_signature: Some(true),
        ..Default::default()
    },
);

//    Extended token accounts (account_type == 2 at byte 165).
request.accounts.insert(
    "light_tokens_extended".to_string(),
    SubscribeRequestFilterAccounts {
        owner: vec![LIGHT_TOKEN_PROGRAM_ID.to_string()],
        filters: vec![SubscribeRequestFilterAccountsFilter {
            filter: Some(Filter::Memcmp(SubscribeRequestFilterAccountsFilterMemcmp {
                offset: ACCOUNT_TYPE_OFFSET,
                data: Some(Data::Bytes(vec![ACCOUNT_TYPE_TOKEN])),
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

## Hot-to-cold

Uses shared `find_closed_accounts` directly (see `shared.md`). No discriminator check is needed for tokens -- `compress_and_close` always drains lamports to zero, and `cache.remove` filters out unrelated closures.

## Cold-to-hot

The account subscription delivers the re-created account when a token account is decompressed. Parse with `PodAccount` and update the cache:

```rust
Some(UpdateOneof::Account(account_update)) => {
    if let Some(account) = account_update.account {
        let pubkey: [u8; 32] = account.pubkey.as_slice().try_into().unwrap();
        let parsed: &PodAccount = pod_from_bytes(&account.data[..165])?;

        cold_cache.remove(&pubkey); // no longer cold
        cache.insert(pubkey, *parsed);
    }
}
```

## Data layout

165 bytes base, identical to SPL Token Account.

| Field | Offset | Size |
|:------|:-------|:-----|
| `mint` | 0 | 32 |
| `owner` | 32 | 32 |
| `amount` | 64 | 8 |
| `delegate` | 72 | 36 |
| `state` | 108 | 1 |
| `is_native` | 109 | 12 |
| `delegated_amount` | 121 | 8 |
| `close_authority` | 129 | 36 |
| `account_type` | 165 | 1 |

`account_type = 2` at byte 165 indicates extensions follow (borsh-encoded `Option<Vec<ExtensionStruct>>`).

## Extensions

Extensions are borsh-encoded as `Option<Vec<ExtensionStruct>>` after the 165-byte base. These are not needed for indexing or trading.

Deserialize with `Token::deserialize`:

```rust
use borsh::BorshDeserialize;
use light_token_interface::state::{Token, ExtensionStruct};

let token = Token::deserialize(&mut data.as_slice())?;

if let Some(exts) = &token.extensions {
    for ext in exts {
        if let ExtensionStruct::Compressible(info) = ext {
            // info.compression_authority, info.rent_sponsor, info.last_claimed_slot
        }
    }
}
```

| Variant | Description |
|:--------|:------------|
| `TokenMetadata(TokenMetadata)` | Name, symbol, URI, additional metadata |
| `PausableAccount(PausableAccountExtension)` | Marker: mint is pausable (no data; pause state lives on mint) |
| `PermanentDelegateAccount(PermanentDelegateAccountExtension)` | Marker: mint has permanent delegate |
| `TransferFeeAccount(TransferFeeAccountExtension)` | Withheld fees from transfers |
| `TransferHookAccount(TransferHookAccountExtension)` | Marker: mint has transfer hook |
| `CompressedOnly(CompressedOnlyExtension)` | Compressed-only token (stores delegated amount) |
| `Compressible(CompressibleExtension)` | Compression config: authority, rent sponsor, timing |

Source: [light-token-interface](https://github.com/Lightprotocol/light-protocol/tree/main/program-libs/token-interface/src/state/extensions)

## Additional dependencies

Additions to `Cargo.toml` beyond base streaming dependencies (see `shared.md`):

```toml
[dependencies]
borsh = "0.10"
light-token-interface = "0.3.0"
spl-token-2022-interface = "0.1"
spl-pod = "0.5"
```
