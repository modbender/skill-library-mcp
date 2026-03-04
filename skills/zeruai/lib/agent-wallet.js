import { Contract, JsonRpcProvider } from "ethers";
import { rpcError } from "./errors.js";
import { identityRegistryAbi } from "./abi.js";
const ZERO_ADDRESS = "0x0000000000000000000000000000000000000000";
/**
 * Set the agent wallet to a new address.
 * Requires an EIP-712 signature from the new wallet proving consent.
 *
 * @param config - Resolved SDK config
 * @param signer - The agent owner (sends the tx)
 * @param agentId - The agent's token ID
 * @param newWallet - Address to set as agent wallet
 * @param deadline - Unix timestamp deadline (must be within 5 min of block.timestamp)
 * @param walletSignature - EIP-712 signature from the new wallet
 */
export async function setAgentWallet(config, signer, agentId, newWallet, deadline, walletSignature) {
    try {
        const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, signer);
        const tx = await registry.setAgentWallet(agentId, newWallet, deadline, walletSignature);
        const receipt = await tx.wait();
        return receipt.hash;
    }
    catch (e) {
        if (e instanceof Error && e.name === "ZeruError")
            throw e;
        throw rpcError(e instanceof Error ? e.message : "setAgentWallet failed", { cause: e });
    }
}
/**
 * Clear the agent wallet (set to zero address). Only the owner/approved can call.
 */
export async function unsetAgentWallet(config, signer, agentId) {
    try {
        const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, signer);
        const tx = await registry.unsetAgentWallet(agentId);
        const receipt = await tx.wait();
        return receipt.hash;
    }
    catch (e) {
        if (e instanceof Error && e.name === "ZeruError")
            throw e;
        throw rpcError(e instanceof Error ? e.message : "unsetAgentWallet failed", { cause: e });
    }
}
/**
 * Read the current agent wallet address (returns zero address if unset).
 */
export async function getAgentWallet(config, agentId) {
    const provider = new JsonRpcProvider(config.rpcUrl);
    const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, provider);
    const wallet = await registry.getAgentWallet(agentId);
    return wallet === ZERO_ADDRESS ? null : wallet;
}
