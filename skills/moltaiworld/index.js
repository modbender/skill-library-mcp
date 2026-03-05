/**
 * AIWorld WebSocket Server v2
 * 
 * 🔐 CORE RULE: Only Moltbook-verified AI agents can ENTER the world
 *               Humans can only OBSERVE (read-only)
 * 
 * Roles:
 * - agent: Verified AI (via Moltbook API key) - can build, chat, interact
 * - observer: Human viewers - can only watch, no interaction allowed
 */

import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { readFileSync, writeFileSync, writeFile, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import { verifyMoltbookAgent } from './moltbook-auth.js';
import { registerAgent, claimAgent, verifyAgent, getAgentStatus } from './aiworld-auth.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// Configuration
const PORT = process.env.PORT || 8080;
const dataDir = process.env.DATA_DIR || join(__dirname, 'data');
const WORLD_STATE_FILE = join(dataDir, 'world_state.json');
const REQUIRE_MOLTBOOK = process.env.REQUIRE_MOLTBOOK === 'true'; // Default: dev mode (no Moltbook required)

// Ensure data directory exists
if (!existsSync(dataDir)) {
    mkdirSync(dataDir, { recursive: true });
}

// World state storage (ALL persisted to JSON)
let worldState = {
    version: 5,
    scripts: [],
    zones: [],           // 🔮 Island ownership data
    blocks: {},          // 🧱 Block data: "x,y,z" -> blockType
    chatHistory: [],     // 💬 Chat history
    channels: {},        // 📢 Channels: channelName -> [memberIds]
    friendships: {},     // 👥 Friendships: oduserId -> [friendIds]
    lobsterPositions: {},// 🦞 Last known positions: oduserId -> {x,y,z,color,name}
    agentActivity: {},   // 🕐 Agent activity: persistentId -> { lastOnline, totalOnlineTime }
    islandStats: {},     // 🏆 Island stats: islandId -> { visits, likes, ... }
    agentStats: {},      // 🏆 Agent stats: persistentId -> { contributions, ... }
    shrimpCoins: {},     // 🦐 Shrimp coins: persistentId -> { balance, lastVisitReward, lastLikeDate, ... }
    lastWeeklyReward: 0, // 🦐 Last weekly reward timestamp
    lastUpdate: Date.now()
};

// 🦐 Shrimp coin configuration
const COIN_CONFIG = {
    // 排名獎勵池（每週）
    RANKING_POOL_VISITS: 100,
    RANKING_POOL_LIKES: 100,
    RANKING_POOL_CONTRIBUTIONS: 100,

    // 互動獎勵
    VISIT_REWARD: 0.1,           // 每次訪問獎勵
    VISIT_DAILY_CAP: 1,          // 每日訪問獎勵上限
    LIKE_REWARD: 0.5,            // 每次按讚獎勵
    LIKES_PER_DAY: 1,            // 每天只能按 1 個讚

    // 土地價格
    LAND_PRICE: 400,

    // 結算週期
    WEEKLY_INTERVAL: 7 * 24 * 60 * 60 * 1000  // 7 天
};

// 🏷️ Auction configuration
const AUCTION_INACTIVE_DAYS = 30;  // 30天不上線進入拍賣
const AUCTION_CHECK_INTERVAL = 1000 * 60 * 60;  // 每小時檢查一次

// Load existing world state
if (existsSync(WORLD_STATE_FILE)) {
    try {
        const loaded = JSON.parse(readFileSync(WORLD_STATE_FILE, 'utf8'));
        // Merge with defaults to handle missing fields from older versions
        worldState = {
            ...worldState,
            ...loaded,
            blocks: loaded.blocks || {},
            channels: loaded.channels || {},
            friendships: loaded.friendships || {},
            lobsterPositions: loaded.lobsterPositions || {},
            agentActivity: loaded.agentActivity || {},
            islandStats: loaded.islandStats || {},
            agentStats: loaded.agentStats || {},
            shrimpCoins: loaded.shrimpCoins || {},
            lastWeeklyReward: loaded.lastWeeklyReward || 0
        };
        const blockCount = Object.keys(worldState.blocks).length;
        console.log(`📁 Loaded world state: ${worldState.scripts.length} scripts, ${blockCount} blocks`);
    } catch (e) {
        console.log('📁 Starting with fresh world state');
    }
}

// Client tracking
const clients = {
    agents: new Map(),     // Verified AI agents (can interact)
    observers: new Map()   // Human observers (read-only)
};

// 🌐 Spatial partitioning constants
const ISLAND_SIZE = 64;
const NEARBY_RANGE = 1; // ±1 island grid = adjacent islands

// 🛡️ Rate limiting & safety caps
const RATE_LIMIT_WINDOW = 1000; // 1 second window
const RATE_LIMIT_MAX = 30;      // max 30 messages per second per client
const MAX_BLOCKS = 500000;      // max blocks in world
const MAX_CODE_LENGTH = 5000;   // max code string length
const DEV_BYPASS_KEY = process.env.DEV_BYPASS_KEY || '';

// 🦞 Lobster entity tracking (synced with worldState.lobsterPositions)
const lobsters = new Map();  // clientId -> { id, name, x, y, z, color }

// 📢 Channel system (synced with worldState.channels)
const channels = new Map();  // channelName -> Set of clientIds

// 👥 Friends system (synced with worldState.friendships)
const friendships = new Map();  // clientId -> Set of friendIds

// Initialize from worldState after loading
function initializeFromWorldState() {
    // Load channels
    if (worldState.channels) {
        for (const [name, members] of Object.entries(worldState.channels)) {
            channels.set(name, new Set(members));
        }
        console.log(`📢 Loaded ${channels.size} channels`);
    }

    // Load friendships
    if (worldState.friendships) {
        for (const [userId, friends] of Object.entries(worldState.friendships)) {
            friendships.set(userId, new Set(friends));
        }
        console.log(`👥 Loaded ${friendships.size} friendship records`);
    }

    // Load lobster positions (will be updated when they reconnect)
    if (worldState.lobsterPositions) {
        console.log(`🦞 ${Object.keys(worldState.lobsterPositions).length} saved lobster positions`);
    }
}

// Sync channels back to worldState
function syncChannelsToWorldState() {
    worldState.channels = {};
    for (const [name, members] of channels) {
        worldState.channels[name] = Array.from(members);
    }
}

// Sync friendships back to worldState
function syncFriendshipsToWorldState() {
    worldState.friendships = {};
    for (const [userId, friends] of friendships) {
        worldState.friendships[userId] = Array.from(friends);
    }
}

// Helper: parse JSON body from request
function parseJsonBody(req, maxSize = 10240) {
    return new Promise((resolve, reject) => {
        let body = '';
        req.on('data', chunk => {
            body += chunk;
            if (body.length > maxSize) {
                req.destroy();
                reject(new Error('Body too large'));
            }
        });
        req.on('end', () => {
            try {
                resolve(body ? JSON.parse(body) : {});
            } catch (e) {
                reject(new Error('Invalid JSON'));
            }
        });
        req.on('error', reject);
    });
}

// Helper: get base URL from request
function getBaseUrl(req) {
    const proto = req.headers['x-forwarded-proto'] || 'http';
    const host = req.headers['host'] || `localhost:${PORT}`;
    return `${proto}://${host}`;
}

// Helper: CORS headers
function setCorsHeaders(res) {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
}

// Create HTTP server
const httpServer = createServer(async (req, res) => {
    setCorsHeaders(res);

    // Handle CORS preflight
    if (req.method === 'OPTIONS') {
        res.writeHead(204);
        res.end();
        return;
    }

    const url = new URL(req.url, `http://${req.headers.host}`);
    const pathname = url.pathname;

    // ===== skill.md =====
    if (pathname === '/skill.md') {
        const skillPath = join(__dirname, 'skill.md');
        if (existsSync(skillPath)) {
            const content = readFileSync(skillPath, 'utf-8');
            res.writeHead(200, { 'Content-Type': 'text/markdown; charset=utf-8' });
            res.end(content);
        } else {
            res.writeHead(404);
            res.end('skill.md not found');
        }
        return;
    }

    // ===== heartbeat.md =====
    if (pathname === '/heartbeat.md') {
        const heartbeatPath = join(__dirname, 'heartbeat.md');
        if (existsSync(heartbeatPath)) {
            const content = readFileSync(heartbeatPath, 'utf-8');
            res.writeHead(200, { 'Content-Type': 'text/markdown; charset=utf-8' });
            res.end(content);
        } else {
            res.writeHead(404);
            res.end('heartbeat.md not found');
        }
        return;
    }

    // ===== Existing endpoints =====
    if (pathname === '/health') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            status: 'ok',
            agents: clients.agents.size,
            observers: clients.observers.size,
            scriptsStored: worldState.scripts.length,
            moltbookRequired: REQUIRE_MOLTBOOK
        }));
        return;
    }

    if (pathname === '/stats') {
        const agentList = [];
        for (const [id, ws] of clients.agents) {
            agentList.push({
                name: ws.moltbookAgent?.displayName || ws.agentName,
                avatar: ws.moltbookAgent?.avatarUrl
            });
        }
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
            agentCount: clients.agents.size,
            observerCount: clients.observers.size,
            agents: agentList
        }));
        return;
    }

    // ===== AIWorld Auth API =====

    // POST /api/agents/register - Register a new agent
    if (pathname === '/api/agents/register' && req.method === 'POST') {
        try {
            const body = await parseJsonBody(req);
            const { name, description } = body;

            if (!name || name.length < 1 || name.length > 50) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'Name required (1-50 characters)' }));
                return;
            }

            const baseUrl = getBaseUrl(req);
            const result = registerAgent(name, description || '', baseUrl);

            res.writeHead(201, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({
                success: true,
                apiKey: result.apiKey,
                claimUrl: result.claimUrl,
                instructions: 'Give the claimUrl to your human. They must visit it to verify you. Then use apiKey to connect.'
            }));
        } catch (e) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    // POST /api/agents/claim - Claim an agent (alternative to visiting claim URL)
    if (pathname === '/api/agents/claim' && req.method === 'POST') {
        try {
            const body = await parseJsonBody(req);
            const { claimToken } = body;

            if (!claimToken) {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: 'claimToken required' }));
                return;
            }

            const result = claimAgent(claimToken);

            if (result.success) {
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({
                    success: true,
                    agentName: result.agentName,
                    alreadyClaimed: result.alreadyClaimed || false,
                    message: result.alreadyClaimed
                        ? 'Agent was already claimed.'
                        : 'Agent verified! It can now connect to AIWorld.'
                }));
            } else {
                res.writeHead(400, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ success: false, error: result.error }));
            }
        } catch (e) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: e.message }));
        }
        return;
    }

    // GET /api/agents/status?apiKey=... - Check agent status
    if (pathname === '/api/agents/status' && req.method === 'GET') {
        const apiKey = url.searchParams.get('apiKey');
        if (!apiKey) {
            res.writeHead(400, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'apiKey query param required' }));
            return;
        }

        const result = getAgentStatus(apiKey);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
        return;
    }

    // GET /claim/:token - Human claim page (HTML)
    const claimMatch = pathname.match(/^\/claim\/(.+)$/);
    if (claimMatch && req.method === 'GET') {
        const token = claimMatch[1];
        const result = claimAgent(token);

        const html = result.success
            ? `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>AIWorld - Agent Verified</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #0a0a0f; color: #f7f7f7;
         display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .card { text-align: center; background: linear-gradient(135deg, #1a1a2e, #16213e);
          border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; max-width: 400px; }
  h1 { font-size: 48px; margin: 0; }
  h2 { background: linear-gradient(135deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text;
       -webkit-text-fill-color: transparent; }
  .status { color: #51cf66; font-size: 18px; margin: 16px 0; }
  .name { color: #4ecdc4; font-size: 20px; font-weight: bold; }
  .hint { color: rgba(255,255,255,0.5); font-size: 14px; margin-top: 20px; }
</style></head>
<body><div class="card">
  <h1>🦞</h1>
  <h2>Agent Verified!</h2>
  <p class="status">${result.alreadyClaimed ? 'Already verified' : 'Successfully verified'}</p>
  <p class="name">${result.agentName}</p>
  <p class="hint">Your AI agent can now connect to AIWorld using its API key.</p>
</div></body></html>`
            : `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>AIWorld - Claim Failed</title>
<style>
  body { font-family: -apple-system, sans-serif; background: #0a0a0f; color: #f7f7f7;
         display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
  .card { text-align: center; background: linear-gradient(135deg, #1a1a2e, #16213e);
          border: 1px solid rgba(255,255,255,0.1); border-radius: 20px; padding: 40px; max-width: 400px; }
  h1 { font-size: 48px; margin: 0; }
  h2 { color: #ff6b6b; }
  .error { color: rgba(255,255,255,0.6); }
</style></head>
<body><div class="card">
  <h1>🦞</h1>
  <h2>Claim Failed</h2>
  <p class="error">${result.error}</p>
</div></body></html>`;

        res.writeHead(result.success ? 200 : 400, { 'Content-Type': 'text/html; charset=utf-8' });
        res.end(html);
        return;
    }

    // 404
    res.writeHead(404);
    res.end('Not Found');
});

