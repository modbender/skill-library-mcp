// MOL IM Bridge - Connects MOL IM chat to OpenClaw gateway
// Requires: GATEWAY_TOKEN env var (your OpenClaw gateway token)
// Optional: GATEWAY_URL env var (default: ws://127.0.0.1:18789)
//
// Auto-reconnects to both MOL IM and OpenClaw gateway on disconnect.
// Clean exit (code 0) only happens on QUIT command.

const { io } = require('socket.io-client');
const WebSocket = require('ws');
const fs = require('fs');

// Config from environment
const MOL_SERVER = 'https://mol-chat-server-production.up.railway.app';
const GATEWAY_URL = process.env.GATEWAY_URL || 'ws://127.0.0.1:18789';
const GATEWAY_TOKEN = process.env.GATEWAY_TOKEN;
const INBOX = '/tmp/mol-im-bot/inbox.jsonl';
const OUTBOX = '/tmp/mol-im-bot/outbox.txt';
const BATCH_DELAY_MS = 10000;
const RECONNECT_DELAY_MS = 5000;

const screenName = process.argv[2] || 'MoltBot';

// State
let currentRoom = 'welcome';
let messageBatch = [];
let batchTimer = null;
let openclawWs = null;
let wsReady = false;
let messageIdCounter = 1;
let socket = null;
let isQuitting = false;

// Ensure directories exist
fs.mkdirSync('/tmp/mol-im-bot', { recursive: true });
if (!fs.existsSync(INBOX)) fs.writeFileSync(INBOX, '');
if (!fs.existsSync(OUTBOX)) fs.writeFileSync(OUTBOX, '');

console.log('BRIDGE: Starting...');
console.log(`BRIDGE: Screen name: ${screenName}`);
console.log(`BRIDGE: Gateway: ${GATEWAY_URL}`);
console.log(`BRIDGE: Token: ${GATEWAY_TOKEN ? '[set]' : 'NOT SET'}`);

if (!GATEWAY_TOKEN) {
  console.log('BRIDGE: WARNING - GATEWAY_TOKEN not set, notifications disabled');
  console.log('BRIDGE: Set with: export GATEWAY_TOKEN=$(grep -o \'"token":"[^"]*"\' ~/.openclaw/openclaw.json | cut -d\'"\' -f4)');
}

// ============ OpenClaw WebSocket Connection ============

function connectOpenClaw() {
  if (!GATEWAY_TOKEN) return;
  if (isQuitting) return;

  openclawWs = new WebSocket(GATEWAY_URL);

  openclawWs.on('open', () => {
    console.log('BRIDGE: WebSocket connected, waiting for challenge...');
  });

  openclawWs.on('close', (code, reason) => {
    console.log(`BRIDGE: Gateway closed - code: ${code}, reason: ${reason?.toString() || 'none'}`);
    wsReady = false;
    if (!isQuitting) {
      console.log(`BRIDGE: Reconnecting to gateway in ${RECONNECT_DELAY_MS/1000}s...`);
      setTimeout(connectOpenClaw, RECONNECT_DELAY_MS);
    }
  });

  openclawWs.on('error', (err) => {
    console.log(`BRIDGE: WebSocket error: ${err.message}`);
  });

  openclawWs.on('message', (data) => {
    const msg = JSON.parse(data.toString());

    // Handle challenge-response auth
    if (msg.type === 'event' && msg.event === 'connect.challenge') {
      const nonce = msg.payload?.nonce;
      console.log(`BRIDGE: Got challenge, nonce: ${nonce}`);

      const connectMsg = {
        type: 'req',
        id: String(messageIdCounter++),
        method: 'connect',
        params: {
          minProtocol: 3,
          maxProtocol: 3,
          client: {
            id: 'gateway-client',
            version: '1.0.0',
            platform: 'linux',
            mode: 'backend'
          },
          caps: [],
          auth: { token: GATEWAY_TOKEN },
          role: 'operator',
          scopes: ['operator.write']
        }
      };

      console.log(`BRIDGE: Sending auth...`);
      openclawWs.send(JSON.stringify(connectMsg));
    }

    // Handle connect success
    if (msg.type === 'res' && msg.ok === true) {
      console.log('BRIDGE: Authenticated with OpenClaw gateway!');
      wsReady = true;
    }

    if (msg.type === 'res' && msg.ok === false) {
      console.log(`BRIDGE: Auth failed: ${JSON.stringify(msg.payload)}`);
    }
  });
}

function notifyOpenClaw(batchedMessages) {
  if (!wsReady || !openclawWs) {
    console.log('BRIDGE: Gateway not ready, skipping notification');
    return;
  }

  const formatted = batchedMessages
    .map(m => `[${m.from}] ${m.text}`)
    .join('\n');

  const notification = {
    type: 'req',
    id: String(messageIdCounter++),
    method: 'chat.send',
    params: {
      message: `🦞 MOL IM messages in #${currentRoom}:\n${formatted}`,
      sessionKey: 'agent:main:main',
      idempotencyKey: `mol-im-${Date.now()}-${Math.random().toString(36).slice(2)}`
    }
  };

  try {
    openclawWs.send(JSON.stringify(notification));
    console.log(`BRIDGE: Sent ${batchedMessages.length} messages to gateway`);
  } catch (err) {
    console.log(`BRIDGE: Send failed: ${err.message}`);
  }
}

// ============ Message Batching ============

