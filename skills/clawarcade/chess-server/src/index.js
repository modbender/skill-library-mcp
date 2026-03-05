// Multiplayer Chess Server - Cloudflare Durable Objects
// With authentication integration for ClawArcade

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key',
};

// API endpoint for authentication and match reporting
const API_BASE = 'https://clawarcade-api.bassel-amin92-76d.workers.dev';

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
      const id = env.CHESS_ROOM.idFromName(roomId);
      const room = env.CHESS_ROOM.get(id);
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
    
    return new Response('ClawArcade Chess Server - Connect via WebSocket at /ws/{roomId}', {
      headers: { ...CORS_HEADERS, 'Content-Type': 'text/plain' }
    });
  }
};

// ==================== CHESS ENGINE ====================

const INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

class ChessEngine {
  constructor() {
    this.reset();
  }

  reset() {
    this.loadFen(INITIAL_FEN);
  }

  loadFen(fen) {
    const parts = fen.split(' ');
    const rows = parts[0].split('/');
    
    this.board = [];
    for (let r = 0; r < 8; r++) {
      this.board[r] = [];
      let c = 0;
      for (const char of rows[r]) {
        if (char >= '1' && char <= '8') {
          for (let i = 0; i < parseInt(char); i++) {
            this.board[r][c++] = null;
          }
        } else {
          this.board[r][c++] = char;
        }
      }
    }
    
    this.turn = parts[1] === 'w' ? 'white' : 'black';
    this.castling = parts[2] || '-';
    this.enPassant = parts[3] || '-';
    this.halfmove = parseInt(parts[4]) || 0;
    this.fullmove = parseInt(parts[5]) || 1;
    this.moveHistory = [];
  }

  getFen() {
    let fen = '';
    for (let r = 0; r < 8; r++) {
      let empty = 0;
      for (let c = 0; c < 8; c++) {
        if (this.board[r][c]) {
          if (empty > 0) { fen += empty; empty = 0; }
          fen += this.board[r][c];
        } else {
          empty++;
        }
      }
      if (empty > 0) fen += empty;
      if (r < 7) fen += '/';
    }
    fen += ` ${this.turn === 'white' ? 'w' : 'b'} ${this.castling || '-'} ${this.enPassant || '-'} ${this.halfmove} ${this.fullmove}`;
    return fen;
  }

  getBoard() {
    return this.board.map(row => row.map(p => p || ''));
  }

  isWhite(piece) { return piece && piece === piece.toUpperCase(); }
  isBlack(piece) { return piece && piece === piece.toLowerCase(); }
  isAlly(piece, white) { return white ? this.isWhite(piece) : this.isBlack(piece); }
  isEnemy(piece, white) { return white ? this.isBlack(piece) : this.isWhite(piece); }

  // Convert UCI notation (e.g., "e2e4") to board coordinates
  parseUci(uci) {
    if (uci.length < 4) return null;
    const fc = uci.charCodeAt(0) - 97; // 'a' = 0
    const fr = 8 - parseInt(uci[1]);
    const tc = uci.charCodeAt(2) - 97;
    const tr = 8 - parseInt(uci[3]);
    const promotion = uci[4] || null;
    return { fr, fc, tr, tc, promotion };
  }

  // Convert board coordinates to UCI notation
  toUci(fr, fc, tr, tc, promotion = null) {
    const files = 'abcdefgh';
    let uci = files[fc] + (8 - fr) + files[tc] + (8 - tr);
    if (promotion) uci += promotion.toLowerCase();
    return uci;
  }

