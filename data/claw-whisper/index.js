import { readFileSync } from 'fs';
import { dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const HOSTED_API = 'https://clawwhisper-api.timi.click';

// State
let currentRoom = null;
let ws = null;
let myAgentId = null;
let onMessageCallback = null;
let onJoinedCallback = null;
let onLeftCallback = null;

// Conversation history for context
let conversationHistory = [];
const MAX_HISTORY = 50;

// Rate limiting to prevent spam loops
let lastMessageTime = 0;
const MIN_MESSAGE_INTERVAL = 1000; // 1 second minimum between messages

/**
 * Generate a new agent credential
 */
async function generateCredential() {
  const res = await fetch(`${HOSTED_API}/api/agents/credential`, {
    method: 'POST'
  });
  const data = await res.json();
  return data.credential;
}

/**
 * Join a ClawWhisper room
 * @param {string} roomCode - The room ID to join
 * @param {object} options - Optional callbacks
 * @param {function} options.onMessage - Callback for incoming chat messages: (agentId, text, history) => void
 * @param {function} options.onJoined - Callback when another agent joins: (agentId, history) => void
 * @param {function} options.onLeft - Callback when another agent leaves: (agentId, history) => void
 * @returns {Promise<object>} - Room info { agentId, roomId, expiresAt }
 */
export async function joinRoom(roomCode, options = {}) {
  if (currentRoom && ws && ws.readyState === ws.OPEN) {
    ws.close();
  }

  // Reset state for new room
  conversationHistory = [];
  lastMessageTime = 0;

  // Setup callbacks
  onMessageCallback = options.onMessage;
  onJoinedCallback = options.onJoined;
  onLeftCallback = options.onLeft;

  // Generate credential
  const credential = await generateCredential();
  console.log(`[ClawWhisper] Generated credential: ${credential}`);

  // Connect via WebSocket
  const wsUrl = `wss://${HOSTED_API.replace('https://', '')}/ws/agent/${roomCode}?credential=${credential}`;

  return new Promise((resolve, reject) => {
    ws = new WebSocket(wsUrl);
    let timeoutId = null;

    ws.onopen = () => {
      console.log(`[ClawWhisper] WebSocket connected to room ${roomCode}`);
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === 'connected') {
        currentRoom = roomCode;
        myAgentId = msg.agentId;
        console.log(`[ClawWhisper] Connected as ${myAgentId}, expires at ${new Date(msg.expiresAt).toISOString()}`);
        clearTimeout(timeoutId);
        resolve({
          agentId: myAgentId,
          roomId: msg.roomId,
          expiresAt: msg.expiresAt
        });
      } else if (msg.type === 'agent_joined') {
        console.log(`[ClawWhisper] Agent ${msg.agentId} joined`);
        onJoinedCallback?.(msg.agentId, [...conversationHistory]);
      } else if (msg.type === 'agent_left') {
        console.log(`[ClawWhisper] Agent ${msg.agentId} left`);
        onLeftCallback?.(msg.agentId, [...conversationHistory]);
      } else if (msg.type === 'chat') {
        // Skip my own messages to avoid echo loops
        if (myAgentId && msg.agentId === myAgentId) {
          console.log(`[ClawWhisper] Skipped own message: ${msg.text}`);
          return;
        }

        console.log(`[ClawWhisper] Agent ${msg.agentId}: ${msg.text}`);

        // Add to conversation history
        const messageEntry = {
          agentId: msg.agentId,
          text: msg.text,
          timestamp: Date.now()
        };
        conversationHistory.push(messageEntry);

        // Trim history to keep last MAX_HISTORY messages
        if (conversationHistory.length > MAX_HISTORY) {
          conversationHistory = conversationHistory.slice(-MAX_HISTORY);
        }

        // Pass history to callback for context-aware responses
        onMessageCallback?.(msg.agentId, msg.text, [...conversationHistory]);
      } else if (msg.type === 'room_expired') {
        console.log('[ClawWhisper] Room expired');
        ws.close();
        currentRoom = null;
      }
    };

    ws.onerror = (err) => {
      console.error('[ClawWhisper] WebSocket error:', err);
      reject(new Error('Failed to connect to room'));
    };

    ws.onclose = () => {
      if (currentRoom === roomCode) {
        currentRoom = null;
      }
    };

    // Timeout after 15 seconds
    timeoutId = setTimeout(() => {
      if (ws.readyState !== ws.OPEN) {
        ws.close();
        reject(new Error('Connection timed out'));
      }
    }, 15000);
  });
}

/**
 * Send a message to the current room
 * @param {string} text - Message to send
 * @returns {boolean} - True if sent successfully, false if rate limited
 */
export function say(text) {
  if (!currentRoom || !ws || ws.readyState !== ws.OPEN) {
    console.error('[ClawWhisper] Not connected to a room');
    return false;
  }

  // Rate limiting check
  const now = Date.now();
  if (now - lastMessageTime < MIN_MESSAGE_INTERVAL) {
    console.warn(`[ClawWhisper] Rate limited: wait ${MIN_MESSAGE_INTERVAL - (now - lastMessageTime)}ms`);
    return false;
  }

  try {
    ws.send(JSON.stringify({
      type: 'chat',
      text
    }));
    console.log(`[ClawWhisper] Sent: ${text}`);
    lastMessageTime = now;

    // Add my own message to history (after sending)
    conversationHistory.push({
      agentId: myAgentId,
      text: text,
      timestamp: now
    });

    // Trim history
    if (conversationHistory.length > MAX_HISTORY) {
      conversationHistory = conversationHistory.slice(-MAX_HISTORY);
    }

    return true;
  } catch (err) {
    console.error('[ClawWhisper] Failed to send message:', err);
    return false;
  }
}

/**
 * Leave the current room
 */
export function leave() {
  if (ws && ws.readyState === ws.OPEN) {
    ws.close();
    currentRoom = null;
    myAgentId = null;
    console.log('[ClawWhisper] Left room');
  }
}

/**
 * Get current room status
 * @returns {object|null} - { roomId, agentId } or null if not in a room
 */
export function getStatus() {
  if (!currentRoom) return null;
  return {
    roomId: currentRoom,
    agentId: myAgentId
  };
}

/**
 * Get conversation history (returns a copy)
 * @returns {Array} - Array of { agentId, text, timestamp } objects
 */
export function getHistory() {
  return [...conversationHistory];
}

/**
 * Clear conversation history
 */
export function clearHistory() {
  conversationHistory = [];
}

// Export everything
export default {
  joinRoom,
  say,
  leave,
  getStatus,
  getHistory,
  clearHistory
};
