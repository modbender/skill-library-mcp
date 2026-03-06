const fetch = require('node-fetch');
const { getToken } = require('./getToken');

// Fetch conversations from a specific inbox
async function fetchConversations({ inboxId = null,
                                    status = null,
                                    folderId = null,
                                    assignedTo = null,
                                    customerId = null,
                                    number = null,
                                    modifiedSince = null,
                                    sortField = null,
                                    sortOrder = null,
                                    tag = null,
                                    query = null,
                                    page = null}) {
  const token = await getToken();
  const parameters = new URLSearchParams({
    mailbox: inboxId,
    status: status,
    folderId: folderId,
    assignedTo: assignedTo,
    customerId: customerId,
    number: number,
    modifiedSince: modifiedSince,
    sortField: sortField,
    sortOrder: sortOrder,
    tag: tag,
    query: query,
    page: page
  });

  // Filter out null parameters
  for (const [key, value] of parameters.entries()) {
    if (value === null) {
      parameters.delete(key);
    }
  }

  const response = await fetch(`https://api.helpscout.net/v2/conversations?${parameters}`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch conversations: ${response.status} ${response.statusText}`);
  }

  const conversations = await response.json();
  return conversations;
}

module.exports = { fetchConversations };