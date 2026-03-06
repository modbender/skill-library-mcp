## Unsigned Transaction Formats by Chain

The `unsignedTransaction` field in the API response is encoded differently for each blockchain family.

### EVM Chains (Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, BSC, Linea, zkSync, Sonic, etc.)

**Encoding:** JSON string
**Must parse:** Yes — `JSON.parse(unsignedTransaction)`

```json
{
  "from": "0xUserWallet",
  "to": "0xContractAddress",
  "data": "0xEncodedCallData...",
  "value": "0",
  "gasLimit": "200000",
  "nonce": 42,
  "chainId": 8453,
  "maxFeePerGas": "107500073",
  "maxPriorityFeePerGas": "109421",
  "type": 2
}
```

| Field | Type | Description |
|-------|------|-------------|
| from | string | Sender address |
| to | string | Contract/recipient address |
| data | string | Hex-encoded calldata |
| value | string | Amount in wei (usually "0" for token operations) |
| gasLimit | string | Gas limit |
| nonce | number | Transaction nonce |
| chainId | number | Network chain ID (e.g., 1=Ethereum, 8453=Base, 42161=Arbitrum) |
| maxFeePerGas | string | EIP-1559 max fee per gas (type 2 only) |
| maxPriorityFeePerGas | string | EIP-1559 priority fee (type 2 only) |
| gasPrice | string | Legacy gas price (type 0 only) |
| type | number | 0=legacy, 2=EIP-1559 |


### Cosmos Chains (Cosmos Hub, Osmosis, Celestia, dYdX, Injective, Sei, etc.)

**Encoding:** Hex-encoded SignDoc bytes (string)
**Must parse:** No — pass hex string directly to Cosmos signing SDK

```
"0a92010a8f010a2f2f636f736d6f732e7374616b696e672e763162657461312e4d736744656c6567617465125c0a2d..."
```

The hex string encodes a Protobuf `SignDoc` containing:
- `bodyBytes`: Encoded `TxBody` (messages, memo, timeout)
- `authInfoBytes`: Encoded `AuthInfo` (signer, fee, gas)
- `chainId`: Chain identifier (e.g., "cosmoshub-4")
- `accountNumber`: Account number on chain

**Chain-specific argument:** `cosmosPubKey` is required in action arguments for Cosmos staking.

### Solana

**Encoding:** Hex-encoded bytes (legacy) or Base64-encoded bytes (versioned transactions)
**Must parse:** No — decode hex/base64 and pass to Solana signing SDK

```
"01000103ab4f6f7b4e3c8f2d1a..."
```

Legacy transactions are hex-encoded serialized `Transaction` objects. Versioned transactions (v0) are Base64-encoded wire format. The signing SDK (`@solana/web3.js`) handles both.

### Substrate (Polkadot, Kusama, Westend)

**Encoding:** JSON object (NOT a string — already parsed)
**Must parse:** No — it's already a JSON object in the response

```json
{
  "tx": {
    "address": "5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY",
    "blockHash": "0x...",
    "blockNumber": 12345678,
    "eraPeriod": 64,
    "genesisHash": "0x91b171bb158e2d3848fa23a9f1c25182fb8e20313b2c1eb49219da7a70ce90c3",
    "method": "0x0700...",
    "nonce": 5,
    "specVersion": 1002000,
    "tip": 0,
    "transactionVersion": 26
  },
  "specName": "polkadot",
  "specVersion": 1002000,
  "metadataRpc": "0x..."
}
```

**Note:** Substrate transactions include chain metadata (`metadataRpc`) needed for offline signing with `@substrate/txwrapper-polkadot`.

### Tezos

**Encoding:** Hex-encoded forged operation bytes (string)
**Must parse:** No — pass hex string to Tezos signing SDK

```
"6c00fbe8..."
```

For Ledger Wallet API compatibility (when `ledgerWalletApiCompatible: true` in arguments), the format changes to a JSON string:

```json
{
  "family": "tezos",
  "mode": "delegate",
  "amount": "1000000",
  "recipient": "tz1...",
  "fees": "1420",
  "gasLimit": "10600"
}
```

**Chain-specific argument:** `tezosPubKey` is required in action arguments for Tezos staking.

### TON

**Encoding:** JSON string (serialized message object)
**Must parse:** Yes — `JSON.parse(unsignedTransaction)`

