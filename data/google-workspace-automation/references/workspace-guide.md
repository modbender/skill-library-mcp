# Workspace Automation Guide

## Scope Strategy

- Request only service scopes required by actions.
- Keep separate automations for unrelated scope sets.
- Rotate credentials and monitor token usage.

## Reliability Strategy

- Use idempotent action design.
- Include retry policies for quota/rate-limit errors.
- Log run summaries for auditing.

## Input Requirements

- `automation_name`
- `services`
- `actions`
