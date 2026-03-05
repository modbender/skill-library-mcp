# Safety and Privacy

## Key risks
- Audio content can include sensitive data; treat outputs as PII.
- Avoid client-side API key exposure.

## Zero retention
- Some endpoints support `enable_logging=false` for zero retention (enterprise only).

## Operational safeguards
- Redact secrets in logs and monitoring.
- Use single-use tokens for browser-side calls.
