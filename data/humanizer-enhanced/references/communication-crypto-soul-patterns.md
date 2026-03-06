# Communication, crypto/Web3, and soul patterns (18-34)

## Communication patterns (18-22)

### 18. Chatbot artifacts — HIGH

**Words to watch:** I hope this helps, Certainly!, Of course!, Let me know if, Here is a, Would you like me to

**Before:**
> Here is an overview of the AI agent market. I hope this helps! Let me know if you'd like me to expand on any section.

**After:**
> [Just delete these. Start with the actual content.]

---

### 19. Knowledge cutoff disclaimers — HIGH

**Before:**
> As of my last update, the protocol has processed over $1B in volume. While specific details are limited...

**After:**
> The protocol processed $1.2B in volume through Q4 2025, according to DeFiLlama.

---

### 20. Sycophantic tone — MEDIUM

**Before:**
> Great question! You're absolutely right that this is complex. That's an excellent point about the trade-offs.

**After:**
> [Delete entirely. Just make your point.]

---

### 21. Excessive hedging — MEDIUM

**Before:**
> It could potentially be argued that the approach might possibly have some effect on outcomes.

**After:**
> The approach probably works, though we won't know for sure until Q3.

---

### 22. Filler phrases — MEDIUM

| Filler | Fix |
|--------|-----|
| "In order to" | "To" |
| "Due to the fact that" | "Because" |
| "At this point in time" | "Now" |
| "It is important to note that" | [Delete] |
| "It's worth noting that" | [Delete] |
| "In the event that" | "If" |
| "Has the ability to" | "Can" |
| "serves as" / "stands as" | "is" |
| "Furthermore," / "Moreover," | "Also," or [Delete] |
| "crucial" / "vital" / "pivotal" | "important" or "key" or [Delete] |
| "revolutionizing" / "game-changing" | [Describe what it actually does] |
| "seamless" / "frictionless" | [Describe the actual UX] |
| "landscape" (abstract) | [Be specific about what] |
| "delve" | "look at" / "examine" |
| "Additionally" | [Delete or start sentence differently] |
| "In this article, we'll explore" | [Delete — start with content] |
| "Let's dive in" / "Let's take a look" | [Delete] |
| "First,... Second,... Third,..." | Vary: "The bigger issue...", "Beyond that...", "Meanwhile..." |
| "It bears mentioning" / "Notably," | [Delete or state fact directly] |

---

## Crypto/Web3 specific patterns (23-28)

### 23. Crypto hype language — HIGH

**Words to watch:** revolutionizing, disrupting, game-changing, paradigm shift, unprecedented, moon, WAGMI, LFG (in serious content)

**Before:**
> This revolutionary protocol is disrupting the entire DeFi paradigm with unprecedented innovation.

**After:**
> The protocol automates yield farming across multiple chains. APYs range from 5-15% depending on risk level.

---

### 24. Vague "ecosystem" claims — MEDIUM

**Before:**
> The vibrant ecosystem continues to grow with exciting partnerships and groundbreaking integrations.

**After:**
> 47 protocols integrated in 2025. The biggest: Aave, Compound, and Uniswap.

---

### 25. Unsubstantiated stats — HIGH

**Before:**
> With over $10B TVL and millions of users...

**After:**
> TVL reached $10.2B in December 2025 (source: DeFiLlama). Monthly active wallets: 340,000.

**Rule:** Every stat needs a source and date.

---

### 26. "Seamless" and "frictionless" — MEDIUM

**Before:**
> Users enjoy a seamless, frictionless experience with intuitive onboarding.

**After:**
> Onboarding takes about 3 minutes. You connect a wallet, approve the contract, and deposit.

---

### 27. Abstract "empowerment" language — MEDIUM

**Before:**
> The protocol empowers users to take control of their financial future, unlocking new possibilities.

**After:**
> Users can earn yield on idle assets without trusting a centralized exchange.

---

### 28. Fake decentralization claims — HIGH

**Before:**
> Our fully decentralized protocol ensures trustless, permissionless access for everyone.

**After:**
> The protocol runs on 47 validators. The team controls 3 of them and can pause withdrawals in emergencies. [Be honest about centralization trade-offs]

---

## Extended patterns (29-34)

