# Client Onboarding

## Intake Process

When new client inquiry arrives (email, audio, call notes):

1. **Extract and structure:**
   - Business/project name
   - Core need (what they want done)
   - Budget range (stated or implied)
   - Timeline expectations
   - Decision maker and stakeholders
   - How they found you

2. **Generate structured brief:**
   - Problem statement (what's broken/missing)
   - Success criteria (how we'll know it worked)
   - Scope boundaries (in/out of scope)
   - Constraints (tech, brand, legal, time)
   - Deliverables list with acceptance criteria

3. **Flag red flags:**
   - "ASAP" without clear deadline → clarify actual deadline
   - Scope larger than budget suggests → validate budget range
   - No clear decision maker → identify before proposal
   - Changing requirements during intake → document version
   - Past agency horror stories → probe what went wrong

## Discovery Questions by Agency Type

**Marketing/Content:**
- Current channels and performance
- Brand guidelines and assets
- Competitor examples they like/dislike
- Internal approval process

**Development:**
- Existing tech stack
- User volumes expected
- Integration requirements
- Maintenance expectations

**Design/Creative:**
- Brand assets available
- Examples they like (moodboard)
- Stakeholder approval chain
- Usage rights needed

**Consulting:**
- Who commissioned this and why now
- Previous attempts to solve this
- Data/access available
- Implementation capacity after recommendations

## Client Folder Setup

Create `~/agency/clients/[client-slug].md`:

```markdown
# [Client Name]

## Status: [prospect|active|past]
## Start date: [date]
## Primary contact: [name, email]

### Brand/Voice Notes
<!-- Tone, terminology, preferences -->

### Projects
<!-- List with dates and outcomes -->

### History Log
<!-- Key interactions, decisions, issues -->
```

## Red Flag Response Templates

**Budget mismatch:**
> Based on the scope described, our typical investment range is [X-Y]. Let me know if we should adjust scope to fit [their budget] or if there's flexibility on budget.

**Unclear decision maker:**
> To ensure the project moves smoothly, who will be giving final approval on [deliverables]? I want to make sure they're involved at the right checkpoints.

**Rush request:**
> We can accommodate a faster timeline with a [X]% rush rate. The standard timeline for this scope would be [Y weeks]. Which works better for your situation?
