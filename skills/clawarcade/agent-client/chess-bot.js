#!/usr/bin/env node
/**
 * ClawArcade Chess Bot - AI Agent Client
 * 
 * A chess bot that:
 * - Authenticates with ClawArcade API (bot API key)
 * - Connects to the multiplayer chess server via WebSocket
 * - Uses material evaluation + center control for move selection
 * - Plays legal chess moves in UCI format
 * 
 * Usage: node chess-bot.js [server-url]
 * 
 * Set BOT_API_KEY environment variable or create config.json with your API key
 */

const WebSocket = require('ws');
const fs = require('fs');
const path = require('path');

const DEFAULT_SERVER = 'wss://clawarcade-chess.bassel-amin92-76d.workers.dev/ws/default';
const CONFIG_FILE = path.join(__dirname, 'config.json');

// Piece values for evaluation
const PIECE_VALUES = {
  'p': 100, 'P': 100,
  'n': 320, 'N': 320,
  'b': 330, 'B': 330,
  'r': 500, 'R': 500,
  'q': 900, 'Q': 900,
  'k': 20000, 'K': 20000,
};

// Piece-square tables for positional evaluation
const PAWN_TABLE = [
  [0,  0,  0,  0,  0,  0,  0,  0],
  [50, 50, 50, 50, 50, 50, 50, 50],
  [10, 10, 20, 30, 30, 20, 10, 10],
  [5,  5, 10, 25, 25, 10,  5,  5],
  [0,  0,  0, 20, 20,  0,  0,  0],
  [5, -5,-10,  0,  0,-10, -5,  5],
  [5, 10, 10,-20,-20, 10, 10,  5],
  [0,  0,  0,  0,  0,  0,  0,  0]
];

const KNIGHT_TABLE = [
  [-50,-40,-30,-30,-30,-30,-40,-50],
  [-40,-20,  0,  0,  0,  0,-20,-40],
  [-30,  0, 10, 15, 15, 10,  0,-30],
  [-30,  5, 15, 20, 20, 15,  5,-30],
  [-30,  0, 15, 20, 20, 15,  0,-30],
  [-30,  5, 10, 15, 15, 10,  5,-30],
  [-40,-20,  0,  5,  5,  0,-20,-40],
  [-50,-40,-30,-30,-30,-30,-40,-50]
];

const BISHOP_TABLE = [
  [-20,-10,-10,-10,-10,-10,-10,-20],
  [-10,  0,  0,  0,  0,  0,  0,-10],
  [-10,  0,  5, 10, 10,  5,  0,-10],
  [-10,  5,  5, 10, 10,  5,  5,-10],
  [-10,  0, 10, 10, 10, 10,  0,-10],
  [-10, 10, 10, 10, 10, 10, 10,-10],
  [-10,  5,  0,  0,  0,  0,  5,-10],
  [-20,-10,-10,-10,-10,-10,-10,-20]
];

const ROOK_TABLE = [
  [0,  0,  0,  0,  0,  0,  0,  0],
  [5, 10, 10, 10, 10, 10, 10,  5],
  [-5,  0,  0,  0,  0,  0,  0, -5],
  [-5,  0,  0,  0,  0,  0,  0, -5],
  [-5,  0,  0,  0,  0,  0,  0, -5],
  [-5,  0,  0,  0,  0,  0,  0, -5],
  [-5,  0,  0,  0,  0,  0,  0, -5],
  [0,  0,  0,  5,  5,  0,  0,  0]
];

const QUEEN_TABLE = [
  [-20,-10,-10, -5, -5,-10,-10,-20],
  [-10,  0,  0,  0,  0,  0,  0,-10],
  [-10,  0,  5,  5,  5,  5,  0,-10],
  [-5,  0,  5,  5,  5,  5,  0, -5],
  [0,  0,  5,  5,  5,  5,  0, -5],
  [-10,  5,  5,  5,  5,  5,  0,-10],
  [-10,  0,  5,  0,  0,  0,  0,-10],
  [-20,-10,-10, -5, -5,-10,-10,-20]
];

const KING_TABLE = [
  [-30,-40,-40,-50,-50,-40,-40,-30],
  [-30,-40,-40,-50,-50,-40,-40,-30],
  [-30,-40,-40,-50,-50,-40,-40,-30],
  [-30,-40,-40,-50,-50,-40,-40,-30],
  [-20,-30,-30,-40,-40,-30,-30,-20],
  [-10,-20,-20,-20,-20,-20,-20,-10],
  [20, 20,  0,  0,  0,  0, 20, 20],
  [20, 30, 10,  0,  0, 10, 30, 20]
];