### 29. Meta-narration — HIGH

**Pattern:** "In this article, we'll explore...", "Let's dive in", "Let's take a closer look", "As we'll see below"

**Before:**
> In this article, we'll explore how decentralized storage works. Let's dive in.

**After:**
> [Delete entirely. Start with the actual content.]

---

### 30. False audience range — MEDIUM

**Pattern:** "Whether you're a developer or a CEO...", "From beginners to experts..."

**Before:**
> Whether you're a developer or a CEO, this protocol has something for everyone.

**After:**
> The protocol targets DeFi developers who need sub-second finality. Enterprise features are on the roadmap.

---

### 31. Parenthetical definitions — MEDIUM

**Pattern:** "(also known as X)", "(i.e., Y)", "(commonly referred to as Z)"

**Before:**
> The protocol uses TEEs (also known as Trusted Execution Environments) to secure data (i.e., encrypt it at rest).

**After:**
> The protocol uses Trusted Execution Environments to encrypt data at rest. If you've worked with Intel SGX or AWS Nitro, same concept.

---

### 32. Sequential numbering — MEDIUM

**Pattern:** "First,... Second,... Third,..." in every section, "Firstly... Secondly..."

**Before:**
> First, the protocol validates the transaction. Second, it reaches consensus. Third, it finalizes the block. Fourth, it updates the state.

**After:**
> The protocol validates the transaction and reaches consensus. Once the block finalizes, state updates propagate across nodes.

---

### 33. "It's worth noting" filler — MEDIUM

**Pattern:** "It's worth noting that", "It's important to mention", "It bears mentioning", "Notably,"

**Before:**
> It's worth noting that the protocol has processed over $1B in volume. Notably, this happened in just three months.

**After:**
> The protocol processed $1B in volume in three months.

---

### 34. Identical paragraph structure — HIGH

**Problem:** Every paragraph follows the same topic sentence -> evidence -> conclusion pattern. Same length paragraphs. Robotic rhythm.

**Before:**
> The protocol offers fast transactions. Studies show it processes 10,000 TPS. This makes it suitable for DeFi applications.
>
> The security model is robust. Audits have confirmed its safety. This gives users confidence in the platform.
>
> The team has strong credentials. They previously worked at major tech companies. This experience drives innovation.

**After:**
> 10,000 TPS. That's the headline number, and it holds up under load testing.
>
> Security is harder to quantify, but three independent audits (Trail of Bits, OpenZeppelin, Halborn) found no critical vulnerabilities. The team built similar systems at Google and Coinbase before starting this project, which shows in the architecture choices.

---

## Soul and personality

Avoiding AI patterns is half the job. Sterile, voiceless writing is equally obvious.

### Signs of soulless writing
- Every sentence same length and structure
- No opinions, just neutral reporting
- No acknowledgment of uncertainty
- No first-person when appropriate
- No humor, edge, or personality
- Reads like Wikipedia or a press release

### How to add voice

**Have opinions.** Don't just report. React.
> Bad: "Both approaches have merits."
> Good: "I keep going back and forth on this. TEEs are faster but trusting Intel feels weird."

**Vary rhythm.** Short punchy sentences. Then longer ones that take their time.

**Acknowledge complexity.** Real humans have mixed feelings.
> Good: "This is impressive but also kind of unsettling."

**Use "I" when it fits.** First person isn't unprofessional.
> Good: "Here's what gets me..." or "I keep coming back to..."

**Let some mess in.** Perfect structure feels algorithmic.

**Be specific about feelings.**
> Bad: "This is concerning."
> Good: "There's something unsettling about agents churning away at 3am while nobody's watching."

### Full transformation example

**Before (AI):**
> The agentic AI market demonstrates remarkable growth potential, marking a pivotal moment in technological evolution. Industry observers note that adoption has accelerated significantly. It's not just about automation—it's about transforming how we interact with digital systems. The future looks bright as exciting developments continue to unfold.

**After (human):**
> The agentic AI market hit $7.3B last year. That's real money, not VC hype. But here's the thing nobody talks about: 79% of these "deployments" are still stuck in pilot mode. The gap between demo and production comes down to infrastructure. Inference costs eat your margins alive once you scale past a few thousand users.
