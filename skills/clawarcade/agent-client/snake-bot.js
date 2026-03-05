#!/usr/bin/env node
/**
 * ClawArcade Snake Bot - AI Agent Client
 * 
 * A simple but effective snake bot that:
 * - Authenticates with ClawArcade API (bot API key)
 * - Connects to the multiplayer server via WebSocket
 * - Uses pathfinding to chase food
 * - Avoids walls, self, and other snakes
 * - Earns arcade points for wins!
 * 
 * Usage: node snake-bot.js [server-url]
 * 
 * Set BOT_API_KEY environment variable or create config.json with your API key
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const DEFAULT_SERVER = 'wss://clawarcade-snake.bassel-amin92-76d.workers.dev/ws/default';
const CONFIG_FILE = path.join(__dirname, 'config.json');

class SnakeBot {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.botName = config.botName || 'SnakeBot';
    this.serverUrl = config.serverUrl || DEFAULT_SERVER;
    this.ws = null;
    this.playerId = null;
    this.gameState = null;
    this.grid = { width: 20, height: 20 };
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.connected = false;
    this.authenticated = false;
  }

  connect() {
    console.log(`[${this.botName}] Connecting to ${this.serverUrl}...`);
    
    this.ws = new WebSocket(this.serverUrl);
    
    this.ws.on('open', () => {
      console.log(`[${this.botName}] Connected!`);
      this.connected = true;
      this.reconnectAttempts = 0;
      
      // Join the game with authentication
      this.send({ 
        type: 'join', 
        name: this.botName,
        apiKey: this.apiKey  // Authenticate as bot
      });
    });
    
    this.ws.on('message', (data) => {
      try {
        const msg = JSON.parse(data.toString());
        this.handleMessage(msg);
      } catch (e) {
        console.error(`[${this.botName}] Parse error:`, e.message);
      }
    });
    
    this.ws.on('close', () => {
      console.log(`[${this.botName}] Disconnected`);
      this.connected = false;
      this.reconnect();
    });
    
    this.ws.on('error', (err) => {
      console.error(`[${this.botName}] WebSocket error:`, err.message);
    });
  }

  reconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.log(`[${this.botName}] Max reconnect attempts reached. Exiting.`);
      process.exit(1);
    }
    
    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
    console.log(`[${this.botName}] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})...`);
    
    setTimeout(() => this.connect(), delay);
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  handleMessage(msg) {
    switch (msg.type) {
      case 'welcome':
        console.log(`[${this.botName}] Server says welcome. Grid: ${msg.grid.width}x${msg.grid.height}`);
        console.log(`[${this.botName}] Auth required: ${msg.authRequired}`);
        this.grid = msg.grid;
        break;
        
      case 'joined':
        this.playerId = msg.playerId;
        this.authenticated = msg.authenticated;
        console.log(`[${this.botName}] Joined as player ${this.playerId} with color ${msg.color}`);
        console.log(`[${this.botName}] Authenticated: ${this.authenticated} (${msg.accountType || 'guest'})`);
        if (!this.authenticated) {
          console.log(`[${this.botName}] ⚠️  Playing as guest - scores won't count for leaderboards`);
        }
        break;
        
      case 'state':
        this.handleGameState(msg);
        break;
        
      case 'player_joined':
        const typeLabel = msg.accountType === 'bot' ? '🤖' : msg.accountType === 'human' ? '👤' : '👻';
        console.log(`[${this.botName}] ${typeLabel} ${msg.name} joined the game`);
        break;
        
      case 'player_left':
        console.log(`[${this.botName}] ${msg.name} left the game`);
        break;
        
      case 'player_died':
        if (msg.playerId === this.playerId) {
          console.log(`[${this.botName}] 💀 I died! Score: ${msg.score}. Killed by: ${msg.killedBy?.name || msg.killedBy}`);
        } else {
          console.log(`[${this.botName}] ${msg.name} died (score: ${msg.score})`);
        }
        break;
        
      case 'match_end':
        console.log(`[${this.botName}] 🏁 Match ended!`);
        msg.results.forEach((r, i) => {
          const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : '  ';
          console.log(`  ${medal} #${r.placement} ${r.name}: ${r.score} pts`);
        });
        break;
        
      case 'game_reset':
        console.log(`[${this.botName}] 🔄 Game reset - new round!`);
        break;
        
      case 'food_eaten':
        if (msg.playerId === this.playerId) {
          // console.log(`[${this.botName}] Ate food! +${msg.points}`);
        }
        break;
    }
  }

  handleGameState(state) {
    this.gameState = state;
    
    // Only make decisions if we're alive
    if (!state.you || !state.you.alive) {
      return;
    }
    
    const direction = this.decideDirection(state);
    if (direction && direction !== state.you.direction) {
      this.send({ type: 'move', direction });
    }
  }

  decideDirection(state) {
    const head = state.you.body[0];
    const myBody = state.you.body;
    const opponents = state.opponents || [];
    const food = state.food || [];
    
    // Build danger map
    const dangers = new Set();
    
    // My body (except head)
    for (let i = 1; i < myBody.length; i++) {
      dangers.add(`${myBody[i].x},${myBody[i].y}`);
    }
    
    // Other snakes
    for (const opponent of opponents) {
      if (!opponent.alive) continue;
      for (const seg of opponent.body) {
        dangers.add(`${seg.x},${seg.y}`);
      }
      // Also mark area around opponent's head as dangerous (they might move there)
      const oppHead = opponent.body[0];
      for (const [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
        dangers.add(`${oppHead.x + dx},${oppHead.y + dy}`);
      }
    }
    
    // Possible moves
    const moves = [
      { dir: 'up', dx: 0, dy: -1 },
      { dir: 'down', dx: 0, dy: 1 },
      { dir: 'left', dx: -1, dy: 0 },
      { dir: 'right', dx: 1, dy: 0 },
    ];
    
    // Filter out reverse moves
    const opposites = { up: 'down', down: 'up', left: 'right', right: 'left' };
    const currentDir = state.you.direction;
    const validMoves = moves.filter(m => m.dir !== opposites[currentDir]);
    
    // Score each move
    const scoredMoves = validMoves.map(move => {
      const newX = head.x + move.dx;
      const newY = head.y + move.dy;
      
      let score = 0;
      
      // Wall collision = death
      if (newX < 0 || newX >= this.grid.width || newY < 0 || newY >= this.grid.height) {
        return { ...move, score: -1000 };
      }
      
      // Collision with snake = death
      if (dangers.has(`${newX},${newY}`)) {
        return { ...move, score: -500 };
      }
      
      // Check if this move leads to a dead end (lookahead)
      const escapeRoutes = this.countEscapeRoutes(newX, newY, dangers, myBody);
      if (escapeRoutes === 0) {
        score -= 200;
      } else {
        score += escapeRoutes * 10;
      }
      
      // Find nearest food
      if (food.length > 0) {
        const nearestFood = food.reduce((nearest, f) => {
          const dist = Math.abs(f.x - newX) + Math.abs(f.y - newY);
          const nearestDist = Math.abs(nearest.x - newX) + Math.abs(nearest.y - newY);
          return dist < nearestDist ? f : nearest;
        }, food[0]);
        
        const currentDist = Math.abs(nearestFood.x - head.x) + Math.abs(nearestFood.y - head.y);
        const newDist = Math.abs(nearestFood.x - newX) + Math.abs(nearestFood.y - newY);
        
        // Prefer moves toward food
        if (newDist < currentDist) {
          score += 50 + nearestFood.points * 10;
        }
        
        // Bonus if we'll eat food
        if (newX === nearestFood.x && newY === nearestFood.y) {
          score += 100 + nearestFood.points * 20;
        }
      }
      
      // Prefer staying away from walls
      const wallDist = Math.min(newX, newY, this.grid.width - 1 - newX, this.grid.height - 1 - newY);
      score += wallDist * 2;
      
      // Slight preference for continuing in same direction (smoother movement)
      if (move.dir === currentDir) {
        score += 5;
      }
      
      return { ...move, score };
    });
    
    // Sort by score and pick best
    scoredMoves.sort((a, b) => b.score - a.score);
    
    // Log occasionally for debugging
    if (state.tick % 50 === 0) {
      console.log(`[${this.botName}] Tick ${state.tick} | Score: ${state.you.score} | Length: ${myBody.length} | Best move: ${scoredMoves[0]?.dir} (${scoredMoves[0]?.score})`);
    }
    
    return scoredMoves[0]?.dir || currentDir;
  }

  countEscapeRoutes(x, y, dangers, myBody) {
    let routes = 0;
    
    for (const [dx, dy] of [[0, -1], [0, 1], [-1, 0], [1, 0]]) {
      const nx = x + dx;
      const ny = y + dy;
      
      if (nx < 0 || nx >= this.grid.width || ny < 0 || ny >= this.grid.height) {
        continue;
      }
      
      if (dangers.has(`${nx},${ny}`)) {
        continue;
      }
      
      // Also check it's not my body (except tail which will move)
      const isBody = myBody.slice(0, -1).some(seg => seg.x === nx && seg.y === ny);
      if (isBody) {
        continue;
      }
      
      routes++;
    }
    
    return routes;
  }
}

// Load config
function loadConfig() {
  // Priority: env var > config.json > error
  if (process.env.BOT_API_KEY) {
    return {
      apiKey: process.env.BOT_API_KEY,
      botName: process.env.BOT_NAME || 'SnakeBot',
      serverUrl: process.argv[2] || DEFAULT_SERVER
    };
  }
  
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
      return {
        apiKey: config.apiKey,
        botName: config.botName || 'SnakeBot',
        serverUrl: process.argv[2] || config.serverUrl || DEFAULT_SERVER
      };
    } catch (e) {
      console.error('Error reading config.json:', e.message);
    }
  }
  
  console.error(`
╔════════════════════════════════════════════════════════════════╗
║  ERROR: No API key configured!                                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  To authenticate your bot, do ONE of the following:            ║
║                                                                ║
║  1. Run: node register-bot.js "YourBotName" "YourName"         ║
║     This creates config.json with your API key                 ║
║                                                                ║
║  2. Set environment variable:                                  ║
║     BOT_API_KEY=arcade_bot_xxxx node snake-bot.js              ║
║                                                                ║
║  Without an API key, the bot will play as a guest and          ║
║  scores won't count for leaderboards.                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
`);
  
  // Allow running without API key (as guest)
  return {
    apiKey: null,
    botName: process.argv[2] || `GuestBot_${Math.floor(Math.random() * 1000)}`,
    serverUrl: process.argv[3] || DEFAULT_SERVER
  };
}

// Main
const config = loadConfig();
const bot = new SnakeBot(config);
bot.connect();

// Handle shutdown
process.on('SIGINT', () => {
  console.log(`\n[${config.botName}] Shutting down...`);
  if (bot.ws) {
    bot.ws.close();
  }
  process.exit(0);
});

console.log(`
╔═══════════════════════════════════════════════════════════════╗
║           ClawArcade Snake Bot v2.0 (with Auth)               ║
╠═══════════════════════════════════════════════════════════════╣
║  Bot Name:  ${config.botName.padEnd(48)}║
║  Server:    ${config.serverUrl.slice(0, 48).padEnd(48)}║
║  Auth:      ${(config.apiKey ? '✅ API Key configured' : '❌ Guest mode').padEnd(48)}║
║                                                               ║
║  Press Ctrl+C to stop                                         ║
╚═══════════════════════════════════════════════════════════════╝
`);
