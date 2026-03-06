---
name: Knowledge Management System
description: "Score each dimension 1-5 (1=nonexistent, 5=excellent):"
---

# Knowledge Management System

> Turn tribal knowledge into searchable, maintained organizational intelligence. Stop losing expertise when people leave.

## Phase 1: Knowledge Audit

### Current State Assessment

Score each dimension 1-5 (1=nonexistent, 5=excellent):

| Dimension | Score | Evidence |
|-----------|-------|----------|
| Documentation coverage | | % of processes documented |
| Findability | | Can new hire find answers in <5 min? |
| Freshness | | % of docs updated in last 6 months |
| Contribution culture | | % of team actively contributing |
| Onboarding effectiveness | | Time to productivity for new hires |
| Knowledge retention | | Impact when someone leaves |
| Cross-team sharing | | Teams accessing other teams' knowledge |

**Total Score: ___/35**

Interpretation:
- 28-35: Mature — optimize and maintain
- 21-27: Developing — fill gaps systematically
- 14-20: Basic — needs foundational work
- 7-13: Critical — knowledge is at risk

### Knowledge Risk Register

```yaml
knowledge_risk:
  single_points_of_failure:
    - person: "[Name]"
      unique_knowledge: "[What only they know]"
      risk_if_leaves: "high|medium|low"
      extraction_priority: 1
      extraction_method: "interview|shadowing|recording|pair-work"
  
  undocumented_processes:
    - process: "[Name]"
      frequency: "daily|weekly|monthly|quarterly"
      complexity: "high|medium|low"
      current_owner: "[Name]"
      documentation_priority: 1
  
  tribal_knowledge:
    - topic: "[What people 'just know']"
      holders: ["[Name1]", "[Name2]"]
      impact_area: "[What breaks without it]"
      capture_method: "interview|workshop|write-up"
```

### Knowledge Extraction Interview Guide

For each single-point-of-failure person:

1. **Context**: "I'm documenting [X] so the team isn't dependent on any one person. This protects you too — less interruptions."
2. **Process walk**: "Walk me through [X] from start to finish. I'll record/note."
3. **Decision points**: "Where do you make judgment calls? What factors do you consider?"
4. **Edge cases**: "What are the weird situations that come up? How do you handle them?"
5. **Tools & access**: "What tools, credentials, or access do you need?"
6. **History**: "Why is it done this way? What was tried before?"
7. **Gotchas**: "What are the things that trip people up?"

**Output format**: Write up as a runbook (see Phase 3 templates).

---

## Phase 2: Knowledge Architecture

### Taxonomy Design

```yaml
knowledge_taxonomy:
  # Level 1: Knowledge Types
  types:
    how_to:
      description: "Step-by-step procedures and guides"
      examples: ["Deploy to production", "Process a refund", "Set up dev environment"]
      template: "runbook"
      
    reference:
      description: "Facts, specs, configurations to look up"
      examples: ["API endpoints", "Config values", "Vendor contacts", "Pricing tables"]
      template: "reference_doc"
      
    explanation:
      description: "Why things work the way they do"
      examples: ["Architecture decisions", "Policy rationale", "Historical context"]
      template: "explainer"
      
    decision:
      description: "How to make specific judgment calls"
      examples: ["Escalation criteria", "Approval thresholds", "Priority frameworks"]
      template: "decision_tree"
      
    troubleshooting:
      description: "Diagnosis and fix for known problems"
      examples: ["Error codes", "Common failures", "Debug procedures"]
      template: "troubleshooting_guide"

  # Level 2: Domains (customize per org)
  domains:
    - engineering
    - product
    - sales
    - operations
    - finance
    - hr_people
    - customer_success
    - security
    - legal_compliance

  # Level 3: Topics (within each domain)
  # Example for engineering:
  engineering_topics:
    - architecture
    - deployment
    - monitoring
    - incident_response
    - development_workflow
    - testing
    - security
    - infrastructure
```

### Information Architecture Rules

1. **Maximum 3 levels deep** — if deeper, reorganize
2. **One canonical location per topic** — link, don't duplicate
3. **Every page has an owner** — no orphan docs
4. **Every page has a freshness date** — reviewed within 6 months or flagged
5. **Cross-references over duplication** — "See [X]" beats copy-paste
6. **Search-first design** — assume people search, not browse

### Naming Conventions

