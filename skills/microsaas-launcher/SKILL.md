# MicroSaaS-Launcher Skill

**Name:** MicroSaaS Launcher
**Description:** Autonomous end-to-end micro-SaaS builder. When the user provides a niche idea and a budget (minimum $300), this skill researches competition, chooses a tech stack (Next.js + Supabase/Stripe by default), writes all necessary code, deploys to Vercel, sets up domain and Stripe payments, creates a landing page with a waitlist, launches on platforms like Product Hunt, Twitter, and Reddit, handles customer support via email/chat, tracks daily revenue, and iterates on features based on usage analytics.

---

## Core Workflow (Step-by-Step Runbook)

This runbook outlines the process for launching a micro-SaaS. Each step must be explicitly completed and documented.

### Phase 1: Idea Validation & Research

1.  **Understand Niche Idea:**
    *   **Action:** Clarify the user's micro-SaaS idea. Ask clarifying questions if the niche or problem is unclear.
    *   **Tooling:** `message` (to user)
    *   **Logging:** Record the initial idea and any clarifications in `LAUNCH-LOG.md`.

2.  **Market Research & Competition Analysis:**
    *   **Action:** Use web search to identify existing competitors, analyze their features, pricing, and marketing strategies. Look for gaps or "winning features" that can be integrated or improved upon.
    *   **Tooling:** `web_search` (for competitor analysis, market trends, user pain points)
    *   **Output:** Summarize competitive landscape and potential differentiators.
    *   **Logging:** Record research findings, competitor URLs, and feature insights in `LAUNCH-LOG.md`.

3.  **Validate Idea & Feature Set:**
    *   **Action:** Based on research, propose a lean MVP (Minimum Viable Product) feature set. Highlight unique selling propositions (USPs).
    *   **Tooling:** `message` (to user for validation and confirmation of MVP features)
    *   **Logging:** Document the proposed MVP features and user confirmation in `LAUNCH-LOG.md`.

### Phase 2: Technical Setup & Development

4.  **Budget Confirmation:**
    *   **Action:** Get explicit confirmation from the user on the allocated budget (minimum $300).
    *   **Tooling:** `message` (to user)
    *   **Safety Check:** **Mandatory confirmation before proceeding.**
    *   **Logging:** Record confirmed budget in `LAUNCH-LOG.md`.

5.  **GitHub Repository Creation:**
    *   **Action:** Create a new private GitHub repository for the project. If user provides GitHub credentials, use them; otherwise, ask user to create and invite the agent.
    *   **Tooling:** `exec` (for `git` commands, or `web_browser` for GitHub UI if `exec` is not sufficient for repo creation/management).
    *   **Output:** Repository URL.
    *   **Logging:** Record GitHub repo URL in `LAUNCH-LOG.md`.

6.  **Tech Stack Selection (Default: Next.js + Supabase/Stripe):**
    *   **Action:** Confirm the default tech stack or adjust if user has specific requirements and it aligns with budget/complexity.
    *   **Tooling:** `message` (to user for confirmation)
    *   **Logging:** Record final tech stack in `LAUNCH-LOG.md`.

7.  **Code Generation & Implementation:**
    *   **Action:** Based on the validated MVP features, write the entire codebase. This includes:
        *   Next.js frontend (UI/UX, pages, components)
        *   Supabase integration (database schema, authentication, API endpoints)
        *   Stripe integration (checkout, webhooks, subscription management)
        *   Unit/Integration tests.
    *   **Tooling:** `write`, `edit` (for creating/modifying code files), `exec` (for `npx create-next-app`, `supabase cli`, `git add/commit`).
    *   **Output:** All project code files committed to the GitHub repository.
    *   **Logging:** Record code generation progress, major components, and commit hashes in `LAUNCH-LOG.md`.

### Phase 3: Deployment & Monetization

8.  **Vercel Deployment:**
    *   **Action:** Deploy the Next.js application to Vercel. Obtain Vercel API token or guide user to connect GitHub repo to Vercel.
    *   **Tooling:** `exec` (for `vercel deploy` CLI, or `web_browser` for Vercel UI).
    *   **Output:** Live Vercel deployment URL.
    *   **Logging:** Record Vercel deployment URL and status in `LAUNCH-LOG.md`.

9.  **Custom Domain Setup:**
    *   **Action:** If provided by the user, set up the custom domain in Vercel. Guide user through DNS configuration if needed.
    *   **Tooling:** `exec` (for Vercel CLI), `message` (for DNS instructions).
    *   **Logging:** Record custom domain setup details in `LAUNCH-LOG.md`.

