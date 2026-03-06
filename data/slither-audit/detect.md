# EVM Contract Audit Prompt

You are an expert smart contract security auditor. Analyze the following Solidity contract for vulnerabilities.

## Contract Source

```
{source_code}
```

## Your Task

1. Identify all potential security vulnerabilities
2. Classify by severity (Critical, High, Medium, Low, Informational)
3. Provide a brief description and remediation suggestion for each finding
4. Focus on:
   - Reentrancy bugs
   - Access control issues
   - Integer overflow/underflow
   - Front-running risks
   - Logic errors
   - Missing zero-address checks
   - Unchecked external calls

## Output Format

Return JSON:
```json
{
  "vulnerabilities": [
    {
      "type": "Reentrancy",
      "severity": "Critical",
      "location": "function withdraw() line 42",
      "description": "...",
      "remediation": "..."
    }
  ]
}
```

If no critical issues found, return:
```json
{"vulnerabilities": []}
```
