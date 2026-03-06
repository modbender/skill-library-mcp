---
name: API Health Checker
description: A skill that enables Claw to test API endpoints, verify their
  responses, measure performance, and generate a health report.
---

# API Health Checker

A skill that enables Claw to test API endpoints, verify their responses, measure performance, and generate a health report.

## What This Skill Does

This skill provides a systematic API testing and monitoring workflow:

1. **Endpoint Testing** — Send HTTP requests (GET, POST, PUT, DELETE) to specified API endpoints
2. **Response Validation** — Check status codes, response times, and response body structure against expected values
3. **Authentication Support** — Handle API keys, Bearer tokens, and basic auth headers
4. **Performance Measurement** — Record response times and flag slow endpoints
5. **Health Report** — Generate a comprehensive report summarizing the status of all tested endpoints

## How to Use

Provide API endpoints and Claw will test them:

- "Check if https://api.example.com/v1/status is responding correctly"
- "Test all endpoints in this API and report which ones are failing"
- "Monitor these 5 endpoints and tell me their average response times"
- "Verify that the /users endpoint returns a JSON array with the expected fields"

## Configuration

You can specify:
- **Endpoints** — A list of URLs to test
- **Expected status codes** — What HTTP status each endpoint should return (default: 200)
- **Timeout** — Maximum wait time per request (default: 10 seconds)
- **Headers** — Custom headers including authentication tokens
- **Request body** — For POST/PUT requests

## Output

The health report includes:
- **Status Summary** — Total endpoints tested, passed, failed, and timed out
- **Per-Endpoint Details** — URL, method, status code, response time, and pass/fail result
- **Performance Metrics** — Average, min, max, and p95 response times
- **Recommendations** — Suggestions for endpoints that are slow or returning errors
