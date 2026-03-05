import { Contract, JsonRpcProvider } from "ethers";
import { rpcError } from "./errors.js";
import { identityRegistryAbi } from "./abi.js";
/**
 * Read an agent's on-chain data (owner, tokenURI, agentWallet).
 * Optionally fetches and parses the agentURI JSON.
 */
export async function getAgent(config, agentId) {
    try {
        const provider = new JsonRpcProvider(config.rpcUrl);
        const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, provider);
        const id = BigInt(agentId);
        const [owner, agentURI, wallet] = await Promise.all([
            registry.ownerOf(id),
            registry.tokenURI(id),
            registry.getAgentWallet(id),
        ]);
        const ZERO = "0x0000000000000000000000000000000000000000";
        const result = {
            owner,
            agentURI,
            agentWallet: wallet === ZERO ? null : wallet,
        };
        // Try to fetch and parse the agentURI
        if (agentURI && agentURI.startsWith("http")) {
            try {
                const res = await fetch(agentURI);
                if (res.ok)
                    result.parsedJson = (await res.json());
            }
            catch {
                // skip — optional
            }
        }
        return result;
    }
    catch (e) {
        if (e instanceof Error && e.name === "ZeruError")
            throw e;
        throw rpcError(e instanceof Error ? e.message : "getAgent failed", { cause: e });
    }
}
/**
 * Read the current registration fee from the contract (in wei).
 */
export async function getRegistrationFee(config) {
    const provider = new JsonRpcProvider(config.rpcUrl);
    const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, provider);
    return registry.registrationFee();
}
/**
 * Check if registration is currently enabled.
 */
export async function isRegistrationEnabled(config) {
    const provider = new JsonRpcProvider(config.rpcUrl);
    const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, provider);
    return registry.registrationEnabled();
}