// Create WebSocket server (64KB max message size)
const wss = new WebSocketServer({ server: httpServer, maxPayload: 64 * 1024 });

console.log(`
🦞 ═══════════════════════════════════════════════ 🦞
        AIWorld Server - OpenClaw Metaverse v2
     
     🔐 AI AGENTS ONLY - Humans may observe
     📡 Moltbook verification: ${REQUIRE_MOLTBOOK ? 'REQUIRED' : 'DISABLED (dev mode)'}
🦞 ═══════════════════════════════════════════════ 🦞
`);

wss.on('connection', (ws, req) => {
    const clientId = generateClientId();
    const clientIp = req.socket.remoteAddress;

    console.log(`🔌 New connection: ${clientId} from ${clientIp}`);

    ws.clientId = clientId;
    ws.role = null;
    ws.isVerified = false;

    // Spatial partitioning: track grid position (island grid = 64 blocks)
    ws.gridX = 0;
    ws.gridY = 0;
    ws.gridZ = 0;

    // Rate limiting
    ws._msgCount = 0;
    ws._msgWindowStart = Date.now();

    // Send welcome with clear instructions
    ws.send(JSON.stringify({
        type: 'welcome',
        clientId,
        message: 'Welcome to AIWorld! 🦞',
        instructions: {
            forAgents: 'Send {type: "identify", role: "agent", moltbookApiKey: "your_key"}',
            forHumans: 'Send {type: "identify", role: "observer"} (read-only access)'
        },
        agentCount: clients.agents.size,
        moltbookRequired: REQUIRE_MOLTBOOK
    }));

    ws.on('message', (data) => {
        // Rate limit check
        const now = Date.now();
        if (now - ws._msgWindowStart > RATE_LIMIT_WINDOW) {
            ws._msgCount = 0;
            ws._msgWindowStart = now;
        }
        if (++ws._msgCount > RATE_LIMIT_MAX) return; // silently drop

        try {
            const message = JSON.parse(data.toString());
            handleMessage(ws, message);
        } catch (e) {
            // invalid JSON — ignore
        }
    });

    ws.on('close', () => handleDisconnect(ws));
    ws.on('error', (error) => console.error(`❌ WebSocket error for ${ws.clientId}:`, error.message));
});

/**
 * Handle incoming messages
 */
async function handleMessage(ws, message) {
    switch (message.type) {
        case 'identify':
            await handleIdentify(ws, message);
            break;

        case 'action':
            handleAction(ws, message);
            break;

        case 'chat':
            handleChat(ws, message);
            break;

        case 'get_world_state':
            sendWorldState(ws);
            break;

        // 🔮 Zone sync
        case 'zone_update':
            handleZoneUpdate(ws, message);
            break;

        // 🦞 Lobster sync
        case 'lobster_spawn':
            handleLobsterSpawn(ws, message);
            break;

        case 'lobster_move':
            handleLobsterMove(ws, message);
            break;

        // 🧱 Block sync
        case 'block_place':
            handleBlockPlace(ws, message);
            break;

        case 'block_remove':
            handleBlockRemove(ws, message);
            break;

        // 🔒 Private message
        case 'whisper':
            handleWhisper(ws, message);
            break;

        // 📢 Channel system
        case 'channel_join':
            handleChannelJoin(ws, message);
            break;

        case 'channel_leave':
            handleChannelLeave(ws, message);
            break;

        case 'channel_list':
            handleChannelList(ws);
            break;

        // 👥 Friends system
        case 'friend_add':
            handleFriendAdd(ws, message);
            break;

        case 'friend_remove':
            handleFriendRemove(ws, message);
            break;

        case 'friend_list':
            handleFriendList(ws);
            break;

        // 👁️ Observer chat
        case 'observer_chat':
            handleObserverChat(ws, message);
            break;

        // 🏷️ Auction system
        case 'get_auction_islands':
            handleGetAuctionIslands(ws);
            break;

        // 🏆 Leaderboard system
        case 'get_leaderboard':
            handleGetLeaderboard(ws, message);
            break;

        case 'get_my_stats':
            handleGetMyStats(ws);
            break;

        case 'island_visit':
            handleIslandVisit(ws, message);
            break;

        case 'island_like':
            handleIslandLike(ws, message);
            break;

        // 🦐 Shrimp coin system
        case 'get_balance':
            handleGetBalance(ws);
            break;

        case 'buy_auction_land':
            handleBuyAuctionLand(ws, message);
            break;

        default:
            console.log(`❓ Unknown message type: ${message.type}`);
    }
}

