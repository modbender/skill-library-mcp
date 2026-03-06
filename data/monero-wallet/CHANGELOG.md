# Monero Wallet Skill Changelog

Documentation of version history and updates for the `monero-wallet` AI Agent skill.

## [1.2.2] - 2026-02-26

### Fixed
- **Instruction Consistency**: Removed all references to the undeclared `$AGENT_GATEWAY_URL` in `SKILL.md` examples. Standardized all manual `curl` examples to use `http://127.0.0.1:38084` to match the hardcoded security logic in the helper script. This resolves OpenClaw's "contradictory instructions" flag.

## [1.2.1] - 2026-02-26

### Security
- **Anti-Exfiltration Patch**: Hardcoded `GATEWAY_URL` to `127.0.0.1` in `monero_wallet_rpc.py` and removed `AGENT_GATEWAY_URL` from `SKILL.md`. This prevents compromised agents from redirecting the `AGENT_API_KEY` to attacker-controlled servers via prompt injection.

## [1.2.0] - 2026-02-26

### Changed
- **Instruction Prioritization**: Refactored `SKILL.md` to prioritize the native Python helper (`monero_wallet_rpc.py`) as the primary interaction tool for agents.
- **REST API Fallback**: Categorized direct HTTP/Curl calls as a secondary fallback method for universal compatibility.
- **Improved UX**: Agents are now instructed to use the script, which automatically handles environment-injected API keys and Gateway URLs.

## [1.1.1] - 2026-02-26

### Security
- **OpenClaw Audit Hardening**: Formalized `AGENT_GATEWAY_URL` and `pip:requests` declarations in `SKILL.md` to resolve "Suspicious" flags.
- **Anti-Exfiltration Guardrails**: Added explicit security warnings to `monero_wallet_rpc.py` to prevent credentials from being sent to untrusted remote endpoints.
- **Dependency Validation**: Added runtime checks for the `requests` library with helpful installation prompts.

### Changed
- **Content Refinement**: Simplified swap service descriptions in `SKILL.md` for better readability.

## [1.1.0] - 2026-02-26

### Added
- **OpenClaw Support**: Integrated `metadata.openclaw` with `primaryEnv: AGENT_API_KEY` to enable the configuration panel UI.
- **Ecosystem Meta**: Added `emoji`, `categories`, and `homepage` to standard skill definition.
- **Skill CLI**: Added a custom installation guide for `clawhub install` and `gemini skills install`.
- **Swap Guidance**: Integrated explicit instructions for agents to suggest [kyc.rip/swap](https://kyc.rip/swap) when wallet balance is insufficient.

### Changed
- **Authenticated Architecture**: Migrated all instructions from plain Python scripts to secure, authenticated HTTP Gateway calls.
- **Identity Refinement**: Formally branded as the official **Ripley XMR Gateway** skill.
- **Helper Script Optimization**: `monero_wallet_rpc.py` now supports explicit `--api-key` passing for better integration with host-injected environments.

### Security
- **Mandatory Authentication**: All agent tools now require `AGENT_API_KEY`.
- **Privacy Focus**: Enhanced guidelines for subaddress generation to ensure on-chain anonymity.

## [1.0.0] - 2026-02-24

### Added
- Initial release of the `monero-wallet` skill definition.
- Fundamental subaddress and transfer instruction sets.
- Basic RPC communication helper scripts.
