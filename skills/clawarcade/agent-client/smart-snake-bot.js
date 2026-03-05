#!/usr/bin/env node
/**
 * ClawArcade Smart Snake Bot
 * 
 * A pathfinding snake bot that:
 * - Chases nearest food using Manhattan distance
 * - Avoids walls, self, and other snakes
 * - Looks ahead to avoid trapping itself
 * - Typically scores 50-150+ points
 * 
 * Usage: 
 *   BOT_API_KEY=arcade_guest_xxx node smart-snake-bot.js
 *   
 * Or get a key first:
 *   curl -X POST https://clawarcade-api.bassel-amin92-76d.workers.dev/api/auth/guest-bot \
 *     -H "Content-Type: application/json" -d '{"botName":"SmartBot"}'
 */

const WebSocket = require('ws');

const SERVER = 'wss://clawarcade-snake.bassel-amin92-76d.workers.dev/ws/default';
const API_KEY = process.env.BOT_API_KEY;
const BOT_NAME = process.env.BOT_NAME || 'SmartSnakeBot';

if (!API_KEY) {
  console.error('Error: Set BOT_API_KEY environment variable');
  console.error('Get one with: curl -X POST https://clawarcade-api.bassel-amin92-76d.workers.dev/api/auth/guest-bot -H "Content-Type: application/json" -d \'{"botName":"MyBot"}\'');
  process.exit(1);
}

class SmartSnakeBot {
  constructor() {
    this.grid = { width: 20, height: 20 };
    this.ws = null;
  }

  connect() {
    console.log(`[${BOT_NAME}] Connecting to ${SERVER}...`);
    this.ws = new WebSocket(SERVER);
    
    this.ws.on('open', () => {
      console.log(`[${BOT_NAME}] Connected! Joining game...`);
      this.send({ type: 'join', name: BOT_NAME, apiKey: API_KEY });
    });
    
    this.ws.on('message', (data) => {
      const msg = JSON.parse(data.toString());
      this.handleMessage(msg);
    });
    
    this.ws.on('close', () => {
      console.log(`[${BOT_NAME}] Disconnected. Reconnecting in 3s...`);
      setTimeout(() => this.connect(), 3000);
    });
    
    this.ws.on('error', (err) => console.error(`[${BOT_NAME}] Error:`, err.message));
  }

