/** Minimal ABI for ZeruIdentityRegistryUpgradeable (v4.0.0) */
export const identityRegistryAbi = [
    // ── Registration ──
    "function registerWithFee(string agentURI) external payable returns (uint256 agentId)",
    "function registrationFee() external view returns (uint256)",
    "function registrationEnabled() external view returns (bool)",
    "function freeRegistrationEnabled() external view returns (bool)",
    // ── Agent URI ──
    "function setAgentURI(uint256 agentId, string newURI) external",
    "function tokenURI(uint256 tokenId) external view returns (string)",
    // ── Agent Wallet ──
    "function setAgentWallet(uint256 agentId, address newWallet, uint256 deadline, bytes signature) external",
    "function unsetAgentWallet(uint256 agentId) external",
    "function getAgentWallet(uint256 agentId) external view returns (address)",
    // ── Metadata ──
    "function setMetadata(uint256 agentId, string metadataKey, bytes metadataValue) external",
    "function getMetadata(uint256 agentId, string metadataKey) external view returns (bytes)",
    // ── Reads ──
    "function ownerOf(uint256 tokenId) external view returns (address)",
    "function isAuthorizedOrOwner(address spender, uint256 agentId) external view returns (bool)",
    "function getVersion() external view returns (string)",
    // ── Events ──
    "event Registered(uint256 indexed agentId, string agentURI, address indexed owner)",
    "event URIUpdated(uint256 indexed agentId, string newURI, address indexed updatedBy)",
    "event MetadataSet(uint256 indexed agentId, string indexed indexedMetadataKey, string metadataKey, bytes metadataValue)",
];
