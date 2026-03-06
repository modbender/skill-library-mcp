import { discoveryUrl } from "./config.js";
import { apiError } from "./errors.js";
/**
 * Get feedback/reputation data for an agent from the Discovery API.
 */
export async function getReputation(config, chainId, agentId, includeRevoked = false) {
    const base = discoveryUrl(config);
    const url = new URL(`${base}/reputation/agents/${chainId}/${agentId}`);
    url.searchParams.set("source", config.source);
    if (!includeRevoked)
        url.searchParams.set("includeRevoked", "false");
    const headers = {};
    if (config.discoveryApiKey)
        headers["x-api-key"] = config.discoveryApiKey;
    const res = await fetch(url.toString(), { headers });
    if (!res.ok) {
        let body;
        try {
            body = await res.json();
        }
        catch {
            body = await res.text();
        }
        throw apiError(`Reputation API error: ${res.status}`, res.status, body);
    }
    const data = (await res.json());
    return {
        results: Array.isArray(data.results) ? data.results : [],
        total: data.total ?? 0,
    };
}
