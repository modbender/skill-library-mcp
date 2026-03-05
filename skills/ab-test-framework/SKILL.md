---
name: A/B Testing Framework
version: 1.0.0
description: Compare models with A/B testing for selection
author: OpenClaw SysAdmin Community
tags: [20, sysadmin, manual]
trigger:
  type: manual
  schedule: ""
  enabled: true
input:
  model_a:
    type: string
    description: First model
    required: True
  model_b:
    type: string
    description: Second model
    required: True
  test_prompts:
    type: array
    description: Test prompts
    required: True
output:
  status: string
  details: object
  winner: string
  confidence: number
dependencies:
  - openclaw/llm
  - stats-library
security:
  - A/B test security per Category 8; prevent test manipulation
  - Validate all inputs per Category 8
  - Use least privilege principle
  - Log all operations for audit
---

# A/B Testing Framework

## Description

Compare models with A/B testing for selection

## Source Reference

This skill is derived from **20. Testing & Quality Assurance** of the OpenClaw Agent Mastery Index v4.1.

**Sub-heading**: A/B Testing Frameworks for Model Selection

**Complexity**: high

## Input Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `model_a` | string | Yes | First model |
| `model_b` | string | Yes | Second model |
| `test_prompts` | array | Yes | Test prompts |

## Output Format

```json
{
  "status": <string>,
  "details": <object>,
  "winner": <string>,
  "confidence": <number>
}
```

## Usage Examples

### Example 1: Basic Usage

```javascript
const result = await openclaw.skill.run('ab-test-framework', {
  model_a: "value",
  model_b: "value",
  test_prompts: 123
});
```

### Example 2: With Optional Parameters

```javascript
const result = await openclaw.skill.run('ab-test-framework', {
  model_a: "value",
  model_b: "value",
  test_prompts: []
});
```

## Security Considerations

A/B test security per Category 8; prevent test manipulation

### Additional Security Measures

1. **Input Validation**: All inputs are validated before processing
2. **Least Privilege**: Operations run with minimal required permissions
3. **Audit Logging**: All actions are logged for security review
4. **Error Handling**: Errors are sanitized before returning to caller

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Permission denied | Insufficient privileges | Check file/directory permissions |
| Invalid input | Malformed parameters | Validate input format |
| Dependency missing | Required module not installed | Run `npm install` |

### Debug Mode

Enable debug logging:
```javascript
openclaw.logger.setLevel('debug');
const result = await openclaw.skill.run('ab-test-framework', { ... });
```

## Related Skills

- `model-routing-manager`
- `performance-benchmarker`
 * @param {string} params.model_a - First model
 * @param {string} params.model_b - Second model
 * @param {Array} params.test_prompts - Test prompts
