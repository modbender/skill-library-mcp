import { keccak256, toUtf8Bytes } from "ethers";
import canon from "canonicalize";
const canonicalize = typeof canon === "function" ? canon : canon.default;
import { agentUriApiUrl } from "./config.js";
import { apiError, validationError } from "./errors.js";
import { parseCreateAgentURIInput, toAgentRegistration } from "./schema.js";
const CREATE_PREFIX = "Zeru Agent URI create\n";
const UPDATE_PREFIX = "Zeru Agent URI update\n";
function canonicalStringify(obj) {
    if (obj === null || typeof obj !== "object")
        return JSON.stringify(obj);
    const out = canonicalize(obj);
    if (out === undefined)
        throw new Error("JCS canonicalize returned undefined");
    return out;
}
function hashBody(body) {
    return keccak256(toUtf8Bytes(canonicalStringify(body)));
}
async function signCreate(signer, body) {
    const timestamp = Date.now();
    const bodyHash = hashBody(body);
    const message = `${CREATE_PREFIX}${timestamp}\n${bodyHash}`;
    const signature = await signer.signMessage(message);
    return { signature, timestamp };
}
async function signUpdate(signer, id, body) {
    const timestamp = Date.now();
    const bodyHash = hashBody(body);
    const message = `${UPDATE_PREFIX}${id}\n${timestamp}\n${bodyHash}`;
    const signature = await signer.signMessage(message);
    return { signature, timestamp };
}
/**
 * Build Agent Registration JSON from input and POST to the Agent URI API.
 * Signs the request with EIP-191 (personal_sign) for authentication.
 * Returns the hosted agentURI that can be passed to registerWithFee().
 */
export async function createAgentURI(config, signer, input) {
    let parsed;
    try {
        parsed = parseCreateAgentURIInput(input);
    }
    catch (e) {
        throw validationError(e instanceof Error ? e.message : "Invalid input");
    }
    const json = toAgentRegistration(parsed, config.identityRegistryAddress, config.chainId);
    const url = agentUriApiUrl(config);
    const { signature, timestamp } = await signCreate(signer, json);
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "x-signature": signature,
            "x-timestamp": String(timestamp),
        },
        body: JSON.stringify(json),
    });
    if (!res.ok) {
        let body;
        try {
            body = await res.json();
        }
        catch {
            body = await res.text();
        }
        throw apiError(`Agent URI API error: ${res.status} ${res.statusText}`, res.status, body);
    }
    const data = (await res.json());
    if (!data.agentURI || !data.id) {
        throw apiError("Agent URI API did not return id/agentURI", res.status, data);
    }
    return { id: data.id, agentURI: data.agentURI, json };
}
/**
 * Update an existing agent URI document (e.g. to set the real agentId after minting).
 * Requires signature from the original owner.
 */
export async function updateAgentURI(config, signer, documentId, json) {
    const url = `${agentUriApiUrl(config)}/${documentId}`;
    const { signature, timestamp } = await signUpdate(signer, documentId, json);
    const res = await fetch(url, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
            "x-signature": signature,
            "x-timestamp": String(timestamp),
        },
        body: JSON.stringify(json),
    });
    if (!res.ok) {
        let body;
        try {
            body = await res.json();
        }
        catch {
            body = await res.text();
        }
        throw apiError(`Agent URI API update error: ${res.status}`, res.status, body);
    }
    return (await res.json());
}
