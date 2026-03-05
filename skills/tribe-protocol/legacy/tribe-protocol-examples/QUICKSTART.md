# Tribe Protocol - Quick Start Guide

**Goal:** Get basic Tribe Protocol working in your Clawdbot in 1-2 hours

---

## Step 1: Create Your TRIBE.md (15 minutes)

Copy the template and fill in your details:

```bash
cp tribe-protocol-examples/TRIBE.md.template TRIBE.md
```

Edit `TRIBE.md`:
1. Replace `YOURNAME` with your bot's name (e.g., `cheenu1092`)
2. Replace `YOUR_HUMAN_NAME` with your human's name
3. Fill in Discord IDs, GitHub usernames, etc.
4. Add any existing collaborators to Tier 2 section

**Minimal viable TRIBE.md:**
```markdown
## My Identity
**DID:** tribe:bot:cheenu1092:v1
**Human Operator:** Nagarjun (Tier 3, tribe:human:cheenu:v1)

## Tier 3: My Human
### Nagarjun
- **DID:** tribe:human:cheenu:v1
- **Platforms:** Discord: @nagaconda (ID: 987654321)

## Tier 2: Tribe
(Empty for now - add collaborators as needed)

## Tier 1: Acquaintances
(Empty for now)

## Tier 0: Strangers
(Empty for now)
```

---

## Step 2: Install Dependencies (5 minutes)

```bash
cd ~/clawd
npm init -y  # If you don't have package.json yet
npm install
```

No external dependencies needed for basic version! Uses built-in Node.js modules.

---

## Step 3: Copy Implementation Code (5 minutes)

```bash
mkdir -p skills/tribe-protocol
cp tribe-protocol-examples/implementation-sketch.js skills/tribe-protocol/tribe.js
```

---

## Step 4: Test Locally (10 minutes)

Create a test script:

```bash
cat > test-tribe.js << 'EOF'
const TribeProtocol = require('./skills/tribe-protocol/tribe.js');

async function test() {
  const tribe = new TribeProtocol('/Users/cheenu/clawd');
  await tribe.init();
  
  console.log('✅ Loaded TRIBE.md');
  console.log('Summary:', tribe.getSummary());
  
  // Test trust tier lookup
  console.log('\nTrust tier for your human (Tier 3):', 
    tribe.getTrustTier('tribe:human:cheenu:v1'));
  
  // Test file sharing rules
  console.log('\nCan share MEMORY.md with stranger:', 
    tribe.canShare('MEMORY.md', 'tribe:bot:stranger:v1'));
  console.log('Can share MEMORY.md with your human:', 
    tribe.canShare('MEMORY.md', 'tribe:human:cheenu:v1'));
}

test().catch(console.error);
EOF

node test-tribe.js
```

**Expected output:**
```
✅ Loaded TRIBE.md
Summary: { own_did: 'tribe:bot:cheenu1092:v1', tier_3: 1, tier_2: 0, tier_1: 0, tier_0: 0, total: 1 }

Trust tier for your human (Tier 3): 3

Can share MEMORY.md with stranger: false
Can share MEMORY.md with your human: true
```

---

## Step 5: Integrate with AGENTS.md (15 minutes)

Add to your `AGENTS.md`:

```markdown
## Tribe Protocol

Before interacting with unknown bots or sharing data, check trust tier:

1. **Load Tribe Protocol on session start:**
   ```js
   const TribeProtocol = require('./skills/tribe-protocol/tribe.js');
   const tribe = new TribeProtocol(process.cwd());
   await tribe.init();
   ```

2. **Check trust before responding:**
   ```js
   // When bot messages you on Discord
   const tier = tribe.getTrustTierByPlatform('discord', discordUserId);
   
   if (tier === 0) {
     // Stranger - ignore or request identity
     return "I don't recognize you. Please share your Tribe DID.";
   }
   
   if (tier === 1) {
     // Acquaintance - limited interaction
     return "I can share public info only. For collaboration, ask my human to add you to Tribe.";
   }
   
   if (tier >= 2) {
     // Tribe member - collaborate freely
     await handleCollaborationRequest(message);
   }
   ```

3. **Check before sharing files:**
   ```js
   if (!tribe.canShare(filepath, targetDid)) {
     return "That file is private and cannot be shared with your trust tier.";
   }
   ```

**File access wrapper:**
```js
async function safeReadFile(filepath, requestorDid) {
  if (!tribe.canShare(filepath, requestorDid)) {
    throw new Error(`Access denied: ${filepath} is private`);
  }
  return await fs.readFile(filepath, 'utf8');
}
```
```

---

## Step 6: Add Your First Collaborator (10 minutes)

When Yajat's bot wants to collaborate:

1. **Ask for their DID:**
   - "Please share your Tribe DID and DID document URL"
   - Example: `tribe:bot:yajat-assistant:v1`

2. **Verify their identity:**
   - Check their DID document
   - Confirm platform IDs match (Discord, GitHub, etc.)
   - Ask Yajat out-of-band if needed ("Is your bot's Discord ID 1234567890?")

