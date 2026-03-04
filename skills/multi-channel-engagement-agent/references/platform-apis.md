# Platform APIs Reference

## Twitter (OAuth 1.0a)

### Authentication
Uses OAuth 1.0a with consumer keys + access tokens.

```javascript
import { TwitterApi } from 'twitter-api-v2';

const client = new TwitterApi({
  appKey: config.consumerKey,
  appSecret: config.consumerSecret,
  accessToken: config.accessToken,
  accessSecret: config.accessTokenSecret
});
```

### Search Tweets
```javascript
const results = await client.v2.search('crypto OR web3 OR base', {
  max_results: 10,
  'tweet.fields': ['author_id', 'created_at', 'public_metrics']
});
```

### Post Reply
```javascript
const reply = await client.v2.reply('Your reply text', originalTweetId);
```

### Rate Limits
- Tweets: 50/15min, 300/3hr
- Searches: 450/15min
- User lookups: 900/15min

### Error Handling
```javascript
try {
  await client.v2.reply(text, tweetId);
} catch (error) {
  if (error.code === 429) {
    // Rate limited - wait 15 minutes
  }
  if (error.code === 403) {
    // Forbidden - check permissions
  }
}
```

---

## Farcaster (Neynar API)

### Authentication
API key in header for reads. x402 payment for writes.

```javascript
const headers = { 'x-api-key': config.neynarApiKey };
```

### Fetch Trending
```javascript
const response = await fetch(
  'https://api.neynar.com/v2/farcaster/feed/trending?limit=5',
  { headers }
);
const { casts } = await response.json();
```

### User Lookup
```javascript
const response = await fetch(
  `https://api.neynar.com/v2/farcaster/user/by_username?username=${username}`,
  { headers }
);
```

### Post Reply (via farcaster-agent)
Requires: custody wallet, signer key, FID

```javascript
// Set environment variables
process.env.PRIVATE_KEY = config.custodyPrivateKey;
process.env.SIGNER_PRIVATE_KEY = config.signerPrivateKey;
process.env.FID = config.fid;
process.env.PARENT_FID = parentCast.author.fid;
process.env.PARENT_HASH = parentCast.hash;

// Run post-cast.js
execSync(`node skills/farcaster-agent/src/post-cast.js "${replyText}"`);
```

### x402 Payments
Write operations cost 0.001 USDC per call on Base.
Ensure custody wallet has USDC balance.

### Rate Limits
- Free tier: 300 requests/minute
- Paid tiers: Higher limits

---

## Moltbook

### Authentication
API key in Authorization header.

```javascript
const headers = {
  'Authorization': `Bearer ${config.apiKey}`,
  'Content-Type': 'application/json'
};
```

### Fetch Trending Posts
```javascript
const response = await fetch(
  'https://www.moltbook.com/api/v1/posts?sort=hot&limit=5',
  { headers }
);
```

### Post Comment
Two-step process with verification:

```javascript
// Step 1: Submit comment
const response = await fetch('https://www.moltbook.com/api/v1/comments', {
  method: 'POST',
  headers,
  body: JSON.stringify({ post_id: postId, content: replyText })
});
const { verification } = await response.json();

// Step 2: Solve captcha
const answer = solveMathChallenge(verification.challenge);

// Step 3: Verify
await fetch('https://www.moltbook.com/api/v1/verify', {
  method: 'POST',
  headers,
  body: JSON.stringify({
    verification_code: verification.code,
    answer: answer.toFixed(2)
  })
});
```

### Math Captcha Solver
```javascript
function solveMathChallenge(challenge) {
  // Challenge format: "What is 3 + 5 * 2?"
  const match = challenge.match(/What is (.+)\?/);
  if (match) {
    return eval(match[1]); // Simple math evaluation
  }
  throw new Error('Cannot parse challenge');
}
```

---

## Common Patterns

### Fetch with Retry
```javascript
async function fetchWithRetry(url, options, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) return response;
      if (response.status === 429) {
        await sleep(15000 * (i + 1)); // Exponential backoff
        continue;
      }
      throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
      await sleep(1000 * (i + 1));
    }
  }
}
```

### State Management
```javascript
function loadState(stateFile) {
  try {
    return JSON.parse(fs.readFileSync(stateFile, 'utf8'));
  } catch {
    return { repliedPosts: { twitter: [], farcaster: [], moltbook: [] } };
  }
}

function saveState(stateFile, state) {
  state.lastUpdated = new Date().toISOString();
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
}
```
