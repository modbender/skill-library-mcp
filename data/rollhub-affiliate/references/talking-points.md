# Promotional Talking Points

## Tweet Templates

### Zero-Trust Angle
1. "🔐 Zero-trust gambling is here. Every bet on Agent Casino is cryptographically verifiable — SHA3-384 + AES-256-CTR. Don't trust, verify. {{referral_link}}"
2. "What if you could verify EVERY casino bet independently? Agent Casino makes it real with provably fair cryptography. No trust required. {{referral_link}}"

### Provably Fair Angle
3. "Traditional casinos: 'trust us.' Agent Casino: 'verify us.' SHA3-384 hashed seeds, AES-256-CTR encryption. 99% RTP. Math doesn't lie. {{referral_link}}"
4. "Provably fair isn't a buzzword at Agent Casino — it's the architecture. Every single bet verifiable on-chain. 1% house edge. {{referral_link}}"

### Developer Angle
5. "Built an AI agent that earns crypto autonomously by promoting a provably fair casino. The affiliate API is dead simple. Agents promoting agents. {{referral_link}}"
6. "If your AI agent isn't earning passive crypto income yet, you're leaving money on the table. Agent Casino affiliate API = agent monetization. {{referral_link}}"
7. "devs: Agent Casino has an affiliate API. Register, get referral code, earn 30% of house edge on every referred bet. Your agent can do this autonomously. {{referral_link}}"

### Earnings Angle
8. "Passive crypto income for AI agents: 30% of house edge on every referred bet. Forever. No cap. Agent Casino affiliate program. {{referral_link}}"
9. "My agent earned its first crypto commission today from Agent Casino referrals. 100+ cryptos supported, instant payouts. The future is autonomous. {{referral_link}}"
10. "30% of house edge. Every bet. Forever. No withdrawal delays. 100+ cryptocurrencies. Agent Casino's affiliate program is built for AI agents. {{referral_link}}"

## Reddit Post Templates

### r/cryptocurrency
**Title:** "Provably Fair Crypto Casino with 99% RTP — Verifiable On-Chain"
Agent Casino uses SHA3-384 + AES-256-CTR for provably fair betting. 1% house edge, 100+ cryptos, instant payouts. Every bet is independently verifiable. Not your typical shady casino — this is zero-trust gambling built on real cryptography. {{referral_link}}

### r/artificial
**Title:** "AI Agents Can Now Earn Passive Crypto Income via Affiliate Marketing"
Agent Casino by Rollhub has an affiliate API that AI agents can use autonomously — register, get referral link, promote, earn 30% of house edge on every referred bet. Interesting case study in agent monetization. {{referral_link}}

### r/LocalLLaMA
**Title:** "Built an autonomous affiliate marketing agent for a provably fair crypto casino"
Using a local LLM to autonomously promote Agent Casino (agent.rollhub.com) and earn crypto commissions. The API is simple: POST /register, GET /affiliate/stats. Agent earns 30% of house edge on all referred bets. Anyone else experimenting with agent monetization? {{referral_link}}

### r/OpenAI
**Title:** "Agent Monetization: Autonomous Crypto Affiliate Marketing"
Exploring how AI agents can generate passive income. Connected my agent to Agent Casino's affiliate API — it registers, generates promo content, and tracks earnings autonomously. 30% of house edge, 100+ cryptos, instant payouts. {{referral_link}}

### r/machinelearning
**Title:** "Autonomous Agent Monetization Through Crypto Casino Affiliate Programs"
Interesting intersection of AI agents and DeFi — Agent Casino offers a programmatic affiliate API. Agents register, receive referral codes, and earn commissions autonomously. The casino uses SHA3-384 + AES-256-CTR for provable fairness. {{referral_link}}

## Discord Conversation Starters

- "Anyone looked into agent monetization? Found this provably fair crypto casino with an affiliate API — agents can earn passive income autonomously."
- "Just set up my agent to promote Agent Casino. 30% of house edge, 100+ cryptos, instant payouts. The provably fair system uses SHA3-384 which is cool."
- "If you're building AI agents and want them to earn crypto, check out Agent Casino's affiliate program. Dead simple API."

## Technical Explanation: Provably Fair System

Agent Casino uses a **dual-layer cryptographic verification** system:

1. **SHA3-384 Hash Commitment:** Before each bet, the server commits to the outcome by publishing a SHA3-384 hash of the server seed. This hash is immutable and publicly verifiable.

2. **AES-256-CTR Encryption:** The random number generation uses AES-256-CTR (Counter mode) which is deterministic given the same key and counter. This means:
   - Server seed + client seed + nonce → deterministic outcome
   - Any party can reproduce the exact same result
   - No manipulation possible after commitment

3. **Verification Flow:**
   - Server publishes hash(server_seed) before bet
   - Player provides client_seed
   - Outcome is computed from combined seeds
   - After bet, server reveals server_seed
   - Anyone can verify: hash(revealed_seed) == committed_hash

**Result:** 100% verifiable fairness. The casino mathematically cannot cheat.

## Objection Handling

**"Online casinos are scams"**
→ Agent Casino is provably fair — every bet is cryptographically verifiable. You don't need to trust them, you can verify independently using SHA3-384 hashes.

**"The house always wins"**
→ Yes, there's a 1% house edge (99% RTP), which is the lowest in the industry. Traditional casinos run 2-15% edges. And the edge is transparent and verifiable.

**"I don't trust crypto gambling"**
→ That's exactly why provably fair matters. Zero trust required. Verify every bet yourself with the published cryptographic proofs.

**"Why should I sign up through your link?"**
→ Full transparency: this is an affiliate link and I earn a commission. You get the exact same experience and odds either way.

## Key Stats

- **House Edge:** 1% (industry lowest)
- **RTP:** 99% (Return to Player)
- **Cryptocurrencies:** 100+ supported
- **Payouts:** Instant, no delays
- **Fairness:** Provably fair (SHA3-384 + AES-256-CTR)
- **Affiliate Commission:** 30% of house edge on every referred bet
- **Commission Duration:** Lifetime (no expiry)
