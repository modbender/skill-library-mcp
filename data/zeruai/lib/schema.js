import { z } from "zod";
/** Service object — name + endpoint required, everything else optional and passed through */
const serviceSchema = z.object({
    name: z.string().min(1).max(128),
    endpoint: z.string().min(1).max(2048),
    version: z.string().max(64).optional(),
}).passthrough();
const registrationSchema = z.object({
    agentId: z.union([z.number(), z.string()]),
    agentRegistry: z.string().min(1).max(256),
});
/** Full ERC-8004 registration-v1 JSON (matches backend validation) */
export const agentRegistrationSchema = z.object({
    type: z.literal("https://eips.ethereum.org/EIPS/eip-8004#registration-v1"),
    name: z.string().min(1).max(256),
    description: z.string().max(2048),
    image: z.string().min(1).max(2048),
    services: z.array(serviceSchema).min(1).max(64),
    x402Support: z.boolean(),
    active: z.boolean(),
    registrations: z.array(registrationSchema).min(1).max(32),
    supportedTrust: z.array(z.string()).max(32).optional(),
    owner: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
}).passthrough();
/** Simplified input for createAgentURI — SDK fills in boilerplate */
export const createAgentURIInputSchema = z.object({
    name: z.string().min(1).max(256),
    description: z.string().max(2048),
    image: z.string().min(1).max(2048).optional(),
    services: z.array(serviceSchema).min(1).max(64),
    x402Support: z.boolean().optional(),
    active: z.boolean().optional(),
    supportedTrust: z.array(z.string()).max(32).optional(),
    owner: z.string().regex(/^0x[a-fA-F0-9]{40}$/).optional(),
});
export function parseCreateAgentURIInput(input) {
    const parsed = createAgentURIInputSchema.safeParse(input);
    if (!parsed.success) {
        const msg = parsed.error.errors.map((e) => `${e.path.join(".")}: ${e.message}`).join("; ");
        throw new Error(msg);
    }
    return parsed.data;
}
/** Build full AgentRegistration JSON from simplified input */
export function toAgentRegistration(input, registryAddress, chainId) {
    return {
        type: "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
        name: input.name,
        description: input.description,
        image: input.image || "https://placehold.co/512x512/1a1a2e/white?text=Agent",
        services: input.services,
        x402Support: input.x402Support ?? false,
        active: input.active ?? true,
        registrations: [{
                agentId: 0, // placeholder — updated after on-chain mint
                agentRegistry: `eip155:${chainId}:${registryAddress}`,
            }],
        supportedTrust: input.supportedTrust,
        owner: input.owner,
    };
}
