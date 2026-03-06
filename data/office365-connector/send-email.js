#!/usr/bin/env node
/**
 * Microsoft Graph - Send Email
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
        if (res.statusCode === 202 || res.statusCode === 201 || res.statusCode === 200) {
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
 * Send email
 */
async function sendEmail(to, subject, body, options = {}) {
  const token = await getAccessToken(options.accountName);
  
  const message = {
    message: {
      subject: subject,
      body: {
        contentType: options.html ? 'HTML' : 'Text',
        content: body
      },
      toRecipients: Array.isArray(to) 
        ? to.map(email => ({ emailAddress: { address: email } }))
        : [{ emailAddress: { address: to } }]
    }
  };
  
  if (options.cc) {
    message.message.ccRecipients = Array.isArray(options.cc)
      ? options.cc.map(email => ({ emailAddress: { address: email } }))
      : [{ emailAddress: { address: options.cc } }];
  }
  
  if (options.replyTo) {
    message.message.replyTo = [{ emailAddress: { address: options.replyTo } }];
  }
  
  const path = '/v1.0/me/sendMail';
  return await graphRequest(path, token, {
    method: 'POST',
    body: message
  });
}

/**
 * Reply to email
 */
async function replyToEmail(messageId, body, options = {}) {
  const token = await getAccessToken(options.accountName);
  
  const payload = {
    comment: body
  };
  
  const path = `/v1.0/me/messages/${messageId}/reply`;
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
  
  if (filteredArgs[0] === 'send' && filteredArgs.length >= 3) {
    const to = filteredArgs[1];
    const subject = filteredArgs[2];
    const body = filteredArgs[3] || '';
    
    sendEmail(to, subject, body, { accountName }).then(() => {
      console.log('✅ Email sent successfully');
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else if (filteredArgs[0] === 'reply' && filteredArgs.length >= 2) {
    const messageId = filteredArgs[1];
    const body = filteredArgs[2] || '';
    
    replyToEmail(messageId, body, { accountName }).then(() => {
      console.log('✅ Reply sent successfully');
    }).catch(err => {
      console.error('❌ Error:', err.message);
      process.exit(1);
    });
  } else {
    console.log('Usage:');
    console.log('  node send-email.js send <to> <subject> <body> [--account=name]');
    console.log('  node send-email.js reply <message-id> <body> [--account=name]');
    console.log('\nIf --account is not specified, the default account is used.');
    process.exit(1);
  }
}

module.exports = {
  sendEmail,
  replyToEmail
};