```
[DOMAIN]-[TYPE]-[TOPIC]-[SPECIFICS]

Examples:
eng-howto-deploy-production
eng-ref-api-endpoints-v3
sales-decision-pricing-enterprise
ops-troubleshoot-billing-failed-charges
product-explain-auth-architecture
```

### Navigation Structure

```yaml
knowledge_base:
  homepage:
    - quick_links:  # Top 10 most-accessed pages
    - recently_updated:  # Last 10 changes
    - needs_review:  # Stale docs flagged
    
  by_audience:
    new_hire: "[Onboarding path → essential reading list]"
    engineer: "[Dev setup → architecture → deployment → debugging]"
    manager: "[Policies → processes → templates → reports]"
    customer_facing: "[Product knowledge → troubleshooting → escalation]"
    
  by_domain: "[Taxonomy Level 2 domains]"
  by_type: "[How-to | Reference | Explanations | Decisions | Troubleshooting]"
```

---

## Phase 3: Document Templates

### Runbook Template (How-To)

```markdown
# [Title]: [Action verb] + [Object]

**Owner:** [Name]  
**Last verified:** [YYYY-MM-DD]  
**Estimated time:** [X minutes]  
**Difficulty:** Easy | Medium | Advanced  

## Prerequisites
- [ ] [Access/tool/permission needed]
- [ ] [Knowledge assumed]

## Steps

### 1. [First action]
[Specific instruction with exact commands, clicks, or actions]

> ⚠️ [Warning about common mistake at this step]

### 2. [Second action]
[Instructions]

**Expected result:** [What you should see/get]

### 3. [Continue...]

## Verification
- [ ] [How to confirm it worked]
- [ ] [What to check]

## Troubleshooting
| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| [Symptom] | [Why] | [Steps] |

## Related
- [Link to related runbook]
- [Link to reference doc]
```

### Reference Document Template

```markdown
# [Subject] Reference

**Owner:** [Name]  
**Last verified:** [YYYY-MM-DD]  
**Scope:** [What this covers and doesn't cover]

## Overview
[1-2 sentence summary of what this reference contains]

## [Main content organized as tables, lists, or structured data]

| Item | Value | Notes |
|------|-------|-------|
| | | |

## Quick Lookup
[Most frequently needed items at the top]

## Change Log
| Date | Change | By |
|------|--------|-----|
| | | |
```

### Architecture Decision Record (ADR)

```markdown
# ADR-[NNN]: [Title]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-[NNN]  
**Date:** [YYYY-MM-DD]  
**Deciders:** [Names]  

## Context
[What situation or problem prompted this decision?]

## Decision
[What was decided and why?]

## Alternatives Considered
| Option | Pros | Cons | Why rejected |
|--------|------|------|-------------|
| [A] | | | |
| [B] | | | |

## Consequences
- **Positive:** [Benefits]
- **Negative:** [Tradeoffs accepted]
- **Risks:** [What could go wrong]

## Review Date
[When should this be revisited?]
```

### Troubleshooting Guide Template

```markdown
# Troubleshooting: [System/Process Name]

**Owner:** [Name]  
**Last verified:** [YYYY-MM-DD]

## Quick Diagnostic

```
[Flowchart as text]
Is [X] happening? 
  → YES: Go to Problem A
  → NO: Is [Y] happening?
    → YES: Go to Problem B
    → NO: Go to Problem C
```

## Problem A: [Symptom Description]

**Likely causes (in order of probability):**
1. [Most common cause]
2. [Second most common]
3. [Rare but possible]

**Fix for Cause 1:**
[Step-by-step resolution]

**Fix for Cause 2:**
[Step-by-step resolution]

**Escalation:** If none of the above work → [who to contact, what info to provide]

## Problem B: [Next symptom]
[Same structure]
```

### Decision Tree Template

```markdown
# Decision Guide: [Topic]

**Owner:** [Name]  
**Last verified:** [YYYY-MM-DD]

## When to use this guide
[Situation that triggers this decision]

## Decision Flow

### Step 1: [First question]
- **If [condition A]** → [Action/next step]
- **If [condition B]** → [Action/next step]
- **If unsure** → [Default action or escalation]

### Step 2: [Second question based on Step 1 answer]
[Continue branching]

## Override conditions
[When to ignore this guide and escalate instead]

## Examples
| Scenario | Decision | Reasoning |
|----------|----------|-----------|
| [Real example] | [What was decided] | [Why] |
```