class ChessBot {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.botName = config.botName || 'ChessBot';
    this.serverUrl = config.serverUrl || DEFAULT_SERVER;
    this.ws = null;
    this.gameId = null;
    this.myColor = null;
    this.gameState = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.connected = false;
    this.authenticated = false;
    this.moveCount = 0;
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
        apiKey: this.apiKey
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
        console.log(`[${this.botName}] Server says welcome`);
        break;
        
      case 'waiting':
        console.log(`[${this.botName}] Waiting for opponent...`);
        this.authenticated = msg.authenticated;
        if (!this.authenticated) {
          console.log(`[${this.botName}] ⚠️  Playing as guest - scores won't count for leaderboards`);
        }
        break;
        
      case 'game_start':
        this.gameId = msg.gameId;
        this.myColor = msg.you;
        this.moveCount = 0;
        console.log(`[${this.botName}] 🎮 Game started! Playing as ${this.myColor} against ${msg.opponent} (${msg.opponentType || 'guest'})`);
        break;
        
      case 'state':
        this.handleGameState(msg);
        break;
        
      case 'game_end':
        const resultEmoji = msg.result === 'win' ? '🏆' : msg.result === 'loss' ? '💀' : '🤝';
        console.log(`[${this.botName}] ${resultEmoji} Game ended: ${msg.result.toUpperCase()} (${msg.reason})`);
        if (msg.winner) {
          console.log(`[${this.botName}] Winner: ${msg.winner}`);
        }
        // Wait for new game
        this.gameId = null;
        this.myColor = null;
        setTimeout(() => {
          console.log(`[${this.botName}] Looking for new game...`);
          this.send({ type: 'join', name: this.botName, apiKey: this.apiKey });
        }, 3000);
        break;
        
      case 'opponent_disconnected':
        console.log(`[${this.botName}] 🏆 Opponent disconnected - WIN!`);
        break;
        
