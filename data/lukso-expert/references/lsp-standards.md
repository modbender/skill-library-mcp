# LUKSO LSP Standards — Complete Reference

> **Purpose:** Comprehensive reference for AI agents building on LUKSO. Covers all LSP standards (LSP0–LSP26+) with practical implementation details, interface IDs, data keys, deployed contract addresses, code examples, and common pitfalls.  
> **Last updated:** February 2026  
> **Chain:** LUKSO Mainnet (Chain ID: 42, currency: LYX)  
> **Block explorer:** https://explorer.lukso.network  
> **RPC:** https://42.rpc.thirdweb.com

---

## Table of Contents

| LSP | Name | Category |
|-----|------|----------|
| [LSP0](#lsp0---erc725account) | ERC725Account | Account |
| [LSP1](#lsp1---universal-receiver) | Universal Receiver | Account |
| [LSP2](#lsp2---erc725y-json-schema) | ERC725Y JSON Schema | Metadata |
| [LSP3](#lsp3---profile-metadata) | Profile Metadata | Metadata |
| [LSP4](#lsp4---digital-asset-metadata) | Digital Asset Metadata | Metadata |
| [LSP5](#lsp5---received-assets) | Received Assets | Metadata |
| [LSP6](#lsp6---key-manager) | Key Manager | Access Control |
| [LSP7](#lsp7---digital-asset-fungible) | Digital Asset (Fungible) | Token |
| [LSP8](#lsp8---identifiable-digital-asset-nft) | Identifiable Digital Asset (NFT) | Token |
| [LSP9](#lsp9---vault) | Vault | Account |
| [LSP10](#lsp10---received-vaults) | Received Vaults | Metadata |
| [LSP11](#lsp11---basic-social-recovery) | Basic Social Recovery | Security |
| [LSP12](#lsp12---issued-assets) | Issued Assets | Metadata |
| [LSP14](#lsp14---ownable2step) | Ownable2Step | Ownership |
| [LSP16](#lsp16---universal-factory) | Universal Factory | Deployment |
| [LSP17](#lsp17---contract-extension) | Contract Extension | Extensibility |
| [LSP19](#lsp19---beacon-proxy) | Beacon Proxy | Deployment |
| [LSP20](#lsp20---call-verification) | Call Verification | Access Control |
| [LSP23](#lsp23---linked-contracts-factory) | Linked Contracts Factory | Deployment |
| [LSP25](#lsp25---execute-relay-call) | Execute Relay Call | Meta-Transactions |
| [LSP26](#lsp26---follower-system) | Follower System | Social |

---

## Quick Reference: Interface IDs

```
ERC165:                       0x01ffc9a7
ERC1271:                      0x1626ba7e
ERC725X:                      0x7545acac
ERC725Y:                      0x629aa694
LSP0ERC725Account:            0x24871b3d
LSP1UniversalReceiver:        0x6bb56a14 (approx - check latest)
LSP1UniversalReceiverDelegate: (check @lukso/lsp1delegate-contracts)
LSP6KeyManager:               0x23f34c62
LSP7DigitalAsset:             (check @lukso/lsp7-contracts)
LSP8IdentifiableDigitalAsset: (check @lukso/lsp8-contracts)
LSP9Vault:                    (check @lukso/lsp9-contracts)
LSP11BasicSocialRecovery:     0x049a28f1
LSP14Ownable2Step:            (check @lukso/lsp14-contracts)
LSP17Extendable:              (check @lukso/lsp17contractextension-contracts)
LSP17Extension:               (check @lukso/lsp17contractextension-contracts)
LSP20CallVerification:        (check @lukso/lsp20-contracts)
LSP20CallVerifier:            (check @lukso/lsp20-contracts)
LSP25ExecuteRelayCall:        0x5ac79908
LSP26FollowerSystem:          (check @lukso/lsp26-contracts)
```

**To get exact interface IDs at runtime (JS/TS):**
```typescript
import { INTERFACE_IDS } from '@lukso/lsp-smart-contracts';
console.log(INTERFACE_IDS.LSP0ERC725Account);  // '0x24871b3d'
console.log(INTERFACE_IDS.LSP6KeyManager);     // '0x23f34c62'
```

---

## Quick Reference: Deployed Contract Addresses (LUKSO Mainnet)

| Contract | Address |
|----------|---------|
| LSP16 Universal Factory | `0x1600000000000000000000000000000000000000` |
| LSP23 Linked Contracts Factory | `0x2300000A84D25dF63081feAa37ba6b62C4c89a30` |
| LSP26 Follower System | `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` |
| Nick Factory (deterministic deployer) | `0x4e59b44847b379578588920cA78FbF26c0B4956C` |

Universal Profile and Key Manager are deployed per-user — not singleton contracts.

---

---

# LSP0 - ERC725Account

**Status:** Draft  
**Interface ID:** `0x24871b3d`  
**Requires:** ERC165, ERC725X, ERC725Y, ERC1271, LSP1, LSP2, LSP14, LSP17, LSP20

## Purpose

LSP0 is the **Universal Profile** — a smart contract account that serves as a blockchain identity for humans, organizations, machines, or other smart contracts. It replaces EOAs (Externally Owned Accounts) with a flexible, extensible smart contract account.

Think of it as: *a digital passport that can hold assets, verify signatures, execute transactions, be extended with new functions, and react to incoming tokens/notifications.*

## Key Features

- **ERC725X** — Generic execution (CALL, STATICCALL, DELEGATECALL, CREATE, CREATE2)
- **ERC725Y** — Key-value data store (profile info, permissions, received assets, etc.)
- **ERC1271** — Signature verification (can sign on behalf of the account)
- **LSP1** — Universal Receiver (reacts to incoming tokens/vault transfers)
- **LSP14** — 2-step ownership transfer
- **LSP17** — Contract extensions (add new functions post-deployment via fallback)
- **LSP20** — Call verification (allows non-owner calls if owner approves)

## Key Interface / Functions

```solidity
interface ILSP0 {
    // ERC725X
    function execute(uint256 operationType, address target, uint256 value, bytes memory data) 
        external payable returns (bytes memory);
    function executeBatch(uint256[] memory operationsType, address[] memory targets, 
        uint256[] memory values, bytes[] memory datas) 
        external payable returns (bytes[] memory);

    // ERC725Y
    function getData(bytes32 dataKey) external view returns (bytes memory);
    function getDataBatch(bytes32[] memory dataKeys) external view returns (bytes[] memory);
    function setData(bytes32 dataKey, bytes memory dataValue) external payable;
    function setDataBatch(bytes32[] memory dataKeys, bytes[] memory dataValues) external payable;

    // ERC1271
    function isValidSignature(bytes32 hash, bytes memory signature) 
        external view returns (bytes4);

    // LSP1
    function universalReceiver(bytes32 typeId, bytes memory receivedData) 
        external payable returns (bytes memory);

    // LSP14
    function owner() external view returns (address);
    function pendingOwner() external view returns (address);
    function transferOwnership(address newPendingOwner) external;
    function acceptOwnership() external;
    function renounceOwnership() external;

    // LSP0 specific
    function batchCalls(bytes[] calldata functionCalls) 
        external returns (bytes[] memory results);

    // Payable hooks
    receive() external payable;
    fallback() external payable;
}
```

### ERC725X Operation Types

```solidity
// Operation types for execute()
uint256 constant CALL         = 0;  // Regular CALL
uint256 constant CREATE       = 1;  // Deploy new contract
uint256 constant CREATE2      = 2;  // Deploy with deterministic address
uint256 constant STATICCALL   = 3;  // Read-only call
uint256 constant DELEGATECALL = 4;  // Dangerous - execute in own context
```

## ERC725Y Data Keys (LSP0-specific)

```json
// Universal Receiver Delegate (global - catches all typeIds)
{
  "name": "LSP1UniversalReceiverDelegate",
  "key": "0x0cfc51aec37c55a4d0b1a65c6255c4bf2fbdf6277f3cc0730c45b828b6db8b47",
  "keyType": "Singleton",
  "valueType": "address"
}

// Universal Receiver Delegate (per typeId)
{
  "name": "LSP1UniversalReceiverDelegate:<bytes32>",
  "key": "0x0cfc51aec37c55a4d0b10000<bytes32>",  // first 20 bytes of typeId
  "keyType": "Mapping",
  "valueType": "address"
}

// LSP17 Extension for function selector
{
  "name": "LSP17Extension:<bytes4>",
  "key": "0xcee78b4094da860110960000<bytes4>",
  "keyType": "Mapping",
  "valueType": "(address, bytes1)"  // address + bool (forward value)
}
```

## LSP1 Type IDs (for value receive notifications)

```
keccak256('LSP0ValueReceived') = 0x9c4705229491d365fb5434052e12a386d6771d976bea61070a8c694e8affea3d
keccak256('LSP0OwnershipTransferStarted') = 0xe17117c9d2665d1dbeb479ed8058bbebde3c50ac50e2e65619f60006caac6926
keccak256('LSP0OwnershipTransferred_SenderNotification') = 0xa4e59c931d14f7c8a7a35027f92ee40b5f2886b9fdcdb78f30bc5ecce5a2f814
keccak256('LSP0OwnershipTransferred_RecipientNotification') = 0xceca317f109c43507871523e82dc2a3cc64dfa18f12da0b6db14f6e23f995538
```

## Code Examples

### Read profile data
```javascript
import { ERC725 } from '@erc725/erc725.js';
import LSP3Schema from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';

const erc725 = new ERC725(LSP3Schema, upAddress, 'https://42.rpc.thirdweb.com');
const profile = await erc725.fetchData('LSP3Profile');
```

### Execute a call from a UP (via ethers.js)
```javascript
const up = new ethers.Contract(upAddress, LSP0ABI, signer);

// Send LYX to another address
await up.execute(
  0,           // operationType = CALL
  recipient,   // target address
  ethers.parseEther("1.0"),  // value
  "0x"         // calldata
);

// Call a function on another contract
const calldata = myContract.interface.encodeFunctionData("myFunction", [arg1, arg2]);
await up.execute(0, myContractAddress, 0, calldata);
```

### Set data on the UP
```javascript
import { ERC725 } from '@erc725/erc725.js';

const encodedKey = ERC725.encodeKeyName('LSP3Profile');
await up.setData(encodedKey, encodedValue);
```

### Extend the UP with a new function
```javascript
// 1. Deploy an extension contract that implements the new function
// 2. Store the extension address in the UP's data store
const functionSelector = '0xdeadbeef';  // selector of new function
const extensionKey = `0xcee78b4094da860110960000${functionSelector.slice(2)}`;
await up.setData(extensionKey, extensionContractAddress);
// Now calling myFunction() on the UP will be forwarded to the extension
```

## Gotchas & Common Mistakes

1. **Owner vs KeyManager**: In production, the UP's `owner()` is typically the LSP6 KeyManager, NOT an EOA. Direct calls to `setData`, `execute` etc. must go through the KeyManager.

2. **LSP20 Call Verification**: If the owner is a KeyManager, any address can call UP functions directly — the KeyManager's `lsp20VerifyCall` is invoked automatically. Don't assume only the KM can call the UP.

3. **batchCalls() is NOT payable**: Can't send ETH with batchCalls. Use executeBatch for value transfers.

4. **Extension fallback**: The `fallback()` function handles unknown selectors. If a function doesn't exist on the UP, it checks `LSP17Extension:<selector>` in storage. If no extension found, reverts (except for `0x00000000` selector which passes).

5. **Value forwarding to extensions**: You must store 21 bytes (address + `0x01`) under the LSP17Extension key to forward ETH value to an extension. 20 bytes = no value forwarding.

6. **typeId trimming in URD**: When using `LSP1UniversalReceiverDelegate:<bytes32>`, only the first 20 bytes of the typeId are used as the key. Unique parts of typeIds must be in the first 20 bytes.

7. **2-step ownership**: `transferOwnership()` only sets the pending owner. The new owner must call `acceptOwnership()` to complete the transfer.

---

# LSP1 - Universal Receiver

**Status:** Draft  
**Interface ID:** `0x6bb56a14`  
**Requires:** ERC165

## Purpose

LSP1 defines a standardized way for smart contracts to **receive notifications** about events — token transfers, vault transfers, following events, etc. The `universalReceiver(bytes32 typeId, bytes data)` function acts like a universal hook that any contract can implement to react to any type of notification.

Think of it as: *a smart webhook that lets your contract be notified and react to anything happening in the ecosystem.*

## Key Interfaces

```solidity
// ILSP1 - The receiver interface
interface ILSP1UniversalReceiver {
    event UniversalReceiver(
        address indexed from,
        uint256 indexed value,
        bytes32 indexed typeId,
        bytes receivedData,
        bytes returnedValue
    );

    function universalReceiver(bytes32 typeId, bytes memory receivedData) 
        external payable returns (bytes memory);
}

// ILSP1Delegate - The delegate interface (contracts that handle specific typeIds)
interface ILSP1UniversalReceiverDelegate {
    function universalReceiverDelegate(
        address caller,      // the address that called universalReceiver
        uint256 value,       // value sent with the call
        bytes32 typeId,
        bytes memory receivedData
    ) external returns (bytes memory);
}
```

## How Delegation Works

An LSP0 account can delegate `universalReceiver` calls to handler contracts:

```
Caller → UP.universalReceiver(typeId, data)
    → UP checks: LSP1UniversalReceiverDelegate (global handler)
    → UP checks: LSP1UniversalReceiverDelegate:<typeId> (per-typeId handler)  
    → Both delegates get called if they exist
    → UniversalReceiver event is emitted
```

## Common typeIds

```
// LSP7 token transfers
keccak256('LSP7Tokens_RecipientNotification') = 0x20804611b3e2ea21c480dc465142210acf4a2485947541770ec1fb87dee4a55c
keccak256('LSP7Tokens_SenderNotification')    = 0x429ac7a06903dbc9c13dfcb3c9d11df8194581fa047c96d7a4171fc7402958ea

// LSP8 NFT transfers
keccak256('LSP8Tokens_RecipientNotification') = 0xb23eae7a994373421bf4f29f7206d7ded2d97af07b405eb6769bbfb0bbd1b9da
keccak256('LSP8Tokens_SenderNotification')    = 0x5b84d9550adb7000df7bee717735ecd3af48ea3f66c6886d52e8227548fb1b60

// LSP9 Vault transfers
keccak256('LSP9OwnershipTransferStarted')     = 0xaefd43f45fed1bcd8992f23c803b6f4ec45cf6b62b0d5d4a7c9f9f put context

// LSP14 ownership
// LSP26 follow/unfollow
keccak256('LSP26FollowerSystem_FollowNotification')   = 0x71e02f9f05bcd5816ec4f3134aa2e5a916669537ec6c77fe66ea595fabc2d51a
keccak256('LSP26FollowerSystem_UnfollowNotification') = 0x9d3c0b4012b69658977b099bdaa51eff0f0460f421fba96d15669506c00d1c4f
```

## Code Examples

### Implementing a Universal Receiver Delegate
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {LSP1UniversalReceiverDelegateUP} from "@lukso/lsp1delegate-contracts/contracts/LSP1UniversalReceiverDelegateUP.sol";

// The default LUKSO URD handles LSP7/LSP8 token bookkeeping automatically
// For custom logic, implement ILSP1UniversalReceiverDelegate:

contract MyCustomURD {
    function universalReceiverDelegate(
        address caller,
        uint256 value,
        bytes32 typeId,
        bytes memory data
    ) external returns (bytes memory) {
        // Custom logic based on typeId
        if (typeId == keccak256("LSP7Tokens_RecipientNotification")) {
            // Token received - do something
        }
        return "";
    }
}
```

### Register a URD on a Universal Profile
```javascript
// Set the global URD address
const URD_KEY = '0x0cfc51aec37c55a4d0b1a65c6255c4bf2fbdf6277f3cc0730c45b828b6db8b47';
await up.setData(URD_KEY, urdContractAddress);
```

## Gotchas & Common Mistakes

1. **URD must implement ERC165**: If the address stored as the URD doesn't implement `ILSP1UniversalReceiverDelegate` interface ID via `supportsInterface`, the call is silently skipped.

2. **URD failures don't revert transfers**: The LSP7/LSP8 transfer doesn't revert if the URD call fails. Token transfers are safe even if the receiver's URD reverts.

3. **Both URDs get called**: If there's both a global URD and a typeId-specific URD, BOTH are called. Design accordingly.

4. **typeId is bytes32 (keccak256 hash)**: Not a string. Always hash your typeId strings.

5. **Don't block in URD**: A URD that always reverts will block token receipt for that typeId. Test carefully.

---

# LSP2 - ERC725Y JSON Schema

**Status:** Draft  
**No interface ID** (it's a schema standard, not a contract)

## Purpose

LSP2 defines a **naming and encoding convention** for ERC725Y key-value data. It specifies how to construct `bytes32` data keys from human-readable names, and how to encode/decode values.

Think of it as: *the naming convention and ABI for the ERC725Y key-value store.*

## Key Types

### Singleton
```
key = keccak256("KeyName")

Example:
"LSP3Profile" → keccak256("LSP3Profile")
             → 0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5
```

### Array
```
// Array length key (how many items)
key = keccak256("KeyName[]")

// Array element key (item at index i)  
key = keccak256("KeyName[]")[0..16] + index_as_uint128

Example: "LSP5ReceivedAssets[]"
Length key: 0x6460ee3c0aac563ccbf76d6e1d07bada78e3a9514e6382b736ed3f478ab7b90b
Element[0]: 0x6460ee3c0aac563ccbf76d6e1d07bada00000000000000000000000000000000
Element[1]: 0x6460ee3c0aac563ccbf76d6e1d07bada00000000000000000000000000000001
```

### Mapping
```
key = keccak256("FirstWord")[:10] + 0x0000 + keccak256("SecondWord")[:20]

Example: "LSP5ReceivedAssetsMap:<address>"
key = keccak256("LSP5ReceivedAssetsMap")[:10] + 0x0000 + <address padded to 20 bytes>
    = 0x812c4334633eb816c80d0000<address>
```

### MappingWithGrouping
```
key = keccak256("FirstWord")[:6] + keccak256("SecondWord")[:4] + 0x0000 + keccak256("ThirdWord")[:20]

Example: "AddressPermissions:Permissions:<address>"
key = 0x4b80742de2bf82acb3630000<address>
```

### Bytes[CompactBytesArray]
```
A dynamic array where each element is prefixed with its 2-byte length.
Format: <length_1><element_1><length_2><element_2>...

Example (two 20-byte addresses):
0x0014<address1>0014<address2>
```

## Value Types

| valueType | Encoding |
|-----------|----------|
| `address` | 20 bytes, right-padded to 32 |
| `uint256` | 32 bytes big-endian |
| `bytes32` | 32 bytes |
| `bytes4`  | 4 bytes, right-padded |
| `bool`    | 1 byte (0x00 = false, 0x01 = true) |
| `string`  | UTF-8 encoded bytes |
| `bytes`   | raw bytes |
| `BitArray`| bytes32 where each bit = one permission |
| `VerifiableURI` | JSONURL encoded: `<hashFunction><hash><url>` |
| `JSONURL` (legacy) | `<hashFunction><hash><url>` |

## VerifiableURI Encoding (JSONURL)

Used for off-chain JSON data (profile metadata, token metadata, etc.):

```
Format: 0x<verificationMethodId><hash><url>

verificationMethodId:
  0x6f357c6a = keccak256 hash method

Example:
0x6f357c6a<32-byte keccak256 hash of JSON><utf8 url bytes>
```

## Code Examples

```javascript
import { ERC725 } from '@erc725/erc725.js';

// Encode a data key
const keyName = 'LSP3Profile';
const encodedKey = ERC725.encodeKeyName(keyName);

// Encode data (JSONURL for off-chain JSON)
const encoded = ERC725.encodeData([{
  keyName: 'LSP3Profile',
  value: {
    json: { ... },
    url: 'ipfs://Qm...'
  }
}], schemas);

// Decode data
const decoded = ERC725.decodeData([{ key, value }], schemas);
```

## Gotchas & Common Mistakes

1. **Mapping key trimming**: The second word of a Mapping key is trimmed to 20 bytes. Unique parts must be in the FIRST 20 bytes. Example: two typeIds that are identical in the first 20 bytes will clash.

2. **Array vs Mapping confusion**: There are two separate keys for arrays — one for the length and one per index. You must update BOTH when adding/removing items.

3. **Case sensitivity**: Key names are case-sensitive. `lsp3Profile` ≠ `LSP3Profile`.

4. **Don't compute keys manually**: Use `@erc725/erc725.js` or `@lukso/lsp-smart-contracts` to encode keys. Manual computation is error-prone.

---

# LSP3 - Profile Metadata

**Status:** Draft  
**No dedicated interface ID** (data schema standard)  
**Supported Standard Key:** `0xeafec4d89fa9619884b600005ef83ad9` (SupportedStandards:LSP3Profile)

## Purpose

LSP3 defines the **data keys and JSON structure** for Universal Profile metadata — name, description, avatar, background, links, tags. It's stored in the UP's ERC725Y key-value store as a `VerifiableURI` pointing to off-chain JSON.

## ERC725Y Data Keys

```json
// The profile metadata (points to off-chain JSON)
{
  "name": "LSP3Profile",
  "key": "0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5",
  "keyType": "Singleton",
  "valueType": "bytes",
  "valueContent": "VerifiableURI"
}

// Supported standard marker (always set to LSP3 value)
{
  "name": "SupportedStandards:LSP3Profile",
  "key": "0xeafec4d89fa9619884b60000 5ef83ad9559033e6e941db7d7c495acdce616347",
  "valueContent": "0x5ef83ad9"
}
```

## LSP3 JSON Schema

```json
{
  "LSP3Profile": {
    "name": "string",
    "description": "string",
    "links": [
      { "title": "string", "url": "string" }
    ],
    "tags": ["string"],
    "avatar": [
      {
        "width": 1800,
        "height": 1800,
        "url": "ipfs://...",
        "verification": {
          "method": "keccak256(bytes)",
          "data": "0x<hash>"
        }
      }
    ],
    "backgroundImage": [
      { "width": 1800, "height": 1800, "url": "ipfs://...", "verification": {...} }
    ],
    "profileImage": [
      { "width": 400, "height": 400, "url": "ipfs://...", "verification": {...} }
    ]
  }
}
```

## Code Examples

### Read a UP's profile
```javascript
import { ERC725 } from '@erc725/erc725.js';
import LSP3Schema from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';

const erc725 = new ERC725(
  LSP3Schema, 
  upAddress, 
  'https://42.rpc.thirdweb.com',
  { ipfsGateway: 'https://api.universalprofile.cloud/ipfs/' }
);

const profile = await erc725.fetchData('LSP3Profile');
console.log(profile.value.LSP3Profile.name);
console.log(profile.value.LSP3Profile.description);
```

### Set a UP's profile metadata
```javascript
// 1. Upload JSON to IPFS
const ipfsHash = await uploadToIPFS(profileJSON);
const ipfsUrl = `ipfs://${ipfsHash}`;

// 2. Encode the data
const encoded = erc725.encodeData([{
  keyName: 'LSP3Profile',
  value: {
    json: profileJSON,
    url: ipfsUrl
  }
}]);

// 3. Write to the UP (via KeyManager if applicable)
await up.setData(encoded.keys[0], encoded.values[0]);
```

## Gotchas & Common Mistakes

1. **Multiple image sizes**: Always provide multiple resolutions for images — apps expect an array and pick the best-fitting size.

2. **IPFS gateway**: The LUKSO gateway `https://api.universalprofile.cloud/ipfs/` is for development only. Use Pinata/Infura for production.

3. **Hash verification**: `VerifiableURI` includes a keccak256 hash of the JSON. If the JSON changes but the hash doesn't, the data is considered corrupt. Always re-encode when updating.

4. **SupportedStandards key**: Required for dApps to identify this as an LSP3 profile. Don't forget to set `SupportedStandards:LSP3Profile`.

---

# LSP4 - Digital Asset Metadata

**Status:** Draft  
**No dedicated interface ID** (data schema, required by LSP7 and LSP8)  
**Supported Standard Key:** `0xeafec4d89fa9619884b600008af7b0248d21e28b` (SupportedStandards:LSP4DigitalAsset)

## Purpose

LSP4 defines the **metadata schema** for digital assets (tokens and NFTs) — name, symbol, type, and metadata URI. Similar to LSP3 but for assets rather than profiles.

## ERC725Y Data Keys

```json
// Token name
{
  "name": "LSP4TokenName",
  "key": "0xdeba1e292f8ba88238e10ab3c7f88bd4be4fac56cad5194b6ecceaf653468af1",
  "keyType": "Singleton",
  "valueType": "string"
}

// Token symbol
{
  "name": "LSP4TokenSymbol",
  "key": "0x2f0a68ab07768e01943a599e73362a0e17a63a72e94dd2e384d2c1d4db932756",
  "keyType": "Singleton",
  "valueType": "string"
}

// Token type (0=Token, 1=NFT, 2=Collection)
{
  "name": "LSP4TokenType",
  "key": "0xe0261fa95db2eb3b5439bd033cda66d56b96f92f243a8228fd87550ed7bdfdb3",
  "keyType": "Singleton",
  "valueType": "uint256"
}

// Asset metadata URI
{
  "name": "LSP4Metadata",
  "key": "0x9afb95cacc9f95858ec44aa8c3b685511002e30ae54415823f406128b85b238e",
  "keyType": "Singleton",
  "valueType": "bytes",
  "valueContent": "VerifiableURI"
}

// List of creators' addresses
{
  "name": "LSP4Creators[]",
  "key": "0x114bd03b3a46d48759680d81ebb2b414fda7d030a7105a851867accf1c2352e7",
  "keyType": "Array",
  "valueType": "address"
}

// Map: creator address → (index, interface ID)
{
  "name": "LSP4CreatorsMap:<address>",
  "key": "0x6de85eaf5d982b4e5da00000<address>",
  "keyType": "Mapping",
  "valueType": "(bytes4,uint128)"
}
```

## Token Types

```javascript
import { LSP4_TOKEN_TYPES } from '@lukso/lsp4-contracts';

// LSP4_TOKEN_TYPES.TOKEN    = 0  (fungible token like ERC20)
// LSP4_TOKEN_TYPES.NFT      = 1  (single NFT like ERC721)
// LSP4_TOKEN_TYPES.COLLECTION = 2  (NFT collection like ERC1155)
```

## LSP4 Metadata JSON Structure

```json
{
  "LSP4Metadata": {
    "name": "My Asset",
    "description": "Description here",
    "links": [{ "title": "Website", "url": "https://..." }],
    "icon": [{ "width": 256, "height": 256, "url": "ipfs://...", "verification": {...} }],
    "images": [[{ "width": 1024, "height": 1024, "url": "ipfs://...", "verification": {...} }]],
    "assets": [{ "url": "ipfs://...", "fileType": "glb", "verification": {...} }],
    "attributes": [
      { "key": "Rarity", "value": "Legendary", "type": "string" }
    ]
  }
}
```

## Code Example

```javascript
// Read token name/symbol
const name = await erc725.getData('LSP4TokenName');
const symbol = await erc725.getData('LSP4TokenSymbol');
const tokenType = await erc725.getData('LSP4TokenType');
// tokenType.value: 0=Token, 1=NFT, 2=Collection
```

## Gotchas

1. **LSP4TokenType is critical**: Marketplaces and wallets use this to differentiate fungible tokens from NFTs. Always set it correctly.

2. **LSP4 vs. ERC20 name/symbol**: LSP4 stores name/symbol in ERC725Y storage (not as `name()` / `symbol()` functions). LSP7 also exposes `name()` and `symbol()` functions for backward compatibility.

---

# LSP5 - Received Assets

**Status:** Draft  
**No dedicated interface ID** (data schema for bookkeeping)

## Purpose

LSP5 defines **ERC725Y data keys** to track which LSP7/LSP8 assets a profile has received. These arrays are automatically maintained by the **LSP1 Universal Receiver Delegate** when tokens are transferred to/from a profile.

Think of it as: *the automatic "portfolio" tracker built into every Universal Profile.*

## ERC725Y Data Keys

```json
// Array of received asset contract addresses
{
  "name": "LSP5ReceivedAssets[]",
  "key": "0x6460ee3c0aac563ccbf76d6e1d07bada78e3a9514e6382b736ed3f478ab7b90b",
  "keyType": "Array",
  "valueType": "address"
}

// Map: asset address → (array index, asset interface ID)
{
  "name": "LSP5ReceivedAssetsMap:<address>",
  "key": "0x812c4334633eb816c80d0000<address>",
  "keyType": "Mapping",
  "valueType": "(bytes4,uint128)"  // interfaceId + index in array
}
```

## How It Works

1. You transfer LSP7/LSP8 tokens to a UP
2. The token contract calls `universalReceiver(typeId, data)` on the recipient UP
3. The UP's URD (Universal Receiver Delegate) handles the `LSP7Tokens_RecipientNotification`
4. The URD automatically writes/removes the asset from `LSP5ReceivedAssets[]`
5. When all tokens are sent away, the asset is removed from the array

## Code Examples

```javascript
// Read all received assets
const receivedAssets = await erc725.getData('LSP5ReceivedAssets[]');
// Returns array of asset contract addresses

// Check if a specific asset is in the list
const assetMap = await erc725.getData({
  keyName: 'LSP5ReceivedAssetsMap:<address>',
  dynamicKeyParts: [assetAddress]
});
// assetMap.value = { interfaceId: '0x...', index: 0 }
```

## Gotchas

1. **Auto-managed by URD**: Don't manually write to `LSP5ReceivedAssets[]`. The URD handles it. Manual writes can corrupt the bookkeeping.

2. **Requires URD**: If the profile has no URD set, `LSP5ReceivedAssets[]` won't be updated automatically. The URD from LUKSO's deployment is `LSP1UniversalReceiverDelegateUP`.

3. **Array compaction**: When an asset is removed, the URD moves the last element to the removed index (swap-and-pop). Don't assume array order is chronological.

4. **ERC20 tokens NOT tracked**: Only LSP7 and LSP8 tokens (which call `universalReceiver`) are tracked. ERC20/ERC721 transfers don't trigger `universalReceiver`.

---

# LSP6 - Key Manager

**Status:** Draft  
**Interface ID:** `0x23f34c62`  
**Requires:** ERC165, ERC1271, LSP2, LSP20, LSP25

## Purpose

LSP6 is the **access control layer** for Universal Profiles. It acts as the owner of the UP and enforces permission-based access for multiple controller addresses (EOAs or contracts).

Think of it as: *the ACL/RBAC system for your smart contract account. Instead of one private key having total control, you can grant fine-grained permissions to multiple parties.*

## Key Concepts

- **Target**: The ERC725Account (UP) controlled by this Key Manager
- **Controllers**: Addresses that have permissions to interact with the UP through the KM
- **Permissions**: BitArray flags stored on the UP's ERC725Y store

## Permission System

Permissions are 32-byte BitArrays stored under `AddressPermissions:Permissions:<address>`.

```
CHANGEOWNER:                  0x0000...0001 (bit 0)
ADDCONTROLLER:                0x0000...0002 (bit 1)
EDITPERMISSIONS:              0x0000...0004 (bit 2)
ADDEXTENSIONS:                0x0000...0008 (bit 3)
CHANGEEXTENSIONS:             0x0000...0010 (bit 4)
ADDUNIVERSALRECEIVERDELEGATE: 0x0000...0020 (bit 5)
CHANGEUNIVERSALRECEIVERDELEGATE: 0x0000...0040 (bit 6)
REENTRANCY:                   0x0000...0080 (bit 7)
SUPER_TRANSFERVALUE:          0x0000...0100 (bit 8)
TRANSFERVALUE:                0x0000...0200 (bit 9)
SUPER_CALL:                   0x0000...0400 (bit 10)
CALL:                         0x0000...0800 (bit 11)
SUPER_STATICCALL:             0x0000...1000 (bit 12)
STATICCALL:                   0x0000...2000 (bit 13)
SUPER_DELEGATECALL:           0x0000...4000 (bit 14)
DELEGATECALL:                 0x0000...8000 (bit 15)
DEPLOY:                       0x0001...0000 (bit 16)
SUPER_SETDATA:                0x0002...0000 (bit 17)
SETDATA:                      0x0004...0000 (bit 18)
ENCRYPT:                      0x0008...0000 (bit 19)
DECRYPT:                      0x0010...0000 (bit 20)
SIGN:                         0x0020...0000 (bit 21)
EXECUTE_RELAY_CALL:           0x0040...0000 (bit 22)

// All permissions (admin):
ALL_PERMISSIONS: 0x0000000000000000000000000000000000000000000000000000000000007fff
// (in practice includes all defined bits)
```

### SUPER_ vs. non-SUPER permissions

- `SUPER_CALL`: Can call ANY address, ANY function — no restrictions
- `CALL`: Can only call addresses/functions allowed in `AddressPermissions:AllowedCalls:<address>`
- Same pattern applies to `SUPER_TRANSFERVALUE`, `SUPER_STATICCALL`, `SUPER_DELEGATECALL`, `SUPER_SETDATA`

## ERC725Y Data Keys (stored on the UP)

```json
// List of all controller addresses
{
  "name": "AddressPermissions[]",
  "key": "0xdf30dba06db6a30e65354d9a64c609861f089545ca58c6b4dbe31a5f338cb0e3",
  "keyType": "Array",
  "valueType": "address"
}

// Permissions for a specific controller
{
  "name": "AddressPermissions:Permissions:<address>",
  "key": "0x4b80742de2bf82acb3630000<address>",
  "keyType": "MappingWithGrouping",
  "valueType": "bytes32"  // BitArray
}

// Allowed calls for a specific controller
{
  "name": "AddressPermissions:AllowedCalls:<address>",
  "key": "0x4b80742de2bf393a64c70000<address>",
  "keyType": "MappingWithGrouping",
  "valueType": "(bytes4,address,bytes4,bytes4)[CompactBytesArray]"
  // Each 32-byte tuple: restrictionOp + allowedAddress + allowedInterfaceId + allowedFunction
}

// Allowed ERC725Y data keys for a specific controller
{
  "name": "AddressPermissions:AllowedERC725YDataKeys:<address>",
  "key": "0x4b80742de2bf866c29110000<address>",
  "keyType": "MappingWithGrouping",
  "valueType": "bytes[CompactBytesArray]"
}
```

## Key Interface

```solidity
interface ILSP6 {
    event PermissionsVerified(
        address indexed signer, 
        uint256 indexed value, 
        bytes4 indexed selector
    );

    function target() external view returns (address);
    
    // Direct execution
    function execute(bytes calldata payload) external payable returns (bytes memory);
    function executeBatch(uint256[] calldata values, bytes[] calldata payloads) 
        external payable returns (bytes[] memory);
    
    // Meta-transactions (LSP25)
    function executeRelayCall(bytes memory signature, uint256 nonce, 
        uint256 validityTimestamps, bytes memory payload) 
        external payable returns (bytes memory);
    function executeRelayCallBatch(bytes[] memory signatures, uint256[] memory nonces,
        uint256[] memory validityTimestamps, uint256[] memory values, bytes[] memory payloads)
        external payable returns (bytes[] memory);
    
    // LSP20 verification hooks
    function lsp20VerifyCall(address caller, uint256 value, bytes memory receivedCalldata) 
        external returns (bytes4);
    function lsp20VerifyCallResult(bytes32 callHash, bytes memory callResult) 
        external returns (bytes4);
    
    // Nonces (LSP25)
    function getNonce(address signer, uint128 channel) external view returns (uint256);
    
    // ERC1271
    function isValidSignature(bytes32 hash, bytes memory signature) 
        external view returns (bytes4);
}
```

## Code Examples

### Grant permissions to a controller
```javascript
import { ERC725 } from '@erc725/erc725.js';
import { PERMISSIONS } from '@lukso/lsp6-contracts';

const controllerAddress = '0x...';

// Grant CALL + TRANSFERVALUE permissions
const permissionValue = PERMISSIONS.CALL | PERMISSIONS.TRANSFERVALUE;

const encodedData = erc725.encodeData([
  {
    keyName: 'AddressPermissions:Permissions:<address>',
    dynamicKeyParts: [controllerAddress],
    value: permissionValue.toString(16).padStart(64, '0')
  },
  {
    keyName: 'AddressPermissions[]',
    value: [controllerAddress]  // adds to array
  }
]);

// Execute via the KeyManager
const payload = up.interface.encodeFunctionData('setDataBatch', [
  encodedData.keys, encodedData.values
]);
await keyManager.execute(payload);
```

### Execute through the KeyManager
```javascript
const km = new ethers.Contract(keyManagerAddress, LSP6ABI, signer);

// Execute a call through the KM → UP
const callPayload = up.interface.encodeFunctionData('execute', [
  0,          // CALL operation
  targetAddr,
  ethers.parseEther('0.1'),
  '0x'
]);
await km.execute(callPayload);
```

### Set allowed calls restriction
```javascript
// Allow controller to only call a specific function on a specific contract
import { encodeAllowedCalls } from '@lukso/lsp6-contracts'; // (utility if available)

// Manual encoding: 0x0020 + [4-byte restrict op] + [20-byte address] + [4-byte interfaceId] + [4-byte selector]
const allowedCalls = 
  '0x0020' +                    // 32 bytes total
  '00000002' +                  // callType: CALL
  contractAddress.slice(2) +    // 20 bytes
  'ffffffff' +                  // any interfaceId
  functionSelector.slice(2);    // specific function selector
```

## Gotchas & Common Mistakes

1. **Executing via KM vs. directly**: Always call `keyManager.execute(payload)` where `payload` is the ABI-encoded call to the UP. Don't call the UP directly unless you're the KM or the UP's LSP20 allows it.

2. **SUPER_ permissions bypass restrictions**: `SUPER_CALL` ignores `AllowedCalls`. Only use SUPER_ permissions for fully trusted parties (or the account owner itself).

3. **DELEGATECALL is dangerous**: Granting `DELEGATECALL` lets controllers execute arbitrary code in the UP's context. Only grant to audited contracts.

4. **AllowedCalls empty = blocked**: Setting `AllowedCalls` to empty bytes blocks the controller entirely even if they have CALL permission. Only set `AllowedCalls` if you want to restrict. If left unset, CALL is unrestricted (but SUPER_CALL would still bypass).

5. **REENTRANCY permission**: Required for a controller to re-enter the KM during execution. Without it, re-entrant calls will revert.

6. **Permissions stored on UP, not KM**: Upgrading the Key Manager doesn't lose permissions — they're in the UP's ERC725Y store.

7. **AddressPermissions[] is optional**: You don't have to add a controller to the `AddressPermissions[]` array to give them permissions. The array is informational (for UIs). The actual permissions are in `AddressPermissions:Permissions:<address>`.

8. **EXECUTE_RELAY_CALL permission**: Controllers who will submit relay calls need this permission explicitly.

---

# LSP7 - Digital Asset (Fungible)

**Status:** Draft  
**Interface ID:** See `INTERFACE_IDS.LSP7DigitalAsset` from `@lukso/lsp-smart-contracts`  
**Requires:** ERC165, LSP4

## Purpose

LSP7 is the **fungible token standard** for LUKSO — analogous to ERC20, but with:
- Universal Receiver notifications (sender and receiver are notified)
- Built-in ERC725Y metadata (LSP4)
- `force` parameter to prevent accidental sends to contracts
- Operator system (like ERC20 approve/allowance but cleaner)

## Key Interface

```solidity
interface ILSP7 {
    // Events
    event Transfer(address indexed operator, address indexed from, address indexed to, 
        uint256 amount, bool force, bytes data);
    event OperatorAuthorizationChanged(address indexed operator, address indexed tokenOwner, 
        uint256 amount, bytes operatorNotificationData);
    event OperatorRevoked(address indexed operator, address indexed tokenOwner, 
        bool notified, bytes operatorNotificationData);

    // Queries
    function totalSupply() external view returns (uint256);
    function balanceOf(address tokenOwner) external view returns (uint256);
    function authorizedAmountFor(address operator, address tokenOwner) 
        external view returns (uint256);
    function getOperatorsOf(address tokenOwner) external view returns (address[] memory);

    // Transfers
    function transfer(address from, address to, uint256 amount, bool force, bytes memory data) 
        external;
    function transferBatch(address[] memory from, address[] memory to, uint256[] memory amount, 
        bool[] memory force, bytes[] memory data) external;

    // Operators
    function authorizeOperator(address operator, uint256 amount, bytes memory operatorNotificationData) 
        external;
    function revokeOperator(address operator, bool notify, bytes memory operatorNotificationData) 
        external;
    function increaseAllowance(address operator, uint256 addedAmount, bytes memory operatorNotificationData) 
        external;
    function decreaseAllowance(address operator, uint256 subtractedAmount, bytes memory operatorNotificationData) 
        external;

    // Metadata (LSP4)
    function name() external view returns (string memory);
    function symbol() external view returns (string memory);
    function decimals() external view returns (uint8);
}
```

## Universal Receiver Type IDs

```
// Sent to the RECIPIENT
keccak256('LSP7Tokens_RecipientNotification') 
= 0x20804611b3e2ea21c480dc465142210acf4a2485947541770ec1fb87dee4a55c

// Sent to the SENDER
keccak256('LSP7Tokens_SenderNotification')    
= 0x429ac7a06903dbc9c13dfcb3c9d11df8194581fa047c96d7a4171fc7402958ea

// Sent to the OPERATOR
keccak256('LSP7Tokens_OperatorNotification')  
= 0x386072cc5a58e61263b434c722602eb4ae4ab8ee20f9af44b65a6a33e0efe5ac
```

## Code Examples

### Transfer tokens
```javascript
const lsp7 = new ethers.Contract(tokenAddress, LSP7ABI, signer);

// Transfer 100 tokens
await lsp7.transfer(
  fromAddress,
  toAddress, 
  ethers.parseUnits('100', 18),  // amount
  true,    // force: true = allow sending to EOAs and contracts without URD
  '0x'     // data
);
```

### Authorize an operator (like ERC20 approve)
```javascript
await lsp7.authorizeOperator(
  operatorAddress,
  ethers.parseUnits('1000', 18),  // max amount
  '0x'  // notification data
);
```

### Deploy an LSP7 token
```solidity
// Solidity example
import "@lukso/lsp7-contracts/contracts/LSP7DigitalAsset.sol";

contract MyToken is LSP7DigitalAsset {
    constructor(
        string memory name_,
        string memory symbol_,
        address newOwner,
        uint256 lsp4TokenType_,  // 0 = TOKEN
        bool isNonDivisible_     // false = 18 decimals, true = 0 decimals
    ) LSP7DigitalAsset(name_, symbol_, newOwner, lsp4TokenType_, isNonDivisible_) {
        // Mint initial supply to owner
        _mint(newOwner, 1_000_000 * 10**18, true, "");
    }
}
```

## Gotchas & Common Mistakes

1. **`force` parameter**: If `force = false` and the recipient is a contract without `universalReceiver`, the transfer **reverts**. Use `force = true` for sending to EOAs or unknown contracts. Use `force = false` to ensure only LSP1-aware contracts receive tokens.

2. **transfer() takes `from` not `msg.sender`**: Unlike ERC20's `transfer(to, amount)`, LSP7 requires `transfer(from, to, amount, force, data)`. Operators specify the `from` address.

3. **Operator vs. ERC20 allowance**: LSP7 operators don't have unlimited approval by default — you specify the exact authorized amount. Use `authorizeOperator` not `approve`.

4. **Decimals**: LSP7 uses `decimals()` function (like ERC20). By default 18. `isNonDivisible = true` sets decimals to 0.

5. **Backward compat interface IDs**: Old LSP7 deployments (v0.12.0, v0.14.0) have different interface IDs. Check `INTERFACE_ID_LSP7_V0_12_0` and `INTERFACE_ID_LSP7_V0_14_0` for compatibility with old tokens.

6. **URD failures don't revert transfers**: The transfer always completes even if the recipient's URD throws.

---

# LSP8 - Identifiable Digital Asset (NFT)

**Status:** Draft  
**Interface ID:** See `INTERFACE_IDS.LSP8IdentifiableDigitalAsset` from `@lukso/lsp-smart-contracts`  
**Requires:** ERC165, LSP4

## Purpose

LSP8 is the **NFT standard** for LUKSO — analogous to ERC721/ERC1155, but with:
- Flexible tokenId formats (uint256, address, bytes32, hash, etc.)
- Per-token metadata via ERC725Y
- Universal Receiver notifications
- Operator system

## Token ID Formats

```javascript
import { LSP8_TOKEN_ID_FORMAT } from '@lukso/lsp8-contracts';

// LSP8_TOKEN_ID_FORMAT:
// NUMBER   = 0  (uint256 token ID, padded to bytes32)
// STRING   = 1  (UTF-8 string, hashed to bytes32)
// ADDRESS  = 2  (Ethereum address, padded to bytes32)
// UNIQUE_ID = 3 (custom unique 32-byte ID)
// HASH     = 4  (keccak256 hash)
// MIXED_DEFAULT_NUMBER = 100  (fallback to NUMBER)
```

## Key Interface

```solidity
interface ILSP8 {
    // Events
    event Transfer(address indexed operator, address indexed from, address indexed to, 
        bytes32 indexed tokenId, bool force, bytes data);
    event OperatorAuthorizationChanged(address indexed operator, address indexed tokenOwner, 
        bytes32 indexed tokenId, bytes operatorNotificationData);
    event OperatorRevoked(address indexed operator, address indexed tokenOwner, 
        bytes32 indexed tokenId, bool notified, bytes operatorNotificationData);
    event TokenIdDataChanged(bytes32 indexed tokenId, bytes32 indexed dataKey, bytes dataValue);

    // Queries
    function totalSupply() external view returns (uint256);
    function balanceOf(address tokenOwner) external view returns (uint256);
    function tokenOwnerOf(bytes32 tokenId) external view returns (address);
    function tokenIdsOf(address tokenOwner) external view returns (bytes32[] memory);
    function isOperatorFor(address operator, bytes32 tokenId) external view returns (bool);
    function getOperatorsOf(bytes32 tokenId) external view returns (address[] memory);

    // Transfers
    function transfer(address from, address to, bytes32 tokenId, bool force, bytes memory data) 
        external;
    function transferBatch(address[] memory from, address[] memory to, bytes32[] memory tokenId, 
        bool[] memory force, bytes[] memory data) external;

    // Operators
    function authorizeOperator(address operator, bytes32 tokenId, 
        bytes memory operatorNotificationData) external;
    function revokeOperator(address operator, bytes32 tokenId, bool notify, 
        bytes memory operatorNotificationData) external;

    // Per-token metadata (ERC725Y on the token contract)
    function getDataForTokenId(bytes32 tokenId, bytes32 dataKey) 
        external view returns (bytes memory);
    function getDataBatchForTokenIds(bytes32[] memory tokenIds, bytes32[] memory dataKeys) 
        external view returns (bytes[] memory);
    function setDataForTokenId(bytes32 tokenId, bytes32 dataKey, bytes memory dataValue) 
        external;
    function setDataBatchForTokenIds(bytes32[] memory tokenIds, bytes32[] memory dataKeys, 
        bytes[] memory dataValues) external;
}
```

## Universal Receiver Type IDs

```
keccak256('LSP8Tokens_RecipientNotification') 
= 0xb23eae7a994373421bf4f29f7206d7ded2d97af07b405eb6769bbfb0bbd1b9da

keccak256('LSP8Tokens_SenderNotification')    
= 0x5b84d9550adb7000df7bee717735ecd3af48ea3f66c6886d52e8227548fb1b60

keccak256('LSP8Tokens_OperatorNotification')
= 0x8a1c15a8799f71b547e08e2bcb2e85257e81b0a07eee2ce6712549eef1f00970
```

## ERC725Y Data Keys (per-token metadata)

```json
// Per-token metadata URI
{
  "name": "LSP8MetadataTokenURI:<bytes32>",
  "key": "0x1339e76a390b7b9ec9010000<tokenId>",
  "keyType": "Mapping",
  "valueType": "bytes"
}

// Collection-level metadata
{
  "name": "LSP4Metadata",
  "key": "0x9afb95cacc9f95858ec44aa8c3b685511002e30ae54415823f406128b85b238e"
}
```

## Code Examples

### Transfer an NFT
```javascript
const lsp8 = new ethers.Contract(nftAddress, LSP8ABI, signer);

// tokenId must be bytes32
const tokenId = ethers.zeroPadValue(ethers.toBeHex(1), 32); // tokenId = 1

await lsp8.transfer(fromAddress, toAddress, tokenId, false, '0x');
```

### Deploy an LSP8 NFT collection
```solidity
import "@lukso/lsp8-contracts/contracts/LSP8IdentifiableDigitalAsset.sol";
import { _LSP8_TOKENID_FORMAT_NUMBER } from "@lukso/lsp8-contracts/contracts/LSP8Constants.sol";
import { _LSP4_TOKEN_TYPE_NFT } from "@lukso/lsp4-contracts/contracts/LSP4Constants.sol";

contract MyNFT is LSP8IdentifiableDigitalAsset {
    uint256 private _tokenIdCounter;

    constructor(address owner) 
        LSP8IdentifiableDigitalAsset(
            "My NFT Collection",
            "MNFT",
            owner,
            _LSP4_TOKEN_TYPE_NFT,        // token type
            _LSP8_TOKENID_FORMAT_NUMBER  // tokenId format
        ) {}

    function mint(address to, bytes memory data) external onlyOwner {
        _tokenIdCounter++;
        bytes32 tokenId = bytes32(_tokenIdCounter);
        _mint(to, tokenId, true, data);
    }
}
```

### Set per-token metadata
```javascript
const tokenId = ethers.zeroPadValue('0x01', 32);
const metadataKey = '0x9afb95cacc9f95858ec44aa8c3b685511002e30ae54415823f406128b85b238e';
const encodedMetadata = encodeVerifiableURI(metadataJson, ipfsUrl);

await lsp8.setDataForTokenId(tokenId, metadataKey, encodedMetadata);
```

## Gotchas & Common Mistakes

1. **tokenId is always bytes32**: Even if your token IDs are sequential integers, you must zero-pad them: `bytes32(uint256(1))`.

2. **`force` parameter**: Same as LSP7 — `false` means recipient must support `universalReceiver`, `true` allows any address.

3. **Token ID format matters**: Set `LSP8TokenIdFormat` in your LSP4 metadata or as a data key so wallets know how to display token IDs.

4. **Per-token data is set on the collection contract**: Not on individual token contracts. Use `setDataForTokenId(tokenId, key, value)`.

5. **Operator is per-tokenId**: Unlike ERC721 where you approve an operator for ALL tokens, LSP8 operators are granted per tokenId.

---

# LSP9 - Vault

**Status:** Draft  
**Interface ID:** See `INTERFACE_IDS.LSP9Vault` from `@lukso/lsp-smart-contracts`  
**Supported Standard Key:** `0xeafec4d89fa9619884b6000074c7e3b7b4c6ee80a46a86d4cf3dd8e7dc7b7a43`  
**Requires:** ERC165, ERC725X, ERC725Y, LSP1, LSP2, LSP14, LSP17

## Purpose

LSP9 is a **Vault** — a separate smart contract account that can be owned by a Universal Profile. It functions similarly to an LSP0 account but without LSP6 Key Manager integration. Use it to:
- Isolate assets from the main UP (security compartmentalization)
- Hold assets that should be separately managed
- Create sub-accounts for the UP

## Key Difference from LSP0

| Feature | LSP0 (UP) | LSP9 (Vault) |
|---------|-----------|--------------|
| Owned by | KeyManager or EOA | UP or EOA |
| Access control | LSP6 KeyManager | Owner-only |
| LSP20 support | Yes | No |
| Primary use | Identity/profile | Asset isolation |

## Key Interface

```solidity
interface ILSP9 {
    // ERC725X
    function execute(uint256 operationType, address target, uint256 value, bytes memory data)
        external payable returns (bytes memory);
    function executeBatch(uint256[] memory operationsType, address[] memory targets,
        uint256[] memory values, bytes[] memory datas)
        external payable returns (bytes[] memory);

    // ERC725Y
    function getData(bytes32 dataKey) external view returns (bytes memory);
    function getDataBatch(bytes32[] memory dataKeys) external view returns (bytes[] memory);
    function setData(bytes32 dataKey, bytes memory dataValue) external payable;
    function setDataBatch(bytes32[] memory dataKeys, bytes[] memory dataValues) external payable;

    // LSP1
    function universalReceiver(bytes32 typeId, bytes memory receivedData)
        external payable returns (bytes memory);

    // LSP14
    function owner() external view returns (address);
    function transferOwnership(address newOwner) external;
    function acceptOwnership() external;

    receive() external payable;
}
```

## LSP1 Type IDs (Vault-specific)

```
keccak256('LSP9OwnershipTransferStarted')
= 0xaefd43f45fed1bcd8992f23c803b6f4ec45cf6b62b0d5d4a7c9f9f9e7fffbc3

keccak256('LSP9OwnershipTransferred_SenderNotification')
= 0x0c622e58e6b7089ae35f1af1c86d997be92fcdd8c9509652022d41aa65169471

keccak256('LSP9OwnershipTransferred_RecipientNotification')
= 0x79855c97dbc259ce395421d933d7bc0699b0f1561f988f09a9e8633fd542fe5c
```

## ERC725Y Data Keys (LSP9-specific)

```json
{
  "name": "SupportedStandards:LSP9Vault",
  "key": "0xeafec4d89fa9619884b6000074c7e3b7b4c6ee80a46a86d4cf3dd8e7dc7b7a43",
  "valueContent": "0x74c7e3b7"
}

// LSP1 Universal Receiver Delegate
{
  "name": "LSP1UniversalReceiverDelegate",
  "key": "0x0cfc51aec37c55a4d0b1a65c6255c4bf2fbdf6277f3cc0730c45b828b6db8b47"
}
```

## Code Example

```javascript
// Deploy a vault and link it to a UP
const LSP9VaultFactory = await ethers.getContractFactory("LSP9Vault");
const vault = await LSP9VaultFactory.deploy(upAddress); // UP becomes owner

// Track the vault in the UP's LSP10ReceivedVaults
// (this is done automatically if the UP has a URD that handles LSP9)

// Execute from the vault (through UP)
// UP must first execute to the vault, and vault executes outward
const vaultExecutePayload = vault.interface.encodeFunctionData('execute', [
  0, targetAddress, ethers.parseEther('0.1'), '0x'
]);
const upExecutePayload = up.interface.encodeFunctionData('execute', [
  0, vaultAddress, 0, vaultExecutePayload
]);
await keyManager.execute(upExecutePayload);
```

## Gotchas

1. **No Key Manager**: The vault's owner (typically the UP) has full control. The UP's KM permissions still apply when calling through the UP.

2. **LSP10 tracking**: Vaults are tracked in `LSP10ReceivedVaults[]` array (analogous to LSP5 for tokens).

3. **Asset isolation**: Tokens sent to a vault are tracked separately from the main UP's LSP5 list.

---

# LSP10 - Received Vaults

**Status:** Draft  
**No dedicated interface ID** (data schema)

## Purpose

LSP10 defines **ERC725Y data keys** to track LSP9 Vault addresses owned by a profile. Auto-maintained by the URD when vault ownership is transferred.

## ERC725Y Data Keys

```json
// Array of vault addresses
{
  "name": "LSP10ReceivedVaults[]",
  "key": "0x55482936e01da86729a45d2b87a6b1d3bc582bea0ec00e38bdb340e3af6f9f06",
  "keyType": "Array",
  "valueType": "address"
}

// Map: vault address → (array index, interface ID)
{
  "name": "LSP10ReceivedVaultsMap:<address>",
  "key": "0x192448c3c0f88c7f238c0000<address>",
  "keyType": "Mapping",
  "valueType": "(bytes4,uint128)"
}
```

## Usage

```javascript
// Read all vaults owned by a UP
const vaults = await erc725.getData('LSP10ReceivedVaults[]');
```

---

# LSP11 - Basic Social Recovery

**Status:** Draft  
**Interface ID:** `0x049a28f1`

## Purpose

LSP11 provides a **social recovery mechanism** for smart contract accounts. If you lose access to your account, a set of trusted "guardians" can help you recover it by voting for a new owner.

## How It Works

1. Deploy an LSP11 contract linked to your UP/KM
2. Add trusted guardians (friends, family, other wallets)
3. Set a threshold (minimum guardians needed to recover)
4. If you lose access: guardians vote for a new controller address
5. Once threshold met, the new controller is set and recovery is applied

## Key Interface

```solidity
interface ILSP11BasicSocialRecovery {
    function target() external view returns (address);
    
    // Guardian management (only owner)
    function addGuardian(address newGuardian) external;
    function removeGuardian(address existingGuardian) external;
    function setThreshold(uint256 newThreshold) external;
    
    // Recovery process
    function voteForRecovery(address newController) external;
    function recoverOwnership(address newController) external;
    function getVotes(address newController) external view returns (address[] memory);
    
    // Queries
    function getGuardians() external view returns (address[] memory);
    function getGuardiansThreshold() external view returns (uint256);
    function isGuardian(address recoverer) external view returns (bool);
}
```

## Code Example

```javascript
// Deploy social recovery
const LSP11SocialRecovery = await ethers.getContractFactory("LSP11BasicSocialRecovery");
const recovery = await LSP11SocialRecovery.deploy(
  keyManagerAddress  // target: the KM controlling the UP
);

// Add guardians
await recovery.addGuardian(guardian1);
await recovery.addGuardian(guardian2);
await recovery.addGuardian(guardian3);
await recovery.setThreshold(2);  // 2/3 required

// When recovery needed, each guardian votes:
await recovery.connect(guardian1Signer).voteForRecovery(newControllerAddress);
await recovery.connect(guardian2Signer).voteForRecovery(newControllerAddress);

// Once threshold met, apply recovery:
await recovery.recoverOwnership(newControllerAddress);
```

## Gotchas

1. **Guardians must be trusted**: Enough guardians can change the account owner. Choose carefully.

2. **Recovery resets**: Once recovery is executed, the vote count resets. Guardians must vote again for subsequent recoveries.

3. **The recovery contract needs permissions**: It must have `CHANGEOWNER` permission on the Key Manager's target UP.

---

# LSP12 - Issued Assets

**Status:** Draft  
**No dedicated interface ID** (data schema)

## Purpose

LSP12 defines **ERC725Y data keys** to track which LSP7/LSP8 assets a profile has issued (created/deployed). It's the "creator" counterpart to LSP5 (received assets).

## ERC725Y Data Keys

```json
// Array of issued asset contract addresses
{
  "name": "LSP12IssuedAssets[]",
  "key": "0x7c8c3416d6cda87cd42c71ea1843df28ac4850354f988d55ee2eaa47b6dc05cd",
  "keyType": "Array",
  "valueType": "address"
}

// Map: asset address → (array index, interface ID)
{
  "name": "LSP12IssuedAssetsMap:<address>",
  "key": "0x74ac2555c10b9349e78f0000<address>",
  "keyType": "Mapping",
  "valueType": "(bytes4,uint128)"
}
```

## Usage

```javascript
// After deploying an LSP7/LSP8 token, register it as an issued asset
const encodedData = erc725.encodeData([{
  keyName: 'LSP12IssuedAssets[]',
  value: [myTokenAddress]
}]);
await up.setDataBatch(encodedData.keys, encodedData.values);
```

---

# LSP14 - Ownable2Step

**Status:** Draft  
**Interface ID:** See `INTERFACE_IDS.LSP14Ownable2Step`  
**Requires:** ERC165

## Purpose

LSP14 is a **2-step ownership transfer** standard. Unlike OpenZeppelin's `Ownable` where `transferOwnership` immediately transfers control, LSP14 requires the new owner to explicitly accept — preventing accidental ownership loss.

The new owner also receives a notification via LSP1 if it supports `universalReceiver`.

## Key Interface

```solidity
interface ILSP14 {
    // Events
    event OwnershipTransferStarted(address indexed previousOwner, address indexed newOwner);
    event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);
    event RenounceOwnershipStarted();
    event OwnershipRenounced();

    function owner() external view returns (address);
    function pendingOwner() external view returns (address);
    
    // Step 1: Initiate transfer
    function transferOwnership(address newOwner) external;
    
    // Step 2: Accept transfer (called by new owner)
    function acceptOwnership() external;
    
    // 2-step renounce (must call twice in different blocks)
    function renounceOwnership() external;
}
```

## LSP1 Type IDs

```
keccak256('LSP14OwnershipTransferStarted')
= 0xee9a7c0924f740a2ca33d59b7f0c2929821ea9837ce043ce91c1823e9c4e52c0

keccak256('LSP14OwnershipTransferred_SenderNotification')
= 0xa124442e1cc7b52d8e2ede2787d43527dabb7ae7d7d2467d906b87c47e0f983a

keccak256('LSP14OwnershipTransferred_RecipientNotification')
= 0xe32c7debcb817925ba4883fdbfc52797187f28f73f860641dab1a68d9b32902c
```

## Gotchas

1. **`renounceOwnership()` requires TWO calls**: First call starts a countdown, second call (in a later block) finalizes renunciation. This prevents accidental renunciation.

2. **`pendingOwner` must call `acceptOwnership()`**: If the new owner never calls accept, ownership doesn't change. The pending owner can be cancelled by calling `transferOwnership` again.

3. **LSP0/LSP9 override type IDs**: LSP0 and LSP9 use their own `OwnershipTransfer` type IDs to avoid confusion between the UP's ownership notifications and the base LSP14 ones.

---

# LSP16 - Universal Factory

**Status:** Draft  
**Deployed at:** `0x1600000000000000000000000000000000000000` (LUKSO Mainnet)

## Purpose

LSP16 provides a **universal deterministic contract deployment** factory. Any contract can be deployed to the same address on all EVM chains using CREATE2, making it easy to have consistent contract addresses across networks.

## Key Interface

```solidity
interface ILSP16UniversalFactory {
    event ContractCreated(
        address indexed contractCreated,
        bytes32 indexed providedSalt,
        bytes32 generatedSalt,
        bool indexed initialized,
        bytes initializeCalldata
    );

    // Deploy regular contract (no init call)
    function deployCreate2(
        bytes memory creationBytecode,
        bytes32 providedSalt
    ) external payable returns (address contractAddress);

    // Deploy + initialize (init-based upgradeable contracts)
    function deployCreate2AndInitialize(
        bytes memory creationBytecode,
        bytes32 providedSalt,
        bytes memory initializeCalldata,
        uint256 constructorMsgValue,
        uint256 initializeCalldataMsgValue
    ) external payable returns (address contractAddress);

    // Deploy ERC1167 proxy
    function deployERC1167Proxy(
        address implementationContract,
        bytes32 providedSalt
    ) external payable returns (address proxy);

    // Deploy ERC1167 proxy + initialize
    function deployERC1167ProxyAndInitialize(
        address implementationContract,
        bytes32 providedSalt,
        bytes memory initializeCalldata
    ) external payable returns (address proxy);

    // Compute addresses before deployment
    function computeAddress(bytes memory creationBytecode, bytes32 providedSalt, 
        bool initializable, bytes memory initializeCalldata) 
        external view returns (address);

    function computeERC1167Address(address implementationContract, bytes32 providedSalt, 
        bool initializable, bytes memory initializeCalldata) 
        external view returns (address proxy);
}
```

## Code Example

```javascript
const factory = new ethers.Contract(
  '0x1600000000000000000000000000000000000000',
  LSP16ABI,
  signer
);

// Compute address first
const salt = ethers.id('my-unique-salt');
const computedAddress = await factory.computeAddress(bytecode, salt, false, '0x');

// Deploy
await factory.deployCreate2(bytecode, salt);
```

## Gotchas

1. **Salt is generated internally**: LSP16 combines your provided salt with the `msg.sender` address (hashed together). So the same salt from different deployers yields different addresses. This prevents front-running/squatting.

2. **Same address across chains**: If you use the same bytecode + salt from the same address, the deployment will be at the same address on any EVM chain where LSP16 is deployed.

---

# LSP17 - Contract Extension

**Status:** Draft  
**Interface IDs:**
- `LSP17Extendable`: contract that can be extended
- `LSP17Extension`: contract that IS an extension

## Purpose

LSP17 allows smart contracts to **add new functions after deployment** without upgrading or migrating. When a function is called that doesn't exist on the contract, it checks ERC725Y for an extension address and forwards the call there.

Think of it as: *a dynamic plugin system for smart contracts.*

## How It Works

```
User calls: myUP.unknownFunction(args)
    → fallback() triggered
    → UP reads: LSP17Extension:0xabcd1234 (the function selector)
    → If extension found: delegatecall-like forward to extension contract
    → Extension executes with: originalCalldata + msg.sender (20 bytes) + msg.value (32 bytes)
    → Result returned to user
```

## ERC725Y Data Key Format

```json
{
  "name": "LSP17Extension:<bytes4>",
  "key": "0xcee78b4094da860110960000<bytes4>",
  "keyType": "Mapping",
  "valueType": "(address, bytes1)"
}
```

Value encoding:
- 20 bytes: extension contract address
- Optional 21st byte: `0x01` = forward ETH value to extension; no 21st byte = keep ETH in UP

## Writing an Extension

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@lukso/lsp17contractextension-contracts/contracts/LSP17Extension.sol";

contract MyExtension is LSP17Extension {
    // The extension gets the original call's msg.sender and msg.value
    // appended to calldata as the last 52 bytes
    
    function myNewFunction(uint256 param) external {
        // Access original caller (not the UP) via _extendableMsgSender()
        address originalCaller = _extendableMsgSender();
        // Access original value via _extendableMsgValue()
        uint256 sentValue = _extendableMsgValue();
        
        // Your custom logic here
    }
}
```

## Register an Extension on a UP

```javascript
// 1. Deploy the extension
const MyExtension = await ethers.getContractFactory('MyExtension');
const ext = await MyExtension.deploy();

// 2. Compute the data key
const functionSelector = ext.interface.getFunction('myNewFunction').selector;
// extensionKey = 0xcee78b4094da860110960000 + functionSelector (no 0x, padded)
const extensionKey = '0xcee78b4094da860110960000' + functionSelector.slice(2);

// 3. Set the extension on the UP
await up.setData(extensionKey, ext.target);

// 4. Now anyone can call myNewFunction() on the UP address
const upAsExtension = new ethers.Contract(upAddress, MyExtensionABI, signer);
await upAsExtension.myNewFunction(42);
```

## Gotchas

1. **Extensions run in the UP's context** (via regular CALL, not DELEGATECALL). The extension is a separate contract that receives forwarded calls. It cannot directly modify the UP's storage.

2. **52 bytes appended to calldata**: The UP appends `msg.sender` (20 bytes) + `msg.value` (32 bytes) to every extension call. Your extension must use `_extendableMsgSender()` / `_extendableMsgValue()` to read these, not `msg.sender` / `msg.value` directly.

3. **`supportsInterface` can be extended**: Store an extension at `LSP17Extension:0x01ffc9a7` (the `supportsInterface` selector) to add new interface IDs to your UP.

4. **Value forwarding must be explicit**: Add `0x01` as a 21st byte to forward ETH to the extension. Otherwise ETH stays in the UP.

---

# LSP19 - Beacon Proxy

**Status:** Draft  
**No deployed singleton** (pattern/standard)

## Purpose

LSP19 defines a **Beacon Proxy pattern** for upgradeable contracts on LUKSO. Instead of each proxy holding its own implementation address, all proxies point to a "beacon" contract that holds the implementation. Upgrading the beacon upgrades all proxies simultaneously.

Useful for deploying many instances of the same contract (e.g., many UP instances) where you want to upgrade all at once.

## When to Use

- **LSP19 Beacon**: When you need to upgrade many contracts at once (e.g., a dApp with thousands of user contracts)
- **Regular ERC1167 proxy**: When each contract is independently upgraded
- **No proxy**: When immutability is required

---

# LSP20 - Call Verification

**Status:** Draft  
**Interface IDs:**
- `LSP20CallVerification`: contract that uses verification (e.g., the UP)
- `LSP20CallVerifier`: contract that does verification (e.g., the Key Manager)

## Purpose

LSP20 defines a **call verification protocol** that allows any address to call "owner-restricted" functions on a contract, as long as the owner contract approves the call. This is how non-owners can interact with a UP directly — the UP asks its owner (KM) to approve the call.

Think of it as: *the middleware between the UP and KeyManager that enables the UP to accept calls from anyone (not just the KM).*

## How It Works

```
Caller (not owner) → UP.setData(key, value)
    → UP sees caller is not owner
    → UP calls: owner.lsp20VerifyCall(caller, value, calldata)  [= KM.lsp20VerifyCall]
    → KM checks permissions for caller
    → KM returns: 0x1a238 + 0x01 (success + need post-verify)
    → UP executes setData
    → UP calls: owner.lsp20VerifyCallResult(callHash, result)
    → KM releases reentrancy guard
```

## Key Interface

```solidity
interface ILSP20CallVerification {
    // Called before execution
    function lsp20VerifyCall(
        address requestor,   // contract implementing LSP20 (the UP)
        address target,      // same as requestor in most cases
        address caller,      // original msg.sender
        uint256 value,
        bytes memory receivedCalldata
    ) external returns (bytes4 returnedStatus);

    // Called after execution (if 4th byte of returnedStatus is 0x01)
    function lsp20VerifyCallResult(
        bytes32 callHash,
        bytes memory result
    ) external returns (bytes4);
}
```

## Return Value Encoding

```
lsp20VerifyCall must return:
  First 3 bytes: keccak256("lsp20VerifyCall(address,address,address,uint256,bytes)")[0..2]
  4th byte: 0x00 = don't call lsp20VerifyCallResult
            0x01 = DO call lsp20VerifyCallResult after execution
```

## Gotchas

1. **Only called when caller ≠ owner**: If the owner calls the UP directly, no LSP20 verification happens.

2. **Reentrancy guard**: The KM sets a reentrancy lock during verification. Calls that re-enter during execution need `REENTRANCY` permission.

3. **`acceptOwnership` uses pending owner**: LSP20 verification for `acceptOwnership` is done against the pending owner's contract (if it's a contract), not the current owner.

---

# LSP23 - Linked Contracts Factory

**Status:** Draft  
**Deployed at:** `0x2300000A84D25dF63081feAa37ba6b62C4c89a30` (LUKSO Mainnet)

## Purpose

LSP23 solves the **circular dependency problem** in contract deployment. When deploying two contracts that need each other's addresses at construction time (like a UP and its KeyManager), LSP23 handles deploying them in the correct order and linking them together.

Used by the LUKSO Universal Profile Factory to deploy UP + KM pairs.

## Key Interface

```solidity
interface ILSP23LinkedContractsFactory {
    event DeployedContracts(
        address indexed primaryContract,
        address indexed secondaryContract,
        ...
    );

    struct PrimaryContractDeployment {
        bytes32 salt;
        uint256 fundingAmount;
        bytes creationBytecode;
    }

    struct SecondaryContractDeployment {
        uint256 fundingAmount;
        bytes creationBytecode;
        bool addPrimaryContractAddress;   // append primary address to constructor args?
        bytes extraConstructorParams;
    }

    // Deploy two regular contracts (linked)
    function deployContracts(
        PrimaryContractDeployment calldata primaryContractDeployment,
        SecondaryContractDeployment calldata secondaryContractDeployment,
        address postDeploymentModule,
        bytes calldata postDeploymentModuleCalldata
    ) external payable returns (address primaryContractAddress, address secondaryContractAddress);

    // Deploy two ERC1167 proxy contracts (linked)
    function deployERC1167Proxies(
        PrimaryContractDeploymentInit calldata primaryContractDeploymentInit,
        SecondaryContractDeploymentInit calldata secondaryContractDeploymentInit,
        address postDeploymentModule,
        bytes calldata postDeploymentModuleCalldata
    ) external payable returns (address primaryContractAddress, address secondaryContractAddress);

    // Compute addresses before deployment
    function computeAddresses(...) external view returns (address, address);
    function computeERC1167Addresses(...) external view returns (address, address);
}

interface IPostDeploymentModule {
    function executePostDeployment(
        address primaryContractAddress,
        address secondaryContractAddress,
        bytes calldata postDeploymentModuleCalldata
    ) external;
}
```

## Code Example (deploy UP + KM pair)

```javascript
const factory = new ethers.Contract(
  '0x2300000A84D25dF63081feAa37ba6b62C4c89a30',
  LSP23ABI,
  signer
);

// Primary = UP, Secondary = KeyManager (KM needs UP address)
const salt = ethers.randomBytes(32);

// Compute addresses first
const [upAddr, kmAddr] = await factory.computeERC1167Addresses(
  { salt, fundingAmount: 0, implementationContract: upImplementation, initializationCalldata: '0x' },
  { fundingAmount: 0, implementationContract: kmImplementation, 
    initializationCalldata: km_init_without_target, 
    addPrimaryContractAddress: true,  // appends UP address
    extraInitializationParams: '0x' },
  postDeploymentModuleAddress,
  postDeploymentCalldata
);

// Deploy
await factory.deployERC1167Proxies(...);
```

## Gotchas

1. **Salt includes `msg.sender`**: The factory hashes your salt with `msg.sender` to prevent front-running. You can't deploy the exact same setup from a different address.

2. **Post-deployment module**: This is where you set up permissions and other post-deploy config. The LUKSO UP factory uses this to set the UP's LSP3 metadata and KM permissions.

3. **Order matters**: Primary contract is deployed first, then secondary (with primary's address). The secondary can receive the primary's address as a constructor param.

---

# LSP25 - Execute Relay Call

**Status:** Draft  
**Interface ID:** `0x5ac79908`  
**LSP25_VERSION:** `25`

## Purpose

LSP25 provides a **meta-transaction framework** — allows users to sign transactions off-chain and have someone else (a relayer) submit them on-chain, paying the gas. This enables gasless transactions on LUKSO.

The LSP6 KeyManager implements LSP25, enabling gasless interactions with Universal Profiles.

## Key Interface

```solidity
interface ILSP25ExecuteRelayCall {
    function getNonce(address signer, uint128 channel) external view returns (uint256);
    
    function executeRelayCall(
        bytes memory signature,
        uint256 nonce,
        uint256 validityTimestamps,
        bytes memory payload
    ) external payable returns (bytes memory);

    function executeRelayCallBatch(
        bytes[] memory signatures,
        uint256[] memory nonces,
        uint256[] memory validityTimestamps,
        uint256[] memory values,
        bytes[] memory payloads
    ) external payable returns (bytes[] memory);
}
```

## Signature Format

The message to sign uses EIP-191 version 0:

```
Hash = keccak256(
  0x19            // EIP-191 prefix
  0x00            // version 0
  <KM address>    // the Key Manager that will execute
  25              // LSP25_VERSION (uint256)
  <chainId>       // chain ID
  <nonce>         // from getNonce()
  <validityTimestamps>  // uint256: [startTimestamp (uint128) | endTimestamp (uint128)]
  <value>         // LYX to send
  <payload>       // the ABI-encoded function call
)
```

All values are PACKED (not ABI-encoded/padded).

## Multi-Channel Nonces

Nonces are `uint256` = `channelId (uint128) | nonceId (uint128)`:
- Left 128 bits = channel ID (you choose, 0 to 2^128-1)
- Right 128 bits = nonce ID within that channel (auto-incremented)

**Why channels?** Different channels execute independently. You can sign a nonce on channel 5 and it will execute even if channel 0 has pending transactions. Sequential within a channel, but parallel across channels.

## Code Example

```javascript
import { ethers } from 'ethers';

// 1. Get the nonce for channel 0
const channel = 0;
const nonce = await keyManager.getNonce(signerAddress, channel);

// 2. Build validity timestamps (0 = always valid)
const validityTimestamps = 0;

// 3. Build the payload (e.g., execute a transfer through UP)
const upPayload = up.interface.encodeFunctionData('execute', [
  0, recipientAddress, ethers.parseEther('0.1'), '0x'
]);

// 4. Build the hash to sign
const chainId = 42; // LUKSO mainnet
const LSP25_VERSION = 25;

const encodedMessage = ethers.solidityPacked(
  ['uint8', 'uint8', 'address', 'uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes'],
  [0x19, 0x00, keyManagerAddress, LSP25_VERSION, chainId, nonce, validityTimestamps, 
   ethers.parseEther('0.1'), upPayload]
);
const hash = ethers.keccak256(encodedMessage);

// 5. Sign the hash
const signature = await signer.signMessage(ethers.getBytes(hash));

// 6. Submit via relayer (anyone can call this)
await keyManager.connect(relayerSigner).executeRelayCall(
  signature,
  nonce,
  validityTimestamps,
  upPayload,
  { value: ethers.parseEther('0.1') }
);
```

## Validity Timestamps

```javascript
// Pack two uint128 timestamps into one uint256
const now = Math.floor(Date.now() / 1000);
const startTimestamp = 0; // valid immediately
const endTimestamp = now + 3600; // expires in 1 hour

// Pack: startTimestamp in upper 128 bits, endTimestamp in lower 128 bits
const validityTimestamps = (BigInt(startTimestamp) << 128n) | BigInt(endTimestamp);
```

## Gotchas

1. **Signer needs `EXECUTE_RELAY_CALL` permission**: The address that signed the relay call must have this permission on the KM. Without it, the relay call fails.

2. **Gas is NOT in the signature**: Unlike some EIP-2612 style signatures, LSP25 doesn't include gas parameters. The relayer sets the gas.

3. **Channel selection matters**: For ordered execution use channel 0. For independent parallel transactions, use different channels.

4. **nonce >> 128 gives channel**: The `getNonce` function returns the full 256-bit combined nonce. The channel's base is `uint128(nonce >> 128) << 128`.

5. **Replay protection**: Nonces are per-signer per-channel. A used nonce can never be reused. Expired timestamps also prevent replay.

6. **Value must be forwarded by relayer**: If the payload needs to send LYX, the relayer must include `msg.value` equal to the `value` in the relay call signature.

---

# LSP26 - Follower System

**Status:** Draft  
**Deployed at:** `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` (LUKSO Mainnet)

## Purpose

LSP26 provides an **on-chain follower registry** — a single smart contract where any address can follow/unfollow other addresses, and where anyone can read follower/following lists. When you follow/unfollow an LSP1-supporting address, it receives a `universalReceiver` notification.

Think of it as: *a decentralized, portable social graph stored on-chain.*

## Key Interface

```solidity
interface ILSP26 {
    event Follow(address follower, address addr);
    event Unfollow(address unfollower, address addr);

    function follow(address addr) external;
    function followBatch(address[] memory addresses) external;
    function unfollow(address addr) external;
    function unfollowBatch(address[] memory addresses) external;

    function isFollowing(address follower, address addr) external view returns (bool);
    function followerCount(address addr) external view returns (uint256);
    function followingCount(address addr) external view returns (uint256);

    // Paginated reading
    function getFollowsByIndex(address addr, uint256 startIndex, uint256 endIndex) 
        external view returns (address[] memory);
    function getFollowersByIndex(address addr, uint256 startIndex, uint256 endIndex) 
        external view returns (address[] memory);
}
```

## LSP1 Notification Type IDs

```
// Sent to the followed address when someone follows them
keccak256('LSP26FollowerSystem_FollowNotification')
= 0x71e02f9f05bcd5816ec4f3134aa2e5a916669537ec6c77fe66ea595fabc2d51a

// Sent to the followed address when someone unfollows them
keccak256('LSP26FollowerSystem_UnfollowNotification')  
= 0x9d3c0b4012b69658977b099bdaa51eff0f0460f421fba96d15669506c00d1c4f
```

## Code Examples

### Follow/unfollow an address
```javascript
const lsp26 = new ethers.Contract(
  '0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA',
  LSP26ABI,
  signer
);

// Follow
await lsp26.follow(targetAddress);

// Follow multiple
await lsp26.followBatch([addr1, addr2, addr3]);

// Unfollow
await lsp26.unfollow(targetAddress);

// Check if following
const isFollowing = await lsp26.isFollowing(myAddress, targetAddress);

// Get follower count
const count = await lsp26.followerCount(targetAddress);

// Get paginated followers (first 50)
const followers = await lsp26.getFollowersByIndex(targetAddress, 0, 50);

// Get paginated following (first 50)
const following = await lsp26.getFollowsByIndex(myAddress, 0, 50);
```

### Using Envio indexer (faster than on-chain reads)

```bash
# Query followers via GraphQL (Envio indexer)
curl -X POST https://envio.lukso-mainnet.universal.tech/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Profile(where: {name: {_eq: \"myusername\"}}) { id name } }"}'
```

## Gotchas

1. **Single registry for all chains**: Deploy the LSP26 contract at the same address on other chains using Nick Factory (see deployment section in LIP-26).

2. **Pagination required for large accounts**: For accounts with thousands of followers, use the `startIndex/endIndex` params. Fetching all at once may hit gas limits for on-chain queries or be slow.

3. **You can follow yourself** (not prevented by contract): Guard against this in your UI.

4. **LSP1 notifications are optional**: The `universalReceiver` call on the followed address is wrapped in a try-catch. If it fails, the follow still succeeds.

5. **No permission required**: Anyone can follow any address. This is a public registry.

---

## Standard Interaction Patterns

### 1. Reading a UP's full state

```javascript
import { ERC725 } from '@erc725/erc725.js';
import LSP3Schema from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';
import LSP4Schema from '@erc725/erc725.js/schemas/LSP4DigitalAsset.json';
import LSP5Schema from '@erc725/erc725.js/schemas/LSP5ReceivedAssets.json';
import LSP6Schema from '@erc725/erc725.js/schemas/LSP6KeyManager.json';
import LSP10Schema from '@erc725/erc725.js/schemas/LSP10ReceivedVaults.json';
import LSP12Schema from '@erc725/erc725.js/schemas/LSP12IssuedAssets.json';

const allSchemas = [...LSP3Schema, ...LSP5Schema, ...LSP10Schema, ...LSP12Schema];
const erc725 = new ERC725(allSchemas, upAddress, 'https://42.rpc.thirdweb.com');

const [profile, receivedAssets, issuedAssets, receivedVaults] = await Promise.all([
  erc725.fetchData('LSP3Profile'),
  erc725.fetchData('LSP5ReceivedAssets[]'),
  erc725.fetchData('LSP12IssuedAssets[]'),
  erc725.fetchData('LSP10ReceivedVaults[]'),
]);
```

### 2. Deploying a Universal Profile (simplified)

```javascript
import { LSPFactory } from '@lukso/lsp-factory.js';

const lspFactory = new LSPFactory('https://42.rpc.thirdweb.com', {
  deployKey: '0xYOUR_PRIVATE_KEY',
  chainId: 42
});

const contracts = await lspFactory.UniversalProfile.deploy({
  controllerAddresses: ['0xYOUR_EOA_ADDRESS'],
  lsp3Profile: {
    name: 'My Profile',
    description: 'My Universal Profile',
    tags: ['LUKSO'],
    links: [],
    profileImage: [{ width: 400, height: 400, url: 'ipfs://...' }],
    backgroundImage: [],
  }
});

console.log('UP deployed at:', contracts.LSP0ERC725Account.address);
console.log('KM deployed at:', contracts.LSP6KeyManager.address);
```

### 3. Execute a batch of operations

```javascript
// Execute multiple operations in one transaction via batchCalls
const calls = [
  up.interface.encodeFunctionData('execute', [0, addr1, 0, data1]),
  up.interface.encodeFunctionData('execute', [0, addr2, 0, data2]),
  up.interface.encodeFunctionData('setData', [key, value]),
];
await up.batchCalls(calls);  // or through KM
```

### 4. Check if a contract implements a standard

```javascript
const { INTERFACE_IDS } = require('@lukso/lsp-smart-contracts');

async function isLSP7(address, provider) {
  const contract = new ethers.Contract(address, ['function supportsInterface(bytes4) view returns (bool)'], provider);
  return await contract.supportsInterface(INTERFACE_IDS.LSP7DigitalAsset);
}

// Check multiple standards
const checks = await Promise.all([
  contract.supportsInterface(INTERFACE_IDS.LSP0ERC725Account),
  contract.supportsInterface(INTERFACE_IDS.LSP7DigitalAsset),
  contract.supportsInterface(INTERFACE_IDS.LSP8IdentifiableDigitalAsset),
  contract.supportsInterface(INTERFACE_IDS.LSP9Vault),
]);
```

---

## NPM Package Reference

```bash
# Main package with all LSP tools
npm install @lukso/lsp-smart-contracts

# Individual packages
npm install @lukso/lsp0-contracts    # ERC725Account
npm install @lukso/lsp1-contracts    # Universal Receiver  
npm install @lukso/lsp1delegate-contracts  # URD
npm install @lukso/lsp2-contracts    # ERC725Y JSON Schema
npm install @lukso/lsp3-contracts    # Profile Metadata
npm install @lukso/lsp4-contracts    # Digital Asset Metadata
npm install @lukso/lsp5-contracts    # Received Assets
npm install @lukso/lsp6-contracts    # Key Manager
npm install @lukso/lsp7-contracts    # Fungible Token
npm install @lukso/lsp8-contracts    # NFT
npm install @lukso/lsp9-contracts    # Vault
npm install @lukso/lsp14-contracts   # Ownable2Step
npm install @lukso/lsp17contractextension-contracts  # Extensions
npm install @lukso/lsp20-contracts   # Call Verification
npm install @lukso/lsp23-contracts   # Linked Contracts Factory
npm install @lukso/lsp25-contracts   # Execute Relay Call
npm install @lukso/lsp26-contracts   # Follower System

# High-level tools
npm install @erc725/erc725.js        # ERC725Y read/write/encode/decode
npm install @lukso/lsp-factory.js    # Deploy UPs easily
```

---

## Common Error Reference

| Error | Cause | Fix |
|-------|-------|-----|
| `NotAuthorised` | Controller lacks permission | Check `AddressPermissions:Permissions:<address>` |
| `NoCallsAllowed` | Controller has CALL but empty AllowedCalls | Set AllowedCalls or use SUPER_CALL |
| `NotAllowedERC725YDataKey` | Controller has SETDATA but restricted keys | Add key to AllowedERC725YDataKeys |
| `CallerNotOwner` | Called owner-only function without going through KM | Call via KeyManager.execute() |
| `LSP7AmountExceedsAuthorizedAmount` | Operator transfer > authorized amount | Increase authorization or reduce amount |
| `LSP7CannotUseAddressZeroAsOperator` | Tried to authorize address(0) as operator | Use a real address |
| `LSP7NotTokenOwner` | Transfer from address that doesn't own tokens | Check balanceOf |
| `LSP8TokenIdNotMinted` | tokenId doesn't exist | Mint it first |
| `InvalidSignature` | LSP25 relay call bad signature | Verify hash construction (packed encoding, not ABI-encoded) |
| `InvalidNonce` | Nonce already used or wrong channel | Call getNonce() again |
| `ExecutionFailed` | The forwarded call reverted | Debug the underlying payload |

---

## Resources

- **LUKSO Docs:** https://docs.lukso.tech
- **LIPs Repository:** https://github.com/lukso-network/LIPs
- **LSP Smart Contracts:** https://github.com/lukso-network/lsp-smart-contracts
- **ERC725.js:** https://github.com/ERC725Alliance/erc725.js
- **LSP Factory:** https://github.com/lukso-network/tools-lsp-factory
- **Block Explorer:** https://explorer.lukso.network
- **Envio Indexer:** https://envio.lukso-mainnet.universal.tech/v1/graphql
- **Universal Profile App:** https://universalprofile.cloud
- **Discord:** https://discord.gg/lukso