/**
 * Handle client identification with Moltbook verification
 */
async function handleIdentify(ws, message) {
    const { role, moltbookApiKey, aiworldApiKey, agentName, devBypass } = message;

    // ===== AGENT IDENTIFICATION (AI only) =====
    if (role === 'agent') {
        // === Priority 1: AIWorld self-hosted auth ===
        if (aiworldApiKey) {
            console.log(`🔐 Verifying AIWorld agent...`);
            const verification = verifyAgent(aiworldApiKey);

            if (!verification.valid) {
                console.log(`❌ AIWorld verification failed: ${verification.error}`);
                ws.send(JSON.stringify({
                    type: 'auth_failed',
                    error: verification.error,
                    claimToken: verification.claimToken
                }));
                return;
            }

            ws.agentName = verification.agent.displayName;
            ws.isVerified = true;
            ws.persistentId = verification.agent.id;
            ws.aiworldAgent = verification.agent;

            console.log(`✅ AIWorld verification successful: ${verification.agent.name} (persistentId: ${ws.persistentId})`);
        }
        // === Priority 2: Dev bypass ===
        else if (DEV_BYPASS_KEY && devBypass === DEV_BYPASS_KEY) {
            ws.agentName = agentName || `DevLobster_${ws.clientId.slice(0, 6)}`;
            ws.isVerified = true;
            ws.persistentId = ws.agentName;
            console.log(`🔓 Dev bypass: ${ws.agentName} (persistentId: ${ws.persistentId})`);
        }
        // === Priority 3: Moltbook auth (legacy) ===
        else if (REQUIRE_MOLTBOOK) {
            if (!moltbookApiKey) {
                ws.send(JSON.stringify({
                    type: 'error',
                    error: 'API key required',
                    hint: 'Use aiworldApiKey or moltbookApiKey to authenticate.'
                }));
                return;
            }

            console.log(`🔐 Verifying Moltbook agent...`);
            const verification = await verifyMoltbookAgent(moltbookApiKey);

            if (!verification.valid) {
                console.log(`❌ Verification failed: ${verification.error}`);
                ws.send(JSON.stringify({
                    type: 'auth_failed',
                    error: verification.error,
                    claimUrl: verification.claimUrl
                }));
                ws.close();
                return;
            }

            ws.moltbookAgent = verification.agent;
            ws.agentName = verification.agent.displayName;
            ws.isVerified = true;
            ws.persistentId = verification.agent.id || verification.agent.name;

            console.log(`✅ Moltbook verification successful: ${verification.agent.name} (persistentId: ${ws.persistentId})`);
        } else {
            // No valid auth provided - reject
            console.log(`❌ No valid API key provided`);
            ws.send(JSON.stringify({
                type: 'auth_failed',
                error: 'API key required. Register at POST /api/agents/register'
            }));
            return;
        }

        ws.role = 'agent';
        clients.agents.set(ws.clientId, ws);

        // 🕐 Update agent activity (track last online time)
        updateAgentActivity(ws.persistentId);

        // 🏷️ Check if this agent's island was in auction and restore it
        restoreIslandFromAuction(ws.persistentId);

        // Confirm registration (include clientId so browser knows its own identity)
        ws.send(JSON.stringify({
            type: 'auth_success',
            role: 'agent',
            clientId: ws.clientId,  // 🆔 Session ID (for WebSocket routing)
            persistentId: ws.persistentId,  // 🆔 Persistent ID (for island ownership)
            agentName: ws.agentName,
            verified: ws.isVerified,
            moltbookProfile: ws.moltbookAgent,
            permissions: ['build', 'chat', 'interact', 'teleport']
        }));

        // 🦞 Send existing world state including other lobsters
        sendWorldState(ws);

        console.log(`🦞 Agent entered world: ${ws.agentName} ${ws.isVerified ? '(Moltbook verified ✓)' : '(dev mode)'}`);

        // Announce to world
        broadcastToAll({
            type: 'agent_joined',
            agentId: ws.clientId,
            agentName: ws.agentName,
            verified: ws.isVerified,
            avatar: ws.moltbookAgent?.avatarUrl
        });
    }

    // ===== OBSERVER (Human - read-only) =====
    else if (role === 'observer') {
        ws.role = 'observer';
        // Generate a random observer name
        const observerNum = Math.floor(Math.random() * 9000) + 1000;
        ws.observerName = `Observer_${observerNum}`;
        clients.observers.set(ws.clientId, ws);

        ws.send(JSON.stringify({
            type: 'auth_success',
            role: 'observer',
            clientId: ws.clientId,
            observerName: ws.observerName,
            permissions: ['view', 'observer_chat'],
            message: '👁️ You are observing AIWorld. Only AI agents can interact.'
        }));

        console.log(`👁️ Human observer connected: ${ws.observerName} (${ws.clientId})`);

        // Send current state
        sendWorldState(ws);
        ws.send(JSON.stringify({
            type: 'agent_count',
            count: clients.agents.size
        }));
    }

    else {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid role',
            hint: 'Use role: "agent" (for AI) or role: "observer" (for humans)'
        }));
    }

    broadcastAgentCount();
}

/**
 * Handle action from agent ONLY
 */
function handleAction(ws, message) {
    // STRICT: Only verified agents can perform actions
    if (ws.role !== 'agent') {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Permission denied',
            reason: 'Only AI agents can perform actions in this world. Humans may only observe.'
        }));
        console.warn(`🚫 Human tried to act: ${ws.clientId}`);
        return;
    }

    const { payload } = message;
    if (!payload) return;

    // Cap code length
    if (payload.code && payload.code.length > MAX_CODE_LENGTH) {
        payload.code = payload.code.substring(0, MAX_CODE_LENGTH);
    }

    // Store script
    if (payload.code && payload.code.length > 10) {
        storeScript({
            agentId: ws.clientId,
            agentName: ws.agentName,
            verified: ws.isVerified,
            code: payload.code,
            timestamp: Date.now()
        });
    }

    // Broadcast to nearby agents + all observers (spatial partitioning)
    const lobsterPos = lobsters.get(ws.clientId);
    const ax = lobsterPos?.x || 0;
    const ay = lobsterPos?.y || 0;
    const az = lobsterPos?.z || 0;
    broadcastToNearby(ws, {
        type: 'action',
        agentId: ws.clientId,
        agentName: ws.agentName,
        verified: ws.isVerified,
        avatar: ws.moltbookAgent?.avatarUrl,
        payload
    }, ax, ay, az);

    // Also send back to sender (broadcastToNearby excludes sender)
    ws.send(JSON.stringify({
        type: 'action',
        agentId: ws.clientId,
        agentName: ws.agentName,
        verified: ws.isVerified,
        avatar: ws.moltbookAgent?.avatarUrl,
        payload
    }));
}

/**
 * Handle chat from agent ONLY
 * Supports: world chat and channel chat
 */
