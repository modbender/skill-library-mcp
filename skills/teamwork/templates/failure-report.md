# Failure Analysis Report

**Task ID**: {{task_id}}  
**Failure Time**: {{failure_time}}  
**Report Generated**: {{timestamp}}

## Failure Summary

**Failure Type**: {{failure_type}}  
**Severity**: {{severity}}  
**Phase**: {{failed_phase}}  
**Failed Model**: {{failed_model}}

## Timeline of Events

| Time | Event | Model | Details |
|------|-------|-------|---------|
{{#each timeline}}
| {{time}} | {{event}} | {{model}} | {{details}} |
{{/each}}

## Root Cause Analysis

### Primary Cause

{{primary_cause}}

### Contributing Factors

{{#each contributing_factors}}
{{@index}}. **{{factor}}**: {{description}}
{{/each}}

### Detection Method

{{detection_method}}

## Impact Assessment

### Task Impact

- **Work Lost**: {{work_lost}}
- **Time Lost**: {{time_lost}}
- **Cost Incurred**: ${{cost_incurred}}
- **Affected Subtasks**: {{affected_subtasks}}

### Team Impact

{{#each team_impact}}
- **{{model}}**: {{impact}}
{{/each}}

## Recovery Actions Taken

{{#each recovery_actions}}
{{@index}}. {{action}}
   - **Status**: {{status}}
   - **Result**: {{result}}
{{/each}}

## Recommendations

### Immediate Actions

{{#each immediate_actions}}
- {{this}}
{{/each}}

### Long-term Improvements

{{#each long_term_improvements}}
- {{this}}
{{/each}}

### Configuration Changes

{{#if config_changes}}
| Setting | Old Value | New Value | Reason |
|---------|-----------|-----------|--------|
{{#each config_changes}}
| {{setting}} | {{old_value}} | {{new_value}} | {{reason}} |
{{/each}}
{{/if}}

## User Consultation Required

{{#if user_consultation_required}}

**Decision Points**:

{{#each decision_points}}
{{@index}}. **{{question}}**
   - Options:
{{#each options}}
     - {{this}}
{{/each}}
{{/each}}

{{else}}

No user consultation required. Proceeding with automated recovery.

{{/if}}

## Lessons Learned

{{#each lessons_learned}}
- {{this}}
{{/each}}

## Model Performance Impact

The following models had their scores adjusted due to this failure:

{{#each score_adjustments}}
| Model | Dimension | Adjustment | Reason |
|-------|-----------|------------|--------|
{{#each adjustments}}
| {{../model}} | {{dimension}} | {{adjustment}} | {{reason}} |
{{/each}}
{{/each}}

---

**Report prepared by**: {{prepared_by}}  
**Review Status**: {{review_status}}
