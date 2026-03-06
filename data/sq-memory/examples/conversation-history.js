/**
 * Example: Conversation History Tracker
 * 
 * Store conversation summaries beyond the context window limit.
 * This enables true long-term memory for extended interactions.
 */

/**
 * Store a conversation summary
 */
async function storeConversationSummary(conversationId, summary) {
  const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
  const coordinate = `conversations/${date}/${conversationId}`;
  
  await remember(coordinate, JSON.stringify({
    date: date,
    conversationId: conversationId,
    summary: summary,
    timestamp: Date.now()
  }));
  
  return `Stored summary for conversation ${conversationId}`;
}

/**
 * Recall conversation history for a specific conversation
 */
async function recallConversation(conversationId) {
  const coords = await list_memories(`conversations/`);
  const relevant = coords.filter(c => c.includes(conversationId));
  
  const history = [];
  for (const coord of relevant) {
    const text = await recall(coord);
    if (text) {
      try {
        history.push(JSON.parse(text));
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return history.sort((a, b) => a.timestamp - b.timestamp);
}

/**
 * Get recent conversation summaries (last N days)
 */
async function getRecentConversations(days = 7) {
  const now = new Date();
  const cutoff = new Date(now.getTime() - (days * 24 * 60 * 60 * 1000));
  
  const coords = await list_memories('conversations/');
  const recent = [];
  
  for (const coord of coords) {
    const text = await recall(coord);
    if (text) {
      try {
        const data = JSON.parse(text);
        const convDate = new Date(data.date);
        if (convDate >= cutoff) {
          recent.push(data);
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return recent.sort((a, b) => b.timestamp - a.timestamp);
}

/**
 * Usage example in agent conversation:
 */

// After a long conversation spanning multiple sessions:
// AGENT: "Let me summarize what we discussed..."
// AGENT uses: storeConversationSummary("conv-2026-02-11", "User asked about phext storage. Explained 11D coordinates, showed examples of SQ API usage, discussed multi-tenant architecture.")

// Days later, context window has cleared:
// USER: "What did we talk about last week regarding phext?"
// AGENT uses: getRecentConversations(7)
// AGENT: "We discussed phext storage on February 11th. I explained 11D coordinates and showed you how to use the SQ API."

// Continuing a specific conversation thread:
// USER: "Continue our discussion about phext storage"
// AGENT uses: recallConversation("conv-2026-02-11")
// AGENT: "Right, we were discussing phext's 11D coordinate system. You wanted to know about..."

/**
 * Recommended coordinate structure for conversations:
 * 
 * conversations/2026-02-11/conv-001
 * conversations/2026-02-11/conv-002
 * conversations/2026-02-12/conv-003
 * 
 * This enables:
 * - Chronological browsing
 * - Date-range queries
 * - Conversation threading
 */

/**
 * Advanced: Store conversation turns (messages)
 */
async function storeConversationTurn(conversationId, turn, role, message) {
  const date = new Date().toISOString().split('T')[0];
  const coordinate = `conversations/${date}/${conversationId}/turn-${turn}`;
  
  await remember(coordinate, JSON.stringify({
    role: role,        // "user" or "assistant"
    message: message,
    timestamp: Date.now(),
    turn: turn
  }));
}

/**
 * Retrieve full conversation transcript
 */
async function getConversationTranscript(conversationId) {
  const coords = await list_memories(`conversations/`);
  const turns = coords
    .filter(c => c.includes(conversationId))
    .filter(c => c.includes('/turn-'));
  
  const transcript = [];
  for (const coord of turns) {
    const text = await recall(coord);
    if (text) {
      try {
        transcript.push(JSON.parse(text));
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
  
  return transcript.sort((a, b) => a.turn - b.turn);
}

// This enables:
// - Complete conversation replay
// - Context reconstruction after restarts
// - Training data generation
// - Audit trails
