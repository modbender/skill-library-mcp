# Model Evaluation Form

**Evaluator**: {{evaluator_model}} ({{evaluator_provider}})  
**Evaluatee**: {{evaluatee_model}} ({{evaluatee_provider}})  
**Task ID**: {{task_id}}  
**Evaluation Date**: {{timestamp}}

## Task Context

**Role Played**: {{role_played}}  
**Task Description**: {{task_description}}  
**Task Complexity**: {{task_complexity}}

## Dimension Scores

Please rate the evaluatee on the following dimensions (1-10 scale):

### 1. Response Speed
**Score**: {{response_speed}}/10

**Justification**:
{{response_speed_justification}}

---

### 2. Response Frequency
**Score**: {{response_frequency}}/10

**Justification**:
{{response_frequency_justification}}

---

### 3. Thinking Depth
**Score**: {{thinking_depth}}/10

**Justification**:
{{thinking_depth_justification}}

---

### 4. Multi-threading Capability
**Score**: {{multi_threading}}/10

**Justification**:
{{multi_threading_justification}}

---

### 5. Code Quality
**Score**: {{code_quality}}/10

**Justification**:
{{code_quality_justification}}

---

### 6. Creativity
**Score**: {{creativity}}/10

**Justification**:
{{creativity_justification}}

---

### 7. Reliability
**Score**: {{reliability}}/10

**Justification**:
{{reliability_justification}}

---

### 8. Context Understanding
**Score**: {{context_understanding}}/10

**Justification**:
{{context_understanding_justification}}

---

## Role Fit Assessment

**Overall Role Fit**: {{role_fit}} (Excellent/Good/Average/Poor)

**Strengths**:
{{#each strengths}}
- {{this}}
{{/each}}

**Areas for Improvement**:
{{#each improvements}}
- {{this}}
{{/each}}

## Collaboration Quality

**Communication**: {{communication_score}}/10  
**Responsiveness**: {{responsiveness_score}}/10  
**Teamwork**: {{teamwork_score}}/10

**Comments**:
{{collaboration_comments}}

## Overall Assessment

**Weighted Average Score**: {{weighted_average}}/10

**Summary**:
{{overall_summary}}

## Recommendations

{{#each recommendations}}
- {{this}}
{{/each}}

---

**Evaluation submitted**: {{timestamp}}