  // Get all raw moves for a piece (doesn't check for self-check)
  getRawMoves(r, c) {
    const p = this.board[r][c];
    if (!p) return [];
    const white = this.isWhite(p);
    const moves = [];
    const t = p.toLowerCase();

    const addIfValid = (tr, tc) => {
      if (tr < 0 || tr > 7 || tc < 0 || tc > 7) return false;
      if (this.isAlly(this.board[tr][tc], white)) return false;
      moves.push([tr, tc]);
      return !this.board[tr][tc];
    };

    const slide = (dr, dc) => {
      for (let i = 1; i < 8; i++) {
        if (!addIfValid(r + dr * i, c + dc * i)) break;
      }
    };

    if (t === 'p') {
      const dir = white ? -1 : 1;
      const start = white ? 6 : 1;
      const promoRow = white ? 0 : 7;
      
      // Forward moves
      if (r + dir >= 0 && r + dir < 8 && !this.board[r + dir][c]) {
        moves.push([r + dir, c]);
        if (r === start && !this.board[r + 2 * dir][c]) {
          moves.push([r + 2 * dir, c]);
        }
      }
      
      // Captures
      [-1, 1].forEach(dc => {
        const tr = r + dir, tc = c + dc;
        if (tc >= 0 && tc < 8 && tr >= 0 && tr < 8) {
          if (this.board[tr][tc] && this.isEnemy(this.board[tr][tc], white)) {
            moves.push([tr, tc]);
          }
          // En passant
          if (this.enPassant !== '-') {
            const epFile = this.enPassant.charCodeAt(0) - 97;
            const epRank = 8 - parseInt(this.enPassant[1]);
            if (tr === epRank && tc === epFile) {
              moves.push([tr, tc]);
            }
          }
        }
      });
    }

    if (t === 'n') {
      [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr, dc]) => addIfValid(r + dr, c + dc));
    }

    if (t === 'b' || t === 'q') {
      [[-1,-1],[-1,1],[1,-1],[1,1]].forEach(([dr, dc]) => slide(dr, dc));
    }

    if (t === 'r' || t === 'q') {
      [[-1,0],[1,0],[0,-1],[0,1]].forEach(([dr, dc]) => slide(dr, dc));
    }

    if (t === 'k') {
      [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]].forEach(([dr, dc]) => addIfValid(r + dr, c + dc));
      
      // Castling
      const row = white ? 7 : 0;
      const kingSide = white ? 'K' : 'k';
      const queenSide = white ? 'Q' : 'q';
      
      if (r === row && c === 4) {
        // King-side castling
        if (this.castling.includes(kingSide) && 
            !this.board[row][5] && !this.board[row][6] &&
            !this.isSquareAttacked(row, 4, !white) &&
            !this.isSquareAttacked(row, 5, !white) &&
            !this.isSquareAttacked(row, 6, !white)) {
          moves.push([row, 6]);
        }
        // Queen-side castling
        if (this.castling.includes(queenSide) &&
            !this.board[row][1] && !this.board[row][2] && !this.board[row][3] &&
            !this.isSquareAttacked(row, 4, !white) &&
            !this.isSquareAttacked(row, 3, !white) &&
            !this.isSquareAttacked(row, 2, !white)) {
          moves.push([row, 2]);
        }
      }
    }

    return moves;
  }

  isSquareAttacked(r, c, byWhite) {
    for (let rr = 0; rr < 8; rr++) {
      for (let cc = 0; cc < 8; cc++) {
        const p = this.board[rr][cc];
        if (p && this.isWhite(p) === byWhite) {
          const t = p.toLowerCase();
          // Special handling for king to avoid infinite recursion
          if (t === 'k') {
            if (Math.abs(rr - r) <= 1 && Math.abs(cc - c) <= 1) return true;
          } else if (t === 'p') {
            // Pawns attack diagonally
            const dir = byWhite ? -1 : 1;
            if (r === rr + dir && Math.abs(c - cc) === 1) return true;
          } else {
            // Use raw moves for other pieces
            const moves = this.getRawMovesWithoutCastling(rr, cc);
            if (moves.some(m => m[0] === r && m[1] === c)) return true;
          }
        }
      }
    }
    return false;
  }

  // Helper to get raw moves without castling (to avoid recursion in attack check)
  getRawMovesWithoutCastling(r, c) {
    const p = this.board[r][c];
    if (!p) return [];
    const white = this.isWhite(p);
    const moves = [];
    const t = p.toLowerCase();

    const addIfValid = (tr, tc) => {
      if (tr < 0 || tr > 7 || tc < 0 || tc > 7) return false;
      if (this.isAlly(this.board[tr][tc], white)) return false;
      moves.push([tr, tc]);
      return !this.board[tr][tc];
    };

    const slide = (dr, dc) => {
      for (let i = 1; i < 8; i++) {
        if (!addIfValid(r + dr * i, c + dc * i)) break;
      }
    };

    if (t === 'n') {
      [[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr, dc]) => addIfValid(r + dr, c + dc));
    }
    if (t === 'b' || t === 'q') {
      [[-1,-1],[-1,1],[1,-1],[1,1]].forEach(([dr, dc]) => slide(dr, dc));
    }
    if (t === 'r' || t === 'q') {
      [[-1,0],[1,0],[0,-1],[0,1]].forEach(([dr, dc]) => slide(dr, dc));
    }
    if (t === 'k') {
      [[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]].forEach(([dr, dc]) => addIfValid(r + dr, c + dc));
    }

    return moves;
  }

  inCheck(white) {
    const k = white ? 'K' : 'k';
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        if (this.board[r][c] === k) {
          return this.isSquareAttacked(r, c, !white);
        }
      }
    }
    return false;
  }

  // Get legal moves for a piece (filters out moves that leave king in check)
  getLegalMoves(r, c) {
    const p = this.board[r][c];
    if (!p) return [];
    const white = this.isWhite(p);
    
    return this.getRawMoves(r, c).filter(([tr, tc]) => {
      // Simulate the move
      const captured = this.board[tr][tc];
      const orig = this.board[r][c];
      this.board[tr][tc] = orig;
      this.board[r][c] = null;
      
      // Handle en passant capture
      let epPiece = null;
      if (p.toLowerCase() === 'p' && c !== tc && !captured) {
        const epR = white ? tr + 1 : tr - 1;
        epPiece = this.board[epR][tc];
        this.board[epR][tc] = null;
      }
      
      // Handle castling - move rook
      let rookMove = null;
      if (p.toLowerCase() === 'k' && Math.abs(tc - c) === 2) {
        if (tc > c) {
          rookMove = { fr: tr, fc: 7, tr: tr, tc: 5 };
          this.board[tr][5] = this.board[tr][7];
          this.board[tr][7] = null;
        } else {
          rookMove = { fr: tr, fc: 0, tr: tr, tc: 3 };
          this.board[tr][3] = this.board[tr][0];
          this.board[tr][0] = null;
        }
      }
      
      const check = this.inCheck(white);
      
      // Undo the move
      this.board[r][c] = orig;
      this.board[tr][tc] = captured;
      if (epPiece !== null) {
        const epR = white ? tr + 1 : tr - 1;
        this.board[epR][tc] = epPiece;
      }
      if (rookMove) {
        this.board[rookMove.fr][rookMove.fc] = this.board[rookMove.tr][rookMove.tc];
        this.board[rookMove.tr][rookMove.tc] = null;
      }
      
      return !check;
    });
  }

  // Get all legal moves in UCI format
  getAllLegalMoves() {
    const white = this.turn === 'white';
    const moves = [];
    
    for (let r = 0; r < 8; r++) {
      for (let c = 0; c < 8; c++) {
        const p = this.board[r][c];
        if (p && this.isAlly(p, white)) {
          const legal = this.getLegalMoves(r, c);
          for (const [tr, tc] of legal) {
            // Check for pawn promotion
            if (p.toLowerCase() === 'p' && (tr === 0 || tr === 7)) {
              ['q', 'r', 'b', 'n'].forEach(promo => {
                moves.push(this.toUci(r, c, tr, tc, promo));
              });
            } else {
              moves.push(this.toUci(r, c, tr, tc));
            }
          }
        }
      }
    }
    
    return moves;
  }

  // Make a move (UCI format)
  makeMove(uci) {
    const move = this.parseUci(uci);
    if (!move) return { valid: false, error: 'Invalid UCI format' };
    
    const { fr, fc, tr, tc, promotion } = move;
    const piece = this.board[fr][fc];
    
    if (!piece) return { valid: false, error: 'No piece at source square' };
    
    const white = this.isWhite(piece);
    if ((white && this.turn !== 'white') || (!white && this.turn !== 'black')) {
      return { valid: false, error: 'Not your turn' };
    }
    
    // Check if move is legal
    const legal = this.getLegalMoves(fr, fc);
    if (!legal.some(m => m[0] === tr && m[1] === tc)) {
      return { valid: false, error: 'Illegal move' };
    }
    
    // Execute the move
    const captured = this.board[tr][tc];
    let isCapture = !!captured;
    let isCastle = false;
    let isEnPassant = false;
    let isPromotion = false;
    
    // En passant capture
    if (piece.toLowerCase() === 'p' && fc !== tc && !captured) {
      const epR = white ? tr + 1 : tr - 1;
      this.board[epR][tc] = null;
      isCapture = true;
      isEnPassant = true;
    }
    
    // Castling - move the rook
    if (piece.toLowerCase() === 'k' && Math.abs(tc - fc) === 2) {
      isCastle = true;
      if (tc > fc) {
        // King-side
        this.board[tr][5] = this.board[tr][7];
        this.board[tr][7] = null;
      } else {
        // Queen-side
        this.board[tr][3] = this.board[tr][0];
        this.board[tr][0] = null;
      }
    }
    
    // Move the piece
    this.board[tr][tc] = piece;
    this.board[fr][fc] = null;
    
    // Pawn promotion
    if (piece.toLowerCase() === 'p' && (tr === 0 || tr === 7)) {
      isPromotion = true;
      const promoPiece = promotion || 'q';
      this.board[tr][tc] = white ? promoPiece.toUpperCase() : promoPiece.toLowerCase();
    }
    
    // Update castling rights
    if (piece.toLowerCase() === 'k') {
      // King moved - remove both castling rights
      if (white) {
        this.castling = this.castling.replace('K', '').replace('Q', '');
      } else {
        this.castling = this.castling.replace('k', '').replace('q', '');
      }
    }
    if (piece.toLowerCase() === 'r') {
      // Rook moved - remove that side's castling
      if (fr === 7 && fc === 0) this.castling = this.castling.replace('Q', '');
      if (fr === 7 && fc === 7) this.castling = this.castling.replace('K', '');
      if (fr === 0 && fc === 0) this.castling = this.castling.replace('q', '');
      if (fr === 0 && fc === 7) this.castling = this.castling.replace('k', '');
    }
    // Rook captured - remove castling
    if (tr === 0 && tc === 0) this.castling = this.castling.replace('q', '');
    if (tr === 0 && tc === 7) this.castling = this.castling.replace('k', '');
    if (tr === 7 && tc === 0) this.castling = this.castling.replace('Q', '');
    if (tr === 7 && tc === 7) this.castling = this.castling.replace('K', '');
    
    if (!this.castling) this.castling = '-';
    
    // Update en passant square
    if (piece.toLowerCase() === 'p' && Math.abs(tr - fr) === 2) {
      const epRank = white ? fr - 1 : fr + 1;
      this.enPassant = 'abcdefgh'[fc] + (8 - epRank);
    } else {
      this.enPassant = '-';
    }
    
    // Update halfmove clock
    if (isCapture || piece.toLowerCase() === 'p') {
      this.halfmove = 0;
    } else {
      this.halfmove++;
    }
    
    // Update fullmove number
    if (this.turn === 'black') {
      this.fullmove++;
    }
    
    // Switch turn
    this.turn = this.turn === 'white' ? 'black' : 'white';
    
    // Store move in history
    this.moveHistory.push(uci);
    
    // Check game state
    const check = this.inCheck(this.turn === 'white');
    const legalMoves = this.getAllLegalMoves();
    let checkmate = false;
    let stalemate = false;
    
    if (legalMoves.length === 0) {
      if (check) {
        checkmate = true;
      } else {
        stalemate = true;
      }
    }
    
    return {
      valid: true,
      captured: captured,
      isCapture,
      isCastle,
      isEnPassant,
      isPromotion,
      check,
      checkmate,
      stalemate
    };
  }

  getGameState() {
    const check = this.inCheck(this.turn === 'white');
    const legalMoves = this.getAllLegalMoves();
    
    return {
      fen: this.getFen(),
      board: this.getBoard(),
      turn: this.turn,
      legalMoves,
      check,
      checkmate: legalMoves.length === 0 && check,
      stalemate: legalMoves.length === 0 && !check,
      lastMove: this.moveHistory.length > 0 ? this.moveHistory[this.moveHistory.length - 1] : null
    };
  }
}

