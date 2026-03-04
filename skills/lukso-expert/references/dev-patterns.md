# LUKSO Developer Patterns — Practical Reference

> Last updated: 2026-02-18  
> Sources: docs.lukso.tech, LIPs GitHub, erc725.js docs  
> Code-heavy, copy-paste ready reference for LUKSO development

---

## Table of Contents

1. [Network Info & RPC Endpoints](#1-network-info--rpc-endpoints)
2. [Universal Profile Creation (LSP0 + LSP6)](#2-universal-profile-creation-lsp0--lsp6)
3. [Key Manager Permissions (LSP6)](#3-key-manager-permissions-lsp6)
4. [Token Operations — LSP7 (Fungible)](#4-token-operations--lsp7-fungible)
5. [Token Operations — LSP8 (NFT)](#5-token-operations--lsp8-nft)
6. [Gasless Transactions (LSP25)](#6-gasless-transactions-lsp25)
7. [Profile Metadata (LSP3)](#7-profile-metadata-lsp3)
8. [Universal Receiver (LSP1)](#8-universal-receiver-lsp1)
9. [The Grid (LSP28)](#9-the-grid-lsp28)
10. [Followers (LSP26)](#10-followers-lsp26)
11. [Dev Tools](#11-dev-tools)
12. [Common Pitfalls](#12-common-pitfalls)
13. [Key Contract Addresses](#13-key-contract-addresses)

---

## 1. Network Info & RPC Endpoints

```
LUKSO Mainnet:
  Chain ID: 42
  RPC: https://rpc.mainnet.lukso.network  (or via Thirdweb: https://42.rpc.thirdweb.com)
  Explorer: https://explorer.lukso.network
  Relayer: https://relayer.mainnet.lukso.network

LUKSO Testnet:
  Chain ID: 4201
  RPC: https://rpc.testnet.lukso.network
  Explorer: https://explorer.testnet.lukso.network
  Faucet: https://faucet.testnet.lukso.network
  Relayer: https://relayer.testnet.lukso.network
```

### Hardhat config

```ts
// hardhat.config.ts
import { HardhatUserConfig } from 'hardhat/config';
import '@nomicfoundation/hardhat-toolbox';
import * as dotenv from 'dotenv';
dotenv.config();

const config: HardhatUserConfig = {
  solidity: {
    version: '0.8.17',
    settings: { optimizer: { enabled: true, runs: 1000 } },
  },
  networks: {
    luksoTestnet: {
      url: 'https://rpc.testnet.lukso.network',
      chainId: 4201,
      accounts: [process.env.PRIVATE_KEY!],
    },
    luksoMainnet: {
      url: 'https://rpc.mainnet.lukso.network',
      chainId: 42,
      accounts: [process.env.PRIVATE_KEY!],
    },
  },
  etherscan: {
    apiKey: { luksoTestnet: 'no-api-key-needed' },
    customChains: [
      {
        network: 'luksoTestnet',
        chainId: 4201,
        urls: {
          apiURL: 'https://api.explorer.testnet.lukso.network/api',
          browserURL: 'https://explorer.testnet.lukso.network',
        },
      },
    ],
  },
};
export default config;
```

---

## 2. Universal Profile Creation (LSP0 + LSP6)

A Universal Profile (UP) is an **LSP0ERC725Account** controlled by an **LSP6KeyManager**.  
The standard way to deploy is via the **LSP23 Linked Contracts Factory** — deploys both via proxy (EIP-1167) in one transaction.

### Contract Addresses (Mainnet = Testnet same)

```
LSP23 Factory:              0x2300000A84D25dF63081feAa37ba6b62C4c89a30
LSP23 PostDeployment:       0x000000000066093407b6704B89793beFfD0D8F00
UP Implementation:          0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F
LSP6 KM Implementation:     0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4
Default URD (Mainnet):      0x7870C5B8BC9572A8001C3f96f7ff59961B23500D
```

### Full Deploy Script (ethers.js v6)

```ts
import { AbiCoder, Contract, ethers } from 'ethers';
import { ERC725 } from '@erc725/erc725.js';
import LSP23FactoryArtifact from '@lukso/lsp-smart-contracts/artifacts/LSP23LinkedContractsFactory.json';
import UniversalProfileInitArtifact from '@lukso/lsp-smart-contracts/artifacts/UniversalProfileInit.json';
import LSP1URDSchemas from '@erc725/erc725.js/schemas/LSP1UniversalReceiverDelegate.json';
import LSP3Schemas from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';
import LSP6Schemas from '@erc725/erc725.js/schemas/LSP6KeyManager.json';

const LSP23_FACTORY         = '0x2300000A84D25dF63081feAa37ba6b62C4c89a30';
const LSP23_POST_DEPLOY     = '0x000000000066093407b6704B89793beFfD0D8F00';
const UP_IMPL               = '0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F';
const KM_IMPL               = '0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4';
const DEFAULT_URD            = '0x7870C5B8BC9572A8001C3f96f7ff59961B23500D';
const MAIN_CONTROLLER       = '0xYOUR_EOA_ADDRESS';

// Random unique salt — MUST be different per deploy
const SALT = ethers.hexlify(ethers.randomBytes(32));

async function deployUP() {
  const provider = new ethers.JsonRpcProvider('https://rpc.testnet.lukso.network');
  const signer = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

  const lsp23Factory = new Contract(LSP23_FACTORY, LSP23FactoryArtifact.abi, signer);
  const upImpl = new Contract(UP_IMPL, UniversalProfileInitArtifact.abi, signer);

  // 1. Encode permissions using erc725.js
  const erc725 = new ERC725([...LSP6Schemas, ...LSP3Schemas, ...LSP1URDSchemas]);

  const lsp3DataValue = {
    verification: { method: 'keccak256(utf8)', data: '0x...' }, // hash of your JSON
    url: 'ipfs://Qm...',
  };

  const encoded = erc725.encodeData([
    { keyName: 'LSP3Profile', value: lsp3DataValue },
    { keyName: 'LSP1UniversalReceiverDelegate', value: DEFAULT_URD },
    {
      keyName: 'AddressPermissions:Permissions:<address>',
      dynamicKeyParts: [DEFAULT_URD],
      value: erc725.encodePermissions({ REENTRANCY: true, SUPER_SETDATA: true }),
    },
    {
      keyName: 'AddressPermissions:Permissions:<address>',
      dynamicKeyParts: [MAIN_CONTROLLER],
      value: erc725.encodePermissions({
        CHANGEOWNER: true, ADDCONTROLLER: true, EDITPERMISSIONS: true,
        ADDEXTENSIONS: true, CHANGEEXTENSIONS: true,
        ADDUNIVERSALRECEIVERDELEGATE: true, CHANGEUNIVERSALRECEIVERDELEGATE: true,
        SUPER_TRANSFERVALUE: true, TRANSFERVALUE: true,
        SUPER_CALL: true, CALL: true,
        SUPER_STATICCALL: true, STATICCALL: true,
        DEPLOY: true, SUPER_SETDATA: true, SETDATA: true,
        ENCRYPT: true, DECRYPT: true, SIGN: true, EXECUTE_RELAY_CALL: true,
      }),
    },
    { keyName: 'AddressPermissions[]', value: [DEFAULT_URD, MAIN_CONTROLLER] },
  ]);

  // 2. ABI encode initialization bytes
  const abiCoder = new AbiCoder();
  const initCalldata = abiCoder.encode(
    ['bytes32[]', 'bytes[]'],
    [encoded.keys, encoded.values]
  );

  // 3. Build structs
  const upInitStruct = {
    salt: SALT,
    fundingAmount: 0,
    implementationContract: UP_IMPL,
    initializationCalldata: upImpl.interface.encodeFunctionData('initialize', [LSP23_POST_DEPLOY]),
  };

  const kmInitStruct = {
    fundingAmount: 0,
    implementationContract: KM_IMPL,
    addPrimaryContractAddress: true,   // appends UP address to init calldata
    initializationCalldata: '0xc4d66de8', // initialize() selector
    extraInitializationParams: '0x',
  };

  // 4. Deploy
  const tx = await lsp23Factory.deployERC1167Proxies(
    upInitStruct,
    kmInitStruct,
    LSP23_POST_DEPLOY,
    initCalldata
  );
  const receipt = await tx.wait();

  // Parse addresses from events
  const event = receipt.logs.find((log: any) =>
    log.topics[0] === ethers.id('DeployedERC1167Proxies(address,address,bytes32)')
  );
  console.log('UP deployed at:', /* parse from event */);
}
```

### Quick Deploy (EOA without factory, for testing)

```ts
import { ethers } from 'ethers';
import UniversalProfile from '@lukso/lsp-smart-contracts/artifacts/UniversalProfile.json';
import LSP6KeyManager from '@lukso/lsp-smart-contracts/artifacts/LSP6KeyManager.json';

async function quickDeploy() {
  const provider = new ethers.JsonRpcProvider('https://rpc.testnet.lukso.network');
  const deployer = new ethers.Wallet(process.env.PRIVATE_KEY!, provider);

  // Deploy UP (owner = deployer initially)
  const UPFactory = new ethers.ContractFactory(UniversalProfile.abi, UniversalProfile.bytecode, deployer);
  const up = await UPFactory.deploy(deployer.address);
  await up.waitForDeployment();
  const upAddress = await up.getAddress();

  // Deploy Key Manager pointing to UP
  const KMFactory = new ethers.ContractFactory(LSP6KeyManager.abi, LSP6KeyManager.bytecode, deployer);
  const km = await KMFactory.deploy(upAddress);
  await km.waitForDeployment();
  const kmAddress = await km.getAddress();

  // Transfer UP ownership to Key Manager
  // First: initiate transfer
  await up.transferOwnership(kmAddress);
  // Then: accept from within KM context (claimOwnership)
  const payload = up.interface.encodeFunctionData('claimOwnership', []);
  await km.execute(payload);

  console.log('UP:', upAddress);
  console.log('KM:', kmAddress);
}
```

---

## 3. Key Manager Permissions (LSP6)

Permissions are stored in the **UP's ERC725Y storage**, not in the KM itself (making KM upgradeable without permission reset).

### Permission Bit Values

| Permission | Hex Value | Description |
|---|---|---|
| `CHANGEOWNER` | `0x...01` | Change UP ownership |
| `ADDCONTROLLER` | `0x...02` | Grant permissions to new addresses |
| `EDITPERMISSIONS` | `0x...04` | Modify existing permissions |
| `ADDEXTENSIONS` | `0x...08` | Add LSP17 extension contracts |
| `CHANGEEXTENSIONS` | `0x...10` | Edit extension addresses |
| `ADDUNIVERSALRECEIVERDELEGATE` | `0x...20` | Add new URD contracts |
| `CHANGEUNIVERSALRECEIVERDELEGATE` | `0x...40` | Edit URD addresses |
| `REENTRANCY` | `0x...80` | Allow reentrant calls |
| `SUPER_TRANSFERVALUE` | `0x...100` | Transfer LYX to ANY address |
| `TRANSFERVALUE` | `0x...200` | Transfer LYX (with AllowedCalls restriction) |
| `SUPER_CALL` | `0x...400` | Call ANY contract |
| `CALL` | `0x...800` | Call contracts (with AllowedCalls restriction) |
| `SUPER_STATICCALL` | `0x...1000` | Static call ANY |
| `STATICCALL` | `0x...2000` | Static call (restricted) |
| `DELEGATECALL` | `0x...8000` | ⚠️ DISALLOWED even if set |
| `DEPLOY` | `0x...10000` | Deploy contracts via UP |
| `SUPER_SETDATA` | `0x...20000` | Set ANY data key |
| `SETDATA` | `0x...40000` | Set data (with AllowedERC725YDataKeys restriction) |
| `ENCRYPT` | `0x...80000` | Encrypt messages |
| `DECRYPT` | `0x...100000` | Decrypt messages |
| `SIGN` | `0x...200000` | Sign messages (Web2 login) |
| `EXECUTE_RELAY_CALL` | `0x...400000` | Sign relay calls via LSP25 |

### Grant Permissions (erc725.js)

```ts
import { ERC725 } from '@erc725/erc725.js';
import LSP6Schemas from '@erc725/erc725.js/schemas/LSP6KeyManager.json';

const erc725 = new ERC725(LSP6Schemas, upAddress, provider);

// Encode permissions for a new controller
const permissionsEncoded = erc725.encodePermissions({
  CALL: true,
  SETDATA: true,
  SIGN: true,
  EXECUTE_RELAY_CALL: true,
});

// Encode the full setData payload
const encoded = erc725.encodeData([
  {
    keyName: 'AddressPermissions:Permissions:<address>',
    dynamicKeyParts: [newControllerAddress],
    value: permissionsEncoded,
  },
  {
    keyName: 'AddressPermissions[]',
    value: [existingController, newControllerAddress], // must include ALL controllers
  },
]);

// Execute via KM
const up = new ethers.Contract(upAddress, UP_ABI, signer);
await up.setDataBatch(encoded.keys, encoded.values);
```

### Revoke Permissions

```ts
// To remove: set permissions to 0x0000...0000
const encoded = erc725.encodeData([
  {
    keyName: 'AddressPermissions:Permissions:<address>',
    dynamicKeyParts: [controllerToRemove],
    value: erc725.encodePermissions({}), // all false = zero bytes
  },
  // Update AddressPermissions[] array to remove the controller
  {
    keyName: 'AddressPermissions[]',
    value: [remainingController1, remainingController2],
  },
]);
```

### Read Permissions

```ts
const erc725 = new ERC725(LSP6Schemas, upAddress, rpcUrl);

// Read raw
const permsData = await erc725.getData({
  keyName: 'AddressPermissions:Permissions:<address>',
  dynamicKeyParts: [controllerAddress],
});

// Decode to object
const decoded = erc725.decodePermissions(permsData.value as string);
console.log(decoded); // { CALL: true, SETDATA: false, ... }

// Read all controllers
const controllersArray = await erc725.getData('AddressPermissions[]');
```

### Common Permission Sets

```ts
// Minimal read-only bot (sign login only)
const readOnlyBot = { SIGN: true };

// dApp interaction (call contracts + set some data + gasless)
const dAppController = {
  CALL: true,
  SETDATA: true,
  EXECUTE_RELAY_CALL: true,
  SIGN: true,
};

// Token manager (send tokens + gasless)
const tokenManager = {
  SUPER_CALL: true,
  EXECUTE_RELAY_CALL: true,
};

// Universal Receiver Delegate (default for URD)
const urdPermissions = {
  REENTRANCY: true,
  SUPER_SETDATA: true,
};

// Full admin (main controller EOA)
const fullAdmin = {
  CHANGEOWNER: true, ADDCONTROLLER: true, EDITPERMISSIONS: true,
  ADDEXTENSIONS: true, CHANGEEXTENSIONS: true,
  ADDUNIVERSALRECEIVERDELEGATE: true, CHANGEUNIVERSALRECEIVERDELEGATE: true,
  SUPER_TRANSFERVALUE: true, TRANSFERVALUE: true,
  SUPER_CALL: true, CALL: true, SUPER_STATICCALL: true, STATICCALL: true,
  DEPLOY: true, SUPER_SETDATA: true, SETDATA: true,
  ENCRYPT: true, DECRYPT: true, SIGN: true, EXECUTE_RELAY_CALL: true,
};
```

### AllowedCalls (Restricting CALL/TRANSFERVALUE)

```ts
// Restrict a controller to only call a specific contract
const encoded = erc725.encodeData([
  {
    keyName: 'AddressPermissions:AllowedCalls:<address>',
    dynamicKeyParts: [controllerAddress],
    value: [
      {
        action: '0x000000003',   // CALL operation type
        address: '0xTARGET_CONTRACT',
        standard: '0xffffffff',  // any interface
        function: '0xffffffff',  // any function
      },
    ],
  },
]);
```

---

## 4. Token Operations — LSP7 (Fungible)

LSP7 = LUKSO's ERC20 equivalent. Key differences: `force` param, `universalReceiver` hooks, richer metadata.

### Deploy a Custom LSP7 Token (Hardhat/Solidity)

```solidity
// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.9;

import "@lukso/lsp-smart-contracts/contracts/LSP7DigitalAsset/presets/LSP7Mintable.sol";
import "@lukso/lsp-smart-contracts/contracts/LSP7DigitalAsset/extensions/LSP7Burnable.sol";

contract MyToken is LSP7Mintable, LSP7Burnable {
    constructor(
        string memory name,
        string memory symbol,
        address owner,
        uint256 tokenType,   // 0 = TOKEN, 1 = NFT, 2 = COLLECTION
        bool isNonDivisible  // true = whole units only (like NFTs)
    )
    LSP7Mintable(name, symbol, owner, tokenType, isNonDivisible)
    {
        // Pre-mint to deployer
        _mint(
            msg.sender,
            20_000 * 10 ** decimals(),
            true,   // force: true (EOA minting = needs force)
            ""
        );
    }
}
```

### Deploy Script (ethers.js)

```ts
import { ethers } from 'hardhat';

async function deploy() {
  const [deployer] = await ethers.getSigners();

  const Token = await ethers.getContractFactory('MyToken');
  const token = await Token.deploy(
    'My Token',     // name
    'MYT',          // symbol
    deployer.address, // owner
    0,              // token type (TOKEN)
    false,          // divisible (has decimals)
  );
  await token.waitForDeployment();
  console.log('Token:', await token.getAddress());
}
```

### Mint

```ts
const token = new ethers.Contract(tokenAddress, LSP7_ABI, signer);

await token.mint(
  recipientAddress,           // to
  ethers.parseEther('100'),   // amount (in wei if 18 decimals)
  false,                      // force: false = recipient must implement LSP1
  '0x'                        // data
);
```

### Transfer

```ts
await token.transfer(
  senderAddress,      // from (must be caller or operator)
  recipientAddress,   // to
  ethers.parseEther('10'), // amount
  false,              // force: false = safe (LSP1 required on recipient)
  '0x'                // data (passed to universalReceiver hooks)
);
```

### The `force` Parameter — Critical Concept

```
force = false (SAFE, recommended for production):
  - Recipient must be a smart contract implementing LSP1 universalReceiver()
  - Prevents accidental sends to EOAs or dumb contracts
  - Follows LUKSO's "smart contract first" design philosophy
  - Will REVERT if recipient is an EOA or non-LSP1 contract

force = true (UNSAFE, use for testing/compatibility):
  - Transfer goes through regardless
  - EOAs and any contracts can receive
  - Use when: interacting with non-LUKSO contracts, bridging, testing
  - Use when: recipient is an EOA controller (not a UP)
```

### Operator Pattern (approve equivalent)

```ts
// Approve an operator to spend tokens
await token.authorizeOperator(
  operatorAddress,
  ethers.parseEther('500'),  // amount they can spend
  '0x'                       // optional data
);

// Check allowance
const allowance = await token.allowance(ownerAddress, operatorAddress);

// Revoke
await token.revokeOperator(operatorAddress, false, '0x');
```

### Token Type Constants (LSP4)

```ts
import {
  LSP4_TOKEN_TYPES,
} from '@lukso/lsp-smart-contracts';

// 0 = TOKEN (fungible)
// 1 = NFT (non-fungible, used in LSP7 for non-divisible)
// 2 = COLLECTION (LSP8 collections)
```

---

## 5. Token Operations — LSP8 (NFT)

LSP8 = LUKSO's ERC721/1155 equivalent. TokenIds are `bytes32` with configurable format types.

### TokenId Format Types

| Value | Format | Use Case |
|---|---|---|
| `0` | `uint256` / Number | Standard sequential NFTs |
| `1` | `string` | Named NFTs (≤32 chars) |
| `2` | `address` | NFTs as smart contracts (richest) |
| `3` | `bytes32` | Arbitrary byte identifiers |
| `4` | `bytes32` hash | Hash digests of longer strings |

### Deploy LSP8 Collection (Solidity)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.4;

import {LSP8Mintable} from "@lukso/lsp-smart-contracts/contracts/LSP8IdentifiableDigitalAsset/presets/LSP8Mintable.sol";
import {_LSP8_TOKENID_FORMAT_NUMBER} from "@lukso/lsp-smart-contracts/contracts/LSP8IdentifiableDigitalAsset/LSP8Constants.sol";
import {_LSP4_TOKEN_TYPE_COLLECTION} from "@lukso/lsp-smart-contracts/contracts/LSP4DigitalAssetMetadata/LSP4Constants.sol";

contract MyNFTCollection is LSP8Mintable {
    uint256 private _tokenCounter = 0;

    constructor(address owner)
    LSP8Mintable(
        "My NFT Collection",    // name
        "MNFT",                 // symbol
        owner,                  // owner
        _LSP4_TOKEN_TYPE_COLLECTION,    // token type
        _LSP8_TOKENID_FORMAT_NUMBER     // tokenId format = number
    ) {}

    function mint(address to) external onlyOwner {
        _tokenCounter++;
        bytes32 tokenId = bytes32(_tokenCounter); // number → bytes32
        _mint(
            to,
            tokenId,
            false,  // force: false = recipient must implement LSP1
            ""
        );
    }
}
```

### Mint & Transfer (JS)

```ts
const nft = new ethers.Contract(nftAddress, LSP8_ABI, signer);

// Mint (only owner)
const tokenId = ethers.zeroPadValue(ethers.toBeHex(1), 32); // tokenId = 1 as bytes32
await nft.mint(
  recipientAddress,
  tokenId,
  false,   // force
  '0x'     // data
);

// Transfer
await nft.transfer(
  fromAddress,
  toAddress,
  tokenId,
  false,   // force
  '0x'     // data
);

// Check owner
const owner = await nft.tokenOwnerOf(tokenId);

// List all tokenIds of an address
const tokenIds = await nft.tokenIdsOf(holderAddress);
```

### Per-TokenId Metadata

```ts
// Set metadata for a specific tokenId (on-chain)
const dataKey = ethers.keccak256(ethers.toUtf8Bytes('LSP4Metadata'));
await nft.setDataForTokenId(
  tokenId,
  dataKey,
  encodedVerifiableURI  // VerifiableURI pointing to JSON
);

// Read tokenId metadata
const data = await nft.getDataForTokenId(tokenId, dataKey);
```

### LSP8 Operator (approve equivalent)

```ts
// Authorize operator for a specific tokenId
await nft.authorizeOperator(
  operatorAddress,
  tokenId,
  '0x'
);

// Authorize operator for ALL tokens (like setApprovalForAll)
// LSP8 doesn't have native setApprovalForAll — use per-tokenId operators
// OR override in custom contract

// Check if operator authorized
const isOperator = await nft.isOperatorFor(operatorAddress, tokenId);
```

---

## 6. Gasless Transactions (LSP25)

LSP25 allows signing transactions off-chain; a relayer submits them and pays gas.  
LUKSO provides a free relay service with **20 million gas/month per registered UP**.

### How It Works

```
1. Controller encodes the payload (what UP should do)
2. Controller gets nonce from Key Manager (channel-based)
3. Controller signs LSP25 message (EIP-191 v0 — NOT standard signMessage!)
4. Controller sends to LUKSO relay API
5. Relayer calls executeRelayCall() on the Key Manager → pays gas
```

### Full Example (ethers.js v6)

```ts
import { ethers } from 'ethers';

const RPC = 'https://rpc.mainnet.lukso.network';
const CHAIN_ID = 42;           // mainnet (testnet: 4201)
const RELAYER = 'https://relayer.mainnet.lukso.network';

async function executeGasless(
  controllerPrivKey: string,
  upAddress: string,
  payload: string            // ABI-encoded function call for UP to execute
) {
  const provider = new ethers.JsonRpcProvider(RPC);
  const controller = new ethers.Wallet(controllerPrivKey, provider);
  const controllerAddress = controller.address;

  // 1. Get Key Manager address
  const up = new ethers.Contract(upAddress,
    ['function owner() view returns (address)'], provider);
  const kmAddress = await up.owner();

  // 2. Get nonce (channel 0 = sequential; use other channels for parallel)
  const km = new ethers.Contract(kmAddress,
    ['function getNonce(address,uint128) view returns (uint256)'], provider);
  const nonce = await km.getNonce(controllerAddress, 0);

  // 3. Build LSP25 encoded message
  const validityTimestamps = 0;  // 0 = no time restriction
  const msgValue = 0;            // no LYX being sent
  const encodedMessage = ethers.solidityPacked(
    ['uint256', 'uint256', 'uint256', 'uint256', 'uint256', 'bytes'],
    [
      25,                   // LSP25_VERSION
      CHAIN_ID,
      nonce,
      validityTimestamps,
      msgValue,
      payload,
    ]
  );

  // 4. Hash with EIP-191 v0 (NOT ethers signMessage!)
  const hash = ethers.keccak256(
    ethers.concat(['0x19', '0x00', kmAddress, encodedMessage])
  );

  // 5. Sign raw hash (EIP-191 v0)
  const signingKey = new ethers.SigningKey(controllerPrivKey);
  const sig = signingKey.sign(hash);
  const signature = ethers.Signature.from(sig).serialized;

  // 6. Submit to relay service
  const response = await fetch(`${RELAYER}/api/execute`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      address: upAddress,
      transaction: {
        abi: payload,
        signature,
        nonce: Number(nonce),
        validityTimestamps: '0x0',
      },
    }),
  });

  const result = await response.json();
  if (!result.transactionHash) throw new Error(JSON.stringify(result));
  return result.transactionHash;
}

// Example usage: gasless setData
const UP_ABI = ['function setData(bytes32,bytes)'];
const iface = new ethers.Interface(UP_ABI);
const payload = iface.encodeFunctionData('setData', [
  '0x5ef83ad9...', // data key
  '0x...',         // data value
]);

const txHash = await executeGasless(PRIVATE_KEY, UP_ADDRESS, payload);
```

### Validity Timestamps (Time-Limited Signatures)

```ts
// Format: packed uint128 (startTimestamp) + uint128 (endTimestamp)
// 0x0 = no restriction (both 0)

const now = Math.floor(Date.now() / 1000);
const oneHour = 3600;

// Valid for next 1 hour only
const validityTimestamps = ethers.solidityPacked(
  ['uint128', 'uint128'],
  [now, now + oneHour]
);

// Valid only after tomorrow
const tomorrow = now + 86400;
const validityTimestamps2 = ethers.solidityPacked(
  ['uint128', 'uint128'],
  [tomorrow, 0]  // 0 end = no expiry
);
```

### Nonce Channels (Parallel Execution)

```ts
// Channel 0: sequential (nonce must be exact)
// Channels 1-127: independent sequences (can submit in any order)

// Get nonce for channel 5
const nonce = await km.getNonce(controllerAddress, 5);

// Use same channel in signature
// This allows submitting multiple independent txs without waiting for confirmations
```

### Check Quota

```ts
async function checkQuota(upAddress: string, wallet: ethers.Wallet) {
  const timestamp = Math.floor(Date.now() / 1000);
  const message = `${upAddress}:${timestamp}`;
  const signature = await wallet.signMessage(message);

  const res = await fetch(`${RELAYER}/api/quota`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: upAddress, timestamp, signature }),
  });
  return res.json();
  // Returns: { quota: 20000000, used: 1234567, unit: 'gas', resetDate: '...' }
}
```

### Required Permission

Controller signing relay calls must have `EXECUTE_RELAY_CALL` permission:
```
0x0000000000000000000000000000000000000000000000000000000000400000
```

---

## 7. Profile Metadata (LSP3)

LSP3 defines the JSON schema for Universal Profile metadata, stored as a `VerifiableURI` in ERC725Y.

### LSP3 JSON Schema

```json
{
  "LSP3Profile": {
    "name": "My Name",
    "description": "Short bio or description",
    "links": [
      { "title": "Website", "url": "https://example.com" },
      { "title": "Twitter", "url": "https://twitter.com/handle" }
    ],
    "tags": ["blockchain", "developer"],
    "profileImage": [
      {
        "width": 640,
        "height": 640,
        "url": "ipfs://QmYour...",
        "verification": {
          "method": "keccak256(bytes)",
          "data": "0xhash_of_image_file"
        }
      }
    ],
    "backgroundImage": [
      {
        "width": 1024,
        "height": 576,
        "url": "ipfs://QmYour...",
        "verification": {
          "method": "keccak256(bytes)",
          "data": "0xhash_of_image_file"
        }
      }
    ]
  }
}
```

**Notes:**
- `profileImage` max width: 800px (for universalprofile.cloud)
- `backgroundImage` max width: 1800px
- Image sizes must be numbers, not strings
- Multiple image sizes recommended (let clients pick appropriate one)

### Upload to IPFS (Pinata)

```ts
import { IPFSHttpClientUploader } from '@lukso/data-provider-ipfs-http-client';
import { createReadStream } from 'fs';

const provider = new IPFSHttpClientUploader('https://api.pinata.cloud/pinning/pinFileToIPFS', {
  headers: { Authorization: `Bearer ${process.env.PINATA_JWT}` }
});
// Or use local IPFS node: 'http://127.0.0.1:5001/api/v0/add'

// Upload image
const imageStream = createReadStream('./avatar.png');
const { url: imageUrl, hash: imageHash } = await provider.upload(imageStream);
// url = 'ipfs://Qm...'
// hash = '0x...' (keccak256 of file bytes)

// Upload JSON
import lsp3Json from './lsp3-metadata.json';
const { url: jsonUrl, hash: jsonHash } = await provider.upload(lsp3Json);
```

### Encode & Set Profile Data

```ts
import { ERC725 } from '@erc725/erc725.js';
import LSP3Schemas from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';

const erc725 = new ERC725(LSP3Schemas);

// Method 1: pass JSON + url, let erc725.js compute hash
const encoded = ERC725.encodeData(
  [{
    keyName: 'LSP3Profile',
    value: {
      json: lsp3JsonObject,  // the actual JSON object
      url: jsonIpfsUrl,      // 'ipfs://Qm...'
    },
  }],
  LSP3Schemas
);

// Method 2: pass hash + url manually
const encoded2 = ERC725.encodeData(
  [{
    keyName: 'LSP3Profile',
    value: {
      verification: {
        method: 'keccak256(utf8)',
        data: jsonHash,  // '0x...'
      },
      url: jsonIpfsUrl,
    },
  }],
  LSP3Schemas
);

// Set on UP
const up = new ethers.Contract(upAddress, UP_ABI, signer);
await up.setData(encoded.keys[0], encoded.values[0]);
// Or via KM for permission check
```

### Read Profile Data

```ts
const erc725 = new ERC725(
  LSP3Schemas,
  upAddress,
  'https://rpc.mainnet.lukso.network',
  { ipfsGateway: 'https://api.universalprofile.cloud/ipfs/' }
);

// Get encoded value (just the VerifiableURI bytes)
const raw = await erc725.getData('LSP3Profile');
// raw.value = '0x0000...' (VerifiableURI bytes)

// Fetch + decode + download JSON from IPFS
const profile = await erc725.fetchData('LSP3Profile');
// profile.value.LSP3Profile = { name, description, links, ... }
```

### VerifiableURI Encoding

```ts
import { encodeDataSourceWithHash } from '@erc725/erc725.js';

// Manual VerifiableURI encoding
const verifiableURI = encodeDataSourceWithHash(
  { method: 'keccak256(utf8)', data: '0xabcdef...' },
  'ipfs://QmYour...'
);
// Returns bytes like: 0x00006f357c6a0020<hash><url>

// Decode
import { decodeDataSourceWithHash } from '@erc725/erc725.js';
const decoded = decodeDataSourceWithHash(verifiableURI);
// { verification: { method, data }, source: 'ipfs://...' }
```

---

## 8. Universal Receiver (LSP1)

LSP1 is the notification system. When tokens are sent to a UP, the token contract calls `universalReceiver()` on the UP, which can react to it.

### How It Works

```
Token Transfer ──► token.transfer(from, to, ...)
                        │
                        ├─► _notifyTokenSender(from)  → calls from.universalReceiver(typeId, data)
                        │
                        └─► _notifyTokenReceiver(to)  → calls to.universalReceiver(typeId, data)
                                                              │
                                                              └─► Delegates to LSP1URD contract
                                                                  (if set in UP storage)
```

### TypeIds Reference

```
LSP7 Sender:   keccak256('LSP7Tokens_SenderNotification')
               0x429ac7a06903dbc9c13dfcb3c9d11df8194581fa047c96d7a4171fc7402958ea

LSP7 Receiver: keccak256('LSP7Tokens_RecipientNotification')
               0x20804611b3e2ea21c480dc465142210acf4a2485947541770ec1fb87dee4a55c

LSP8 Sender:   keccak256('LSP8Tokens_SenderNotification')
               0xb23eae7e6d1564b295b4c3e3be402d9a2f0776c57bdf365903496f6fa481ab00

LSP8 Receiver: keccak256('LSP8Tokens_RecipientNotification')
               0x0b084a55ebf70fd3c06fd755269dac2212c4d3f0f4d09079780bfa50c1b2984d

LSP26 Follow:  keccak256('LSP26FollowerSystem_FollowNotification')
               0x71e02f9f05bcd5816ec4f3134aa2e5a916669537ec6c77fe66ea595fabc2d51a

LSP26 Unfollow: keccak256('LSP26FollowerSystem_UnfollowNotification')
               0x9d3c0b4012b69658977b099bdaa51eff0f0460f421fba96d15669506c00d1c4f
```

### Custom Universal Receiver Delegate (Token Forwarder Example)

```solidity
// SPDX-License-Identifier: CC0-1.0
pragma solidity ^0.8.11;

import {IERC725X} from "@erc725/smart-contracts/contracts/interfaces/IERC725X.sol";
import {ILSP1UniversalReceiverDelegate} from
    "@lukso/lsp-smart-contracts/contracts/LSP1UniversalReceiver/ILSP1UniversalReceiverDelegate.sol";
import {ILSP7DigitalAsset} from
    "@lukso/lsp-smart-contracts/contracts/LSP7DigitalAsset/ILSP7DigitalAsset.sol";
import {ERC165} from "@openzeppelin/contracts/utils/introspection/ERC165.sol";
import {_TYPEID_LSP7_TOKENSRECIPIENT} from
    "@lukso/lsp-smart-contracts/contracts/LSP7DigitalAsset/LSP7Constants.sol";

contract TokenForwarder is ERC165, ILSP1UniversalReceiverDelegate {
    address public immutable recipient;
    uint256 public percentage; // e.g. 20 = 20%
    mapping(address => bool) public allowedTokens;

    constructor(address _recipient, uint256 _pct, address[] memory tokens) {
        recipient = _recipient;
        percentage = _pct;
        for (uint i; i < tokens.length; i++) allowedTokens[tokens[i]] = true;
    }

    function universalReceiverDelegate(
        address notifier,     // token contract that sent notification
        uint256 /*value*/,
        bytes32 typeId,
        bytes memory data
    ) external override returns (bytes memory) {
        // Only handle LSP7 incoming transfers
        if (typeId != _TYPEID_LSP7_TOKENSRECIPIENT) return "";

        // Only for allowed tokens
        if (!allowedTokens[notifier]) return "";

        // Decode transfer data: (operator, from, to, amount, force, transferData)
        (,, address to,, uint256 amount,,) =
            abi.decode(data, (address, address, address, address, uint256, bool, bytes));

        // Sanity check: we are the recipient
        if (to != msg.sender) return "";

        uint256 forwardAmount = (amount * percentage) / 100;

        // Forward via UP.execute() — requires SUPER_CALL + REENTRANCY permissions
        bytes memory transferPayload = abi.encodeWithSelector(
            ILSP7DigitalAsset.transfer.selector,
            msg.sender,   // from = the UP
            recipient,    // to = forwarding target
            forwardAmount,
            true,         // force = true (recipient may be EOA)
            ""
        );

        bytes memory executePayload = abi.encodeWithSelector(
            IERC725X.execute.selector,
            0,          // CALL operation
            notifier,   // target = token contract
            0,          // value
            transferPayload
        );

        // Re-enter UP (requires REENTRANCY permission)
        (bool success,) = msg.sender.call(executePayload);
        require(success, "Forward failed");

        return "";
    }

    // Required for ERC165 interface detection
    function supportsInterface(bytes4 interfaceId) public view override returns (bool) {
        return interfaceId == type(ILSP1UniversalReceiverDelegate).interfaceId
            || super.supportsInterface(interfaceId);
    }
}
```

### Register URD on a UP

```ts
import { ERC725 } from '@erc725/erc725.js';
import LSP1Schemas from '@erc725/erc725.js/schemas/LSP1UniversalReceiverDelegate.json';

const erc725 = new ERC725(LSP1Schemas);

// Set default URD (handles all typeIds without specific URD)
const encoded = erc725.encodeData([{
  keyName: 'LSP1UniversalReceiverDelegate',
  value: urdContractAddress,
}]);

await up.setData(encoded.keys[0], encoded.values[0]);

// Set type-specific URD (only handles one typeId)
// Key = keccak256('LSP1UniversalReceiverDelegate') + typeId
const typeSpecificKey = ethers.keccak256(
  ethers.concat([
    '0x0cfc51aec37c55a4d0b1a65c6255c4bf2fbdf6277f3cc0730c45b828b6db8b47',
    typeId
  ])
).slice(0, 26) + typeId.slice(2); // Mapping key format
```

### URD Permissions Required

For a URD to operate via `UP.execute()` (re-enter UP):
```ts
const urdPerms = { REENTRANCY: true, SUPER_SETDATA: true };
// If URD also calls execute on UP:
const urdWithCall = { REENTRANCY: true, SUPER_SETDATA: true, SUPER_CALL: true };
```

---

## 9. The Grid (LSP28)

LSP28 defines a customizable widget grid for Universal Profiles, displayed on universaleverything.io.

### ERC725Y Data Key

```
Name:     LSP28TheGrid
Key:      0x724141d9918ce69e6b8afcf53a91748466086ba2c74b94cab43c649ae2ac23ff
Type:     VerifiableURI → points to a JSON file
```

### Grid JSON Format

```json
{
  "LSP28TheGrid": [
    {
      "title": "My Profile Grid",
      "gridColumns": 3,
      "visibility": "public",
      "grid": [
        {
          "width": 2,
          "height": 2,
          "type": "IFRAME",
          "properties": {
            "src": "https://myapp.com/widget",
            "sandbox": "allow-scripts allow-same-origin",
            "allowfullscreen": false
          }
        },
        {
          "width": 1,
          "height": 1,
          "type": "TEXT",
          "properties": {
            "title": "Welcome!",
            "text": "This is my **LUKSO** profile.",
            "textColor": "#ffffff",
            "backgroundColor": "#1a1a2e",
            "link": "https://lukso.network"
          }
        },
        {
          "width": 2,
          "height": 2,
          "type": "IMAGES",
          "properties": {
            "type": "carousel",
            "images": [
              "ipfs://QmImage1...",
              "ipfs://QmImage2..."
            ]
          }
        },
        {
          "width": 2,
          "height": 1,
          "type": "X",
          "properties": {
            "type": "post",
            "username": "myhandle",
            "id": "1234567890",
            "theme": "dark"
          }
        },
        {
          "width": 2,
          "height": 2,
          "type": "INSTAGRAM",
          "properties": {
            "type": "p",
            "id": "postId123"
          }
        },
        {
          "width": 1,
          "height": 1,
          "type": "QR_CODE",
          "properties": {
            "data": "https://universaleverything.io/0xYourAddress"
          }
        }
      ]
    }
  ]
}
```

**Grid Types:** `IFRAME` | `TEXT` | `IMAGES` | `X` | `INSTAGRAM` | `ELFSIGHT` | `QR_CODE`  
**Width/Height:** 1-3 (steps; interface determines pixel size)  
**gridColumns:** 2-4 recommended

### Set Grid on Profile

```ts
import { ERC725 } from '@erc725/erc725.js';
import { IPFSHttpClientUploader } from '@lukso/data-provider-ipfs-http-client';

const GRID_SCHEMA = [{
  name: 'LSP28TheGrid',
  key: '0x724141d9918ce69e6b8afcf53a91748466086ba2c74b94cab43c649ae2ac23ff',
  keyType: 'Singleton',
  valueType: 'bytes',
  valueContent: 'VerifiableURI',
}];

async function setGrid(upAddress: string, gridJson: object) {
  const ipfs = new IPFSHttpClientUploader('https://api.pinata.cloud/pinning/pinFileToIPFS');
  const { url, hash } = await ipfs.upload(gridJson);

  const erc725 = new ERC725(GRID_SCHEMA);
  const encoded = erc725.encodeData([{
    keyName: 'LSP28TheGrid',
    value: {
      verification: { method: 'keccak256(utf8)', data: hash },
      url,
    },
  }]);

  const up = new ethers.Contract(upAddress, UP_ABI, signer);
  await up.setData(encoded.keys[0], encoded.values[0]);
}
```

### Read Grid

```ts
const erc725 = new ERC725(
  GRID_SCHEMA,
  upAddress,
  rpcUrl,
  { ipfsGateway: 'https://api.universalprofile.cloud/ipfs/' }
);

const grid = await erc725.fetchData('LSP28TheGrid');
// grid.value = { LSP28TheGrid: [...] }
```

---

## 10. Followers (LSP26)

LSP26 is a singleton registry contract for on-chain follows/followers. All LUKSO profiles share one global registry.

### Contract Address (All Chains via Nick Factory)

```
0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA
```

### Interface

```solidity
interface ILSP26 {
    event Follow(address indexed follower, address indexed addr);
    event Unfollow(address indexed unfollower, address indexed addr);

    function follow(address addr) external;
    function followBatch(address[] memory addresses) external;
    function unfollow(address addr) external;
    function unfollowBatch(address[] memory addresses) external;
    function isFollowing(address follower, address addr) external view returns (bool);
    function followerCount(address addr) external view returns (uint256);
    function followingCount(address addr) external view returns (uint256);
    function getFollowsByIndex(address addr, uint256 startIndex, uint256 endIndex)
        external view returns (address[] memory);
    function getFollowersByIndex(address addr, uint256 startIndex, uint256 endIndex)
        external view returns (address[] memory);
}
```

### Follow / Unfollow (JS)

```ts
const LSP26_ADDRESS = '0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA';

const LSP26_ABI = [
  'function follow(address addr) external',
  'function followBatch(address[] memory addresses) external',
  'function unfollow(address addr) external',
  'function unfollowBatch(address[] memory addresses) external',
  'function isFollowing(address follower, address addr) view returns (bool)',
  'function followerCount(address addr) view returns (uint256)',
  'function followingCount(address addr) view returns (uint256)',
  'function getFollowsByIndex(address addr, uint256 start, uint256 end) view returns (address[])',
  'function getFollowersByIndex(address addr, uint256 start, uint256 end) view returns (address[])',
];

const registry = new ethers.Contract(LSP26_ADDRESS, LSP26_ABI, signer);

// Follow from UP (via UP.execute → KM.execute)
// The UP calls follow() on the registry
const followPayload = registry.interface.encodeFunctionData('follow', [targetAddress]);
const up = new ethers.Contract(upAddress, UP_ABI, signer);
await up.execute(
  0,              // CALL
  LSP26_ADDRESS,
  0,              // no LYX
  followPayload
);

// Unfollow
const unfollowPayload = registry.interface.encodeFunctionData('unfollow', [targetAddress]);
await up.execute(0, LSP26_ADDRESS, 0, unfollowPayload);

// Read-only queries (no signer needed)
const registryRead = new ethers.Contract(LSP26_ADDRESS, LSP26_ABI, provider);

const isFollowing = await registryRead.isFollowing(followerAddress, targetAddress);
const followerCount = await registryRead.followerCount(targetAddress);
const followingCount = await registryRead.followingCount(upAddress);

// Paginated followers list
const followers = await registryRead.getFollowersByIndex(targetAddress, 0, 100);
const following = await registryRead.getFollowsByIndex(upAddress, 0, 100);
```

### LSP1 Notifications on Follow

When you call `follow(addr)`, the registry calls `addr.universalReceiver(typeId, data)` if supported:
```
typeId = 0x71e02f9f05bcd5816ec4f3134aa2e5a916669537ec6c77fe66ea595fabc2d51a
data = abi.encodePacked(followerAddress)
```

### Gasless Follow via Relay

```ts
// Encode nested call: controller signs → KM executes → UP executes → Registry.follow()
const followPayload = registry.interface.encodeFunctionData('follow', [targetAddress]);
const upExecutePayload = iface.encodeFunctionData('execute', [0, LSP26_ADDRESS, 0, followPayload]);

const txHash = await executeGasless(privateKey, upAddress, upExecutePayload);
```

---

## 11. Dev Tools

### Package Overview

```bash
# Core smart contracts (Solidity + ABIs + constants)
npm install @lukso/lsp-smart-contracts

# ERC725Y data encoding/decoding library
npm install @erc725/erc725.js

# IPFS upload helpers
npm install @lukso/data-provider-ipfs-http-client

# LSP26 types and constants
npm install @lukso/lsp26-contracts

# UP Provider (for mini-apps in The Grid)
npm install @lukso/up-provider
```

### erc725.js — Key Patterns

```ts
import ERC725, { ERC725JSONSchema } from '@erc725/erc725.js';
import LSP3Schemas from '@erc725/erc725.js/schemas/LSP3ProfileMetadata.json';
import LSP6Schemas from '@erc725/erc725.js/schemas/LSP6KeyManager.json';
import LSP1Schemas from '@erc725/erc725.js/schemas/LSP1UniversalReceiverDelegate.json';
import LSP5Schemas from '@erc725/erc725.js/schemas/LSP5ReceivedAssets.json';
import LSP10Schemas from '@erc725/erc725.js/schemas/LSP10ReceivedVaults.json';
import LSP12Schemas from '@erc725/erc725.js/schemas/LSP12IssuedAssets.json';

// Instance with network connection
const erc725 = new ERC725(
  [...LSP3Schemas, ...LSP6Schemas, ...LSP1Schemas],
  '0xUP_ADDRESS',
  'https://rpc.mainnet.lukso.network',
  { ipfsGateway: 'https://api.universalprofile.cloud/ipfs/' }
);

// Fetch all profile data
const profile = await erc725.fetchData('LSP3Profile');

// Fetch multiple keys at once
const [profile, controllers, assets] = await erc725.getData([
  'LSP3Profile',
  'AddressPermissions[]',
  'LSP5ReceivedAssets[]',
]);

// Encode permissions
const permsHex = erc725.encodePermissions({ CALL: true, SETDATA: true });

// Decode permissions
const permsObj = erc725.decodePermissions('0x0000...0840');
// { CALL: true, SETDATA: true, ... }

// Static methods (no instance needed)
const encoded = ERC725.encodeData([...], schemas);
const decoded = ERC725.decodeData([...], schemas);

// Encode any value type
import { encodeValueType } from '@erc725/erc725.js';
const uint = encodeValueType('uint128', 42);
const addr = encodeValueType('address', '0x...');
```

### ethers.js v6 Patterns for LUKSO

```ts
import { ethers } from 'ethers';

// Connect to LUKSO
const provider = new ethers.JsonRpcProvider('https://rpc.mainnet.lukso.network');
const wallet = new ethers.Wallet(privateKey, provider);

// Get UP's Key Manager address
async function getKeyManager(upAddress: string) {
  const up = new ethers.Contract(upAddress,
    ['function owner() view returns (address)'],
    provider
  );
  return up.owner(); // = KM address
}

// Call UP via Key Manager (controller → KM → UP)
async function callViaKM(
  controller: ethers.Wallet,
  upAddress: string,
  payload: string  // encoded function call for UP
) {
  const kmAddress = await getKeyManager(upAddress);
  const km = new ethers.Contract(kmAddress,
    ['function execute(bytes calldata payload) returns (bytes memory)'],
    controller
  );
  return km.execute(payload);
}

// Direct UP call (must be called by KM or owner)
// Usually you call KM.execute(payload_for_UP)

// Read ERC725Y data
async function getData(upAddress: string, key: string) {
  const up = new ethers.Contract(upAddress,
    ['function getData(bytes32 dataKey) view returns (bytes memory)'],
    provider
  );
  return up.getData(key);
}
```

### UP Browser Extension Integration

```ts
// Check if extension is installed
if (!window.lukso) {
  alert('Please install the Universal Profile Browser Extension');
  return;
}

// Connect
const [upAddress] = await window.lukso.request({ method: 'eth_requestAccounts' });

// Use with ethers.js
import { BrowserProvider } from 'ethers';
const provider = new BrowserProvider(window.lukso);
const signer = await provider.getSigner();

// The signer routes through KM automatically
// Just call functions directly on the UP contract
const up = new ethers.Contract(upAddress, UP_ABI, signer);
await up.setData(key, value); // Extension handles KM routing + signing

// Chain ID check
const { chainId } = await provider.getNetwork();
if (chainId !== 42n) {
  await window.lukso.request({
    method: 'wallet_switchEthereumChain',
    params: [{ chainId: '0x2A' }], // 42 hex
  });
}
```

### Envio Indexer (GraphQL)

```
Endpoint: https://envio.lukso-mainnet.universal.tech/v1/graphql

Resolve username → address:
curl -X POST https://envio.lukso-mainnet.universal.tech/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Profile(where: {name: {_eq: \"username\"}}) { id name } }"}'

Query token transfers:
curl -X POST https://envio.lukso-mainnet.universal.tech/v1/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Token_transfer(where: {from: {_eq: \"0x...\"}}) { id from to amount } }"}'
```

---

## 12. Common Pitfalls

### 1. `force` Parameter Confusion

```ts
// ❌ WRONG: Sending to EOA without force
await token.transfer(from, eoaAddress, amount, false, '0x');
// → REVERTS: "LSP7NotifyTokenReceiverIsEOA"

// ❌ WRONG: Assuming force=true is always safe
await token.transfer(from, randomContract, amount, true, '0x');
// → No error, but tokens may be stuck if contract can't use them

// ✅ CORRECT: Production transfers to UPs
await token.transfer(from, upAddress, amount, false, '0x');
// force=false ensures recipient can handle tokens

// ✅ CORRECT: Testing/bridging with EOA recipient
await token.transfer(from, testEOA, amount, true, '0x');
// force=true explicitly, you understand the risk
```

### 2. LSP6 Permission Complexity

```ts
// ❌ WRONG: Giving SETDATA without specifying which keys
// (Actually works but risky — controller can set ANY data except permission keys)
// Better to use SUPER_SETDATA for full access or SETDATA + AllowedERC725YDataKeys

// ❌ WRONG: Forgetting to update AddressPermissions[] array
// The array must include ALL controller addresses or the KM won't know about them
erc725.encodeData([
  { keyName: 'AddressPermissions:Permissions:<address>', ... },
  // Missing AddressPermissions[] update → controller added silently but array wrong
]);

// ✅ CORRECT: Always update the array when adding/removing controllers
erc725.encodeData([
  { keyName: 'AddressPermissions:Permissions:<address>', dynamicKeyParts: [newCtrl], value: perms },
  { keyName: 'AddressPermissions[]', value: [existingCtrl, newCtrl] }, // include ALL
]);

// ❌ WRONG: EDITPERMISSIONS lets controller edit its OWN permissions!
// Never give untrusted parties EDITPERMISSIONS

// ❌ WRONG: DELEGATECALL won't work even if set
// It's blocked at contract level for security
```

### 3. Gas Estimation Issues

```ts
// ❌ WRONG: Default gas limit often too low for complex UP interactions
await up.execute(0, target, 0, payload);
// → "out of gas" especially with URD hooks

// ✅ CORRECT: Estimate first, add buffer
const estimated = await up.execute.estimateGas(0, target, 0, payload);
await up.execute(0, target, 0, payload, { gasLimit: estimated * 120n / 100n }); // +20%

// Note: URD callbacks add significant gas (100k-300k extra for complex URDs)
// Relay service: 20M gas/month quota — don't waste on large operations

// Common gas costs:
// Simple setData: ~50k gas
// Token transfer (with URD): ~200-400k gas
// UP deployment via LSP23: ~1-2M gas
```

### 4. ERC725Y Data Encoding

```ts
// ❌ WRONG: Using raw ethers.js ABI encoding for ERC725Y keys
const key = ethers.keccak256(ethers.toUtf8Bytes('LSP3Profile'));
// → Returns FULL keccak256. LSP keys have specific formats!

// ✅ CORRECT: Use erc725.js for all key/value encoding
const encoded = ERC725.encodeData(
  [{ keyName: 'LSP3Profile', value: { json, url } }],
  LSP3Schemas
);
// erc725.js handles key format, value encoding, VerifiableURI, etc.

// ❌ WRONG: Direct bytes manipulation for VerifiableURI
// VerifiableURI has specific prefix bytes (0x00006f357c6a...)

// ✅ CORRECT: Use encodeDataSourceWithHash
const uri = encodeDataSourceWithHash(
  { method: 'keccak256(utf8)', data: hash },
  'ipfs://Qm...'
);

// ❌ WRONG: Not accounting for dynamic keys
// 'AddressPermissions:Permissions:<address>' requires dynamicKeyParts!
erc725.encodeData([{
  keyName: 'AddressPermissions:Permissions:<address>',
  // Missing dynamicKeyParts: [address]
}]);
```

### 5. LSP25 Signature Mistakes

```ts
// ❌ WRONG: Using wallet.signMessage() (EIP-191 v0x45, "Ethereum Signed Message:")
const sig = await wallet.signMessage(hash);
// → WRONG prefix! Relay will reject it.

// ✅ CORRECT: Use SigningKey.sign() for raw EIP-191 v0
const signingKey = new ethers.SigningKey(privateKey);
const hash = ethers.keccak256(
  ethers.concat(['0x19', '0x00', keyManagerAddress, encodedMessage])
);
const sig = signingKey.sign(hash); // signs RAW hash without any prefix

// ❌ WRONG: Reusing nonces
// If nonce N is submitted, it increments. Don't cache nonces across multiple calls.

// ❌ WRONG: Wrong chain ID in LSP25 message
// Mainnet = 42, Testnet = 4201. Cross-chain replay attacks prevented by this.

// ❌ WRONG: Controller missing EXECUTE_RELAY_CALL permission
// Relay will reject even with valid signature
```

### 6. UP Architecture Confusion

```ts
// ❌ WRONG: Thinking you interact with UP directly
// UP.execute() can only be called by its owner (= Key Manager)

// ✅ CORRECT: Controller → KM.execute(payload) → UP.execute(...)
// Or: Controller signs → Relay → KM.executeRelayCall() → UP.execute(...)

// ❌ WRONG: Checking balances/permissions on Key Manager
// All data is on UP! KM is just the gateway.

// ✅ CORRECT:
const balance = await provider.getBalance(upAddress);  // LYX balance on UP
const perms = await up.getData(permissionKey);          // permissions in UP storage
```

### 7. Token Hooks Causing Unexpected Reverts

```ts
// When you transfer tokens TO a UP:
// 1. Token calls up.universalReceiver(...)
// 2. UP calls its URD
// 3. URD might do SETDATA or other operations
// If ANY of these fail → ENTIRE transfer reverts!

// Common cause: URD out of gas
// Fix: increase gas limit

// Common cause: URD has a bug / reverts intentionally (user blocked tokens)
// This is by design — UP owner controls what they accept

// To bypass: use force=true (skips universalReceiver call on recipient)
// But then LSP1 recipient notification is skipped
```

---

## 13. Key Contract Addresses

| Contract | Address |
|---|---|
| LSP23 Linked Contracts Factory | `0x2300000A84D25dF63081feAa37ba6b62C4c89a30` |
| LSP23 Post Deployment Module | `0x000000000066093407b6704B89793beFfD0D8F00` |
| Universal Profile Implementation | `0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F` |
| LSP6 Key Manager Implementation | `0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4` |
| Default URD (Mainnet) | `0x7870C5B8BC9572A8001C3f96f7ff59961B23500D` |
| LSP26 Follower Registry | `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` |

### Key Data Keys (ERC725Y)

| Name | Key |
|---|---|
| LSP3Profile | `0x5ef83ad9559033e6e941db7d7c495acdce616347d28e90c7ce47cbfcfcad3bc5` |
| LSP1UniversalReceiverDelegate | `0x0cfc51aec37c55a4d0b1a65c6255c4bf2fbdf6277f3cc0730c45b828b6db8b47` |
| LSP5ReceivedAssets[] | `0x6460ee3c0aac563ccbf76d6e1d07bada78e3a9514e6382b736ed3f478ab7b90b` |
| LSP12IssuedAssets[] | `0x7c8c3416d6cda87cd42c71ea1843df28ac4850354f988d55ee2eaa47b6dc05cd` |
| LSP28TheGrid | `0x724141d9918ce69e6b8afcf53a91748466086ba2c74b94cab43c649ae2ac23ff` |
| AddressPermissions[] | `0xdf30dba06db6a30e65354d9a64c609861f089545ca58c6b4dbe31a5f338cb0e3` |

### Useful Links

- Docs: https://docs.lukso.tech
- LIPs (standards): https://github.com/lukso-network/LIPs
- Smart Contracts: https://github.com/lukso-network/lsp-smart-contracts
- erc725.js: https://github.com/ERC725Alliance/erc725.js
- ERC725 Inspect Tool: https://erc725-inspect.lukso.tech
- Universal Everything: https://universaleverything.io
- UP Profile Viewer: https://universalprofile.cloud
- Playground: https://github.com/lukso-network/lukso-playground
- LUKSO Envio Indexer: https://envio.lukso-mainnet.universal.tech/v1/graphql
