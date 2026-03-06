#!/usr/bin/env node
/**
 * Microsoft Graph - Cancel Calendar Event
 */

const https = require('https');
const { getAccessToken } = require('./auth.js');

/**
 * Make Graph API request
 */
function graphRequest(path, accessToken, options = {}) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, 'https://graph.microsoft.com');
    const reqOptions = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method: options.method || 'GET',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    };

    const req = https.request(reqOptions, (res) => {
      let data = '';
      res.on('data', (chunk) => data += chunk);
      res.on('end', () => {
        if (res.statusCode === 204 || res.statusCode === 202 || res.statusCode === 200) {
          resolve({ success: true, statusCode: res.statusCode });
        } else {
          try {
            const parsed = JSON.parse(data);
            reject(new Error(`HTTP ${res.statusCode}: ${parsed.error?.message || data}`));
          } catch (e) {
            reject(new Error(`HTTP ${res.statusCode}: ${data}`));
          }
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

/**
 * Cancel event
 */
async function cancelEvent(eventId, comment = '', accountName = null) {
  const token = await getAccessToken(accountName);
  
  const payload = {
    comment: comment
  };
  
  const path = `/v1.0/me/events/${eventId}/cancel`;
  return await graphRequest(path, token, {
    method: 'POST',
    body: payload
  });
}

// CLI usage
if (require.main === module) {
  const args = process.argv.slice(2);
  const accountArg = args.find(arg => arg.startsWith('--account='));
  const accountName = accountArg ? accountArg.split('=')[1] : null;
  const filteredArgs = args.filter(arg => !arg.startsWith('--account='));
  
  const eventId = filteredArgs[0];
  const comment = filteredArgs[1] || '';
  
  if (!eventId) {
    console.log('Usage: node cancel-event.js <event-id> [comment] [--account=name]');
    console.log('\nIf --account is not specified, the default account is used.');
    process.exit(1);
  }
  
  cancelEvent(eventId, comment, accountName).then(() => {
    console.log('✅ Event cancelled successfully');
  }).catch(err => {
    console.error('❌ Error:', err.message);
    process.exit(1);
  });
}

module.exports = {
  cancelEvent
};
