import { Contract, JsonRpcProvider, hexlify, toUtf8Bytes, toUtf8String } from "ethers";
import { rpcError } from "./errors.js";
import { identityRegistryAbi } from "./abi.js";
/**
 * Set custom metadata on an agent. Only the owner/approved can call.
 * Note: "agentWallet" is a reserved key — use setAgentWallet() instead.
 *
 * @param value - Metadata value as string (encoded to bytes) or raw hex bytes
 */
export async function setMetadata(config, signer, agentId, key, value) {
    try {
        const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, signer);
        const valueBytes = value.startsWith("0x") ? value : hexlify(toUtf8Bytes(value));
        const tx = await registry.setMetadata(agentId, key, valueBytes);
        const receipt = await tx.wait();
        return receipt.hash;
    }
    catch (e) {
        if (e instanceof Error && e.name === "ZeruError")
            throw e;
        throw rpcError(e instanceof Error ? e.message : "setMetadata failed", { cause: e });
    }
}
/**
 * Read metadata from an agent. Returns the value as a UTF-8 string, or raw hex if not valid UTF-8.
 * Returns null if no metadata exists for the key.
 */
export async function getMetadata(config, agentId, key) {
    const provider = new JsonRpcProvider(config.rpcUrl);
    const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, provider);
    const raw = await registry.getMetadata(agentId, key);
    if (!raw || raw === "0x" || raw === "0x0" || raw.length <= 2)
        return null;
    try {
        return toUtf8String(raw);
    }
    catch {
        return raw; // Return raw hex if not valid UTF-8
    }
}
