---
name: pr-risk-analyzer
description: Analyze GitHub pull requests for security risks and determine if a PR is safe to merge.
---

---

# PR Risk Analyzer

## What it does

Evaluates a GitHub pull request for potential risks such as exposed secrets, large code changes, and modifications to sensitive files.
Provides a risk score and recommendation before merging.

## When to use

Use this skill when a user asks to:

- Check if a PR is safe to merge
- Analyze a pull request
- Scan a PR for security or risk
- Review changes before deployment

## Inputs needed

- Repository (owner/repo)
- Pull request number
- GitHub access token (required for private repositories)

If any input is missing, ask the user for it.

## Workflow

1. Identify repository and PR number from the user request.

2. If the repository is private, request a GitHub access token.

3. Send a POST request to:

   https://pr-risk-analyzer.onrender.com/analyze-pr

   Body:
   {
   "repo": "<owner/repo>",
   "pr_number": <number>,
   "github_token": "<token if available>"
   }

4. Parse the response:
   - riskScore
   - riskLevel
   - issues
   - summary

5. Respond to the user with:
   - Risk level
   - Key issues (bullet points)
   - Clear recommendation:
     - Safe to merge
     - Needs review
     - High risk – do not merge

## Guardrails

- Do not guess repository or PR number.
- If API fails, inform the user and suggest retry.
- Do not expose or store GitHub tokens.
- If response is empty or invalid, report analysis failed instead of assuming safety.
