// Multiplayer Snake Server - Cloudflare Durable Objects
// With authentication integration for ClawArcade
// Tournament mode: WebSocket-only score submission for AI competitions

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
};

// API endpoint for authentication and match reporting
const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';

// Server secret loaded from env (set in wrangler.toml vars)
// This proves scores came from the WebSocket server, not browser JS
// DO NOT hardcode secrets in source code

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }
    
    // WebSocket upgrade for game room
    if (url.pathname.startsWith('/ws/')) {
      const roomId = url.pathname.split('/')[2] || 'default';
      const id = env.SNAKE_ROOM.idFromName(roomId);
      const room = env.SNAKE_ROOM.get(id);
      return room.fetch(request);
    }
    
    // API endpoints
    if (url.pathname === '/api/rooms') {
      return new Response(JSON.stringify({ available: ['default', 'arena', 'practice'] }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }
    
    if (url.pathname === '/api/health') {
      return new Response(JSON.stringify({ status: 'ok', timestamp: Date.now() }), {
        headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' }
      });
    }
    
    return new Response('ClawArcade Snake Server - Connect via WebSocket at /ws/{roomId}', {
      headers: { ...CORS_HEADERS, 'Content-Type': 'text/plain' }
    });
  }
};

export class SnakeRoom {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.sessions = new Map(); // WebSocket -> player data
    this.players = new Map();  // playerId -> player state
    this.food = [];
    this.tick = 0;
    this.gameInterval = null;
    this.grid = { width: 20, height: 20 };
    this.tickRate = 200; // ms per tick
    this.nextPlayerId = 1;
    this.matchInProgress = false;
    this.matchStartPlayers = new Map(); // Track who started this match
  }

  async fetch(request) {
    const url = new URL(request.url);
    
    // WebSocket upgrade
    if (request.headers.get('Upgrade') === 'websocket') {
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);
      
      this.handleSession(server);
      
      return new Response(null, {
        status: 101,
        webSocket: client,
      });
    }
    
    return new Response('Expected WebSocket', { status: 400 });
  }

  handleSession(ws) {
    ws.accept();
    
    const sessionId = crypto.randomUUID();
    const session = {
      id: sessionId,
      ws: ws,
      playerId: null,
      name: null,
      spectating: false,
      authenticated: false,
      accountId: null,  // ClawArcade account ID
      accountType: null, // 'human' or 'bot'
      authToken: null,
      apiKey: null,
      // Tournament mode (WebSocket bots only)
      tournamentId: null,
      tournamentRegistered: false,
      moltbookVerified: false,
      isWebSocketBot: false, // True if connected via API key (not browser token)
      // Response time tracking for anti-cheat
      lastStateSentAt: null,  // When we last sent game state
      responseTimes: [],      // Array of response times in ms
    };
    
    this.sessions.set(ws, session);
    
    // Send welcome message
    this.send(ws, {
      type: 'welcome',
      sessionId: sessionId,
      grid: this.grid,
      tickRate: this.tickRate,
      authRequired: true,
    });
    
    ws.addEventListener('message', async (event) => {
      try {
        const msg = JSON.parse(event.data);
        await this.handleMessage(ws, session, msg);
      } catch (e) {
        console.error('Invalid message:', e);
      }
    });
    
    ws.addEventListener('close', () => {
      this.handleDisconnect(ws, session);
    });
    
    ws.addEventListener('error', () => {
      this.handleDisconnect(ws, session);
    });
  }

  async handleMessage(ws, session, msg) {
    switch (msg.type) {
      case 'join':
        await this.handleJoin(ws, session, msg);
        break;
      case 'move':
        this.handleMove(session, msg);
        break;
      case 'spectate':
        this.handleSpectate(ws, session);
        break;
      case 'ping':
        this.send(ws, { type: 'pong', timestamp: Date.now() });
        break;
    }
  }

  async validateAuth(token, apiKey) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }
    
    try {
      const response = await fetch(`${API_BASE}/api/validate`, { headers });
      if (response.ok) {
        return await response.json();
      }
    } catch (e) {
      console.error('Auth validation error:', e);
    }
    return null;
  }
  
  async validateTournament(tournamentId, token, apiKey) {
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }
    
    try {
      const response = await fetch(`${API_BASE}/api/validate-tournament/${tournamentId}`, { headers });
      if (response.ok) {
        return await response.json();
      }
      const errorData = await response.json();
      return { valid: false, error: errorData.error };
    } catch (e) {
      console.error('Tournament validation error:', e);
      return { valid: false, error: e.message };
    }
  }
  
  // Auto-enroll bots in active snake tournaments
  async tryAutoEnrollTournament(session, token, apiKey) {
    try {
      // Fetch active snake tournaments
      const tournamentsRes = await fetch(`${API_BASE}/api/tournaments?status=active`);
      if (!tournamentsRes.ok) return null;
      
      const data = await tournamentsRes.json();
      const snakeTournaments = (data.tournaments || []).filter(t => t.game === 'snake');
      
      if (snakeTournaments.length === 0) return null;
      
      // Pick the first active snake tournament
      const tournament = snakeTournaments[0];
      
      // Check if already registered
      const headers = { 'Content-Type': 'application/json' };
      if (apiKey) headers['X-API-Key'] = apiKey;
      if (token) headers['Authorization'] = `Bearer ${token}`;
      
      const validateRes = await fetch(`${API_BASE}/api/validate-tournament/${tournament.id}`, { headers });
      if (validateRes.ok) {
        const validation = await validateRes.json();
        if (validation.isRegistered) {
          // Already registered, just use it
          return { tournamentId: tournament.id, tournamentName: tournament.name, alreadyRegistered: true };
        }
      }
      
      // Auto-register the bot (guest bots can participate but not win prizes)
      const registerRes = await fetch(`${API_BASE}/api/tournaments/${tournament.id}/register`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          // No wallet = not prize eligible, but can still participate
          nickname: session.name || 'AutoBot'
        })
      });
      
      if (registerRes.ok) {
        const regResult = await registerRes.json();
        console.log(`Auto-registered bot for tournament: ${tournament.name}`);
        return { tournamentId: tournament.id, tournamentName: tournament.name, newlyRegistered: true };
      } else {
        const err = await registerRes.json();
        console.log(`Auto-register failed: ${err.error}`);
        // Still allow playing even if tournament registration fails
        return null;
      }
    } catch (e) {
      console.error('Auto-enroll error:', e);
      return null;
    }
  }
  
  // Calculate response time statistics
  calculateResponseStats(responseTimes) {
    if (!responseTimes || responseTimes.length < 3) {
      return { avg: null, stdDev: null, count: responseTimes?.length || 0 };
    }
    
    const sum = responseTimes.reduce((a, b) => a + b, 0);
    const avg = sum / responseTimes.length;
    
    const squaredDiffs = responseTimes.map(t => Math.pow(t - avg, 2));
    const avgSquaredDiff = squaredDiffs.reduce((a, b) => a + b, 0) / responseTimes.length;
    const stdDev = Math.sqrt(avgSquaredDiff);
    
    return { avg, stdDev, count: responseTimes.length };
  }
  
  async submitTournamentScore(session, score) {
    // Submit score to tournament API with server secret
    // This proves the score came from WebSocket server, not browser JS
    const headers = { 'Content-Type': 'application/json' };
    if (session.apiKey) {
      headers['X-API-Key'] = session.apiKey;
    } else if (session.authToken) {
      headers['Authorization'] = `Bearer ${session.authToken}`;
    }
    
    // Calculate response time stats for anti-cheat
    const responseStats = this.calculateResponseStats(session.responseTimes);
    
    try {
      const response = await fetch(`${API_BASE}/api/tournaments/${session.tournamentId}/scores`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          score: score,
          metadata: { submittedBy: 'snake-server', sessionId: session.id },
          websocketSubmission: true,
          serverSecret: this.env.SNAKE_SERVER_SECRET,
          // Response time stats for anti-cheat
          avgResponseTime: responseStats.avg,
          stdDevResponseTime: responseStats.stdDev,
          totalMoves: responseStats.count,
        }),
      });
      
      const result = await response.json();
      if (result.success) {
        const flagInfo = result.flagged ? ` [FLAGGED: ${result.flagReason}]` : '';
        console.log(`Tournament score submitted: ${score} for ${session.name} (tournament: ${session.tournamentId})${flagInfo}`);
        console.log(`  Response stats: avg=${responseStats.avg?.toFixed(1)}ms, stdDev=${responseStats.stdDev?.toFixed(1)}ms, moves=${responseStats.count}`);
        return result;
      } else {
        console.error('Tournament score submission failed:', result.error);
        return null;
      }
    } catch (e) {
      console.error('Tournament score submission error:', e);
      return null;
    }
  }

  async handleJoin(ws, session, msg) {
    const { name, token, apiKey, tournamentId } = msg;
    
    // Try to authenticate
    let authResult = null;
    if (token || apiKey) {
      authResult = await this.validateAuth(token, apiKey);
    }
    
    // Allow guest play but track authenticated players
    let displayName = (name || 'Player').slice(0, 20);
    let accountId = null;
    let accountType = 'guest';
    
    if (authResult && authResult.valid) {
      session.authenticated = true;
      session.accountId = authResult.playerId;
      session.accountType = authResult.type;
      session.authToken = token;
      session.apiKey = apiKey;
      session.moltbookVerified = authResult.moltbookVerified || false;
      // Mark as WebSocket bot if authenticated via API key (includes guest bots)
      const isBotType = authResult.type === 'bot' || authResult.type === 'guest_bot';
      session.isWebSocketBot = !!apiKey && isBotType;
      session.isGuestBot = authResult.type === 'guest_bot' || authResult.isGuest;
      displayName = authResult.displayName || displayName;
      accountId = authResult.playerId;
      accountType = authResult.type;
      console.log(`Authenticated player: ${displayName} (${accountType}, moltbook: ${session.moltbookVerified}, wsBot: ${session.isWebSocketBot}, guest: ${session.isGuestBot})`);
    } else {
      console.log(`Guest player: ${displayName}`);
    }
    
    // AUTO-ENROLL: Check for active snake tournaments and auto-register bots (including guests)
    if (!tournamentId && session.authenticated && session.isWebSocketBot) {
      const autoEnroll = await this.tryAutoEnrollTournament(session, token, apiKey);
      if (autoEnroll) {
        session.tournamentId = autoEnroll.tournamentId;
        session.tournamentRegistered = true;
        session.autoEnrolled = true;
        console.log(`Auto-enrolled ${displayName} in tournament: ${autoEnroll.tournamentName}`);
      }
    }
    
    // Handle explicit tournament mode (legacy flow)
    if (tournamentId && !session.tournamentId) {
      if (!session.authenticated) {
        this.send(ws, {
          type: 'error',
          message: 'Authentication required for tournament mode',
        });
        return;
      }
      
      // Validate tournament registration
      const tournamentValidation = await this.validateTournament(tournamentId, token, apiKey);
      
      if (!tournamentValidation || !tournamentValidation.valid) {
        this.send(ws, {
          type: 'error',
          message: tournamentValidation?.error || 'Failed to validate tournament',
        });
        return;
      }
      
      if (!tournamentValidation.isRegistered) {
        this.send(ws, {
          type: 'error',
          message: 'You must register for this tournament first at clawarcade.surge.sh/tournament.html',
        });
        return;
      }
      
      if (tournamentValidation.isBotTournament) {
        // Bot-only tournament - enforce WebSocket bot requirement
        if (!session.isWebSocketBot) {
          this.send(ws, {
            type: 'error',
            message: 'This is an AI-only tournament. You must connect via WebSocket bot client with API key (browser play not allowed).',
          });
          return;
        }
        
        if (!session.moltbookVerified) {
          this.send(ws, {
            type: 'error', 
            message: 'Only Moltbook-verified agents can compete in AI tournaments. Register your bot with a Moltbook username.',
          });
          return;
        }
      }
      
      if (!tournamentValidation.canCompete) {
        this.send(ws, {
          type: 'error',
          message: 'You cannot compete in this tournament. Check registration status and tournament requirements.',
        });
        return;
      }
      
      session.tournamentId = tournamentId;
      session.tournamentRegistered = true;
      console.log(`Tournament mode enabled: ${tournamentId} for ${displayName}`);
    }
    
    const playerId = this.nextPlayerId++;
    
    // Find a safe spawn position
    const spawn = this.findSpawnPosition();
    
    const player = {
      id: playerId,
      name: displayName,
      body: [spawn, { x: spawn.x - 1, y: spawn.y }, { x: spawn.x - 2, y: spawn.y }],
      direction: 'right',
      nextDirection: 'right',
      alive: true,
      score: 0,
      color: this.getPlayerColor(playerId),
      accountId: accountId,
      accountType: accountType,
      // Tournament tracking
      tournamentId: session.tournamentId,
      tournamentRegistered: session.tournamentRegistered,
      isWebSocketBot: session.isWebSocketBot,
      moltbookVerified: session.moltbookVerified,
    };
    
    this.players.set(playerId, player);
    session.playerId = playerId;
    session.name = displayName;
    session.spectating = false;
    
    // Track for match results
    if (accountId) {
      this.matchStartPlayers.set(playerId, {
        accountId,
        accountType,
        name: displayName,
        authToken: session.authToken,
        apiKey: session.apiKey,
      });
    }
    
    // Mark match in progress if we have 2+ authenticated players
    const authPlayerCount = [...this.players.values()].filter(p => p.accountId).length;
    if (authPlayerCount >= 2) {
      this.matchInProgress = true;
    }
    
    // Send joined confirmation
    this.send(ws, {
      type: 'joined',
      playerId: playerId,
      name: displayName,
      color: player.color,
      authenticated: session.authenticated,
      accountType: session.accountType,
      tournamentMode: !!session.tournamentId,
      tournamentId: session.tournamentId,
      autoEnrolled: session.autoEnrolled || false,
      isWebSocketBot: session.isWebSocketBot,
      moltbookVerified: session.moltbookVerified,
    });
    
    // Broadcast player joined to others
    this.broadcast({
      type: 'player_joined',
      playerId: playerId,
      name: displayName,
      accountType: accountType,
    }, ws);
    
    // Ensure food exists
    this.ensureFood();
    
    // Start game loop if not running
    this.startGameLoop();
  }

  handleSpectate(ws, session) {
    session.spectating = true;
    session.playerId = null;
    
    this.send(ws, {
      type: 'spectating',
      message: 'You are now spectating',
    });
    
    // Start game loop if there are players
    if (this.players.size > 0) {
      this.startGameLoop();
    }
  }

  handleMove(session, msg) {
    if (!session.playerId) return;
    
    const player = this.players.get(session.playerId);
    if (!player || !player.alive) return;
    
    // Track response time for anti-cheat
    if (session.lastStateSentAt) {
      const responseTime = Date.now() - session.lastStateSentAt;
      session.responseTimes.push(responseTime);
      // Keep last 100 response times
      if (session.responseTimes.length > 100) {
        session.responseTimes.shift();
      }
    }
    
    const dir = msg.direction;
    const current = player.direction;
    
    // Prevent 180-degree turns
    const opposites = { up: 'down', down: 'up', left: 'right', right: 'left' };
    if (opposites[dir] === current) return;
    
    if (['up', 'down', 'left', 'right'].includes(dir)) {
      player.nextDirection = dir;
    }
  }

  handleDisconnect(ws, session) {
    if (session.playerId) {
      const player = this.players.get(session.playerId);
      if (player) {
        // Broadcast player left
        this.broadcast({
          type: 'player_left',
          playerId: session.playerId,
          name: session.name,
        });
        
        this.players.delete(session.playerId);
        console.log(`Player ${session.name} (${session.playerId}) disconnected`);
      }
    }
    
    this.sessions.delete(ws);
    
    // Stop game loop if no players
    if (this.players.size === 0 && this.gameInterval) {
      clearInterval(this.gameInterval);
      this.gameInterval = null;
      this.tick = 0;
      this.food = [];
      this.matchInProgress = false;
      this.matchStartPlayers.clear();
    }
  }

  startGameLoop() {
    if (this.gameInterval) return;
    
    this.gameInterval = setInterval(() => {
      this.gameTick();
    }, this.tickRate);
  }

  async gameTick() {
    this.tick++;
    
    // Update all players
    for (const [playerId, player] of this.players) {
      if (!player.alive) continue;
      
      // Apply direction change
      player.direction = player.nextDirection;
      
      // Calculate new head position
      const head = player.body[0];
      const newHead = { ...head };
      
      switch (player.direction) {
        case 'up': newHead.y--; break;
        case 'down': newHead.y++; break;
        case 'left': newHead.x--; break;
        case 'right': newHead.x++; break;
      }
      
      // Check wall collision
      if (newHead.x < 0 || newHead.x >= this.grid.width ||
          newHead.y < 0 || newHead.y >= this.grid.height) {
        player.alive = false;
        await this.broadcastDeath(player);
        continue;
      }
      
      // Check self collision
      if (player.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
        player.alive = false;
        await this.broadcastDeath(player);
        continue;
      }
      
      // Check collision with other snakes
      let hitOther = false;
      for (const [otherId, other] of this.players) {
        if (otherId === playerId || !other.alive) continue;
        if (other.body.some(seg => seg.x === newHead.x && seg.y === newHead.y)) {
          player.alive = false;
          hitOther = true;
          await this.broadcastDeath(player, other);
          break;
        }
      }
      if (hitOther) continue;
      
      // Move snake
      player.body.unshift(newHead);
      
      // Check food collision
      let ateFood = false;
      for (let i = this.food.length - 1; i >= 0; i--) {
        const f = this.food[i];
        if (f.x === newHead.x && f.y === newHead.y) {
          player.score += f.points;
          this.food.splice(i, 1);
          ateFood = true;
          
          // Broadcast food eaten
          this.broadcast({
            type: 'food_eaten',
            playerId: playerId,
            position: { x: f.x, y: f.y },
            points: f.points,
          });
          break;
        }
      }
      
      // Remove tail if didn't eat
      if (!ateFood) {
        player.body.pop();
      }
    }
    
    // Respawn food
    this.ensureFood();
    
    // Send state to all clients
    this.broadcastState();
    
    // Check for game over (all players dead or only one left)
    const alivePlayers = [...this.players.values()].filter(p => p.alive);
    const totalPlayers = this.players.size;
    
    if (totalPlayers > 0 && (alivePlayers.length === 0 || (totalPlayers > 1 && alivePlayers.length === 1))) {
      // Match ended - report results
      this.endMatch(alivePlayers);
    }
  }

  async endMatch(alivePlayers) {
    if (!this.matchInProgress) {
      // Just reset if no match was being tracked
      setTimeout(() => this.resetGame(), 3000);
      return;
    }
    
    // Build results array sorted by placement
    const allPlayers = [...this.players.values()];
    const deadPlayers = allPlayers.filter(p => !p.alive);
    
    // Winner is either the last alive or the one with highest score
    const results = [];
    
    if (alivePlayers.length === 1) {
      // Clear winner
      results.push({
        playerId: alivePlayers[0].accountId,
        placement: 1,
        score: alivePlayers[0].score,
        name: alivePlayers[0].name,
      });
    }
    
    // Sort dead players by score (higher score = died later/better)
    deadPlayers.sort((a, b) => b.score - a.score);
    
    let placement = results.length + 1;
    for (const player of deadPlayers) {
      if (player.accountId) {
        results.push({
          playerId: player.accountId,
          placement: placement++,
          score: player.score,
          name: player.name,
        });
      }
    }
    
    // Report match to API if we have authenticated players
    if (results.length >= 2) {
      try {
        // Use first player's auth to submit
        const authPlayer = this.matchStartPlayers.values().next().value;
        if (authPlayer) {
          const headers = { 'Content-Type': 'application/json' };
          if (authPlayer.authToken) {
            headers['Authorization'] = `Bearer ${authPlayer.authToken}`;
          } else if (authPlayer.apiKey) {
            headers['X-API-Key'] = authPlayer.apiKey;
          }
          
          await fetch(`${API_BASE}/api/matches`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              game: 'snake',
              results: results,
            }),
          });
          
          console.log('Match reported:', results);
        }
      } catch (e) {
        console.error('Failed to report match:', e);
      }
    }
    
    // Broadcast match results
    this.broadcast({
      type: 'match_end',
      results: results.map(r => ({
        name: r.name,
        placement: r.placement,
        score: r.score,
      })),
    });
    
    // Reset after delay
    setTimeout(() => this.resetGame(), 5000);
  }

  async broadcastDeath(player, killer = null) {
    this.broadcast({
      type: 'player_died',
      playerId: player.id,
      name: player.name,
      score: player.score,
      killedBy: killer ? { id: killer.id, name: killer.name } : 'wall',
    });
    
    // Find the session for this player
    let playerSession = null;
    for (const [ws, session] of this.sessions) {
      if (session.playerId === player.id) {
        playerSession = session;
        break;
      }
    }
    
    if (!playerSession) return;
    
    // Submit tournament score if player was in tournament mode
    if (player.tournamentId && player.tournamentRegistered && player.isWebSocketBot) {
      const result = await this.submitTournamentScore(playerSession, player.score);
      if (result) {
        this.send(playerSession.ws, {
          type: 'tournament_score_submitted',
          score: player.score,
          isNewBest: result.isNewBest,
          previousBest: result.previousBest,
        });
      }
    }
    
    // Submit to regular leaderboard ONLY if not in tournament mode
    // (Tournament scores are already submitted above and shouldn't duplicate)
    if (playerSession.authenticated && player.score > 0 && !player.tournamentId) {
      await this.submitRegularScore(playerSession, player.score);
    }
  }
  
  async submitRegularScore(session, score) {
    const headers = { 'Content-Type': 'application/json' };
    if (session.apiKey) {
      headers['X-API-Key'] = session.apiKey;
    } else if (session.authToken) {
      headers['Authorization'] = `Bearer ${session.authToken}`;
    }
    
    try {
      const response = await fetch(`${API_BASE}/api/scores`, {
        method: 'POST',
        headers,
        body: JSON.stringify({
          game: 'snake',
          score: score,
          metadata: { source: 'websocket', sessionId: session.id }
        }),
      });
      
      const result = await response.json();
      if (result.success) {
        console.log(`Score submitted: ${score} for ${session.name}`);
        if (result.pointsEarned > 0) {
          this.send(session.ws, {
            type: 'score_submitted',
            score: score,
            pointsEarned: result.pointsEarned,
            achievements: result.achievements || [],
          });
        }
      }
    } catch (e) {
      console.error('Score submission error:', e);
    }
  }

  broadcastState() {
    const allPlayers = [...this.players.values()].map(p => ({
      id: p.id,
      name: p.name,
      body: p.body,
      direction: p.direction,
      alive: p.alive,
      score: p.score,
      color: p.color,
      accountType: p.accountType,
    }));
    
    const now = Date.now();
    
    for (const [ws, session] of this.sessions) {
      const state = {
        type: 'state',
        tick: this.tick,
        food: this.food,
        grid: this.grid,
        playerCount: this.players.size,
      };
      
      if (session.playerId) {
        const player = this.players.get(session.playerId);
        if (player) {
          state.you = {
            id: player.id,
            name: player.name,
            body: player.body,
            direction: player.direction,
            alive: player.alive,
            score: player.score,
            color: player.color,
            accountType: player.accountType,
          };
        }
        state.opponents = allPlayers.filter(p => p.id !== session.playerId);
      } else {
        state.you = null;
        state.opponents = allPlayers;
      }
      
      // Record when state is sent for response time tracking
      session.lastStateSentAt = now;
      
      this.send(ws, state);
    }
  }

  resetGame() {
    // Respawn all players
    for (const [playerId, player] of this.players) {
      const spawn = this.findSpawnPosition();
      player.body = [spawn, { x: spawn.x - 1, y: spawn.y }, { x: spawn.x - 2, y: spawn.y }];
      player.direction = 'right';
      player.nextDirection = 'right';
      player.alive = true;
      player.score = 0;
    }
    
    this.food = [];
    this.ensureFood();
    
    // Reset match tracking and response time tracking
    this.matchStartPlayers.clear();
    for (const [ws, session] of this.sessions) {
      // Reset response time tracking for new game
      session.responseTimes = [];
      session.lastStateSentAt = null;
      
      if (session.playerId && session.accountId) {
        const player = this.players.get(session.playerId);
        if (player) {
          this.matchStartPlayers.set(session.playerId, {
            accountId: session.accountId,
            accountType: session.accountType,
            name: session.name,
            authToken: session.authToken,
            apiKey: session.apiKey,
          });
        }
      }
    }
    
    const authPlayerCount = [...this.players.values()].filter(p => p.accountId).length;
    this.matchInProgress = authPlayerCount >= 2;
    
    this.broadcast({
      type: 'game_reset',
      message: 'New round starting!',
    });
  }

  findSpawnPosition() {
    const margin = 4;
    let attempts = 0;
    
    while (attempts < 100) {
      const x = margin + Math.floor(Math.random() * (this.grid.width - margin * 2));
      const y = margin + Math.floor(Math.random() * (this.grid.height - margin * 2));
      
      // Check if position is clear
      let clear = true;
      for (const player of this.players.values()) {
        for (const seg of player.body) {
          if (Math.abs(seg.x - x) < 4 && Math.abs(seg.y - y) < 4) {
            clear = false;
            break;
          }
        }
        if (!clear) break;
      }
      
      if (clear) {
        return { x, y };
      }
      attempts++;
    }
    
    // Fallback
    return { x: Math.floor(this.grid.width / 2), y: Math.floor(this.grid.height / 2) };
  }

  ensureFood() {
    const targetFood = Math.max(3, Math.min(8, this.players.size * 2 + 1));
    
    while (this.food.length < targetFood) {
      const pos = this.findFoodPosition();
      if (pos) {
        const type = this.randomFoodType();
        this.food.push({ x: pos.x, y: pos.y, ...type });
      } else {
        break;
      }
    }
  }

  findFoodPosition() {
    let attempts = 0;
    
    while (attempts < 100) {
      const x = Math.floor(Math.random() * this.grid.width);
      const y = Math.floor(Math.random() * this.grid.height);
      
      // Check if position is clear
      let clear = true;
      
      for (const player of this.players.values()) {
        if (player.body.some(seg => seg.x === x && seg.y === y)) {
          clear = false;
          break;
        }
      }
      
      if (clear && !this.food.some(f => f.x === x && f.y === y)) {
        return { x, y };
      }
      
      attempts++;
    }
    
    return null;
  }

  randomFoodType() {
    const r = Math.random();
    if (r < 0.5) return { type: 'green', points: 1, color: '#00ff88' };
    if (r < 0.75) return { type: 'yellow', points: 2, color: '#ffdd00' };
    return { type: 'blue', points: 3, color: '#00bbff' };
  }

  getPlayerColor(playerId) {
    const colors = [
      '#00ff88', '#ff00ff', '#00bbff', '#ffdd00', 
      '#ff6600', '#ff4444', '#aa00ff', '#00ffff'
    ];
    return colors[(playerId - 1) % colors.length];
  }

  send(ws, data) {
    try {
      ws.send(JSON.stringify(data));
    } catch (e) {
      // Client disconnected
    }
  }

  broadcast(data, exclude = null) {
    const msg = JSON.stringify(data);
    for (const [ws, session] of this.sessions) {
      if (ws !== exclude) {
        try {
          ws.send(msg);
        } catch (e) {
          // Client disconnected
        }
      }
    }
  }
}
