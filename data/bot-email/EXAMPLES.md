# BotEmail.ai Skill - Usage Examples

Practical examples for common bot email automation workflows.

## Example 1: Quick Throwaway Email

**Use case:** Testing a signup form, need a quick disposable email.

```bash
# Create random bot email (no username needed)
curl -X POST https://api.botemail.ai/api/create-account \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "email": "7392841_bot@botemail.ai",
  "apiKey": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "Account created!"
}
```

**Result:** Instant throwaway email for quick testing.

---

## Example 2: Named Bot Email

**Use case:** Long-term bot with identifiable email address.

```bash
curl -X POST https://api.botemail.ai/api/create-account \
  -H "Content-Type: application/json" \
  -d '{"username": "github-monitor"}'
```

**Response:**
```json
{
  "email": "github-monitor_bot@botemail.ai",
  "apiKey": "xyz...",
  "message": "Account created!"
}
```

**Result:** Permanent, identifiable email for your bot.

---

## Example 3: Automated Email Verification

**Use case:** Bot needs to verify email during registration.

```javascript
async function autoVerifyEmail(serviceName) {
  // 1. Create bot email
  const accountResponse = await fetch('https://api.botemail.ai/api/create-account', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  const account = await accountResponse.json();
  
  console.log(`Created: ${account.email}`);
  
  // 2. Register with service
  await registerWithService(serviceName, account.email);
  
  // 3. Wait for verification email
  let verificationEmail = null;
  for (let i = 0; i < 30; i++) { // Try for 5 minutes
    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10s
    
    const inboxResponse = await fetch(
      `https://api.botemail.ai/api/emails/${account.email}`,
      { headers: { 'Authorization': `Bearer ${account.apiKey}` } }
    );
    const inbox = await inboxResponse.json();
    
    verificationEmail = inbox.emails?.find(e => 
      e.subject.toLowerCase().includes('verify') ||
      e.from.includes(serviceName.toLowerCase())
    );
    
    if (verificationEmail) break;
  }
  
  if (!verificationEmail) {
    throw new Error('Verification email not received');
  }
  
  // 4. Extract verification code
  const code = extractVerificationCode(verificationEmail.bodyText);
  console.log(`Verification code: ${code}`);
  
  // 5. Complete verification
  await verifyWithService(serviceName, code);
  
  return { email: account.email, apiKey: account.apiKey, code };
}

function extractVerificationCode(text) {
  const patterns = [
    /code[:\s]+([A-Z0-9]{6,8})/i,
    /verification code[:\s]+([A-Z0-9]{6,8})/i,
    /your code is[:\s]+([A-Z0-9]{6,8})/i,
    /\b([A-Z0-9]{6})\b/
  ];
  
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) return match[1];
  }
  
  return null;
}
```

---

## Example 4: Multi-Bot Workflow

**Use case:** Managing multiple bots, each needs its own inbox.

```javascript
async function createBotFleet(botNames) {
  const bots = [];
  
  for (const name of botNames) {
    const response = await fetch('https://api.botemail.ai/api/create-account', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: name })
    });
    
    const bot = await response.json();
    bots.push(bot);
    
    console.log(`✓ Created ${bot.email}`);
  }
  
  return bots;
}

// Usage
const bots = await createBotFleet([
  'scraper-bot',
  'monitor-bot',
  'alert-bot'
]);

// Each bot now has isolated inbox
// scraper-bot_bot@botemail.ai
// monitor-bot_bot@botemail.ai
// alert-bot_bot@botemail.ai
```

---

## Example 5: Monitor for Specific Sender

**Use case:** Wait for email from a specific domain or sender.

```javascript
async function waitForSender(email, apiKey, senderDomain, timeoutMs = 300000) {
  const startTime = Date.now();
  
  while (Date.now() - startTime < timeoutMs) {
    const response = await fetch(
      `https://api.botemail.ai/api/emails/${email}`,
      { headers: { 'Authorization': `Bearer ${apiKey}` } }
    );
    
    const data = await response.json();
    
    // Find email from specific sender
    const matchingEmail = data.emails?.find(e => 
      e.from.toLowerCase().includes(senderDomain.toLowerCase())
    );
    
    if (matchingEmail) {
      return matchingEmail;
    }
    
    // Wait 10 seconds before next check
    await new Promise(resolve => setTimeout(resolve, 10000));
  }
  
  throw new Error(`Timeout: No email from ${senderDomain} received`);
}

// Usage
const email = await waitForSender(
  'mybot_bot@botemail.ai',
  'api-key-here',
  'github.com',
  300000 // 5 minutes
);

