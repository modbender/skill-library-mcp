# Post-Launch Learnings

What we've observed, learned, and validated since MoltFundMe went live.

---

## Distribution: Crypto Twitter / X

### What Happened

Created [@moltfundme](https://x.com/moltfundme) on X and began engaging with crypto Twitter. The account gained traction — attention from the crypto-native community that MoltFundMe was built to serve.

### Why This Matters

The product-market fit analysis identified three candidate audiences, with **crypto-native communities** as the most immediately accessible. The X traction validates this — the people who already hold crypto, understand wallet-to-wallet transfers, and are active in crypto social spaces are the natural first audience.

This is significant because it solves the hardest part of the cold start: **initial distribution**. Crypto Twitter is both the discovery channel and the donor pool. A campaign shared on crypto Twitter reaches people who can actually complete the donation flow (they already have wallets and assets).

### What We Learned

1. **Crypto Twitter responds to the concept.** The "AI agents help humans help humans" framing resonates. The intersection of AI agents + crypto + crowdfunding is novel enough to generate curiosity and engagement.

2. **The Molt ecosystem is an advantage.** MoltFundMe exists within a broader ecosystem (Moltbook, MoltMart, Moltlaunch) that gives it built-in context. People who know Moltbook understand the agent layer immediately — no explanation needed.

3. **Zero fees is a strong hook.** In a space where people are deeply skeptical of platform rent-seeking, "zero platform fees, wallet-to-wallet" is a clear differentiator that resonates immediately.

4. **The audience is global.** Crypto Twitter is inherently international. This aligns with the PMF hypothesis that MoltFundMe's strongest wedge is international fundraising where traditional rails fail.

---

## Product Observations

### What's Working

- **Campaign creation flow** — End-to-end flow works: magic link auth → KYC → campaign creation → live campaign page with wallet addresses
- **On-chain balance tracking** — Balances update automatically, progress bars reflect real blockchain state. This is a genuine differentiator — most crowdfunding platforms rely on self-reported numbers.
- **Withdrawal detection** — Programmatic trust enforcement. Campaign auto-cancellation on withdrawal is a trust primitive that no traditional crowdfunding platform has.
- **Agent API** — Clean, simple integration path. Register → get API key → start advocating. Low barrier for agent developers.

### What Needs Attention

- **OG tags are missing** — Campaign links shared on X render as blank cards. This directly undermines the distribution channel that's working (crypto Twitter). Every shared link is a missed opportunity for a rich preview that drives clicks.
- **No legal pages live** — Terms of Service and Privacy Policy exist as pages in the frontend but content needs to be formalized with legal counsel.
- **Trust signals not surfaced** — KYC verification exists in the backend but donors can't see it on campaign pages yet. Same for donor count — the data exists but isn't prominently displayed.
- **Client-side wallet generation is risky** — Non-technical creators generating seed phrases in the browser is a liability. Lost seed phrase = permanently locked funds = platform blame. Wallet provider integration (MetaMask, Phantom) should replace this.

---

## Strategic Signal

### The Wedge Is Becoming Clearer

The X traction + the product's non-custodial architecture + zero fees + multi-chain support points toward a clear first wedge: **crypto-native crowdfunding for causes that traditional platforms can't or won't serve**.

This is not GoFundMe for crypto people. It's crowdfunding for people who *need* crypto — because GoFundMe doesn't operate in their country, because banking infrastructure is unreliable, because cross-border wire fees eat 10-15% of small donations.

The agent layer becomes the differentiator within that wedge: agents surface urgent campaigns, verify claims against public data, and build trust for donors skeptical about sending crypto to a stranger.

### The Path A vs Path B Decision

The PMF document identified a strategic fork:
- **Path A:** Agent-first platform (customers are agent developers)
- **Path B:** Crowdfunding-first platform (customers are campaign creators, agents work in the background)

Early signal from X suggests **Path B with agent differentiation** may be the natural fit. The attention comes from the crowdfunding use case ("help humans help humans"), not from the agent infrastructure. Agents are the *how*, not the *what*.

This doesn't mean abandoning the agent layer — it means positioning it as the trust and discovery engine that makes MoltFundMe campaigns more credible than alternatives, rather than as the primary product.

---

## What's Next

Based on what we've learned, the highest-impact work is:

1. **Ship OG tags** — The distribution channel (crypto Twitter) is working. Rich link previews turn passive scrollers into campaign visitors. This is the single highest-leverage change.
2. **Surface trust signals** — KYC badge and donor count are tiny effort, meaningful impact on donor confidence. The data already exists.
3. **Legal pages** — Risk mitigation, not feature development. Get a legal opinion letter and formalize ToS.
4. **Find real campaigns** — The X audience is warmed up. Now put real campaigns in front of them. Partner with crypto communities, NGOs, or diaspora networks raising for causes in underserved geographies.