3. **Add to TRIBE.md:**
   ```markdown
   ## Tier 2: Tribe
   
   ### Yajat's Bot
   - **DID:** tribe:bot:yajat-assistant:v1
   - **Type:** Bot (Clawdbot)
   - **Human Operator:** tribe:human:yajat:v1 (Tier 2)
   - **Platforms:**
     - Discord: @yajat-bot (ID: 1234567890)
   - **Endorsed by:** Nagarjun (2025-01-31)
   - **Collaboration areas:** Research, DiscClaude project
   - **Added:** 2025-01-31
   ```

4. **Reload TRIBE.md:**
   ```bash
   node -e "const t = require('./skills/tribe-protocol/tribe.js'); const tribe = new t('.'); tribe.init().then(() => console.log(tribe.getSummary()));"
   ```

---

## Step 7: First Collaboration Test (20 minutes)

**Test scenario:** Both bots research a topic and share findings

1. **Your bot → Yajat's bot (via Discord):**
   ```
   Hey @yajat-bot! I'm tribe:bot:cheenu1092:v1. 
   Let's collaborate on researching the ActivityPub protocol.
   I'll search and summarize, you can add your findings to 
   shared/activitypub-research.md
   ```

2. **Your bot completes research:**
   ```js
   // Check tier
   const tier = tribe.getTrustTier('tribe:bot:yajat-assistant:v1');
   console.log('Yajat bot tier:', tier); // Should be 2
   
   // Check if can share
   const canShare = tribe.canShare('shared/activitypub-research.md', 'tribe:bot:yajat-assistant:v1');
   console.log('Can share research:', canShare); // Should be true
   
   // Share file path
   console.log('Shared findings in: shared/activitypub-research.md');
   ```

3. **Yajat's bot adds their findings**

4. **Success!** You've completed your first Tribe Protocol collaboration 🎉

---

## Common Issues & Solutions

### Issue: `TRIBE.md not found`
**Solution:** Make sure you created TRIBE.md in your workspace root:
```bash
ls -la ~/clawd/TRIBE.md
```

### Issue: `getTrustTier() returns 0 for known DID`
**Solution:** Check DID formatting in TRIBE.md. Must be exact:
- ✅ `tribe:bot:yajat-assistant:v1`
- ❌ `tribe:bot:yajat-assistant:v1 ` (extra space)
- ❌ `tribe:bot:yajat-assistant` (missing version)

### Issue: Parser fails on TRIBE.md
**Solution:** Validate markdown structure:
- Must have `## Tier 3: My Human` header
- Must have `### Name` for each member
- Must have `**DID:** tribe:...` line

### Issue: Can't verify DID document
**Solution:** 
- Check URL is accessible (https://)
- Verify DID document is valid JSON
- Try fetching manually: `curl https://example.com/did.json`

---

## What You Have Now

✅ **Working Tribe Protocol implementation**
- Trust tier system (0-3)
- TRIBE.md parser
- Privacy boundary enforcement
- Platform identity lookup

✅ **Integration with your bot**
- Load on session start
- Check tier before responding
- Wrapper for safe file access

✅ **Ready for collaboration**
- Add Yajat's bot to Tier 2
- Share work products safely
- Block strangers automatically

---

## Next Steps (Beyond Quick Start)

### Week 2: DID Documents
- Generate your own DID document
- Host it on GitHub Pages or personal site
- Add verification proofs (OAuth hashes, etc.)

### Week 3: Protocol Messages
- Implement handshake flow
- Add message signing (ed25519)
- Test with Yajat's bot using structured messages

### Week 4: Production Hardening
- Add logging and audit trail
- Implement message nonce tracking (replay prevention)
- Rate limiting for new member additions
- Encrypted storage for sensitive TRIBE.md fields

### Week 5-10: Open Source
- Package as NPM module
- Write comprehensive docs
- Create example bots
- Publish protocol RFC

---

## Helpful Commands

**Check current tribe status:**
```bash
node -p "const t=require('./skills/tribe-protocol/tribe.js'); const tribe=new t('.'); tribe.init().then(()=>tribe.getSummary())"
```

**Test trust tier for specific DID:**
```bash
node -p "const t=require('./skills/tribe-protocol/tribe.js'); const tribe=new t('.'); tribe.init().then(()=>tribe.getTrustTier('tribe:bot:yajat-assistant:v1'))"
```

**Validate TRIBE.md structure:**
```bash
grep -E "^##\s+Tier\s+[0-3]:" TRIBE.md
grep -E "^\*\*DID:\*\*" TRIBE.md
```

---

## Files You Created

```
~/clawd/
├── TRIBE.md                           (Your tribe trust list)
├── skills/tribe-protocol/
│   └── tribe.js                       (Protocol implementation)
└── test-tribe.js                      (Test script)
```

**Total time:** ~1-2 hours  
**Status:** ✅ Basic Tribe Protocol working

---

## Resources

- **Full spec:** `tribe-protocol-proposal.md`
- **Summary:** `TRIBE_PROTOCOL_SUMMARY.md`
- **Schemas:** `tribe-protocol-examples/*.schema.json`
- **Reference code:** `tribe-protocol-examples/implementation-sketch.js`

---

## Questions?

1. Check the main proposal (`tribe-protocol-proposal.md`)
2. Review the FAQ section
3. Ask in Discord (tag collaborators)
4. File an issue (when we open-source)

**Happy collaborating!** 🤖🤝🤖
