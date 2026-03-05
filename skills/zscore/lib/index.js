/**
 * @zeru/erc8004 — SDK for Zeru ERC-8004 Identity Registry
 *
 * Register agents, manage wallets & metadata, discover other agents.
 */
export { resolveConfig, agentUriApiUrl, discoveryUrl } from "./config.js";
// ── Errors ──
export { ErrorCode, ZeruError, rpcError, apiError, validationError } from "./errors.js";
// ── Schema ──
export { agentRegistrationSchema, createAgentURIInputSchema, parseCreateAgentURIInput, toAgentRegistration, } from "./schema.js";
// ── ABI ──
export { identityRegistryAbi } from "./abi.js";
// ── Agent URI ──
export { createAgentURI, updateAgentURI } from "./create-agent-uri.js";
// ── Registration ──
export { registerAgent } from "./register-agent.js";
// ── On-chain reads ──
export { getAgent, getRegistrationFee, isRegistrationEnabled } from "./get-agent.js";
// ── Wallet ──
export { setAgentWallet, unsetAgentWallet, getAgentWallet } from "./agent-wallet.js";
// ── Metadata ──
export { setMetadata, getMetadata } from "./metadata.js";
// ── Discovery ──
export { searchAgents } from "./search-agents.js";
// ── Reputation ──
export { getReputation } from "./get-reputation.js";
