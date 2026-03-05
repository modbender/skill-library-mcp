# Known Issues & Limitations

> Transparency matters. Here's everything we know about that isn't perfect yet.

**Last Updated:** 2026-02-15

## npm Dependency Vulnerabilities (Non-Critical)

The following npm vulnerabilities exist in development/build dependencies and **do not affect the smart contracts or SDK**:

| Package | Severity | Context | Why It's Unfixable |
|---------|----------|---------|-------------------|
| `next@14` (DoS via cache poisoning) | High × 2 | Frontend only | Patched in Next.js 15, which is a major breaking upgrade. Migration planned. |
| `elliptic` (signature malleability) | High | Hardhat dev dependency | No upstream patch exists. Dev-only — never reaches production. |
| `cookie` via `@sentry/node` | Moderate | Hardhat dev chain | Transitive dep through hardhat → sentry. Dev-only. |
| `axios` (prototype pollution in mergeConfig) | High | Backend | Low practical risk — behind authentication, no user-controlled config merging. Monitoring for patch. |
| `validator` (URL bypass) | Moderate | Backend via express-validator | App-layer input sanitization provides defense-in-depth. Monitoring for patch. |

**Smart contracts and the TypeScript SDK have zero known vulnerabilities.**

## Static Analysis Tools Not Run

The following tools were unavailable during validation and have not been run:
- **Slither** (Solidity static analyzer)
- **Mythril** (symbolic execution)
- **ggshield** (GitGuardian secret scanner)

The contracts have passed 2 rounds of internal AI-assisted adversarial review and 129 automated tests including 7 exploit regression tests. **No third-party audit has been performed.**

## Solidity Compiler Warnings

4 variable shadowing warnings exist in `AgentAccountV2.sol` and `AgentAccountV2_4337.sol` (local `success`/`result` variables in nested scopes). These are cosmetic and do not affect functionality or security.

## Test Coverage

- `forge coverage` requires the `--ir-minimum` flag due to Solidity compiler stack-too-deep limitations with the IR pipeline. This is a known Foundry/Solc limitation, not a project issue.
- 35 backend tests are skipped in CI (WebSocket and live API endpoint tests requiring running services). These should be run in integration/staging environments.

## Frontend

- Web3 provider (wagmi/rainbowkit) is loaded client-side only (`ssr: false`) to avoid `localStorage` access during server-side rendering. This means wallet connection UI appears after hydration, not during initial page load — a brief flash may be visible.

---

*If you discover an issue not listed here, please report it. We take security and quality seriously.*
