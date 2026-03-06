# Discovery Playbook

## Goal
Build a schema-aware profile from any Salesforce org without hardcoding RevenueCat-specific fields.

## Steps
1. Validate credentials and token acquisition.
2. Discover available objects via `GET /sobjects`.
3. Prioritize business objects:
   - Account, Contact, Lead, Opportunity, Campaign, CampaignMember, Task, Event, EmailMessage.
4. Describe each available object and collect:
   - field name, label, type, nillable, custom flag.
5. Detect signal packs by field patterns:
   - 6sense: `*6sense*`, `*6QA*`, `*Intent*`.
   - churn: `*churn*`, `*at_risk*`, `*risk*`.
   - ARR/revenue: `*arr*`, `*revenue*`, `*mrr*`.
6. Generate canonical mapping candidates with confidence scores.
7. Ask adaptive follow-ups only for low-confidence mappings.
8. Save profile JSON for reuse.

## Confidence guidance
- High: exact semantic match with expected type and object.
- Medium: partial keyword match or custom naming convention.
- Low: ambiguous candidates with overlapping semantics.