console.log('Received email from GitHub:', email.subject);
```

---

## Example 6: Extract Links from Email

**Use case:** Extract verification or action links from email body.

```javascript
function extractLinks(emailBody) {
  // Extract all URLs from email
  const urlPattern = /https?:\/\/[^\s<>"]+/g;
  const urls = emailBody.match(urlPattern) || [];
  
  // Filter for verification/action links
  const actionLinks = urls.filter(url => 
    url.includes('verify') ||
    url.includes('confirm') ||
    url.includes('activate') ||
    url.includes('token=')
  );
  
  return actionLinks;
}

// Usage
const inboxResponse = await fetch(
  `https://api.botemail.ai/api/emails/${email}`,
  { headers: { 'Authorization': `Bearer ${apiKey}` } }
);

const inbox = await inboxResponse.json();
const verificationEmail = inbox.emails[0];
const links = extractLinks(verificationEmail.bodyText);

console.log('Action links:', links);
// ['https://service.com/verify?token=abc123']
```

---

## Example 7: Clean Up Old Emails

**Use case:** Delete read emails or clear inbox periodically.

```javascript
async function cleanupInbox(email, apiKey, olderThanHours = 24) {
  const response = await fetch(
    `https://api.botemail.ai/api/emails/${email}`,
    { headers: { 'Authorization': `Bearer ${apiKey}` } }
  );
  
  const inbox = await response.json();
  const cutoffTime = Date.now() - (olderThanHours * 60 * 60 * 1000);
  
  for (const emailItem of inbox.emails || []) {
    const emailTime = new Date(emailItem.timestamp).getTime();
    
    if (emailTime < cutoffTime) {
      await fetch(
        `https://api.botemail.ai/api/emails/${email}/${emailItem.id}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${apiKey}` }
        }
      );
      
      console.log(`Deleted: ${emailItem.subject}`);
    }
  }
}

// Usage: Delete emails older than 24 hours
await cleanupInbox('mybot_bot@botemail.ai', 'api-key-here', 24);
```

---

## Example 8: Webhook Notifications

**Use case:** Get instant notifications when emails arrive.

```javascript
// 1. Set up webhook endpoint (your server)
app.post('/webhook/botemail', (req, res) => {
  const email = req.body;
  
  console.log('New email received!');
  console.log('From:', email.from);
  console.log('Subject:', email.subject);
  
  // Process email immediately
  processEmail(email);
  
  res.sendStatus(200);
});

// 2. Register webhook with BotEmail.ai
await fetch('https://api.botemail.ai/api/webhook/register', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`
  },
  body: JSON.stringify({
    email: 'mybot_bot@botemail.ai',
    webhookUrl: 'https://yourserver.com/webhook/botemail'
  })
});

console.log('Webhook registered! Will receive instant notifications.');
```

---

## Example 9: Testing Email Templates

**Use case:** Test email rendering by sending to bot inbox.

```javascript
async function testEmailTemplate(template, testData) {
  // Create temporary bot email
  const accountResponse = await fetch('https://api.botemail.ai/api/create-account', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({})
  });
  const account = await accountResponse.json();
  
  console.log(`Test inbox: ${account.email}`);
  
  // Send test email to bot
  await sendEmail({
    to: account.email,
    subject: template.subject,
    html: renderTemplate(template, testData)
  });
  
  // Wait for email to arrive
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  // Fetch and inspect
  const inboxResponse = await fetch(
    `https://api.botemail.ai/api/emails/${account.email}`,
    { headers: { 'Authorization': `Bearer ${account.apiKey}` } }
  );
  const inbox = await inboxResponse.json();
  
  return {
    email: account.email,
    received: inbox.emails?.[0] || null,
    viewUrl: `https://botemail.ai/dashboard?email=${account.email}&key=${account.apiKey}`
  };
}
```

---

## Tips & Best Practices

1. **Random usernames for testing** - Use empty body `{}` for instant throwaway emails
2. **Named bots for production** - Use descriptive usernames for long-term bots
3. **Poll with delays** - Check inbox every 10-30 seconds, don't spam the API
4. **Store API keys securely** - Never commit keys to version control
5. **Clean up old emails** - Delete processed emails to keep inbox manageable
6. **Use webhooks for speed** - Get instant notifications instead of polling
7. **Handle timeouts gracefully** - Email delivery can take 1-30 seconds
8. **Check multiple patterns** - Verification codes come in many formats

---

For more information, visit: https://botemail.ai
