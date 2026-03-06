---
slug: freelance-pilot
name: FreelancePilot
description: AI Agent Co-Pilot for Upwork & Fiverr. Includes Bid Calculator & Proposal Drafter. (Community Edition)
version: 1.0.0
---

# ✈️ FreelancePilot (Community Edition)

**The AI Co-Pilot for Upwork, Fiverr, and Toptal.**

Turn your OpenClaw agent into a top-1% bidder. This skill provides specialized logic for pricing and proposal structuring.

> **💎 Upgrade to PRO:**
> Get the **Red Flag Scanner**, **Fee Shield Calculator**, and **Advanced Sales Prompts** in the PRO version.
> [👉 Get FreelancePilot PRO on Gumroad](https://gumroad.com/l/freelance-pilot)

## 📦 Installation


1.  **Unzip** into your workspace or skills directory.
2.  **Configure:** Rename `config.example.json` to `config.json` and set your rates.
3.  **Install Deps:** None! (Built on native Node.js).

## 🛠️ Tools & Usage

### 1. `freelance_calculate_bid`
Calculates the perfect bid price to ensure you cover platform fees (20%) and taxes.
*   **Usage:** "Calculate a bid for a 20-hour high complexity project."
*   **Logic:** Takes your base rate, adjusts for difficulty, and adds a "Fee Shield" buffer.

### 2. `freelance_draft_proposal`
Generates a proposal using the **"Consultant Flip"** framework—a sales technique that focuses on client ROI rather than your technical skills.
*   **Usage:** "Draft a proposal for this job description..."

## 🤖 SOUL.md Integration (Optional)

Add this to your agent's `SOUL.md`:

> You are equipped with FreelancePilot. When a user shares a freelance job post:
> 1. Always run `freelance_calculate_bid` first to anchor the value.
> 2. Never just summarize the job. Critique it. Look for "red flags".
> 3. Use the output of `freelance-pilot/index.js` to structure your reply.