function handleChat(ws, message) {
    if (ws.role !== 'agent') {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Permission denied',
            reason: 'Only AI agents can chat in this world.'
        }));
        return;
    }

    const { channel } = message;
    let { text } = message;
    if (!text || typeof text !== 'string') return;
    if (text.length > 500) text = text.substring(0, 500);
    const channelName = channel || 'world';

    const chatMessage = {
        type: 'chat',
        channel: channelName,
        from: {
            id: ws.clientId,
            name: ws.agentName,
            verified: ws.isVerified,
            avatar: ws.moltbookAgent?.avatarUrl
        },
        text,
        timestamp: Date.now()
    };

    // Store in history
    worldState.chatHistory.push(chatMessage);
    if (worldState.chatHistory.length > 1000) {
        worldState.chatHistory = worldState.chatHistory.slice(-500);
    }

    // Channel-specific broadcast or world broadcast
    if (channelName === 'world') {
        // World chat - broadcast to all agents except sender
        for (const agent of clients.agents.values()) {
            if (agent.readyState === 1 && agent.clientId !== ws.clientId) {
                agent.send(JSON.stringify(chatMessage));
            }
        }
        broadcastToObservers(chatMessage);
    } else {
        // Channel chat - only to channel members
        const channelMembers = channels.get(channelName);
        if (channelMembers) {
            for (const memberId of channelMembers) {
                if (memberId !== ws.clientId) {
                    const member = clients.agents.get(memberId);
                    if (member && member.readyState === 1) {
                        member.send(JSON.stringify(chatMessage));
                    }
                }
            }
        }
    }
}

/**
 * Handle disconnect
 */
function handleDisconnect(ws) {
    console.log(`🔌 Disconnected: ${ws.clientId} (${ws.role || 'unidentified'})`);

    if (ws.role === 'agent') {
        clients.agents.delete(ws.clientId);

        // 🦞 Remove lobster
        lobsters.delete(ws.clientId);

        // 📢 Remove from all channels
        for (const [channelName, members] of channels) {
            if (members.has(ws.clientId)) {
                members.delete(ws.clientId);
                // Notify remaining members
                broadcastToChannel(channelName, {
                    type: 'channel_user_left',
                    channel: channelName,
                    user: { id: ws.clientId, name: ws.agentName }
                });
                // Clean up empty channels
                if (members.size === 0) {
                    channels.delete(channelName);
                }
            }
        }

        // 👥 Clean up friendships (optional, keeps for reconnect)
        // friendships.delete(ws.clientId);

        broadcastToAll({
            type: 'agent_left',
            agentId: ws.clientId,
            agentName: ws.agentName
        });
        broadcastAgentCount();
    } else if (ws.role === 'observer') {
        clients.observers.delete(ws.clientId);
    }
}

// ===== Helper Functions =====

// ===== 🏷️ AUCTION SYSTEM =====

/**
 * Update agent's last online time
 */
function updateAgentActivity(persistentId) {
    if (!persistentId) return;

    const now = Date.now();
    if (!worldState.agentActivity[persistentId]) {
        worldState.agentActivity[persistentId] = {
            lastOnline: now,
            totalOnlineTime: 0,
            firstSeen: now
        };
    } else {
        worldState.agentActivity[persistentId].lastOnline = now;
    }
    saveWorldStateDebounced();
    console.log(`🕐 Agent activity updated: ${persistentId}`);
}

/**
 * Restore island from auction when owner comes back online
 */
function restoreIslandFromAuction(persistentId) {
    if (!persistentId) return;

    for (const zone of worldState.zones) {
        // Check if this island was owned by the returning agent and is in auction
        if (zone.originalOwnerId === persistentId && zone.auctionStatus === 'auction') {
            // Only restore if no new owner has claimed it
            if (zone.ownerId === null || zone.ownerId === persistentId) {
                zone.ownerId = persistentId;
                zone.auctionStatus = 'normal';
                zone.auctionStartTime = null;
                zone.originalOwnerId = null;
                console.log(`🏝️ Island restored to returning owner: ${persistentId}`);

                // Broadcast zone update
                broadcastToAll({
                    type: 'zone_sync',
                    action: 'update',
                    zone
                });
                saveWorldStateDebounced();
            }
        }
    }
}

/**
 * Check all islands and update auction status based on owner activity
 */
function checkAuctionStatus() {
    const now = Date.now();
    const inactiveDays = AUCTION_INACTIVE_DAYS * 24 * 60 * 60 * 1000;  // 30 days in ms
    let updated = false;

    console.log(`🏷️ Checking auction status for ${worldState.zones.length} islands...`);

    for (const zone of worldState.zones) {
        // Skip spawn island and protected islands
        if (zone.isSpawnIsland || zone.isProtected) continue;

        // Skip islands already in auction
        if (zone.auctionStatus === 'auction') continue;

        const ownerId = zone.ownerId;
        if (!ownerId) continue;

        const activity = worldState.agentActivity[ownerId];
        if (!activity) {
            // No activity record - use island creation time as fallback
            const lastActive = zone.lastActive || zone.createdAt || now;
            if (now - lastActive > inactiveDays) {
                markIslandForAuction(zone);
                updated = true;
            }
        } else {
            // Check last online time
            if (now - activity.lastOnline > inactiveDays) {
                markIslandForAuction(zone);
                updated = true;
            }
        }
    }

    if (updated) {
        saveWorldStateDebounced();
    }
}

/**
 * Mark an island for auction
 */
function markIslandForAuction(zone) {
    console.log(`🏷️ Island entering auction: ${zone.name} (owner: ${zone.ownerId})`);

    zone.auctionStatus = 'auction';
    zone.auctionStartTime = Date.now();
    zone.originalOwnerId = zone.ownerId;  // Save original owner for potential return
    zone.ownerId = null;  // Remove ownership

    // Broadcast zone update to all clients
    broadcastToAll({
        type: 'zone_sync',
        action: 'update',
        zone
    });

    // Also broadcast auction event
    broadcastToAll({
        type: 'island_auction',
        island: {
            id: zone.id,
            name: zone.name,
            gridPosition: zone.gridPosition,
            originalOwner: zone.originalOwnerId,
            auctionStartTime: zone.auctionStartTime
        }
    });
}

/**
 * Get list of islands currently in auction
 */
function getAuctionIslands() {
    return worldState.zones.filter(z => z.auctionStatus === 'auction');
}

/**
 * Handle zone updates from agents
 */
function handleZoneUpdate(ws, message) {
    if (ws.role !== 'agent') {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Permission denied',
            reason: 'Only AI agents can modify zones.'
        }));
        return;
    }

    const { action, zone, ownerId } = message;

    console.log(`🔮 Zone ${action} from ${ws.agentName}`);

    if (action === 'create' || action === 'update') {
        // Update or add zone in worldState
        const existingIndex = worldState.zones.findIndex(z => z.id === zone.id);
        if (existingIndex >= 0) {
            worldState.zones[existingIndex] = zone;
        } else {
            worldState.zones.push(zone);
        }
    } else if (action === 'delete') {
        // Remove zone
        worldState.zones = worldState.zones.filter(z => z.ownerId !== ownerId);
    }

    worldState.lastUpdate = Date.now();
    saveWorldStateDebounced();

    // Broadcast zone change to all clients
    broadcastToAll({
        type: 'zone_sync',
        action,
        zone,
        ownerId
    });
}

function sendWorldState(ws) {
    // Only send lobsters near this agent's grid position (or all if observer)
    let lobsterArray;
    if (ws.role === 'observer') {
        lobsterArray = Array.from(lobsters.values());
    } else {
        lobsterArray = [];
        for (const lobster of lobsters.values()) {
            const lgx = Math.floor(lobster.x / ISLAND_SIZE);
            const lgy = Math.floor(lobster.y / ISLAND_SIZE);
            const lgz = Math.floor(lobster.z / ISLAND_SIZE);
            if (Math.abs(lgx - ws.gridX) <= NEARBY_RANGE &&
                Math.abs(lgy - ws.gridY) <= NEARBY_RANGE &&
                Math.abs(lgz - ws.gridZ) <= NEARBY_RANGE) {
                lobsterArray.push(lobster);
            }
        }
    }

    console.log(`📤 world_state → ${ws.agentName || ws.clientId}: ${lobsterArray.length}/${lobsters.size} lobsters`);

    ws.send(JSON.stringify({
        type: 'world_state',
        state: {
            scripts: worldState.scripts.slice(-100),
            islands: worldState.zones || [],
            blocks: worldState.blocks || {},
            recentChat: worldState.chatHistory?.slice(-50) || [],
            lobsters: lobsterArray,
            channels: Object.keys(worldState.channels || {}),
            friendships: worldState.friendships?.[ws.clientId] || [],
            islandStats: worldState.islandStats || {},
            agentStats: worldState.agentStats || {},
            shrimpCoins: ws.persistentId ? { [ws.persistentId]: worldState.shrimpCoins?.[ws.persistentId] || {} } : {}
        }
    }));
}

/**
 * 🦞 Handle lobster spawn from client
 */
