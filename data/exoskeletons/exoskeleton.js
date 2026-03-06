#!/usr/bin/env node
/**
 * Exoskeletons — Node.js helper library for AI Agent Identity NFTs on Base.
 *
 * Exoskeletons are fully onchain NFTs designed as agent identity primitives.
 * Visual identity, communication, storage, reputation, modules — all onchain.
 * CC0 — Creative Commons Zero. No rights reserved.
 *
 * Usage:
 *   import { Exoskeleton } from "./exoskeleton.js";
 *   const exo = new Exoskeleton();
 *
 *   // Reading (no wallet needed)
 *   const identity = await exo.getIdentity(1);
 *   const score = await exo.getReputationScore(1);
 *   const stats = await exo.getNetworkStats();
 *
 *   // Writing (returns transaction JSON for Bankr)
 *   const tx = exo.buildSetName(1, "Atlas");
 *   const tx = exo.buildSendMessage(1, 42, ethers.ZeroHash, 0, "hello!");
 *   // Submit `tx` via Bankr: curl -X POST https://api.bankr.bot/agent/submit ...
 *
 * CLI:
 *   node exoskeleton.js 1
 *   node exoskeleton.js stats
 *   node exoskeleton.js lookup Atlas
 */

import { ethers } from "ethers";

// --- Contract Addresses (update after deployment) ---

const CONTRACTS = {
  core: "0x8241BDD5009ed3F6C99737D2415994B58296Da0d",
  renderer: "0xE559f88f124AA2354B1570b85f6BE9536B6D60bC",
  registry: "0x46fd56417dcd08cA8de1E12dd6e7f7E1b791B3E9",
  wallet: "0x78aF4B6D78a116dEDB3612A30365718B076894b9",
  marketplace: "0x0E760171da676c219F46f289901D0be1CBD06188",
};

const RPC_URL = "https://mainnet.base.org";
const CHAIN_ID = 8453;

// --- ABI Fragments ---

const CORE_ABI = [
  // Minting
  "function mint(bytes config) payable",
  "function getMintPrice() view returns (uint256)",
  "function getMintPhase() view returns (string)",
  "function nextTokenId() view returns (uint256)",
  "function mintCount(address) view returns (uint256)",
  "function usedFreeMint(address) view returns (bool)",
  "function whitelist(address) view returns (bool)",
  // Identity
  "function setName(uint256 tokenId, string name)",
  "function setBio(uint256 tokenId, string bio)",
  "function setVisualConfig(uint256 tokenId, bytes config)",
  "function setCustomVisual(uint256 tokenId, string netProtocolKey)",
  "function getIdentity(uint256 tokenId) view returns (string name, string bio, bytes visualConfig, string customVisualKey, uint256 mintedAt, bool genesis)",
  "function isGenesis(uint256 tokenId) view returns (bool)",
  "function ownerOf(uint256 tokenId) view returns (address)",
  "function nameToToken(string name) view returns (uint256)",
  // Communication
  "function sendMessage(uint256 fromToken, uint256 toToken, bytes32 channel, uint8 msgType, bytes payload)",
  "function getMessageCount() view returns (uint256)",
  "function getChannelMessageCount(bytes32 channel) view returns (uint256)",
  "function getInboxCount(uint256 tokenId) view returns (uint256)",
  "function messages(uint256 index) view returns (uint256 fromToken, uint256 toToken, bytes32 channel, uint8 msgType, bytes payload, uint256 timestamp)",
  // Storage
  "function setData(uint256 tokenId, bytes32 key, bytes value)",
  "function getData(uint256 tokenId, bytes32 key) view returns (bytes)",
  "function setNetProtocolOperator(uint256 tokenId, address operator)",
  "function netProtocolOperator(uint256 tokenId) view returns (address)",
  // Reputation
  "function getReputationScore(uint256 tokenId) view returns (uint256)",
  "function getReputation(uint256 tokenId) view returns (uint256 messagesSent, uint256 storageWrites, uint256 modulesActive, uint256 age)",
  "function grantScorer(uint256 tokenId, address scorer)",
  "function revokeScorer(uint256 tokenId, address scorer)",
  "function setExternalScore(uint256 tokenId, bytes32 scoreKey, int256 value)",
  "function externalScores(uint256 tokenId, bytes32 scoreKey) view returns (int256)",
  // Modules
  "function activateModule(uint256 tokenId, bytes32 moduleName) payable",
  "function deactivateModule(uint256 tokenId, bytes32 moduleName)",
  "function isModuleActive(uint256 tokenId, bytes32 moduleName) view returns (bool)",
  // Token URI
  "function tokenURI(uint256 tokenId) view returns (string)",
];