---

## Phase 4: Contribution System

### Writing Standards

**The 4C Test** (every document must pass all four):
1. **Clear** — Would a new hire understand this? No jargon without definitions.
2. **Correct** — Has this been verified by doing/testing? Not from memory.
3. **Current** — Does this reflect how things work TODAY? Not 6 months ago.
4. **Concise** — Can anything be cut without losing meaning? Cut it.

**Formatting rules:**
- Headers: action-oriented ("Deploy to Production" not "Production Deployment")
- Steps: numbered, one action per step, imperative mood
- Warnings: callout boxes, before the step (not after)
- Code/commands: exact, copy-pasteable, tested
- Screenshots: only if truly needed (they go stale fast)
- Links: to canonical sources, never paste full URLs inline

### Contribution Workflow

```yaml
contribution_workflow:
  create:
    trigger: "New knowledge identified (incident learnings, process change, new tool)"
    steps:
      - choose_template: "Match content type to template"
      - draft: "Write using template structure"
      - self_review: "Run 4C Test checklist"
      - peer_review: "SME validates accuracy"
      - publish: "Add to knowledge base in correct location"
      - announce: "Notify relevant teams/channels"
    
  update:
    trigger: "Existing doc is wrong, incomplete, or stale"
    steps:
      - flag: "Mark as needs-update with reason"
      - update: "Make changes, update 'Last verified' date"
      - review: "If significant change, get peer review"
      - publish: "Update in place"
      - notify: "If behavioral change, announce"
    
  retire:
    trigger: "Doc no longer relevant (deprecated system, changed process)"
    steps:
      - mark: "Status: Deprecated, add redirect to replacement"
      - archive: "Move to archive after 30 days"
      - redirect: "Ensure all links point to replacement"
```

### Incentivizing Contributions

**Making it easy (remove friction):**
- Templates pre-filled with structure
- "Quick capture" channel — dump raw notes, someone structures later
- Post-incident: "What would have helped?" → becomes a doc
- Post-onboarding: new hire documents what was confusing
- Meeting notes → action items include "document [X]"

**Making it visible (social proof):**
- Monthly "top contributors" shoutout
- "Docs champion" rotating role — each sprint, one person owns doc health
- Include documentation in performance criteria
- Knowledge sharing in team meetings (5-min "TIL" segment)

**Making it expected (cultural norms):**
- "If you answered a question twice, write it down"
- PR template includes "Documentation updated? Y/N"
- Incident postmortem includes "Docs to create/update"
- Onboarding feedback includes "What couldn't you find?"

---

## Phase 5: Search & Discovery

### Search Optimization

**Every document should be findable by:**
1. **Title** — descriptive, includes key terms
2. **Tags** — domain, type, audience, technology
3. **Synonyms** — include alternate terms people might search
4. **Problem description** — "When [X] happens" phrasing

**Tag schema:**
```yaml
document_tags:
  domain: "[engineering|product|sales|ops|finance|hr|cs|security|legal]"
  type: "[howto|reference|explanation|decision|troubleshooting]"
  audience: "[all|engineering|management|customer-facing|new-hire]"
  technology: "[list relevant tools/systems]"
  status: "[current|needs-review|deprecated]"
  difficulty: "[beginner|intermediate|advanced]"
```

### Discovery Mechanisms

1. **Contextual links** — Related docs linked at bottom of every page
2. **FAQ collections** — Per-domain "frequently asked" with links to full docs
3. **Onboarding paths** — Curated reading lists by role
4. **Slack/chat bot** — "Ask the KB" — searches and returns relevant docs
5. **Weekly digest** — "New & updated docs this week" email/message
6. **Error-page links** — Application errors link to troubleshooting docs

### Quality Signals

Prioritize search results by:
- **Freshness** — Recently updated > stale
- **Verification** — Peer-reviewed > unreviewed
- **Usage** — Frequently accessed > rarely accessed
- **Completeness** — Fully structured > quick notes

---

## Phase 6: Knowledge Capture Workflows

### Post-Incident Knowledge Capture

