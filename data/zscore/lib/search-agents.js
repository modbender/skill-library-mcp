import { discoveryUrl } from "./config.js";
import { apiError } from "./errors.js";
/**
 * Search or list agents via the Discovery API.
 * Source defaults to config.source ("zeru").
 */
export async function searchAgents(config, params = {}) {
    const base = discoveryUrl(config);
    const endpoint = params.q ? `${base}/search` : `${base}/agents`;
    const url = new URL(endpoint);
    url.searchParams.set("source", config.source);
    if (params.chainId != null)
        url.searchParams.set("chainId", String(params.chainId));
    if (params.q)
        url.searchParams.set("q", params.q);
    if (params.serviceType)
        url.searchParams.set("serviceType", params.serviceType);
    if (params.limit != null)
        url.searchParams.set("limit", String(params.limit));
    if (params.offset != null)
        url.searchParams.set("offset", String(params.offset));
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
        throw apiError(`Discovery API error: ${res.status}`, res.status, body);
    }
    const data = (await res.json());
    return {
        results: Array.isArray(data.results) ? data.results : [],
        total: data.total ?? 0,
    };
}