const REGISTRY_ABI = [
  "function resolveByName(string name) view returns (uint256)",
  "function getName(uint256 tokenId) view returns (string)",
  "function getProfile(uint256 tokenId) view returns (string name, string bio, bool genesis, uint256 age, uint256 messagesSent, uint256 storageWrites, uint256 modulesActive, uint256 reputationScore, address owner)",
  "function getNetworkStats() view returns (uint256 totalMinted, uint256 totalMessages)",
  "function getReputationBatch(uint256 startId, uint256 count) view returns (uint256[] tokenIds, uint256[] scores)",
  "function getProfileBatch(uint256[] ids) view returns (string[] names, bool[] genesisFlags, uint256[] repScores)",
  "function getActiveModulesForToken(uint256 tokenId) view returns (bytes32[])",
  "function getTrackedModules() view returns (bytes32[])",
  "function moduleLabels(bytes32 moduleName) view returns (string)",
];

const WALLET_ABI = [
  "function activateWallet(uint256 tokenId) returns (address)",
  "function getWalletAddress(uint256 tokenId) view returns (address)",
  "function hasWallet(uint256 tokenId) view returns (bool)",
];

const RENDERER_ABI = [
  "function renderSVG(uint256 tokenId) view returns (string)",
];

const MARKETPLACE_ABI = [
  // Builder
  "function registerBuilder(string name, string bio)",
  "function updateBuilderProfile(string name, string bio)",
  "function getBuilder(address builderAddr) view returns (string name, string bio, uint256 modulesSubmitted, uint256 totalEarnings, bool registered)",
  // Module submission
  "function submitModule(bytes32 moduleName, string name, string description, string version, uint256 price) payable",
  // Activation
  "function activateModule(uint256 tokenId, bytes32 moduleName) payable",
  "function deactivateModule(uint256 tokenId, bytes32 moduleName)",
  // Builder updates
  "function updateModulePrice(bytes32 moduleName, uint256 newPrice)",
  "function updateModuleDescription(bytes32 moduleName, string newDescription)",
  "function updateModuleVersion(bytes32 moduleName, string newVersion)",
  "function builderDelistModule(bytes32 moduleName)",
  // Views
  "function getModule(bytes32 moduleName) view returns (address builder, string name, string description, string version, uint256 price, uint8 status, uint256 submittedAt, uint256 approvedAt, uint256 moduleActivations, uint256 moduleRevenue)",
  "function isModuleActive(uint256 tokenId, bytes32 moduleName) view returns (bool)",
  "function getActivation(uint256 tokenId, bytes32 moduleName) view returns (bool active, uint256 activatedAt)",
  "function getTokenActiveModules(uint256 tokenId) view returns (bytes32[])",
  "function getBuilderModules(address builderAddr) view returns (bytes32[])",
  "function getAllModuleNames() view returns (bytes32[])",
  "function getPendingQueue() view returns (bytes32[])",
  "function getModuleCount() view returns (uint256)",
  "function getPendingCount() view returns (uint256)",
  "function getStats() view returns (uint256 totalModules, uint256 totalApproved, uint256 totalActivations, uint256 totalPlatformRevenue, uint256 pendingCount, uint256 listingFees)",
  // Constants
  "function PLATFORM_FEE_BPS() view returns (uint256)",
  "function LISTING_FEE() view returns (uint256)",
  "function MAX_PRICE() view returns (uint256)",
  "function platformTreasury() view returns (address)",
];

// --- ABI Coder ---