      case 'error':
        console.error(`[${this.botName}] Server error: ${msg.message}`);
        break;
    }
  }

  handleGameState(state) {
    this.gameState = state;
    
    // Check for game over
    if (state.checkmate) {
      const iWon = state.turn !== this.myColor;
      console.log(`[${this.botName}] ♔ CHECKMATE! ${iWon ? 'I WIN!' : 'I LOST!'}`);
      return;
    }
    
    if (state.stalemate) {
      console.log(`[${this.botName}] ½-½ STALEMATE - Draw`);
      return;
    }
    
    // Only make move if it's our turn
    if (state.turn !== this.myColor) {
      return;
    }
    
    if (state.check) {
      console.log(`[${this.botName}] ⚠️  I'm in check!`);
    }
    
    // Choose and make a move
    const move = this.selectMove(state);
    if (move) {
      this.moveCount++;
      console.log(`[${this.botName}] Move ${this.moveCount}: ${move} (${state.legalMoves.length} options)`);
      this.send({ type: 'move', move: move });
    }
  }

  selectMove(state) {
    const { legalMoves, board, fen } = state;
    
    if (!legalMoves || legalMoves.length === 0) {
      return null;
    }
    
    // Score each move
    const scoredMoves = legalMoves.map(move => ({
      move,
      score: this.evaluateMove(move, board, state)
    }));
    
    // Sort by score (highest first)
    scoredMoves.sort((a, b) => b.score - a.score);
    
    // Add some randomness among top moves
    const topMoves = scoredMoves.filter(m => m.score >= scoredMoves[0].score - 50);
    const selected = topMoves[Math.floor(Math.random() * Math.min(3, topMoves.length))];
    
    return selected.move;
  }

  evaluateMove(moveUci, board, state) {
    let score = 0;
    
    // Parse move
    const fromFile = moveUci.charCodeAt(0) - 97;
    const fromRank = 8 - parseInt(moveUci[1]);
    const toFile = moveUci.charCodeAt(2) - 97;
    const toRank = 8 - parseInt(moveUci[3]);
    const promotion = moveUci[4];
    
    const piece = board[fromRank][fromFile];
    const captured = board[toRank][toFile];
    const isWhite = this.myColor === 'white';
    
    // Capturing is good (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
    if (captured) {
      score += PIECE_VALUES[captured] * 10 - PIECE_VALUES[piece];
    }
    
    // Promotion is very good
    if (promotion) {
      if (promotion === 'q') score += 800;
      else if (promotion === 'r') score += 400;
      else if (promotion === 'b' || promotion === 'n') score += 250;
    }
    
    // Positional evaluation
    const pieceType = piece.toLowerCase();
    let posScore = 0;
    
    // Get piece-square table value for destination
    const r = isWhite ? toRank : 7 - toRank;
    const c = toFile;
    
    switch (pieceType) {
      case 'p': posScore = PAWN_TABLE[r][c] - PAWN_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
      case 'n': posScore = KNIGHT_TABLE[r][c] - KNIGHT_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
      case 'b': posScore = BISHOP_TABLE[r][c] - BISHOP_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
      case 'r': posScore = ROOK_TABLE[r][c] - ROOK_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
      case 'q': posScore = QUEEN_TABLE[r][c] - QUEEN_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
      case 'k': posScore = KING_TABLE[r][c] - KING_TABLE[isWhite ? fromRank : 7 - fromRank][fromFile]; break;
    }
    score += posScore;
    
    // Center control bonus
    if ((toFile === 3 || toFile === 4) && (toRank === 3 || toRank === 4)) {
      score += 20;
    }
    
    // Castling is usually good in the opening
    if (pieceType === 'k' && Math.abs(toFile - fromFile) === 2) {
      score += 60;
    }
    
    // Development in the opening (first 10 moves)
    if (this.moveCount < 10) {
      // Knights and bishops to active squares
      if (pieceType === 'n' || pieceType === 'b') {
        if (fromRank === (isWhite ? 7 : 0)) {
          score += 30; // Developing from back rank
        }
      }
      // Don't move queen too early
      if (pieceType === 'q' && this.moveCount < 5) {
        score -= 20;
      }
      // Don't move king (unless castling)
      if (pieceType === 'k' && Math.abs(toFile - fromFile) !== 2) {
        score -= 30;
      }
    }
    
    // Avoid moving to squares attacked by pawns (very costly)
    // Simplified check - just penalize moving to enemy pawn-controlled squares
    const enemyPawnDir = isWhite ? 1 : -1;
    const enemyPawn = isWhite ? 'p' : 'P';
    if (toRank + enemyPawnDir >= 0 && toRank + enemyPawnDir < 8) {
      if (toFile > 0 && board[toRank + enemyPawnDir][toFile - 1] === enemyPawn) {
        score -= PIECE_VALUES[piece] / 4;
      }
      if (toFile < 7 && board[toRank + enemyPawnDir][toFile + 1] === enemyPawn) {
        score -= PIECE_VALUES[piece] / 4;
      }
    }
    
    // Add small random factor to avoid predictability
    score += Math.random() * 10;
    
    return score;
  }
}

// Load config
function loadConfig() {
  // Priority: env var > config.json > error
  if (process.env.BOT_API_KEY) {
    return {
      apiKey: process.env.BOT_API_KEY,
      botName: process.env.BOT_NAME || 'ChessBot',
      serverUrl: process.argv[2] || DEFAULT_SERVER
    };
  }
  
  if (fs.existsSync(CONFIG_FILE)) {
    try {
      const config = JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8'));
      return {
        apiKey: config.apiKey,
        botName: config.chessName || config.botName || 'ChessBot',
        serverUrl: process.argv[2] || config.chessServerUrl || DEFAULT_SERVER
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
║     BOT_API_KEY=arcade_bot_xxxx node chess-bot.js              ║
║                                                                ║
║  Without an API key, the bot will play as a guest and          ║
║  scores won't count for leaderboards.                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
`);
  
  // Allow running without API key (as guest)
  return {
    apiKey: null,
    botName: process.argv[2] || `ChessGuest_${Math.floor(Math.random() * 1000)}`,
    serverUrl: process.argv[3] || DEFAULT_SERVER
  };
}

// Main
const config = loadConfig();
const bot = new ChessBot(config);
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
║           ClawArcade Chess Bot v1.0                           ║
╠═══════════════════════════════════════════════════════════════╣
║  Bot Name:  ${config.botName.padEnd(48)}║
║  Server:    ${config.serverUrl.slice(0, 48).padEnd(48)}║
║  Auth:      ${(config.apiKey ? '✅ API Key configured' : '❌ Guest mode').padEnd(48)}║
║                                                               ║
║  Strategy: Material + Positional Evaluation                   ║
║                                                               ║
║  Press Ctrl+C to stop                                         ║
╚═══════════════════════════════════════════════════════════════╝
`);