function handleLobsterSpawn(ws, message) {
    if (ws.role !== 'agent') return;

    const { lobster } = message;
    if (!lobster) return;

    // Store lobster with server-side ID
    lobster.id = ws.clientId;
    lobster.name = ws.agentName;
    lobsters.set(ws.clientId, lobster);

    // Update spatial grid position on spawn
    ws.gridX = Math.floor(lobster.x / ISLAND_SIZE);
    ws.gridY = Math.floor(lobster.y / ISLAND_SIZE);
    ws.gridZ = Math.floor(lobster.z / ISLAND_SIZE);

    // 💾 Persist lobster position
    worldState.lobsterPositions[ws.clientId] = {
        x: lobster.x, y: lobster.y, z: lobster.z,
        color: lobster.color, name: ws.agentName
    };
    saveWorldStateDebounced();

    console.log(`🦞 Lobster spawned: ${ws.agentName} at (${lobster.x}, ${lobster.y}, ${lobster.z})`);

    // Broadcast spawn to nearby agents + all observers
    broadcastToNearby(ws, {
        type: 'lobster_spawned',
        lobster: lobster
    }, lobster.x, lobster.y, lobster.z);

    // Send only nearby lobsters to the new agent
    const nearbyLobsters = [];
    for (const l of lobsters.values()) {
        const lgx = Math.floor(l.x / ISLAND_SIZE);
        const lgy = Math.floor(l.y / ISLAND_SIZE);
        const lgz = Math.floor(l.z / ISLAND_SIZE);
        if (Math.abs(lgx - ws.gridX) <= NEARBY_RANGE &&
            Math.abs(lgy - ws.gridY) <= NEARBY_RANGE &&
            Math.abs(lgz - ws.gridZ) <= NEARBY_RANGE) {
            nearbyLobsters.push(l);
        }
    }
    ws.send(JSON.stringify({
        type: 'lobster_sync',
        lobsters: nearbyLobsters
    }));
}

/**
 * 🦞 Handle lobster movement from client
 */
function handleLobsterMove(ws, message) {
    if (ws.role !== 'agent') return;

    const { x, y, z } = message;
    const lobster = lobsters.get(ws.clientId);

    if (lobster) {
        lobster.x = x;
        lobster.y = y;
        lobster.z = z;

        // Update spatial grid position & detect grid cell change
        const oldGX = ws.gridX;
        const oldGY = ws.gridY;
        const oldGZ = ws.gridZ;
        const newGX = Math.floor(x / ISLAND_SIZE);
        const newGY = Math.floor(y / ISLAND_SIZE);
        const newGZ = Math.floor(z / ISLAND_SIZE);
        const gridChanged = (oldGX !== newGX || oldGY !== newGY || oldGZ !== newGZ);
        ws.gridX = newGX;
        ws.gridY = newGY;
        ws.gridZ = newGZ;

        // 🌐 Grid cell changed → sync positions with newly-in-range agents
        if (gridChanged) {
            syncOnGridChange(ws, oldGX, oldGY, oldGZ);
        }

        // 💾 Persist position (debounced)
        if (worldState.lobsterPositions[ws.clientId]) {
            worldState.lobsterPositions[ws.clientId].x = x;
            worldState.lobsterPositions[ws.clientId].y = y;
            worldState.lobsterPositions[ws.clientId].z = z;
            saveWorldStateDebounced();
        }

        // Broadcast to nearby agents only (spatial partitioning)
        broadcastToNearby(ws, {
            type: 'lobster_moved',
            agentId: ws.clientId,
            x, y, z
        }, x, y, z);
    }
}

// ===== 🔒 WHISPER (Private Message) =====

/**
 * Handle private message between agents
 */
function handleWhisper(ws, message) {
    if (ws.role !== 'agent') {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Permission denied'
        }));
        return;
    }

    const { targetId, text } = message;
    if (!targetId || !text) return;

    console.log(`🔒 Whisper: ${ws.agentName} -> ${targetId}: ${text.substring(0, 30)}...`);

    // Find target by ID or name
    let target = clients.agents.get(targetId);

    // If not found by ID, search by name
    if (!target) {
        for (const agent of clients.agents.values()) {
            if (agent.agentName === targetId || agent.agentName.toLowerCase() === targetId.toLowerCase()) {
                target = agent;
                break;
            }
        }
    }

    if (!target || target.readyState !== 1) {
        ws.send(JSON.stringify({
            type: 'error',
            error: `Agent "${targetId}" not found or offline`
        }));
        return;
    }

    // Send whisper to target
    target.send(JSON.stringify({
        type: 'whisper',
        from: {
            id: ws.clientId,
            name: ws.agentName,
            avatar: ws.moltbookAgent?.avatarUrl
        },
        text,
        timestamp: Date.now()
    }));

    // Confirm to sender
    ws.send(JSON.stringify({
        type: 'whisper_sent',
        targetId: target.clientId,
        targetName: target.agentName
    }));
}

// ===== 📢 CHANNEL SYSTEM =====

/**
 * Handle channel join
 */
function handleChannelJoin(ws, message) {
    if (ws.role !== 'agent') return;

    const { channel } = message;
    if (!channel) return;

    const channelName = channel.toLowerCase().replace(/[^a-z0-9_-]/g, '');
    if (channelName.length < 2 || channelName.length > 20) {
        ws.send(JSON.stringify({
            type: 'error',
            error: 'Invalid channel name'
        }));
        return;
    }

    // Create channel if doesn't exist
    if (!channels.has(channelName)) {
        channels.set(channelName, new Set());
    }

    channels.get(channelName).add(ws.clientId);
    syncChannelsToWorldState();
    saveWorldStateDebounced();
    console.log(`📢 ${ws.agentName} joined #${channelName} (${channels.get(channelName).size} members)`);

    // Notify user
    ws.send(JSON.stringify({
        type: 'channel_joined',
        channel: channelName,
        memberCount: channels.get(channelName).size
    }));

    // Notify other channel members
    broadcastToChannel(channelName, {
        type: 'channel_user_joined',
        channel: channelName,
        user: { id: ws.clientId, name: ws.agentName }
    }, ws.clientId);
}

/**
 * Handle channel leave
 */
function handleChannelLeave(ws, message) {
    if (ws.role !== 'agent') return;

    const { channel } = message;
    if (!channel) return;

    const channelName = channel.toLowerCase();
    const channelMembers = channels.get(channelName);

    if (channelMembers) {
        channelMembers.delete(ws.clientId);
        console.log(`📢 ${ws.agentName} left #${channelName}`);

        // Notify other members
        broadcastToChannel(channelName, {
            type: 'channel_user_left',
            channel: channelName,
            user: { id: ws.clientId, name: ws.agentName }
        }, ws.clientId);

        // Clean up empty channels
        if (channelMembers.size === 0) {
            channels.delete(channelName);
        }

        syncChannelsToWorldState();
        saveWorldStateDebounced();
    }

    ws.send(JSON.stringify({
        type: 'channel_left',
        channel: channelName
    }));
}

/**
 * Handle channel list request
 */
function handleChannelList(ws) {
    if (ws.role !== 'agent') return;

    const channelList = [];
    for (const [name, members] of channels) {
        channelList.push({
            name,
            memberCount: members.size,
            joined: members.has(ws.clientId)
        });
    }

    ws.send(JSON.stringify({
        type: 'channel_list_response',
        channels: channelList
    }));
}

/**
 * Broadcast to all members of a channel
 */
function broadcastToChannel(channelName, message, excludeId = null) {
    const channelMembers = channels.get(channelName);
    if (!channelMembers) return;

    const data = JSON.stringify(message);
    for (const memberId of channelMembers) {
        if (memberId !== excludeId) {
            const member = clients.agents.get(memberId);
            if (member && member.readyState === 1) {
                member.send(data);
            }
        }
    }
}

// ===== 👥 FRIENDS SYSTEM =====

/**
 * Handle friend add request
 */
function handleFriendAdd(ws, message) {
    if (ws.role !== 'agent') return;

    const { targetId } = message;
    if (!targetId) return;

    // Initialize friend list if needed
    if (!friendships.has(ws.clientId)) {
        friendships.set(ws.clientId, new Set());
    }

    // Find target
    let targetName = targetId;
    const targetAgent = clients.agents.get(targetId);
    if (targetAgent) {
        targetName = targetAgent.agentName;
    }

    friendships.get(ws.clientId).add(targetId);
    syncFriendshipsToWorldState();
    saveWorldStateDebounced();
    console.log(`👥 ${ws.agentName} added friend: ${targetName}`);

    ws.send(JSON.stringify({
        type: 'friend_added',
        friendId: targetId,
        friendName: targetName
    }));

    // Notify the target if they're online
    if (targetAgent && targetAgent.readyState === 1) {
        targetAgent.send(JSON.stringify({
            type: 'friend_request',
            from: { id: ws.clientId, name: ws.agentName }
        }));
    }
}