const coder = ethers.AbiCoder.defaultAbiCoder();
const iface = {
  core: new ethers.Interface(CORE_ABI),
  registry: new ethers.Interface(REGISTRY_ABI),
  wallet: new ethers.Interface(WALLET_ABI),
  renderer: new ethers.Interface(RENDERER_ABI),
  marketplace: new ethers.Interface(MARKETPLACE_ABI),
};

// --- Visual Config Constants ---

export const SHAPES = ["hexagon", "circle", "diamond", "shield", "octagon", "triangle"];
export const SYMBOLS = ["none", "eye", "gear", "bolt", "star", "wave", "node", "diamond"];
export const PATTERNS = ["none", "grid", "dots", "lines", "circuits", "rings"];

// --- Exoskeleton Class ---

export class Exoskeleton {
  constructor(rpcUrl = RPC_URL, contracts = CONTRACTS) {
    this.rpcUrl = rpcUrl;
    this.contracts = contracts;
  }

  // ═══════════════════════════════════════════════════════════════
  //  RPC HELPERS
  // ═══════════════════════════════════════════════════════════════

  async rpcCall(to, data) {
    const resp = await fetch(this.rpcUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "eth_call",
        params: [{ to, data }, "latest"],
        id: 1,
      }),
    });
    const result = await resp.json();
    if (result.error) throw new Error(`RPC error: ${JSON.stringify(result.error)}`);
    if (!result.result || result.result === "0x") throw new Error(`Empty RPC response`);
    return result.result;
  }

  _buildTx(to, data, value = "0") {
    return { to, data, value, chainId: CHAIN_ID };
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — IDENTITY
  // ═══════════════════════════════════════════════════════════════

  async getIdentity(tokenId) {
    const data = iface.core.encodeFunctionData("getIdentity", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getIdentity", result);
    return {
      name: decoded.name,
      bio: decoded.bio,
      visualConfig: decoded.visualConfig,
      customVisualKey: decoded.customVisualKey,
      mintedAt: decoded.mintedAt,
      genesis: decoded.genesis,
    };
  }

  async getOwner(tokenId) {
    const data = iface.core.encodeFunctionData("ownerOf", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("ownerOf", result);
    return decoded[0];
  }

  async isGenesis(tokenId) {
    const data = iface.core.encodeFunctionData("isGenesis", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("isGenesis", result);
    return decoded[0];
  }

  async resolveByName(name) {
    const data = iface.registry.encodeFunctionData("resolveByName", [name]);
    const result = await this.rpcCall(this.contracts.registry, data);
    const decoded = iface.registry.decodeFunctionResult("resolveByName", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — REPUTATION
  // ═══════════════════════════════════════════════════════════════

  async getReputation(tokenId) {
    const data = iface.core.encodeFunctionData("getReputation", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getReputation", result);
    return {
      messagesSent: decoded.messagesSent,
      storageWrites: decoded.storageWrites,
      modulesActive: decoded.modulesActive,
      age: decoded.age,
    };
  }

  async getReputationScore(tokenId) {
    const data = iface.core.encodeFunctionData("getReputationScore", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getReputationScore", result);
    return decoded[0];
  }

  async getExternalScore(tokenId, scoreKey) {
    const data = iface.core.encodeFunctionData("externalScores", [tokenId, scoreKey]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("externalScores", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — COMMUNICATION
  // ═══════════════════════════════════════════════════════════════

  async getMessageCount() {
    const data = iface.core.encodeFunctionData("getMessageCount", []);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getMessageCount", result);
    return decoded[0];
  }

  async getChannelMessageCount(channel) {
    const data = iface.core.encodeFunctionData("getChannelMessageCount", [channel]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getChannelMessageCount", result);
    return decoded[0];
  }

  async getInboxCount(tokenId) {
    const data = iface.core.encodeFunctionData("getInboxCount", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getInboxCount", result);
    return decoded[0];
  }

  async getMessage(index) {
    const data = iface.core.encodeFunctionData("messages", [index]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("messages", result);
    return {
      fromToken: decoded.fromToken,
      toToken: decoded.toToken,
      channel: decoded.channel,
      msgType: decoded.msgType,
      payload: decoded.payload,
      timestamp: decoded.timestamp,
    };
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — STORAGE
  // ═══════════════════════════════════════════════════════════════

  async getData(tokenId, key) {
    const data = iface.core.encodeFunctionData("getData", [tokenId, key]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getData", result);
    return decoded[0];
  }

  async getNetProtocolOperator(tokenId) {
    const data = iface.core.encodeFunctionData("netProtocolOperator", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("netProtocolOperator", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — MODULES
  // ═══════════════════════════════════════════════════════════════

  async isModuleActive(tokenId, moduleName) {
    const data = iface.core.encodeFunctionData("isModuleActive", [tokenId, moduleName]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("isModuleActive", result);
    return decoded[0];
  }

  async getActiveModulesForToken(tokenId) {
    const data = iface.registry.encodeFunctionData("getActiveModulesForToken", [tokenId]);
    const result = await this.rpcCall(this.contracts.registry, data);
    const decoded = iface.registry.decodeFunctionResult("getActiveModulesForToken", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — REGISTRY & STATS
  // ═══════════════════════════════════════════════════════════════

  async getProfile(tokenId) {
    const data = iface.registry.encodeFunctionData("getProfile", [tokenId]);
    const result = await this.rpcCall(this.contracts.registry, data);
    const decoded = iface.registry.decodeFunctionResult("getProfile", result);
    return {
      name: decoded.name,
      bio: decoded.bio,
      genesis: decoded.genesis,
      age: decoded.age,
      messagesSent: decoded.messagesSent,
      storageWrites: decoded.storageWrites,
      modulesActive: decoded.modulesActive,
      reputationScore: decoded.reputationScore,
      owner: decoded.owner,
    };
  }

  async getNetworkStats() {
    const data = iface.registry.encodeFunctionData("getNetworkStats", []);
    const result = await this.rpcCall(this.contracts.registry, data);
    const decoded = iface.registry.decodeFunctionResult("getNetworkStats", result);
    return {
      totalMinted: decoded.totalMinted,
      totalMessages: decoded.totalMessages,
    };
  }

  async getReputationBatch(startId, count) {
    const data = iface.registry.encodeFunctionData("getReputationBatch", [startId, count]);
    const result = await this.rpcCall(this.contracts.registry, data);
    const decoded = iface.registry.decodeFunctionResult("getReputationBatch", result);
    return { tokenIds: decoded.tokenIds, scores: decoded.scores };
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — MINT INFO
  // ═══════════════════════════════════════════════════════════════

  async getMintPrice() {
    const data = iface.core.encodeFunctionData("getMintPrice", []);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getMintPrice", result);
    return decoded[0];
  }

  async getMintPhase() {
    const data = iface.core.encodeFunctionData("getMintPhase", []);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("getMintPhase", result);
    return decoded[0];
  }

  async getNextTokenId() {
    const data = iface.core.encodeFunctionData("nextTokenId", []);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("nextTokenId", result);
    return decoded[0];
  }

  async getMintCount(address) {
    const data = iface.core.encodeFunctionData("mintCount", [address]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("mintCount", result);
    return decoded[0];
  }

  async hasUsedFreeMint(address) {
    const data = iface.core.encodeFunctionData("usedFreeMint", [address]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("usedFreeMint", result);
    return decoded[0];
  }

  async isWhitelisted(address) {
    const data = iface.core.encodeFunctionData("whitelist", [address]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("whitelist", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — WALLET
  // ═══════════════════════════════════════════════════════════════

  async getWalletAddress(tokenId) {
    const data = iface.wallet.encodeFunctionData("getWalletAddress", [tokenId]);
    const result = await this.rpcCall(this.contracts.wallet, data);
    const decoded = iface.wallet.decodeFunctionResult("getWalletAddress", result);
    return decoded[0];
  }

  async hasWallet(tokenId) {
    const data = iface.wallet.encodeFunctionData("hasWallet", [tokenId]);
    const result = await this.rpcCall(this.contracts.wallet, data);
    const decoded = iface.wallet.decodeFunctionResult("hasWallet", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — RENDERER
  // ═══════════════════════════════════════════════════════════════

  async renderSVG(tokenId) {
    const data = iface.renderer.encodeFunctionData("renderSVG", [tokenId]);
    const result = await this.rpcCall(this.contracts.renderer, data);
    const decoded = iface.renderer.decodeFunctionResult("renderSVG", result);
    return decoded[0];
  }

  async getTokenURI(tokenId) {
    const data = iface.core.encodeFunctionData("tokenURI", [tokenId]);
    const result = await this.rpcCall(this.contracts.core, data);
    const decoded = iface.core.decodeFunctionResult("tokenURI", result);
    return decoded[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — MINTING (returns Bankr tx JSON)
  // ═══════════════════════════════════════════════════════════════

  /**
   * Build mint transaction. Automatically determines if free (WL first mint) or paid.
   * @param config Visual config bytes (9 bytes or Uint8Array)
   * @param ethValue Optional ETH value override. If not provided, fetches price from contract.
   */
  async buildMint(config, ethValue) {
    const configBytes = config instanceof Uint8Array ? ethers.hexlify(config) : config;
    const data = iface.core.encodeFunctionData("mint", [configBytes]);
    const value = ethValue !== undefined ? ethValue.toString() : (await this.getMintPrice()).toString();
    return this._buildTx(this.contracts.core, data, value);
  }

  /** Build a free mint transaction (for whitelisted first mint). */
  buildFreeMint(config) {
    const configBytes = config instanceof Uint8Array ? ethers.hexlify(config) : config;
    const data = iface.core.encodeFunctionData("mint", [configBytes]);
    return this._buildTx(this.contracts.core, data, "0");
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — IDENTITY
  // ═══════════════════════════════════════════════════════════════

  buildSetName(tokenId, name) {
    const data = iface.core.encodeFunctionData("setName", [tokenId, name]);
    return this._buildTx(this.contracts.core, data);
  }

  buildSetBio(tokenId, bio) {
    const data = iface.core.encodeFunctionData("setBio", [tokenId, bio]);
    return this._buildTx(this.contracts.core, data);
  }

  buildSetVisualConfig(tokenId, config) {
    const configBytes = config instanceof Uint8Array ? ethers.hexlify(config) : config;
    const data = iface.core.encodeFunctionData("setVisualConfig", [tokenId, configBytes]);
    return this._buildTx(this.contracts.core, data);
  }

  buildSetCustomVisual(tokenId, netProtocolKey) {
    const data = iface.core.encodeFunctionData("setCustomVisual", [tokenId, netProtocolKey]);
    return this._buildTx(this.contracts.core, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — COMMUNICATION
  // ═══════════════════════════════════════════════════════════════

  buildSendMessage(fromToken, toToken, channel, msgType, text) {
    const payload = typeof text === "string" ? ethers.toUtf8Bytes(text) : text;
    const data = iface.core.encodeFunctionData("sendMessage", [
      fromToken, toToken, channel, msgType, payload,
    ]);
    return this._buildTx(this.contracts.core, data);
  }

  /** Helper: send a direct text message. */
  buildDirectMessage(fromToken, toToken, text) {
    return this.buildSendMessage(fromToken, toToken, ethers.ZeroHash, 0, text);
  }

  /** Helper: broadcast a text message to all. */
  buildBroadcast(fromToken, text) {
    return this.buildSendMessage(fromToken, 0, ethers.ZeroHash, 0, text);
  }

  /** Helper: send to a named channel. */
  buildChannelMessage(fromToken, channelName, text) {
    const channel = ethers.keccak256(ethers.toUtf8Bytes(channelName));
    return this.buildSendMessage(fromToken, 0, channel, 0, text);
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — STORAGE
  // ═══════════════════════════════════════════════════════════════

  buildSetData(tokenId, key, value) {
    const valueBytes = typeof value === "string" ? ethers.toUtf8Bytes(value) : value;
    const data = iface.core.encodeFunctionData("setData", [tokenId, key, valueBytes]);
    return this._buildTx(this.contracts.core, data);
  }

  buildSetNetProtocolOperator(tokenId, operator) {
    const data = iface.core.encodeFunctionData("setNetProtocolOperator", [tokenId, operator]);
    return this._buildTx(this.contracts.core, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — REPUTATION
  // ═══════════════════════════════════════════════════════════════

  buildGrantScorer(tokenId, scorer) {
    const data = iface.core.encodeFunctionData("grantScorer", [tokenId, scorer]);
    return this._buildTx(this.contracts.core, data);
  }

  buildRevokeScorer(tokenId, scorer) {
    const data = iface.core.encodeFunctionData("revokeScorer", [tokenId, scorer]);
    return this._buildTx(this.contracts.core, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — MODULES
  // ═══════════════════════════════════════════════════════════════

  buildActivateModule(tokenId, moduleName, ethValue = "0") {
    const data = iface.core.encodeFunctionData("activateModule", [tokenId, moduleName]);
    return this._buildTx(this.contracts.core, data, ethValue.toString());
  }

  buildDeactivateModule(tokenId, moduleName) {
    const data = iface.core.encodeFunctionData("deactivateModule", [tokenId, moduleName]);
    return this._buildTx(this.contracts.core, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — WALLET
  // ═══════════════════════════════════════════════════════════════

  buildActivateWallet(tokenId) {
    const data = iface.wallet.encodeFunctionData("activateWallet", [tokenId]);
    return this._buildTx(this.contracts.wallet, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  READ — MARKETPLACE
  // ═══════════════════════════════════════════════════════════════

  async getMarketplaceModule(moduleName) {
    const data = iface.marketplace.encodeFunctionData("getModule", [moduleName]);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    const d = iface.marketplace.decodeFunctionResult("getModule", result);
    const STATUS_NAMES = ["NONE", "PENDING", "APPROVED", "REJECTED", "DELISTED"];
    return {
      builder: d.builder, name: d.name, description: d.description,
      version: d.version, price: d.price, status: STATUS_NAMES[Number(d.status)] || "UNKNOWN",
      statusCode: d.status, submittedAt: d.submittedAt, approvedAt: d.approvedAt,
      totalActivations: d.moduleActivations, totalRevenue: d.moduleRevenue,
    };
  }

  async getMarketplaceBuilder(builderAddr) {
    const data = iface.marketplace.encodeFunctionData("getBuilder", [builderAddr]);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    const d = iface.marketplace.decodeFunctionResult("getBuilder", result);
    return { name: d.name, bio: d.bio, modulesSubmitted: d.modulesSubmitted, totalEarnings: d.totalEarnings, registered: d.registered };
  }

  async isMarketplaceModuleActive(tokenId, moduleName) {
    const data = iface.marketplace.encodeFunctionData("isModuleActive", [tokenId, moduleName]);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    return iface.marketplace.decodeFunctionResult("isModuleActive", result)[0];
  }

  async getMarketplaceActiveModules(tokenId) {
    const data = iface.marketplace.encodeFunctionData("getTokenActiveModules", [tokenId]);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    return iface.marketplace.decodeFunctionResult("getTokenActiveModules", result)[0];
  }

  async getMarketplaceStats() {
    const data = iface.marketplace.encodeFunctionData("getStats", []);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    const d = iface.marketplace.decodeFunctionResult("getStats", result);
    return {
      totalModules: d.totalModules, totalApproved: d.totalApproved,
      totalActivations: d.totalActivations, totalPlatformRevenue: d.totalPlatformRevenue,
      pendingCount: d.pendingCount, listingFees: d.listingFees,
    };
  }

  async getMarketplaceModuleCount() {
    const data = iface.marketplace.encodeFunctionData("getModuleCount", []);
    const result = await this.rpcCall(this.contracts.marketplace, data);
    return iface.marketplace.decodeFunctionResult("getModuleCount", result)[0];
  }

  // ═══════════════════════════════════════════════════════════════
  //  WRITE — MARKETPLACE (returns Bankr tx JSON)
  // ═══════════════════════════════════════════════════════════════

  buildRegisterBuilder(name, bio) {
    const data = iface.marketplace.encodeFunctionData("registerBuilder", [name, bio]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  buildSubmitModule(moduleName, name, description, version, price) {
    const data = iface.marketplace.encodeFunctionData("submitModule", [moduleName, name, description, version, price]);
    return this._buildTx(this.contracts.marketplace, data, "1000000000000000"); // 0.001 ETH listing fee
  }

  buildActivateMarketplaceModule(tokenId, moduleName, ethValue = "0") {
    const data = iface.marketplace.encodeFunctionData("activateModule", [tokenId, moduleName]);
    return this._buildTx(this.contracts.marketplace, data, ethValue.toString());
  }

  buildDeactivateMarketplaceModule(tokenId, moduleName) {
    const data = iface.marketplace.encodeFunctionData("deactivateModule", [tokenId, moduleName]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  buildUpdateModulePrice(moduleName, newPrice) {
    const data = iface.marketplace.encodeFunctionData("updateModulePrice", [moduleName, newPrice]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  buildUpdateModuleDescription(moduleName, newDescription) {
    const data = iface.marketplace.encodeFunctionData("updateModuleDescription", [moduleName, newDescription]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  buildUpdateModuleVersion(moduleName, newVersion) {
    const data = iface.marketplace.encodeFunctionData("updateModuleVersion", [moduleName, newVersion]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  buildBuilderDelistModule(moduleName) {
    const data = iface.marketplace.encodeFunctionData("builderDelistModule", [moduleName]);
    return this._buildTx(this.contracts.marketplace, data);
  }

  // ═══════════════════════════════════════════════════════════════
  //  UTILITY
  // ═══════════════════════════════════════════════════════════════

  /** Build a visual config from human-readable parameters. */
  static buildConfig(shape, r1, g1, b1, r2, g2, b2, symbol, pattern) {
    return new Uint8Array([shape, r1, g1, b1, r2, g2, b2, symbol, pattern]);
  }

  /** Parse a visual config into human-readable object. */
  static parseConfig(configBytes) {
    const bytes = typeof configBytes === "string"
      ? ethers.getBytes(configBytes)
      : configBytes;

    if (bytes.length < 9) {
      return { shape: "unknown", primary: "#000000", secondary: "#000000", symbol: "none", pattern: "none" };
    }

    const toHex = (r, g, b) => "#" + [r, g, b].map(v => v.toString(16).padStart(2, "0")).join("");

    return {
      shape: SHAPES[bytes[0]] || "unknown",
      primary: toHex(bytes[1], bytes[2], bytes[3]),
      secondary: toHex(bytes[4], bytes[5], bytes[6]),
      symbol: SYMBOLS[bytes[7]] || "none",
      pattern: PATTERNS[bytes[8]] || "none",
      raw: bytes,
    };
  }

  /** Format a reputation score with context. */
  static formatScore(score) {
    const n = typeof score === "bigint" ? Number(score) : score;
    if (n >= 100000) return `${(n / 1000).toFixed(0)}K`;
    if (n >= 10000) return `${(n / 1000).toFixed(1)}K`;
    return n.toString();
  }

  /** Create a channel hash from a channel name. */
  static channelHash(name) {
    return ethers.keccak256(ethers.toUtf8Bytes(name));
  }

  /** Create a key hash for storage. */
  static keyHash(name) {
    return ethers.keccak256(ethers.toUtf8Bytes(name));
  }
}

// --- CLI ---

const isMain = process.argv[1] && (
  process.argv[1].endsWith("exoskeleton.js") ||
  process.argv[1].endsWith("exoskeleton")
);

if (isMain) {
  const exo = new Exoskeleton();
  const arg = process.argv[2];

  if (!arg) {
    console.log("Usage:");
    console.log("  node exoskeleton.js <tokenId>    — View token profile");
    console.log("  node exoskeleton.js stats        — Network statistics");
    console.log("  node exoskeleton.js lookup <name> — Find token by name");
    console.log("  node exoskeleton.js price        — Current mint price");
    console.log("  node exoskeleton.js config <hex> — Parse visual config");
    process.exit(0);
  }

  (async () => {
    try {
      if (arg === "stats") {
        const stats = await exo.getNetworkStats();
        console.log("=== EXOSKELETON NETWORK ===\n");
        console.log(`  Total Minted:   ${stats.totalMinted}`);
        console.log(`  Total Messages: ${stats.totalMessages}`);
        console.log(`  Mint Phase:     ${await exo.getMintPhase()}`);
        console.log(`  Mint Price:     ${ethers.formatEther(await exo.getMintPrice())} ETH`);

      } else if (arg === "lookup") {
        const name = process.argv[3];
        if (!name) { console.log("Usage: node exoskeleton.js lookup <name>"); process.exit(1); }
        const tokenId = await exo.resolveByName(name);
        if (tokenId === 0n) {
          console.log(`No Exoskeleton found with name "${name}"`);
        } else {
          console.log(`"${name}" → Exoskeleton #${tokenId}`);
          const profile = await exo.getProfile(tokenId);
          printProfile(tokenId, profile);
        }

      } else if (arg === "price") {
        const price = await exo.getMintPrice();
        const phase = await exo.getMintPhase();
        const nextId = await exo.getNextTokenId();
        console.log(`Next Token ID: #${nextId}`);
        console.log(`Phase:         ${phase}`);
        console.log(`Price:         ${ethers.formatEther(price)} ETH`);

      } else if (arg === "config") {
        const hex = process.argv[3];
        if (!hex) { console.log("Usage: node exoskeleton.js config <hex>"); process.exit(1); }
        const parsed = Exoskeleton.parseConfig(hex);
        console.log("=== VISUAL CONFIG ===\n");
        console.log(`  Shape:     ${parsed.shape}`);
        console.log(`  Primary:   ${parsed.primary}`);
        console.log(`  Secondary: ${parsed.secondary}`);
        console.log(`  Symbol:    ${parsed.symbol}`);
        console.log(`  Pattern:   ${parsed.pattern}`);

      } else {
        // Token ID lookup
        const tokenId = parseInt(arg);
        if (isNaN(tokenId) || tokenId < 1) {
          console.log(`Invalid token ID: ${arg}`);
          process.exit(1);
        }

        const profile = await exo.getProfile(tokenId);
        printProfile(tokenId, profile);

        // Parse visual config
        const identity = await exo.getIdentity(tokenId);
        if (identity.visualConfig && identity.visualConfig.length >= 9) {
          const config = Exoskeleton.parseConfig(identity.visualConfig);
          console.log("\n=== VISUAL CONFIG ===\n");
          console.log(`  Shape:     ${config.shape}`);
          console.log(`  Primary:   ${config.primary}`);
          console.log(`  Secondary: ${config.secondary}`);
          console.log(`  Symbol:    ${config.symbol}`);
          console.log(`  Pattern:   ${config.pattern}`);
        }

        // Check wallet
        try {
          const hasWallet = await exo.hasWallet(tokenId);
          if (hasWallet) {
            const walletAddr = await exo.getWalletAddress(tokenId);
            console.log(`\n=== WALLET ===\n`);
            console.log(`  Address: ${walletAddr}`);
          }
        } catch { /* wallet contract may not be deployed yet */ }
      }
    } catch (e) {
      if (e.message.includes("Empty RPC") || e.message.includes("cannot unmarshal") || e.message.includes("ADDRESS_HERE")) {
        console.log("Contracts not deployed yet. Update addresses in exoskeleton.js after deployment.");
      } else {
        console.error(`Error: ${e.message}`);
      }
    }
  })();
}

function printProfile(tokenId, profile) {
  const genesisTag = profile.genesis ? " [GENESIS]" : "";
  console.log(`\nEXOSKELETON #${tokenId}${genesisTag}`);
  console.log(`Owner: ${profile.owner}`);
  console.log(`Name:  ${profile.name || "(unnamed)"}`);
  if (profile.bio) console.log(`Bio:   ${profile.bio}`);
  console.log(`\n=== REPUTATION ===\n`);
  console.log(`  Messages:       ${profile.messagesSent}`);
  console.log(`  Storage Writes: ${profile.storageWrites}`);
  console.log(`  Active Modules: ${profile.modulesActive}`);
  console.log(`  Age:            ${profile.age} blocks`);
  console.log(`  Score:          ${Exoskeleton.formatScore(profile.reputationScore)}`);
}