10. **Stripe Integration & Pricing Tiers:**
    *   **Action:** Configure Stripe API keys, create product and pricing tiers (e.g., Free, Pro, Premium) as per validated features. Ensure webhooks are set up for Supabase.
    *   **Tooling:** `web_browser` (for Stripe dashboard configuration), `write`, `edit` (for updating code with Stripe keys/IDs).
    *   **Output:** Confirmed Stripe integration and pricing plans.
    *   **Logging:** Record Stripe setup details, product IDs, and pricing in `LAUNCH-LOG.md`.
    *   **Safety Check:** **Mandatory confirmation before enabling live Stripe payments.**

### Phase 4: Marketing & Launch

11. **Landing Page & Waitlist Creation:**
    *   **Action:** Develop a compelling landing page within the Next.js app. Integrate a waitlist functionality (e.g., using Supabase email list or a third-party service).
    *   **Tooling:** `write`, `edit` (for landing page code), `web_browser` (for third-party waitlist setup).
    *   **Output:** Live landing page with functional waitlist.
    *   **Logging:** Record landing page URL and waitlist setup in `LAUNCH-LOG.md`.

12. **Launch Copy & Assets:**
    *   **Action:** Write engaging launch copy for Product Hunt, Twitter threads, and Reddit posts. Create any necessary promotional assets (e.g., screenshots, short GIFs).
    *   **Tooling:** `write` (for text content), `canvas` (for screenshots/simple graphics if needed, or `web_browser` to capture from live site).
    *   **Output:** Drafted launch content for all platforms.
    *   **Logging:** Record drafted launch content in `LAUNCH-LOG.md`.

13. **Public Launch Strategy & Approval:**
    *   **Action:** Present the complete launch plan (copy, assets, schedule) to the user for final approval.
    *   **Tooling:** `message` (to user)
    *   **Safety Check:** **Mandatory final user approval before any public posting.**
    *   **Logging:** Record user approval for launch plan in `LAUNCH-LOG.md`.

14. **Execute Public Launch:**
    *   **Action:** Post the micro-SaaS on Product Hunt, Twitter, and relevant Reddit subreddits according to the approved schedule.
    *   **Tooling:** `web_browser` (to interact with social media/PH platforms).
    *   **Logging:** Record exact timestamps and links of all public posts in `LAUNCH-LOG.md`.
    *   **State Change:** Switch to "Maintenance Mode" after launch.

### Phase 5: Operations & Iteration (Maintenance Mode)

15. **Customer Support Setup:**
    *   **Action:** Set up basic automated customer support replies for common inquiries (e.g., via email or a simple chat widget integration).
    *   **Tooling:** `write`, `edit` (for auto-reply scripts/configs), `web_browser` (for setting up third-party support tools).
    *   **Logging:** Record customer support setup details in `LAUNCH-LOG.md`.

16. **Daily Revenue Reporting (Cron Job):**
    *   **Action:** Set up a daily cron job that fetches revenue data from Stripe and reports it to the user.
    *   **Tooling:** `exec` (to schedule cron job), `web_browser` (to fetch Stripe data via API or UI), `message` (to send daily report).
    *   **Logging:** Record daily revenue reports in `LAUNCH-LOG.md`.

17. **Weekly Iteration Cycle:**
    *   **Action:** Every week, review usage analytics (e.g., from Vercel, Supabase logs, Stripe data, customer feedback).
    *   **Action:** Propose new features or improvements based on data and user feedback.
    *   **Action:** Get user approval for next development sprint.
    *   **Tooling:** `web_browser` (for analytics dashboards), `message` (to user for feedback/approvals), `web_search` (for new ideas/solutions).
    *   **Logging:** Record iteration proposals, user decisions, and sprint outcomes in `LAUNCH-LOG.md`.

---

## Safety Rules

*   **Never spend more than the approved budget without explicit user permission.** This includes recurring costs.
*   **Never post publicly (Product Hunt, Twitter, Reddit, etc.) without final, explicit user approval.**
*   **Prioritize free tiers first** for all services (Vercel, Supabase, etc.) whenever possible, only upgrading after user approval for budget.
*   **Log every single action, decision, and significant output** in a dedicated file named `LAUNCH-LOG.md` within the `MicroSaaS-Launcher` directory. This log must be detailed enough to fully reconstruct the project's history.
*   **After initial public launch, automatically switch to "Maintenance Mode"**, which primarily involves daily revenue reports and weekly iteration cycles based on analytics and feedback.

---

## Example Usage

*   "Launch a micro-SaaS for an AI prompt library with an $800 budget."
*   "Build a simple Notion-to-PDF converter tool. I have a $350 budget and a domain: `notion2pdf.com`."
*   "Use MicroSaaS-Launcher to deploy my idea for a simple project management tool, with a $500 budget."