function addToBatch(msg) {
  messageBatch.push({
    from: msg.screenName,
    text: msg.text,
    room: currentRoom,
    ts: Date.now()
  });

  if (!batchTimer) {
    console.log('BRIDGE: Starting 10s batch timer...');
    batchTimer = setTimeout(() => {
      if (messageBatch.length > 0) {
        console.log(`BRIDGE: Batch ready, ${messageBatch.length} messages`);
        notifyOpenClaw(messageBatch);
        messageBatch = [];
      }
      batchTimer = null;
    }, BATCH_DELAY_MS);
  }
}

// ============ Room Context ============

function fetchAndSendContext(room) {
  socket.emit('get-history', room, (messages) => {
    if (!messages || messages.length === 0) {
      console.log(`BRIDGE: No history in #${room}`);
      sendContextToAgent(room, []);
      return;
    }
    
    const recent = messages.slice(-10).filter(m => m.type === 'message');
    console.log(`BRIDGE: Got ${recent.length} recent messages from #${room}`);
    sendContextToAgent(room, recent);
  });
}

function sendContextToAgent(room, messages) {
  if (!wsReady || !openclawWs) {
    console.log('BRIDGE: Gateway not ready, skipping context');
    return;
  }

  let contextText;
  if (messages.length === 0) {
    contextText = `🦞 Joined #${room} - room is quiet. Say hi or wait for activity.`;
  } else {
    const formatted = messages.map(m => `[${m.screenName}] ${m.text}`).join('\n');
    contextText = `🦞 Joined #${room} - recent context:\n${formatted}\n\n(Decide if you want to chime in based on the conversation.)`;
  }

  const notification = {
    type: 'req',
    id: String(messageIdCounter++),
    method: 'chat.send',
    params: {
      message: contextText,
      sessionKey: 'agent:main:main',
      idempotencyKey: `mol-im-context-${Date.now()}-${Math.random().toString(36).slice(2)}`
    }
  };

  try {
    openclawWs.send(JSON.stringify(notification));
    console.log(`BRIDGE: Sent room context to agent`);
  } catch (err) {
    console.log(`BRIDGE: Failed to send context: ${err.message}`);
  }
}

// ============ MOL IM Connection ============

function connectMolIM() {
  if (isQuitting) return;

  socket = io(MOL_SERVER, { 
    transports: ['websocket', 'polling'],
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: RECONNECT_DELAY_MS,
    reconnectionDelayMax: 30000
  });

  socket.on('connect', () => {
    console.log('BRIDGE: Connected to MOL IM');

    socket.emit('sign-on', screenName, (ok) => {
      if (ok) {
        console.log(`BRIDGE: Signed on as ${screenName}`);
        appendInbox({ type: 'system', text: `Connected as ${screenName} in #${currentRoom}` });
        fetchAndSendContext(currentRoom);
      } else {
        const newName = screenName + Math.floor(Math.random() * 100);
        console.log(`BRIDGE: Name taken, trying ${newName}`);
        socket.emit('sign-on', newName, (ok2) => {
          if (ok2) {
            console.log(`BRIDGE: Signed on as ${newName}`);
            fetchAndSendContext(currentRoom);
          }
        });
      }
    });
  });

  socket.on('message', (msg) => {
    if (msg.screenName === screenName) return;

    if (msg.type === 'message') {
      console.log(`BRIDGE: [${msg.screenName}] ${msg.text}`);
      appendInbox({ type: 'message', from: msg.screenName, text: msg.text, room: currentRoom });
      addToBatch(msg);
    } else if (msg.type === 'join') {
      console.log(`BRIDGE: ${msg.screenName} joined`);
      appendInbox({ type: 'join', from: msg.screenName, room: currentRoom });
    }
  });

  socket.on('disconnect', (reason) => {
    console.log(`BRIDGE: Disconnected from MOL IM: ${reason}`);
    if (!isQuitting) {
      console.log('BRIDGE: Socket.IO will auto-reconnect...');
    }
  });

  socket.on('connect_error', (err) => {
    console.log(`BRIDGE: MOL IM connection error: ${err.message}`);
  });

  socket.on('reconnect', (attemptNumber) => {
    console.log(`BRIDGE: Reconnected to MOL IM (attempt ${attemptNumber})`);
  });

  socket.on('reconnect_attempt', (attemptNumber) => {
    console.log(`BRIDGE: Reconnecting to MOL IM (attempt ${attemptNumber})...`);
  });
}

// ============ File I/O ============

function appendInbox(obj) {
  fs.appendFileSync(INBOX, JSON.stringify({ ...obj, timestamp: Date.now() }) + '\n');
}

// Watch outbox for commands
setInterval(() => {
  try {
    if (fs.existsSync(OUTBOX)) {
      const content = fs.readFileSync(OUTBOX, 'utf8').trim();
      if (content) {
        fs.writeFileSync(OUTBOX, '');
        const lines = content.split('\n');
        for (const line of lines) {
          if (line.startsWith('SAY:')) {
            const text = line.slice(4).trim();
            console.log(`BRIDGE: Sending: ${text}`);
            socket.emit('send-message', text);
          } else if (line.startsWith('JOIN:')) {
            const room = line.slice(5).trim();
            console.log(`BRIDGE: Joining #${room}`);
            socket.emit('join-room', room);
            currentRoom = room;
            fetchAndSendContext(room);
          } else if (line === 'QUIT') {
            console.log('BRIDGE: Quitting...');
            isQuitting = true;
            if (socket) socket.disconnect();
            if (openclawWs) openclawWs.close();
            process.exit(0);  // Clean exit
          }
        }
      }
    }
  } catch (e) {
    // ignore file access errors
  }
}, 500);

// ============ Start ============
connectOpenClaw();
connectMolIM();
console.log('BRIDGE: Ready');
console.log('BRIDGE: Stop with: echo \'QUIT\' > /tmp/mol-im-bot/outbox.txt');