After every incident:
1. **Immediate** (within 24h): Raw timeline and resolution steps
2. **Postmortem** (within 5 days): Root cause, contributing factors, action items
3. **Knowledge extraction** (within 10 days):
   - New troubleshooting guide? → Create from postmortem
   - New runbook needed? → Create from resolution steps
   - Existing doc wrong? → Update with correct information
   - Architecture decision needed? → Write ADR
   - Monitoring gap? → Document what to monitor

### Post-Meeting Knowledge Capture

Meeting types that MUST produce knowledge artifacts:
- **Architecture review** → ADR
- **Process change** → Updated runbook
- **Strategy decision** → Decision record
- **Customer feedback pattern** → Product knowledge update
- **Retrospective** → Process improvement doc

### New Employee Knowledge Capture

**First 30 days — new hire documents:**
- What was confusing during onboarding
- Questions that weren't answered by existing docs
- Things that were wrong in existing docs
- Suggestions for improvement

**Template for new hire feedback:**
```yaml
onboarding_feedback:
  week: "[1|2|3|4]"
  couldnt_find: 
    - topic: "[What they looked for]"
      where_looked: "[Where they searched]"
      how_resolved: "[Asked someone? Found eventually? Still unclear?]"
  wrong_or_outdated:
    - doc: "[Which document]"
      issue: "[What's wrong]"
  suggestions:
    - "[Free text improvements]"
```

### Exit Knowledge Transfer

When someone is leaving:
1. **Identify unique knowledge** — What do they know that no one else does?
2. **Schedule extraction sessions** — 1-2 hours per major topic area
3. **Record if possible** — Video walkthroughs of complex processes
4. **Pair them** — Have successor shadow for final 2 weeks
5. **Review their authored docs** — Are they complete? Assign new owners
6. **Document tribal knowledge** — "Why" questions only they can answer

---

## Phase 7: Maintenance & Freshness

### Freshness Policy

```yaml
freshness_policy:
  review_frequency:
    critical_operations: "quarterly"  # Deployment, incident response, security
    standard_processes: "semi-annually"  # Regular workflows
    reference_docs: "annually"  # Specs, contacts, architecture
    explanations: "annually"  # Background, history, rationale
    
  review_process:
    - owner_notified: "2 weeks before due date"
    - review_actions:
        - verify: "Is this still accurate? Test/confirm."
        - update: "Fix any outdated information"
        - stamp: "Update 'Last verified' date"
        - skip: "If can't review, reassign or flag"
    - escalation: "Unreviewed after 30 days → manager notified"
    - stale_threshold: "2x review period without update → flagged as stale"
```

### Content Health Dashboard

```yaml
kb_health:
  date: "[YYYY-MM-DD]"
  
  coverage:
    total_documents: 0
    by_type:
      howto: 0
      reference: 0
      explanation: 0
      decision: 0
      troubleshooting: 0
    by_domain: {}
    gaps_identified: []
    
  freshness:
    current: 0  # Reviewed within policy
    needs_review: 0  # Due for review
    stale: 0  # Past review deadline
    deprecated: 0
    freshness_rate: "0%"  # current / (current + needs_review + stale)
    
  quality:
    peer_reviewed: "0%"
    using_templates: "0%"
    has_owner: "0%"
    has_tags: "0%"
    
  usage:
    searches_per_week: 0
    failed_searches: 0  # Searches with no results
    top_10_pages: []
    pages_never_accessed: 0
    
  contribution:
    docs_created_this_month: 0
    docs_updated_this_month: 0
    unique_contributors: 0
    contribution_rate: "0%"  # contributors / total team size
```

### Quarterly Knowledge Review

**Agenda (60 min):**
1. Dashboard review (10 min) — health metrics trend
2. Gap analysis (15 min) — what's missing? What questions keep being asked?
3. Stale doc triage (15 min) — update, deprecate, or reassign owners
4. Failed searches review (10 min) — what are people searching for and not finding?
5. Process improvements (10 min) — what's working, what isn't?

---

## Phase 8: Knowledge-Driven Automation

### Automated Knowledge Triggers

```yaml
automation_triggers:
  incident_resolved:
    action: "Create task: 'Write troubleshooting guide for [incident title]'"
    assignee: "Incident commander"
    due: "+10 days"
    
  new_hire_started:
    action: "Generate personalized onboarding reading list from KB by role"
    
  doc_stale:
    action: "Notify owner, CC manager if unreviewed after 14 days"
    
  repeated_question:
    threshold: "Same question asked 3+ times in support/Slack"
    action: "Create task: 'Document answer to [question]'"
    
  process_changed:
    trigger: "PR merged that changes workflow/process"
    action: "Check if related docs need updating, create task if yes"
    
  failed_search:
    threshold: "Same search term fails 5+ times/week"
    action: "Flag as gap, create task to write missing doc"
```