// ==================== CHESS ROOM DURABLE OBJECT ====================

export class ChessRoom {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.sessions = new Map(); // WebSocket -> session data
    this.waitingPlayer = null; // Player waiting for opponent
    this.games = new Map(); // gameId -> game state
    this.spectators = new Map(); // gameId -> Set<WebSocket>
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
      name: null,
      authenticated: false,
      accountId: null,
      accountType: null,
      apiKey: null,
      authToken: null,
      gameId: null,
      color: null,
      spectating: null,
    };
    
    this.sessions.set(ws, session);
    
    // Send welcome message
    this.send(ws, {
      type: 'welcome',
      sessionId: sessionId,
      message: 'ClawArcade Chess Server',
    });
    
    ws.addEventListener('message', async (event) => {
      try {
        const msg = JSON.parse(event.data);
        await this.handleMessage(ws, session, msg);
      } catch (e) {
        console.error('Invalid message:', e);
        this.send(ws, { type: 'error', message: 'Invalid message format' });
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
        this.handleMove(ws, session, msg);
        break;
      case 'spectate':
        this.handleSpectate(ws, session, msg);
        break;
      case 'resign':
        this.handleResign(ws, session);
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

  async handleJoin(ws, session, msg) {
    const { name, token, apiKey } = msg;
    
    // Try to authenticate
    let authResult = null;
    if (token || apiKey) {
      authResult = await this.validateAuth(token, apiKey);
    }
    
    let displayName = (name || 'Player').slice(0, 20);
    
    if (authResult && authResult.valid) {
      session.authenticated = true;
      session.accountId = authResult.playerId;
      session.accountType = authResult.type;
      session.authToken = token;
      session.apiKey = apiKey;
      displayName = authResult.displayName || displayName;
      console.log(`Authenticated player: ${displayName} (${session.accountType})`);
    } else {
      console.log(`Guest player: ${displayName}`);
    }
    
    session.name = displayName;
    
    // Matchmaking
    if (this.waitingPlayer && this.waitingPlayer !== session) {
      // Match found! Start a game
      const opponent = this.waitingPlayer;
      this.waitingPlayer = null;
      
      const gameId = crypto.randomUUID();
      const whitePlayer = Math.random() < 0.5 ? session : opponent;
      const blackPlayer = whitePlayer === session ? opponent : session;
      
      const game = {
        id: gameId,
        engine: new ChessEngine(),
        white: whitePlayer,
        black: blackPlayer,
        startTime: Date.now(),
        moves: [],
      };
      
      this.games.set(gameId, game);
      this.spectators.set(gameId, new Set());
      
      whitePlayer.gameId = gameId;
      whitePlayer.color = 'white';
      blackPlayer.gameId = gameId;
      blackPlayer.color = 'black';
      
      // Notify both players
      const state = game.engine.getGameState();
      
      this.send(whitePlayer.ws, {
        type: 'game_start',
        gameId: gameId,
        you: 'white',
        opponent: blackPlayer.name,
        opponentType: blackPlayer.accountType || 'guest',
      });
      
      this.send(blackPlayer.ws, {
        type: 'game_start',
        gameId: gameId,
        you: 'black',
        opponent: whitePlayer.name,
        opponentType: whitePlayer.accountType || 'guest',
      });
      
      // Send initial state to both
      this.sendState(game, whitePlayer.ws, 'white');
      this.sendState(game, blackPlayer.ws, 'black');
      
      console.log(`Game started: ${whitePlayer.name} (white) vs ${blackPlayer.name} (black)`);
    } else {
      // No opponent yet, wait
      this.waitingPlayer = session;
      this.send(ws, {
        type: 'waiting',
        message: 'Waiting for opponent...',
        authenticated: session.authenticated,
        accountType: session.accountType,
      });
      console.log(`${displayName} waiting for opponent`);
    }
  }

  sendState(game, ws, color) {
    const state = game.engine.getGameState();
    this.send(ws, {
      type: 'state',
      fen: state.fen,
      board: state.board,
      turn: state.turn,
      you: color,
      legalMoves: state.turn === color ? state.legalMoves : [],
      check: state.check,
      checkmate: state.checkmate,
      stalemate: state.stalemate,
      lastMove: state.lastMove,
    });
  }

  handleMove(ws, session, msg) {
    const { move } = msg;
    
    if (!session.gameId) {
      this.send(ws, { type: 'error', message: 'Not in a game' });
      return;
    }
    
    const game = this.games.get(session.gameId);
    if (!game) {
      this.send(ws, { type: 'error', message: 'Game not found' });
      return;
    }
    
    // Check if it's this player's turn
    const state = game.engine.getGameState();
    if (state.turn !== session.color) {
      this.send(ws, { type: 'error', message: 'Not your turn' });
      return;
    }
    
    // Try to make the move
    const result = game.engine.makeMove(move);
    
    if (!result.valid) {
      this.send(ws, { type: 'error', message: result.error });
      return;
    }
    
    game.moves.push(move);
    
    // Send updated state to both players
    this.sendState(game, game.white.ws, 'white');
    this.sendState(game, game.black.ws, 'black');
    
    // Send to spectators
    const spectatorSet = this.spectators.get(session.gameId);
    if (spectatorSet) {
      const newState = game.engine.getGameState();
      for (const spectatorWs of spectatorSet) {
        this.send(spectatorWs, {
          type: 'state',
          fen: newState.fen,
          board: newState.board,
          turn: newState.turn,
          you: null,
          legalMoves: [],
          check: newState.check,
          checkmate: newState.checkmate,
          stalemate: newState.stalemate,
          lastMove: newState.lastMove,
          whiteName: game.white.name,
          blackName: game.black.name,
        });
      }
    }
    
    // Check for game end
    if (result.checkmate || result.stalemate) {
      this.endGame(game, result.checkmate ? (session.color === 'white' ? 'white' : 'black') : 'draw');
    }
  }

  handleSpectate(ws, session, msg) {
    const { gameId } = msg;
    
    // If no gameId specified, find any active game
    let targetGameId = gameId;
    if (!targetGameId) {
      for (const [id, game] of this.games) {
        targetGameId = id;
        break;
      }
    }
    
    if (!targetGameId) {
      this.send(ws, { type: 'error', message: 'No games to spectate' });
      return;
    }
    
    const game = this.games.get(targetGameId);
    if (!game) {
      this.send(ws, { type: 'error', message: 'Game not found' });
      return;
    }
    
    session.spectating = targetGameId;
    
    let spectatorSet = this.spectators.get(targetGameId);
    if (!spectatorSet) {
      spectatorSet = new Set();
      this.spectators.set(targetGameId, spectatorSet);
    }
    spectatorSet.add(ws);
    
    const state = game.engine.getGameState();
    this.send(ws, {
      type: 'spectating',
      gameId: targetGameId,
      whiteName: game.white.name,
      blackName: game.black.name,
    });
    
    this.send(ws, {
      type: 'state',
      fen: state.fen,
      board: state.board,
      turn: state.turn,
      you: null,
      legalMoves: [],
      check: state.check,
      checkmate: state.checkmate,
      stalemate: state.stalemate,
      lastMove: state.lastMove,
      whiteName: game.white.name,
      blackName: game.black.name,
    });
  }

  handleResign(ws, session) {
    if (!session.gameId) {
      this.send(ws, { type: 'error', message: 'Not in a game' });
      return;
    }
    
    const game = this.games.get(session.gameId);
    if (!game) {
      this.send(ws, { type: 'error', message: 'Game not found' });
      return;
    }
    
    const winner = session.color === 'white' ? 'black' : 'white';
    this.endGame(game, winner, 'resignation');
  }

  async endGame(game, result, reason = null) {
    const whiteName = game.white.name;
    const blackName = game.black.name;
    
    let winnerName = null;
    let loserName = null;
    
    if (result === 'white') {
      winnerName = whiteName;
      loserName = blackName;
    } else if (result === 'black') {
      winnerName = blackName;
      loserName = whiteName;
    }
    
    // Notify both players
    this.send(game.white.ws, {
      type: 'game_end',
      result: result === 'white' ? 'win' : result === 'black' ? 'loss' : 'draw',
      reason: reason || (result === 'draw' ? 'stalemate' : 'checkmate'),
      winner: winnerName,
    });
    
    this.send(game.black.ws, {
      type: 'game_end',
      result: result === 'black' ? 'win' : result === 'white' ? 'loss' : 'draw',
      reason: reason || (result === 'draw' ? 'stalemate' : 'checkmate'),
      winner: winnerName,
    });
    
    // Notify spectators
    const spectatorSet = this.spectators.get(game.id);
    if (spectatorSet) {
      for (const spectatorWs of spectatorSet) {
        this.send(spectatorWs, {
          type: 'game_end',
          result: result,
          reason: reason || (result === 'draw' ? 'stalemate' : 'checkmate'),
          winner: winnerName,
        });
      }
    }
    
    // Report to leaderboard API
    await this.reportMatch(game, result);
    
    // Cleanup
    game.white.gameId = null;
    game.white.color = null;
    game.black.gameId = null;
    game.black.color = null;
    this.games.delete(game.id);
    this.spectators.delete(game.id);
  }

  async reportMatch(game, result) {
    // Submit scores for both players
    const players = [
      { session: game.white, won: result === 'white', drew: result === 'draw' },
      { session: game.black, won: result === 'black', drew: result === 'draw' },
    ];
    
    for (const { session, won, drew } of players) {
      if (!session.apiKey && !session.authToken) continue;
      
      const score = won ? 1 : (drew ? 0.5 : 0);
      const headers = { 'Content-Type': 'application/json' };
      
      if (session.apiKey) {
        headers['X-API-Key'] = session.apiKey;
      } else if (session.authToken) {
        headers['Authorization'] = `Bearer ${session.authToken}`;
      }
      
      try {
        // If in tournament, submit to tournament endpoint
        if (session.tournamentId) {
          const response = await fetch(`${API_BASE}/api/tournaments/${session.tournamentId}/scores`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              score: score,
              metadata: { 
                submittedBy: 'chess-server', 
                gameId: game.id,
                result: won ? 'win' : (drew ? 'draw' : 'loss'),
                opponent: session === game.white ? game.black.name : game.white.name,
              },
              websocketSubmission: true,
              serverSecret: this.env.CHESS_SERVER_SECRET,
            }),
          });
          const data = await response.json();
          console.log(`Tournament score submitted for ${session.name}: ${score} pts`, data.success ? '✓' : data.error);
        } else {
          // Submit to general scores endpoint
          const response = await fetch(`${API_BASE}/api/scores`, {
            method: 'POST',
            headers,
            body: JSON.stringify({
              game: 'chess',
              score: won ? 100 : (drew ? 50 : 0), // Convert to point scale
              metadata: {
                submittedBy: 'chess-server',
                gameId: game.id,
                result: won ? 'win' : (drew ? 'draw' : 'loss'),
                opponent: session === game.white ? game.black.name : game.white.name,
              },
            }),
          });
          const data = await response.json();
          console.log(`Score submitted for ${session.name}: ${won ? 'WIN' : drew ? 'DRAW' : 'LOSS'}`, data.success ? '✓' : data.error);
        }
      } catch (e) {
        console.error(`Failed to submit score for ${session.name}:`, e);
      }
    }
  }

  handleDisconnect(ws, session) {
    console.log(`${session.name || 'Unknown'} disconnected`);
    
    // If waiting, clear waiting status
    if (this.waitingPlayer === session) {
      this.waitingPlayer = null;
    }
    
    // If in a game, opponent wins
    if (session.gameId) {
      const game = this.games.get(session.gameId);
      if (game) {
        const winner = session.color === 'white' ? 'black' : 'white';
        const opponent = session.color === 'white' ? game.black : game.white;
        
        this.send(opponent.ws, {
          type: 'opponent_disconnected',
          message: 'Opponent disconnected - you win!',
        });
        
        this.endGame(game, winner, 'disconnection');
      }
    }
    
    // If spectating, remove from spectators
    if (session.spectating) {
      const spectatorSet = this.spectators.get(session.spectating);
      if (spectatorSet) {
        spectatorSet.delete(ws);
      }
    }
    
    this.sessions.delete(ws);
  }

  send(ws, data) {
    try {
      ws.send(JSON.stringify(data));
    } catch (e) {
      // Client disconnected
    }
  }
}
