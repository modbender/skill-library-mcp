# LUKSO Contracts, Repos & API Reference

> Last updated: 2026-02-18  
> Source: [docs.lukso.tech](https://docs.lukso.tech), GitHub, NPM registry  
> Network: **LUKSO Mainnet** — Chain ID **42** — Currency: **LYX**

---

## 🌐 Network Parameters

| Setting                 | Value                                                  |
|-------------------------|--------------------------------------------------------|
| Chain ID / Network ID   | **42**                                                 |
| Network Name            | LUKSO                                                  |
| Currency Symbol         | LYX                                                    |
| Genesis Fork Version    | `0x42000001`                                           |
| Testnet Chain ID        | **4201**                                               |
| Testnet Network Name    | LUKSO Testnet                                          |

### RPC Endpoints

| Provider   | Mainnet URL                              | Testnet URL                               |
|------------|------------------------------------------|-------------------------------------------|
| Official   | `https://rpc.mainnet.lukso.network`      | `https://rpc.testnet.lukso.network`       |
| Thirdweb   | `https://42.rpc.thirdweb.com`            | —                                         |
| Envio      | `https://lukso.rpc.hypersync.xyz`        | —                                         |
| SigmaCore  | `https://rpc.lukso.sigmacore.io`         | (requires API key)                        |
| NowNodes   | `https://lukso.nownodes.io`              | (requires API key)                        |

---

## 📋 Deployed Contract Addresses (Mainnet)

### 🏭 Factory Contracts

These are **singletons** deployed once, used by all.

| Contract | Address |
|----------|---------|
| **LSP23 Linked Contracts Factory** | `0x2300000A84D25dF63081feAa37ba6b62C4c89a30` |
| **UP Post Deployment Module** (LSP23) | `0x000000000066093407b6704B89793beFfD0D8F00` |
| **LSP16 Universal Factory** | `0x1600016e23e25D20CA8759338BfB8A8d11563C4e` |

**Nick Factory** (used to deploy the above): `0x4e59b44847b379578588920ca78fbf26c0b4956c`

> The LSP23 factory is the **primary deployment path** for Universal Profiles. It deploys UP + KeyManager as EIP-1167 minimal proxies in a single transaction and calls the Post Deployment Module to set up permissions.

### 📑 Implementation Contracts (current: v0.14.0)

EIP-1167 minimal proxies for each user UP/KM point to these implementation contracts.

| Contract | Version | Address |
|----------|---------|---------|
| **Universal Profile (LSP0) Impl** | v0.14.0 | `0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F` |
| **LSP6 Key Manager Impl** | v0.14.0 | `0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4` |
| **LSP1 Universal Receiver Delegate UP** | v0.14.0 | `0x7870C5B8BC9572A8001C3f96f7ff59961B23500D` |
| **LSP7 Mintable (Init)** | v0.14.0 | `0x28B7CcdaD1E15cCbDf380c439Cc1F2EBe7f5B2d8` |
| **LSP8 Mintable (Init)** | v0.14.0 | `0xd787a2f6B14d4dcC2fb897f40b87f2Ff63a07997` |

### 📑 Legacy Implementation Contracts (v0.12.1)

Older UPs deployed before v0.14.0 use these. Still functional on-chain.

| Contract | Version | Address |
|----------|---------|---------|
| Universal Profile Impl | v0.12.1 | `0x52c90985AF970D4E0DC26Cb5D052505278aF32A9` |
| LSP6 Key Manager Impl  | v0.12.1 | `0xa75684d7D048704a2DB851D05Ba0c3cbe226264C` |
| LSP1 URD UP            | v0.12.1 | `0xA5467dfe7019bF2C7C5F7A707711B9d4cAD118c8` |

### 🌐 Social / Other Contracts

| Contract | Address | Notes |
|----------|---------|-------|
| **LSP26 Follower System** | `0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA` | Follow/unfollow on-chain |

### Key Constants

```typescript
// From @lukso/lsp-smart-contracts
const LSP23_FACTORY_ADDRESS        = '0x2300000A84D25dF63081feAa37ba6b62C4c89a30';
const LSP23_POST_DEPLOYMENT_MODULE = '0x000000000066093407b6704B89793beFfD0D8F00';
const UP_IMPLEMENTATION_ADDRESS    = '0x3024D38EA2434BA6635003Dc1BDC0daB5882ED4F';
const KM_IMPLEMENTATION_ADDRESS    = '0x2Fe3AeD98684E7351aD2D408A43cE09a738BF8a4';
const UNIVERSAL_RECEIVER_DELEGATE  = '0x7870C5B8BC9572A8001C3f96f7ff59961B23500D';
const LSP16_UNIVERSAL_FACTORY      = '0x1600016e23e25D20CA8759338BfB8A8d11563C4e';
const LSP26_FOLLOWER_SYSTEM        = '0xf01103E5a9909Fc0DBe8166dA7085e0285daDDcA';
```

---

## 🔌 API Endpoints

### Envio GraphQL Indexer

Index of Universal Profiles, tokens, NFTs, events — queries or subscriptions.

| Network  | URL |
|----------|-----|
| **Mainnet** | `https://envio.lukso-mainnet.universal.tech/v1/graphql` |
| Testnet  | `https://envio.lukso-testnet.universal.tech/v1/graphql` |
| WebSocket (subscriptions) | `wss://envio.lukso-mainnet.universal.tech/v1/graphql` |
| Interactive Playground   | `https://envio.lukso-mainnet.universal.tech/` |

**Example query** (resolve username → UP address):
```bash
curl -s -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "{ Profile(where: {name: {_eq: \"schizo\"}}) { id name } }"}' \
  https://envio.lukso-mainnet.universal.tech/v1/graphql
```

### Transaction Relay Service (Gasless TX)

No API key required — uses LSP25 signatures for authorization.  
UP must be **registered** with the relayer to use free quota (20M gas/month).

| | Mainnet | Testnet |
|-|---------|---------|
| **Base URL** | `https://relayer.mainnet.lukso.network` | `https://relayer.testnet.lukso.network` |
| Execute TX | `POST /api/execute` | `POST /api/execute` |
| Check Quota | `POST /api/quota` | `POST /api/quota` |

**Execute request body:**
```json
{
  "address": "0x<UP_ADDRESS>",
  "transaction": {
    "abi": "0x<ENCODED_PAYLOAD>",
    "signature": "0x<LSP25_EIP191_V0_SIG>",
    "nonce": 0,
    "validityTimestamps": "0x0"
  }
}
```

> ⚠️ Sign with `SigningKey.sign(hash)` — **NOT** `wallet.signMessage()`. This is EIP-191 v0 (0x00), not the Ethereum Signed Message format.

### Relayer User API (Deploy / Register UPs)

Requires an API key (`Authorization: Bearer <key>`). **Private beta** — apply at https://forms.gle/rhWA25m3jjuPNPva9

| | Mainnet | Testnet |
|-|---------|---------|
| **Base URL** | `https://relayer-api.mainnet.lukso.network` | `https://relayer-api.testnet.lukso.network` |
| Deploy UP | `POST /api/universal-profile` | `POST /api/universal-profile` |
| Register UP | `POST /api/universal-profile/register` | `POST /api/universal-profile/register` |
| Swagger Docs | `https://relayer-api.mainnet.lukso.network/docs#/` | `https://relayer-api.testnet.lukso.network/docs#/` |

### Block Explorers

| Explorer | URL | API |
|----------|-----|-----|
| Execution (Blockscout) | `https://explorer.lukso.network` | `https://explorer.execution.mainnet.lukso.network/api` |
| Blockscout v2 API | — | `https://explorer.execution.mainnet.lukso.network/api/v2/` |
| Consensus (Beaconcha.in-style) | `https://explorer.consensus.mainnet.lukso.network` | `https://explorer.consensus.mainnet.lukso.network/api/v1/` |
| Execution Stats | `https://stats.execution.mainnet.lukso.network` | — |
| Client Diversity | `https://clientdiversity.lukso.network` | — |
| Checkpoints | `https://checkpoints.mainnet.lukso.network` | — |

### IPFS Gateway

> ⚠️ For **development only** — no SLA, rate limits may apply. Use Pinata/Infura for production.

```
https://api.universalprofile.cloud/ipfs/<CID>
```

**Example:**
```bash
curl "https://api.universalprofile.cloud/ipfs/QmPRoJsaYcNqQiUrQxE7ajTRaXwHyAU29tHqYNctBmK64w"
```

---

## 📦 NPM Packages

### Official LUKSO Packages

| Package | Version | Description |
|---------|---------|-------------|
| `@lukso/lsp-smart-contracts` | **v0.16.7** | All LSP Solidity contracts + ABIs + constants |
| `@erc725/erc725.js` | **v0.28.2** | Encode/decode ERC725Y data keys and values |
| `@lukso/lsp-utils` | **v0.2.0** | TypeScript utility functions for LSPs |
| `@lukso/eip191-signer.js` | **v0.2.5** | Sign EIP-191 data (LSP6 relay calls) |
| `@lukso/up-provider` | **v0.3.7** | EIP-1193 provider for mini-apps (UP Browser Extension) |

### What's in `@lukso/lsp-smart-contracts`

The main package exports:
- **ABIs** (artifacts JSON) for all LSP contracts
- **Interface IDs** (ERC165): `INTERFACE_IDS.LSP0ERC725Account`, `.LSP6KeyManager`, `.LSP7DigitalAsset`, `.LSP8IdentifiableDigitalAsset`, `.LSP26FollowerSystem`, etc.
- **ERC725Y Data Keys**: `ERC725YDataKeys.LSP3`, `.LSP4`, `.LSP5`, `.LSP6`, etc.
- **Permission constants**: `ALL_PERMISSIONS`, `PERMISSIONS.CALL`, `.SETDATA`, etc.
- **Type IDs** (for URD): `LSP1_TYPE_IDS`
- **Other constants**: `LSP8_TOKEN_ID_FORMAT`, `LSP4_TOKEN_TYPES`, `OPERATION_TYPES`

```typescript
import {
  INTERFACE_IDS,
  ERC725YDataKeys,
  ALL_PERMISSIONS,
  PERMISSIONS,
  LSP8_TOKEN_ID_FORMAT,
  LSP4_TOKEN_TYPES,
  LSP1_TYPE_IDS,
} from '@lukso/lsp-smart-contracts';
```

Individual packages (sub-packages of lsp-smart-contracts monorepo):
- `@lukso/lsp0-contracts` — ERC725Account (Universal Profile)
- `@lukso/lsp1-contracts` — Universal Receiver
- `@lukso/lsp1delegate-contracts` — Universal Receiver Delegate
- `@lukso/lsp2-contracts` — ERC725Y JSON Schema
- `@lukso/lsp3-contracts` — Profile Metadata
- `@lukso/lsp4-contracts` — Digital Asset Metadata
- `@lukso/lsp5-contracts` — Received Assets
- `@lukso/lsp6-contracts` — Key Manager
- `@lukso/lsp7-contracts` — Digital Asset (Fungible)
- `@lukso/lsp8-contracts` — Identifiable Digital Asset (NFT)
- `@lukso/lsp9-contracts` — Vault
- `@lukso/lsp10-contracts` — Received Vaults
- `@lukso/lsp11-contracts` — Basic Social Recovery
- `@lukso/lsp12-contracts` — Issued Assets
- `@lukso/lsp14-contracts` — Ownable2Step
- `@lukso/lsp16-contracts` — Universal Factory
- `@lukso/lsp17contractextension-contracts` — Contract Extension
- `@lukso/lsp20-contracts` — Call Verification
- `@lukso/lsp23-contracts` — Linked Contracts Factory
- `@lukso/lsp25-contracts` — Execute Relay Call
- `@lukso/lsp26-contracts` — Follower System

---

## 🐙 GitHub Repositories

Organization: **https://github.com/lukso-network**

### 🔑 Core / Must-Know Repos

| Repo | Stars | Description |
|------|-------|-------------|
| [lsp-smart-contracts](https://github.com/lukso-network/lsp-smart-contracts) | ⭐82 | Reference Solidity implementation of all LSP standards (monorepo) |
| [LIPs](https://github.com/lukso-network/LIPs) | ⭐98 | LUKSO Improvement Proposals — specifications for all LSP standards |
| [docs](https://github.com/lukso-network/docs) | ⭐30 | LUKSO technical documentation (docs.lukso.tech source) |
| [network-configs](https://github.com/lukso-network/network-configs) | ⭐14 | Mainnet/testnet network config files |
| [lukso-playground](https://github.com/lukso-network/lukso-playground) | ⭐24 | Code snippets for UP/LSP interactions (Hardhat + ethers.js) |
| [tools-lukso-cli](https://github.com/lukso-network/tools-lukso-cli) | ⭐19 | CLI to download/run LUKSO node clients |

### 🛠️ Tools / Libraries

| Repo | Stars | Description |
|------|-------|-------------|
| [tools-erc725-inspect](https://github.com/lukso-network/tools-erc725-inspect) | ⭐10 | Website to inspect ERC725Y key-value stores (erc725-inspect.lukso.tech) |
| [tools-lsp-factory](https://github.com/lukso-network/tools-lsp-factory) | ⭐16 | **Legacy** easy deployment tool for UPs and Digital Assets |
| [lsp-utils](https://github.com/lukso-network/lsp-utils) | ⭐0 | TypeScript utility functions for LSPs |
| [tools-eip191-signer](https://github.com/lukso-network/tools-eip191-signer) | ⭐3 | EIP-191 signer for relay calls |
| [tools-up-provider](https://github.com/lukso-network/tools-up-provider) | ⭐2 | EIP-1193 provider for UP mini-apps |
| [tools-data-providers](https://github.com/lukso-network/tools-data-providers) | ⭐1 | Upload/download from IPFS, Arweave, etc. |
| [tools-dapp-boilerplate](https://github.com/lukso-network/tools-dapp-boilerplate) | ⭐11 | LUKSO dApp template (Next.js) |
| [tools-mock-relayer](https://github.com/lukso-network/tools-mock-relayer) | ⭐2 | Mock relayer for LSP15 testing |
| [awesome-lukso](https://github.com/lukso-network/awesome-lukso) | ⭐10 | Community resource list |

### 🖥️ Front-End / dApps

| Repo | Stars | Description |
|------|-------|-------------|
| [universalprofile.cloud](https://github.com/lukso-network/universalprofile.cloud) | ⭐8 | Universal Profile website (UP Browser, token/NFT viewer) |
| [universalprofile-test-dapp](https://github.com/lukso-network/universalprofile-test-dapp) | ⭐18 | Testing dApp for ERC725 and Universal Profiles |
| [example-dapp-lsps](https://github.com/lukso-network/example-dapp-lsps) | ⭐7 | Example dApp with LSP7/LSP8 tokens and NFTs |
| [example-dapps](https://github.com/lukso-network/example-dapps) | ⭐3 | Web3.js example dApps |
| [miniapp-nextjs-template](https://github.com/lukso-network/miniapp-nextjs-template) | ⭐7 | Next.js template for Grid mini-apps |

### 🌐 Services

| Repo | Stars | Description |
|------|-------|-------------|
| [service-ipfs-proxy](https://github.com/lukso-network/service-ipfs-proxy) | ⭐1 | IPFS proxy API |
| [web3-onboard-config](https://github.com/lukso-network/web3-onboard-config) | ⭐1 | UP integration for Web3-Onboard |
| [lsp-bridge-HypLSP7](https://github.com/lukso-network/lsp-bridge-HypLSP7) | ⭐1 | Hyperlane bridge for LSP7 tokens |

### 📚 Standards Reference Repos

| Repo | Stars | Description |
|------|-------|-------------|
| [lsp17-extensions](https://github.com/lukso-network/lsp17-extensions) | ⭐0 | LSP17 extension contracts |
| [universalprofile-subgraph](https://github.com/lukso-network/universalprofile-subgraph) | ⭐2 | TheGraph subgraph for Universal Profiles |

---

## 📐 Interface IDs (ERC165)

Key IDs to check via `supportsInterface(interfaceId)`:

| Standard | Interface ID |
|----------|-------------|
| ERC165 | `0x01ffc9a7` |
| ERC1271 | `0x1626ba7e` |
| ERC725X | `0x7545acac` |
| ERC725Y | `0x629aa694` |
| LSP0 ERC725Account (UP) | `0x24871b3d` |
| LSP1 Universal Receiver | `0x6bb56a14` |
| LSP1 Universal Receiver Delegate | `0xa3427fd8` |
| LSP6 Key Manager | `0x23f34c62` |
| LSP7 Digital Asset | `0xc52d6008` |
| LSP8 Identifiable Digital Asset | `0x3a271706` |
| LSP9 Vault | `0x28af17e6` |
| LSP11 Social Recovery | `0x049a28f1` |
| LSP14 Ownable2Step | `0x94be5999` |
| LSP17 Extendable | `0xa918fa6b` |
| LSP17 Extension | `0xcee78b40` |
| LSP20 Call Verification | `0x1a0eb6a5` |
| LSP20 Call Verifier | `0x480c0ec2` |
| LSP25 Execute Relay Call | `0x5ac79908` |
| LSP26 Follower System | `0x2f554be6` |

---

## 🔑 Key ERC725Y Data Keys

Important data keys stored in Universal Profiles:

| Key Name | Purpose |
|----------|---------|
| `LSP3Profile` | Profile metadata (name, description, avatar) |
| `LSP1UniversalReceiverDelegate` | Default URD contract address |
| `LSP5ReceivedAssets[]` | Array of received tokens |
| `LSP10ReceivedVaults[]` | Array of received vaults |
| `LSP12IssuedAssets[]` | Array of issued assets |
| `AddressPermissions[]` | Array of controller addresses |
| `AddressPermissions:Permissions:<addr>` | Permission bitmap for a controller |
| `AddressPermissions:AllowedCalls:<addr>` | Allowed calls whitelist |
| `AddressPermissions:AllowedERC725YDataKeys:<addr>` | Allowed data keys |

---

## 🔗 Useful Links

| Resource | URL |
|----------|-----|
| Docs | https://docs.lukso.tech |
| ERC725 Inspect Tool | https://erc725-inspect.lukso.tech |
| Universal Profile | https://universalprofile.cloud |
| Execution Explorer | https://explorer.lukso.network |
| Consensus Explorer | https://explorer.consensus.mainnet.lukso.network |
| Validator Launchpad | https://deposit.mainnet.lukso.network |
| Testnet Faucet | https://faucet.testnet.lukso.network |
| Grid (mini-apps) | https://universal.page |
| Universal Swaps DEX | https://universalswaps.io |
| Relayer User API Docs | https://relayer-api.mainnet.lukso.network/docs#/ |
| Envio Playground | https://envio.lukso-mainnet.universal.tech/ |
| GitHub Org | https://github.com/lukso-network |

---

## 📜 LSP Standards Quick Reference

| LSP | Name | Key Purpose |
|-----|------|-------------|
| LSP0 | ERC725Account (Universal Profile) | Smart contract account |
| LSP1 | Universal Receiver | Hook for incoming assets/transfers |
| LSP2 | ERC725Y JSON Schema | Key-value store schema |
| LSP3 | Profile Metadata | Name, avatar, bio |
| LSP4 | Digital Asset Metadata | Token name, symbol, metadata |
| LSP5 | Received Assets | Track received tokens in UP |
| LSP6 | Key Manager | Permission/access control |
| LSP7 | Digital Asset | Fungible token (like ERC20) |
| LSP8 | Identifiable Digital Asset | NFT (like ERC721) |
| LSP9 | Vault | Sub-wallet / vault contract |
| LSP10 | Received Vaults | Track received vaults in UP |
| LSP11 | Basic Social Recovery | Social key recovery |
| LSP12 | Issued Assets | Track issued assets by creator |
| LSP14 | Ownable2Step | Secure 2-step ownership transfer |
| LSP15 | Transaction Relayer API | Gasless tx API spec |
| LSP16 | Universal Factory | CREATE2 cross-chain factory |
| LSP17 | Contract Extension | Extend contracts w/o upgrade |
| LSP20 | Call Verification | Verify calls via LSP6 |
| LSP23 | Linked Contracts Factory | Deploy UP+KM together |
| LSP25 | Execute Relay Call | Nonce management for relays |
| LSP26 | Follower System | On-chain social graph |