### Knowledge-Powered Chatbot Design

```yaml
kb_chatbot:
  flow:
    1_receive_question: "User asks in designated channel"
    2_search: "Semantic search across KB"
    3_respond:
      found_match: "Return relevant doc link + summary"
      partial_match: "Return closest docs + 'Did you mean...?'"
      no_match: "Log as gap, route to human expert, create doc task"
    4_feedback: "Was this helpful? 👍/👎"
    5_improve: "Use feedback to tune search, identify doc improvements"
    
  sources:
    - knowledge_base_docs
    - slack_saved_answers  # Curated from Slack threads
    - incident_postmortems
    - meeting_notes_tagged_as_knowledge
```

---

## Phase 9: Cross-Team Knowledge Sharing

### Knowledge Sharing Mechanisms

| Mechanism | Frequency | Format | Audience |
|-----------|-----------|--------|----------|
| "TIL" channel | Daily | Short post (1-3 sentences + link) | All |
| Brown bag lunch | Bi-weekly | 20-min presentation + Q&A | Cross-team |
| Architecture review | Monthly | 45-min deep dive + ADR | Engineering |
| Customer insight share | Monthly | Top 5 patterns + implications | Product + CS + Sales |
| Postmortem review | Per incident | Written + optional walkthrough | Engineering + ops |
| New tool/technique demo | As needed | 15-min demo + doc link | Relevant teams |
| Quarterly knowledge review | Quarterly | Dashboard + gap analysis | Leadership |

### Cross-Team Knowledge Map

```yaml
knowledge_map:
  engineering:
    produces: ["Architecture docs", "Runbooks", "API specs", "ADRs"]
    consumes_from:
      product: ["PRDs", "User research", "Roadmap"]
      customer_success: ["Bug patterns", "Feature requests", "Usage data"]
      sales: ["Technical requirements", "Integration needs"]
      
  product:
    produces: ["PRDs", "User research", "Roadmap", "Release notes"]
    consumes_from:
      engineering: ["Technical feasibility", "Architecture constraints"]
      customer_success: ["Feature requests", "Churn reasons"]
      sales: ["Deal requirements", "Competitive intel"]
      
  customer_success:
    produces: ["FAQ", "Troubleshooting guides", "Best practices"]
    consumes_from:
      engineering: ["Release notes", "Known issues"]
      product: ["Feature docs", "Roadmap"]
      
  sales:
    produces: ["Battlecards", "Competitive intel", "Use case docs"]
    consumes_from:
      product: ["Feature docs", "Roadmap", "Pricing"]
      customer_success: ["Case studies", "Success metrics"]
      engineering: ["Technical capabilities", "Integration docs"]
```

---

## Phase 10: Metrics & ROI

### Knowledge Management KPIs

| Metric | Target | Measurement |
|--------|--------|-------------|
| Time to answer | <5 min for documented topics | Sample timing tests |
| New hire time to productivity | Reduce by 30% | First solo task date |
| Repeated questions | Decrease 50% in 6 months | Support ticket analysis |
| Doc coverage | >80% of critical processes | Audit against process list |
| Freshness rate | >85% within review policy | Dashboard metric |
| Contribution rate | >40% of team contributing monthly | Contributor count |
| Search success rate | >80% find what they need | Search analytics |
| Failed search rate | <10% of searches | Search analytics |
| Knowledge reuse | >60% of team using KB weekly | Usage analytics |

### ROI Calculation

```
Knowledge Management ROI:

Time Saved:
  Reduced question-answering = [hours/week] × [avg hourly cost] × 52
  Faster onboarding = [weeks saved] × [new hires/year] × [weekly cost]
  Faster incident resolution = [hours saved/incident] × [incidents/year] × [hourly cost]
  
Risk Reduced:
  Key person dependency = [probability of departure] × [knowledge reconstruction cost]
  Compliance documentation = [audit prep hours saved] × [hourly cost]
  
Quality Improved:
  Fewer repeated mistakes = [error rate reduction] × [cost per error]
  Consistent processes = [variance reduction] × [rework cost]
  
Total Annual Value = Time Saved + Risk Reduced + Quality Improved
Investment = Tool cost + Time spent maintaining KB + Training
ROI = (Total Annual Value - Investment) / Investment × 100
```

