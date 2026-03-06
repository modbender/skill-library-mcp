/** Built-in chain defaults */
const CHAIN_DEFAULTS = {
    8453: {
        identityRegistryAddress: "0xFfE9395fa761e52DBC077a2e7Fd84f77e8abCc41",
        reputationRegistryAddress: "0x187d72a58b3BF4De6432958fc36CE569Fb15C237",
        rpcUrl: "https://mainnet.base.org",
        agentUriApiBase: "https://agenturi.zpass.ai",
        zeruApiBase: "https://agentapi.zpass.ai",
    },
    84532: {
        identityRegistryAddress: "0xF0682549516A4BA09803cCa55140AfBC4e5ed2E0",
        reputationRegistryAddress: "0xaAC7557475023AEB581ECc8bD6886d1742382421",
        rpcUrl: "https://sepolia.base.org",
        agentUriApiBase: "https://agenturi.zpass.ai",
        zeruApiBase: "https://agentapi.zpass.ai",
    },
};
const ADDRESS_REGEX = /^0x[a-fA-F0-9]{40}$/;
function stripTrailingSlash(url) {
    return url.replace(/\/$/, "");
}
/** Resolve a ZeruConfig by filling in defaults for known chains. */
export function resolveConfig(config) {
    const defaults = CHAIN_DEFAULTS[config.chainId];
    const identityRegistryAddress = config.identityRegistryAddress ?? defaults?.identityRegistryAddress;
    const rpcUrl = config.rpcUrl ?? defaults?.rpcUrl;
    const agentUriApiBase = config.agentUriApiBase ?? defaults?.agentUriApiBase;
    const zeruApiBase = config.zeruApiBase ?? defaults?.zeruApiBase;
    if (!identityRegistryAddress || !ADDRESS_REGEX.test(identityRegistryAddress)) {
        throw new Error(`identityRegistryAddress required for chainId ${config.chainId}`);
    }
    if (!rpcUrl) {
        throw new Error(`rpcUrl required for chainId ${config.chainId}`);
    }
    if (!agentUriApiBase) {
        throw new Error(`agentUriApiBase required for chainId ${config.chainId}`);
    }
    if (!zeruApiBase) {
        throw new Error(`zeruApiBase required for chainId ${config.chainId}`);
    }
    return {
        chainId: config.chainId,
        identityRegistryAddress,
        rpcUrl,
        agentUriApiBase: stripTrailingSlash(agentUriApiBase),
        zeruApiBase: stripTrailingSlash(zeruApiBase),
        discoveryApiKey: config.discoveryApiKey,
        source: config.source ?? "zeru",
    };
}
export function agentUriApiUrl(rc) {
    return `${rc.agentUriApiBase}/v1/agent-uri`;
}
export function discoveryUrl(rc) {
    return `${rc.zeruApiBase}/v1/discovery`;
}
