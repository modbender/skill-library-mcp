# LUKSO Ecosystem Reference

> Last updated: February 2026  
> Sources: lukso.network, docs.lukso.tech, medium.com/lukso, community research

---

## Table of Contents
1. [Chain Basics](#chain-basics)
2. [Key Infrastructure](#key-infrastructure)
3. [Core Standards (LSPs)](#core-standards-lsps)
4. [Core Team](#core-team)
5. [Ecosystem Projects](#ecosystem-projects)
6. [Grants Program](#grants-program)
7. [Token Economics & Staking](#token-economics--staking)
8. [Community Channels](#community-channels)
9. [Ecosystem Stats](#ecosystem-stats)

---

## Chain Basics

| Setting | Value |
|---|---|
| **Network Name** | LUKSO |
| **Chain ID / Network ID** | `42` |
| **Genesis Fork Version** | `0x42000001` |
| **Currency Symbol** | `LYX` |
| **Consensus Mechanism** | Proof of Stake — Casper FFG + LMD-GHOST (Gasper) |
| **Block Time** | ~12 seconds (Ethereum-equivalent) |
| **EVM Compatibility** | Full — unmodified Ethereum protocol |
| **Gas Model** | EIP-1559 (base fee + tip), gasless UX via Relayer API |

**LUKSO is NOT a custom/modified chain** — it runs an identical Ethereum protocol stack (Casper + LMD-GHOST Gasper consensus, same EVM). The differentiator is the new LSP standard layer on top.

### What Makes LUKSO Different

- **Universal Profiles (UP)**: Smart contract-based accounts (ERC-725 Account / LSP0), replacing traditional EOA wallets. They are programmable, extensible, and hold metadata about the owner.
- **Gasless Transactions**: The Relayer API allows dApps to subsidize gas, so users interact without holding LYX.
- **LSP Standards**: LUKSO Standard Proposals — a layered set of standards for accounts, tokens, NFTs, notifications, access control, and more.
- **The Grid**: LUKSO's decentralized social feed / mini-dApp ecosystem embedded within Universal Profiles.

### Testnet

| Setting | Value |
|---|---|
| **Chain ID** | `4201` |
| **Currency Symbol** | `LYXt` |
| **RPC URL** | https://rpc.testnet.lukso.network |
| **Websocket RPC** | wss://ws-rpc.testnet.lukso.network |
| **Faucet** | https://faucet.testnet.lukso.network |
| **Block Explorer** | https://explorer.execution.testnet.lukso.network |
| **Consensus Explorer** | https://explorer.consensus.testnet.lukso.network |
| **Launchpad** | https://deposit.testnet.lukso.network |
| **Checkpoints** | https://checkpoints.testnet.lukso.network |

---

## Key Infrastructure

### Mainnet RPC Endpoints

| Provider | RPC URL | Notes |
|---|---|---|
| **Thirdweb** | https://42.rpc.thirdweb.com | Free, no key required (recommended default) |
| **SigmaCore** | https://rpc.lukso.sigmacore.io | Requires API key |
| **NowNodes** | https://lukso.nownodes.io | Requires API key |
| **Envio** | https://lukso.rpc.hypersync.xyz | Read-only, optimized |

### Block Explorers

| Explorer | URL | Type |
|---|---|---|
| **Blockscout** (Execution) | https://explorer.lukso.network | Main block explorer |
| **Execution Explorer** | https://explorer.execution.mainnet.lukso.network | Alternative URL |
| **Consensus Explorer** | https://explorer.consensus.mainnet.lukso.network | Beacon chain / validators |
| **Txs.app** | https://txs.app | Human-readable live transaction visualizer |
| **Stats** | https://stats.execution.mainnet.lukso.network | Network stats |
| **Client Diversity** | https://clientdiversity.lukso.network | Client distribution dashboard |

### Network Utilities

| Tool | URL |
|---|---|
| **Validator Launchpad** | https://deposit.mainnet.lukso.network |
| **Checkpoint Sync** | https://checkpoints.mainnet.lukso.network |
| **LYXe → LYX Migration Bridge** | https://migrate.lukso.network |
| **SAFE Multisig** | https://safe.mainnet.lukso.network |
| **Blockscout API** | https://explorer.execution.mainnet.lukso.network/api |

### IPFS

- **Dev gateway (rate limited, no SLA):** `https://api.universalprofile.cloud/ipfs`
- **Production recommended:** Use your own Pinata or Infura IPFS gateway
- LUKSO does NOT provide an official production IPFS upload gateway

### Indexer / GraphQL (Envio)

- **Endpoint:** `https://envio.lukso-mainnet.universal.tech/v1/graphql`
- Query Universal Profiles, LSP7/LSP8 Digital Assets
- Supports username → UP address resolution:
  ```bash
  curl -X POST -H "Content-Type: application/json" \
    -d '{"query": "query { Profile(where: {name: {_eq: \"USERNAME\"}}) { id name } }"}' \
    https://envio.lukso-mainnet.universal.tech/v1/graphql
  ```

### Developer Tools

| Tool | Description |
|---|---|
| **LUKSO CLI** | `curl https://install.lukso.network | sh` — node/validator setup |
| **LUKSO Wagyu Key Gen** | GUI tool for generating validator deposit keys |
| **LUKSO CLI Keygen** | CLI alternative for generating validator keys |
| **erc725.js** | `npm install @erc725/erc725.js` — fetch/encode UP metadata |
| **lsp-utils.js** | `npm install @lukso/lsp-utils` — high-level UP/token helpers |
| **@up-provider** | `npm install @lukso/up-provider` — mini-app Grid integration |
| **web3-onboard-config** | Universal Profile connector for Web3-Onboard |
| **ERC725 Inspector** | Browser tool to inspect UP metadata and permissions |
| **Authorize Controller** | Manage UP controller keys and permissions |

### Oracles & VRF

- **DIA Oracles** — Data feeds available for LUKSO (https://diadata.org)
- **Gateway VRF** — Verifiable Random Function by Gateway FM (https://gateway.fm)

---

## Core Standards (LSPs)

LUKSO Standard Proposals (LSPs) are the building blocks of the ecosystem:

| Standard | Name | Description |
|---|---|---|
| **LSP0** | ERC725 Account | Foundation of Universal Profiles; smart contract account combining ERC725X + ERC725Y + ERC1271 + LSP1 + LSP14 + LSP17 + LSP20 |
| **LSP1** | Universal Receiver | Notification system — account gets notified on incoming tokens/follows/events |
| **LSP2** | ERC725Y JSON Schema | Structured key-value metadata storage encoding |
| **LSP3** | Profile Metadata | Standard for profile info (name, avatar, description, links) |
| **LSP4** | Digital Asset Metadata | Metadata standard for tokens and NFTs |
| **LSP6** | Key Manager | Access control — manage permissions for controllers (sub-keys, dApps, etc.) |
| **LSP7** | Digital Asset (Fungible) | Improved fungible token standard (replaces ERC-20) |
| **LSP8** | Identifiable Digital Asset | NFT 2.0 standard (replaces ERC-721) — extensible metadata |
| **LSP14** | Ownable2Step | Secure 2-step ownership transfer |
| **LSP17** | Contract Extension | Extend contracts with new functionality post-deployment |
| **LSP20** | Call Verification | Unified access pattern for Universal Profiles |
| **LSP25** | Execute Relay Call | Meta-transactions / gasless execution |
| **LSP26** | Follower System | On-chain social graph — follow/unfollow Universal Profiles |
| **ERC725** | Foundation | ERC725X (executor) + ERC725Y (key-value store) — foundation of all LSPs |

All LSP specs are open source: https://github.com/lukso-network/LIPs

---

## Core Team

### Fabian Vogelsteller — Co-Founder & Chief Architect

- **Background:** Joined Ethereum Foundation in 2015; built core Ethereum ecosystem 2015–2018
- **Key contributions:**
  - Proposed **ERC-20** (2015) — the token standard that enabled all DeFi
  - Created **web3.js** — Ethereum's most widely used JavaScript library
  - Built the first official **Ethereum Wallet** and the first decentralized web3 browser
  - Created **ERC-725** — blockchain identity standard, foundation of Universal Profiles
- **Founded LUKSO:** 2017 (launched mainnet May 2023)
- **Twitter/X:** @feindura
- **Vision:** Blockchain for social, culture, and creative industries; re-imagined digital identity

### Marjorie Hernandez — Co-Founder & CEO

- **Background:** Architect by training; visionary in design, tech, and blockchain
- **Key contributions:**
  - Co-founded **The Dematerialised** — first web3 digital fashion marketplace
  - Drives LUKSO's creative industry strategy and ecosystem growth
  - Featured in Vogue Business, Bloomberg, Wired, Forbes
- **Focus:** Building lifestyle ecosystems; empowering brands and creatives
- **LUKSO Founded:** 2017 with Fabian

### Foundation for the New Creative Economies (FNCΞ)

- Swiss foundation based in Zug
- Independent organization supporting the LUKSO ecosystem
- Has a restriction clause: cannot stake more than 30% of total LYX staked on network
- Has a Freeze Smart Contract mechanism: if LYX market cap exceeds 2B EUR mean over 6 months, 70% of Foundation LYX gets frozen over 5 years (deflationary mechanism)

### LUKSO Blockchain GmbH (LBG)

- German company (Berlin-based)
- Organized the rICO (Reversible ICO) in 2020
- Responsible for LYXe migration, private sale distributions, future development funding
- Received 30.5M LYX at genesis for obligations (migration, sales, grants, development)

---

## Ecosystem Projects

### 🔵 Core / Official

#### Universal Everything (universaleverything.io)
- **Category:** Profile browser / social explorer
- **Description:** The main social profile browser for LUKSO. Browse Universal Profiles, explore assets, discover creators. Also hosts **The Grid** — a drag-and-drop mini-dApp system embedded in profiles. Users can arrange widgets (swap, portfolio, feeds) on their profile page.
- **URL:** https://universaleverything.io
- **The Grid:** Profiles have customizable "Grid" spaces where mini-dApps (called Grid apps) can be embedded
- **Key to ecosystem:** This is effectively the "homepage" of LUKSO social experience

#### The Dematerialised (thedematerialised.com)
- **Category:** Digital fashion / phygital marketplace
- **Description:** First web3 digital fashion marketplace. Co-founded by LUKSO co-founder Marjorie Hernandez. Brands can create and sell digital fashion items as NFTs, supporting phygital (physical + digital) ownership. Built on LUKSO using LSP standards.
- **Connection to LUKSO:** Deep — co-founder overlap; demonstrates fashion industry use case

#### CommonGround (app.cg)
- **Category:** Community platform / social
- **Description:** Decentralized community platform integrated with LUKSO Universal Profiles. Enables community spaces, DAO governance, and social coordination. Listed in LUKSO's official documentation as a community platform.
- **URL:** https://app.cg

### 🟢 DeFi / Finance

#### Universal Swaps (universalswaps.io)
- **Category:** DEX (Decentralized Exchange)
- **Description:** The primary DEX on LUKSO. Enables token swaps between LYX and LSP7 tokens. Supports the LUKSO native token ecosystem and provides liquidity for ecosystem projects.
- **URL:** https://universalswaps.io
- **Note:** Key infrastructure for LSP7 token trading; integrates with Universal Profiles

#### Stakingverse (stakingverse.io)
- **Category:** Liquid staking / staking services
- **Description:** Staking platform for LUKSO. Provides liquid staking solutions enabling LYX holders to stake without running their own validator node, receiving liquid staking tokens in return. Also provides educational resources and community guides (docs.luksoverse.io).
- **URL:** https://stakingverse.io
- **Community docs:** https://docs.luksoverse.io — comprehensive community node guides
- **Note:** Key resource for the LUKSO staking community; maintains LUKSO Node Guide

### 🟡 NFTs / Digital Assets

#### Forever Moments
- **Category:** NFT / digital memories platform
- **Description:** Platform for minting and trading "moments" as NFTs on LUKSO. Focuses on the idea of preserving significant life moments as verifiable digital assets, leveraging LSP8 NFT 2.0 standard with extensible metadata.

#### Universal Page (universal.page)
- **Category:** NFT marketplace / profile management
- **Description:** Marketplace and tools for Universal Profiles and digital assets on LUKSO. Allows profile customization, NFT display, and asset management.

### 🔧 Infrastructure / Dev Tools

#### Envio
- **Category:** Blockchain indexer
- **Description:** GraphQL indexer for LUKSO. Query Universal Profile data, LSP7 tokens, LSP8 NFTs in structured GraphQL queries. Free tier available; may become paid service.
- **Docs:** https://docs.envio.dev/blog/envio-data-indexing-supports-developers-building-on-lukso
- **Endpoint:** https://envio.lukso-mainnet.universal.tech/v1/graphql

#### Dappnode
- **Category:** Node infrastructure hardware/software
- **Description:** Hardware and software solution for running LUKSO validators easily. LUKSO has an official partnership with Dappnode. One of the easiest ways to run a node — difficulty rated Easy 🌶️.
- **Docs:** https://docs.dappnode.io/docs/user/staking/lukso/solo
- **Announcement:** Partnership announced 2023

#### DIA Oracles
- **Category:** Oracle / price feeds
- **Description:** Provides decentralized data feeds for LUKSO. Partners with LUKSO for on-chain price oracle data.
- **URL:** https://diadata.org

#### Gateway FM (VRF)
- **Category:** Verifiable Random Function
- **Description:** Provides VRF (Verifiable Random Function) for LUKSO, enabling provably fair randomness for games, lotteries, and NFT reveals.
- **URL:** https://gateway.fm

#### Txs.app
- **Category:** Transaction visualizer
- **Description:** Live transaction visualizer for the LUKSO network. Decodes and displays transactions in a human-readable format, great for monitoring network activity.

#### Luksoverse / Community Guides
- **Category:** Community documentation
- **Description:** Community-maintained comprehensive node guide and documentation.
- **URL:** https://docs.luksoverse.io

### 🎨 Creative / Art

#### Refraction (Refraction x LUKSO Grants)
- **Category:** Digital art / phygital
- **Description:** Partner in LUKSO's grants program (Jan–Mar 2025). A program for artists exploring digital and phygital art, pushing boundaries of abstraction and storytelling.

### 📡 Ecosystem Tools Referenced in Docs

| Project | Category | Notes |
|---|---|---|
| **ERC725 Alliance** | Standards body | Maintains ERC-725 standard; erc725alliance.org |
| **Fractal ID** | Identity / KYC | Early LUKSO supporter; identity verification |
| **SAFE Multisig** | Treasury management | Deployed for Foundation treasury on LUKSO mainnet |

---

## Grants Program

### Overview

LUKSO's developer grants program is run by LUKSO Blockchain GmbH / Foundation for the New Creative Economies (FNCΞ). It supports projects building on LUKSO with:
- Technical development support
- Community & marketing engagement
- Access to resources & partner benefits
- Access to co-working spaces in Berlin

**Apply at:** https://lukso.network/developer-grants

### Grant Waves

| Wave | Period | Description |
|---|---|---|
| **Wave 1 – Open Grants** | May–July 2024 | First major grants round; infrastructure, dev tools, dApps, educational initiatives |
| **LUKSO Community Grants** | September 2024 | Quadratic funding via Gitcoin; community decides fund allocation |
| **Refraction x LUKSO** | January–March 2025 | Artists program; digital and phygital art, abstraction and storytelling |
| **Wave 2 – Hack The Grid** | February–June 2025 | Fast-paced hackathon-style program for mini-dApps on The Grid; in partnership with Gitcoin |

### Eligibility Requirements

**Good fit:**
- Projects that meaningfully integrate LSPs (LUKSO Standard Proposals) and Universal Profiles
- Innovative dApps, infrastructure, developer tools, educational initiatives
- Multi-chain strategies are OK if LUKSO integration is meaningful
- Open source preferred but not required

**Not eligible:**
- Projects not meaningfully using Universal Profiles or LSP standards
- Pure repurposing of existing ERC-20/ERC-721 standards without LSP integration

### Application Process

1. Fill out the application form
2. Application reviewed by grant committee (allow ~4 weeks after wave closes)
3. If advanced → interview stage
4. Grant committee deliberates → final decision
5. Upon approval: KYC required for project owner (via third-party provider)
6. Sign grant agreement

### Evaluation Criteria

1. **Technical Excellence** — Implementation quality of LSPs, tools, Universal Profiles
2. **Use Case** — Usefulness, scalability, market potential
3. **User Experience** — UI ease and intuitiveness
4. **Strategy** — Go-to-market, user adoption, marketing
5. **Ecosystem Fit** — Alignment with LUKSO ecosystem
6. **Milestones & Deliverables** — Roadmap clarity and feasibility
7. **Team Expertise** — Technical + strategic skills, motivation

**Note:** Applications cannot be modified after submission. KYC is mandatory post-approval.

### Community Grants via Gitcoin

LUKSO has partnered with **Gitcoin** for quadratic funding rounds, allowing the community to vote on grant distribution. This enables non-technical and grassroots projects to receive funding alongside technical projects.

---

## Token Economics & Staking

### LYX Token

| Property | Value |
|---|---|
| **Total Supply** | 42,000,000 LYX (chosen by Genesis Validators) |
| **Token on Ethereum** | LYXe (ERC-20, Ethereum Mainnet) |
| **Native chain token** | LYX (LUKSO Mainnet) |
| **Migration bridge** | https://migrate.lukso.network (LYXe → LYX) |
| **Minimum bridge amount** | 1 LYXe |
| **Migration duration open** | ~4 years from launch (July 2023 launch) |

### Token History

- **LYXe** was created as an ERC-20 on Ethereum for the rICO (Reversible ICO) in 2020
- **Mainnet launched May 23, 2023** with 42M LYX initial supply
- Genesis Validators voted on supply (options: 35M, 42M, or higher)
- LYXe migration bridge opened **July 4, 2023**
- LYXe in the Genesis Deposit Contract is **permanently locked** (≈330,752 LYXe) — a historical artifact

### Initial LYX Distribution (at Genesis)

| Recipient | Purpose | Amount |
|---|---|---|
| LUKSO Blockchain GmbH (LBG) | LYXe migration + sales + development | ~30.5M LYX |
| Foundation for the New Creative Economies (FNCΞ) | Ecosystem support | ~11.5M LYX |
| Genesis Validators | Staked at network start | ~10,336 × 32 LYX |

**LBG allocation breakdown:**
- LYXe migration pool: 15,245,164 LYX
- Seed Sale: 4,695,000 LYX
- Private Sale #1: 5,089,264 LYX
- Private Sale #2: 2,049,802 LYX
- Advisors: 1,240,000 LYX
- Initial Grants: 206,500 LYX
- Future development: 2,000,000 LYX

### Foundation Tokenomics Safeguards

- FNCΞ cannot hold more than **30% of total staked LYX** (anti-centralization clause)
- **Freeze Smart Contract**: If LYX market cap >2B EUR mean over 6 months → 70% of Foundation LYX gets frozen over 5 years (deflationary)
- Foundation can withdraw max 10% of frozen contract every 3 months (safety valve)

### Staking / Validators

| Parameter | Value |
|---|---|
| **Minimum per validator key** | 32 LYX |
| **Maximum per validator key** | 2048 LYX (after Pectra fork) |
| **Active validators (Feb 2026)** | ~155,000 |
| **Genesis Validators** | 10,336 (launched network on May 23, 2023) |
| **Avg genesis participation rate** | ~98.5% |
| **Withdrawal credentials** | 0x00 (no withdrawal), 0x01 (ETH1 address), 0x02 (post-Pectra) |
| **Shapella fork** | Executed; automatic reward withdrawals enabled June 28, 2023 |
| **Pectra fork** | Raised max effective balance to 2048 LYX; simplified multi-key management |

### Hardware Requirements (Running a Node)

| Spec | Value |
|---|---|
| **OS** | Linux or macOS |
| **CPU cores** | 4+ |
| **RAM** | 16 GB |
| **SSD (NVMe)** | 100 GB |

### Supported Clients

**Execution:** Geth, Erigon, Besu, Nethermind  
**Consensus:** Prysm, Lighthouse, Teku, Nimbus

### How to Stake

1. **Easy (Dappnode):** Hardware node with Dappnode OS — guided UI setup
2. **Medium (LUKSO CLI):** `curl https://install.lukso.network | sh` → `lukso init` → `lukso install` → `lukso start --validator`
3. **Advanced (Docker):** Custom Docker compose setup
4. **No-node options:** Liquid staking via Stakingverse.io (coming online)

**Deposit Launchpad:** https://deposit.mainnet.lukso.network  
**Key generation tools:** LUKSO Wagyu (GUI) or LUKSO Keygen CLI

### Staking Rewards

- APY displayed on Deposit Launchpad (fluctuates with validator count and network usage)
- Rewards = consensus layer rewards + execution layer tips/MEV
- Penalties for being offline (inactivity leak, proportional to downtime squared)
- Slashing for double-signing (rare)
- No lock-up after Shapella fork; exit process takes several hours

---

## Community Channels

| Platform | URL / Handle | Notes |
|---|---|---|
| **Discord** | https://discord.com/invite/lukso | Official, main developer + community hub |
| **Twitter / X** | https://twitter.com/lukso_io (@lukso_io) | Official announcements |
| **YouTube** | LUKSO YouTube channel | Tech talks, Fabian's Tech Time series |
| **Medium** | https://medium.com/lukso | Official blog — ecosystem updates, announcements |
| **GitHub** | https://github.com/lukso-network | All open source code, LSP specs |
| **CommonGround** | https://app.cg | LUKSO community on their own platform |
| **Forum** | Linked from docs | Developer Q&A forum |
| **StackOverflow** | Tagged [lukso] | Developer technical questions |

### Key Twitter Handles

| Account | Description |
|---|---|
| **@lukso_io** | Official LUKSO |
| **@feindura** | Fabian Vogelsteller (co-founder) |
| **@marjoriehernandez** | Marjorie Hernandez (co-founder) |

### Luksoverse Community

- **Community node guide:** https://docs.luksoverse.io
- Maintained by community members; comprehensive validator setup guides
- Also provides Grafana monitoring templates, explorer automation scripts

---

## Ecosystem Stats

*As of early 2026 (from lukso.network homepage):*

| Metric | Value |
|---|---|
| **Universal Profiles created** | 36,000+ |
| **Total LYX Supply** | 42,000,000 |
| **Active Validators** | 155,000+ |
| **Chain ID** | 42 |
| **Genesis Validators** | 10,336 |
| **Genesis Participation Rate** | ~98.5% |

### Key Milestones

| Date | Milestone |
|---|---|
| **2017** | LUKSO founded by Fabian Vogelsteller & Marjorie Hernandez |
| **2020** | LUKSO Whitepaper released |
| **2020** | Reversible ICO (rICO) conducted on Ethereum |
| **2021** | L14 Testnet launched |
| **2022** | L15 Testnet (PoS integration) |
| **Apr 20, 2023** | Genesis Validator Deposit Contract launched on Ethereum |
| **May 23, 2023** | **LUKSO Mainnet launched** — 10,336 Genesis Validators |
| **Jun 23, 2023** | Discovery month ended |
| **Jun 28, 2023** | Shapella fork — automatic staking withdrawals enabled |
| **Jul 4, 2023** | LYXe → LYX migration bridge opened |
| **Sep 2023** | Dappnode partnership announced |
| **2024** | The Grid launched on Universal Everything |
| **May–Jul 2024** | Wave 1 Open Grants |
| **Sep 2024** | Community Grants (Gitcoin quadratic funding) |
| **Jan–Mar 2025** | Refraction x LUKSO Grants |
| **Feb–Jun 2025** | Wave 2 — Hack The Grid (Gitcoin partnership) |

---

## Notable Links Quick Reference

```
MAINNET RPC:     https://42.rpc.thirdweb.com
BLOCK EXPLORER:  https://explorer.lukso.network
CONSENSUS:       https://explorer.consensus.mainnet.lukso.network
LAUNCHPAD:       https://deposit.mainnet.lukso.network
CHECKPOINTS:     https://checkpoints.mainnet.lukso.network
MIGRATION:       https://migrate.lukso.network
TESTNET RPC:     https://rpc.testnet.lukso.network
TESTNET FAUCET:  https://faucet.testnet.lukso.network
DOCS:            https://docs.lukso.tech
IPFS (dev):      https://api.universalprofile.cloud/ipfs
GRAPHQL:         https://envio.lukso-mainnet.universal.tech/v1/graphql
DISCORD:         https://discord.com/invite/lukso
GITHUB:          https://github.com/lukso-network
GRANTS:          https://lukso.network/developer-grants
UP BROWSER:      https://universaleverything.io
DEX:             https://universalswaps.io
STAKING:         https://stakingverse.io
TWITTER:         https://twitter.com/lukso_io
MEDIUM:          https://medium.com/lukso
```

---

## LSP Standards Reference (Quick Look-up)

| LSP | Replaces / Analogous to | Key Feature |
|---|---|---|
| LSP0 (ERC725Account) | EOA wallet | Smart contract account = Universal Profile |
| LSP1 (Universal Receiver) | N/A | On-chain notifications/hooks |
| LSP2 (ERC725Y JSON Schema) | N/A | Structured metadata encoding |
| LSP3 (Profile Metadata) | N/A | name, avatar, bio, links on-chain |
| LSP4 (Digital Asset Metadata) | ERC-721 tokenURI | Richer token/NFT metadata |
| LSP6 (Key Manager) | Multisig | Granular permissions for controllers |
| LSP7 (Digital Asset) | ERC-20 | Fungible tokens with notifications |
| LSP8 (Identifiable Digital Asset) | ERC-721 | NFT 2.0 with extensible metadata |
| LSP17 (Contract Extension) | Upgrade patterns | Post-deploy extensibility |
| LSP25 (Execute Relay Call) | Meta-tx / EIP-2771 | Gasless execution / relayer |
| LSP26 (Follower System) | Social graph | On-chain follow/unfollow |

---

*Reference file for the LUKSO Expert skill. Cross-reference with: `lsp-standards.md`, `universal-profiles.md`, `dev-cookbook.md`*
