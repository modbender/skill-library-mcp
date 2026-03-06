# n8n Automation Notes

## Recommended approach
- Use the built-in HTTP Request node for bot API calls.
- Keep tokens in credentials or environment variables.

## Community nodes
- If you evaluate third-party nodes (e.g., "n8n-nodes-ultimate"), verify source, maintenance, and security posture before production use.

## Safety
- Do not store cookies or tokens in workflow JSON exports.
- Apply rate limiting and retry backoff.
