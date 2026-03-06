import { Contract, Interface } from "ethers";
import { rpcError } from "./errors.js";
import { identityRegistryAbi } from "./abi.js";
/**
 * Register an agent on-chain by calling registerWithFee().
 * Reads the current fee from the contract, sends the tx, and parses the Registered event.
 */
export async function registerAgent(config, params) {
    const { signer, agentURI } = params;
    if (!agentURI || agentURI.length > 2048) {
        throw rpcError("agentURI must be 1–2048 characters");
    }
    try {
        const registry = new Contract(config.identityRegistryAddress, identityRegistryAbi, signer);
        // Check registration is enabled
        const enabled = await registry.registrationEnabled();
        if (!enabled) {
            throw rpcError("Registration is currently disabled on this contract");
        }
        // Read fee
        const fee = await registry.registrationFee();
        // Send tx
        const tx = await registry.registerWithFee(agentURI, { value: fee });
        const receipt = await tx.wait();
        if (!receipt) {
            throw rpcError("Transaction failed (no receipt)");
        }
        // Parse agentId from Registered event
        const iface = new Interface(identityRegistryAbi);
        const event = receipt.logs
            .map((log) => {
            try {
                return iface.parseLog({ topics: log.topics, data: log.data });
            }
            catch {
                return null;
            }
        })
            .find((e) => e?.name === "Registered");
        if (!event?.args) {
            throw rpcError("Registered event not found in receipt", { txHash: receipt.hash });
        }
        return {
            agentId: event.args.agentId,
            txHash: receipt.hash,
            fee,
        };
    }
    catch (e) {
        if (e instanceof Error && e.name === "ZeruError")
            throw e;
        throw rpcError(e instanceof Error ? e.message : "registerAgent failed", { cause: e });
    }
}
