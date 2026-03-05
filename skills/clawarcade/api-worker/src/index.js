/**
 * ClawArcade API Worker
 * Handles authentication, leaderboards, tournaments, and score submissions
 * for both human players and AI bots
 */

// Admin player IDs that can create/manage tournaments
const ADMIN_IDS = [
  // Add admin player IDs here
];

// Admin API key loaded from env (set in wrangler.toml secrets)
// DO NOT hardcode secrets in source code

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
};

// Simple password hashing (for production, use Argon2 or bcrypt via WASM)
async function hashPassword(password) {
  const encoder = new TextEncoder();
  const data = encoder.encode(password + 'clawarcade-salt-v1');
  const hash = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(hash)));
}

async function verifyPassword(password, hash) {
  const computed = await hashPassword(password);
  return computed === hash;
}

// JWT implementation
async function createJWT(payload, secret) {
  const header = { alg: 'HS256', typ: 'JWT' };
  const now = Math.floor(Date.now() / 1000);
  const tokenPayload = {
    ...payload,
    iat: now,
    exp: now + 86400 * 7, // 7 days
  };
  
  const encodedHeader = btoa(JSON.stringify(header)).replace(/=/g, '');
  const encodedPayload = btoa(JSON.stringify(tokenPayload)).replace(/=/g, '');
  
  const encoder = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw',
    encoder.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  const signature = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(`${encodedHeader}.${encodedPayload}`)
  );
  
  const encodedSignature = btoa(String.fromCharCode(...new Uint8Array(signature)))
    .replace(/=/g, '')
    .replace(/\+/g, '-')
    .replace(/\//g, '_');
  
  return `${encodedHeader}.${encodedPayload}.${encodedSignature}`;
}

async function verifyJWT(token, secret) {
  try {
    const [header, payload, signature] = token.split('.');
    if (!header || !payload || !signature) return null;
    
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['verify']
    );
    
    const signatureBytes = Uint8Array.from(
      atob(signature.replace(/-/g, '+').replace(/_/g, '/')),
      c => c.charCodeAt(0)
    );
    
    const valid = await crypto.subtle.verify(
      'HMAC',
      key,
      signatureBytes,
      encoder.encode(`${header}.${payload}`)
    );
    
    if (!valid) return null;
    
    const data = JSON.parse(atob(payload));
    if (data.exp && data.exp < Math.floor(Date.now() / 1000)) {
      return null; // Expired
    }
    
    return data;
  } catch {
    return null;
  }
}

// Generate API key for bots
function generateApiKey() {
  const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let key = 'arcade_bot_';
  for (let i = 0; i < 32; i++) {
    key += chars[Math.floor(Math.random() * chars.length)];
  }
  return key;
}

// Generate player ID
function generateId() {
  return crypto.randomUUID();
}

// Router helper
function matchRoute(pathname, pattern) {
  const patternParts = pattern.split('/');
  const pathParts = pathname.split('/');
  
  if (patternParts.length !== pathParts.length) return null;
  
  const params = {};
  for (let i = 0; i < patternParts.length; i++) {
    if (patternParts[i].startsWith(':')) {
      params[patternParts[i].slice(1)] = pathParts[i];
    } else if (patternParts[i] !== pathParts[i]) {
      return null;
    }
  }
  return params;
}

// Auth middleware
async function authenticate(request, env) {
  // Check API key first (for bots)
  const apiKey = request.headers.get('X-API-Key');
  if (apiKey) {
    const player = await env.DB.prepare(
      'SELECT * FROM players WHERE api_key = ?'
    ).bind(apiKey).first();
    if (player) {
      // Check if guest has expired (guest_expires_at being set = guest account)
      const isGuest = !!player.guest_expires_at;
      if (isGuest) {
        const expiresAt = new Date(player.guest_expires_at + 'Z');
        if (expiresAt < new Date()) {
          return null; // Guest expired
        }
      }
      // Return appropriate type
      const playerType = isGuest ? 'guest_bot' : 'bot';
      return { player, type: playerType, isGuest };
    }
  }
  
  // Check JWT token (for humans)
  const authHeader = request.headers.get('Authorization');
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.slice(7);
    const payload = await verifyJWT(token, env.JWT_SECRET);
    if (payload && payload.playerId) {
      const player = await env.DB.prepare(
        'SELECT * FROM players WHERE id = ?'
      ).bind(payload.playerId).first();
      if (player) {
        // Check if guest has expired
        const isGuest = !!player.guest_expires_at;
        if (isGuest) {
          const expiresAt = new Date(player.guest_expires_at + 'Z');
          if (expiresAt < new Date()) {
            return null; // Guest expired
          }
        }
        const playerType = isGuest ? 'guest_human' : 'human';
        return { player, type: playerType, isGuest };
      }
    }
  }
  
  return null;
}

// Response helpers
function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

function error(message, status = 400) {
  return json({ error: message }, status);
}

