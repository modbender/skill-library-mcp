# ABIXUS Deterministic Oracle
A high-performance validation layer for autonomous agent consistency on Polygon PoS.

## Security & Privacy Disclosure
- **Zero-Knowledge Principle**: ABIXUS does not require, store, or ask for Private Keys.
- **Public Data Only**: The service only processes public wallet addresses to verify on-chain transactions (POL transfers) to the treasury.
- **Data Integrity**: No session data is stored. Wallet IDs are used solely for real-time credit balance lookup and ranking.

## Technical Architecture
ABIXUS acts as a secure bridge between the Polygon ledger and an agent's runtime, utilizing a dedicated Cloudflare Tunnel for encrypted communication.
- **Endpoint**: https://api.abixus.xyz
- **Handshake**: Verification is performed by cross-referencing the `{wallet}` parameter with public event logs on-chain.
- **Infrastructure**: Proxied via TLS 1.3 to ensure enterprise-grade security for agent-to-agent calls.

## Usage
1. **Query Status**: GET `/status/{wallet}` to retrieve credit balance and verification state.
2. **Execute Validation**: POST `/certifica/{wallet}` to initiate a deterministic stress-test batch.
3. **Funding**: If balance is 0, refer to `abixus_manifesto.json` for the treasury settlement address.