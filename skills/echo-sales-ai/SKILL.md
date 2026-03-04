name: echo-sales-ai
description: A comprehensive AI sales assistant that integrates with your email to classify leads, interpret feedback, generate quotes, and manage your entire sales pipeline for manufacturing and technical sales.
---

# Echo Sales AI

Echo is an advanced, AI-powered sales operations manager designed to automate and enhance the sales workflow for manufacturing and technical sales teams. It integrates directly with your email and CRM to provide intelligent assistance at every stage of the sales process.

## Core Workflow

The skill operates on a continuous loop, orchestrated by the **Learning & Compounding Agent**:

1.  **Ingestion:** Monitors connected email accounts for new messages.
2.  **Triage:** The **Email Type Classifier** categorizes each message (e.g., `new_lead`, `customer_reply`, `feedback`, `spam`).
3.  **Enrichment:** For new leads, the **Company Profile Agent** and **Contact Finder** enrich the data.
4.  **Action:** Based on the type, the appropriate agent is triggered (e.g., **Quote Generator** for a request, **Objection Handler** for a customer question).
5.  **Generation:** A draft email is created.
6.  **Feedback Loop:** The draft is presented to you for feedback. The **Feedback Interpreter** processes your natural language comments to refine the draft.
7.  **Dispatch:** The final email is sent.
8.  **CRM Update:** The **CRM Database Agent** logs the entire interaction, updating the deal status in the pipeline.

## The 15 Support Agents

Echo's intelligence is powered by a suite of 15 specialized agents. The core logic for each agent will be developed and stored in the `scripts/` directory. For detailed agent interaction protocols and API specifications, see [references/agents.md](references/agents.md).

1.  **Email Type Classifier:** Categorizes incoming emails.
2.  **Feedback Interpreter:** Translates natural language feedback into structured commands.
3.  **Quote Generator:** Creates sales quotes. See [references/pricing_rules.md](references/pricing_rules.md).
4.  **Pricing Engine:** Calculates pricing based on rules, tiers, and discounts.
5.  **Company Profile Agent:** Researches and summarizes company information.
6.  **Voice-to-Text Transcriber:** Transcribes audio notes from calls.
7.  **CRM Database Agent:** Manages all interactions with the CRM. See [references/crm_schema.md](references/crm_schema.md).
8.  **Pipeline Tracker:** Monitors and reports on the sales pipeline.
9.  **Follow-up Scheduler:** Schedules and drafts follow-up emails.
10. **Urgency Detector:** Identifies urgent messages requiring immediate attention.
11. **Sentiment Analyzer:** Gauges the sentiment of customer replies.
12. **Report Generator:** Creates weekly and monthly sales reports.
13. **Contact Finder:** Finds contact information for new leads.
14. **Objection Handler:** Suggests responses to common sales objections.
15. **Learning & Compounding Agent:** The orchestrator that learns from all interactions.

## Bundled Resources

This skill is designed to be self-contained and includes the following resources:

-   `scripts/echo-skill/`: The core Python application containing the logic for all agents and the Telegram bot interface.
-   `references/`: Contains detailed documentation for the agents and data schemas.
-   `assets/`: Will contain email templates and quote formatting assets.

## How to Use This Skill

Activate the skill by telling your OpenClaw agent:

-   "Activate the echo-sales-ai skill."
-   "Use Echo to check my email."
-   "Ask Echo to help me write a sales quote."
EOF