```json
{
  "to": "EQ...",
  "value": "1000000000",
  "body": "te6cckEBAQEADgAAGEhfZccAAAAAAAAAAIA6ig=="
}
```

For Ledger Wallet API compatibility, the format changes to:

```json
{
  "family": "ton",
  "amount": "1000000000",
  "recipient": "EQ...",
  "fees": "10000000",
  "comment": { "text": "d:pool_address", "isEncrypted": false }
}
```

### Near

**Encoding:** Hex-encoded serialized `Transaction` bytes (string)
**Must parse:** No — decode hex and pass to Near signing SDK (`near-api-js`)

```
"09000000736f6d652e6e656172..."
```

The hex string encodes a serialized `Transaction` containing:
- `signerId`: Sender account ID
- `publicKey`: Sender's public key
- `nonce`: Transaction nonce
- `receiverId`: Recipient account ID
- `actions`: Array of actions (stake, transfer, etc.)
- `blockHash`: Recent block hash

### Sui

**Encoding:** Base64-encoded JSON (string)
**Must parse:** No — decode base64, then pass to Sui signing SDK (`@mysten/sui`)

```
"eyJ0eXBlIjoiY2FsbCIsInRhcmdldCI6IjB4Li4uIiwiYXJncyI6Wy4uLl19..."
```

Built using the `Transaction` class from `@mysten/sui/transactions`, serialized via `tx.toJSON()` then Base64-encoded.

### Aptos

**Encoding:** Base64-encoded BCS (Binary Canonical Serialization) bytes (string)
**Must parse:** No — decode base64, then pass to Aptos signing SDK (`@aptos-labs/ts-sdk`)

```
"AAAAAAAAAAAAAAABAgAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBHN0YWtl..."
```

The Base64 string encodes a `RawTransaction` containing:
- `sender`: Sender address
- `sequenceNumber`: Account sequence number
- `payload`: Transaction payload (entry function call)
- `maxGasAmount`: Maximum gas units
- `gasUnitPrice`: Gas unit price in APT
- `expirationTimestampSecs`: Transaction expiration
- `chainId`: Network chain ID

### Cardano

**Encoding:** CBOR hex string (string)
**Must parse:** No — pass hex to Cardano signing SDK (`@meshsdk/core`)

```
"84a50081825820abc123...ff"
```

Built using `MeshTxBuilder` from `@meshsdk/core`. The CBOR-encoded transaction contains inputs, outputs, fees, and certificates for staking operations.

### Stellar

**Encoding:** XDR string (string)
**Must parse:** No — pass XDR to Stellar signing SDK (`@stellar/stellar-sdk`)

```
"AAAAAgAAAABk..."
```

Built using `TransactionBuilder` from `@stellar/stellar-sdk`. The XDR string is produced by `transaction.toXDR()`.

### Tron

**Encoding:** JSON string (same as EVM format)
**Must parse:** Yes — `JSON.parse(unsignedTransaction)`

Tron is EVM-compatible, so the format follows the EVM structure. Uses `ethers.ContractTransaction` serialized as a JSON string.

**Chain-specific argument:** `tronResource` (`BANDWIDTH` or `ENERGY`) is required for Tron staking.

### Quick Reference Table

| Chain Family | Encoding | Type in Response | Parse Before Signing? | Signing SDK |
|-------------|----------|------------------|-----------------------|-------------|
| EVM | JSON string | `string` | Yes (`JSON.parse`) | ethers.js / viem |
| Cosmos | Hex bytes | `string` | No (hex decode) | @cosmjs/stargate |
| Solana | Hex/Base64 bytes | `string` | No (hex/base64 decode) | @solana/web3.js |
| Substrate | JSON object | `object` | No (already parsed) | @substrate/txwrapper |
| Tezos | Hex bytes / JSON | `string` | Depends on mode | @taquito/taquito |
| TON | JSON string | `string` | Yes (`JSON.parse`) | @ton/ton |
| Near | Hex bytes | `string` | No (hex decode) | near-api-js |
| Sui | Base64 JSON | `string` | No (base64 decode) | @mysten/sui |
| Aptos | Base64 BCS | `string` | No (base64 decode) | @aptos-labs/ts-sdk |
| Cardano | CBOR hex | `string` | No (hex decode) | @meshsdk/core |
| Stellar | XDR | `string` | No (XDR decode) | @stellar/stellar-sdk |
| Tron | JSON string | `string` | Yes (`JSON.parse`) | ethers.js / TronWeb |