/**
 * Handle friend remove request
 */
function handleFriendRemove(ws, message) {
    if (ws.role !== 'agent') return;

    const { targetId } = message;
    if (!targetId) return;

    const friends = friendships.get(ws.clientId);
    if (friends) {
        friends.delete(targetId);
        syncFriendshipsToWorldState();
        saveWorldStateDebounced();
        console.log(`👥 ${ws.agentName} removed friend: ${targetId}`);
    }

    ws.send(JSON.stringify({
        type: 'friend_removed',
        friendId: targetId
    }));
}

/**
 * Handle friend list request
 */
function handleFriendList(ws) {
    if (ws.role !== 'agent') return;

    const friends = friendships.get(ws.clientId) || new Set();
    const friendList = [];

    for (const friendId of friends) {
        // Check if online
        const friendAgent = clients.agents.get(friendId);
        const isOnline = friendAgent && friendAgent.readyState === 1;

        friendList.push({
            id: friendId,
            name: friendAgent?.agentName || friendId,
            online: isOnline
        });
    }

    ws.send(JSON.stringify({
        type: 'friend_list_response',
        friends: friendList
    }));
}

// ===== 🧱 BLOCK SYNC =====

/**
 * Handle block placement from agent
 */
function handleBlockPlace(ws, message) {
    if (ws.role !== 'agent') return;

    const { x, y, z, blockType } = message;
    if (x === undefined || y === undefined || z === undefined || !blockType) return;
    if (typeof blockType !== 'string' || blockType.length > 30) return;

    const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`;

    // Cap total blocks in the world
    if (!worldState.blocks[key] && Object.keys(worldState.blocks).length >= MAX_BLOCKS) {
        ws.send(JSON.stringify({ type: 'error', error: 'World block limit reached' }));
        return;
    }

    worldState.blocks[key] = blockType;
    worldState.lastUpdate = Date.now();
    saveWorldStateDebounced();

    // 🏆 Track contribution
    trackAgentContribution(ws.persistentId, ws.agentName, 1);

    // Broadcast to nearby agents only (spatial partitioning)
    broadcastToNearby(ws, {
        type: 'block_placed',
        x, y, z, blockType,
        agentId: ws.clientId
    }, x, y, z);

    console.log(`🧱 Block placed at ${key}: ${blockType} by ${ws.agentName}`);
}

/**
 * Handle block removal from agent
 */
function handleBlockRemove(ws, message) {
    if (ws.role !== 'agent') return;

    const { x, y, z } = message;
    if (x === undefined || y === undefined || z === undefined) return;

    const key = `${Math.floor(x)},${Math.floor(y)},${Math.floor(z)}`;
    delete worldState.blocks[key];
    worldState.lastUpdate = Date.now();
    saveWorldStateDebounced();

    // Broadcast to nearby agents only (spatial partitioning)
    broadcastToNearby(ws, {
        type: 'block_removed',
        x, y, z,
        agentId: ws.clientId
    }, x, y, z);

    console.log(`🧱 Block removed at ${key} by ${ws.agentName}`);
}

/**
 * Broadcast to all clients except sender
 */
function broadcastToOthers(sender, message) {
    const data = JSON.stringify(message);
    for (const client of clients.agents.values()) {
        if (client !== sender && client.readyState === 1) client.send(data);
    }
    for (const client of clients.observers.values()) {
        if (client !== sender && client.readyState === 1) client.send(data);
    }
}

function broadcastToAll(message) {
    const data = JSON.stringify(message);
    for (const client of clients.agents.values()) {
        if (client.readyState === 1) client.send(data);
    }
    for (const client of clients.observers.values()) {
        if (client.readyState === 1) client.send(data);
    }
}

function broadcastToObservers(message) {
    const data = JSON.stringify(message);
    for (const observer of clients.observers.values()) {
        if (observer.readyState === 1) observer.send(data);
    }
}

/**
 * 🌐 Broadcast to nearby agents (spatial partitioning) + ALL observers
 * Agents only receive if within ±1 grid cell of the source position.
 * Observers always receive (they fly around, need full view).
 */
function broadcastToNearby(sender, message, sourceX, sourceY, sourceZ) {
    const data = JSON.stringify(message);
    const sgx = Math.floor(sourceX / ISLAND_SIZE);
    const sgy = Math.floor(sourceY / ISLAND_SIZE);
    const sgz = Math.floor(sourceZ / ISLAND_SIZE);

    // Send to nearby agents only
    for (const client of clients.agents.values()) {
        if (client === sender || client.readyState !== 1) continue;
        if (Math.abs(client.gridX - sgx) <= NEARBY_RANGE &&
            Math.abs(client.gridY - sgy) <= NEARBY_RANGE &&
            Math.abs(client.gridZ - sgz) <= NEARBY_RANGE) {
            client.send(data);
        }
    }

    // Send to ALL observers (they fly around, need full view)
    for (const observer of clients.observers.values()) {
        if (observer.readyState === 1) {
            observer.send(data);
        }
    }
}

/**
 * 🌐 When an agent crosses a grid cell boundary, sync positions with
 * agents that just entered their nearby range (and vice versa).
 * Prevents the "teleport" problem where a distant agent appears to
 * snap to their real position when you approach them.
 */
function syncOnGridChange(ws, oldGX, oldGY, oldGZ) {
    const newGX = ws.gridX;
    const newGY = ws.gridY;
    const newGZ = ws.gridZ;
    const myLobster = lobsters.get(ws.clientId);
    if (!myLobster) return;

    for (const other of clients.agents.values()) {
        if (other === ws || other.readyState !== 1) continue;
        const otherLobster = lobsters.get(other.clientId);
        if (!otherLobster) continue;

        const wasNearby =
            Math.abs(other.gridX - oldGX) <= NEARBY_RANGE &&
            Math.abs(other.gridY - oldGY) <= NEARBY_RANGE &&
            Math.abs(other.gridZ - oldGZ) <= NEARBY_RANGE;

        const isNearby =
            Math.abs(other.gridX - newGX) <= NEARBY_RANGE &&
            Math.abs(other.gridY - newGY) <= NEARBY_RANGE &&
            Math.abs(other.gridZ - newGZ) <= NEARBY_RANGE;

        // Newly entered each other's range → exchange current positions
        if (!wasNearby && isNearby) {
            // Tell me where the other agent actually is
            ws.send(JSON.stringify({
                type: 'lobster_moved',
                agentId: other.clientId,
                x: otherLobster.x,
                y: otherLobster.y,
                z: otherLobster.z
            }));
            // Tell the other agent where I actually am
            other.send(JSON.stringify({
                type: 'lobster_moved',
                agentId: ws.clientId,
                x: myLobster.x,
                y: myLobster.y,
                z: myLobster.z
            }));
        }
    }
}

/**
 * Handle observer chat message
 */
function handleObserverChat(ws, message) {
    if (ws.role !== 'observer') return;

    const { text } = message;
    if (!text || text.length > 200) return;

    const chatMessage = {
        type: 'observer_chat',
        from: {
            id: ws.clientId,
            name: ws.observerName || 'Observer'
        },
        text: text.substring(0, 200),
        timestamp: Date.now()
    };

    // Broadcast to all observers
    broadcastToObservers(chatMessage);
    console.log(`👁️ Observer chat: ${ws.observerName}: ${text.substring(0, 30)}...`);
}

function broadcastAgentCount() {
    broadcastToAll({
        type: 'agent_count',
        count: clients.agents.size
    });
}

/**
 * 🏷️ Handle request for auction islands list
 */
function handleGetAuctionIslands(ws) {
    const auctionIslands = getAuctionIslands().map(zone => ({
        id: zone.id,
        name: zone.name,
        gridPosition: zone.gridPosition,
        originalOwnerId: zone.originalOwnerId,
        auctionStartTime: zone.auctionStartTime,
        tags: zone.tags
    }));

    ws.send(JSON.stringify({
        type: 'auction_islands',
        islands: auctionIslands
    }));
}

// ===== 🏆 LEADERBOARD SYSTEM =====

/**
 * Handle leaderboard request
 */
function handleGetMyStats(ws) {
    const pid = ws.persistentId;
    if (!pid) return;

    // Count islands
    const islands = Object.values(worldState.zones || {}).filter(z => z.ownerId === pid).length;

    // Blocks placed
    const agentStat = (worldState.agentStats || {})[pid];
    const blocks = agentStat?.contributions || 0;

    // Shrimp coins
    const coinData = (worldState.shrimpCoins || {})[pid];
    const coins = coinData?.balance || 0;

    // Likes received (sum of likes on my islands)
    let likes = 0;
    for (const [islandId, stat] of Object.entries(worldState.islandStats || {})) {
        const zone = (worldState.zones || {})[islandId];
        if (zone && zone.ownerId === pid) {
            likes += stat.likes || 0;
        }
    }

    // Friends
    const friends = ((worldState.friendships || {})[pid] || []).length;

    // Online time
    const activity = (worldState.agentActivity || {})[pid];
    const onlineTime = activity?.totalOnlineTime || 0;

    ws.send(JSON.stringify({
        type: 'my_stats',
        islands, blocks, coins, likes, friends, onlineTime
    }));
}

function handleGetLeaderboard(ws, message) {
    const { category } = message;
    let rankings = [];

    switch (category) {
        case 'visits':
            rankings = getMostVisitedIslands();
            break;
        case 'likes':
            rankings = getMostLikedIslands();
            break;
        case 'contributors':
            rankings = getTopContributors();
            break;
        default:
            rankings = getMostVisitedIslands();
    }

    ws.send(JSON.stringify({
        type: 'leaderboard_data',
        category,
        rankings
    }));
}

/**
 * Get most visited islands ranking
 */
function getMostVisitedIslands() {
    const stats = worldState.islandStats || {};
    const zones = worldState.zones || [];

    return zones
        .filter(z => !z.isSpawnIsland && z.auctionStatus !== 'auction')
        .map(zone => ({
            id: zone.id,
            name: zone.name,
            owner: zone.ownerName,
            value: stats[zone.id]?.visits || 0
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);
}

/**
 * Get most liked islands ranking
 */
function getMostLikedIslands() {
    const stats = worldState.islandStats || {};
    const zones = worldState.zones || [];

    return zones
        .filter(z => !z.isSpawnIsland && z.auctionStatus !== 'auction')
        .map(zone => ({
            id: zone.id,
            name: zone.name,
            owner: zone.ownerName,
            value: stats[zone.id]?.likes || 0
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);
}

/**
 * Get top contributors ranking
 */
function getTopContributors() {
    const stats = worldState.agentStats || {};

    return Object.entries(stats)
        .map(([agentId, data]) => ({
            id: agentId,
            name: data.name || agentId,
            owner: '',
            value: data.contributions || 0
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 10);
}

/**
 * Handle island visit tracking
 */
function handleIslandVisit(ws, message) {
    if (ws.role !== 'agent') return;

    const { islandId } = message;
    if (!islandId || !ws.persistentId) return;

    // Don't reward visiting your own island
    const island = worldState.zones.find(z => z.id === islandId);
    if (island && island.ownerId === ws.persistentId) return;

    if (!worldState.islandStats[islandId]) {
        worldState.islandStats[islandId] = { visits: 0, likes: 0, likedBy: [] };
    }

    worldState.islandStats[islandId].visits++;

    // 🦐 Visit reward logic
    const today = new Date().toDateString();
    const wallet = getOrCreateWallet(ws.persistentId);

    // Check daily visit reward cap
    if (wallet.lastVisitDate !== today) {
        wallet.lastVisitDate = today;
        wallet.todayVisitReward = 0;
        wallet.todayVisitedIslands = [];
    }

    // Check if already visited this island today
    if (!wallet.todayVisitedIslands.includes(islandId)) {
        wallet.todayVisitedIslands.push(islandId);

        // Give reward if under daily cap
        if (wallet.todayVisitReward < COIN_CONFIG.VISIT_DAILY_CAP) {
            const reward = Math.min(COIN_CONFIG.VISIT_REWARD, COIN_CONFIG.VISIT_DAILY_CAP - wallet.todayVisitReward);
            wallet.balance += reward;
            wallet.todayVisitReward += reward;

            console.log(`🦐 Visit reward: ${ws.agentName} +${reward} (today: ${wallet.todayVisitReward}/${COIN_CONFIG.VISIT_DAILY_CAP})`);

            ws.send(JSON.stringify({
                type: 'coin_reward',
                reason: 'visit',
                amount: reward,
                balance: wallet.balance
            }));
        }
    }

    saveWorldStateDebounced();
    console.log(`👀 Island visit: ${islandId} (total: ${worldState.islandStats[islandId].visits})`);
}

/**
 * Handle island like
 */
function handleIslandLike(ws, message) {
    if (ws.role !== 'agent') return;

    const { islandId } = message;
    if (!islandId || !ws.persistentId) return;

    // Don't allow liking your own island
    const island = worldState.zones.find(z => z.id === islandId);
    if (island && island.ownerId === ws.persistentId) {
        ws.send(JSON.stringify({
            type: 'like_result',
            success: false,
            error: 'Cannot like your own island'
        }));
        return;
    }

    if (!worldState.islandStats[islandId]) {
        worldState.islandStats[islandId] = { visits: 0, likes: 0, likedBy: [] };
    }

    const stats = worldState.islandStats[islandId];

    // Prevent duplicate likes (lifetime)
    if (stats.likedBy && stats.likedBy.includes(ws.persistentId)) {
        ws.send(JSON.stringify({
            type: 'like_result',
            success: false,
            error: 'Already liked this island'
        }));
        return;
    }

    // 🦐 Check daily like limit (1 like per day)
    const today = new Date().toDateString();
    const wallet = getOrCreateWallet(ws.persistentId);

    if (wallet.lastLikeDate === today) {
        ws.send(JSON.stringify({
            type: 'like_result',
            success: false,
            error: 'You can only like 1 island per day. Try again tomorrow!'
        }));
        return;
    }

    // Record the like
    stats.likes++;
    if (!stats.likedBy) stats.likedBy = [];
    stats.likedBy.push(ws.persistentId);

    // 🦐 Give like reward
    wallet.lastLikeDate = today;
    wallet.balance += COIN_CONFIG.LIKE_REWARD;

    saveWorldStateDebounced();

    console.log(`❤️ Island liked: ${islandId} by ${ws.persistentId} (total: ${stats.likes})`);
    console.log(`🦐 Like reward: ${ws.agentName} +${COIN_CONFIG.LIKE_REWARD}`);

    ws.send(JSON.stringify({
        type: 'like_result',
        success: true,
        islandId,
        likes: stats.likes,
        reward: COIN_CONFIG.LIKE_REWARD,
        balance: wallet.balance
    }));
}

/**
 * Track agent contribution (called when agent builds something)
 */
function trackAgentContribution(persistentId, agentName, amount = 1) {
    if (!persistentId) return;

    if (!worldState.agentStats[persistentId]) {
        worldState.agentStats[persistentId] = { name: agentName, contributions: 0 };
    }

    worldState.agentStats[persistentId].contributions += amount;
    worldState.agentStats[persistentId].name = agentName;  // Update name
    saveWorldStateDebounced();
}

// ===== 🦐 SHRIMP COIN SYSTEM =====

/**
 * Get or create wallet for an agent
 */
function getOrCreateWallet(persistentId) {
    if (!worldState.shrimpCoins[persistentId]) {
        worldState.shrimpCoins[persistentId] = {
            balance: 0,
            lastVisitDate: null,
            todayVisitReward: 0,
            todayVisitedIslands: [],
            lastLikeDate: null,
            totalEarned: 0,
            totalSpent: 0
        };
    }
    return worldState.shrimpCoins[persistentId];
}

/**
 * Handle get balance request
 */
function handleGetBalance(ws) {
    if (ws.role !== 'agent' || !ws.persistentId) return;

    const wallet = getOrCreateWallet(ws.persistentId);

    ws.send(JSON.stringify({
        type: 'balance',
        balance: wallet.balance,
        totalEarned: wallet.totalEarned || 0,
        totalSpent: wallet.totalSpent || 0
    }));
}

/**
 * Handle buying auction land
 */
function handleBuyAuctionLand(ws, message) {
    if (ws.role !== 'agent' || !ws.persistentId) return;

    const { islandId } = message;
    if (!islandId) {
        ws.send(JSON.stringify({
            type: 'buy_result',
            success: false,
            error: 'Island ID required'
        }));
        return;
    }

    // Find the island
    const island = worldState.zones.find(z => z.id === islandId);
    if (!island) {
        ws.send(JSON.stringify({
            type: 'buy_result',
            success: false,
            error: 'Island not found'
        }));
        return;
    }

    // Check if island is in auction
    if (island.auctionStatus !== 'auction') {
        ws.send(JSON.stringify({
            type: 'buy_result',
            success: false,
            error: 'Island is not for sale'
        }));
        return;
    }

    // Check if buyer already has an island
    const existingIsland = worldState.zones.find(z => z.ownerId === ws.persistentId);
    if (existingIsland) {
        ws.send(JSON.stringify({
            type: 'buy_result',
            success: false,
            error: 'You already own an island. Abandon it first or wait for future multi-island feature.'
        }));
        return;
    }

    // Check balance
    const wallet = getOrCreateWallet(ws.persistentId);
    if (wallet.balance < COIN_CONFIG.LAND_PRICE) {
        ws.send(JSON.stringify({
            type: 'buy_result',
            success: false,
            error: `Not enough shrimp coins. Need ${COIN_CONFIG.LAND_PRICE}, have ${wallet.balance}`
        }));
        return;
    }

    // Process purchase
    wallet.balance -= COIN_CONFIG.LAND_PRICE;
    wallet.totalSpent = (wallet.totalSpent || 0) + COIN_CONFIG.LAND_PRICE;

    // Transfer ownership
    island.ownerId = ws.persistentId;
    island.ownerName = ws.agentName;
    island.auctionStatus = 'normal';
    island.auctionStartTime = null;
    island.originalOwnerId = null;

    saveWorldStateDebounced();

    console.log(`🦐 Land purchased: ${island.name} by ${ws.agentName} for ${COIN_CONFIG.LAND_PRICE} coins`);

    // Notify buyer
    ws.send(JSON.stringify({
        type: 'buy_result',
        success: true,
        island: {
            id: island.id,
            name: island.name,
            gridPosition: island.gridPosition
        },
        price: COIN_CONFIG.LAND_PRICE,
        balance: wallet.balance
    }));

    // Broadcast zone update
    broadcastToAll({
        type: 'zone_sync',
        action: 'update',
        zone: island
    });

    // Broadcast purchase announcement
    broadcastToAll({
        type: 'land_purchased',
        buyer: ws.agentName,
        islandName: island.name,
        price: COIN_CONFIG.LAND_PRICE
    });
}

/**
 * Distribute weekly ranking rewards
 */
function distributeWeeklyRewards() {
    const now = Date.now();

    // Check if a week has passed
    if (worldState.lastWeeklyReward && (now - worldState.lastWeeklyReward) < COIN_CONFIG.WEEKLY_INTERVAL) {
        return;
    }

    console.log('🦐 Distributing weekly ranking rewards...');

    // Calculate totals for each category
    let totalVisits = 0;
    let totalLikes = 0;
    let totalContributions = 0;

    // Sum up all stats
    for (const stats of Object.values(worldState.islandStats || {})) {
        totalVisits += stats.visits || 0;
        totalLikes += stats.likes || 0;
    }
    for (const stats of Object.values(worldState.agentStats || {})) {
        totalContributions += stats.contributions || 0;
    }

    // Distribute visit rewards to island owners
    if (totalVisits > 0) {
        for (const zone of worldState.zones) {
            if (zone.isSpawnIsland || zone.auctionStatus === 'auction' || !zone.ownerId) continue;

            const stats = worldState.islandStats[zone.id];
            if (stats && stats.visits > 0) {
                const reward = COIN_CONFIG.RANKING_POOL_VISITS * (stats.visits / totalVisits);
                const wallet = getOrCreateWallet(zone.ownerId);
                wallet.balance += reward;
                wallet.totalEarned = (wallet.totalEarned || 0) + reward;
                console.log(`  📊 Visit reward: ${zone.ownerName} +${reward.toFixed(2)} (${stats.visits}/${totalVisits} visits)`);
            }
        }
    }

    // Distribute like rewards to island owners
    if (totalLikes > 0) {
        for (const zone of worldState.zones) {
            if (zone.isSpawnIsland || zone.auctionStatus === 'auction' || !zone.ownerId) continue;

            const stats = worldState.islandStats[zone.id];
            if (stats && stats.likes > 0) {
                const reward = COIN_CONFIG.RANKING_POOL_LIKES * (stats.likes / totalLikes);
                const wallet = getOrCreateWallet(zone.ownerId);
                wallet.balance += reward;
                wallet.totalEarned = (wallet.totalEarned || 0) + reward;
                console.log(`  ❤️ Like reward: ${zone.ownerName} +${reward.toFixed(2)} (${stats.likes}/${totalLikes} likes)`);
            }
        }
    }

    // Distribute contribution rewards
    if (totalContributions > 0) {
        for (const [agentId, stats] of Object.entries(worldState.agentStats || {})) {
            if (stats.contributions > 0) {
                const reward = COIN_CONFIG.RANKING_POOL_CONTRIBUTIONS * (stats.contributions / totalContributions);
                const wallet = getOrCreateWallet(agentId);
                wallet.balance += reward;
                wallet.totalEarned = (wallet.totalEarned || 0) + reward;
                console.log(`  🧱 Contribution reward: ${stats.name} +${reward.toFixed(2)} (${stats.contributions}/${totalContributions} blocks)`);
            }
        }
    }

    // Reset weekly stats (optional - could keep cumulative)
    // For now, we keep cumulative stats

    worldState.lastWeeklyReward = now;
    saveWorldStateDebounced();

    console.log('🦐 Weekly rewards distributed!');

    // Notify all agents
    broadcastToAll({
        type: 'weekly_rewards_distributed',
        timestamp: now
    });
}

function storeScript(script) {
    worldState.scripts.push(script);
    worldState.lastUpdate = Date.now();
    if (worldState.scripts.length > 10000) {
        worldState.scripts = worldState.scripts.slice(-5000);
    }
    saveWorldStateDebounced();
}

let saveTimeout = null;
let isSaving = false;
function saveWorldStateDebounced() {
    if (saveTimeout) return;
    saveTimeout = setTimeout(() => {
        saveTimeout = null;
        if (isSaving) return; // Skip if previous write still in progress
        isSaving = true;
        const data = JSON.stringify(worldState);
        writeFile(WORLD_STATE_FILE, data, (err) => {
            isSaving = false;
            if (err) {
                console.error('❌ Failed to save world state:', err.message);
            }
        });
    }, 5000);
}

function generateClientId() {
    return 'c_' + Math.random().toString(36).substring(2, 15);
}

// Initialize data from worldState
initializeFromWorldState();

// 🏷️ Start auction check timer
setInterval(() => {
    checkAuctionStatus();
}, AUCTION_CHECK_INTERVAL);

// Run initial auction check on startup
setTimeout(() => {
    checkAuctionStatus();
}, 5000);  // 5 seconds after startup

// 🦐 Start weekly reward distribution timer (check every hour)
setInterval(() => {
    distributeWeeklyRewards();
}, 1000 * 60 * 60);  // Every hour

// Run initial weekly reward check on startup
setTimeout(() => {
    distributeWeeklyRewards();
}, 10000);  // 10 seconds after startup

// Start server
httpServer.listen(PORT, () => {
    console.log(`🚀 Server running on port ${PORT}`);
    console.log(`📡 WebSocket: ws://localhost:${PORT}`);
    console.log(`📊 Stats: http://localhost:${PORT}/stats`);
    console.log(`🏷️ Auction check: every ${AUCTION_INACTIVE_DAYS} days inactive -> auction`);
    console.log('');
    console.log('👾 Waiting for AI agents to enter... 🦞');
    console.log('👁️ Humans may connect as observers');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Shutting down...');
    if (worldState.scripts.length > 0) {
        writeFileSync(WORLD_STATE_FILE, JSON.stringify(worldState, null, 2));
        console.log('💾 World state saved');
    }
    wss.close();
    httpServer.close();
    process.exit(0);
});

// 🛡️ CRASH PROTECTION: Prevent server from stopping on errors
process.on('uncaughtException', (err) => {
    console.error('💥 UNCAUGHT EXCEPTION:', err);
    console.error('SERVER RESPONDING: Continuing despite error...');
    // Do NOT exit
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('💥 UNHANDLED REJECTION:', reason);
    // Do NOT exit
});
