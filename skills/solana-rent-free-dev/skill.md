---
name: solana-rent-free-dev
description: >
  Build Solana applications 200x cheaper for stablecoin payments, agent
  payments, DeFi, airdrops, token distribution, and ZK applications using Light
  Protocol's rent-free token accounts, mint accounts, and PDAs. Covers client
  development (TypeScript, Rust) and program development (Rust) across Anchor,
  native Rust, and Pinocchio.
compatibility: |
  Requires ZK Compression CLI, Solana CLI, Anchor CLI, and Node.js.
metadata:
  mintlify-proj: lightprotocol
  openclaw:
    requires:
      env: []
      bins: ["node", "solana", "anchor", "cargo", "light"]
allowed-tools:
  - Read
  - Glob
  - Grep
  - Task
  - WebFetch(https://zkcompression.com/*)
  - WebFetch(https://github.com/Lightprotocol/*)
  - WebSearch
  - mcp__zkcompression__SearchLightProtocol
  - mcp__deepwiki__ask_question
---

## Capabilities

Light Token allows agents to build scalable Solana applications with rent-free token and mint accounts and PDA's.

| Primitive        | Use case                                                                                                                                                                                               | Constraints                                                                    |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------ |
| Light Token      | Most token use cases (launchpads, DeFi, payments). Rent-free mint and token accounts. \~200x cheaper than SPL and more compute-unit efficient on the hot path.                                         | Currently in Beta and on Solana Devnet with mainnet in Q1 2026                 |
| Light-PDA        | DeFi program state such as AMM pools and vaults. \~98% cheaper than PDAs and can be implemented with minimal code changes.                                                                             | Currently in Beta and on Solana Devnet with mainnet in Q1 2026                 |
| Compressed Token | Only for Airdrops and token distribution. Prefer Light Token for other purposes. Used by Light Token under the hood for rent-free storage of inactive Light Tokens. Supported by Phantom and Backpack. | Do not use for general-purpose token features. Use Light Token instead.        |
| Compressed PDA   | User state and app state, nullifiers (payments and ZK applications), DePIN nodes, and stake accounts. Similar to program-derived addresses without a rent-exempt balance.                              | Not for shared state, pool accounts, or config accounts. Use Light-PDA instead |

Comparing creation cost and CU usage:

|                          |     Light-Token |  SPL-Token |
| :----------------------- | --------------: | ---------: |
| **Mint Account**         | **0.00001 SOL** | 0.0015 SOL |
| **Token Account**        | **0.00001 SOL** |  0.002 SOL |
| **Associated token account creation** |    **4,348 CU** |  14,194 CU |
| **Transfer**             |      **312 CU** |   4,645 CU |
| **Transfer** (rent-free) |    **1,885 CU** |   4,645 CU |

Install this reference skill:

```bash theme={null}
npx skills add Lightprotocol/skills
```

## Security

This skill does not pull, store, or transmit external secrets. It provides code patterns, documentation references, and development guidance only.

- **No credentials consumed.** The skill requires no API keys, private keys, or signing secrets. `env: []` is declared explicitly.
- **User-provided configuration.** RPC endpoints, wallet keypairs, and authentication tokens (Privy, wallet adapters) are configured in the user's own application code — the skill only demonstrates how to use them.
- **Install source.** `npx skills add Lightprotocol/skills` installs from the public GitHub repository ([Lightprotocol/skills](https://github.com/Lightprotocol/skills)). Verify the source before running.
- **Audited protocol.** Light Protocol smart contracts are independently audited. Reports are published at [github.com/Lightprotocol/light-protocol/tree/main/audits](https://github.com/Lightprotocol/light-protocol/tree/main/audits).

## Workflow

1. **Clarify intent**
   * Recommend plan mode, if it's not activated
   * Use `AskUserQuestion` to resolve blind spots
   * All questions must be resolved before execution
2. **Identify references and skills**
   * Match task to available [skills](#defi) below
   * Locate relevant [documentation and examples](#documentation-and-examples)
3. **Write plan file** (YAML task format)
   * Use `AskUserQuestion` for anything unclear — never guess or assume
   * Identify blockers: permissions, dependencies, unknowns
   * Plan must be complete before execution begins
4. **Execute**
   * Use `Task` tool with subagents for parallel research
   * Subagents load skills via `Skill` tool
   * Track progress with `TodoWrite`
5. **When stuck**: spawn subagent with `Read`, `Glob`, `Grep`, DeepWiki MCP access and load `skills/ask-mcp`

## Skills

| Use case                                                                                                                                                                                              | Skill                                                                                                 |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Build rent-free Solana programs with Light SDK (Anchor or Pinocchio). Includes router integration.                                                                                                    | [light-sdk](https://github.com/Lightprotocol/skills/tree/main/skills/light-sdk)                       |
| Use Light Token client SDKs (TypeScript and Rust) for mints, associated token accounts, transfers                                                                                                                         | [light-token-client](https://github.com/Lightprotocol/skills/tree/main/skills/light-token-client)     |
| Stream account state via Laserstream gRPC                                                                                                                                                             | [data-streaming](https://github.com/Lightprotocol/skills/tree/main/skills/data-streaming)             |
| Build payment flows and wallet integrations with light-token. Covers receive/send/balance/history, client-side signing patterns for Privy and Solana wallet adapters, and nullifier-based double-spend prevention. | [payments-and-wallets](https://github.com/Lightprotocol/skills/tree/main/skills/payments-and-wallets) |
| Airdrops, DePIN, token distribution                                                                                                                                                                   | [token-distribution](https://github.com/Lightprotocol/skills/tree/main/skills/token-distribution)     |
| Anti-double-spend nullifiers for Privacy-preserving ZK programs                                                                                                                                       | [zk-nullifier](https://github.com/Lightprotocol/skills/tree/main/skills/zk-nullifier)                 |
| Testing programs and clients on localnet, devnet, mainnet                                                                                                                                             | [testing](https://github.com/Lightprotocol/skills/tree/main/skills/testing)                           |
| Help with Debugging and Questions via DeepWiki MCP                                                                                                                                                    | [ask-mcp](https://github.com/Lightprotocol/skills/tree/main/skills/ask-mcp)                           |

Skills for compressed PDAs and more are in development.

### Install to Claude Code

Add the marketplace and install:

```
/plugin marketplace add Lightprotocol/skills
/plugin install solana-rent-free-dev
```

All skills are included. Use them by name (`/light-sdk`, `/token-distribution`, `/testing`, etc.) or let Claude invoke them based on task context.

### Install to Cursor

1. Open Settings (**Cmd+Shift+J** / **Ctrl+Shift+J**)
2. Navigate to **Rules & Commands** → **Project Rules** → **Add Rule** → **Remote Rule (GitHub)**
3. Enter: `https://github.com/Lightprotocol/skills.git`

Skills are auto-discovered based on context. Ask about light-token, defi, payments, or program migration and the agent uses the relevant skill automatically.

### Install to Any Agent

```
npx skills add Lightprotocol/skills
```

## Context

### light-token

A token standard functionally equivalent to SPL that stores mint and token accounts more efficiently.

**Mint accounts** represent a unique mint and optionally store token-metadata. Functionally equivalent to SPL mints.

**Token accounts** hold balances from any light, SPL, or Token-2022 mint, without paying rent-exemption.

The token program pays rent-exemption cost for you. When an account has no remaining sponsored rent, the account is automatically compressed. Your tokens are cryptographically preserved as a compressed token account (rent-free). The account is loaded into hot account state in-flight when someone interacts with it again.

Use for: Launchpads, DeFi, token transfers, payments, ... .

### light-PDA

The Light-SDK pays rent-exemption for your PDAs, token accounts, and mints (98% cost savings). Your program logic stays the same.

After extended inactivity (multiple epochs without writes), accounts auto-compress to cold state. Your program only interacts with hot accounts. Clients load cold accounts back on-chain via `create_load_instructions`.

| Area            | Change                                                          |
| --------------- | --------------------------------------------------------------- |
| State struct    | Derive `LightAccount`, add `compression_info: CompressionInfo`  |
| Accounts struct | Derive `LightAccounts`, add `#[light_account]` on init accounts |
| Program module  | Add `#[light_program]` above `#[program]`                       |
| Instructions    | No changes                                                      |

Use for: DeFi program state, AMM pools, vaults.

### Compressed token (Only use for Token Distribution)

Compressed token accounts store token balance, owner, and other information of tokens like SPL and light-tokens. Compressed token accounts are rent-free. Any light-token or SPL token can be compressed/decompressed at will. Supported by Phantom and Backpack.

Only Use for: airdrops, token distribution without paying upfront rent per recipient.

### Compressed PDA

Compressed PDAs are derived using a specific program address and seed, like regular PDAs. Custom programs invoke the Light System program to create and update accounts, instead of the System program.

Persistent unique identification. Program ownership. CPI between compressed and regular PDAs.

Use rent-free PDAs for: user state, app state, nullifiers for payments, DePIN node accounts, stake accounts, nullifiers for zk applications. Not for shared state, pool, and config accounts.

### Guidelines

* **light-token ≠ compressed token.** light-token is a Solana account in hot state. Compressed token is a compressed account, always compressed, rent-free.
* **light-PDA ≠ compressed PDA.** light-PDA is a Solana PDA that transitions to compressed state when inactive. Compressed PDA is always compressed, derived like a PDA and requires a validity proof.
* **light-token accounts hold SPL and Token-2022 balances**, not just light-mint balances.
* When sponsored rent on a light-token or light-PDA runs out, the account compresses. It decompresses on next interaction.

### Documentation and Examples

#### TypeScript Client (`@lightprotocol/compressed-token`)

| Operation             | Docs guide                                                                              | GitHub example                                                                                                                                                                                                                                                   |
| --------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `createMintInterface` | [create-mint](https://zkcompression.com/light-token/cookbook/create-mint)               | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/create-mint.ts)                                                                                                                                               |
| `createAtaInterface`  | [create-ata](https://zkcompression.com/light-token/cookbook/create-ata)                 | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/create-ata.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/create-ata.ts)                 |
| `mintToInterface`     | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to)                       | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/mint-to.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/mint-to.ts)                       |
| `transferInterface`   | [transfer-interface](https://zkcompression.com/light-token/cookbook/transfer-interface) | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/transfer-interface.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/transfer-interface.ts) |
| `approve`             | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)         | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/delegate-approve.ts)                                                                                                                                          |
| `revoke`              | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)         | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/delegate-revoke.ts)                                                                                                                                           |
| `wrap`                | [wrap-unwrap](https://zkcompression.com/light-token/cookbook/wrap-unwrap)               | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/wrap.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/wrap.ts)                             |
| `unwrap`              | [wrap-unwrap](https://zkcompression.com/light-token/cookbook/wrap-unwrap)               | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/unwrap.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/unwrap.ts)                         |
| `loadAta`             | [load-ata](https://zkcompression.com/light-token/cookbook/load-ata)                     | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/actions/load-ata.ts) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/typescript-client/instructions/load-ata.ts)                     |

#### Rust Client (`light_token_client`)

| Operation            | Docs guide                                                                                  | GitHub example                                                                                                                                                                                                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `CreateMint`         | [create-mint](https://zkcompression.com/light-token/cookbook/create-mint)                   | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/create_mint.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_mint.rs)                                         |
| `CreateAta`          | [create-ata](https://zkcompression.com/light-token/cookbook/create-ata)                     | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/create_associated_token_account.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_associated_token_account.rs) |
| `CreateTokenAccount` | [create-token-account](https://zkcompression.com/light-token/cookbook/create-token-account) | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/create_token_account.rs)                                                                                                                                                |
| `MintTo`             | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to)                           | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/mint_to.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/mint_to.rs)                                                 |
| `TransferInterface`  | [transfer-interface](https://zkcompression.com/light-token/cookbook/transfer-interface)     | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/transfer_interface.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/transfer_interface.rs)                           |
| `TransferChecked`    | [transfer-checked](https://zkcompression.com/light-token/cookbook/transfer-checked)         | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/transfer_checked.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/transfer_checked.rs)                               |
| `Approve`            | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)             | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/approve.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/approve.rs)                                                 |
| `Revoke`             | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)             | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/revoke.rs) \| [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/revoke.rs)                                                   |
| `Burn`               | [burn](https://zkcompression.com/light-token/cookbook/burn)                                 | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/burn.rs)                                                                                                                                                                |
| `BurnChecked`        | [burn](https://zkcompression.com/light-token/cookbook/burn)                                 | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/burn_checked.rs)                                                                                                                                                        |
| `Freeze`             | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw)                   | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/freeze.rs)                                                                                                                                                              |
| `Thaw`               | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw)                   | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/thaw.rs)                                                                                                                                                                |
| `Close`              | [close-token-account](https://zkcompression.com/light-token/cookbook/close-token-account)   | [instruction](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/close.rs)                                                                                                                                                               |
| `Wrap`               | [wrap-unwrap](https://zkcompression.com/light-token/cookbook/wrap-unwrap)                   | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/wrap.rs)                                                                                                                                                                          |
| `Unwrap`             | [wrap-unwrap](https://zkcompression.com/light-token/cookbook/wrap-unwrap)                   | [action](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/actions/unwrap.rs)                                                                                                                                                                        |
| `SplToLight`         | —                                                                                           | [example](https://github.com/Lightprotocol/examples-light-token/blob/main/rust-client/instructions/spl_to_light_transfer.rs)                                                                                                                                                   |

#### Program (`light_token`)

##### Examples

|                                                                                                                            | Description                                                            |
| -------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| [cp-swap-reference](https://github.com/Lightprotocol/cp-swap-reference)                                                    | Fork of Raydium AMM that creates markets without paying rent-exemption |
| [create-and-transfer](https://github.com/Lightprotocol/examples-light-token/tree/main/programs/anchor/create-and-transfer) | Create account via macro and transfer via CPI                          |
| [pinocchio-swap](https://github.com/Lightprotocol/examples-light-token/tree/main/pinocchio/swap)                           | Light Token swap reference implementation                              |

##### Macros

|                                                                                                                                           | Description                              |
| ----------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| [counter](https://github.com/Lightprotocol/examples-light-token/tree/main/programs/anchor/basic-macros/counter)                           | Create PDA with sponsored rent-exemption |
| [create-ata](https://github.com/Lightprotocol/examples-light-token/tree/main/programs/anchor/basic-macros/create-ata)                     | Create associated light-token account    |
| [create-mint](https://github.com/Lightprotocol/examples-light-token/tree/main/programs/anchor/basic-macros/create-mint)                   | Create light-token mint                  |
| [create-token-account](https://github.com/Lightprotocol/examples-light-token/tree/main/programs/anchor/basic-macros/create-token-account) | Create light-token account               |

##### CPI Instructions

CPI calls can be combined with existing and/or light macros. The API is a superset of SPL-token.

| Operation                    | Docs guide                                                                                  | GitHub example                                                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `CreateAssociatedAccountCpi` | [create-ata](https://zkcompression.com/light-token/cookbook/create-ata)                     | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/create-ata/src/lib.rs)           |
| `CreateTokenAccountCpi`      | [create-token-account](https://zkcompression.com/light-token/cookbook/create-token-account) | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/create-token-account/src/lib.rs) |
| `CreateMintCpi`              | [create-mint](https://zkcompression.com/light-token/cookbook/create-mint)                   | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/create-mint/src/lib.rs)          |
| `MintToCpi`                  | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to)                           | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/mint-to/src/lib.rs)              |
| `MintToCheckedCpi`           | [mint-to](https://zkcompression.com/light-token/cookbook/mint-to)                           | [src](https://github.com/Lightprotocol/examples-light-token/tree/main/program-examples/anchor/basic-instructions/mint-to-checked)         |
| `BurnCpi`                    | [burn](https://zkcompression.com/light-token/cookbook/burn)                                 | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/burn/src/lib.rs)                 |
| `TransferCheckedCpi`         | [transfer-checked](https://zkcompression.com/light-token/cookbook/transfer-checked)         | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/transfer-checked/src/lib.rs)     |
| `TransferInterfaceCpi`       | [transfer-interface](https://zkcompression.com/light-token/cookbook/transfer-interface)     | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/transfer-interface/src/lib.rs)   |
| `ApproveCpi`                 | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)             | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/approve/src/lib.rs)              |
| `RevokeCpi`                  | [approve-revoke](https://zkcompression.com/light-token/cookbook/approve-revoke)             | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/revoke/src/lib.rs)               |
| `FreezeCpi`                  | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw)                   | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/freeze/src/lib.rs)               |
| `ThawCpi`                    | [freeze-thaw](https://zkcompression.com/light-token/cookbook/freeze-thaw)                   | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/thaw/src/lib.rs)                 |
| `CloseAccountCpi`            | [close-token-account](https://zkcompression.com/light-token/cookbook/close-token-account)   | [src](https://github.com/Lightprotocol/examples-light-token/blob/main/programs/anchor/basic-instructions/close/src/lib.rs)                |

## General References

### TypeScript SDK

| Package                           | npm                                                                  |
| --------------------------------- | -------------------------------------------------------------------- |
| `@lightprotocol/stateless.js`     | [npm](https://www.npmjs.com/package/@lightprotocol/stateless.js)     |
| `@lightprotocol/compressed-token` | [npm](https://www.npmjs.com/package/@lightprotocol/compressed-token) |

### Rust Crates and SDK

| Crate                        | docs.rs                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------- |
| `light-sdk`                  | [docs.rs/light-sdk](https://docs.rs/light-sdk)                                   |
| `light-sdk-pinocchio`        | [docs.rs/light-sdk-pinocchio](https://docs.rs/light-sdk-pinocchio)               |
| `light-token`                | [docs.rs/light-token](https://docs.rs/light-token)                               |
| `light-token-client`         | [docs.rs/light-token-client](https://docs.rs/light-token-client)                 |
| `light-compressed-token-sdk` | [docs.rs/light-compressed-token-sdk](https://docs.rs/light-compressed-token-sdk) |
| `light-client`               | [docs.rs/light-client](https://docs.rs/light-client)                             |
| `light-program-test`         | [docs.rs/light-program-test](https://docs.rs/light-program-test)                 |
| `light-account-pinocchio`    | [docs.rs/light-account-pinocchio](https://docs.rs/light-account-pinocchio)       |
| `light-token-pinocchio`      | [docs.rs/light-token-pinocchio](https://docs.rs/light-token-pinocchio)           |
| `light-hasher`               | [docs.rs/light-hasher](https://docs.rs/light-hasher)                             |
| `light-account`              | [docs.rs/light-account](https://docs.rs/light-account)                           |

***

> For additional documentation and navigation, see: [https://www.zkcompression.com/llms.txt](https://www.zkcompression.com/llms.txt)
> For additional skills, see: [https://github.com/Lightprotocol/skills](https://github.com/Lightprotocol/skills)