// Arcade points calculation
const POINTS = {
  MULTIPLAYER_WIN: 100,
  SECOND_PLACE: 50,
  THIRD_PLACE: 25,
  PARTICIPATION: 10,
  HIGH_SCORE_BEATEN: 50,
  PERSONAL_BEST: 10,
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Handle CORS preflight
    if (method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    try {
      // ==================== AUTH ROUTES ====================
      
      // POST /api/auth/register - Human registration
      if (method === 'POST' && path === '/api/auth/register') {
        const body = await request.json();
        const { username, password, displayName } = body;
        
        if (!username || !password) {
          return error('Username and password required');
        }
        
        if (username.length < 3 || username.length > 20) {
          return error('Username must be 3-20 characters');
        }
        
        if (password.length < 6) {
          return error('Password must be at least 6 characters');
        }
        
        // Check if username exists
        const existing = await env.DB.prepare(
          'SELECT id FROM players WHERE username = ?'
        ).bind(username.toLowerCase()).first();
        
        if (existing) {
          return error('Username already taken');
        }
        
        const id = generateId();
        const passwordHash = await hashPassword(password);
        
        await env.DB.prepare(`
          INSERT INTO players (id, type, username, display_name, password_hash)
          VALUES (?, 'human', ?, ?, ?)
        `).bind(id, username.toLowerCase(), displayName || username, passwordHash).run();
        
        const token = await createJWT({ playerId: id }, env.JWT_SECRET);
        
        return json({
          success: true,
          player: {
            id,
            username: username.toLowerCase(),
            displayName: displayName || username,
            type: 'human',
            arcadePoints: 0,
          },
          token,
        });
      }
      
      // POST /api/auth/login - Human login
      if (method === 'POST' && path === '/api/auth/login') {
        const body = await request.json();
        const { username, password } = body;
        
        if (!username || !password) {
          return error('Username and password required');
        }
        
        const player = await env.DB.prepare(
          'SELECT * FROM players WHERE username = ? AND type = ?'
        ).bind(username.toLowerCase(), 'human').first();
        
        if (!player) {
          return error('Invalid username or password', 401);
        }
        
        const valid = await verifyPassword(password, player.password_hash);
        if (!valid) {
          return error('Invalid username or password', 401);
        }
        
        const token = await createJWT({ playerId: player.id }, env.JWT_SECRET);
        
        return json({
          success: true,
          player: {
            id: player.id,
            username: player.username,
            displayName: player.display_name,
            type: player.type,
            arcadePoints: player.arcade_points,
            avatarUrl: player.avatar_url,
          },
          token,
        });
      }
      
      // POST /api/auth/register-bot/start - Start bot registration, get verification code
      if (method === 'POST' && path === '/api/auth/register-bot/start') {
        const body = await request.json();
        const { botName, operatorName, moltbookUsername } = body;
        
        if (!botName || !operatorName || !moltbookUsername) {
          return error('Bot name, operator name, and Moltbook username required');
        }
        
        if (botName.length < 3 || botName.length > 20) {
          return error('Bot name must be 3-20 characters');
        }
        
        // Check if Moltbook username already registered
        const existingMoltbook = await env.DB.prepare(
          'SELECT id FROM players WHERE moltbook_username = ?'
        ).bind(moltbookUsername.toLowerCase()).first();
        
        if (existingMoltbook) {
          return error(`This Moltbook agent already has a registered bot on ClawArcade.`);
        }
        
        // Generate unique verification code
        const verifyCode = 'clawarcade_' + crypto.randomUUID().replace(/-/g, '').slice(0, 16);
        
        // Store pending registration (expires in 30 minutes)
        const pendingId = generateId();
        await env.DB.prepare(`
          INSERT INTO pending_registrations (id, bot_name, operator_name, moltbook_username, verify_code, expires_at)
          VALUES (?, ?, ?, ?, ?, datetime('now', '+30 minutes'))
        `).bind(pendingId, botName, operatorName, moltbookUsername.toLowerCase(), verifyCode).run();
        
        return json({
          success: true,
          pendingId,
          verifyCode,
          moltbookUsername: moltbookUsername.toLowerCase(),
          instructions: `Post this EXACT code on Moltbook: "${verifyCode}" — then call /api/auth/register-bot/complete`,
          expiresIn: '30 minutes',
          nextStep: 'POST /api/auth/register-bot/complete with { pendingId }',
        });
      }
      
      // POST /api/auth/register-bot/complete - Complete registration by verifying Moltbook post
      if (method === 'POST' && path === '/api/auth/register-bot/complete') {
        const body = await request.json();
        const { pendingId } = body;
        
        if (!pendingId) {
          return error('pendingId required');
        }
        
        // Get pending registration
        const pending = await env.DB.prepare(`
          SELECT * FROM pending_registrations 
          WHERE id = ? AND expires_at > datetime('now')
        `).bind(pendingId).first();
        
        if (!pending) {
          return error('Registration expired or not found. Start again with /api/auth/register-bot/start');
        }
        
        // Fetch user's recent posts from Moltbook to find the verification code
        let verified = false;
        let moltbookUserId = null;
        let isAgent = false;
        
        try {
          // First get user profile to check if they're an agent
          const profileRes = await fetch(`https://www.moltbook.com/api/v1/users/${pending.moltbook_username}`);
          if (!profileRes.ok) {
            return error(`Moltbook user "${pending.moltbook_username}" not found`);
          }
          const profile = await profileRes.json();
          moltbookUserId = profile.id;
          isAgent = profile.is_agent || profile.isAgent || false;
          
          if (!isAgent) {
            return error(`${pending.moltbook_username} is not an AI agent on Moltbook. Only AI agents can register.`);
          }
          
          // Now check their recent posts for the verification code
          const postsRes = await fetch(`https://www.moltbook.com/api/v1/users/${pending.moltbook_username}/posts?limit=10`);
          if (postsRes.ok) {
            const postsData = await postsRes.json();
            const posts = postsData.posts || postsData || [];
            
            for (const post of posts) {
              const content = (post.content || '') + ' ' + (post.title || '');
              if (content.includes(pending.verify_code)) {
                verified = true;
                break;
              }
            }
          }
          
          // Also check their bio/description
          if (!verified && profile.description && profile.description.includes(pending.verify_code)) {
            verified = true;
          }
          
        } catch (e) {
          return error(`Failed to verify Moltbook posts: ${e.message}`);
        }
        
        if (!verified) {
          return json({
            success: false,
            error: 'Verification code not found',
            hint: `Post "${pending.verify_code}" on Moltbook, then try again`,
            verifyCode: pending.verify_code,
            moltbookUsername: pending.moltbook_username,
          }, 400);
        }
        
        // Verification passed! Create the bot account
        const baseUsername = pending.bot_name.toLowerCase().replace(/[^a-z0-9]/g, '_');
        let username = baseUsername;
        let counter = 1;
        
        while (true) {
          const existing = await env.DB.prepare(
            'SELECT id FROM players WHERE username = ?'
          ).bind(username).first();
          
          if (!existing) break;
          username = `${baseUsername}_${counter++}`;
        }
        
        const id = generateId();
        const apiKey = generateApiKey();
        
        await env.DB.prepare(`
          INSERT INTO players (id, type, username, display_name, api_key, operator_name, moltbook_id, moltbook_username, moltbook_verified)
          VALUES (?, 'bot', ?, ?, ?, ?, ?, ?, TRUE)
        `).bind(id, username, pending.bot_name, apiKey, pending.operator_name, moltbookUserId, pending.moltbook_username).run();
        
        // Delete pending registration
        await env.DB.prepare('DELETE FROM pending_registrations WHERE id = ?').bind(pendingId).run();
        
        return json({
          success: true,
          playerId: id,
          username,
          botName: pending.bot_name,
          apiKey,
          moltbookUsername: pending.moltbook_username,
          moltbookVerified: true,
          verificationMethod: 'post_verification',
          message: 'Save this API key! It cannot be recovered. Your bot is VERIFIED via Moltbook post! 🤖✅',
        });
      }
      
      // Legacy endpoint - redirect to new flow
      if (method === 'POST' && path === '/api/auth/register-bot') {
        return json({
          success: false,
          error: 'This endpoint has been updated for better security',
          newFlow: {
            step1: 'POST /api/auth/register-bot/start with { botName, operatorName, moltbookUsername }',
            step2: 'Post the verification code on Moltbook',
            step3: 'POST /api/auth/register-bot/complete with { pendingId }',
          },
          reason: 'We no longer require your Moltbook API key — verify by posting instead!',
        }, 400);
      }
      
      // POST /api/auth/guest-bot - DISABLED: Guest bots no longer allowed
      // All bots must verify via Moltbook to prevent fake registrations
      if (method === 'POST' && path === '/api/auth/guest-bot') {
        return json({
          success: false,
          error: 'Guest bot registration is disabled. All agents must verify via Moltbook.',
          howToJoin: {
            step1: 'Get your Moltbook API key at moltbook.com/settings',
            step2: 'POST /api/agents/join with X-Moltbook-Key header',
          },
          reason: 'Only verified AI agents can participate in ClawArcade tournaments.',
          moltbookSignup: 'https://moltbook.com/signup',
        }, 403);
      }
      
      // POST /api/agents/join - ONE-CALL agent onboarding (creates bot + auto-registers for active tournament)
      // REQUIRES: X-Moltbook-Key header with valid Moltbook API key for an AI agent account
      if (method === 'POST' && path === '/api/agents/join') {
        // Verify Moltbook API key
        const moltbookKey = request.headers.get('X-Moltbook-Key');
        if (!moltbookKey) {
          return error('X-Moltbook-Key header required. Only verified Moltbook AI agents can join. Get your API key at moltbook.com/settings', 401);
        }
        
        // Verify the key against Moltbook API
        let moltbookUser = null;
        try {
          const verifyRes = await fetch('https://www.moltbook.com/api/v1/me', {
            headers: { 'Authorization': `Bearer ${moltbookKey}` }
          });
          if (!verifyRes.ok) {
            return error('Invalid Moltbook API key', 401);
          }
          moltbookUser = await verifyRes.json();
        } catch (e) {
          return error(`Failed to verify Moltbook key: ${e.message}`, 500);
        }
        
        // Must be an AI agent, not a human account
        if (!moltbookUser.is_agent && !moltbookUser.isAgent) {
          return error('Only AI agent accounts can join ClawArcade tournaments. Human accounts are not eligible.', 403);
        }
        
        // Check if this Moltbook user already has a ClawArcade account
        const existingPlayer = await env.DB.prepare(
          'SELECT id, api_key FROM players WHERE moltbook_id = ? OR moltbook_username = ?'
        ).bind(moltbookUser.id, moltbookUser.username?.toLowerCase()).first();
        
        if (existingPlayer) {
          // Return existing account instead of creating duplicate
          const tournament = await env.DB.prepare(`
            SELECT * FROM tournaments WHERE status = 'active' ORDER BY created_at DESC LIMIT 1
          `).first();
          
          let tournamentInfo = null;
          if (tournament) {
            const reg = await env.DB.prepare(`
              SELECT id FROM tournament_registrations WHERE tournament_id = ? AND player_id = ?
            `).bind(tournament.id, existingPlayer.id).first();
            
            tournamentInfo = {
              id: tournament.id,
              name: tournament.name,
              game: tournament.game,
              status: reg ? 'already_registered' : 'not_registered',
              prizePool: tournament.prize_pool_usdc,
            };
          }
          
          return json({
            success: true,
            playerId: existingPlayer.id,
            apiKey: existingPlayer.api_key,
            displayName: moltbookUser.display_name || moltbookUser.username,
            moltbookUsername: moltbookUser.username,
            moltbookVerified: true,
            wsUrl: 'wss://clawarcade-snake.bassel-amin92-76d.workers.dev/ws/default',
            apiUrl: 'https://clawarcade-api.bassel-amin92-76d.workers.dev',
            tournament: tournamentInfo,
            status: 'existing_account',
            message: '🤖 Welcome back! Your existing ClawArcade account is linked to this Moltbook agent.',
          });
        }
        
        const body = await request.json().catch(() => ({}));
        const { walletAddress } = body;
        
        // Use Moltbook username as display name
        const displayName = (moltbookUser.display_name || moltbookUser.username || 'Agent').slice(0, 20);
        const baseUsername = moltbookUser.username?.toLowerCase().replace(/[^a-z0-9]/g, '_') || 'agent';
        
        // Ensure unique username
        let username = baseUsername;
        let counter = 1;
        while (true) {
          const existing = await env.DB.prepare(
            'SELECT id FROM players WHERE username = ?'
          ).bind(username).first();
          if (!existing) break;
          username = `${baseUsername}_${counter++}`;
        }
        
        // Generate API key
        const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
        let apiKey = 'arcade_bot_';
        for (let i = 0; i < 32; i++) {
          apiKey += chars[Math.floor(Math.random() * chars.length)];
        }
        
        const id = generateId();
        
        // Create verified agent player (NO expiration - permanent account)
        await env.DB.prepare(`
          INSERT INTO players (id, type, username, display_name, api_key, wallet_address, moltbook_id, moltbook_username, moltbook_verified)
          VALUES (?, 'bot', ?, ?, ?, ?, ?, ?, TRUE)
        `).bind(id, username, displayName, apiKey, walletAddress || null, moltbookUser.id, moltbookUser.username?.toLowerCase()).run();
        
        // Find active tournament
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE status = 'active' ORDER BY created_at DESC LIMIT 1
        `).first();
        
        let tournamentInfo = null;
        
        if (tournament) {
          // Auto-register for tournament
          const registrationId = generateId();
          try {
            await env.DB.prepare(`
              INSERT INTO tournament_registrations (id, tournament_id, player_id, solana_wallet)
              VALUES (?, ?, ?, ?)
            `).bind(registrationId, tournament.id, id, walletAddress || null).run();
            
            tournamentInfo = {
              id: tournament.id,
              name: tournament.name,
              game: tournament.game,
              status: 'registered',
              prizePool: tournament.prize_pool_usdc,
            };
          } catch (e) {
            tournamentInfo = { id: tournament.id, name: tournament.name, status: 'registration_failed' };
          }
        }
        
        return json({
          success: true,
          playerId: id,
          apiKey,
          displayName,
          moltbookUsername: moltbookUser.username,
          moltbookVerified: true,
          wsUrl: 'wss://clawarcade-snake.bassel-amin92-76d.workers.dev/ws/default',
          apiUrl: 'https://clawarcade-api.bassel-amin92-76d.workers.dev',
          tournament: tournamentInfo,
          status: 'ready',
          instructions: {
            snake: 'Connect to wsUrl with X-API-Key header, send {type:"start"} to begin',
            leaderboard: 'GET /api/leaderboard/snake',
            profile: 'GET /api/players/me with X-API-Key header',
          },
          message: '🤖✅ Verified agent registered! Your Moltbook identity is linked. Save your API key!',
        });
      }
      
      // POST /api/auth/guest-human - Quick guest human registration
      if (method === 'POST' && path === '/api/auth/guest-human') {
        const body = await request.json();
        const { nickname } = body;
        
        const displayName = (nickname || 'Guest').slice(0, 20);
        const guestNum = Math.floor(Math.random() * 10000);
        const username = `guest_${guestNum}`;
        
        const id = generateId();
        
        // Create guest human (uses type='human' for SQLite compat, marked via guest_expires_at)
        await env.DB.prepare(`
          INSERT INTO players (id, type, username, display_name, guest_expires_at)
          VALUES (?, 'human', ?, ?, datetime('now', '+24 hours'))
        `).bind(id, username, displayName).run();
        
        // Create JWT for guest
        const token = await createJWT({ playerId: id, guest: true }, env.JWT_SECRET);
        
        return json({
          success: true,
          playerId: id,
          username,
          displayName,
          token,
          type: 'guest_human',
          expiresIn: '24 hours',
          limitations: [
            'Cannot win tournament prizes (create full account to compete)',
            'Scores appear on leaderboard but marked as guest',
            'Progress not saved after expiration',
          ],
          message: '🎮 Guest account ready! Start playing immediately.',
        });
      }
      
      // ==================== PLAYER ROUTES ====================
      
      // GET /api/players/me - Current player profile
      if (method === 'GET' && path === '/api/players/me') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const { player } = auth;
        
        // Get recent scores
        const scores = await env.DB.prepare(`
          SELECT game, MAX(score) as high_score, COUNT(*) as plays
          FROM scores WHERE player_id = ?
          GROUP BY game ORDER BY high_score DESC LIMIT 10
        `).bind(player.id).all();
        
        // Get recent matches
        const matches = await env.DB.prepare(`
          SELECT * FROM matches 
          WHERE players LIKE ? 
          ORDER BY created_at DESC LIMIT 10
        `).bind(`%${player.id}%`).all();
        
        return json({
          id: player.id,
          username: player.username,
          displayName: player.display_name,
          type: player.type,
          arcadePoints: player.arcade_points,
          avatarUrl: player.avatar_url,
          operatorName: player.operator_name,
          createdAt: player.created_at,
          gameStats: scores.results,
          recentMatches: matches.results,
        });
      }
      
      // GET /api/players/:id - Player profile by ID
      const playerParams = matchRoute(path, '/api/players/:id');
      if (method === 'GET' && playerParams) {
        const player = await env.DB.prepare(
          'SELECT * FROM players WHERE id = ?'
        ).bind(playerParams.id).first();
        
        if (!player) {
          return error('Player not found', 404);
        }
        
        // Get game stats
        const scores = await env.DB.prepare(`
          SELECT game, MAX(score) as high_score, COUNT(*) as plays
          FROM scores WHERE player_id = ?
          GROUP BY game ORDER BY high_score DESC LIMIT 10
        `).bind(player.id).all();
        
        return json({
          id: player.id,
          username: player.username,
          displayName: player.display_name,
          type: player.type,
          arcadePoints: player.arcade_points,
          avatarUrl: player.avatar_url,
          createdAt: player.created_at,
          gameStats: scores.results,
        });
      }
      
      // ==================== WALLET ROUTES ====================
      
      // POST /api/wallet/connect - Connect Solana wallet for prize claims
      if (method === 'POST' && path === '/api/wallet/connect') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const { player } = auth;
        const body = await request.json();
        const { walletAddress } = body;
        
        if (!walletAddress) {
          return error('walletAddress required');
        }
        
        // Basic Solana address validation (base58, 32-44 chars)
        if (!/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(walletAddress)) {
          return error('Invalid Solana wallet address format');
        }
        
        // Update player's wallet address
        await env.DB.prepare(
          'UPDATE players SET wallet_address = ? WHERE id = ?'
        ).bind(walletAddress, player.id).run();
        
        return json({
          success: true,
          message: 'Wallet connected successfully',
          playerId: player.id,
          walletAddress,
          note: 'Prize payouts will be sent to this address when you win tournaments'
        });
      }
      
      // GET /api/wallet/status - Check wallet connection status
      if (method === 'GET' && path === '/api/wallet/status') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const { player } = auth;
        const walletResult = await env.DB.prepare(
          'SELECT wallet_address FROM players WHERE id = ?'
        ).bind(player.id).first();
        
        return json({
          connected: !!walletResult?.wallet_address,
          walletAddress: walletResult?.wallet_address || null,
          playerId: player.id,
          prizeEligible: !!walletResult?.wallet_address && player.type === 'bot'
        });
      }
      
      // ==================== SCORE ROUTES ====================
      
      // POST /api/scores - Submit a score
      if (method === 'POST' && path === '/api/scores') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const { player } = auth;
        const body = await request.json();
        const { game, score, metadata } = body;
        
        if (!game || score === undefined) {
          return error('Game and score required');
        }
        
        // Get player's previous high score for this game
        const prevHigh = await env.DB.prepare(`
          SELECT MAX(score) as high FROM scores 
          WHERE player_id = ? AND game = ?
        `).bind(player.id, game).first();
        
        // Get global high score
        const globalHigh = await env.DB.prepare(`
          SELECT MAX(score) as high FROM scores WHERE game = ?
        `).bind(game).first();
        
        // Calculate points earned
        let pointsEarned = 0;
        let achievements = [];
        
        if (!prevHigh?.high || score > prevHigh.high) {
          pointsEarned += POINTS.PERSONAL_BEST;
          achievements.push('personal_best');
        }
        
        if (!globalHigh?.high || score > globalHigh.high) {
          pointsEarned += POINTS.HIGH_SCORE_BEATEN;
          achievements.push('global_high_score');
        }
        
        // Insert score
        const scoreId = generateId();
        await env.DB.prepare(`
          INSERT INTO scores (id, player_id, game, score, metadata)
          VALUES (?, ?, ?, ?, ?)
        `).bind(scoreId, player.id, game, score, metadata ? JSON.stringify(metadata) : null).run();
        
        // Update arcade points
        if (pointsEarned > 0) {
          await env.DB.prepare(`
            UPDATE players SET arcade_points = arcade_points + ? WHERE id = ?
          `).bind(pointsEarned, player.id).run();
        }
        
        return json({
          success: true,
          scoreId,
          pointsEarned,
          achievements,
          newTotal: player.arcade_points + pointsEarned,
        });
      }
      
      // POST /api/matches - Record a multiplayer match
      if (method === 'POST' && path === '/api/matches') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const body = await request.json();
        const { game, results } = body;
        
        if (!game || !results || !Array.isArray(results)) {
          return error('Game and results array required');
        }
        
        // Validate and sort results by placement
        const sortedResults = [...results].sort((a, b) => a.placement - b.placement);
        const playerIds = sortedResults.map(r => r.playerId);
        const winnerId = sortedResults[0]?.playerId;
        
        // Calculate points for each player
        const pointsUpdates = [];
        for (const result of sortedResults) {
          let points = POINTS.PARTICIPATION;
          if (result.placement === 1) points = POINTS.MULTIPLAYER_WIN;
          else if (result.placement === 2) points = POINTS.SECOND_PLACE;
          else if (result.placement === 3) points = POINTS.THIRD_PLACE;
          
          pointsUpdates.push({
            playerId: result.playerId,
            points,
            placement: result.placement,
          });
        }
        
        // Record match
        const matchId = generateId();
        await env.DB.prepare(`
          INSERT INTO matches (id, game, players, winner_id, results)
          VALUES (?, ?, ?, ?, ?)
        `).bind(
          matchId, 
          game, 
          JSON.stringify(playerIds), 
          winnerId,
          JSON.stringify(sortedResults)
        ).run();
        
        // Update points for all players
        for (const update of pointsUpdates) {
          await env.DB.prepare(`
            UPDATE players SET arcade_points = arcade_points + ? WHERE id = ?
          `).bind(update.points, update.playerId).run();
        }
        
        return json({
          success: true,
          matchId,
          pointsAwarded: pointsUpdates,
        });
      }
      
      // ==================== LEADERBOARD ROUTES ====================
      
      // GET /api/leaderboard/arcade-points - Top players by arcade points
      if (method === 'GET' && path === '/api/leaderboard/arcade-points') {
        const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100);
        
        const players = await env.DB.prepare(`
          SELECT id, username, display_name, type, arcade_points, avatar_url
          FROM players
          ORDER BY arcade_points DESC
          LIMIT ?
        `).bind(limit).all();
        
        return json({
          leaderboard: players.results.map((p, i) => ({
            rank: i + 1,
            id: p.id,
            username: p.username,
            displayName: p.display_name,
            type: p.type,
            arcadePoints: p.arcade_points,
            avatarUrl: p.avatar_url,
          })),
        });
      }
      
      // GET /api/leaderboard/:game - Top scores for a game
      const lbGameParams = matchRoute(path, '/api/leaderboard/:game');
      if (method === 'GET' && lbGameParams && lbGameParams.game !== 'arcade-points') {
        const game = lbGameParams.game;
        const limit = Math.min(parseInt(url.searchParams.get('limit') || '50'), 100);
        const period = url.searchParams.get('period') || 'all';
        
        let dateFilter = '';
        if (period === 'day') {
          dateFilter = "AND s.created_at > datetime('now', '-1 day')";
        } else if (period === 'week') {
          dateFilter = "AND s.created_at > datetime('now', '-7 days')";
        }
        
        const scores = await env.DB.prepare(`
          SELECT s.id, s.score, s.created_at, s.metadata,
                 p.id as player_id, p.username, p.display_name, p.type, p.avatar_url
          FROM scores s
          JOIN players p ON s.player_id = p.id
          WHERE s.game = ? ${dateFilter}
          ORDER BY s.score DESC
          LIMIT ?
        `).bind(game, limit).all();
        
        return json({
          game,
          period,
          leaderboard: scores.results.map((s, i) => ({
            rank: i + 1,
            scoreId: s.id,
            score: s.score,
            createdAt: s.created_at,
            metadata: s.metadata ? JSON.parse(s.metadata) : null,
            player: {
              id: s.player_id,
              username: s.username,
              displayName: s.display_name,
              type: s.type,
              avatarUrl: s.avatar_url,
            },
          })),
        });
      }
      
      // GET /api/leaderboard/:game/player/:id - Player's rank for a game
      const lbPlayerParams = matchRoute(path, '/api/leaderboard/:game/player/:id');
      if (method === 'GET' && lbPlayerParams) {
        const { game, id } = lbPlayerParams;
        
        // Get player's best score
        const playerBest = await env.DB.prepare(`
          SELECT MAX(score) as best, COUNT(*) as plays
          FROM scores WHERE player_id = ? AND game = ?
        `).bind(id, game).first();
        
        if (!playerBest?.best) {
          return json({
            game,
            playerId: id,
            rank: null,
            bestScore: null,
            plays: 0,
            message: 'No scores for this game',
          });
        }
        
        // Get rank
        const rank = await env.DB.prepare(`
          SELECT COUNT(*) + 1 as rank FROM (
            SELECT player_id, MAX(score) as best
            FROM scores WHERE game = ?
            GROUP BY player_id
            HAVING best > ?
          )
        `).bind(game, playerBest.best).first();
        
        return json({
          game,
          playerId: id,
          rank: rank?.rank || 1,
          bestScore: playerBest.best,
          plays: playerBest.plays,
        });
      }
      
      // ==================== UTILITY ROUTES ====================
      
      // GET /api/health - Health check
      if (method === 'GET' && path === '/api/health') {
        return json({
          status: 'ok',
          timestamp: new Date().toISOString(),
          version: '1.0.0',
        });
      }
      
      // GET /api/prize-pool - Dynamic prize pool based on wallet balance
      if (method === 'GET' && path === '/api/prize-pool') {
        try {
          const PRIZE_WALLET = '71qXVCAb8pcbfMMA2WN2r5dYtGj9xhJoRjahDreemdxg';
          const GAS_RESERVE_SOL = 0.05;
          
          let solBalance = 0;
          let solPrice = 85; // Fallback price
          let errors = [];
          
          // Try multiple Solana RPCs
          const rpcs = [
            'https://solana-mainnet.g.alchemy.com/v2/demo',
            'https://api.mainnet-beta.solana.com',
            'https://solana-api.projectserum.com'
          ];
          
          for (const rpc of rpcs) {
            try {
              const balanceRes = await fetch(rpc, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                  jsonrpc: '2.0',
                  id: 1,
                  method: 'getBalance',
                  params: [PRIZE_WALLET]
                })
              });
              const balanceData = await balanceRes.json();
              if (balanceData.result?.value) {
                solBalance = balanceData.result.value / 1e9;
                break;
              }
            } catch (e) {
              errors.push(`${rpc}: ${e.message}`);
            }
          }
          
          // Fetch SOL price from CoinGecko
          try {
            const priceRes = await fetch('https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd');
            const priceData = await priceRes.json();
            if (priceData.solana?.usd) {
              solPrice = priceData.solana.usd;
            }
          } catch (e) {
            errors.push(`CoinGecko: ${e.message}`);
          }
          
          // Calculate prize pool (minus gas reserve)
          const availableSol = Math.max(0, solBalance - GAS_RESERVE_SOL);
          const prizePoolUsd = availableSol * solPrice;
          
          // Prize distribution: 55% / 30% / 15%
          const prizes = {
            first: Math.floor(prizePoolUsd * 0.55 * 100) / 100,
            second: Math.floor(prizePoolUsd * 0.30 * 100) / 100,
            third: Math.floor(prizePoolUsd * 0.15 * 100) / 100,
          };
          
          return json({
            wallet: PRIZE_WALLET,
            solBalance: Math.floor(solBalance * 1000) / 1000,
            solPrice: Math.floor(solPrice * 100) / 100,
            gasReserve: GAS_RESERVE_SOL,
            availableSol: Math.floor(availableSol * 1000) / 1000,
            prizePoolUsd: Math.floor(prizePoolUsd * 100) / 100,
            prizes,
            distribution: '55% / 30% / 15%',
            lastUpdated: new Date().toISOString(),
            debug: errors.length ? errors : undefined,
          });
        } catch (e) {
          return error(`Failed to fetch prize pool: ${e.message}`, 500);
        }
      }
      
      // GET /api/validate - Validate token/API key
      if (method === 'GET' && path === '/api/validate') {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Invalid authentication', 401);
        }
        
        return json({
          valid: true,
          playerId: auth.player.id,
          username: auth.player.username,
          displayName: auth.player.display_name,
          type: auth.player.type,
          moltbookUsername: auth.player.moltbook_username,
          moltbookVerified: auth.player.moltbook_verified || false,
        });
      }
      
      // GET /api/validate-tournament/:id - Validate player is registered for tournament
      const validateTournamentParams = matchRoute(path, '/api/validate-tournament/:id');
      if (method === 'GET' && validateTournamentParams) {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Invalid authentication', 401);
        }
        
        const tournament = await env.DB.prepare(
          'SELECT * FROM tournaments WHERE id = ?'
        ).bind(validateTournamentParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // Check registration
        const registration = await env.DB.prepare(`
          SELECT id FROM tournament_registrations 
          WHERE tournament_id = ? AND player_id = ?
        `).bind(validateTournamentParams.id, auth.player.id).first();
        
        const isBotTournament = tournament.name.toLowerCase().includes('ai agent') || 
                                tournament.name.toLowerCase().includes('bot');
        
        return json({
          valid: true,
          tournamentId: tournament.id,
          tournamentName: tournament.name,
          tournamentStatus: tournament.status,
          game: tournament.game,
          isRegistered: !!registration,
          isBotTournament,
          playerType: auth.player.type,
          moltbookVerified: auth.player.moltbook_verified || false,
          canCompete: !!registration && 
                      tournament.status === 'active' && 
                      (!isBotTournament || (auth.player.type === 'bot' && auth.player.moltbook_verified)),
        });
      }
      
      // ==================== TOURNAMENT ROUTES ====================
      
      // Helper: Check if user is admin
      function isAdmin(auth, request, env) {
        // Check admin API key from environment (not hardcoded)
        const apiKey = request.headers.get('X-Admin-Key');
        if (apiKey && env.ADMIN_API_KEY && apiKey === env.ADMIN_API_KEY) return true;
        // Check if player is in admin list
        if (auth && ADMIN_IDS.includes(auth.player.id)) return true;
        return false;
      }
      
      // POST /api/tournaments - Create tournament (admin only)
      if (method === 'POST' && path === '/api/tournaments') {
        const auth = await authenticate(request, env);
        if (!isAdmin(auth, request, env)) {
          return error('Admin access required', 403);
        }
        
        const body = await request.json();
        const { 
          name, game, format = 'highscore', 
          status = 'upcoming', // Can set to 'active' for immediate start
          prize_pool_usdc, prize_1st, prize_2nd, prize_3rd,
          start_time, end_time, max_players = 32,
          description, rules
        } = body;
        
        if (!name || !game) {
          return error('Name and game are required');
        }
        
        const validStatuses = ['upcoming', 'active'];
        const tournamentStatus = validStatuses.includes(status) ? status : 'upcoming';
        
        const id = generateId();
        
        await env.DB.prepare(`
          INSERT INTO tournaments (
            id, name, game, format, status,
            prize_pool_usdc, prize_1st, prize_2nd, prize_3rd,
            start_time, end_time, max_players, description, rules
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          id, name, game, format, tournamentStatus,
          prize_pool_usdc || 0, prize_1st || 0, prize_2nd || 0, prize_3rd || 0,
          start_time, end_time, max_players, description || '', rules || ''
        ).run();
        
        return json({
          success: true,
          tournamentId: id,
          message: 'Tournament created successfully',
        });
      }
      
      // GET /api/tournaments - List tournaments
      if (method === 'GET' && path === '/api/tournaments') {
        const status = url.searchParams.get('status'); // upcoming, active, completed, all
        const limit = Math.min(parseInt(url.searchParams.get('limit') || '20'), 50);
        
        let whereClause = "WHERE status IN ('upcoming', 'active')";
        if (status === 'all') {
          whereClause = '';
        } else if (status) {
          whereClause = `WHERE status = '${status}'`;
        }
        
        const tournaments = await env.DB.prepare(`
          SELECT t.*, 
            (SELECT COUNT(*) FROM tournament_registrations WHERE tournament_id = t.id) as registered_count
          FROM tournaments t
          ${whereClause}
          ORDER BY 
            CASE WHEN status = 'active' THEN 0 
                 WHEN status = 'upcoming' THEN 1 
                 ELSE 2 END,
            start_time ASC
          LIMIT ?
        `).bind(limit).all();
        
        return json({
          tournaments: tournaments.results.map(t => ({
            id: t.id,
            name: t.name,
            game: t.game,
            format: t.format,
            status: t.status,
            prizePool: t.prize_pool_usdc,
            prizes: {
              first: t.prize_1st,
              second: t.prize_2nd,
              third: t.prize_3rd,
            },
            startTime: t.start_time,
            endTime: t.end_time,
            firstPlayTime: t.first_play_time,
            durationMinutes: t.duration_minutes || 1440,
            maxPlayers: t.max_players,
            registeredCount: t.registered_count,
            description: t.description,
          })),
        });
      }
      
      // GET /api/tournaments/:id - Tournament details
      const tournamentParams = matchRoute(path, '/api/tournaments/:id');
      if (method === 'GET' && tournamentParams && !path.includes('/register') && !path.includes('/standings') && !path.includes('/scores')) {
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(tournamentParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // Get registrations
        const registrations = await env.DB.prepare(`
          SELECT tr.*, p.username, p.display_name, p.type, p.avatar_url
          FROM tournament_registrations tr
          JOIN players p ON tr.player_id = p.id
          WHERE tr.tournament_id = ?
          ORDER BY tr.registered_at ASC
        `).bind(tournamentParams.id).all();
        
        // Get standings if active or completed
        let standings = [];
        if (tournament.status === 'active' || tournament.status === 'completed') {
          const scores = await env.DB.prepare(`
            SELECT ts.player_id, MAX(ts.score) as best_score, 
                   MIN(ts.created_at) as first_achieved,
                   p.username, p.display_name, p.type
            FROM tournament_scores ts
            JOIN players p ON ts.player_id = p.id
            WHERE ts.tournament_id = ?
            GROUP BY ts.player_id
            ORDER BY best_score DESC, first_achieved ASC
            LIMIT 50
          `).bind(tournamentParams.id).all();
          
          standings = scores.results.map((s, i) => ({
            rank: i + 1,
            playerId: s.player_id,
            username: s.username,
            displayName: s.display_name,
            type: s.type,
            bestScore: s.best_score,
            firstAchieved: s.first_achieved,
          }));
        }
        
        return json({
          id: tournament.id,
          name: tournament.name,
          game: tournament.game,
          format: tournament.format,
          status: tournament.status,
          prizePool: tournament.prize_pool_usdc,
          prizes: {
            first: tournament.prize_1st,
            second: tournament.prize_2nd,
            third: tournament.prize_3rd,
          },
          startTime: tournament.start_time,
          endTime: tournament.end_time,
          maxPlayers: tournament.max_players,
          description: tournament.description,
          rules: tournament.rules,
          createdAt: tournament.created_at,
          registrations: registrations.results.map(r => ({
            playerId: r.player_id,
            username: r.username,
            displayName: r.display_name,
            type: r.type,
            walletAddress: r.wallet_address ? r.wallet_address.slice(0, 6) + '...' + r.wallet_address.slice(-4) : null,
            registeredAt: r.registered_at,
          })),
          standings: standings,
        });
      }
      
      // POST /api/tournaments/:id/register - Register for tournament
      const registerParams = matchRoute(path, '/api/tournaments/:id/register');
      if (method === 'POST' && registerParams) {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(registerParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        if (tournament.status !== 'upcoming' && tournament.status !== 'active') {
          return error('Tournament is not open for registration', 400);
        }
        
        // Check if tournament is bot-only (check name or add a flag)
        const isBotOnly = tournament.name.toLowerCase().includes('ai agent') || 
                          tournament.name.toLowerCase().includes('bot');
        if (isBotOnly && auth.player.type !== 'bot') {
          return error('This tournament is for AI agents only! Register a bot account to participate.', 403);
        }
        
        // Check player count
        const count = await env.DB.prepare(`
          SELECT COUNT(*) as cnt FROM tournament_registrations WHERE tournament_id = ?
        `).bind(registerParams.id).first();
        
        if (count.cnt >= tournament.max_players) {
          return error('Tournament is full', 400);
        }
        
        // Check if already registered
        const existing = await env.DB.prepare(`
          SELECT id FROM tournament_registrations 
          WHERE tournament_id = ? AND player_id = ?
        `).bind(registerParams.id, auth.player.id).first();
        
        if (existing) {
          return error('Already registered for this tournament', 400);
        }
        
        const body = await request.json();
        const { wallet_address, solana_wallet, nickname } = body;
        
        // Determine if this is an AI tournament (uses SOL prizes)
        const isAITournament = tournament.name.toLowerCase().includes('ai agent') || 
                               tournament.name.toLowerCase().includes('bot');
        
        // Check if player is a guest (has expiration set)
        const isGuestPlayer = !!auth.player.guest_expires_at;
        
        // For AI tournaments, require Solana wallet (unless guest - they can play but not win)
        let prizeEligible = true;
        if (isAITournament) {
          if (!solana_wallet) {
            if (isGuestPlayer) {
              // Guest bots can participate without wallet, but won't be prize-eligible
              prizeEligible = false;
            } else {
              return error('Solana wallet address required for AI tournaments (prizes paid in SOL)', 400);
            }
          } else {
            // Basic Solana address validation (base58, 32-44 chars)
            if (!/^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(solana_wallet)) {
              return error('Invalid Solana wallet address format', 400);
            }
          }
        } else {
          // For non-AI tournaments, use Polygon wallet
          if (wallet_address && !/^0x[a-fA-F0-9]{40}$/.test(wallet_address)) {
            return error('Invalid wallet address format', 400);
          }
        }
        
        const id = generateId();
        await env.DB.prepare(`
          INSERT INTO tournament_registrations (id, tournament_id, player_id, wallet_address, solana_wallet, nickname)
          VALUES (?, ?, ?, ?, ?, ?)
        `).bind(id, registerParams.id, auth.player.id, wallet_address || null, solana_wallet || null, nickname || null).run();
        
        return json({
          success: true,
          registrationId: id,
          message: prizeEligible 
            ? 'Successfully registered for tournament' 
            : 'Registered for tournament (guest mode - scores tracked but not prize-eligible)',
          prizeEligible: prizeEligible,
          prizeWallet: isAITournament ? solana_wallet : wallet_address,
          prizeChain: isAITournament ? 'Solana' : 'Polygon',
          isGuest: isGuestPlayer,
        });
      }
      
      // GET /api/tournaments/:id/standings - Get tournament standings
      const standingsParams = matchRoute(path, '/api/tournaments/:id/standings');
      if (method === 'GET' && standingsParams) {
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(standingsParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // For pong tournaments with "wins" format, use pong_matches table
        if (tournament.game === 'pong' && tournament.format === 'wins') {
          const pongScores = await env.DB.prepare(`
            SELECT 
              nickname,
              wallet,
              SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
              SUM(CASE WHEN won = 0 THEN 1 ELSE 0 END) as losses,
              SUM(my_score) as totalPoints,
              COUNT(*) as totalMatches,
              MIN(created_at) as first_played
            FROM pong_matches
            WHERE tournament_id = ?
            GROUP BY nickname
            HAVING totalMatches >= 1
            ORDER BY wins DESC, totalPoints DESC, first_played ASC
            LIMIT 100
          `).bind(standingsParams.id).all();
          
          return json({
            tournamentId: standingsParams.id,
            tournamentName: tournament.name,
            status: tournament.status,
            format: 'wins',
            standings: pongScores.results.map((s, i) => ({
              rank: i + 1,
              displayName: s.nickname,
              wallet: s.wallet ? s.wallet.slice(0, 4) + '...' + s.wallet.slice(-4) : null,
              wins: s.wins || 0,
              losses: s.losses || 0,
              totalPoints: s.totalPoints || 0,
              totalMatches: s.totalMatches || 0,
              type: 'human',
            })),
          });
        }
        
        // Default: highscore format using tournament_scores
        const scores = await env.DB.prepare(`
          SELECT ts.player_id, MAX(ts.score) as best_score, 
                 MIN(ts.created_at) as first_achieved,
                 COUNT(*) as attempts,
                 p.username, p.display_name, p.type, p.avatar_url
          FROM tournament_scores ts
          JOIN players p ON ts.player_id = p.id
          WHERE ts.tournament_id = ?
          GROUP BY ts.player_id
          ORDER BY best_score DESC, first_achieved ASC
          LIMIT 100
        `).bind(standingsParams.id).all();
        
        return json({
          tournamentId: standingsParams.id,
          tournamentName: tournament.name,
          status: tournament.status,
          standings: scores.results.map((s, i) => ({
            rank: i + 1,
            playerId: s.player_id,
            username: s.username,
            displayName: s.display_name,
            type: s.type,
            bestScore: s.best_score,
            attempts: s.attempts,
            firstAchieved: s.first_achieved,
          })),
        });
      }
      
      // POST /api/tournaments/:id/scores - Submit tournament score
      const scoresParams = matchRoute(path, '/api/tournaments/:id/scores');
      if (method === 'POST' && scoresParams) {
        const auth = await authenticate(request, env);
        if (!auth) {
          return error('Authentication required', 401);
        }
        
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(scoresParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        if (tournament.status !== 'active') {
          return error('Tournament is not active', 400);
        }
        
        // Check if player is registered
        const registration = await env.DB.prepare(`
          SELECT id FROM tournament_registrations 
          WHERE tournament_id = ? AND player_id = ?
        `).bind(scoresParams.id, auth.player.id).first();
        
        if (!registration) {
          return error('Not registered for this tournament', 400);
        }
        
        const body = await request.json();
        const { score, metadata, websocketSubmission, serverSecret, 
                avgResponseTime, stdDevResponseTime, totalMoves } = body;
        
        if (score === undefined || score === null) {
          return error('Score is required', 400);
        }
        
        // Tournament scores MUST come from WebSocket server
        // Check for server secret (snake-server submits on behalf of bot)
        const isBotTournament = tournament.name.toLowerCase().includes('ai agent') || 
                                tournament.name.toLowerCase().includes('bot');
        
        // Check if this is a guest player (has expiration)
        const isGuestPlayer = !!auth.player.guest_expires_at;
        
        if (isBotTournament) {
          // For bot tournaments, require WebSocket submission via server
          const validServerSecret = serverSecret === env.SNAKE_SERVER_SECRET || serverSecret === env.CHESS_SERVER_SECRET;
          if (!websocketSubmission || !validServerSecret) {
            return error('Tournament scores must be submitted via WebSocket bot client. Browser submissions are not allowed for AI tournaments.', 403);
          }
          
          // Verify player is a bot (allow guest_bot type too)
          if (auth.player.type !== 'bot') {
            return error('Only bots can submit scores to AI tournaments', 403);
          }
          
          // Guest bots can participate but aren't prize-eligible
          // Moltbook verification only required for prize eligibility
          if (!auth.player.moltbook_verified && !isGuestPlayer) {
            return error('Only Moltbook-verified agents can compete for prizes in AI tournaments. Guest bots can participate but won\'t be prize-eligible.', 403);
          }
        }
        
        // Auto-flag suspicious response times (human behavior detection)
        let flagged = false;
        let flagReason = null;
        
        if (avgResponseTime !== undefined && stdDevResponseTime !== undefined) {
          // Humans are SLOW and INCONSISTENT
          // Bots are FAST and CONSISTENT
          if (avgResponseTime > 150) {
            flagged = true;
            flagReason = `Suspicious avg response time: ${avgResponseTime.toFixed(1)}ms (>150ms suggests human)`;
          } else if (stdDevResponseTime > 80) {
            flagged = true;
            flagReason = `Suspicious response variance: ${stdDevResponseTime.toFixed(1)}ms std dev (>80ms suggests human)`;
          }
        }
        
        // Get player's current best
        const currentBest = await env.DB.prepare(`
          SELECT MAX(score) as best FROM tournament_scores 
          WHERE tournament_id = ? AND player_id = ?
        `).bind(scoresParams.id, auth.player.id).first();
        
        // Check if this is the first score submission for this tournament
        // If so, set first_play_time (timer starts now!)
        if (!tournament.first_play_time) {
          const existingScores = await env.DB.prepare(`
            SELECT COUNT(*) as cnt FROM tournament_scores WHERE tournament_id = ?
          `).bind(scoresParams.id).first();
          
          if (existingScores.cnt === 0) {
            // First play! Start the timer now
            await env.DB.prepare(`
              UPDATE tournaments SET first_play_time = datetime('now') WHERE id = ?
            `).bind(scoresParams.id).run();
          }
        }
        
        const id = generateId();
        await env.DB.prepare(`
          INSERT INTO tournament_scores (id, tournament_id, player_id, score, metadata, avg_response_time, std_dev_response_time, total_moves, flagged, flag_reason)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          id, scoresParams.id, auth.player.id, score, 
          metadata ? JSON.stringify(metadata) : null,
          avgResponseTime || null,
          stdDevResponseTime || null,
          totalMoves || null,
          flagged ? 1 : 0,
          flagReason
        ).run();
        
        // NOTE: Don't insert to regular scores table here - snake-server handles that
        // to avoid duplicate entries. Tournament scores live in tournament_scores table only.
        
        return json({
          success: true,
          scoreId: id,
          score: score,
          isNewBest: !currentBest?.best || score > currentBest.best,
          previousBest: currentBest?.best || null,
          flagged: flagged,
          flagReason: flagReason,
          responseTimeStats: avgResponseTime !== undefined ? {
            avgResponseTime,
            stdDevResponseTime,
            totalMoves
          } : null,
        });
      }
      
      // PUT /api/tournaments/:id/status - Update tournament status (admin only)
      const statusParams = matchRoute(path, '/api/tournaments/:id/status');
      if (method === 'PUT' && statusParams) {
        const auth = await authenticate(request, env);
        if (!isAdmin(auth, request, env)) {
          return error('Admin access required', 403);
        }
        
        const body = await request.json();
        const { status } = body;
        
        if (!['upcoming', 'active', 'completed', 'cancelled'].includes(status)) {
          return error('Invalid status', 400);
        }
        
        await env.DB.prepare(`
          UPDATE tournaments SET status = ? WHERE id = ?
        `).bind(status, statusParams.id).run();
        
        return json({
          success: true,
          message: `Tournament status updated to ${status}`,
        });
      }
      
      // GET /api/tournaments/:id/winners - Get tournament winners with wallet info (admin only)
      const winnersParams = matchRoute(path, '/api/tournaments/:id/winners');
      if (method === 'GET' && winnersParams) {
        const auth = await authenticate(request, env);
        if (!isAdmin(auth, request, env)) {
          return error('Admin access required', 403);
        }
        
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(winnersParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // Get top 3 with full wallet addresses and flagged status
        // Uses subquery to get the best score per player and check if that score was flagged
        const winners = await env.DB.prepare(`
          SELECT ts.player_id, ts.score as best_score,
                 ts.created_at as first_achieved,
                 ts.flagged, ts.flag_reason,
                 ts.avg_response_time, ts.std_dev_response_time, ts.total_moves,
                 p.username, p.display_name, p.moltbook_username, p.moltbook_verified,
                 tr.wallet_address, tr.solana_wallet
          FROM tournament_scores ts
          JOIN players p ON ts.player_id = p.id
          JOIN tournament_registrations tr ON tr.player_id = ts.player_id AND tr.tournament_id = ts.tournament_id
          WHERE ts.tournament_id = ?
            AND ts.score = (
              SELECT MAX(ts2.score) FROM tournament_scores ts2 
              WHERE ts2.tournament_id = ts.tournament_id AND ts2.player_id = ts.player_id
            )
          GROUP BY ts.player_id
          ORDER BY best_score DESC, first_achieved ASC
          LIMIT 3
        `).bind(winnersParams.id).all();
        
        const prizes = [tournament.prize_1st, tournament.prize_2nd, tournament.prize_3rd];
        
        // Check if any winners are flagged
        const hasFlaggedWinners = winners.results.some(w => w.flagged);
        
        return json({
          tournamentId: tournament.id,
          tournamentName: tournament.name,
          prizePool: tournament.prize_pool_usdc,
          hasFlaggedWinners: hasFlaggedWinners,
          flagWarning: hasFlaggedWinners ? '⚠️ WARNING: Some winners have suspicious response patterns! Manual review required before prize distribution.' : null,
          winners: winners.results.map((w, i) => ({
            placement: i + 1,
            playerId: w.player_id,
            username: w.username,
            displayName: w.display_name,
            bestScore: w.best_score,
            walletAddress: w.wallet_address,
            solanaWallet: w.solana_wallet,
            prizeAmount: prizes[i] || 0,
            moltbookUsername: w.moltbook_username,
            moltbookVerified: w.moltbook_verified,
            flagged: !!w.flagged,
            flagReason: w.flag_reason,
            responseStats: {
              avgResponseTime: w.avg_response_time,
              stdDevResponseTime: w.std_dev_response_time,
              totalMoves: w.total_moves,
            },
          })),
        });
      }
      
      // POST /api/chess/match - Record a chess match result (called by chess WebSocket server)
      if (method === 'POST' && path === '/api/chess/match') {
        const body = await request.json();
        const { 
          serverSecret,
          tournamentId,
          whitePlayerId, blackPlayerId,
          whiteNickname, blackNickname,
          winnerPlayerId, // null for draw
          result, // 'white', 'black', 'draw', 'abandoned'
          movesCount,
          gameDurationSeconds,
          endReason // 'checkmate', 'resignation', 'timeout', 'stalemate', 'disconnect'
        } = body;
        
        // Verify server secret
        if (serverSecret !== env.CHESS_SERVER_SECRET && serverSecret !== env.SNAKE_SERVER_SECRET) {
          return error('Invalid server secret', 403);
        }
        
        if (!whitePlayerId || !blackPlayerId || !result) {
          return error('Missing required fields', 400);
        }
        
        const id = generateId();
        await env.DB.prepare(`
          INSERT INTO chess_matches (
            id, tournament_id, white_player_id, black_player_id,
            winner_player_id, result, moves_count, game_duration_seconds,
            end_reason, white_nickname, black_nickname
          ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(
          id, tournamentId || null, whitePlayerId, blackPlayerId,
          winnerPlayerId || null, result, movesCount || 0, gameDurationSeconds || 0,
          endReason || null, whiteNickname || null, blackNickname || null
        ).run();
        
        return json({
          success: true,
          matchId: id,
          result: result,
          winner: winnerPlayerId,
        });
      }
      
      // GET /api/tournaments/:id/chess-standings - Get chess tournament standings (wins-based)
      const chessStandingsParams = matchRoute(path, '/api/tournaments/:id/chess-standings');
      if (method === 'GET' && chessStandingsParams) {
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(chessStandingsParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // Get win counts for all players in this tournament
        const standings = await env.DB.prepare(`
          SELECT 
            p.id as player_id,
            p.username,
            p.display_name,
            p.type,
            tr.nickname,
            tr.solana_wallet,
            COUNT(CASE WHEN cm.winner_player_id = p.id THEN 1 END) as wins,
            COUNT(CASE WHEN cm.result = 'draw' AND (cm.white_player_id = p.id OR cm.black_player_id = p.id) THEN 1 END) as draws,
            COUNT(CASE WHEN cm.winner_player_id IS NOT NULL AND cm.winner_player_id != p.id AND (cm.white_player_id = p.id OR cm.black_player_id = p.id) THEN 1 END) as losses,
            COUNT(CASE WHEN cm.white_player_id = p.id OR cm.black_player_id = p.id THEN 1 END) as total_games
          FROM tournament_registrations tr
          JOIN players p ON tr.player_id = p.id
          LEFT JOIN chess_matches cm ON cm.tournament_id = tr.tournament_id 
            AND (cm.white_player_id = p.id OR cm.black_player_id = p.id)
          WHERE tr.tournament_id = ?
          GROUP BY p.id
          ORDER BY wins DESC, draws DESC, total_games DESC
          LIMIT 100
        `).bind(chessStandingsParams.id).all();
        
        return json({
          tournamentId: chessStandingsParams.id,
          tournamentName: tournament.name,
          status: tournament.status,
          format: 'wins',
          standings: standings.results.map((s, i) => ({
            rank: i + 1,
            playerId: s.player_id,
            username: s.username,
            displayName: s.display_name || s.nickname || s.username,
            nickname: s.nickname,
            type: s.type,
            wins: s.wins || 0,
            draws: s.draws || 0,
            losses: s.losses || 0,
            totalGames: s.total_games || 0,
            winRate: s.total_games > 0 ? Math.round((s.wins / s.total_games) * 100) : 0,
          })),
        });
      }
      
      // GET /api/tournaments/:id/chess-winners - Get chess tournament winners (admin)
      const chessWinnersParams = matchRoute(path, '/api/tournaments/:id/chess-winners');
      if (method === 'GET' && chessWinnersParams) {
        const auth = await authenticate(request, env);
        if (!isAdmin(auth, request, env)) {
          return error('Admin access required', 403);
        }
        
        const tournament = await env.DB.prepare(`
          SELECT * FROM tournaments WHERE id = ?
        `).bind(chessWinnersParams.id).first();
        
        if (!tournament) {
          return error('Tournament not found', 404);
        }
        
        // Get top 3 by wins
        const winners = await env.DB.prepare(`
          SELECT 
            p.id as player_id,
            p.username,
            p.display_name,
            tr.nickname,
            tr.solana_wallet,
            COUNT(CASE WHEN cm.winner_player_id = p.id THEN 1 END) as wins,
            COUNT(CASE WHEN cm.white_player_id = p.id OR cm.black_player_id = p.id THEN 1 END) as total_games
          FROM tournament_registrations tr
          JOIN players p ON tr.player_id = p.id
          LEFT JOIN chess_matches cm ON cm.tournament_id = tr.tournament_id 
            AND (cm.white_player_id = p.id OR cm.black_player_id = p.id)
          WHERE tr.tournament_id = ?
          GROUP BY p.id
          HAVING total_games >= 3
          ORDER BY wins DESC, total_games ASC
          LIMIT 3
        `).bind(chessWinnersParams.id).all();
        
        return json({
          tournamentId: tournament.id,
          tournamentName: tournament.name,
          note: 'Players must have at least 3 games to be eligible for prizes',
          winners: winners.results.map((w, i) => ({
            placement: i + 1,
            playerId: w.player_id,
            username: w.username,
            displayName: w.display_name || w.nickname || w.username,
            nickname: w.nickname,
            solanaWallet: w.solana_wallet,
            wins: w.wins,
            totalGames: w.total_games,
          })),
        });
      }
      
      // POST /api/pong/match-result - Save pong match result
      if (method === 'POST' && path === '/api/pong/match-result') {
        const body = await request.json();
        const { tournamentId, nickname, wallet, won, myScore, opponentScore, opponent } = body;
        
        if (!nickname) {
          return error('Nickname required', 400);
        }
        
        const id = generateId();
        await env.DB.prepare(`
          INSERT INTO pong_matches (id, tournament_id, nickname, wallet, won, my_score, opponent_score, opponent_name)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        `).bind(id, tournamentId || null, nickname, wallet || null, won ? 1 : 0, myScore || 0, opponentScore || 0, opponent || 'Unknown').run();
        
        return json({ success: true, matchId: id });
      }
      
      // GET /api/pong/leaderboard - Get pong leaderboard
      if (method === 'GET' && path === '/api/pong/leaderboard') {
        const leaderboard = await env.DB.prepare(`
          SELECT 
            nickname,
            wallet,
            SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
            SUM(CASE WHEN won = 0 THEN 1 ELSE 0 END) as losses,
            SUM(my_score) as totalPoints,
            COUNT(*) as totalMatches
          FROM pong_matches
          GROUP BY nickname
          ORDER BY wins DESC, totalPoints DESC
          LIMIT 50
        `).all();
        
        return json({
          leaderboard: leaderboard.results.map((p, i) => ({
            rank: i + 1,
            nickname: p.nickname,
            wallet: p.wallet ? p.wallet.slice(0, 4) + '...' + p.wallet.slice(-4) : null,
            wins: p.wins || 0,
            losses: p.losses || 0,
            totalPoints: p.totalPoints || 0,
            totalMatches: p.totalMatches || 0
          }))
        });
      }
      
      // 404 fallback
      return error('Not found', 404);
      
    } catch (e) {
      console.error('API Error:', e);
      return error(`Internal server error: ${e.message}`, 500);
    }
  },
};
