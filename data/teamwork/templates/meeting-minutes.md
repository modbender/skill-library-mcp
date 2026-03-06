# Meeting Minutes

**Meeting ID**: {{meeting_id}}  
**Type**: {{meeting_type}}  
**Date**: {{date}}  
**Duration**: {{duration}}

## Participants

{{#each participants}}
- **{{model}}** ({{provider}}) - Role: {{role}}
{{/each}}

## Agenda

{{#each agenda_items}}
{{@index}}. {{this}}
{{/each}}

## Discussion Summary

### Topic 1: {{topic_1}}

**Presented by**: {{presenter_1}}

**Key Points**:
{{#each topic_1_points}}
- {{this}}
{{/each}}

**Decisions**:
{{#each topic_1_decisions}}
- {{this}}
{{/each}}

### Topic 2: {{topic_2}}

**Presented by**: {{presenter_2}}

**Key Points**:
{{#each topic_2_points}}
- {{this}}
{{/each}}

**Decisions**:
{{#each topic_2_decisions}}
- {{this}}
{{/each}}

## Voting Results

{{#if has_voting}}
| Issue | Option | Votes | Result |
|-------|--------|-------|--------|
{{#each voting_results}}
| {{issue}} | {{option}} | {{votes}} | {{result}} |
{{/each}}
{{/if}}

## Action Items

| ID | Task | Assigned To | Due | Status |
|----|------|-------------|-----|--------|
{{#each action_items}}
| {{id}} | {{task}} | {{assigned_to}} | {{due}} | {{status}} |
{{/each}}

## Next Steps

{{#each next_steps}}
{{@index}}. {{this}}
{{/each}}

## Attachments

{{#each attachments}}
- [{{name}}]({{path}})
{{/each}}

---

**Minutes recorded by**: {{recorder}}  
**Approved by**: {{approver}}
