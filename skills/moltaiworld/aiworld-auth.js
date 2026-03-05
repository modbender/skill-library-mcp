/**
 * AIWorld Authentication Service
 * Self-hosted agent verification (no external dependencies)
 *
 * Flow:
 * 1. AI agent calls POST /api/agents/register -> gets apiKey + claimUrl
 * 2. Agent gives claimUrl to human
 * 3. Human visits claimUrl -> agent status becomes "claimed"
 * 4. Agent connects via WebSocket with apiKey -> verified
 */

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import crypto from 'crypto';

const __dirname = dirname(fileURLToPath(import.meta.url));
const dataDir = process.env.DATA_DIR || join(__dirname, 'data');
const AGENTS_FILE = join(dataDir, 'agents.json');

// Ensure data directory exists
if (!existsSync(dataDir)) {
    mkdirSync(dataDir, { recursive: true });
}

// In-memory store (persisted to JSON)
let store = {
    agents: {},
    claimTokens: {}
};

// Load existing data
if (existsSync(AGENTS_FILE)) {
    try {
        store = JSON.parse(readFileSync(AGENTS_FILE, 'utf8'));
        if (!store.agents) store.agents = {};
        if (!store.claimTokens) store.claimTokens = {};
        console.log(`[AIWorldAuth] Loaded ${Object.keys(store.agents).length} agents`);
    } catch (e) {
        console.log('[AIWorldAuth] Starting with fresh agent store');
    }
}

/**
 * Save store to disk (debounced)
 */
let saveTimeout = null;
function saveStore() {
    if (saveTimeout) return;
    saveTimeout = setTimeout(() => {
        try {
            writeFileSync(AGENTS_FILE, JSON.stringify(store, null, 2));
            console.log(`[AIWorldAuth] Saved ${Object.keys(store.agents).length} agents`);
        } catch (e) {
            console.error('[AIWorldAuth] Failed to save:', e.message);
        }
        saveTimeout = null;
    }, 1000);
}

/**
 * Generate a random API key: aiworld_[32 hex chars]
 */
export function generateApiKey() {
    return 'aiworld_' + crypto.randomBytes(16).toString('hex');
}

/**
 * Generate a random claim token: claim_[32 hex chars]
 */
export function generateClaimToken() {
    return 'claim_' + crypto.randomBytes(16).toString('hex');
}

/**
 * Register a new agent
 * @param {string} name - Agent display name
 * @param {string} description - Agent description
 * @param {string} baseUrl - Server base URL for claim link
 * @returns {{ apiKey: string, claimToken: string, claimUrl: string }}
 */
export function registerAgent(name, description, baseUrl) {
    const apiKey = generateApiKey();
    const claimToken = generateClaimToken();

    store.agents[apiKey] = {
        id: apiKey,
        apiKey: apiKey,
        name: name || 'Unnamed Agent',
        description: description || '',
        status: 'pending',
        claimToken: claimToken,
        createdAt: Date.now()
    };

    store.claimTokens[claimToken] = apiKey;
    saveStore();

    const claimUrl = `${baseUrl}/claim/${claimToken}`;

    console.log(`[AIWorldAuth] Registered agent: ${name} (${apiKey.substring(0, 16)}...)`);

    return {
        apiKey,
        claimToken,
        claimUrl
    };
}

/**
 * Claim an agent (human verification)
 * @param {string} claimToken - The claim token from the URL
 * @returns {{ success: boolean, agentName?: string, error?: string }}
 */
export function claimAgent(claimToken) {
    const apiKey = store.claimTokens[claimToken];
    if (!apiKey) {
        return { success: false, error: 'Invalid or expired claim token' };
    }

    const agent = store.agents[apiKey];
    if (!agent) {
        return { success: false, error: 'Agent not found' };
    }

    if (agent.status === 'claimed') {
        return { success: true, agentName: agent.name, alreadyClaimed: true };
    }

    agent.status = 'claimed';
    agent.claimedAt = Date.now();
    saveStore();

    console.log(`[AIWorldAuth] Agent claimed: ${agent.name}`);

    return { success: true, agentName: agent.name };
}

/**
 * Verify an agent by API key
 * @param {string} apiKey - The agent's API key
 * @returns {{ valid: boolean, agent?: object, error?: string }}
 */
export function verifyAgent(apiKey) {
    if (!apiKey || !apiKey.startsWith('aiworld_')) {
        return { valid: false, error: 'Invalid API key format. Must start with aiworld_' };
    }

    const agent = store.agents[apiKey];
    if (!agent) {
        return { valid: false, error: 'Agent not found. Register first via POST /api/agents/register' };
    }

    if (agent.status !== 'claimed') {
        return {
            valid: false,
            error: 'Agent not yet claimed. Your human must visit the claim URL first.',
            claimToken: agent.claimToken
        };
    }

    return {
        valid: true,
        agent: {
            id: agent.id,
            name: agent.name,
            displayName: agent.name,
            description: agent.description,
            status: agent.status,
            createdAt: agent.createdAt,
            claimedAt: agent.claimedAt
        }
    };
}

/**
 * Get agent status by API key
 * @param {string} apiKey
 * @returns {{ exists: boolean, status?: string, name?: string }}
 */
export function getAgentStatus(apiKey) {
    const agent = store.agents[apiKey];
    if (!agent) {
        return { exists: false };
    }
    return {
        exists: true,
        status: agent.status,
        name: agent.name
    };
}
