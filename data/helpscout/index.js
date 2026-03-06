const { getCredentials } = require('./scripts/getCredentials');
const { getToken } = require('./scripts/getToken');
const { fetchConversations } = require('./scripts/fetchConversations');
const { sendReply, createNote } = require('./scripts/sendReply');

/**
 * Fetch conversations from all configured inboxes
 * @param {Object} options - Optional query parameters (see fetchConversations for details)
 * @returns {Promise<Array>} - Array of results, one per inbox
 */
async function fetchAllInboxes(options = {}) {
  const { inboxIds } = getCredentials();
  const results = await Promise.all(
    inboxIds.map(inboxId => fetchConversations(inboxId, options))
  );
  return results;
}

module.exports = { 
  getCredentials, 
  getToken, 
  fetchConversations,
  fetchAllInboxes,
  sendReply,
  createNote
};