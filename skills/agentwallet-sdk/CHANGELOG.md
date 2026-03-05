# Changelog

All notable changes to the Agent Wallet project are documented in this file.

## [1.0.0] — 2026-02-15

### Added
- **AgentAccountV2** — Core smart contract wallet with per-tx and period spend limits, operator permissions, pending tx queue, reentrancy guards, ERC-1271 signature validation
- **AgentAccountV2_4337** — ERC-4337 (Account Abstraction) variant with EntryPoint integration, `validateUserOp`, prefund validation (H2-2 fix)
- **AgentAccountFactoryV2** — CREATE2 factory for deterministic wallet deployment keyed by NFT (contract + tokenId)
- **AgentSwapRouter** — Swap aggregator router with 0.875% fee collection, whitelisted DEX targets, owner-adjustable fee (capped 2%)
- **A2APaymentProtocol** — Agent-to-agent payment protocol
- **AgentNexusEscrow** — On-chain escrow for agent payments
- **AgentNexusEntitlements** — ERC-1155 entitlement NFTs
- **AgentNexusCctpReceiver** — Circle CCTP cross-chain USDC receiver
- **@agentwallet/sdk** — TypeScript SDK (20 exports) with `createWallet`, `agentTransferToken`, `getBudgetForecast`, `getWalletHealth`, `batchAgentTransfer`, `getActivityHistory`
- **Operator epoch system** — All operator permissions auto-invalidate on NFT transfer (prevents flash-loan hijack + stale operators)
- **Exploit test suite** — 7 exploit-specific tests (flash-loan hijack, stale operators, 4337 nonce DoS, prefund validation, burned NFT, period boundary)
- **Invariant tests** — 6 invariant property tests
- **CI/CD** — 5 GitHub Actions workflows (CI, CodeQL, container security, secrets scan, security scan)
- **Landing page** — SDK marketing page at `agent-wallet-sdk/landing/`

### Security
- Internal audit V1 (2026-02-14) — `AUDIT_REPORT.md`
- Internal audit V2 (2026-02-15) — `AUDIT_REPORT_V2.md`
- Fixes: C2-1 (flash-loan NFT hijack), C2-2 (stale operators), H2-1 (pending queue brick), H2-2 (prefund validation), M2-1 (NFT burn protection), M2-2 (period boundary double-spend)

### Deployed Addresses
- **Base Mainnet** — AgentAccountFactoryV2: `0x700e9Af71731d707F919fa2B4455F27806D248A1`
- **Base Mainnet** — AgentNexusEscrow: `0x37A7B1f10b87f31ad916Fb3518118f8AA0d8d2fC`
- **Base Mainnet** — AgentNexusEntitlements: `0x3c8f32F9cF41Dc255129d6Add447218053743b33`
