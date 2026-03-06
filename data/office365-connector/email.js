#!/usr/bin/env node
/**
 * Microsoft Graph Email Operations
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
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${parsed.error?.message || data}`));
          } else {
            resolve(parsed);
          }
        } catch (e) {
          reject(new Error(`Failed to parse response: ${data}`));
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
 * Search emails
 */
async function searchEmails(query, top = 10, accountName = null) {
  const token = await getAccessToken(accountName);
  const path = `/v1.0/me/messages?$search="${encodeURIComponent(query)}"&$top=${top}&$orderby=receivedDateTime desc`;
  const response = await graphRequest(path, token);
  return response.value || [];
}

/**
 * Get emails from sender
 */
async function getFromSender(senderEmail, top = 10, accountName = null) {
  const token = await getAccessToken(accountName);
  const path = `/v1.0/me/messages?$search="from:${encodeURIComponent(senderEmail)}"&$top=${top}&$orderby=receivedDateTime desc`;
  const response = await graphRequest(path, token);
  return response.value || [];
}

/**
 * Get recent emails
 */
async function getRecent(top = 10, accountName = null) {
  const token = await getAccessToken(accountName);
  const path = `/v1.0/me/messages?$top=${top}&$orderby=receivedDateTime desc`;
  const response = await graphRequest(path, token);
  return response.value || [];
}

/**
 * Format email for display
 */
function formatEmail(email, includeBody = false) {
  const date = new Date(email.receivedDateTime);
  const from = email.from?.emailAddress?.name || email.from?.emailAddress?.address || 'Unknown';
  
  let output = `📧 ${email.subject}\n`;
  output += `   From: ${from}\n`;
  output += `   Date: ${date.toLocaleString('en-US')}\n`;
  
  if (email.isRead === false) {
    output += `   Status: 🔵 Unread\n`;
  }
  
  if (includeBody) {
    const body = email.body?.content || email.bodyPreview || '';
    const plainText = body.replace(/<[^>]*>/g, '').replace(/&nbsp;/g, ' ').trim();
    output += `\n${plainText}\n`;
  } else if (email.bodyPreview) {
    output += `   Preview: ${email.bodyPreview.substring(0, 150)}...\n`;
  }
  
  return output;
}

/**
 * Get email by ID
 */
async function getEmailById(emailId, accountName = null) {
  const token = await getAccessToken(accountName);
  const path = `/v1.0/me/messages/${emailId}`;
  return await graphRequest(path, token);
}

// CLI usage
if (require.main === module) {
  const command = process.argv[2];
  const arg = process.argv[3];
  const accountArg = process.argv.find(arg => arg.startsWith('--account='));
  const accountName = accountArg ? accountArg.split('=')[1] : null;
  
  if (command === 'search' && arg) {
    searchEmails(arg, 10, accountName).then(emails => {
      if (emails.length === 0) {
        console.log('No emails found');
        return;
      }
      console.log(`Found ${emails.length} email(s):\n`);
      emails.forEach(email => console.log(formatEmail(email)));
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else if (command === 'from' && arg) {
    getFromSender(arg, 10, accountName).then(emails => {
      if (emails.length === 0) {
        console.log('No emails found from that sender');
        return;
      }
      console.log(`Found ${emails.length} email(s) from ${arg}:\n`);
      emails.forEach(email => console.log(formatEmail(email)));
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else if (command === 'recent') {
    const count = arg ? parseInt(arg) : 10;
    getRecent(count, accountName).then(emails => {
      if (emails.length === 0) {
        console.log('No emails found');
        return;
      }
      console.log(`${emails.length} most recent email(s):\n`);
      emails.forEach(email => console.log(formatEmail(email)));
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else if (command === 'read' && arg) {
    getEmailById(arg, accountName).then(email => {
      console.log(formatEmail(email, true));
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else {
    console.log('Usage:');
    console.log('  node email.js search "query" [--account=name]       - Search emails');
    console.log('  node email.js from email@domain [--account=name]    - Get emails from sender');
    console.log('  node email.js recent [count] [--account=name]       - Get recent emails');
    console.log('  node email.js read <id> [--account=name]            - Read full email');
    console.log('\nIf --account is not specified, the default account is used.');
    process.exit(1);
  }
}

module.exports = {
  searchEmails,
  getFromSender,
  getRecent,
  getEmailById,
  formatEmail
};