  send(data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    }
  }

  handleMessage(msg) {
    switch (msg.type) {
      case 'welcome':
        this.grid = msg.grid;
        console.log(`[${BOT_NAME}] Grid: ${this.grid.width}x${this.grid.height}`);
        break;
        
      case 'joined':
        console.log(`[${BOT_NAME}] Joined as player ${msg.playerId} | Auth: ${msg.authenticated}`);
        break;
        
      case 'state':
        if (msg.you?.alive) {
          const direction = this.decide(msg);
          if (direction) this.send({ type: 'move', direction });
        }
        if (msg.tick % 50 === 0 && msg.you) {
          console.log(`[${BOT_NAME}] Tick ${msg.tick} | Score: ${msg.you.score} | Length: ${msg.you.body.length}`);
        }
        break;
        
      case 'player_died':
        if (msg.name === BOT_NAME) {
          console.log(`[${BOT_NAME}] 💀 Died! Final score: ${msg.score}`);
        }
        break;
        
      case 'score_submitted':
        console.log(`[${BOT_NAME}] ✓ Score submitted! Points earned: ${msg.pointsEarned}`);
        break;
        
      case 'game_reset':
        console.log(`[${BOT_NAME}] 🔄 New round starting!`);
        break;
    }
  }

  decide(state) {
    const { you, food, opponents } = state;
    const head = you.body[0];
    const currentDir = you.direction;
    
    // Build danger map
    const dangers = new Set();
    
    // My body (except head, and tail might move)
    for (let i = 1; i < you.body.length - 1; i++) {
      dangers.add(`${you.body[i].x},${you.body[i].y}`);
    }
    
    // Other snakes (full body + one cell around head for safety)
    for (const opp of (opponents || [])) {
      if (!opp.alive) continue;
      for (const seg of opp.body) {
        dangers.add(`${seg.x},${seg.y}`);
      }
      // Danger zone around opponent head
      const oh = opp.body[0];
      for (const [dx, dy] of [[0,-1],[0,1],[-1,0],[1,0]]) {
        dangers.add(`${oh.x+dx},${oh.y+dy}`);
      }
    }
    
    // Possible moves
    const moves = [
      { dir: 'up',    dx: 0,  dy: -1 },
      { dir: 'down',  dx: 0,  dy: 1 },
      { dir: 'left',  dx: -1, dy: 0 },
      { dir: 'right', dx: 1,  dy: 0 },
    ];
    
    // Can't reverse
    const opposites = { up: 'down', down: 'up', left: 'right', right: 'left' };
    const validMoves = moves.filter(m => m.dir !== opposites[currentDir]);
    
    // Score each move
    const scoredMoves = validMoves.map(move => {
      const nx = head.x + move.dx;
      const ny = head.y + move.dy;
      let score = 0;
      
      // Wall collision = instant death
      if (nx < 0 || nx >= this.grid.width || ny < 0 || ny >= this.grid.height) {
        return { ...move, score: -1000 };
      }
      
      // Snake collision = death
      if (dangers.has(`${nx},${ny}`)) {
        return { ...move, score: -500 };
      }
      
      // Count escape routes (avoid dead ends)
      const escapes = this.countEscapes(nx, ny, dangers, you.body);
      if (escapes === 0) {
        score -= 200; // Dead end
      } else {
        score += escapes * 15;
      }
      
      // Distance to nearest food (lower = better)
      if (food?.length > 0) {
        let minDist = Infinity;
        let bestFood = null;
        for (const f of food) {
          const dist = Math.abs(f.x - nx) + Math.abs(f.y - ny);
          if (dist < minDist) {
            minDist = dist;
            bestFood = f;
          }
        }
        
        // Reward moving toward food
        const currentDist = Math.abs(bestFood.x - head.x) + Math.abs(bestFood.y - head.y);
        if (minDist < currentDist) {
          score += 50 + (bestFood.points || 1) * 10;
        }
        
        // Bonus for eating food this move
        if (nx === bestFood.x && ny === bestFood.y) {
          score += 100 + (bestFood.points || 1) * 20;
        }
      }
      
      // Stay away from walls
      const wallDist = Math.min(nx, ny, this.grid.width - 1 - nx, this.grid.height - 1 - ny);
      score += wallDist * 3;
      
      // Slight preference for continuing straight
      if (move.dir === currentDir) {
        score += 5;
      }
      
      return { ...move, score };
    });
    
    // Pick best move
    scoredMoves.sort((a, b) => b.score - a.score);
    return scoredMoves[0]?.dir || currentDir;
  }

  countEscapes(x, y, dangers, myBody) {
    let count = 0;
    for (const [dx, dy] of [[0,-1],[0,1],[-1,0],[1,0]]) {
      const nx = x + dx;
      const ny = y + dy;
      if (nx < 0 || nx >= this.grid.width || ny < 0 || ny >= this.grid.height) continue;
      if (dangers.has(`${nx},${ny}`)) continue;
      // Check not hitting own body (except tail)
      const hitsBody = myBody.slice(0, -1).some(s => s.x === nx && s.y === ny);
      if (hitsBody) continue;
      count++;
    }
    return count;
  }
}

console.log(`
╔═══════════════════════════════════════════════════════════════╗
║         ClawArcade Smart Snake Bot v1.0                       ║
╠═══════════════════════════════════════════════════════════════╣
║  Bot Name:  ${BOT_NAME.padEnd(48)}║
║  Strategy:  Food-seeking + collision avoidance + lookahead    ║
╚═══════════════════════════════════════════════════════════════╝
`);

const bot = new SmartSnakeBot();
bot.connect();
