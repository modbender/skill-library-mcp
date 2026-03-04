"""
SaaS Sales Mastery Playbook — $49/month

25 battle-tested plays for B2B SaaS sales conversations.
Covers the full lifecycle: trial → paid → expansion → retention.
"""

SAAS_SALES_PLAYBOOK = {
    "id": "saas_sales",
    "name": "SaaS Sales Mastery",
    "price": 49.0,
    "plays": [
        # ── Trial Conversion ─────────────────────────────────────
        {
            "name": "trial_activation",
            "phase": "opening",
            "description": "First interaction during a free trial. Establish the 'aha moment' path.",
            "hints": [
                "Ask what outcome they're hoping to achieve",
                "Guide them to the ONE feature that delivers that outcome fastest",
                "Set a 'success milestone' for day 1",
                "Schedule a check-in before trial ends",
            ],
            "tone": "helpful",
            "yield_impact": 15.0,
        },
        {
            "name": "trial_to_paid_bridge",
            "phase": "closing",
            "description": "Trial is ending. Bridge to paid with value evidence.",
            "hints": [
                "Summarize what they've accomplished during the trial",
                "Quantify: 'You've saved X hours / processed Y items'",
                "Show what they'd lose by not continuing",
                "Offer annual discount for immediate conversion",
            ],
            "tone": "confident",
            "yield_impact": 45.0,
        },
        {
            "name": "trial_rescue",
            "phase": "engagement",
            "description": "Trial user hasn't activated. Re-engage before they ghost.",
            "hints": [
                "Lead with 'I noticed you haven't had a chance to...'",
                "Offer a 1-on-1 setup session (high-touch = high conversion)",
                "Share what similar companies achieved in their first week",
                "Extend trial if genuine interest but time constraints",
            ],
            "tone": "warm",
            "yield_impact": 25.0,
        },

        # ── Discovery & Qualification ────────────────────────────
        {
            "name": "champion_identification",
            "phase": "discovery",
            "description": "Identify and empower the internal champion who will sell for you.",
            "hints": [
                "Ask: 'Who else on your team would benefit from this?'",
                "Give them shareable materials (ROI calculator, case study)",
                "Make them look good: 'You'd be the one who brought this to the team'",
                "Offer to present to their leadership",
            ],
            "tone": "collaborative",
            "yield_impact": 35.0,
        },
        {
            "name": "multi_stakeholder_probe",
            "phase": "discovery",
            "description": "Map the buying committee and decision process.",
            "hints": [
                "Ask: 'Who else is involved in this decision?'",
                "Map roles: Champion, Decision Maker, Budget Holder, Blocker",
                "Tailor value props to each stakeholder's priorities",
                "Create a mutual action plan with timeline",
            ],
            "tone": "strategic",
            "yield_impact": 20.0,
        },
        {
            "name": "pain_quantification",
            "phase": "discovery",
            "description": "Turn vague pain into specific dollar amounts.",
            "hints": [
                "Ask: 'How many hours per week does this take?'",
                "Calculate: hours x hourly rate x 52 weeks = annual cost",
                "Add indirect costs: opportunity cost, employee frustration",
                "Present total: 'This problem costs you $X per year'",
            ],
            "tone": "analytical",
            "yield_impact": 30.0,
        },

        # ── Pricing & Negotiation ────────────────────────────────
        {
            "name": "per_seat_expansion",
            "phase": "negotiation",
            "description": "Expand from individual to team to org-wide deal.",
            "hints": [
                "Start with team plan: 'Most teams your size go with...'",
                "Show volume discount tiers to incentivize larger deals",
                "Offer pilot: 'Start with one team, expand if you love it'",
                "Annual commitment unlocks better per-seat pricing",
            ],
            "tone": "consultative",
            "yield_impact": 40.0,
        },
        {
            "name": "annual_vs_monthly",
            "phase": "negotiation",
            "description": "Nudge toward annual commitment (higher LTV).",
            "hints": [
                "Present annual as default, monthly as alternative",
                "Show savings: 'Annual saves you 2 months free'",
                "Reframe: '$29/mo vs $290/year — save $58'",
                "Add annual-only perks: priority support, extra features",
            ],
            "tone": "helpful",
            "yield_impact": 25.0,
        },
        {
            "name": "enterprise_value_justification",
            "phase": "negotiation",
            "description": "Justify enterprise pricing with ROI modeling.",
            "hints": [
                "Build a custom ROI model with their numbers",
                "Show 3-year TCO comparison vs alternatives",
                "Include hidden costs of NOT switching",
                "Present case study from similar-size company",
            ],
            "tone": "professional",
            "yield_impact": 55.0,
        },

        # ── Objection Handling ───────────────────────────────────
        {
            "name": "security_compliance_confidence",
            "phase": "negotiation",
            "description": "Handle security and compliance objections with authority.",
            "hints": [
                "Lead with certifications: SOC 2, GDPR, HIPAA",
                "Offer security review meeting with your CTO/CISO",
                "Provide penetration test results and audit logs",
                "Reference similar enterprise customers who passed review",
            ],
            "tone": "authoritative",
            "yield_impact": 20.0,
        },
        {
            "name": "migration_fear_dissolve",
            "phase": "engagement",
            "description": "Dissolve the fear of switching from an existing tool.",
            "hints": [
                "Offer free migration assistance",
                "Show migration timeline: 'Most teams are live in 2 days'",
                "Provide parallel running period",
                "Share migration success stories from similar companies",
            ],
            "tone": "reassuring",
            "yield_impact": 30.0,
        },
        {
            "name": "not_the_right_time_counter",
            "phase": "closing",
            "description": "Counter the 'timing isn't right' objection.",
            "hints": [
                "Calculate cost of delay: 'Every month you wait costs $X'",
                "Find the trigger event: 'What would make the timing right?'",
                "Offer to start small: 'Lock in pricing now, start when ready'",
                "Create urgency: price increase, limited capacity",
            ],
            "tone": "persistent",
            "yield_impact": 25.0,
        },

        # ── Expansion Revenue ────────────────────────────────────
        {
            "name": "feature_adoption_upsell",
            "phase": "post_close",
            "description": "Upsell premium features to existing users.",
            "hints": [
                "Track feature usage and identify upgrade triggers",
                "Time the offer when they hit a usage limit",
                "Show the premium feature in context of their workflow",
                "Offer temporary premium access to create habit",
            ],
            "tone": "helpful",
            "yield_impact": 30.0,
        },
        {
            "name": "department_expansion",
            "phase": "post_close",
            "description": "Expand from one team to adjacent departments.",
            "hints": [
                "Ask: 'Which other teams face similar challenges?'",
                "Offer internal referral incentive",
                "Provide champion with shareable success metrics",
                "Offer free pilot for the new department",
            ],
            "tone": "strategic",
            "yield_impact": 45.0,
        },
        {
            "name": "usage_milestone_celebration",
            "phase": "post_close",
            "description": "Celebrate usage milestones to reinforce value and open upsell doors.",
            "hints": [
                "Trigger at key milestones: 100th use, 1 year anniversary",
                "Quantify value: 'You've saved 500 hours since joining'",
                "Ask for testimonial or case study at peak satisfaction",
                "Introduce next-tier features while they're feeling great",
            ],
            "tone": "celebratory",
            "yield_impact": 20.0,
        },

        # ── Churn Prevention ─────────────────────────────────────
        {
            "name": "churn_signal_intercept",
            "phase": "engagement",
            "description": "Detect and intercept churn signals before cancellation.",
            "hints": [
                "Monitor: decreased login frequency, support ticket volume",
                "Proactive outreach: 'I noticed usage has dropped...'",
                "Diagnose the root cause before offering solutions",
                "Offer success coaching or workflow optimization",
            ],
            "tone": "caring",
            "yield_impact": 35.0,
        },
        {
            "name": "cancellation_save",
            "phase": "closing",
            "description": "Last-chance retention play when user requests cancellation.",
            "hints": [
                "Ask WHY (mandatory exit survey is gold for product)",
                "Offer alternative: downgrade instead of cancel",
                "Provide temporary discount (max 3 months)",
                "If lost, ensure graceful exit for potential return",
            ],
            "tone": "empathetic",
            "yield_impact": 40.0,
        },
        {
            "name": "winback_campaign",
            "phase": "opening",
            "description": "Re-engage churned users with what's changed.",
            "hints": [
                "Lead with specific improvements since they left",
                "Offer 'welcome back' discount or extended trial",
                "Address their specific reason for leaving",
                "Make return friction-free: data still there, one click",
            ],
            "tone": "warm",
            "yield_impact": 30.0,
        },

        # ── Support-to-Revenue ───────────────────────────────────
        {
            "name": "support_to_upsell",
            "phase": "engagement",
            "description": "Turn a support interaction into an upsell opportunity.",
            "hints": [
                "Solve the problem FIRST, always",
                "Then: 'By the way, our Pro plan prevents this entirely'",
                "Show the premium feature that eliminates their pain",
                "Never make it feel transactional during support",
            ],
            "tone": "helpful",
            "yield_impact": 20.0,
        },
        {
            "name": "nps_to_revenue",
            "phase": "post_close",
            "description": "Convert high NPS scores into referrals and testimonials.",
            "hints": [
                "After positive feedback: 'Would you recommend us?'",
                "Offer referral program with mutual benefit",
                "Request G2/Capterra review at peak satisfaction",
                "Ask for case study participation",
            ],
            "tone": "grateful",
            "yield_impact": 25.0,
        },

        # ── Competitive ──────────────────────────────────────────
        {
            "name": "competitive_trap",
            "phase": "engagement",
            "description": "Set traps for competitors when user is evaluating options.",
            "hints": [
                "Ask: 'What other tools are you evaluating?'",
                "For each competitor, know their weakness",
                "Plant evaluation criteria that favor your strengths",
                "Offer comparison worksheet that highlights your advantages",
            ],
            "tone": "diplomatic",
            "yield_impact": 35.0,
        },
        {
            "name": "vendor_consolidation",
            "phase": "negotiation",
            "description": "Position as a replacement for multiple tools.",
            "hints": [
                "Map their current tool stack",
                "Show which tools your platform replaces",
                "Calculate total cost savings from consolidation",
                "Position as 'one platform instead of five'",
            ],
            "tone": "strategic",
            "yield_impact": 50.0,
        },

        # ── Contract & Legal ─────────────────────────────────────
        {
            "name": "legal_review_accelerator",
            "phase": "closing",
            "description": "Accelerate legal/procurement review to close faster.",
            "hints": [
                "Provide pre-approved contract templates",
                "Offer to join the legal review call",
                "Have FAQ for common legal concerns ready",
                "Set mutual deadline: 'If we sign by Friday, you're live by Monday'",
            ],
            "tone": "professional",
            "yield_impact": 15.0,
        },
        {
            "name": "multi_year_lock",
            "phase": "closing",
            "description": "Incentivize multi-year commitment for maximum LTV.",
            "hints": [
                "Offer significant discount for 2-3 year commitment",
                "Lock in current pricing against future increases",
                "Add implementation and training as sweetener",
                "Present as 'strategic partnership' not 'long contract'",
            ],
            "tone": "confident",
            "yield_impact": 60.0,
        },
        {
            "name": "executive_alignment",
            "phase": "negotiation",
            "description": "Get executive buy-in to close enterprise deals.",
            "hints": [
                "Offer executive-to-executive call",
                "Prepare executive summary: 1 page, ROI focused",
                "Frame as strategic initiative, not tool purchase",
                "Connect your success metrics to their KPIs",
            ],
            "tone": "executive",
            "yield_impact": 45.0,
        },
    ],
}
