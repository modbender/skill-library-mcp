const fetch = require('node-fetch');
const { getToken } = require('./getToken');
const { fetchConversations } = require('./fetchConversations');

/**
 * Get primary customer ID from a conversation
 * @param {number} conversationId - The conversation ID
 * @param {number} inboxId - The inbox ID
 * @returns {Promise<number>} - Customer ID
 */
async function getConversationCustomerId(conversationId, inboxId) {
  const result = await fetchConversations(inboxId, {
    number: conversationId,
    embed: ''
  });
  
  if (!result._embedded || !result._embedded.conversations || result._embedded.conversations.length === 0) {
    throw new Error(`Conversation ${conversationId} not found`);
  }
  
  const conversation = result._embedded.conversations[0];
  return conversation.primaryCustomer.id;
}

/**
 * Create a note on a Helpscout conversation
 * @param {number} conversationId - The conversation ID
 * @param {string} text - The note text (plain text or HTML)
 * @returns {Promise<Object>} - Response from Helpscout API
 */
async function createNote(conversationId, text) {
  if (!text) {
    throw new Error('Note text is required');
  }

  const token = await getToken();

  const payload = {
    text: text
  };

  const response = await fetch(`https://api.helpscout.net/v2/conversations/${conversationId}/notes`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to create note: ${response.status} ${response.statusText} - ${errorBody}`);
  }

  // 201 Created - location header contains the new resource ID
  const location = response.headers.get('location');
  const noteId = location ? location.split('/').pop() : null;

  return {
    success: true,
    conversationId,
    noteId,
    status: response.status,
    statusText: response.statusText
  };
}

/**
 * Send a customer-visible reply to a Helpscout conversation
 * @param {number} conversationId - The conversation ID
 * @param {Object} options - Reply options
 * @param {string} options.text - The reply text (plain text or HTML)
 * @param {number} [options.inboxId] - Inbox ID (required if customerId not provided - will auto-fetch customer)
 * @param {number} [options.customerId] - Customer ID (if not provided, will be fetched from conversation)
 * @param {boolean} [options.imported=false] - Mark as imported (won't send email to customer)
 * @param {string} [options.status] - Conversation status after reply: 'active', 'pending', 'closed'
 * @param {number} [options.userId] - User ID sending the reply (defaults to authenticated user)
 * @returns {Promise<Object>} - Response from Helpscout API
 
  NOTE: For now, this skill is not allowed the send replies, so this function is not exported.
        Only notes can be created in a Helpscout ticket.
*/
async function sendReply(conversationId, options = {}) {
  const { text, inboxId, customerId, imported = false, status, userId } = options;

  if (!text) {
    throw new Error('Reply text is required');
  }

  // Get customer ID if not provided
  let customerIdToUse = customerId;
  if (!customerIdToUse) {
    if (!inboxId) {
      throw new Error('Either customerId or inboxId must be provided');
    }
    customerIdToUse = await getConversationCustomerId(conversationId, inboxId);
  }

  const token = await getToken();

  const payload = {
    text: text,
    imported: imported,
    customer: {
      id: customerIdToUse
    }
  };

  // Set status if provided
  if (status) {
    payload.status = status;
  }

  // Set user if provided
  if (userId) {
    payload.user = userId;
  }

  const response = await fetch(`https://api.helpscout.net/v2/conversations/${conversationId}/reply`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Failed to send reply: ${response.status} ${response.statusText} - ${errorBody}`);
  }

  // 201 Created - location header contains the new resource ID
  const location = response.headers.get('location');
  const replyId = location ? location.split('/').pop() : null;

  return {
    success: true,
    conversationId,
    replyId,
    customerId: customerIdToUse,
    status: response.status,
    statusText: response.statusText
  };
}

module.exports = { /* sendReply ,*/ createNote };
