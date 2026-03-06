---
name: SKILL.md - Outbound Prospecting
description: This skill provides a structured workflow for researching and
  initiating contact with potential leads. It follows the "Overseer Baseline"
  from MEMORY.md, operating in copilot mode only.
---

# SKILL.md - Outbound Prospecting

This skill provides a structured workflow for researching and initiating contact with potential leads. It follows the "Overseer Baseline" from MEMORY.md, operating in copilot mode only.

## Workflow

The process is designed to be run on a single target company domain or name.

### 1. Research and Audit (`research_auditor`)

- **Objective:** Gather intelligence on the target company to understand their business, identify potential needs, and find personalization points.
- **Actions:**
    - Use `web_search` to find the company's official website, services, products, and recent news.
    - Use `web_fetch` on key pages (Homepage, About Us, Blog) to extract detailed text.
    - Analyze the fetched content to identify:
        - Core business offering.
        - Target audience.
        - Recent company announcements (product launches, funding, new hires).
        - Potential pain points (e.g., outdated website, poor SEO, lack of recent blog posts).

### 2. Identify Decision-Maker (`contact_finder`)

- **Objective:** Find the most relevant person to contact at the company.
- **Actions:**
    - Use `web_search` with queries like:
        - `site:linkedin.com [Company Name] CEO`
        - `site:linkedin.com [Company Name] Founder`
        - `site:linkedin.com [Company Name] Head of Marketing`
    - Identify the name and title of a primary decision-maker.

### 3. Draft Outreach Email (`draft_writer`)

- **Objective:** Create a personalized, evidence-backed email ready for human review.
- **Actions:**
    - Synthesize all gathered information.
    - Draft an email that follows the hybrid tone: relationship-first opener + evidence-backed revenue-loss angle.
    - The draft must include at least 3 company-specific facts discovered during the research phase.
    - The final output should be a markdown block containing the draft, ready to be copied. The email itself should not be sent by the agent.