---

## Phase 11: Scoring & Quality

### Document Quality Rubric (0-100)

| Dimension | Weight | 0-2 (Poor) | 3-5 (Adequate) | 6-8 (Good) | 9-10 (Excellent) |
|-----------|--------|------------|-----------------|-------------|-------------------|
| Accuracy | 20% | Unverified, possibly wrong | Mostly correct | Verified, accurate | Tested, peer-reviewed |
| Completeness | 15% | Major gaps | Covers basics | Comprehensive | Edge cases included |
| Clarity | 15% | Confusing, jargon-heavy | Understandable | Clear, well-structured | A new hire gets it |
| Findability | 10% | No tags, bad title | Some tags | Good tags, clear title | Synonyms, cross-refs |
| Freshness | 15% | >12 months stale | Within annual review | Within semi-annual | Within quarterly |
| Template compliance | 10% | No structure | Partial template | Full template | Template + extras |
| Actionability | 10% | Theory only | Some steps | Clear steps | Copy-paste ready |
| Ownership | 5% | No owner | Owner assigned | Owner active | Owner + backup |

**Score interpretation:**
- 90-100: Exemplary — reference model for other docs
- 75-89: Good — meets standards
- 60-74: Acceptable — needs minor improvements
- 40-59: Below standard — needs significant work
- 0-39: Critical — rewrite from scratch

### Knowledge Base Health Score (0-100)

| Dimension | Weight | Metric |
|-----------|--------|--------|
| Coverage | 20% | % of critical processes documented |
| Freshness | 20% | % of docs within review policy |
| Quality | 15% | Average document quality score |
| Usage | 15% | % of team using KB weekly |
| Contribution | 15% | % of team contributing monthly |
| Search effectiveness | 15% | % of searches finding results |

---

## Edge Cases

### Small Team (<10 people)
- Start with a single shared doc/wiki, not a full KB platform
- Focus on: runbooks for critical processes, onboarding guide, decision log
- One person owns KB health (part-time, not full-time)
- Review quarterly, not monthly

### Remote/Distributed Teams
- Default to written over verbal knowledge sharing
- Record important meetings/decisions (not all meetings)
- Async-first: every decision documented, not just discussed
- Time zone coverage: ensure docs cover "what to do when the expert is asleep"

### Rapid Growth (Doubling in 6 months)
- Prioritize onboarding docs above all else
- Implement "new hire documents what they learn" from day 1
- Assign knowledge buddies — each new person paired with a doc mentor
- Weekly new-hire cohort Q&A → captured and documented

### Regulated Industry
- Map compliance requirements to documentation requirements
- Version control with audit trail (who changed what, when)
- Approval workflows for regulated content
- Retention policies aligned with regulations

### Post-Merger/Acquisition
- Map both organizations' knowledge structures
- Identify overlaps and gaps
- Prioritize: "how do we work NOW" docs over historical
- Freeze archives of legacy systems/processes

### Migrating from Scattered Docs
- Don't try to migrate everything — start fresh with new structure
- Import only: still-accurate, frequently-used docs
- Redirect old locations to new ones
- Set a sunset date for old system
- "If it's not in the new KB, it doesn't exist" (after migration period)

---

## Natural Language Commands

| Command | Action |
|---------|--------|
| "Audit our knowledge management" | Run Phase 1 assessment, generate risk register |
| "Design our KB structure" | Create taxonomy and navigation architecture |
| "Write a runbook for [X]" | Generate using runbook template |
| "Write an ADR for [X]" | Generate architecture decision record |
| "Create a troubleshooting guide for [X]" | Generate using troubleshooting template |
| "Review KB health" | Generate health dashboard and identify gaps |
| "Plan knowledge extraction for [person]" | Generate interview guide and schedule |
| "Set up freshness tracking" | Create review schedule and notification rules |
| "Design onboarding knowledge path for [role]" | Curate reading list from KB |
| "Analyze failed searches" | Review search gaps and create tasks |
| "Generate quarterly KB report" | Full metrics dashboard with recommendations |
| "Plan KB migration from [source]" | Create migration plan with prioritization |
