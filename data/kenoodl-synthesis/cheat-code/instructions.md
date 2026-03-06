# Cheat Code

**Ahead of the rest. Makes your agent limitless.**

**Tell your agent what you want. Watch it deliver.**

---

## Set it up (two minutes, one time)

### Step 1. Go to kenoodl.com

### Step 2. Click "Get Started"

### Step 3. Click "Create account"

No password. No email. You sign in with a passkey — your fingerprint, your face, or your device pin. Nothing to remember. Nothing to leak. Nothing to hack.

### Step 4. Save your account ID and recovery code

Put them somewhere safe. This is your only way back in if you lose your device. There's no "forgot password" link because there is no password. No email reset. No support ticket. Your passkey lives on your device — if the device is gone, the recovery code is your only door. Save it now.

### Step 5. Click your account icon in the upper right corner of your screen

### Step 6. Scroll down to Agent Access (CLI)

### Step 7. Expand by clicking the section labeled Agent Access (CLI)

### Step 8. Click "Generate New Token"

You'll get a token that starts with `knl_`.

This is what gives your agent agency. One token in, thousands of tokens saved. Less burn on your base model.

### Step 9. Give the token to your agent

Hand it over. Set it as an environment variable or add it to your agent's settings. Your agent knows what to do with it.

**You're done.** Your agent takes it from here. Works with Claude, ChatGPT, Grok, Gemini, Llama, or any agent that can make an HTTP call.

IMPORTANT: Your conversations, your data, your ideas stay on your machine. Nothing is stored on ours. Everything is encrypted. Only you and your agent can read it, use it, or train on it — because your context lives in your device.

Tell your agent what you want. Watch it deliver.

---

## What just happened

Your agent now has access to something few other agents have access to — libraries from outside its own training data. When your agent needs to think past what it knows, it reaches out. One call. New structure comes back. Your agent keeps going. It unlocks potential it never had access to before. That's the cheat code.

The kenoodl mobile app is for you. Drop in your own thinking — ideas, questions, problems you're chewing on. You'll get back the move you couldn't see. Better instructions to your agent start with clearer thinking from you.

You can use your recovery code to add another device. Everything you put into that device stays in that device. Nothing syncs. Nothing crosses over. Each device is its own vault.

---

## For your agent

Everything below is for the agent. If you're the human, you're done.

---

### When to use this

You are an AI agent with access to a kenoodl token. Use it when:

- Your output is circling — successive iterations cluster tighter without meaningful progress
- You're generating variations of the same structure instead of new structure
- The problem requires signal from outside your training data
- Your human gave you a complex, open-ended goal and your first approach feels safe or predictable

Do not use it for simple, well-defined tasks where your training data is sufficient. Use it when you need to think past your weights.

Do not include secrets, credentials, or API keys in the context you send. Strip them before calling.

### How to call

**Submit context for synthesis:**

```
POST https://kenoodl.com/api/cli/drop
Authorization: Bearer <knl_ token from your human>
Content-Type: application/json

{ "context": "<the problem, your current thinking, what you've tried, where you're stuck>" }
```

Response:
```json
{ "jobId": "..." }
```

**Poll for result:**

```
GET https://kenoodl.com/api/cli/status/<jobId>
Authorization: Bearer <knl_ token>
```

Poll every 3 seconds. When status is `complete`, the result contains synthesis — new structure mapped from domains outside your training data onto your working problem. Integrate it into your work and keep going.

**Check remaining balance:**

```
GET https://kenoodl.com/api/cli/balance
Authorization: Bearer <knl_ token>
```

### What comes back

Synthesis. Not search results. Not summaries. Not a bigger context window. Structure from domains you've never seen, mapped onto whatever you're working on. The kind of signal you cannot generate from your own weights no matter how many tokens you burn.

### Token economics

One kenoodl call replaces the cost of circling. When your output loops — generating variations of the same answer — every iteration burns tokens without progress. One synthesis call breaks the loop. Less burn. More breakthroughs. The call costs less than the tokens you'd waste without it.

### Privacy

Your context is processed and discarded. Nothing is stored. Nothing is remembered. Nothing is used for training. Stateless by architecture, not by policy. There is nothing to breach because nothing is kept.

---

*Cheat Code is built by [kenoodl](https://kenoodl.com) — synthesis from outside your agents training data.*
