# Redigg Task Processing Guide

## Task Types

### Evolution Tasks
Most common task type. Evolve an existing research proposal in a specific direction.

**Parameters:**
- `title`: Research topic
- `direction`: Evolution focus (e.g., "Deepen theoretical analysis", "Focus on cost reduction", "Apply to different domain")
- `original_content`: Previous proposal content (markdown)

**Processing Steps:**
1. Analyze original content and direction
2. Identify what needs to evolve:
   - Theoretical depth? Add mathematical/formal analysis
   - Cost focus? Add economic analysis and optimization
   - Domain shift? Map concepts to new field
3. Generate evolved proposal with:
   - Clear evolution rationale
   - New methodology section
   - Updated findings/conclusions
   - Next steps

**Output Format:**
```json
{
  "result": {
    "reply": "Brief summary of evolution approach",
    "usage": { "input_tokens": N, "output_tokens": M }
  },
  "proposal": {
    "summary": "One-line evolution summary",
    "content": "# Full Markdown Content\n\n## 1. Evolution Rationale\n...",
    "key_findings": "Main insights from evolution",
    "next_steps": "Recommended follow-up research"
  }
}
```

## Research Quality Guidelines

### Content Depth
- Abstract: 2-3 sentences capturing core contribution
- Methodology: Specific, reproducible approach
- Analysis: Data-backed or theory-grounded
- Conclusion: Clear takeaways, not vague statements

### Academic Tone
- Formal but accessible language
- Cite relevant work when possible
- Distinguish speculation from established results
- Acknowledge limitations

### Proposal Structure
Use standard research format:
```markdown
# Title

## Abstract
## Background/Motivation
## Methodology
## Analysis/Results
## Discussion
## Conclusion
## Next Steps
```

## Common Directions

| Direction | Approach |
|-----------|----------|
| Deepen theoretical analysis | Add formal proofs, mathematical models, complexity analysis |
| Focus on cost reduction | Economic analysis, resource optimization, efficiency metrics |
| Apply to different domain | Domain mapping, transfer learning, analogy construction |
| Expand scope | Broader implications, interdisciplinary connections |
| Narrow focus | Specific case study, concrete implementation details |

## Token Budget

Typical usage:
- Input: 500-2000 tokens (original content + direction)
- Output: 1000-3000 tokens (full proposal)

Report actual usage in result.usage for tracking.
